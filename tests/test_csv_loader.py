"""Tests for CSV validation, cleaning, deduplication, and parsing."""

import io
import pytest
from data.csv_provider import CSVValidationError, parse_and_validate_csv


def test_valid_single_series_csv():
    csv_text = """Date,Adj Close
2024-01-01,2500.5
2024-01-02,2520.0
2024-01-03,2490.2
2024-01-04,2515.1
2024-01-05,2530.0
2024-01-08,2545.0
2024-01-09,2540.0
2024-01-10,2560.0
2024-01-11,2555.0
2024-01-12,2570.0
2024-01-15,2580.0
2024-01-16,2590.0
2024-01-17,2585.0
2024-01-18,2600.0
2024-01-19,2610.0
2024-01-22,2620.0
"""
    df, meta = parse_and_validate_csv(io.StringIO(csv_text))
    assert len(df) == 16
    assert "Adj Close" in df.columns
    assert meta["source"] == "CSV Upload"
    assert df.index.is_monotonic_increasing


def test_duplicate_dates_and_unsorted_order():
    # Out of order dates and duplicate date 2024-01-03
    csv_text = """Date,Close
2024-01-04,104
2024-01-02,102
2024-01-01,100
2024-01-03,103.0
2024-01-03,103.5
2024-01-05,105
2024-01-08,106
2024-01-09,107
2024-01-10,108
2024-01-11,109
2024-01-12,110
2024-01-15,111
2024-01-16,112
2024-01-17,113
2024-01-18,114
2024-01-19,115
"""
    df, meta = parse_and_validate_csv(io.StringIO(csv_text))
    assert df.index.is_monotonic_increasing
    # Duplicate removed (16 input rows, 1 duplicate -> 15 rows)
    assert len(df) == 15
    # Latest duplicate price (103.5) was kept
    assert df.loc["2024-01-03"]["Adj Close"] == 103.5
    assert any("duplicate" in w.lower() for w in meta["warnings"])


def test_insufficient_rows_raises_error():
    # Only 5 rows (< MIN_OBSERVATIONS_REQUIRED=15)
    csv_text = """Date,Adj Close
2024-01-01,100
2024-01-02,102
2024-01-03,101
2024-01-04,103
2024-01-05,104
"""
    with pytest.raises(CSVValidationError) as exc_info:
        parse_and_validate_csv(io.StringIO(csv_text))
    assert "observations are required" in str(exc_info.value).lower() or "insufficient" in str(exc_info.value).lower()


def test_missing_date_column_raises_error():
    csv_text = """Timestamp_wrong,Price
2024-01-01,100
2024-01-02,101
"""
    with pytest.raises(CSVValidationError) as exc_info:
        parse_and_validate_csv(io.StringIO(csv_text))
    assert "missing a recognized Date column" in str(exc_info.value)


def test_multi_ticker_filtering():
    rows = ["Date,Ticker,Close"]
    for i in range(1, 25):
        d = f"2024-01-{i:02d}"
        rows.append(f"{d},TCS.NS,{3500 + i}")
        rows.append(f"{d},INFY.NS,{1500 + i}")
    csv_text = "\n".join(rows)

    df_tcs, meta_tcs = parse_and_validate_csv(io.StringIO(csv_text), selected_ticker="TCS.NS")
    assert len(df_tcs) == 24
    assert meta_tcs["selected_ticker"] == "TCS.NS"
    assert df_tcs["Adj Close"].iloc[0] == 3501

    df_infy, meta_infy = parse_and_validate_csv(io.StringIO(csv_text), selected_ticker="INFY.NS")
    assert len(df_infy) == 24
    assert meta_infy["selected_ticker"] == "INFY.NS"
    assert df_infy["Adj Close"].iloc[0] == 1501
