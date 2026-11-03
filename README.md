# Stock Market Distribution Analyzer

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Framework: Flask](https://img.shields.io/badge/Framework-Flask_3.0-green.svg)](https://flask.palletsprojects.com/)
[![Tests: 30 Passed](https://img.shields.io/badge/Tests-30%20Passed-brightgreen.svg)](tests/)
[![Sample: 2000–2026 YTD](https://img.shields.io/badge/Sample-2000--2026%20YTD%20(6%2C615%20Days)-orange.svg)](data/)
[![Distribution: Student-t](https://img.shields.io/badge/Fitted%20Distribution-Student--t%20(%CE%BD%3D3.64)-purple.svg)](analytics/)
[![License: Open Source](https://img.shields.io/badge/License-BSD%2FMIT-lightgrey.svg)](THIRD_PARTY_NOTICES.md)

**Stock Market Distribution Analyzer** is an applied quantitative finance and data science system designed to evaluate empirical asset return distributions, quantify fat-tailed market risks, and deliver transparent, explainable educational guidance for Indian equities. 

Built with **Flask**, **NumPy**, **SciPy**, and **Chart.js**, the platform replaces naive Gaussian assumptions with rigorous heavy-tailed econometric modeling (**Student-$t$ distribution with $\nu = 3.64$ degrees of freedom**), coherent risk metrics (**Value at Risk & Expected Shortfall / CVaR**), and walk-forward trend-following backtests evaluated across a **27-year authentic trading history (2000–2026 YTD, 6,615 daily sessions)**.

---

## 📌 Table of Contents

- [Key Highlights & Project Identity](#-key-highlights--project-identity)
- [Empirical Data & Quality Assurance (2000–2026 YTD)](#-empirical-data--quality-assurance-20002026-ytd)
  - [Sourced Datasets](#sourced-datasets)
  - [Benchmark Comparison Limitation](#benchmark-comparison-limitation)
  - [Raw vs. Cleaned Separation](#raw-vs-cleaned-separation)
- [Quantitative Findings & Econometric Analysis](#-quantitative-findings--econometric-analysis)
  - [1. Long-Horizon Return & Moment Statistics](#1-long-horizon-return--moment-statistics)
  - [2. Normal vs. Student-t Distribution Fit](#2-normal-vs-student-t-distribution-fit)
  - [3. Coherent Risk Measures (VaR & Expected Shortfall)](#3-coherent-risk-measures-var--expected-shortfall)
  - [4. Decadal Regime Shifts (2000–2009, 2010–2019, 2020–2026 YTD)](#4-decadal-regime-shifts-20002009-20102019-20202026-ytd)
  - [5. Walk-Forward Trend Backtest Under Market Friction](#5-walk-forward-trend-backtest-under-market-friction)
- [Explainable AI & Educational Guidance](#-explainable-ai--educational-guidance)
- [Academic Context & Verified Literature Review (2018–2026)](#-academic-context--verified-literature-review-20182026)
- [Presentation Content Pack (22-Slide Mapping)](#-presentation-content-pack-22-slide-mapping)
- [Repository Structure](#-repository-structure)
- [Windows Quickstart & Installation](#-windows-quickstart--installation)
- [Automated Verification & Test Suite](#-automated-verification--test-suite)
- [Regulatory & Academic Disclaimer](#-regulatory--academic-disclaimer)

---

## 🚀 Key Highlights & Project Identity

- **Active Sample Period:** `2000-01-03` to `2026-11-02` (labeled **2000–2026 YTD**; $N = 6,615$ trading sessions, 6,614 daily return observations).
- **Core Asset & Benchmark:** Reliance Industries Ltd (`RELIANCE.NS`) benchmarked against the NIFTY 50 Index (`^NSEI`).
- **Heavy-Tail Superiority:** Maximum Likelihood Estimation proves that the **Student-$t$ distribution ($\Delta\text{AIC} = -1,310.2$, KS $p = 0.7796$)** decisively outperforms the Gaussian normal distribution ($p = 1.79 \times 10^{-23}$), eliminating dangerous underestimation of tail losses.
- **Coherent Risk Metrics:** Computes parametric and non-parametric Value at Risk (VaR) and Expected Shortfall (CVaR) at both 95% and 99% confidence levels.
- **Walk-Forward Validation:** Implements a 20-day / 50-day moving average trend-following strategy with 10 basis points transaction costs, zero look-ahead bias, and an out-of-sample test window (2016–2026 YTD).
- **Deterministic AI Guidance:** An explainable multi-factor guidance engine providing educational BUY/HOLD/SELL signals with transparent factor contribution weights and data sufficiency guards ($\ge 30$ observations).

---

## 📊 Empirical Data & Quality Assurance (2000–2026 YTD)

### Sourced Datasets

| Dataset | File Path | Span | Sessions | Source / Provenance |
| :--- | :--- | :--- | :--- | :--- |
| **Reliance Cleaned** | `data/cleaned/reliance_cleaned_2000_2026.csv` | 2000-01-03 to 2026-11-02 | 6,615 | Yahoo Finance API (`RELIANCE.NS`) |
| **NIFTY 50 Cleaned** | `data/cleaned/nifty50_cleaned_2000_2026.csv` | 2000-01-03 to 2026-11-02 | 6,615 | Official NSE Archive (2000–2007) + Yahoo (`^NSEI`, 2007–2026) |
| **SENSEX Cleaned** | `data/cleaned/sensex_cleaned_2000_2026.csv` | 2000-01-03 to 2026-11-02 | 6,615 | Yahoo Finance API (`^BSESN`) |
| **Multi-Stock Sample** | `data/sample_data/multi_stock_sample.csv` | 2000-01-03 to 2026-11-02 | 19,845 | 3 Tickers (`INFY.NS`, `RELIANCE.NS`, `TCS.NS`; 6,615 rows each) |

### Benchmark Comparison Limitation

> [!WARNING] **Price Return Index vs. Total Return Index Disclosure**
> The NIFTY 50 series used (`^NSEI`) is a **Price Return (PR) index**, which tracks market price movements without accounting for regular cash dividend reinvestment. In contrast, Reliance Industries price series is **dividend-adjusted (Adj Close)**, incorporating all dividend payouts, stock splits, and bonus issues (including bonus shares in 2009, 2017, and 2024). Consequently, comparing Reliance against the NIFTY 50 PR index slightly flatters relative stock alpha by approximately **1.2%–1.5% per annum** (the typical historical dividend yield of the NIFTY 50).

### Raw vs. Cleaned Separation

All raw data downloads are archived unmodified in `data/raw/` to ensure 100% auditability:
- `data/raw/reliance_raw_2000_2026.csv` (Yahoo Finance native download)
- `data/raw/nifty50_raw_yahoo_2007_2026.csv` (Yahoo native benchmark)
- `data/raw/nifty50_raw_historical_archive_1990_2019.csv` (Official NSE India archive)
- `data/raw/bse_sensex_raw_2000_2026.csv` (BSE SENSEX benchmark)

The pipeline (`data/pipeline_fetch_and_clean.py`) enforces strict calendar date intersection across all 6,615 shared trading sessions, eliminates duplicate timestamps, validates positive pricing, and asserts zero missing values.

---

## 📈 Quantitative Findings & Econometric Analysis

### 1. Long-Horizon Return & Moment Statistics

Computed across the full **2000–2026 YTD** horizon ($N = 6,614$ daily return observations):

| Metric | Reliance Industries (`RELIANCE.NS`) | NIFTY 50 Benchmark (`^NSEI`) | Economic Interpretation |
| :--- | :--- | :--- | :--- |
| **Initial Price (2000-01-03)** | ₹13.18 (Adj Close) | 1,592.20 | Reconstructed baseline |
| **Final Price (2026-11-02)** | ₹1,262.00 (Adj Close) | 24,205.35 | Exact recorded trading close |
| **Cumulative Return** | **+9,472.5%** | **+1,420.2%** | $95.7\times$ capital appreciation |
| **CAGR (Annualized Return)** | **18.98%** | **10.76%** | $+8.22\%$ annualized excess return |
| **Annualized Volatility ($\sigma$)** | **32.71%** | **21.84%** | Higher idiosyncratic risk profile |
| **Sample Skewness ($S$)** | **+0.3865** | **-0.2104** | Mild positive asymmetry from rally days |
| **Excess Kurtosis ($\kappa$)** | **+8.4451** | **+7.9124** | **Extreme leptokurtosis (fat tails)** |
| **Jarque-Bera Test Statistic** | **19,301.9** ($p < 10^{-15}$) | **16,842.1** ($p < 10^{-15}$) | **Gaussian normality decisively rejected** |
| **CAPM Beta ($\beta$)** | **1.10** | 1.00 | Systematic market sensitivity |
| **Correlation ($\rho$)** | **0.73** | 1.00 | Strong co-movement with broad market |
| **Sharpe Ratio ($R_f = 6.50\%$)** | **0.50** | 0.38 | Risk-adjusted excess return |

---

### 2. Normal vs. Student-t Distribution Fit

Using Maximum Likelihood Estimation (MLE) across 6,614 daily returns:

$$\text{Gaussian Normal: } f(x; \mu, \sigma) = \frac{1}{\sigma \sqrt{2\pi}} \exp\left(-\frac{(x - \mu)^2}{2\sigma^2}\right)$$

$$\text{Student-}t\text{: } f(x; \nu, \mu, s) = \frac{\Gamma\left(\frac{\nu + 1}{2}\right)}{\Gamma\left(\frac{\nu}{2}\right) \sqrt{\pi \nu} s} \left(1 + \frac{1}{\nu}\left(\frac{x - \mu}{s}\right)^2\right)^{-\frac{\nu + 1}{2}}$$

| Distribution Model | Fitted Parameters | Log-Likelihood | AIC | BIC | KS Test ($p$-value) | Econometric Verdict |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Gaussian Normal** | $\mu = 0.089\%$, $\sigma = 2.061\%$ | $+16,292.4$ | $-32,580.7$ | $-32,567.1$ | $D = 0.0631$ ($p = 1.79 \times 10^{-23}$) | **Decisively Rejected** |
| **Student-$t$** | **$\nu = 3.64$**, $\mu = 0.061\%$, $s = 1.258\%$ | **$+16,948.5$** | **$-33,890.9$** | **$-33,870.5$** | $D = 0.0079$ (**$p = 0.7796$**) | **Overwhelmingly Preferred** |

> [!NOTE] **Model Comparison:** 
> The Student-$t$ distribution achieves an AIC improvement of **$\Delta\text{AIC} = -1,310.2$** and a Kolmogorov-Smirnov test $p$-value of **0.7796** (confirming excellent empirical fit), proving that fat-tail modeling is mathematically required for Indian equity risk management.

---

### 3. Coherent Risk Measures (VaR & Expected Shortfall)

Standard Gaussian Value at Risk severely underestimates the magnitude of tail losses. The table below compares Gaussian parametric risk with empirical Historical VaR and Expected Shortfall (CVaR):

| Confidence Level | Gaussian Parametric VaR | Historical Empirical VaR | Historical Expected Shortfall (ES / CVaR) | Tail Underestimation by Normal Model |
| :--- | :--- | :--- | :--- | :--- |
| **95% Confidence** | 3.30% | **2.93%** | **4.47%** | ES is **52.6% larger** than 95% Historical VaR |
| **99% Confidence** | 4.70% | **5.26%** | **7.57%** | Normal VaR understates 99% ES by **61.1%** |

#### Maximum Drawdown History
- **2008 Global Financial Crisis:** Maximum drawdown of **-68.18%** (Peak: 14-Jan-2008 at ₹364.55 $\to$ Trough: 24-Oct-2008 at ₹115.98). Recovery to previous peak required **3,462 calendar days (9.5 years)**, finally reached on 07-Jul-2017.
- **2020 COVID-19 Shock:** Peak-to-trough drawdown of **-44.08%** (19-Dec-2019 to 23-Mar-2020). Fast recovery: fully reclaimed in **139 calendar days** (09-Aug-2020), catalyzed by Jio Platforms equity raises.

---

### 4. Decadal Regime Shifts (2000–2009, 2010–2019, 2020–2026 YTD)

Market dynamics vary significantly across decadal economic regimes:

| Period Window | Trading Days | Reliance CAGR | Annualized Volatility | Max Drawdown | Fitted $\nu$ (Student-$t$) | Excess Kurtosis | Market Regime Description |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **2000–2009** | 2,497 | **33.13%** | **40.56%** | **-68.18%** | **3.44** | $+6.95$ | Dot-com bust, emerging market bull run, 2008 GFC |
| **2010–2019** | 2,472 | **12.37%** | **26.27%** | **-28.98%** | **7.15** | $+2.08$ | Consolidation, massive 4G/Jio capex, lower volatility |
| **2020–2026 YTD** | 1,646 | **9.84%** | **27.86%** | **-44.08%** | **3.36** | **+10.62** | COVID shock, digital monetization, post-pandemic inflation |

---

### 5. Walk-Forward Trend Backtest Under Market Friction

To verify whether technical moving-average rules produce true risk-adjusted alpha, we evaluated a **20-day / 50-day SMA crossover strategy** with **10 bps transaction fees** deducted on each executed trade:

| Split / Sample Window | Strategy CAGR | Buy & Hold CAGR | Max Drawdown (Strategy) | Max Drawdown (B&H) | Total Trades | Win Rate |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **In-Sample Train (2000–2015)** | 11.03% | **19.65%** | -36.42% | -68.18% | 108 | 44.4% |
| **Out-of-Sample Test (2016–2026 YTD)** | 7.79% | **18.20%** | -28.14% | -44.08% | 58 | 41.4% |
| **Full Sample (2000–2026 YTD)** | 9.24% | **18.98%** | **-36.42%** | **-68.18%** | 166 | 43.4% |

**Key Takeaway:** The trend strategy curtailed drawdowns during market crashes (-36.42% vs -68.18%), but lagged simple Buy & Hold on a total-return basis due to transaction friction and whipsaws during sideways consolidation.

---

## 🤖 Explainable AI & Educational Guidance

The application features an explainable, deterministic multi-factor guidance engine:

1. **Signal Generation:** Computes multi-horizon momentum (20d vs 50d SMA), rolling 30-day volatility relative to historical medians, and current peak drawdown.
2. **Deterministic Weighting:**
   - Trend Momentum: $40\%$ weight
   - Volatility Regime: $30\%$ weight
   - Drawdown Position: $30\%$ weight
3. **Data Sufficiency Safeguard:** Strictly enforces a minimum sample of $N \ge 30$ observations. If fewer rows are provided, the system overrides signals to **HOLD** and issues an explicit data deficiency warning.
4. **Strict Disclaimer:** Signals are labeled as non-personalized academic demonstrations, avoiding deceptive claims of black-box "predictive AI".

---

## 📚 Academic Context & Verified Literature Review (2018–2026)

The system bridges classic econometric foundations with contemporary machine learning and financial risk literature:

### Foundational Context
- **Mandelbrot, B. (1963).** The Variation of Certain Speculative Prices. *Journal of Business*, 36(4), 394–419.
- **Fama, E. F. (1965).** The Behavior of Stock-Market Prices. *Journal of Business*, 38(1), 34–105.
- **Artzner, P., Delbaen, F., Eber, J. M., & Heath, D. (1999).** Coherent Measures of Risk. *Mathematical Finance*, 9(3), 203–228.
- **Künsch, H. R. (1989).** The Jackknife and the Bootstrap for General Stationary Observations. *Annals of Statistics*, 17(3), 1217–1241.
- **Politis, D. N., & Romano, J. P. (1994).** The Stationary Bootstrap. *JASA*, 89(428), 1303–1313.

### Verified Modern Literature (2018–2026)
1. **López de Prado, M. (2018).** *Advances in Financial Machine Learning*. John Wiley & Sons.  
   **DOI:** [10.1002/9781119482109](https://doi.org/10.1002/9781119482109)  
   *Focus: Purging look-ahead leakage, combinatorial cross-validation, and path-dependent transaction cost modeling.*
2. **Taylor, J. W. (2019).** Forecasting Value at Risk and Expected Shortfall Using a Semiparametric Approach Based on the Asymmetric Laplace Distribution. *Journal of Business & Economic Statistics*, 37(1), 121–133.  
   **DOI:** [10.1080/07350015.2017.1281815](https://doi.org/10.1080/07350015.2017.1281815)  
   *Focus: Joint modeling and elicitability of coherent risk measures (VaR and ES).*
3. **Gu, S., Kelly, B., & Xiu, D. (2020).** Empirical Asset Pricing via Machine Learning. *The Review of Financial Studies*, 33(5), 2223–2273.  
   **DOI:** [10.1093/rfs/hhaa009](https://doi.org/10.1093/rfs/hhaa009)  
   *Focus: Comparative analysis of linear, tree, and neural models for risk premia estimation.*
4. **Arrieta, A. B., et al. (2020).** Explainable Artificial Intelligence (XAI): Concepts, taxonomies, opportunities and challenges toward responsible AI. *Information Fusion*, 58, 82–115.  
   **DOI:** [10.1016/j.inffus.2019.12.012](https://doi.org/10.1016/j.inffus.2019.12.012)  
   *Focus: Ethical guidelines, transparency taxonomy, and post-hoc explanation fidelity in automated systems.*
5. **Lim, B., & Zohren, S. (2021).** Time-series forecasting with deep learning: a survey. *Philosophical Transactions of the Royal Society A*, 379(2194), 20200209.  
   **DOI:** [10.1098/rsta.2020.0209](https://doi.org/10.1098/rsta.2020.0209)  
   *Focus: Temporal feature processing, multi-horizon regime shifts, and inductive biases.*
6. **Pesaran, M. H., & Yamagata, T. (2024).** Testing for Alpha in Linear Factor Pricing Models with a Large Number of Securities. *Journal of Financial Econometrics*, 22(2), 407–460.  
   **DOI:** [10.1093/jjfinec/nbad002](https://doi.org/10.1093/jjfinec/nbad002)  
   *Focus: Cross-sectional alpha tests under non-Gaussian error terms and heteroskedasticity.*

---

## 📑 Presentation Content Pack (22-Slide Mapping)

A complete presentation pack mapped to all 22 slides of the review template is maintained in `presentation/`:
- **Content Pack Document:** [`presentation/PRESENTATION_CONTENT_PACK.md`](presentation/PRESENTATION_CONTENT_PACK.md)
- **Verified Facts & JSON Evidence:** [`presentation/slide_facts.json`](presentation/slide_facts.json)
- **High-Resolution Figures:**
  - `presentation/assets/slide02_price_growth.png` (27-Year Price Trajectory & Rebased Growth)
  - `presentation/assets/slide09_return_histogram_fit.png` (Return Histogram with Normal vs. Student-$t$ Overlay)
  - `presentation/assets/slide14_qq_diagnostic_plot.png` (Normal vs. Student-$t$ Q-Q Diagnostic Plots)
  - `presentation/assets/slide15_drawdown_risk.png` (Historical Underwater Drawdown Chart, GFC vs. COVID)
  - `presentation/assets/slide15_period_comparison.png` (Decadal Metrics Comparison: 2000–09, 2010–19, 2020–26)
  - `presentation/assets/slide16_clt_convergence.png` (Central Limit Theorem Mean Return Variance Decay)

---

## 📂 Repository Structure

```text
Stock-Price-Analysis/
├── app.py                             # Flask production application server
├── config.py                          # Global configuration, constants, tickers, and paths
├── requirements.txt                   # Production Python dependencies
├── .env.example                       # Environment configuration template
├── .gitignore                         # Comprehensive Git exclusion rules
├── start_dashboard.bat                # 1-click Windows launcher (starts Flask app)
├── setup_windows.bat                  # 1-click Windows environment setup script
├── run_tests.bat                      # 1-click test runner (executes pytest)
├── README.md                          # Comprehensive project documentation
│
├── analytics/                         # Quantitative econometric modules
│   ├── __init__.py                    # Analytics package initializer
│   ├── returns.py                     # Simple/log returns, annualization, shape moments
│   ├── risk.py                        # Historical/parametric VaR, Expected Shortfall, MDD
│   ├── distributions.py               # Gaussian vs. Student-t MLE fitting, AIC/BIC, KS tests
│   ├── backtest.py                    # Walk-forward SMA strategy, transaction fees
│   ├── ai_agent.py                    # Explainable rule-based guidance engine
│   └── sampling.py                    # IID bootstrap, block bootstrap, CLT simulations
│
├── data/                              # Data storage & pipeline
│   ├── loader.py                      # CSV parsing, multi-ticker filtering, date coercion
│   ├── pipeline_fetch_and_clean.py    # Automated 2000-2026 data ingestion & alignment
│   ├── raw/                           # Unmodified raw historical archives
│   │   ├── reliance_raw_2000_2026.csv
│   │   ├── nifty50_raw_yahoo_2007_2026.csv
│   │   ├── nifty50_raw_historical_archive_1990_2019.csv
│   │   └── bse_sensex_raw_2000_2026.csv
│   ├── cleaned/                       # Aligned, validated 6,615-session datasets
│   │   ├── reliance_cleaned_2000_2026.csv
│   │   ├── nifty50_cleaned_2000_2026.csv
│   │   └── sensex_cleaned_2000_2026.csv
│   └── sample_data/                   # Bundled demo datasets (offline exploration)
│       ├── reliance_sample.csv
│       ├── nifty50_sample.csv
│       └── multi_stock_sample.csv
│
├── templates/                         # Web frontend HTML templates
│   ├── base.html                      # Layout, header, typography, footer
│   └── index.html                     # Interactive dashboard, charts, metric cards, controls
│
├── static/                            # Frontend assets
│   ├── css/styles.css                 # Modern CSS styles (dark theme, responsive)
│   └── js/app.js                      # Client application logic, Chart.js integrations
│
├── tests/                             # Automated test suite (30 test cases)
│   ├── __init__.py
│   ├── conftest.py                    # Pytest test fixtures (sample DataFrames, test clients)
│   ├── test_ai_validation.py          # Signal safety, data sufficiency threshold
│   ├── test_api_endpoints.py          # HTTP routes (/health, /analyze, /export)
│   ├── test_backtest.py               # Look-ahead prevention, fee deductions
│   ├── test_csv_loader.py             # CSV sanitization, sorting, duplicate removal
│   ├── test_distributions.py          # MLE distribution fitting, AIC validation
│   ├── test_returns.py                # Return formulas, edge cases
│   ├── test_risk.py                   # VaR, ES, drawdown ordering
│   └── test_sampling.py               # Bootstrap reproducibility, CLT variance decay
│
├── reports/                           # Reports & automation scripts
│   ├── DATA_SOURCE_AND_QUALITY_REPORT.md # Comprehensive data quality & alignment audit
│   ├── VALIDATION_SUMMARY.md          # Execution log of validation checks
│   ├── project_computed_metrics.json  # Recomputed metrics across all sample periods
│   ├── export.py                      # Markdown report generator
│   ├── generate_presentation_charts.py# Script to render the 6 publication figures
│   ├── update_slide_facts.py          # Script to update slide facts JSON
│   └── build_deliverable_zip.py       # Standalone distribution zip packager
│
├── presentation/                      # Presentation deliverables (22-slide mapping)
│   ├── PRESENTATION_CONTENT_PACK.md   # Complete slide content pack
│   ├── slide_facts.json               # Extracted facts and evidence citations
│   └── assets/                        # 6 high-resolution chart PNGs
│
└── docs/ (Root markdown documents)
    ├── ARCHITECTURE.md                # System component diagram & data flow
    ├── PROJECT_SCOPE.md               # Scope boundaries & mathematical definitions
    ├── SETUP_GUIDE.md                 # Step-by-step setup instructions
    ├── USER_GUIDE.md                  # Detailed walkthrough of dashboard features
    ├── TESTING_AND_EVALUATION.md      # Testing matrix and test coverage
    ├── AI_AND_FINANCIAL_LIMITATIONS.md# Financial risks and AI boundary definitions
    ├── TROUBLESHOOTING.md             # Common issues and resolution steps
    └── THIRD_PARTY_NOTICES.md         # Open-source licenses and attribution
```

---

## 💻 Windows Quickstart & Installation

### Option 1: One-Click Automated Setup (Recommended on Windows)

1. **Clone the repository:**
   ```powershell
   git clone https://github.com/ASRIVATHSAVAREDDY5588/Stock-Price-Analysis.git
   cd Stock-Price-Analysis
   ```

2. **Run setup:**
   Double-click `setup_windows.bat` (or execute in PowerShell). This will create a Python virtual environment (`.venv`) and install all required packages.

3. **Start the application:**
   Double-click `start_dashboard.bat`.

4. **Open in browser:**
   Navigate to [http://127.0.0.1:5000](http://127.0.0.1:5000).

---

### Option 2: Manual Cross-Platform Installation

1. **Create and activate a virtual environment:**
   ```bash
   # Windows PowerShell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1

   # Linux / macOS
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Launch the server:**
   ```bash
   python app.py
   ```

4. **Verify server health:**
   ```bash
   curl http://127.0.0.1:5000/health
   ```

---

## 🧪 Automated Verification & Test Suite

The project includes an extensive test suite implemented in `pytest`, covering data loading, return calculations, distribution fitting, coherent risk metrics, walk-forward backtests, and AI safety validations:

```bash
# Execute test suite
pytest -v
```

**Verification Results:**
```text
============================= 30 passed in 20.47s =============================
tests/test_ai_validation.py::test_validation_enforces_hold_on_short_history PASSED
tests/test_ai_validation.py::test_validation_enforces_enum_values PASSED
tests/test_ai_validation.py::test_deterministic_baseline_score_direction PASSED
tests/test_api_endpoints.py::test_health_check_endpoint PASSED
tests/test_api_endpoints.py::test_index_page_loads PASSED
tests/test_api_endpoints.py::test_api_analyze_synthetic_pipeline PASSED
tests/test_api_endpoints.py::test_api_export_csv PASSED
tests/test_api_endpoints.py::test_api_export_report PASSED
tests/test_api_endpoints.py::test_sample_csv_download PASSED
tests/test_backtest.py::test_no_lookahead_rule PASSED
tests/test_backtest.py::test_transaction_cost_deduction PASSED
tests/test_csv_loader.py::test_valid_single_series_csv PASSED
tests/test_csv_loader.py::test_duplicate_dates_and_unsorted_order PASSED
tests/test_csv_loader.py::test_insufficient_rows_raises_error PASSED
tests/test_csv_loader.py::test_missing_date_column_raises_error PASSED
tests/test_csv_loader.py::test_multi_ticker_filtering PASSED
tests/test_distributions.py::test_student_t_fit_recovers_heavy_tails PASSED
tests/test_distributions.py::test_gaussian_data_prefers_normal_or_high_df PASSED
tests/test_distributions.py::test_plain_language_disclaimer_present PASSED
tests/test_returns.py::test_simple_and_log_returns_basic PASSED
tests/test_returns.py::test_constant_prices PASSED
tests/test_returns.py::test_price_index_normalization PASSED
tests/test_returns.py::test_short_history_edge_case PASSED
tests/test_risk.py::test_var_and_expected_shortfall_ordering PASSED
tests/test_risk.py::test_maximum_drawdown_peak_and_trough PASSED
tests/test_risk.py::test_rolling_volatility PASSED
tests/test_risk.py::test_benchmark_relative_risk PASSED
tests/test_sampling.py::test_bootstrap_reproducibility_with_seed PASSED
tests/test_sampling.py::test_block_bootstrap_execution PASSED
tests/test_sampling.py::test_clt_explorer_variance_decay PASSED
```

---

## ⚖️ Regulatory & Academic Disclaimer

> [!CAUTION] **Non-Advisory Disclosure**
> **Stock Market Distribution Analyzer** is an academic data-science research and software engineering demonstration workbench. It is **not** registered with the Securities and Exchange Board of India (SEBI) as an investment advisor or research analyst. 
> 
> None of the charts, distribution fits, risk statistics, walk-forward backtests, or educational signals constitute financial advice, investment recommendations, or an offer to buy or sell securities. Financial trading in equities, derivatives, and commodities involves substantial risk of permanent capital loss. Past performance, backtested returns, and econometric distribution fits are no guarantee of future results. Always consult a licensed and certified financial advisor before committing real capital to financial markets.

---

**Author:** [A. Srivathsava Reddy](https://github.com/ASRIVATHSAVAREDDY5588)  
**Repository:** [Stock-Price-Analysis](https://github.com/ASRIVATHSAVAREDDY5588/Stock-Price-Analysis)
