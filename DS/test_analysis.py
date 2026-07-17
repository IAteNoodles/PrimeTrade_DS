"""Unit tests for all analysis modules."""

import pandas as pd
from load_datasets import load_fear_greed, load_historical_trades, load_merged
from trader_performance import compute_trader_metrics
from sentiment_analysis import compute_daily_metrics, pnl_by_category

def test_load_fg():
    fg = load_fear_greed()
    assert isinstance(fg, pd.DataFrame)
    assert all(c in fg.columns for c in ["value", "classification", "date"])
    assert len(fg) == 2644
    print("  OK load_fear_greed")

def test_load_trades():
    ht = load_historical_trades()
    assert isinstance(ht, pd.DataFrame)
    assert "Account" in ht.columns and "Closed_PnL" in ht.columns
    assert len(ht) == 211224
    print("  OK load_historical_trades")

def test_merge():
    merged = load_merged()
    assert "fear_greed_value" in merged.columns
    assert "sentiment" in merged.columns
    assert len(merged) == 211224
    print("  OK load_merged")

def test_trader_metrics():
    ht = load_historical_trades()
    metrics = compute_trader_metrics(ht)
    assert len(metrics) == 32
    assert "total_pnl" in metrics.columns and "win_rate" in metrics.columns
    assert metrics["win_rate"].between(0, 1).all()
    print("  OK compute_trader_metrics")

def test_daily_metrics():
    merged = load_merged()
    daily = compute_daily_metrics(merged)
    assert "fear_greed_value" in daily.columns
    assert daily["win_rate"].between(0, 1).all()
    assert len(daily) > 100
    print("  OK compute_daily_metrics")

def test_sentiment_summary():
    merged = load_merged()
    summary = pnl_by_category(merged)
    expected = ["Extreme Fear", "Fear", "Neutral", "Greed", "Extreme Greed"]
    assert list(summary["sentiment"]) == expected
    print("  OK pnl_by_category")

def test_pnl_fg_correlation():
    merged = load_merged()
    daily = compute_daily_metrics(merged)
    corr = daily["fear_greed_value"].corr(daily["total_pnl"])
    assert isinstance(corr, float)
    print(f"  OK PnL-F&G correlation: {corr:.4f}")

def test_sentiment_coverage():
    merged = load_merged()
    cov = merged["sentiment"].notna().mean()
    assert cov > 0.8
    print(f"  OK sentiment coverage: {cov:.2%}")

if __name__ == "__main__":
    print("Running tests...\n")
    test_load_fg()
    test_load_trades()
    test_merge()
    test_trader_metrics()
    test_daily_metrics()
    test_sentiment_summary()
    test_pnl_fg_correlation()
    test_sentiment_coverage()
    print("\nOK All tests passed!")
