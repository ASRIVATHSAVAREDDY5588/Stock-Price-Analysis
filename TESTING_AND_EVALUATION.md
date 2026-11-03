# Testing & Evaluation Guide: Stock Market Distribution Analyzer

The **Stock Market Distribution Analyzer** includes an automated test suite implemented in `pytest`. All tests execute completely offline, using mathematical synthetic series and mock fixtures, requiring neither external internet access nor an OpenAI API key.

---

## 1. Test Suite Architecture

The test suite contains **30 automated test cases** organized across 7 distinct testing modules:

| Test Module | Coverage Area | Key Invariants Verified |
| :--- | :--- | :--- |
| **`test_returns.py`** | Return formulas & series | Arithmetic return $R_t = \frac{P_t}{P_{t-1}}-1$; Log return $r_t = \ln\frac{P_t}{P_{t-1}}$; Cumulative compounding $\exp(\sum r_t)-1 = \prod(1+R_t)-1$; Constant prices ($R_t=0$); Single observation edge cases. |
| **`test_csv_loader.py`** | Data validation & cleaning | Single & multi-ticker CSV parsing; Flexible date parsing; Chronological sorting; Duplicate date elimination (keeping latest quote); Missing/NaN filtering; Minimum observation enforcement ($N \ge 15$). |
| **`test_risk.py`** | Downside & benchmark risk | VaR quantile calculation; Tail ordering ($ES_\alpha \ge VaR_\alpha$); Confidence monotonicity ($VaR_{99\%} > VaR_{95\%}$); Max Drawdown peak, trough, and duration; Rolling volatility $\sqrt{252}$ scaling; CAPM Beta and Correlation. |
| **`test_distributions.py`** | Parametric models & tests | Student-t MLE degrees of freedom ($\nu$) recovery; AIC/BIC model preference on fat-tailed samples; Jarque-Bera normality rejection; Epistemological disclaimer verification. |
| **`test_sampling.py`** | Bootstrap & CLT theory | Bootstrap reproducibility: Identical seeds yield identical confidence intervals; Moving-block bootstrap execution; Central Limit Theorem variance decay ($SE \propto 1/\sqrt{n}$) and kurtosis convergence. |
| **`test_ai_validation.py`** | Schema & grounding audits | Enum validation (`BUY`/`HOLD`/`SELL`; `HIGH`/`MEDIUM`/`LOW`/`INSUFFICIENT_EVIDENCE`); Safety downgrade to `HOLD / INSUFFICIENT_EVIDENCE` when $N < 60$; Sanitization of promotional phrasing; Deterministic baseline directionality. |
| **`test_backtest.py`** | Walk-forward integrity | **Strict zero lookahead:** Alters future prices after day $t$ and verifies past signals and equity remain 100% identical; Verifies transaction cost deduction reduces strategy returns. |
| **`test_api_endpoints.py`** | REST API & web integration | End-to-end execution of `/health`, `/`, `/api/analyze`, `/api/export/csv`, `/api/export/report`, and `/api/sample-csv/<filename>`. |

---

## 2. Walk-Forward Backtesting Evaluation & No-Lookahead Rule

To ensure that historical strategy simulations represent realistic decision-making without hindsight bias, the backtesting engine (`analytics/backtest.py`) follows strict chronological execution rules:

1. **Information Horizon at Time $t$:** At session close on day $t$, moving averages and signals are calculated strictly on $P_{0 \dots t}$.
2. **Lagged Execution at Time $t+1$:** The trade position determined at the close of day $t$ takes effect from close($t$) to close($t+1$).
3. **Transaction Costs:** Slippage and fee deductions (10 bps) are subtracted on every transition between positions (e.g., cash to long or long to cash).

### Automated Verification of the No-Lookahead Invariant
In `tests/test_backtest.py::test_no_lookahead_rule`:
1. A backtest is run on an initial price series from day 0 to 120.
2. A duplicate series is created where prices on days 80 through 120 crash by 90%.
3. The backtest is executed on the modified series.
4. The test verifies that for all days $t < 80$, the cumulative strategy equity paths are identical to within floating-point precision ($10^{-5}$).

---

## 3. How to Run the Test Suite

### Via Windows Batch Launcher
Double-click **`run_tests.bat`** in the project directory.

### Via Command Line
```cmd
cd Stock_Return_AI_Lab
python -m pytest tests -v
```

### Actual Test Execution Output
```
============================= test session starts =============================
platform win32 -- Python 3.11.9, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Users\srivathsava\Documents\antigravity\quirky-bardeen\Stock_Return_AI_Lab
plugins: anyio-4.12.1, cov-7.0.0, typeguard-2.13.3
collected 30 items

tests/test_ai_validation.py::test_validation_enforces_hold_on_short_history PASSED [  3%]
tests/test_ai_validation.py::test_validation_enforces_enum_values PASSED [  6%]
tests/test_ai_validation.py::test_deterministic_baseline_score_direction PASSED [ 10%]
tests/test_api_endpoints.py::test_health_check_endpoint PASSED [ 13%]
tests/test_api_endpoints.py::test_index_page_loads PASSED [ 16%]
tests/test_api_endpoints.py::test_api_analyze_synthetic_pipeline PASSED [ 20%]
tests/test_api_endpoints.py::test_api_export_csv PASSED [ 23%]
tests/test_api_endpoints.py::test_api_export_report PASSED [ 26%]
tests/test_api_endpoints.py::test_sample_csv_download PASSED [ 30%]
tests/test_backtest.py::test_no_lookahead_rule PASSED [ 33%]
tests/test_backtest.py::test_transaction_cost_deduction PASSED [ 36%]
tests/test_csv_loader.py::test_valid_single_series_csv PASSED [ 40%]
tests/test_csv_loader.py::test_duplicate_dates_and_unsorted_order PASSED [ 43%]
tests/test_csv_loader.py::test_insufficient_rows_raises_error PASSED [ 46%]
tests/test_csv_loader.py::test_missing_date_column_raises_error PASSED [ 50%]
tests/test_csv_loader.py::test_multi_ticker_filtering PASSED [ 53%]
tests/test_distributions.py::test_student_t_fit_recovers_heavy_tails PASSED [ 56%]
tests/test_distributions.py::test_gaussian_data_prefers_normal_or_high_df PASSED [ 60%]
tests/test_distributions.py::test_plain_language_disclaimer_present PASSED [ 63%]
tests/test_returns.py::test_simple_and_log_returns_basic PASSED [ 66%]
tests/test_returns.py::test_constant_prices PASSED   [ 70%]
tests/test_returns.py::test_price_index_normalization PASSED [ 73%]
tests/test_returns.py::test_short_history_edge_case PASSED [ 76%]
tests/test_risk.py::test_var_and_expected_shortfall_ordering PASSED [ 80%]
tests/test_risk.py::test_maximum_drawdown_peak_and_trough PASSED [ 83%]
tests/test_risk.py::test_rolling_volatility PASSED   [ 86%]
tests/test_risk.py::test_benchmark_relative_risk PASSED [ 90%]
tests/test_sampling.py::test_bootstrap_reproducibility_with_seed PASSED [ 93%]
tests/test_sampling.py::test_block_bootstrap_execution PASSED [ 96%]
tests/test_sampling.py::test_clt_explorer_variance_decay PASSED [100%]

======================== 30 passed, 1 warning in 4.22s ========================
```
Result: **100% Pass Rate (30 of 30 tests passed).**
