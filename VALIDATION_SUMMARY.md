# Stock Market Distribution Analyzer: Project Validation Summary

**Evaluation Date:** 02-November-2026  
**Active Project Sample Period:** 03-January-2000 through 02-November-2026 (**2000–2026 YTD**)  
**Exact Last Trading Session:** **02-November-2026** (Full-year 2026 data is not yet available)  
**Total Observations:** **6,615 daily sessions** ($6,614$ return observations)  
**Test Suite Status:** **30 / 30 Automated Unit Tests Passed (100%)** in 8.77 seconds  

---

## 1. Summary of Verification Checks

| Category | Check Performed | Verification Method | Actual Result | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Data Integrity** | Date Coverage & Period Label | Sourced from Yahoo Finance & NSE historical archive; verified range | `2000-01-03` to `2026-11-02` (6,615 aligned trading sessions); labeled **2000–2026 YTD** | **PASSED** |
| **Data Hygiene** | Null / NaN Price Values | `df.isnull().sum()` on prices across all 6,615 rows | **0 nulls** in prices or returns | **PASSED** |
| **Data Hygiene** | Price Positivity & Sanity | Verified $P_t > 0$ on all adjusted and closing quotes | Initial: ₹13.18, Latest: ₹1,262.00; **0 non-positive prices** | **PASSED** |
| **Data Hygiene** | Calendar Alignment | Inner-intersection between Reliance and NIFTY 50 dates | Exact calendar alignment on 6,615 trading days | **PASSED** |
| **Data Architecture** | Raw vs. Cleaned Separation | Physical file inspection in `data/raw/` vs `data/cleaned/` | Separate unedited raw dumps and validated clean CSVs | **PASSED** |
| **Benchmark Limit** | Index Specification | Documented Price Return (PR) vs Total Return Index (TRI) | PR exclusion of dividends (~1.2%–1.5% p.a.) explicitly documented in report and presentation | **PASSED** |
| **Math Invariant** | Compounding Consistency | Simple vs Log compounding: $\exp(\sum r_t) - 1 \equiv \prod(1+R_t) - 1$ | Identical within floating-point tolerance ($< 10^{-10}$) | **PASSED** |
| **Risk Monotonicity**| Tail Ordering | Historical $\text{ES}_{99} \ge \text{VaR}_{99} \ge \text{VaR}_{95}$ | $\text{ES}_{99}=7.57\% \ge \text{VaR}_{99}=5.26\% \ge \text{VaR}_{95}=2.93\%$ | **PASSED** |
| **Distribution Fit**| Heavy-Tail Superiority | Student-$t$ ($\nu=3.64$) vs Gaussian ($\mu, \sigma$) | $\Delta\text{AIC} = -1,310.2$; Student-$t$ KS $p=0.7796$ vs Normal $p=1.79 \times 10^{-23}$ | **PASSED** |
| **Normality Test**  | Jarque-Bera Test | Joint skewness and kurtosis test of normality | Stat = $19,301.9$, $p < 10^{-15}$ (Gaussian decisively rejected) | **PASSED** |
| **Zero Lookahead**  | Future Data Poisoning | Injected $-90\%$ price crash at day $t+1$; checked signal at $t$ | Prior trading decisions and equity curves bitwise identical ($10^{-5}$) | **PASSED** |
| **Model Evaluation**| Out-of-Sample Split | Train (2000–2015, $N=3,946$) vs Test (2016–2026 YTD, $N=2,669$) | Train CAGR: 11.03% (44.7% win rate); Test CAGR: 7.79% (42.9% win rate) | **PASSED** |
| **Period Contrast** | Cross-Decade Dynamics | Evaluated 2000–2009, 2010–2019, and 2020–2026 YTD | Documented regime shifts in volatility, tail heaviness, and drawdowns | **PASSED** |
| **Unit Test Suite** | Automated Pytest Suite | Ran `pytest` across all 8 test modules | **30 passed in 8.77s** | **PASSED** |
| **API Endpoints**   | Flask Server Live Health | Queried `/health`, `/api/analyze`, `/api/analytics/periods` | `status: ok`, `sample_period: 2000–2026 YTD`, loaded 6,615 bars | **PASSED** |
| **Citations**       | Modern Literature Audit | Verified 6 sources from 2018–2026 with publisher DOIs | 100% verified with authors, titles, years, and real DOI links | **PASSED** |

---

## 2. Recomputed Quantitative Baseline Table

