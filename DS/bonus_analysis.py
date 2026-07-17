"""Bonus analysis: statistical tests, trader clustering, time series decomposition, risk metrics."""

import os
import warnings
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.tsa.seasonal import seasonal_decompose

from load_datasets import load_merged
from trader_performance import compute_trader_metrics
from sentiment_analysis import compute_daily_metrics

warnings.filterwarnings("ignore", category=FutureWarning)

PLOT_DIR = "plots"
os.makedirs(PLOT_DIR, exist_ok=True)


# ── 1. Statistical Tests ──────────────────────────────────────────────────────

def run_ttest_buy_sell(merged: pd.DataFrame):
    """t-test: is buy vs sell PnL significantly different?"""
    closed = merged[merged["Closed_PnL"] != 0].copy()
    buy = closed.loc[closed["Side"] == "BUY", "Closed_PnL"]
    sell = closed.loc[closed["Side"] == "SELL", "Closed_PnL"]
    t_stat, p_val = stats.ttest_ind(buy, sell, equal_var=False)
    print("\n=== T-TEST: Buy vs Sell PnL ===")
    print(f"t = {t_stat:.4f}, p = {p_val:.6f}")
    if p_val < 0.05:
        print("Significant at p<0.05 — buy/sell PnL differ.")
    else:
        print("Not significant (p>=0.05).")
    return t_stat, p_val


def run_anova_sentiment(merged: pd.DataFrame):
    """One-way ANOVA: does PnL differ across sentiment categories?"""
    closed = merged[merged["Closed_PnL"] != 0].copy()
    groups = [group["Closed_PnL"].values for _, group in closed.groupby("sentiment")]
    f_stat, p_val = stats.f_oneway(*groups)
    print("\n=== ANOVA: PnL across Sentiment Categories ===")
    print(f"F = {f_stat:.4f}, p = {p_val:.6f}")
    if p_val < 0.05:
        print("Significant — PnL varies by sentiment.")
    else:
        print("Not significant.")
    return f_stat, p_val


def run_posthoc(merged: pd.DataFrame):
    """Pairwise t-tests between sentiment categories with Bonferroni correction."""
    from itertools import combinations
    closed = merged[merged["Closed_PnL"] != 0].copy()
    closed = closed.dropna(subset=["sentiment"]).copy()
    sentiments = sorted(closed["sentiment"].unique())
    if len(sentiments) < 2:
        print("\n=== POST-HOC: fewer than 2 sentiment groups — skipping ===")
        return pd.DataFrame()
    results = []
    for s1, s2 in combinations(sentiments, 2):
        g1 = closed.loc[closed["sentiment"] == s1, "Closed_PnL"]
        g2 = closed.loc[closed["sentiment"] == s2, "Closed_PnL"]
        if len(g1) < 2 or len(g2) < 2:
            continue
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            t, p = stats.ttest_ind(g1, g2, equal_var=False)
        results.append((s1, s2, t, p))
    df = pd.DataFrame(results, columns=["group1", "group2", "t_stat", "p_raw"])
    if df.empty:
        print("\n=== POST-HOC: no valid comparisons ===")
        return df
    df["p_bonf"] = np.clip(df["p_raw"] * len(results), 0, 1)
    df["sig"] = df["p_bonf"] < 0.05
    print("\n=== POST-HOC (Bonferroni): Pairwise Sentiment PnL ===")
    for _, r in df.iterrows():
        flag = " ***" if r["sig"] else ""
        print(f"  {str(r['group1']):20s} vs {str(r['group2']):20s}  t={r['t_stat']:7.2f}  p_bonf={r['p_bonf']:.4f}{flag}")
    return df


# ── 2. Trader Clustering ──────────────────────────────────────────────────────

