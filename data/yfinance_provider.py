"""Yahoo Finance provider with timeout, caching, retry, and ticker normalization for Indian markets."""

from __future__ import annotations

import time
from typing import Optional, Tuple
import pandas as pd
import yfinance as yf

from config import (
    CACHE_TTL_SECONDS,
    DOWNLOAD_TIMEOUT_SECONDS,
    MIN_OBSERVATIONS_REQUIRED,
)
from data.cache import cache


class YFinanceFetchError(Exception):
    """Custom exception with actionable remediation message."""

    def __init__(self, message: str, ticker: str, hint: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.ticker = ticker
        self.hint = hint or "You can switch to Synthetic Demo Data or upload a custom CSV."


def normalize_indian_ticker(ticker: str) -> str:
    """Normalize Indian ticker symbols for Yahoo Finance."""
    t = ticker.strip().upper()
    if not t:
        return "RELIANCE.NS"
    # Indices start with ^
    if t.startswith("^"):
        return t
    # If already has exchange suffix
    if t.endswith(".NS") or t.endswith(".BO"):
        return t
    # Default to National Stock Exchange (.NS)
    return f"{t}.NS"


def fetch_yahoo_series(
    ticker: str,
    start_date: str = "2021-01-01",
    end_date: Optional[str] = None,
    timeout_seconds: int = DOWNLOAD_TIMEOUT_SECONDS,
    max_retries: int = 2,
    use_cache: bool = True,
) -> Tuple[pd.DataFrame, dict]:
    """Fetch historical daily data for a ticker using yfinance with timeout, retry, and caching.

    Returns:
        (DataFrame, metadata_dict)
    Raises:
        YFinanceFetchError if download fails or returns insufficient rows.
    """
    clean_ticker = normalize_indian_ticker(ticker)
    cache_key = f"yf_{clean_ticker}_{start_date}_{end_date or 'today'}"

    if use_cache:
        cached = cache.get(cache_key)
        if cached is not None:
            df, meta = cached
            meta["is_cached"] = True
            return df, meta

    last_exc = None
    for attempt in range(1, max_retries + 1):
        try:
            # Download using yfinance with progress=False
            t_obj = yf.Ticker(clean_ticker)
            df = t_obj.history(
                start=start_date,
                end=end_date,
                interval="1d",
                auto_adjust=False,
                timeout=timeout_seconds,
            )

            if df is None or df.empty or len(df) < MIN_OBSERVATIONS_REQUIRED:
                raise YFinanceFetchError(
                    f"Yahoo Finance returned no or insufficient data for '{clean_ticker}' (got {len(df) if df is not None else 0} rows).",
                    ticker=clean_ticker,
                    hint="Check ticker spelling (e.g., RELIANCE.NS, TCS.NS) or select a wider date range.",
                )

            # Ensure DatetimeIndex without timezone
            if hasattr(df.index, "tz") and df.index.tz is not None:
                df.index = df.index.tz_localize(None)
            df.index.name = "Date"
            df = df.sort_index()

            # Ensure Adj Close exists; fallback to Close if missing
            if "Adj Close" not in df.columns or df["Adj Close"].isna().all():
                if "Close" in df.columns:
                    df["Adj Close"] = df["Close"]
                else:
                    raise YFinanceFetchError(
                        f"Missing price column for '{clean_ticker}'.",
                        ticker=clean_ticker,
                    )

            meta = {
                "source": "Yahoo Finance (Live/Cached)",
                "ticker": clean_ticker,
                "fetched_at": time.time(),
                "fetched_time_str": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
                "row_count": len(df),
                "is_synthetic": False,
                "is_cached": False,
            }

            cache.set(cache_key, df, source="Yahoo Finance", extra_meta=meta)
            return df, meta

        except YFinanceFetchError:
            raise
        except Exception as e:
            last_exc = e
            time.sleep(0.5 * attempt)

    raise YFinanceFetchError(
        f"Failed to fetch market data for '{clean_ticker}' after {max_retries} attempts: {last_exc}",
        ticker=clean_ticker,
        hint="External network may be offline or Yahoo Finance rate limit reached. Switch to 'Synthetic Demo Data' for full offline exploration.",
    )
