"""CSV parsing, cleaning, and validation provider.

Handles both single-ticker and multi-ticker CSV formats with flexible date parsing,
duplicate detection, positive price validation, and clear error/warning diagnostics.
"""

from __future__ import annotations

import io
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
import numpy as np
import pandas as pd

from config import MIN_OBSERVATIONS_REQUIRED, SAMPLE_DATA_DIR


class CSVValidationError(Exception):
    """Raised when an uploaded or loaded CSV fails structure or data validation."""

    def __init__(self, message: str, errors: Optional[List[str]] = None):
        super().__init__(message)
        self.message = message
        self.errors = errors or []


def clean_column_name(col: str) -> str:
    """Normalize column header to lowercase alphanumeric without punctuation."""
    return "".join(c.lower() for c in str(col).strip() if c.isalnum())


def parse_and_validate_csv(
    file_source: Union[str, Path, io.BytesIO, io.StringIO],
    selected_ticker: Optional[str] = None,
) -> Tuple[pd.DataFrame, Dict]:
    """Parse, validate, and clean a stock price CSV.

    Accepted column variants:
      - Date: 'date', 'timestamp', 'dt'
      - Price: 'adjclose', 'adjustedclose', 'close', 'price'
      - Ticker (optional): 'ticker', 'symbol', 'stock'

    Returns:
        (DataFrame with DatetimeIndex and 'Adj Close', metadata_dict)
    """
    errors: List[str] = []
    warnings: List[str] = []

    try:
        if isinstance(file_source, (str, Path)) and Path(file_source).exists():
            df_raw = pd.read_csv(file_source)
        else:
            df_raw = pd.read_csv(file_source)
    except Exception as e:
        raise CSVValidationError(f"Could not read CSV file: {str(e)}")

    if df_raw.empty:
        raise CSVValidationError("The provided CSV file is empty.")

    # Map column names
    col_map = {clean_column_name(c): c for c in df_raw.columns}

    # Find Date column
    date_col = None
    for candidate in ["date", "timestamp", "datetime", "dt", "tradedate"]:
        if candidate in col_map:
            date_col = col_map[candidate]
            break

    if not date_col:
        raise CSVValidationError(
            "CSV is missing a recognized Date column. Accepted headers: 'Date', 'timestamp', 'TradeDate'.",
            errors=["Missing Date column"],
        )

    # Find Ticker column if present
    ticker_col = None
    for candidate in ["ticker", "symbol", "stock", "stocksymbol"]:
        if candidate in col_map:
            ticker_col = col_map[candidate]
            break

    # If multi-ticker CSV, filter by selected_ticker or pick the first available
    available_tickers: List[str] = []
    if ticker_col is not None:
        available_tickers = [str(t).strip() for t in df_raw[ticker_col].dropna().unique()]
        if not available_tickers:
            warnings.append("Ticker column was found but contains no non-empty values.")
        else:
            chosen_ticker = selected_ticker if (selected_ticker and selected_ticker in available_tickers) else available_tickers[0]
            df_raw = df_raw[df_raw[ticker_col].astype(str).str.strip() == chosen_ticker].copy()
            warnings.append(f"Filtered multi-ticker CSV for symbol '{chosen_ticker}'. Available symbols: {', '.join(available_tickers[:5])}")

    # Find Price column (prefer Adj Close over Close)
    price_col = None
    for candidate in ["adjclose", "adjustedclose", "adjcloseprice", "close", "price", "closingprice", "lastprice"]:
        if candidate in col_map:
            price_col = col_map[candidate]
            break

    if not price_col:
        raise CSVValidationError(
            "CSV is missing a recognized Price column. Accepted headers: 'Adj Close', 'Close', 'Price', 'Adjusted Close'.",
            errors=["Missing Price column"],
        )

    # 1. Parse Dates
    try:
        parsed_dates = pd.to_datetime(df_raw[date_col], errors="coerce", dayfirst=False)
        invalid_date_count = parsed_dates.isna().sum()
        if invalid_date_count > 0:
            warnings.append(f"Removed {invalid_date_count} rows with unparseable or blank dates.")
        df_raw["ParsedDate"] = parsed_dates
        df_clean = df_raw.dropna(subset=["ParsedDate"]).copy()
    except Exception as e:
        raise CSVValidationError(f"Date conversion error: {str(e)}")

    if df_clean.empty:
        raise CSVValidationError("No valid dates remained after date parsing.")

    # 2. Parse Prices as Numeric
    df_clean["Adj Close"] = pd.to_numeric(df_clean[price_col], errors="coerce")
    invalid_price_count = df_clean["Adj Close"].isna().sum()
    if invalid_price_count > 0:
        warnings.append(f"Removed {invalid_price_count} rows with non-numeric price entries.")
    df_clean = df_clean.dropna(subset=["Adj Close"]).copy()

    # 3. Check for positive prices
    non_positive = (df_clean["Adj Close"] <= 0).sum()
    if non_positive > 0:
        warnings.append(f"Removed {non_positive} rows with non-positive prices (<= 0).")
        df_clean = df_clean[df_clean["Adj Close"] > 0].copy()

    # 4. Sort chronologically
    df_clean = df_clean.sort_values(by="ParsedDate").reset_index(drop=True)

    # 5. Check and handle duplicate dates
    dup_mask = df_clean.duplicated(subset=["ParsedDate"], keep="last")
    dup_count = dup_mask.sum()
    if dup_count > 0:
        warnings.append(f"Found and resolved {dup_count} duplicate dates by retaining the latest record per date.")
        df_clean = df_clean[~dup_mask].copy()

    # 6. Minimum observations check
    valid_count = len(df_clean)
    if valid_count < MIN_OBSERVATIONS_REQUIRED:
        raise CSVValidationError(
            f"CSV contains only {valid_count} valid daily records. At least {MIN_OBSERVATIONS_REQUIRED} observations are required for statistical analysis.",
            errors=[f"Insufficient observations ({valid_count} < {MIN_OBSERVATIONS_REQUIRED})"],
        )

    # Prepare final output DataFrame
    df_final = pd.DataFrame(
        {
            "Adj Close": df_clean["Adj Close"].values,
            "Close": df_clean["Adj Close"].values,
        },
        index=pd.DatetimeIndex(df_clean["ParsedDate"], name="Date"),
    )

    metadata = {
        "source": "CSV Upload",
        "row_count": valid_count,
        "first_date": str(df_final.index.min().date()),
        "last_date": str(df_final.index.max().date()),
        "warnings": warnings,
        "available_tickers": available_tickers,
        "selected_ticker": selected_ticker or (available_tickers[0] if available_tickers else "CSV_ASSET"),
        "is_synthetic": False,
    }

    return df_final, metadata


