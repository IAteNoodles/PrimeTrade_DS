"""Analyze correlation between Fear & Greed sentiment and trader performance."""

import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from load_datasets import load_merged

SENTIMENT_ORDER = ["Extreme Fear", "Fear", "Neutral", "Greed", "Extreme Greed"]

def compute_daily_metrics(merged: pd.DataFrame) -> pd.DataFrame:
    """Aggregate trades and PnL per day, carrying the F&G value."""
    daily = merged.groupby("date").agg(
        total_trades=("Account", "count"),
        total_pnl=("Closed_PnL", "sum"),
        avg_pnl=("Closed_PnL", "mean"),
        win_rate=("Closed_PnL", lambda x: (x > 0).mean()),
        total_volume=("Size_USD", "sum"),
        fear_greed_value=("fear_greed_value", "first"),
        sentiment=("sentiment", "first"),
    ).reset_index()
    return daily

def corr_analysis(daily: pd.DataFrame):
    """Print Pearson correlation of daily metrics with F&G value."""
    cols = ["total_trades", "total_pnl", "avg_pnl", "win_rate", "total_volume", "fear_greed_value"]
    corr = daily[cols].corr()["fear_greed_value"].sort_values(ascending=False)
    print("=== CORRELATION: Daily Metrics vs Fear & Greed Value ===")
    print(corr.to_string())
    return corr

def plot_sentiment_scatter(daily: pd.DataFrame):
    """Scatter plots: F&G vs avg PnL, win rate, trade count, volume."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 8))
    targets = [("avg_pnl", "Avg PnL"), ("win_rate", "Win Rate"), ("total_trades", "Trade Count"), ("total_volume", "Volume")]
    for ax, (col, label) in zip(axes.flat, targets):
        sns.scatterplot(data=daily, x="fear_greed_value", y=col, alpha=0.3, ax=ax)
        ax.set(title=f"{label} vs F&G Value")
    fig.tight_layout()
    fig.savefig("plots/sentiment_vs_performance.png", dpi=100)
    plt.close(fig)

def pnl_by_category(merged: pd.DataFrame) -> pd.DataFrame:
    """Box plot + summary table of PnL grouped by sentiment category."""
    merged["sentiment"] = pd.Categorical(merged["sentiment"], categories=SENTIMENT_ORDER, ordered=True)
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.boxplot(data=merged, x="sentiment", y="Closed_PnL", hue="sentiment", ax=ax, showfliers=False, legend=False)
    ax.set(title="PnL Distribution by Sentiment Category", ylabel="Closed PnL")
    fig.tight_layout()
    fig.savefig("plots/pnl_by_sentiment.png", dpi=100)
    plt.close(fig)

    summary = merged.groupby("sentiment", observed=True).agg(
        total_trades=("Account", "count"),
        avg_pnl=("Closed_PnL", "mean"),
        win_rate=("Closed_PnL", lambda x: (x > 0).mean()),
        total_pnl=("Closed_PnL", "sum"),
    ).reset_index()
    print("\n=== PERFORMANCE BY SENTIMENT CATEGORY ===")
    print(summary.to_string(index=False))
    return summary

if __name__ == "__main__":
    merged = load_merged()
    daily = compute_daily_metrics(merged)
    corr_analysis(daily)
    os.makedirs("plots", exist_ok=True)
    plot_sentiment_scatter(daily)
    pnl_by_category(merged)
    print("\nPlots saved to plots/")