| Metric | Full Sample (2000–2026 YTD) | 2000–2009 Decade | 2010–2019 Decade | 2020–2026 YTD | Train (2000–2015) | Test (2016–2026 YTD) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Observation Span** | 03-Jan-2000 to 02-Nov-2026 | 03-Jan-2000 to 31-Dec-2009 | 04-Jan-2010 to 31-Dec-2019 | 01-Jan-2020 to 02-Nov-2026 | 03-Jan-2000 to 31-Dec-2015 | 04-Jan-2016 to 02-Nov-2026 |
| **Daily Sessions ($N$)** | **6,615** | 2,481 | 2,443 | 1,691 | 3,946 | 2,669 |
| **Reliance CAGR** | **18.98%** | 33.13% | 12.37% | 9.84% | 19.65% | 18.20% |
| **Reliance Volatility**| **32.71%** | 40.56% | 26.27% | 27.86% | 36.12% | 26.89% |
| **Skewness** | **+0.3865** | +0.3573 | +0.2225 | +0.3955 | +0.3558 | +0.4346 |
| **Excess Kurtosis** | **+8.4451** | +6.9527 | +2.0778 | +10.6154 | +7.4233 | +8.9458 |
| **Max Drawdown (MDD)**| **-68.18%** (2008 GFC) | -68.18% (2008 GFC) | -39.15% (2012 capex) | -44.08% (COVID 2020) | -68.18% (2008 GFC) | -45.09% (COVID 2020) |
| **MDD Recovery** | **3,462 days (~9.5 yrs)** | Not recovered in decade| 1,500 days | 139 days | Not recovered in period| 179 days |
| **95% Historical VaR**| **2.93%** | 3.61% | 2.56% | 2.32% | 3.23% | 2.31% |
| **95% Expected Shortfall**| **4.47%** | 5.66% | 3.42% | 3.73% | 4.97% | 3.50% |
| **99% Historical VaR**| **5.26%** | 6.84% | 3.93% | 4.03% | 6.27% | 3.91% |
| **99% Expected Shortfall**| **7.57%** | 8.99% | 4.86% | 6.61% | 8.13% | 5.90% |
| **Normal 99% VaR** | **4.70%** (understated)| 5.80% | 3.79% | 4.03% | 5.20% | 3.86% |
| **Student-$t$ Tail ($\nu$)**| **3.64** | 3.44 | 7.15 | 3.36 | 3.85 | 3.96 |
| **Student-$t$ KS $p$-val**| **0.7796** (Accepted) | 0.9878 | 0.7699 | 0.7536 | 0.8260 | 0.9343 |
| **Normal KS $p$-val** | **$1.79 \times 10^{-23}$** (Rejected)| $5.20 \times 10^{-9}$ | 0.0281 | $5.07 \times 10^{-10}$ | $3.90 \times 10^{-12}$ | $3.41 \times 10^{-9}$ |
| **$\Delta\text{AIC}$ ($t$ vs Norm)**| **-1,310.2** | -481.1 | -101.9 | -440.2 | -684.4 | -523.7 |
| **NIFTY 50 CAGR** | **10.76%** | 12.78% | 9.10% | 10.13% | 10.81% | 10.89% |
| **CAPM Beta ($\beta$)**| **1.10** | 1.10 | 1.10 | 1.10 | 1.11 | 1.08 |
| **Correlation ($\rho$)**| **0.73** | 0.76 | 0.65 | 0.70 | 0.75 | 0.65 |
| **Sharpe Ratio ($R_f=6.5\%$)**| **0.50** | 0.75 | 0.33 | 0.24 | 0.50 | 0.51 |
| **Trend Strategy CAGR**| **9.24%** | 24.89% | 0.24% | 2.51% | 11.03% | 7.79% |
| **Strategy Win Rate** | **43.4%** (166 trades) | 55.6% (55 trades) | 41.9% (63 trades) | 30.4% (46 trades) | 44.7% (95 trades) | 42.9% (70 trades) |

---

## 3. Unit Test Execution Details

Running command: `python -m pytest`  
Root directory: `Stock_Return_AI_Lab`  
Execution time: **8.77 seconds**  
Results:
* `tests/test_ai_validation.py`: 3 passed (10%)
* `tests/test_api_endpoints.py`: 6 passed (30%)
* `tests/test_backtest.py`: 2 passed (36%)
* `tests/test_csv_loader.py`: 5 passed (53%)
* `tests/test_distributions.py`: 3 passed (63%)
* `tests/test_returns.py`: 4 passed (76%)
* `tests/test_risk.py`: 4 passed (90%)
* `tests/test_sampling.py`: 3 passed (100%)

All 30 automated tests execute offline without requiring internet access or third-party API credentials.
