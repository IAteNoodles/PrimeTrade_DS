# PrimeTrade DS — Hyperliquid Trader Performance & Market Sentiment Analysis

Analyze the relationship between Hyperliquid trader performance and Bitcoin Fear & Greed Index sentiment. 211k trades, 32 traders, 246 coins across 2018–2025.

## Structure

```
DS/
├── load_datasets.py        — Load, clean, merge CSVs on date
├── explore_data.py         — EDA: F&G timeseries, PnL distribution
├── trader_performance.py   — Per-trader PnL, win rate, fees, volume
├── sentiment_analysis.py   — F&G correlation, scatter/box plots
├── insights.py             — Buy/sell asymmetry, coin analysis, fee drag
├── bonus_analysis.py       — t-test, ANOVA, KMeans clustering, time series decomp, risk metrics
├── generate_report.py      — PDF report generator (15+ pages, all plots embedded)
├── test_analysis.py        — 8 unit tests
├── DS_Analysis_Report.pdf  — Final report with insights & recommendations
└── plots/                  — All generated visualizations
```

## Key Findings

- **Negative sentiment-trading correlation** (r = −0.25) — traders trade more during Fear, less during Greed
- **Best PnL during Extreme Greed** ($67.89 avg) — trade with momentum
- **Sells outperform buys** — 85.9% WR vs 78.0%
- **5 trader clusters** — from high-frequency broad to focused high-conviction
- **4/32 traders** lose more to fees than PnL
- **ANOVA confirms** PnL varies significantly across sentiment (p = 3e-6)

## Usage

```bash
cd DS
pip install pandas matplotlib seaborn scipy scikit-learn statsmodels
pytest test_analysis.py -v        # run tests
python generate_report.py          # regenerate PDF
```

## Report

[DS_Analysis_Report.pdf](DS/DS_Analysis_Report.pdf) — 15+ pages with embedded plots, statistical tests, and 7 actionable recommendations.
