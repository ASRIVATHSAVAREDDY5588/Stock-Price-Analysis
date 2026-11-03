"""Unified data loading interface for Stock Market Distribution Analyzer.

Coordinates synthetic data generation, Yahoo Finance live/cached fetching,
and CSV file ingestion into a clean, aligned DataPayload.
"""

from __future__ import annotations

import time
from typing import Any, Dict, Optional, Tuple, Union
import pandas as pd

from config import (
    CLEANED_DATA_DIR,
    DEFAULT_BENCHMARK,
    DEFAULT_END_DATE,
    DEFAULT_START_DATE,
    DEFAULT_TICKER,
    MIN_OBSERVATIONS_REQUIRED,
    RAW_DATA_DIR,
    SAMPLE_DATA_DIR,
)
from data.csv_provider import parse_and_validate_csv
from data.synthetic import generate_synthetic_series
from data.yfinance_provider import YFinanceFetchError, fetch_yahoo_series, normalize_indian_ticker


def _load_historical_nifty_archive() -> Optional[pd.DataFrame]:
    """Helper to load pre-2007 authentic NIFTY 50 archive if available."""
    cleaned_nifty = CLEANED_DATA_DIR / "nifty50_cleaned_2000_2026.csv"
    if cleaned_nifty.exists():
        try:
            df = pd.read_csv(cleaned_nifty, parse_dates=["Date"], index_col="Date")
            return df
        except Exception:
            pass

    archive_path = RAW_DATA_DIR / "nifty50_raw_historical_archive_1990_2019.csv"
    if archive_path.exists():
        try:
            df = pd.read_csv(archive_path)
            df["Date"] = pd.to_datetime(df["Date"], format="%d %b %Y", errors="coerce")
            df = df.dropna(subset=["Date", "Close"]).sort_values("Date").set_index("Date")
            df["Adj Close"] = df["Close"]
            return df
        except Exception:
            pass
    return None


class DataPayload:
    """Standardized container for loaded stock and benchmark price histories."""

    def __init__(
        self,
        stock_df: pd.DataFrame,
        benchmark_df: pd.DataFrame,
        ticker: str,
        benchmark_ticker: str,
        source: str,
        is_synthetic: bool,
        last_updated: str,
        warnings: Optional[list] = None,
        extra_meta: Optional[dict] = None,
    ):
        self.stock_df = stock_df
        self.benchmark_df = benchmark_df
        self.ticker = ticker
        self.benchmark_ticker = benchmark_ticker
        self.source = source
        self.is_synthetic = is_synthetic
        self.last_updated = last_updated
        self.warnings = warnings or []
        self.extra_meta = extra_meta or {}

    @property
    def row_count(self) -> int:
        return len(self.stock_df)

    @property
    def date_range_str(self) -> str:
        if self.stock_df.empty:
            return "N/A"
        return f"{self.stock_df.index.min().strftime('%Y-%m-%d')} to {self.stock_df.index.max().strftime('%Y-%m-%d')}"

    def to_dict_summary(self) -> Dict[str, Any]:
        return {
            "ticker": self.ticker,
            "benchmark_ticker": self.benchmark_ticker,
            "source": self.source,
            "is_synthetic": self.is_synthetic,
            "last_updated": self.last_updated,
            "row_count": self.row_count,
            "date_range": self.date_range_str,
            "warnings": self.warnings,
        }


