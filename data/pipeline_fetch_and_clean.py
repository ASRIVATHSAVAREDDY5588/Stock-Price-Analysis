"""Historical data ingestion and cleaning pipeline for Stock Market Distribution Analyzer.

Acquires, validates, and aligns daily price histories for Reliance Industries (RELIANCE.NS)
and the NIFTY 50 benchmark (^NSEI) from 2000-01-01 through the latest trading session in 2026.
Saves raw and cleaned datasets separately, and documents data quality.
"""

from __future__ import annotations

import io
import os
import sys
from pathlib import Path
from typing import Dict, Tuple

import numpy as np
import pandas as pd
import requests
import yfinance as yf

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
CLEANED_DIR = PROJECT_ROOT / "data" / "cleaned"
SAMPLE_DIR = PROJECT_ROOT / "data" / "sample_data"

RAW_DIR.mkdir(parents=True, exist_ok=True)
CLEANED_DIR.mkdir(parents=True, exist_ok=True)
SAMPLE_DIR.mkdir(parents=True, exist_ok=True)


def fetch_reliance_raw(start_date: str = "2000-01-01") -> pd.DataFrame:
    """Fetch raw Reliance Industries data from Yahoo Finance."""
    print(f"[1/4] Fetching raw RELIANCE.NS from Yahoo Finance (start={start_date})...")
    raw = yf.download("RELIANCE.NS", start=start_date, auto_adjust=False, progress=False)
    if isinstance(raw.columns, pd.MultiIndex):
        df = pd.DataFrame(index=raw.index)
        for col in ["Open", "High", "Low", "Close", "Adj Close", "Volume"]:
            if (col, "RELIANCE.NS") in raw.columns:
                df[col] = raw[(col, "RELIANCE.NS")]
    else:
        df = raw.copy()

    df.index = pd.to_datetime(df.index).tz_localize(None)
    df.index.name = "Date"
    raw_path = RAW_DIR / "reliance_raw_2000_2026.csv"
    df.to_csv(raw_path)
    print(f" -> Saved {len(df)} raw rows to {raw_path}")
    return df


def fetch_nifty_yahoo_raw(start_date: str = "2007-09-17") -> pd.DataFrame:
    """Fetch raw NIFTY 50 data from Yahoo Finance (^NSEI)."""
    print(f"[2/4] Fetching raw ^NSEI from Yahoo Finance (start={start_date})...")
    raw = yf.download("^NSEI", start=start_date, auto_adjust=False, progress=False)
    if isinstance(raw.columns, pd.MultiIndex):
        df = pd.DataFrame(index=raw.index)
        for col in ["Open", "High", "Low", "Close", "Adj Close", "Volume"]:
            if (col, "^NSEI") in raw.columns:
                df[col] = raw[(col, "^NSEI")]
    else:
        df = raw.copy()

    df.index = pd.to_datetime(df.index).tz_localize(None)
    df.index.name = "Date"
    raw_path = RAW_DIR / "nifty50_raw_yahoo_2007_2026.csv"
    df.to_csv(raw_path)
    print(f" -> Saved {len(df)} raw rows to {raw_path}")
    return df


def fetch_nifty_historical_archive_raw() -> pd.DataFrame:
    """Fetch authentic pre-2007 NIFTY 50 daily index data from NSE archive."""
    print("[3/4] Fetching pre-2007 NIFTY 50 archive (2000-01-03 to 2007-09-14)...")
    url = "https://raw.githubusercontent.com/Sdaas/nifty-analysis/master/NIFTY%2050_Data.csv"
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()

    df_hist = pd.read_csv(io.StringIO(resp.text))
    raw_path = RAW_DIR / "nifty50_raw_historical_archive_1990_2019.csv"
    df_hist.to_csv(raw_path, index=False)

    df_hist["Date"] = pd.to_datetime(df_hist["Date"], format="%d %b %Y", errors="coerce")
    df_hist = df_hist.dropna(subset=["Date", "Close"]).sort_values("Date").set_index("Date")
    df_hist = df_hist[df_hist.index < "2007-09-17"]
    df_hist = df_hist[df_hist.index >= "2000-01-01"]
    df_hist["Adj Close"] = df_hist["Close"]
    df_hist["Volume"] = 0
    return df_hist


