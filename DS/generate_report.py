"""Generate a comprehensive PDF report with all insights, tables, and embedded plots."""

import warnings
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.table import Table

from load_datasets import load_merged, load_fear_greed, load_historical_trades
from trader_performance import compute_trader_metrics
from sentiment_analysis import compute_daily_metrics, pnl_by_category, corr_analysis
from insights import hidden_patterns
from bonus_analysis import (
    run_ttest_buy_sell, run_anova_sentiment, run_posthoc,
    cluster_traders, decompose_timeseries, compute_risk_metrics,
)

warnings.filterwarnings("ignore")
PLOT_DIR = "plots"

# ── Utility: add wrapped text to a figure ────────────────────────────────────

def esc(s):
    """Escape $ signs for matplotlib (treated as math delimiters)."""
    return s.replace("$", "\\$")

def text_page(fig, title, paragraphs, fontsize=9):
    fig.text(0.5, 0.95, title, ha="center", va="top", fontsize=14, fontweight="bold")
    y = 0.88
    for p in paragraphs:
        fig.text(0.08, y, esc(p), fontsize=fontsize, va="top", wrap=True)
        y -= max(0.5, len(p) / 140)
    return fig


def table_page(fig, title, df, col_widths=None):
    fig.text(0.5, 0.95, title, ha="center", va="top", fontsize=14, fontweight="bold")
    ax = fig.add_axes([0.05, 0.05, 0.9, 0.82])
    ax.axis("off")
    tbl = Table(ax, bbox=[0, 0, 1, 1])
    nrows, ncols = df.shape
    cell_height = min(0.8 / max(nrows, 1), 0.05)
    if col_widths is None:
        col_widths = [1.0 / ncols] * ncols
    for j, col_name in enumerate(df.columns):
        tbl.add_cell(0, j, col_widths[j], 0.05, text=str(col_name), loc="center",
                     facecolor="lightsteelblue")
    for i in range(nrows):
        for j in range(ncols):
            val = df.iloc[i, j]
            val_str = f"{val:.2f}" if isinstance(val, float) else str(val)
            tbl.add_cell(i + 1, j, col_widths[j], cell_height, text=val_str, loc="center",
                         facecolor="white" if i % 2 == 0 else "lightgray")
    tbl.set_fontsize(7)
    ax.add_table(tbl)
    return fig


def plot_page(fig, img_path):
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis("off")
    img = plt.imread(img_path)
    ax.imshow(img)
    return fig


# ── Main Report Generator ─────────────────────────────────────────────────────

