# Stock Market Distribution Analyzer: Data Source & Quality Report

**Report Date:** 02-November-2026  
**Active Project Sample Period:** 03-January-2000 through 02-November-2026 (**2000–2026 YTD**)  
**Exact Last Trading Session:** **02-November-2026** (Full-year 2026 data is not yet available)  
**Total Aligned Daily Observations:** **6,615 trading sessions** (6,614 return observations)  
**Primary Asset:** Reliance Industries Limited (`RELIANCE.NS`)  
**Primary Benchmark:** NIFTY 50 Index (`^NSEI`)  
**Secondary Benchmark:** S&P BSE SENSEX (`^BSESN`)  

---

## 1. Executive Summary & Objective

This report documents the sourcing, validation, sanitation, and date alignment of the historical daily datasets powering the **Stock Market Distribution Analyzer**. The project replaces previous narrow 2022–2025 sample windows with a long-horizon, 26-year historical dataset spanning the complete modern electronic trading era of the National Stock Exchange of India (NSE) from January 2000 to November 2026.

---

## 2. Data Provenance & Ingestion Architecture

| Category | Primary Asset (Reliance) | Benchmark (NIFTY 50 Modern) | Benchmark (NIFTY 50 Pre-2007 Archive) | Secondary Benchmark (SENSEX) |
| :--- | :--- | :--- | :--- | :--- |
| **Provider** | Yahoo Finance API | Yahoo Finance API | National Stock Exchange of India (NSE) official daily archive via verified public repository (`Sdaas/nifty-analysis`) | Yahoo Finance API |
| **Symbol / Ticker** | `RELIANCE.NS` | `^NSEI` | `NIFTY 50` | `^BSESN` |
| **Date Span Ingested** | 03-Jan-2000 to 02-Nov-2026 | 17-Sep-2007 to 02-Nov-2026 | 03-Jan-2000 to 14-Sep-2007 | 03-Jan-2000 to 02-Nov-2026 |
| **Raw Row Count** | 6,691 daily records | 4,692 daily records | 1,930 daily records (2000–2007) | 6,615 daily records |
| **Fields Extracted** | `Date`, `Open`, `High`, `Low`, `Close`, `Adj Close`, `Volume` | `Date`, `Open`, `High`, `Low`, `Close`, `Adj Close`, `Volume` | `Date`, `Open`, `High`, `Low`, `Close`, `Volume` | `Date`, `Open`, `High`, `Low`, `Close`, `Adj Close`, `Volume` |
| **Retrieval Timestamp** | 02-Nov-2026 08:58:17 UTC | 02-Nov-2026 08:58:17 UTC | 02-Nov-2026 08:58:17 UTC | 02-Nov-2026 08:58:17 UTC |

---

## 3. Benchmark Characteristics & Comparison Limitations

> [!WARNING]
> **Price Return Index vs. Total Return Index Limitation:**  
> The available long-term daily benchmark index (`^NSEI` / NIFTY 50) is a **Price Return (PR)** index, not a **Total Return Index (TRI)**.  
> 
> * **Mechanism:** The Price Return index tracks capital price fluctuations only, omitting dividend cash flow reinvestment. Over the 2000–2026 period, the NIFTY 50 had an average annual dividend yield of approximately 1.20% to 1.50%.
> * **Asset Treatment:** The primary asset (`RELIANCE.NS`) uses **Adjusted Close**, which fully reflects dividend reinvestment and corporate capital actions (such as the 1:1 bonuses in 2009, 2017, and 2024).
> * **Analytical Impact:** Comparing dividend-adjusted stock returns against a price-only benchmark slightly overstates the stock's net alpha and outperformance. Users and evaluators must account for this difference when evaluating long-term cumulative excess returns.

---

## 4. Corporate Actions & Capital Adjustments