def fetch_sensex_raw(start_date: str = "2000-01-01") -> pd.DataFrame:
    """Fetch raw BSE SENSEX (^BSESN) from Yahoo Finance as secondary benchmark."""
    print(f"[4/4] Fetching raw ^BSESN from Yahoo Finance (start={start_date})...")
    raw = yf.download("^BSESN", start=start_date, auto_adjust=False, progress=False)
    if isinstance(raw.columns, pd.MultiIndex):
        df = pd.DataFrame(index=raw.index)
        for col in ["Open", "High", "Low", "Close", "Adj Close", "Volume"]:
            if (col, "^BSESN") in raw.columns:
                df[col] = raw[(col, "^BSESN")]
    else:
        df = raw.copy()

    df.index = pd.to_datetime(df.index).tz_localize(None)
    df.index.name = "Date"
    raw_path = RAW_DIR / "bse_sensex_raw_2000_2026.csv"
    df.to_csv(raw_path)
    print(f" -> Saved {len(df)} raw rows to {raw_path}")
    return df


def clean_and_align_datasets() -> Dict[str, pd.DataFrame]:
    """Execute end-to-end cleaning, deduplication, price sanity, and date alignment."""
    # 1. Fetch raw
    rel_raw = fetch_reliance_raw()
    nifty_yf = fetch_nifty_yahoo_raw()
    nifty_pre2007 = fetch_nifty_historical_archive_raw()
    sensex_raw = fetch_sensex_raw()

    # 2. Assemble complete NIFTY 50 series
    nifty_combined = pd.concat([
        nifty_pre2007[["Open", "High", "Low", "Close", "Adj Close", "Volume"]],
        nifty_yf[["Open", "High", "Low", "Close", "Adj Close", "Volume"]],
    ])
    nifty_combined = nifty_combined[~nifty_combined.index.duplicated(keep="last")].sort_index()

    # 3. Clean individual series
    # Reliance: filter non-positive, drop NaNs in prices
    rel_clean = rel_raw.dropna(subset=["Close", "Adj Close"])
    rel_clean = rel_clean[(rel_clean["Close"] > 0) & (rel_clean["Adj Close"] > 0)]
    rel_clean = rel_clean[~rel_clean.index.duplicated(keep="last")].sort_index()

    # NIFTY 50: filter non-positive, drop NaNs
    nifty_clean = nifty_combined.dropna(subset=["Close", "Adj Close"])
    nifty_clean = nifty_clean[(nifty_clean["Close"] > 0) & (nifty_clean["Adj Close"] > 0)]
    nifty_clean = nifty_clean[~nifty_clean.index.duplicated(keep="last")].sort_index()

    # SENSEX
    sensex_clean = sensex_raw.dropna(subset=["Close", "Adj Close"])
    sensex_clean = sensex_clean[(sensex_clean["Close"] > 0) & (sensex_clean["Adj Close"] > 0)]
    sensex_clean = sensex_clean[~sensex_clean.index.duplicated(keep="last")].sort_index()

    # 4. Find common trading days between Reliance and NIFTY 50
    common_idx = rel_clean.index.intersection(nifty_clean.index)
    common_idx = common_idx.sort_values()

    rel_aligned = rel_clean.loc[common_idx].copy()
    nifty_aligned = nifty_clean.loc[common_idx].copy()

    # Format numeric precision
    for df in [rel_aligned, nifty_aligned]:
        for col in ["Open", "High", "Low", "Close", "Adj Close"]:
            if col in df.columns:
                df[col] = df[col].round(4)
        if "Volume" in df.columns:
            df["Volume"] = df["Volume"].fillna(0).astype(int)

    # 5. Save cleaned datasets
    rel_clean_path = CLEANED_DIR / "reliance_cleaned_2000_2026.csv"
    nifty_clean_path = CLEANED_DIR / "nifty50_cleaned_2000_2026.csv"
    sensex_clean_path = CLEANED_DIR / "sensex_cleaned_2000_2026.csv"

    rel_aligned[["Adj Close", "Close", "Volume"]].to_csv(rel_clean_path)
    nifty_aligned[["Adj Close", "Close", "Volume"]].to_csv(nifty_clean_path)
    sensex_clean[["Adj Close", "Close", "Volume"]].to_csv(sensex_clean_path)

    # 6. Update sample_data files for default offline lab operation
    rel_sample_path = SAMPLE_DIR / "reliance_sample.csv"
    nifty_sample_path = SAMPLE_DIR / "nifty50_sample.csv"

    rel_aligned[["Adj Close", "Close", "Volume"]].to_csv(rel_sample_path)
    nifty_aligned[["Adj Close", "Close", "Volume"]].to_csv(nifty_sample_path)

    # Also build multi_stock_sample.csv covering the long horizon
    # Fetch TCS and INFY aligned on the same dates
    print("Building multi_stock_sample.csv for INFY.NS, RELIANCE.NS, TCS.NS...")
    multi_records = []
    # Add Reliance
    for dt, row in rel_aligned.iterrows():
        multi_records.append({
            "Date": dt.strftime("%Y-%m-%d"),
            "Ticker": "RELIANCE.NS",
            "Adj Close": row["Adj Close"],
            "Close": row["Close"],
            "Volume": row["Volume"],
        })

    # Fetch TCS and INFY
    for tkr in ["TCS.NS", "INFY.NS"]:
        try:
            raw_t = yf.download(tkr, start="2000-01-01", auto_adjust=False, progress=False)
            if isinstance(raw_t.columns, pd.MultiIndex):
                c_adj = raw_t["Adj Close"][tkr]
                c_close = raw_t["Close"][tkr]
                c_vol = raw_t["Volume"][tkr]
            else:
                c_adj = raw_t["Adj Close"]
                c_close = raw_t["Close"]
                c_vol = raw_t["Volume"]
            df_t = pd.DataFrame({"Adj Close": c_adj, "Close": c_close, "Volume": c_vol})
            df_t.index = pd.to_datetime(df_t.index).tz_localize(None)
            df_t_aligned = df_t.reindex(common_idx, method="ffill").bfill()
            for dt, row in df_t_aligned.iterrows():
                multi_records.append({
                    "Date": dt.strftime("%Y-%m-%d"),
                    "Ticker": tkr,
                    "Adj Close": round(float(row["Adj Close"]), 4),
                    "Close": round(float(row["Close"]), 4),
                    "Volume": int(row["Volume"]),
                })
        except Exception as e:
            print(f"Warning: could not fetch {tkr} for multi_stock_sample ({e})")

    multi_df = pd.DataFrame(multi_records).sort_values(["Date", "Ticker"])
    multi_sample_path = SAMPLE_DIR / "multi_stock_sample.csv"
    multi_df.to_csv(multi_sample_path, index=False)
    print(f" -> Saved {len(multi_df)} multi-stock rows to {multi_sample_path}")

    print("\n================== PIPELINE SUMMARY ==================")
    print(f"Active Sample Period: 2000-01-03 to {common_idx.max().strftime('%Y-%m-%d')} (2000–2026 YTD)")
    print(f"Aligned Trading Days: {len(common_idx)} daily sessions")
    print(f"Reliance Initial Adj Close: {rel_aligned['Adj Close'].iloc[0]:.4f} (2000-01-03)")
    print(f"Reliance Latest Adj Close:  {rel_aligned['Adj Close'].iloc[-1]:.4f} ({common_idx.max().strftime('%Y-%m-%d')})")
    print(f"NIFTY 50 Initial Level:     {nifty_aligned['Close'].iloc[0]:.2f} (2000-01-03)")
    print(f"NIFTY 50 Latest Level:      {nifty_aligned['Close'].iloc[-1]:.2f} ({common_idx.max().strftime('%Y-%m-%d')})")
    print("======================================================\n")

    return {
        "reliance": rel_aligned,
        "nifty50": nifty_aligned,
        "sensex": sensex_clean,
    }


if __name__ == "__main__":
    clean_and_align_datasets()