def cluster_traders(merged: pd.DataFrame):
    """KMeans clustering on normalized trader behavior metrics."""
    tm = compute_trader_metrics(merged)
    feat_cols = ["total_trades", "avg_pnl", "win_rate", "total_coins", "avg_trade_size"]
    X = tm[feat_cols].fillna(0).values
    scaler = StandardScaler()
    Xs = scaler.fit_transform(X)

    sil_scores = {}
    for k in range(2, 6):
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = km.fit_predict(Xs)
        sil_scores[k] = silhouette_score(Xs, labels)
    best_k = max(sil_scores, key=sil_scores.get)
    km = KMeans(n_clusters=best_k, random_state=42, n_init=10)
    tm["cluster"] = km.fit_predict(Xs)

    print("\n=== TRADER CLUSTERING ===")
    print(f"Best k = {best_k} (silhouette = {sil_scores[best_k]:.3f})")
    for c in sorted(tm["cluster"].unique()):
        subset = tm[tm["cluster"] == c]
        print(f"\n  Cluster {c} ({len(subset)} traders):")
        print(f"    Avg trades: {subset['total_trades'].mean():.0f}")
        print(f"    Avg PnL: ${subset['total_pnl'].mean():.0f}")
        print(f"    Avg win rate: {subset['win_rate'].mean():.1%}")
        print(f"    Avg coins traded: {subset['total_coins'].mean():.1f}")
        print(f"    Avg trade size: ${subset['avg_trade_size'].mean():.0f}")

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    colors = sns.color_palette("husl", best_k)
    for c in sorted(tm["cluster"].unique()):
        subset = tm[tm["cluster"] == c]
        axes[0].scatter(subset["total_trades"], subset["avg_pnl"],
                        label=f"Cluster {c}", alpha=0.7, color=colors[c])
        axes[1].scatter(subset["win_rate"], subset["total_pnl"],
                        label=f"Cluster {c}", alpha=0.7, color=colors[c])
    axes[0].set(xlabel="Total Trades", ylabel="Avg PnL", title="Trader Clusters (Trades vs PnL)")
    axes[0].legend()
    axes[1].set(xlabel="Win Rate", ylabel="Total PnL", title="Trader Clusters (Win Rate vs PnL)")
    axes[1].legend()
    fig.tight_layout()
    fig.savefig(f"{PLOT_DIR}/trader_clusters.png", dpi=100)
    plt.close(fig)
    print(f"\n  Plot saved to {PLOT_DIR}/trader_clusters.png")
    return tm, best_k, sil_scores


# ── 3. Time Series Decomposition ──────────────────────────────────────────────

def decompose_timeseries(merged: pd.DataFrame):
    """Seasonal decomposition of daily trade volume and F&G value."""
    daily = compute_daily_metrics(merged).set_index("date")
    daily = daily.asfreq("D").fillna(method="ffill")

    fig, axes = plt.subplots(4, 2, figsize=(14, 10))

    for idx, (col, label) in enumerate([("total_trades", "Daily Trade Count"),
                                         ("fear_greed_value", "Fear & Greed Index")]):
        series = daily[col].dropna()
        if len(series) < 14:
            continue
        try:
            decomp = seasonal_decompose(series, model="additive", period=7)
            decomp.observed.plot(ax=axes[0, idx], color="tab:blue", linewidth=0.6)
            axes[0, idx].set(title=f"{label} — Observed", ylabel="")
            decomp.trend.plot(ax=axes[1, idx], color="tab:orange", linewidth=0.8)
            axes[1, idx].set(title="Trend", ylabel="")
            decomp.seasonal.plot(ax=axes[2, idx], color="tab:green", linewidth=0.5)
            axes[2, idx].set(title="Weekly Seasonal", ylabel="")
            decomp.resid.plot(ax=axes[3, idx], color="tab:red", linewidth=0.4, marker=".", markersize=1)
            axes[3, idx].set(title="Residual", ylabel="")
        except Exception as e:
            axes[0, idx].text(0.5, 0.5, f"Decomposition failed:\n{e}", transform=axes[0, idx].transAxes, ha="center")

    fig.tight_layout()
    fig.savefig(f"{PLOT_DIR}/timeseries_decomposition.png", dpi=100)
    plt.close(fig)
    print(f"  Time series decomposition plot saved to {PLOT_DIR}/timeseries_decomposition.png")

    fg_corr = daily["fear_greed_value"].corr(daily["total_trades"])
    print("\n=== TIME SERIES ===")
    print(f"  F&G vs Trade Count correlation (daily): {fg_corr:.4f}")
    return daily


