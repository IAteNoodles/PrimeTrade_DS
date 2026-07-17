"""Per-trader performance metrics: PnL, win rate, fees, volume, diversification."""

import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from load_datasets import load_historical_trades

def compute_trader_metrics(ht: pd.DataFrame) -> pd.DataFrame:
    """Aggregate key performance metrics per trader account."""
    grouped = ht.groupby("Account")
    metrics = pd.DataFrame({
        "total_trades": grouped.size(),
        "total_pnl": grouped["Closed_PnL"].sum(),
        "avg_pnl": grouped["Closed_PnL"].mean(),
        "win_rate": grouped["Closed_PnL"].apply(lambda x: (x > 0).mean()),
        "total_fees": grouped["Fee"].sum(),
        "total_volume_usd": grouped["Size_USD"].sum(),
        "avg_trade_size": grouped["Size_USD"].mean(),
        "total_coins": grouped["Coin"].nunique(),
    }).reset_index()
    metrics["net_profit"] = metrics["total_pnl"] - metrics["total_fees"]
    metrics["pnl_per_trade"] = metrics["total_pnl"] / metrics["total_trades"]
    return metrics.sort_values("total_pnl", ascending=False)

def plot_top_traders(metrics: pd.DataFrame):
    """Bar plots of the 10 best traders by PnL and win rate."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    top10 = metrics.head(10)
    sns.barplot(data=top10, x="total_pnl", y="Account", hue="Account", ax=axes[0], palette="viridis", legend=False)
    axes[0].set(title="Top 10 Traders by Total PnL", xlabel="Total PnL (USD)")
    sns.barplot(data=top10, x="win_rate", y="Account", hue="Account", ax=axes[1], palette="magma", legend=False)
    axes[1].set(title="Win Rate", xlabel="Win Rate")
    fig.tight_layout()
    fig.savefig("plots/trader_performance.png", dpi=100)
    plt.close(fig)

if __name__ == "__main__":
    ht = load_historical_trades()
    metrics = compute_trader_metrics(ht)
    print("=== TRADER PERFORMANCE (top 10 by PnL) ===")
    print(metrics.head(10).to_string(index=False))
    os.makedirs("plots", exist_ok=True)
    plot_top_traders(metrics)
    print("\nPlot saved to plots/trader_performance.png")