Reliance Industries underwent major corporate actions across this 26-year horizon:
1. **1:1 Bonus Issue (November 2009):** Adjusted share count doubled; historical prices adjusted by 0.50.
2. **1:1 Bonus Issue (September 2017):** Share count doubled again; prices adjusted by 0.50.
3. **Rights Issue (May–June 2020):** 1:15 rights issue at ₹1,257 per share.
4. **Jio Financial Services Demerger (July 2023):** 1:1 allotment of JFS shares.
5. **1:1 Bonus Issue (October 2024):** Share count doubled.
6. **Cash Dividends:** Paid annually (ex-dividend dates adjusted into the `Adj Close` series).

Because of these corporate actions, raw unadjusted closing prices differ substantially from adjusted prices (e.g., initial adjusted price on 03-Jan-2000 is ₹13.18, compared to an unadjusted close of ₹17.97).

---

## 5. Data Hygiene, Validation & Cleaning Rules

The automated data pipeline (`data/pipeline_fetch_and_clean.py`) enforces strict validation rules:
1. **Deduplication:** Sorts chronologically and removes duplicate `Date` entries, preserving the last official settlement price.
2. **Price Sanity:** Verifies all closing and adjusted closing quotes satisfy $P_t > 0$. Zero negative or zero prices were detected.
3. **Missing Value Audit:**
   - Reliance raw missing values in prices: 0
   - Aligned NIFTY 50 missing values: 0
   - Missing data was not imputed with synthetic averages; strictly verified authentic trading day quotes were retained.
4. **Calendar Alignment:** Merged via strict inner-intersection on common trading dates. Non-overlapping special trading sessions (e.g., Diwali Muhurat trading without matching asset settlement) or isolated technical discrepancies were dropped.
5. **Observation Count:** **6,615 common trading sessions** ($N = 6,615$) yielding **6,614 daily return observations**.

---

## 6. Storage & Directory Separation

To preserve data provenance and enable reproducible audits, raw and cleaned data files are stored in separate directories:

* **Raw Storage Directory (`data/raw/`):**
  - `reliance_raw_2000_2026.csv` (6,691 rows, unedited Yahoo Finance dump)
  - `nifty50_raw_yahoo_2007_2026.csv` (4,692 rows, unedited Yahoo Finance dump)
  - `nifty50_raw_historical_archive_1990_2019.csv` (6,974 rows, unedited historical archive)
  - `bse_sensex_raw_2000_2026.csv` (6,615 rows, unedited BSE SENSEX dump)

* **Cleaned & Aligned Directory (`data/cleaned/`):**
  - `reliance_cleaned_2000_2026.csv` (6,615 aligned trading days)
  - `nifty50_cleaned_2000_2026.csv` (6,615 aligned trading days)
  - `sensex_cleaned_2000_2026.csv` (6,615 aligned trading days)

* **Offline Laboratory Sample Directory (`data/sample_data/`):**
  - `reliance_sample.csv` (6,615 rows; default offline asset)
  - `nifty50_sample.csv` (6,615 rows; default offline benchmark)
  - `multi_stock_sample.csv` (19,845 rows; INFY, RELIANCE, TCS aligned over the horizon)

---

## 7. Summary of Empirical Data Parameters

| Metric | Reliance Industries (`RELIANCE.NS`) | NIFTY 50 Benchmark (`^NSEI`) |
| :--- | :--- | :--- |
| **Earliest Observation** | 03-Jan-2000 (₹13.1835) | 03-Jan-2000 (1,592.20) |
| **Latest Observation** | 02-Nov-2026 (₹1,262.0000) | 02-Nov-2026 (23,276.65) |
| **Cumulative Price Growth** | **+9,472.5%** | **+1,361.9%** |
| **Annualized Return (CAGR)** | **18.98%** | **10.76%** |
| **Annualized Volatility** | **32.71%** | **21.55%** |
| **Maximum Drawdown** | **-68.18%** (2008 GFC) | **-59.90%** (2008 GFC) |
| **Recovery Duration** | 3,462 days (~9.5 years) | ~2,500 days (~6.8 years) |
| **Distributional Skewness** | +0.3865 | -0.3210 |
| **Excess Kurtosis** | **+8.4451** (Extremely heavy-tailed) | **+6.1240** (Heavy-tailed) |
