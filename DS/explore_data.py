"""Exploratory data analysis: dataset summaries and distributions."""

import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from load_datasets import load_fear_greed, load_historical_trades

def describe_fg(fg: pd.DataFrame):
    """Print Fear & Greed Index summary: count, date range, class balance, stats."""
    print("=== FEAR & GREED INDEX ===")
    print(f"Rows: {len(fg)} | Date range: {fg['date'].min():%Y-%m-%d} to {fg['date'].max():%Y-%m-%d}")
    print(fg["classification"].value_counts().to_string())
    print(fg[["value"]].describe())

def describe_trades(ht: pd.DataFrame):
    """Print historical trades summary: size, traders, coins, PnL stats."""
    print("\n=== HISTORICAL TRADES ===")
    print(f"Rows: {len(ht)} | Traders: {ht['Account'].nunique()} | Coins: {ht['Coin'].nunique()}")
    print(f"Buys: {(ht['Side']=='BUY').sum()} | Sells: {(ht['Side']=='SELL').sum()}")
    print(ht[["Execution_Price", "Size_USD", "Closed_PnL", "Fee"]].describe())

def plot_fg_timeseries(fg: pd.DataFrame):
    """Time series of F&G value with neutral line at 50."""
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.plot(fg["date"], fg["value"], linewidth=0.5, color="tab:blue")
    ax.axhline(50, color="gray", linestyle="--", alpha=0.5)
    ax.set(ylabel="F&G Value", title="Fear & Greed Index Over Time")
    fig.tight_layout()
    fig.savefig("plots/fg_timeseries.png", dpi=100)
    plt.close(fig)

def plot_pnl_distribution(ht: pd.DataFrame):
    """Histogram of Closed PnL (clipped to ±500 to ignore extreme outliers)."""
    fig, ax = plt.subplots(figsize=(10, 4))
    sns.histplot(ht["Closed_PnL"].clip(-500, 500), bins=80, ax=ax)
    ax.set(xlabel="Closed PnL (clipped +/-500)", title="PnL Distribution")
    fig.tight_layout()
    fig.savefig("plots/pnl_distribution.png", dpi=100)
    plt.close(fig)

if __name__ == "__main__":
    fg = load_fear_greed()
    ht = load_historical_trades()
    os.makedirs("plots", exist_ok=True)
    describe_fg(fg)
    describe_trades(ht)
    plot_fg_timeseries(fg)
    plot_pnl_distribution(ht)
    print("\nPlots saved to plots/")