def generate_sample_csv_files(target_dir: Path = SAMPLE_DATA_DIR) -> None:
    """Generate bundled sample CSV files for testing and user demo."""
    target_dir = Path(target_dir)
    target_dir.mkdir(parents=True, exist_ok=True)

    from data.synthetic import generate_synthetic_series

    rel_df, nifty_df = generate_synthetic_series("RELIANCE.NS", "^NSEI", start_date="2022-01-01", end_date="2025-12-31", seed=101)

    # 1. Single series sample: Reliance
    rel_export = rel_df[["Adj Close", "Close", "Volume"]].copy()
    rel_export.to_csv(target_dir / "reliance_sample.csv", index=True)

    # 2. Single series benchmark sample: NIFTY 50
    nifty_export = nifty_df[["Adj Close", "Close", "Volume"]].copy()
    nifty_export.to_csv(target_dir / "nifty50_sample.csv", index=True)

    # 3. Multi-ticker sample
    tcs_df, _ = generate_synthetic_series("TCS.NS", "^NSEI", start_date="2022-01-01", end_date="2025-12-31", seed=202)
    infy_df, _ = generate_synthetic_series("INFY.NS", "^NSEI", start_date="2022-01-01", end_date="2025-12-31", seed=303)

    records = []
    for d, row in rel_df.iterrows():
        records.append({"Date": d.strftime("%Y-%m-%d"), "Ticker": "RELIANCE.NS", "Adj Close": row["Adj Close"], "Volume": row["Volume"]})
    for d, row in tcs_df.iterrows():
        records.append({"Date": d.strftime("%Y-%m-%d"), "Ticker": "TCS.NS", "Adj Close": row["Adj Close"], "Volume": row["Volume"]})
    for d, row in infy_df.iterrows():
        records.append({"Date": d.strftime("%Y-%m-%d"), "Ticker": "INFY.NS", "Adj Close": row["Adj Close"], "Volume": row["Volume"]})

    multi_df = pd.DataFrame(records).sort_values(by=["Date", "Ticker"])
    multi_df.to_csv(target_dir / "multi_stock_sample.csv", index=False)
