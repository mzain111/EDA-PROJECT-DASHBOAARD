"""
fetch_data.py
Downloads Ethereum historical data from CoinGecko API and saves as CSV.
Run this ONCE before launching the dashboard.
"""

import requests
import pandas as pd
import os
import time

def fetch_ethereum_data():
    """Fetch Ethereum OHLC + market data from CoinGecko public API."""
    print("Fetching Ethereum market data from CoinGecko...")

    # CoinGecko free API — market chart (price, market cap, volume) max range
    url = "https://api.coingecko.com/api/v3/coins/ethereum/market_chart"
    params = {
        "vs_currency": "usd",
        "days": "max",
        "interval": "daily"
    }

    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        raw = response.json()
    except Exception as e:
        print(f"Live fetch failed ({e}). Generating synthetic demo data instead...")
        return _generate_demo_data()

    prices      = raw.get("prices", [])
    market_caps = raw.get("market_caps", [])
    volumes     = raw.get("total_volumes", [])

    if not prices:
        print("Empty response. Generating synthetic demo data instead...")
        return _generate_demo_data()

    df_price = pd.DataFrame(prices,      columns=["timestamp", "price"])
    df_mcap  = pd.DataFrame(market_caps, columns=["timestamp", "market_cap"])
    df_vol   = pd.DataFrame(volumes,     columns=["timestamp", "total_volume"])

    df = df_price.merge(df_mcap, on="timestamp").merge(df_vol, on="timestamp")
    df["date"] = pd.to_datetime(df["timestamp"], unit="ms").dt.date
    df = df.drop(columns=["timestamp"])
    df = df.drop_duplicates(subset="date").reset_index(drop=True)

    # Derived columns
    df["price_change_pct"] = df["price"].pct_change() * 100
    df["market_cap_b"]     = df["market_cap"] / 1e9          # billions
    df["volume_b"]         = df["total_volume"] / 1e9
    df["year"]             = pd.to_datetime(df["date"]).dt.year
    df["month"]            = pd.to_datetime(df["date"]).dt.month
    df["month_name"]       = pd.to_datetime(df["date"]).dt.strftime("%b")
    df["quarter"]          = pd.to_datetime(df["date"]).dt.quarter
    df["day_of_week"]      = pd.to_datetime(df["date"]).dt.day_name()

    # Rolling averages
    df["ma_7"]  = df["price"].rolling(7).mean()
    df["ma_30"] = df["price"].rolling(30).mean()
    df["ma_90"] = df["price"].rolling(90).mean()

    # Volatility (30-day rolling std of daily returns)
    df["volatility_30d"] = df["price_change_pct"].rolling(30).std()

    out_path = os.path.join("data", "ethereum.csv")
    df.to_csv(out_path, index=False)
    print(f"Saved {len(df)} rows → {out_path}")
    return df


def _generate_demo_data():
    """Generate realistic synthetic ETH data if API is unavailable (offline env)."""
    import numpy as np
    np.random.seed(42)

    dates = pd.date_range("2015-08-07", "2025-05-01", freq="D")
    n = len(dates)

    # Simulated log-normal price path
    log_returns = np.random.normal(0.001, 0.04, n)
    price = [0.70]
    for r in log_returns[1:]:
        price.append(max(price[-1] * np.exp(r), 0.01))
    price = np.array(price)

    # Scale to realistic ETH history
    scale_factors = np.ones(n)
    # Bull run 2017
    mask17 = (dates >= "2017-01-01") & (dates <= "2018-01-15")
    scale_factors[mask17] = np.linspace(1, 1400, mask17.sum())
    # Crash 2018
    mask18 = (dates >= "2018-01-15") & (dates <= "2018-12-31")
    scale_factors[mask18] = np.linspace(1400, 100, mask18.sum())
    # 2020-2021 bull
    mask21 = (dates >= "2020-10-01") & (dates <= "2021-11-09")
    scale_factors[mask21] = np.linspace(350, 4800, mask21.sum())
    # 2022 bear
    mask22 = (dates >= "2021-11-09") & (dates <= "2022-12-31")
    scale_factors[mask22] = np.linspace(4800, 1200, mask22.sum())
    # 2023-2024 recovery
    mask24 = (dates >= "2023-01-01") & (dates <= "2024-03-01")
    scale_factors[mask24] = np.linspace(1200, 3500, mask24.sum())

    price = scale_factors * (price / price.max())

    market_cap   = price * 120_000_000
    total_volume = market_cap * np.random.uniform(0.03, 0.15, n)

    df = pd.DataFrame({
        "date":         dates.date,
        "price":        price,
        "market_cap":   market_cap,
        "total_volume": total_volume,
    })

    df["price_change_pct"] = df["price"].pct_change() * 100
    df["market_cap_b"]     = df["market_cap"] / 1e9
    df["volume_b"]         = df["total_volume"] / 1e9
    df["year"]             = pd.to_datetime(df["date"]).dt.year
    df["month"]            = pd.to_datetime(df["date"]).dt.month
    df["month_name"]       = pd.to_datetime(df["date"]).dt.strftime("%b")
    df["quarter"]          = pd.to_datetime(df["date"]).dt.quarter
    df["day_of_week"]      = pd.to_datetime(df["date"]).dt.day_name()
    df["ma_7"]             = df["price"].rolling(7).mean()
    df["ma_30"]            = df["price"].rolling(30).mean()
    df["ma_90"]            = df["price"].rolling(90).mean()
    df["volatility_30d"]   = df["price_change_pct"].rolling(30).std()

    os.makedirs("data", exist_ok=True)
    out_path = os.path.join("data", "ethereum.csv")
    df.to_csv(out_path, index=False)
    print(f"[Demo data] Saved {len(df)} rows → {out_path}")
    return df


if __name__ == "__main__":
    fetch_ethereum_data()
