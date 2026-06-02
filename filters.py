"""
filters.py
All filter / data-processing functions for the Ethereum dashboard.
"""

import pandas as pd
import os


DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "ethereum.csv")


# ─────────────────────────────────────────────
# Data loading
# ─────────────────────────────────────────────

def load_data() -> pd.DataFrame:
    """Load the Ethereum CSV dataset."""
    df = pd.read_csv(DATA_PATH, parse_dates=["date"])
    df["date"] = pd.to_datetime(df["date"])
    return df


# ─────────────────────────────────────────────
# Filter helpers
# ─────────────────────────────────────────────

def apply_date_filter(df: pd.DataFrame, start_date, end_date) -> pd.DataFrame:
    """Filter rows between start_date and end_date (inclusive)."""
    mask = (df["date"] >= pd.Timestamp(start_date)) & (df["date"] <= pd.Timestamp(end_date))
    return df[mask].copy()


def apply_year_filter(df: pd.DataFrame, years: list) -> pd.DataFrame:
    """Keep only rows whose year is in the given list."""
    if not years:
        return df
    return df[df["year"].isin(years)].copy()


def apply_price_range_filter(df: pd.DataFrame, min_price: float, max_price: float) -> pd.DataFrame:
    """Keep rows where price is between min_price and max_price."""
    return df[(df["price"] >= min_price) & (df["price"] <= max_price)].copy()


def apply_volume_range_filter(df: pd.DataFrame, min_vol: float, max_vol: float) -> pd.DataFrame:
    """Keep rows where volume_b is between min_vol and max_vol."""
    return df[(df["volume_b"] >= min_vol) & (df["volume_b"] <= max_vol)].copy()


def apply_quarter_filter(df: pd.DataFrame, quarters: list) -> pd.DataFrame:
    """Keep rows whose quarter is in the given list."""
    if not quarters:
        return df
    return df[df["quarter"].isin(quarters)].copy()


def apply_text_search(df: pd.DataFrame, keyword: str) -> pd.DataFrame:
    """Filter rows where the date string contains the keyword."""
    if not keyword.strip():
        return df
    mask = df["date"].astype(str).str.contains(keyword.strip(), case=False, na=False)
    return df[mask].copy()


def reset_filters(df_original: pd.DataFrame) -> pd.DataFrame:
    """Return the full unfiltered dataset."""
    return df_original.copy()


# ─────────────────────────────────────────────
# KPI helpers
# ─────────────────────────────────────────────

def get_kpis(df: pd.DataFrame) -> dict:
    """Compute KPI summary values from (filtered) dataframe."""
    if df.empty:
        return {
            "total_records": 0,
            "avg_price": 0,
            "max_price": 0,
            "min_price": 0,
            "avg_volume_b": 0,
            "avg_market_cap_b": 0,
            "max_market_cap_b": 0,
            "best_day_return": 0,
            "worst_day_return": 0,
            "avg_volatility": 0,
        }
    return {
        "total_records":    len(df),
        "avg_price":        df["price"].mean(),
        "max_price":        df["price"].max(),
        "min_price":        df["price"].min(),
        "avg_volume_b":     df["volume_b"].mean(),
        "avg_market_cap_b": df["market_cap_b"].mean(),
        "max_market_cap_b": df["market_cap_b"].max(),
        "best_day_return":  df["price_change_pct"].max(),
        "worst_day_return": df["price_change_pct"].min(),
        "avg_volatility":   df["volatility_30d"].mean(),
    }