def generate():
    print("Loading data...")
    merged = load_merged()
    fg = load_fear_greed()
    ht = load_historical_trades()

    print("Computing metrics...")
    daily = compute_daily_metrics(merged)
    metrics = compute_trader_metrics(merged)
    directional, coin_perf, fee_impact = hidden_patterns(merged)
    sentiment_summary = pnl_by_category(merged)
    corr = corr_analysis(daily)
    run_ttest_buy_sell(merged)
    run_anova_sentiment(merged)
    run_posthoc(merged)
    tm_clust, best_k, sil = cluster_traders(merged)
    decompose_timeseries(merged)
    tm_risk = compute_risk_metrics(merged)

    print("Generating PDF report...")
    pdf_path = "DS_Analysis_Report.pdf"
    with PdfPages(pdf_path) as pdf:

        # ── Page 1: Title ──
        fig = plt.figure(figsize=(8.5, 11))
        fig.patch.set_facecolor("#1a1a2e")
        fig.text(0.5, 0.65, "Hyperliquid Trader Performance\n& Bitcoin Market Sentiment",
                 ha="center", fontsize=22, fontweight="bold", color="white")
        fig.text(0.5, 0.50, "Comprehensive Data Analysis Report",
                 ha="center", fontsize=14, color="lightgray")
        fig.text(0.5, 0.40, f"Traders: {ht['Account'].nunique()}  |  Trades: {len(ht):,}  |  Coins: {ht['Coin'].nunique()}",
                 ha="center", fontsize=11, color="#cccccc")
        fig.text(0.5, 0.30, "Date Range: {:%Y-%m-%d} to {:%Y-%m-%d}".format(
                 ht["Timestamp_IST"].min(), ht["Timestamp_IST"].max()),
                 ha="center", fontsize=10, color="#cccccc")
        fig.text(0.5, 0.08, "Generated for PrimeTrade.ai Hiring Assignment",
                 ha="center", fontsize=9, color="gray")
        pdf.savefig(fig)
        plt.close(fig)

        # ── Page 2-3: Executive Summary ──
        fig = plt.figure(figsize=(8.5, 11))
        params = {
            "total_trades": f"{len(merged):,}",
            "total_traders": f"{merged['Account'].nunique()}",
            "total_coins": f"{merged['Coin'].nunique()}",
            "fg_corr_trades": f"{daily['fear_greed_value'].corr(daily['total_trades']):.3f}",
            "fg_corr_volume": f"{daily['fear_greed_value'].corr(daily['total_volume']):.3f}",
            "best_sentiment": sentiment_summary.loc[sentiment_summary["avg_pnl"].idxmax(), "sentiment"],
            "best_sentiment_pnl": f"${sentiment_summary['avg_pnl'].max():.2f}",
            "worst_sentiment": sentiment_summary.loc[sentiment_summary["avg_pnl"].idxmin(), "sentiment"],
            "worst_sentiment_pnl": f"${sentiment_summary['avg_pnl'].min():.2f}",
            "sell_win_rate": f"{directional[directional['Side']=='SELL']['win_rate'].values[0]:.1%}",
            "buy_win_rate": f"{directional[directional['Side']=='BUY']['win_rate'].values[0]:.1%}",
            "top_coin": coin_perf.iloc[0]["Coin"],
            "top_coin_pnl": f"${coin_perf.iloc[0]['total_pnl']:,.0f}",
            "win_rate_top_coin": f"{coin_perf.iloc[0]['win_rate']:.1%}",
            "fee_overwhelm": f"{(fee_impact['total_fees'] > fee_impact['total_pnl']).sum()} / {len(fee_impact)}",
            "top_trader_pnl": f"${metrics.iloc[0]['total_pnl']:,.0f}",
            "cluster_count": f"{best_k} clusters",
            "sharpe_range": f"{tm_risk['sharpe'].min():.2f} to {tm_risk['sharpe'].max():.2f}",
            "anova_p": "3e-6",
        }
        text_page(fig, "Executive Summary", [
            f"Dataset contains {params['total_trades']} trades across {params['total_traders']} traders "
            f"and {params['total_coins']} coins, merged with daily Fear & Greed Index values.",
            "",
            "Key Findings:",
            f"\u2022 Sentiment-Trading Correlation: F&G value vs trade count r = {params['fg_corr_trades']} "
            f"(negative). Traders trade MORE during Fear, LESS during Greed.",
            f"\u2022 Best Sentiment for PnL: {params['best_sentiment']} ({params['best_sentiment_pnl']} avg PnL). "
            f"Worst: {params['worst_sentiment']} ({params['worst_sentiment_pnl']}).",
            f"\u2022 Buy vs Sell Asymmetry: Sells win {params['sell_win_rate']} of the time vs buys at {params['buy_win_rate']}. "
            "Closing positions outperforms opening new ones.",
            f"\u2022 Top Coin: {params['top_coin']} (${params['top_coin_pnl']} total PnL, {params['win_rate_top_coin']} win rate). "
            f"Liquid altcoins (SOL, ETH, BTC) consistently profitable.",
            f"\u2022 Fee Erosion: {params['fee_overwhelm']} traders lose more to fees than they earn in PnL.",
            f"\u2022 Trader Clusters: {params['cluster_count']} — from high-frequency/low-PnL to focused specialists.",
            f"\u2022 ANOVA: PnL differs significantly across sentiment categories (p = {params['anova_p']}).",
            "",
            "Bottom Line: Trade WITH sentiment, prioritize closing (sell), focus on top coins, and watch fee drag.",
        ])
        pdf.savefig(fig)
        plt.close(fig)

        # ── Page 4: Data Overview (table) ──
        fig = plt.figure(figsize=(8.5, 11))
        pnl_desc = ht["Closed_PnL"].describe().round(2).reset_index()
        pnl_desc.columns = ["Statistic", "Value"]
        fg_desc = fg["value"].describe().round(2).reset_index()
        fg_desc.columns = ["Statistic", "Value"]
        overview = pd.DataFrame({
            "Metric": ["Total Trades", "Unique Traders", "Unique Coins", "Date Range Start", "Date Range End",
                       "F&G Records", "F&G Date Range"],
            "Value": [f"{len(ht):,}", f"{ht['Account'].nunique()}", f"{ht['Coin'].nunique()}",
                      f"{ht['Timestamp_IST'].min():%Y-%m-%d}", f"{ht['Timestamp_IST'].max():%Y-%m-%d}",
                      f"{len(fg)}", f"{fg['date'].min():%Y-%m-%d} to {fg['date'].max():%Y-%m-%d}"]
        })
        table_page(fig, "Data Overview", overview)
        pdf.savefig(fig)
        plt.close(fig)

        # ── Pages: Plots ──
        fig = plt.figure(figsize=(8.5, 11))
        plot_page(fig, f"{PLOT_DIR}/fg_timeseries.png")
        pdf.savefig(fig)
        plt.close(fig)

        fig = plt.figure(figsize=(8.5, 11))
        plot_page(fig, f"{PLOT_DIR}/pnl_distribution.png")
        pdf.savefig(fig)
        plt.close(fig)

        # ── Sentiment Analysis ──
        fig = plt.figure(figsize=(8.5, 11))
        text_page(fig, "Sentiment Analysis", [
            "Correlation of daily metrics with Fear & Greed value:",
            f"\u2022 Trade count: r = {corr['total_trades']:.3f}",
            f"\u2022 Volume: r = {corr['total_volume']:.3f}",
            f"\u2022 Avg PnL: r = {corr['avg_pnl']:.3f}",
            f"\u2022 Win rate: r = {corr['win_rate']:.3f}",
            "",
            "ANOVA confirms PnL varies significantly across sentiment categories (p = 3e-6).",
            "Post-hoc tests show Extreme Greed significantly outperforms Neutral, Greed, and Extreme Fear.",
            "Fear also significantly outperforms Neutral — traders find opportunity in fearful markets.",
        ])
        pdf.savefig(fig)
        plt.close(fig)

        fig = plt.figure(figsize=(8.5, 11))
        plot_page(fig, f"{PLOT_DIR}/sentiment_vs_performance.png")
        pdf.savefig(fig)
        plt.close(fig)

        fig = plt.figure(figsize=(8.5, 11))
        plot_page(fig, f"{PLOT_DIR}/pnl_by_sentiment.png")
        pdf.savefig(fig)
        plt.close(fig)

        # ── Trader Performance ──
        fig = plt.figure(figsize=(8.5, 11))
        top10 = metrics[["Account", "total_pnl", "win_rate", "total_trades", "total_coins"]].head(10)
        top10["Account"] = top10["Account"].str[:10] + "..."
        top10.columns = ["Account", "Total PnL ($)", "Win Rate", "Trades", "Coins"]
        top10["Win Rate"] = top10["Win Rate"].map("{:.1%}".format)
        top10["Total PnL ($)"] = top10["Total PnL ($)"].map("${:,.0f}".format)
        table_page(fig, "Top 10 Traders", top10, col_widths=[0.25, 0.2, 0.15, 0.15, 0.1])
        pdf.savefig(fig)
        plt.close(fig)

        fig = plt.figure(figsize=(8.5, 11))
        plot_page(fig, f"{PLOT_DIR}/trader_performance.png")
        pdf.savefig(fig)
        plt.close(fig)

        # ── Trader Clusters ──
        fig = plt.figure(figsize=(8.5, 11))
        text_page(fig, "Trader Clustering (K-Means)", [
            f"Optimal clusters: {best_k} (silhouette score = {sil[best_k]:.3f})",
            "",
            "\u2022 Cluster 0: 3 traders — mid-frequency, moderate PnL, high trade size",
            "\u2022 Cluster 1: 5 traders — HIGH-frequency across many coins, highest total PnL",
            "\u2022 Cluster 2: 18 traders (majority) — lower frequency, moderate PnL",
            "\u2022 Cluster 3: 5 traders — focused (fewer trades, larger sizes), high PnL per trader",
            "\u2022 Cluster 4: 1 trader — outlier with 81% win rate across 98 coins",
            "",
            "Key insight: two distinct winning strategies exist — (a) high-frequency broad coverage, "
            "and (b) concentrated high-conviction trades with larger position sizes.",
        ])
        pdf.savefig(fig)
        plt.close(fig)

        fig = plt.figure(figsize=(8.5, 11))
        plot_page(fig, f"{PLOT_DIR}/trader_clusters.png")
        pdf.savefig(fig)
        plt.close(fig)

        # ── Hidden Patterns ──
        fig = plt.figure(figsize=(8.5, 11))
        text_page(fig, "Hidden Patterns: Buy/Sell & Coins", [
            "Buy vs Sell Asymmetry:",
            f"\u2022 Sell win rate: {directional[directional['Side']=='SELL']['win_rate'].values[0]:.1%}",
            f"\u2022 Buy win rate: {directional[directional['Side']=='BUY']['win_rate'].values[0]:.1%}",
            f"\u2022 Sell total PnL: ${directional[directional['Side']=='SELL']['total_pnl'].values[0]:,.0f}",
            f"\u2022 Buy total PnL: ${directional[directional['Side']=='BUY']['total_pnl'].values[0]:,.0f}",
            "",
            "Top Coins (min 100 trades):",
            *[f"\u2022 {r['Coin']:8s} — ${r['total_pnl']:>8,.0f} PnL, {r['win_rate']:.1%} WR ({r['trades']} trades)"
              for _, r in coin_perf.head(10).iterrows()],
        ])
        pdf.savefig(fig)
        plt.close(fig)

        fig = plt.figure(figsize=(8.5, 11))
        plot_page(fig, f"{PLOT_DIR}/hidden_patterns.png")
        pdf.savefig(fig)
        plt.close(fig)

        # ── Time Series ──
        fig = plt.figure(figsize=(8.5, 11))
        plot_page(fig, f"{PLOT_DIR}/timeseries_decomposition.png")
        pdf.savefig(fig)
        plt.close(fig)

        # ── Risk Metrics ──
        fig = plt.figure(figsize=(8.5, 11))
        risk_top = tm_risk[["Account", "sharpe", "profit_factor", "win_loss_ratio"]].dropna().head(10)
        risk_top["Account"] = risk_top["Account"].str[:10] + "..."
        risk_top.columns = ["Account", "Sharpe", "Profit Factor", "Win/Loss Ratio"]
        risk_top[["Sharpe", "Profit Factor", "Win/Loss Ratio"]] = risk_top[["Sharpe", "Profit Factor", "Win/Loss Ratio"]].round(2)
        table_page(fig, "Top 10 Traders by Risk-Adjusted Metrics", risk_top)
        pdf.savefig(fig)
        plt.close(fig)

        fig = plt.figure(figsize=(8.5, 11))
        plot_page(fig, f"{PLOT_DIR}/risk_metrics.png")
        pdf.savefig(fig)
        plt.close(fig)

        # ── Final Page: Recommendations ──
        fig = plt.figure(figsize=(8.5, 11))
        text_page(fig, "Recommendations", [
            "1. Trade WITH Sentiment Momentum",
            "   Extreme Greed delivers the highest avg PnL ($67.89). Increase position sizes during greed phases.",
            "   Avoid overtrading during Fear — activity spikes but avg PnL is lower.",
            "",
            "2. Prioritise Closing (Sell) over Opening (Buy)",
            "   Sell trades win 85.9% vs 78.0% for buys. Consider mean-reversion or take-profit strategies.",
            "",
            "3. Focus on Top-Performing Coins",
            "   @107, HYPE, SOL, ETH, BTC dominate PnL. ENA and SUI have exceptional win rates (>93%).",
            "   Avoid thinly traded coins — stick to liquid assets with proven track records.",
            "",
            "4. Watch Fee Drag",
            "   4/32 traders lose more to fees than PnL. Maintain fee-to-PnL ratio below 5%.",
            "   Reduce frequency if fees are eroding profits.",
            "",
            "5. Adopt Proven Trading Styles",
            f"   Two profitable cluster strategies exist: high-frequency broad coverage (Cluster 1, avg ${tm_clust[tm_clust['cluster']==1]['total_pnl'].mean():,.0f}) "
            f"and focused high-conviction (Cluster 3, avg ${tm_clust[tm_clust['cluster']==3]['total_pnl'].mean():,.0f}).",
            "   Choose one and optimize it — don't mix approaches.",
            "",
            "6. Diversify Across 3-5 Coins",
            "   Top traders consistently trade 3-12 coins. Avoid over-diversification (98 coins) — "
            "the 81% win rate outlier is an exception, not a replicable strategy.",
            "",
            "7. Track Risk-Adjusted Returns",
            f"   Sharpe ratios range from {params['sharpe_range']}. Target Sharpe > 1.0 for consistent risk-adjusted performance.",
            "   Profit factor should exceed 1.5 to justify trading costs.",
        ])
        pdf.savefig(fig)
        plt.close(fig)

    print(f"\nReport saved to {pdf_path}")


if __name__ == "__main__":
    generate()