# ── 4. Risk Metrics ───────────────────────────────────────────────────────────

def compute_risk_metrics(merged: pd.DataFrame):
    """Sharpe-like ratio, drawdown, profit factor per trader."""
    tm = compute_trader_metrics(merged)
    pnl_map = merged.groupby("Account")["Closed_PnL"].std().to_dict()
    tm["pnl_std"] = tm["Account"].map(pnl_map)
    tm["sharpe"] = tm["avg_pnl"] / tm["pnl_std"].replace(0, np.nan) * np.sqrt(252)

    pos_sum = merged[merged["Closed_PnL"] > 0].groupby("Account")["Closed_PnL"].sum()
    neg_sum = merged[merged["Closed_PnL"] < 0].groupby("Account")["Closed_PnL"].sum().abs()
    pos_mean = merged[merged["Closed_PnL"] > 0].groupby("Account")["Closed_PnL"].mean()
    neg_mean = merged[merged["Closed_PnL"] < 0].groupby("Account")["Closed_PnL"].mean().abs()
    profit_factor = (pos_sum / neg_sum.replace(0, np.nan)).rename("profit_factor").reset_index()
    win_loss_ratio = (pos_mean / neg_mean.replace(0, np.nan)).rename("win_loss_ratio").reset_index()
    tm = tm.merge(profit_factor, on="Account", how="left")
    tm = tm.merge(win_loss_ratio, on="Account", how="left")

    print("\n=== RISK METRICS ===")
    print(f"  Sharpe range: {tm['sharpe'].min():.2f} to {tm['sharpe'].max():.2f}")
    print(f"  Profit factor range: {tm['profit_factor'].min():.2f} to {tm['profit_factor'].max():.2f}")
    print(f"  Win/loss ratio range: {tm['win_loss_ratio'].min():.2f} to {tm['win_loss_ratio'].max():.2f}")

    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    for ax, col, label in zip(axes,
                               ["sharpe", "profit_factor", "win_loss_ratio"],
                               ["Sharpe Ratio", "Profit Factor", "Win/Loss Ratio"]):
        vals = tm[col].dropna()
        sns.histplot(vals, bins=20, ax=ax)
        ax.axvline(vals.median(), color="red", linestyle="--", label=f"Median={vals.median():.2f}")
        ax.set(title=label, xlabel="")
        ax.legend()
    fig.tight_layout()
    fig.savefig(f"{PLOT_DIR}/risk_metrics.png", dpi=100)
    plt.close(fig)
    print(f"  Risk metrics plot saved to {PLOT_DIR}/risk_metrics.png")
    return tm


# ── 5. Combined Runner ────────────────────────────────────────────────────────

def run_all():
    merged = load_merged()

    print("=" * 60)
    print("BONUS ANALYSIS")
    print("=" * 60)

    t_stat, p_val = run_ttest_buy_sell(merged)
    f_stat, p_val2 = run_anova_sentiment(merged)
    posthoc = run_posthoc(merged)
    tm_clust, best_k, sil = cluster_traders(merged)
    daily_ts = decompose_timeseries(merged)
    tm_risk = compute_risk_metrics(merged)

    return {
        "ttest": (t_stat, p_val),
        "anova": (f_stat, p_val2),
        "posthoc": posthoc,
        "clustering": (tm_clust, best_k, sil),
        "timeseries": daily_ts,
        "risk": tm_risk,
    }


if __name__ == "__main__":
    run_all()
