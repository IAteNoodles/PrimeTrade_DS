"""Load, clean, and merge Fear & Greed Index + historical trade datasets."""

from pathlib import Path
import pandas as pd

DATA_DIR = Path(__file__).parent

def load_fear_greed() -> pd.DataFrame:
    """Load fear_greed_index.csv, parse timestamps/dates, clean column names."""
    df = pd.read_csv(DATA_DIR / "fear_greed_index.csv")
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    df["date"] = pd.to_datetime(df["date"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")
    return df

def load_historical_trades() -> pd.DataFrame:
    """Load historical_data.csv, parse Timestamp IST, extract date for merging."""
    df = pd.read_csv(DATA_DIR / "historical_data.csv")
    df.columns = df.columns.str.strip().str.replace(" ", "_").str.replace("\t", "")
    df["Timestamp_IST"] = pd.to_datetime(df["Timestamp_IST"], format="%d-%m-%Y %H:%M", errors="coerce")
    df["date"] = pd.to_datetime(df["Timestamp_IST"].dt.date)
    return df

def load_merged() -> pd.DataFrame:
    """Merge trades with Fear & Greed sentiment on date (left join)."""
    fg = load_fear_greed()
    ht = load_historical_trades()
    ht = ht.merge(fg[["date", "value", "classification"]], on="date", how="left")
    ht.rename(columns={"value": "fear_greed_value", "classification": "sentiment"}, inplace=True)
    return ht

if __name__ == "__main__":
    merged = load_merged()
    print(f"Fear & Greed rows: {len(load_fear_greed())}")
    print(f"Trade rows: {len(load_historical_trades())}")
    print(f"Merged rows: {len(merged)}, columns: {list(merged.columns)}")