def load_dataset(
    source_type: str = "synthetic",
    ticker: str = DEFAULT_TICKER,
    benchmark_ticker: str = DEFAULT_BENCHMARK,
    start_date: str = DEFAULT_START_DATE,
    end_date: Optional[str] = DEFAULT_END_DATE,
    csv_file: Optional[Any] = None,
    seed: int = 42,
) -> DataPayload:
    """Unified entry point to retrieve and validate price histories.

    Args:
        source_type: 'synthetic', 'yahoo', or 'csv'
        ticker: Target stock symbol (e.g., 'RELIANCE.NS')
        benchmark_ticker: Benchmark symbol (e.g., '^NSEI')
        start_date: Start date string (YYYY-MM-DD)
        end_date: End date string (YYYY-MM-DD or None)
        csv_file: File path or uploaded file object for CSV mode
        seed: Random seed for synthetic reproducibility

    Returns:
        DataPayload ready for statistical return analysis.
    """
    clean_ticker = normalize_indian_ticker(ticker)
    clean_bmk = normalize_indian_ticker(benchmark_ticker)
    warnings = []
    now_str = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())

    if source_type == "synthetic":
        stk_df, bmk_df = generate_synthetic_series(
            ticker=clean_ticker,
            benchmark_ticker=clean_bmk,
            start_date=start_date,
            end_date=end_date or DEFAULT_END_DATE,
            seed=seed,
        )
        return DataPayload(
            stock_df=stk_df,
            benchmark_df=bmk_df,
            ticker=clean_ticker,
            benchmark_ticker=clean_bmk,
            source="Synthetic Demo Engine (Offline/Deterministic)",
            is_synthetic=True,
            last_updated=now_str,
            warnings=["SYNTHETIC DEMO DATA: Modeled with Student-t fat tails for educational testing. Not actual market transactions."],
        )

    elif source_type == "yahoo":
        # Fetch stock
        try:
            stk_df, stk_meta = fetch_yahoo_series(clean_ticker, start_date=start_date, end_date=end_date)
        except Exception as e:
            # Fallback to local sample if Reliance
            if clean_ticker == "RELIANCE.NS" and (SAMPLE_DATA_DIR / "reliance_sample.csv").exists():
                warnings.append(f"Live fetch for '{clean_ticker}' encountered error ({str(e)}). Loaded verified 2000–2026 YTD sample archive.")
                stk_df = pd.read_csv(SAMPLE_DATA_DIR / "reliance_sample.csv", parse_dates=["Date"], index_col="Date")
                stk_meta = {"fetched_time_str": now_str}
            else:
                raise

        # Attempt to fetch benchmark
        try:
            bmk_df, _ = fetch_yahoo_series(clean_bmk, start_date=start_date, end_date=end_date)
        except Exception as e:
            # Check local sample benchmark first
            if clean_bmk == "^NSEI" and (SAMPLE_DATA_DIR / "nifty50_sample.csv").exists():
                warnings.append(f"Live benchmark fetch for '{clean_bmk}' fell back to verified 2000–2026 YTD archive.")
                bmk_df = pd.read_csv(SAMPLE_DATA_DIR / "nifty50_sample.csv", parse_dates=["Date"], index_col="Date")
            else:
                warnings.append(f"Could not fetch live benchmark '{clean_bmk}' ({str(e)}). Substituted synthetic benchmark.")
                _, bmk_df = generate_synthetic_series(ticker=clean_ticker, benchmark_ticker=clean_bmk, start_date=start_date, end_date=end_date or DEFAULT_END_DATE)

        # If benchmark is NIFTY 50 and stock history starts before benchmark (Yahoo ^NSEI starts 2007),
        # splice authentic pre-2007 NIFTY archive
        if clean_bmk == "^NSEI" and not stk_df.empty and not bmk_df.empty:
            if stk_df.index.min() < bmk_df.index.min():
                hist_archive = _load_historical_nifty_archive()
                if hist_archive is not None:
                    pre_2007 = hist_archive[hist_archive.index < bmk_df.index.min()]
                    if not pre_2007.empty:
                        bmk_df = pd.concat([pre_2007, bmk_df])
                        bmk_df = bmk_df[~bmk_df.index.duplicated(keep="last")].sort_index()

        # Inner join on dates to ensure matching observation dates
        common_idx = stk_df.index.intersection(bmk_df.index)
        if len(common_idx) >= MIN_OBSERVATIONS_REQUIRED:
            stk_df = stk_df.loc[common_idx]
            bmk_df = bmk_df.loc[common_idx]
        else:
            warnings.append("Stock and benchmark shared fewer common dates than minimum; retaining independent calendars.")

        return DataPayload(
            stock_df=stk_df,
            benchmark_df=bmk_df,
            ticker=clean_ticker,
            benchmark_ticker=clean_bmk,
            source="Yahoo Finance (Live/Cached)",
            is_synthetic=False,
            last_updated=stk_meta.get("fetched_time_str", now_str),
            warnings=warnings,
        )

    elif source_type == "csv":
        if csv_file is None or csv_file == "sample":
            csv_path = SAMPLE_DATA_DIR / "reliance_sample.csv"
            bmk_path = SAMPLE_DATA_DIR / "nifty50_sample.csv"
            stk_df, csv_meta = parse_and_validate_csv(csv_path, selected_ticker=clean_ticker)
            if bmk_path.exists():
                bmk_df = pd.read_csv(bmk_path, parse_dates=["Date"], index_col="Date")
                common_idx = stk_df.index.intersection(bmk_df.index)
                stk_df = stk_df.loc[common_idx]
                bmk_df = bmk_df.loc[common_idx]
            else:
                _, bmk_df = generate_synthetic_series(ticker="RELIANCE.NS", benchmark_ticker=clean_bmk, start_date="2000-01-01", end_date="2026-11-02")
                bmk_df = bmk_df.reindex(stk_df.index, method="ffill").bfill()

            return DataPayload(
                stock_df=stk_df,
                benchmark_df=bmk_df,
                ticker=clean_ticker,
                benchmark_ticker=clean_bmk,
                source="Bundled Verified Sourced Sample (2000–2026 YTD)",
                is_synthetic=False,
                last_updated=now_str,
                warnings=warnings,
                extra_meta=csv_meta,
            )

        stk_df, csv_meta = parse_and_validate_csv(csv_file, selected_ticker=clean_ticker)
        warnings.extend(csv_meta.get("warnings", []))

        # For benchmark in custom CSV mode: generate synthetic benchmark matching stock's date range
        min_date = stk_df.index.min().strftime("%Y-%m-%d")
        max_date = stk_df.index.max().strftime("%Y-%m-%d")
        _, bmk_df = generate_synthetic_series(
            ticker="RELIANCE.NS",
            benchmark_ticker=clean_bmk,
            start_date=min_date,
            end_date=max_date,
            seed=42,
        )
        # Reindex bmk to exact stock dates
        bmk_df = bmk_df.reindex(stk_df.index, method="ffill").bfill()

        return DataPayload(
            stock_df=stk_df,
            benchmark_df=bmk_df,
            ticker=csv_meta.get("selected_ticker", clean_ticker),
            benchmark_ticker=clean_bmk,
            source="User Uploaded CSV",
            is_synthetic=False,
            last_updated=now_str,
            warnings=warnings,
            extra_meta=csv_meta,
        )

    else:
        raise ValueError(f"Unknown source_type '{source_type}'. Choose 'synthetic', 'yahoo', or 'csv'.")
