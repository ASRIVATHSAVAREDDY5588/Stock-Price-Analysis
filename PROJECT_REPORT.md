# Stock Market Distribution Analyzer

### A Project Report Submitted in Partial Fulfilment of the Requirements for the Award of the Degree of
## BACHELOR OF TECHNOLOGY
### In
## DEPARTMENT OF COMPUTER SCIENCE AND ENGINEERING

**By:**

| Student Name | Registration Number |
| :--- | :--- |
| **A. Srivathsava Reddy** | **2420030634** |
| **Aryan Vinayak Salunkhe** | **2420030137** |

**Under the Esteemed Guidance of:**  
**Dr. N. Sunanda**  
*Associate Professor, Department of Computer Science and Engineering*  
*KLH University, Hyderabad*

**Academic Year:** 2026–2027  
**Year:** III, **Semester:** I  

**DEPARTMENT OF COMPUTER SCIENCE AND ENGINEERING**  
**KLH UNIVERSITY**  
*Koneru Lakshmaiah Education Foundation*  
*(Deemed to be University estd. u/s. 3 of the UGC Act, 1956)*  
*Off-Campus: Bachupally-Gandimaisamma Road, Bowrampet, Hyderabad, Telangana – 500 043*  
*Website: www.klh.edu.in*

---

## DECLARATION

The project report entitled **“Stock Market Distribution Analyzer”** is a record of bona fide work completed by **A. Srivathsava Reddy (2420030634)** and **Aryan Vinayak Salunkhe (2420030137)**, submitted in partial fulfilment of the requirements for the award of the degree of **Bachelor of Technology in Computer Science and Engineering** at **KLH University**. 

The work presented in this report is prepared for academic evaluation and, to the best of our knowledge, has not been submitted elsewhere for another award, degree, or diploma.

\
______________________________  
**A. Srivathsava Reddy** (2420030634)  

\
______________________________  
**Aryan Vinayak Salunkhe** (2420030137)  

**Date:** 03 November 2026  
**Place:** Hyderabad, India  

---

## CERTIFICATE

This is to certify that the project report entitled **“Stock Market Distribution Analyzer”** is a bona fide work carried out by **A. Srivathsava Reddy (2420030634)** and **Aryan Vinayak Salunkhe (2420030137)** in partial fulfilment of the requirements for the award of the degree of **Bachelor of Technology in Computer Science and Engineering** at **KLH University** during **Year III, Semester I (Academic Year 2026–2027)**.

\
\
______________________________  
**Dr. N. Sunanda**  
*Project Guide & Associate Professor*  
*Department of CSE, KLH University*  

\
\
______________________________  
**Course Coordinator**  
*Department of CSE, KLH University*  

\
\
______________________________  
**Head of the Department (HOD)**  
*Department of Computer Science and Engineering*  
*KLH University, Hyderabad*  

---

## ACKNOWLEDGEMENT

We sincerely thank everyone who supported us during the development and completion of this project.

We express our profound gratitude to our project guide, **Dr. N. Sunanda**, Associate Professor, Department of Computer Science and Engineering, for her invaluable guidance, continuous encouragement, constructive critiques, and meticulous feedback throughout every phase of our work.

We extend our deep gratitude to **KLH University** and the **Department of Computer Science and Engineering** for providing the state-of-the-art computational infrastructure, academic facilities, and inspiring research environment essential for the execution of this project.

We are also thankful to our faculty members, course coordinators, and department staff for their academic support and cooperation.

Finally, we express our heartfelt thanks to our families, classmates, and friends for their constant encouragement, moral support, and cooperation throughout the course of this work.

\
**A. Srivathsava Reddy** (2420030634)  
**Aryan Vinayak Salunkhe** (2420030137)  

---

## ABSTRACT

The **Stock Market Distribution Analyzer** is an interactive, reproducible quantitative data-science platform engineered for analyzing long-horizon Indian equity returns and tail-risk dynamics. It combines a rigorous data pipeline with return modeling, non-Gaussian probability distribution fitting, coherent downside risk estimation, resampling simulations, chronological trend backtesting, and explainable AI guidance.

The empirical baseline aligns **Reliance Industries adjusted closing prices (`RELIANCE.NS`)** with the **NIFTY 50 price-return benchmark (`^NSEI`)** across a 27-year span from **03 January 2000 through 02 November 2026 year-to-date (2000–2026 YTD)**, containing **6,615 aligned trading sessions and 6,614 daily return observations**. Over this period, Reliance achieved a **Compound Annual Growth Rate (CAGR) of 18.98%** with an **annualized volatility of 32.71%**, compared to the NIFTY 50 PR benchmark CAGR of **10.76%** and volatility of **21.84%**. 

Empirical returns exhibit pronounced leptokurtosis, with sample skewness of **+0.3865** and an excess kurtosis of **+8.4451**. Gaussian normality is decisively rejected by the Jarque-Bera test ($19,301.9, p < 10^{-15}$). Maximum Likelihood Estimation proves that a **Student-$t$ distribution ($\nu = 3.64$)** provides a vastly superior fit over Gaussian models ($\Delta\text{AIC} = -1,310.2$, Kolmogorov-Smirnov $p = 0.7796$). Coherent downside risk analytics reveal a 95% Historical Value at Risk (VaR) of **2.93%** and Expected Shortfall (ES / CVaR) of **4.47%**, alongside a maximum peak-to-trough drawdown of **-68.18%** during the 2008 Global Financial Crisis (requiring 3,462 days to recover).

The system integrates independent and moving-block bootstrap explorers ($B = 1,000$), a Central Limit Theorem (CLT) variance decay simulator, a walk-forward 20d/50d moving average backtest under 10 bps transaction drag, and an explainable, deterministic multi-factor educational BUY/HOLD/SELL engine with a mandatory data-sufficiency safeguard ($N \ge 30$). All 30 automated test cases pass in 8.77 seconds. The project serves as an applied quantitative laboratory; it does not execute live orders or provide personalized financial advice.

**Keywords:** *Indian equities, time-series analytics, return distribution, leptokurtosis, Value at Risk, Expected Shortfall, Student-t distribution, bootstrap, moving-average backtest, explainable AI guidance.*

---

## TABLE OF CONTENTS

| Chapter No. | Chapter Title & Topics | Page No. |
| :---: | :--- | :---: |
| | **Declaration** | 2 |
| | **Certificate** | 3 |
| | **Acknowledgement** | 4 |
| | **Abstract** | 5 |
| **1** | **Introduction**<br>1.1 Background<br>1.2 Problem Statement<br>1.3 Objectives, Scope and Target Users | 7–8 |
| **2** | **System Requirements**<br>2.1 Functional Requirements<br>2.2 Non-Functional Requirements<br>2.3 Hardware and Software Requirements | 9 |
| **3** | **Technology Stack**<br>3.1 Core Language and Web Layer<br>3.2 Data and Analytics Libraries<br>3.3 AI, Configuration and Export Infrastructure | 10 |
| **4** | **System Architecture**<br>4.1 High-Level Flow<br>4.2 Layer Responsibilities<br>4.3 Local Deployment and Security Architecture | 11–12 |
| **5** | **Design**<br>5.1 User Flow and Interaction Lifecycle<br>5.2 Data Model and State Management<br>5.3 Interactive Charts and Visual Presentation | 13 |
| **6** | **Implementation**<br>6.1 Data Ingestion and Cleansing Pipeline<br>6.2 Returns and Summary Moments Engine<br>6.3 Risk Analytics and Distribution Estimation<br>6.4 Resampling and Backtesting Framework | 14–15 |
| **7** | **Features & User Interface**<br>7.1 Data Controls and Performance Overview<br>7.2 Risk Profile and Distribution Diagnostic Tabs<br>7.3 Sampling, Backtesting, and Technical Exports<br>7.4 AI Analysis Guidance and Rule-Based Signal Engine | 16–17 |
| **8** | **Testing & Quality Assurance**<br>8.1 Automated Test Suite Execution<br>8.2 Data Sanitation and Numerical Invariant Verification<br>8.3 Functional Route, Model Fit, and AI Safety Tests | 18–19 |
| **9** | **Deployment & Operation**<br>9.1 Local Windows Setup & Batch Launchers<br>9.2 Environment Configuration, Secrets, and Offline Execution | 20–21 |
| **10** | **Challenges & Limitations**<br>10.1 Data Provenance and Benchmark Pricing Asymmetry<br>10.2 Econometric Non-Stationarity and Strategy Friction<br>10.3 AI Reasoning Boundaries and Operational Constraints | 22–23 |
| **11** | **Future Enhancements**<br>11.1 Quantitative Modeling and Dataset Extensions<br>11.2 Software Product and Educational Features | 24 |
| **12** | **Conclusion**<br>12.1 Project Summary and Key Achievements<br>12.2 Academic Learning Outcomes | 25 |
| **13** | **References**<br>13.1 Market Data Providers and Framework Documentation<br>13.2 Peer-Reviewed Academic Literature (2018–2026)<br>13.3 Internal Project Engineering Specifications | 26–27 |
| **14** | **Appendices**<br>14.1 Appendix A — Data Dictionary<br>14.2 Appendix B — Mathematical Formulas and Market Conventions<br>14.3 Appendix C — Recorded Validation Matrix<br>14.4 Appendix D — User Operating Instructions<br>14.5 Appendix E — Equal Team Contribution Statement | 28–29 |

---

## CHAPTER 1: INTRODUCTION

### 1.1 Background
Daily financial price series form ordered sequences of observations driven by market microstructure, corporate announcements, and macroeconomic shifts. Classical financial engineering models, originated by Markowitz (1952) and Sharpe (1964), predominantly rely on the tractable assumption that asset returns follow a Gaussian Normal distribution. Under this paradigm, extreme price shocks are treated as practically impossible events (six-sigma anomalies).

However, empirical observation across global and Indian equity markets demonstrates that asset returns consistently exhibit leptokurtosis, significant negative or positive skewness, and volatility clustering. Long-run mean returns mask critical risks: severe multi-month drawdowns, catastrophic tail risk, and extended recovery horizons. A robust data-science educational workbench must connect rigorous econometric theory with real-world market observations, allowing learners to inspect the mathematics behind return transformations and risk metrics.

The **Stock Market Distribution Analyzer** provides an interactive, reproducible environment calibrated for the Indian equity market (NSE/BSE). Using Reliance Industries Ltd (`RELIANCE.NS`) as the primary asset and the NIFTY 50 Index (`^NSEI`) as the benchmark, the project covers 27 years of daily trading history (**2000–2026 YTD**), providing empirical proof of heavy-tailed distributions and coherent risk.

### 1.2 Problem Statement
Traditional pedagogical approaches in quantitative finance frequently suffer from three major deficiencies:
1. **Gaussian Complacency:** Standard textbooks introduce Value at Risk (VaR) assuming normality, severely underestimating the frequency and severity of tail losses.
2. **Disjointed Workflows:** Data ingestion, sanitation, econometric estimation, backtesting, and visualization are often scattered across isolated scripts, obscuring how raw inputs translate into outputs.
3. **Black-Box "AI" Systems:** Many contemporary commercial tools present speculative BUY/SELL signals generated by opaque neural networks without explainable factor attribution or data-sufficiency constraints.

The project addresses these problems by constructing a unified, local web application that demonstrates why normality fails, provides coherent risk measures (Expected Shortfall), evaluates strategies with realistic friction, and grounds AI commentary in verified server metrics.

### 1.3 Objectives, Scope and Target Users
* **Core Objectives:**
  1. Ingest, sanitize, and align historical daily stock and benchmark series across 2000–2026 YTD.
  2. Formulate arithmetic and logarithmic returns with 252-session annualization conventions.
  3. Compute parametric and non-parametric Value at Risk (VaR), Expected Shortfall (ES), and maximum underwater drawdowns.
  4. Perform Maximum Likelihood Estimation (MLE) to fit and compare Normal, Student-$t$, and Gaussian Mixture models using AIC/BIC.
  5. Implement IID bootstrap, moving-block bootstrap, and Central Limit Theorem simulators.
  6. Execute a walk-forward 20d/50d trend strategy backtest with 10 bps fees and zero look-ahead bias.
  7. Deliver an explainable AI guidance engine with deterministic factor attribution and safety fallbacks.
* **Scope Boundaries:**
  - **In-Scope:** End-of-day daily market data; offline exploration; statistical diagnostics; educational signals.
  - **Out-of-Scope:** High-frequency tick data; broker order routing; automated live trading; personalized investment advisory.
* **Target Users:** Undergraduate and graduate computer science and data-science students, finance researchers, and quantitative engineering educators.

---

## CHAPTER 2: SYSTEM REQUIREMENTS

### 2.1 Functional Requirements
1. **Data Ingestion:** Load historical CSV files, fetch Yahoo Finance quotes, access bundled samples offline, and generate synthetic Student-$t$ series.
2. **Data Sanitation & Alignment:** Parse dates, eliminate duplicates, filter non-positive prices, and enforce inner-date calendar intersections between asset and benchmark.
3. **Statistical Computation:** Calculate daily/annualized returns, volatility, skewness, excess kurtosis, and Jarque-Bera normality tests.
4. **Distribution Fitting:** Fit Gaussian Normal and Student-$t$ distributions via MLE; compute log-likelihood, AIC, BIC, and Kolmogorov-Smirnov statistics.
5. **Downside Risk Estimation:** Evaluate 95% and 99% historical and parametric VaR, Expected Shortfall (CVaR), and full underwater drawdown profiles.
6. **Resampling & Backtesting:** Provide 1,000-iteration bootstrap distributions and execute lagged 20d/50d SMA strategy simulations with 10 bps fees.
7. **Explainable Guidance:** Output deterministic BUY/HOLD/SELL signals with factor weights and data-sufficiency guards ($N \ge 30$).
8. **Export Facilities:** Export sanitized CSV series and downloadable Markdown technical reports.

### 2.2 Non-Functional Requirements
1. **Mathematical Reproducibility:** Resampling and simulation engines must produce identical results under seeded random states.
2. **Zero Look-Ahead Integrity:** Backtest positions formed on day $t$ close must execute strictly on day $t+1$.
3. **Graceful Error Handling:** Invalid uploads or truncated series must generate explicit user feedback without server termination.
4. **Zero-Configuration Offline Execution:** All primary features must execute completely offline using bundled datasets and local libraries.
5. **Security & Credential Isolation:** External API keys must reside solely in server-side `.env` files and never leak to client JavaScript.

### 2.3 Hardware and Software Requirements
* **Hardware:**
  - Standard PC/laptop running Windows 10/11, macOS, or Linux.
  - Minimum 4 GB RAM (8 GB recommended for large bootstrap simulations).
  - 500 MB free hard drive space.
  - No GPU or specialized hardware accelerators required.
* **Software:**
  - Python 3.10 to 3.12 (Python 3.11.9 reference build).
  - Modern HTML5 web browser (Google Chrome, Mozilla Firefox, Microsoft Edge).
  - Dependencies: Flask, NumPy, Pandas, SciPy, Statsmodels, scikit-learn, Plotly.js, Chart.js, Pytest.

---

## CHAPTER 3: TECHNOLOGY STACK

### 3.1 Core Language & Web Layer
- **Python 3.11.9:** Primary computational backend language providing high numerical precision and rich scientific ecosystem support.
- **Flask 3.1.0:** Lightweight, robust WSGI web application framework managing routing, file uploads, session state, and JSON endpoints.
- **Jinja2:** Template rendering engine dynamically generating HTML views.
- **HTML5 & Modern CSS3:** Custom responsive layout featuring a dark-themed quantitative trading terminal aesthetic.
- **JavaScript (ES6+):** Client-side controller orchestrating asynchronous AJAX calls and dynamic UI updates without page reloads.

### 3.2 Data and Analytics Libraries
- **Pandas 2.2.3:** High-performance tabular data structures managing datetime indexing, calendar alignment, and rolling windows.
- **NumPy 2.2.1:** Low-level vector and matrix mathematics powering return transformations and seeded pseudo-random resampling.
- **SciPy 1.15.0 (`scipy.stats`):** Maximum Likelihood Estimation for continuous probability distributions, KS goodness-of-fit tests, and degrees-of-freedom optimization.
- **Statsmodels 0.14.4:** Econometric diagnostics including Jarque-Bera test statistics and quantile calculations.
- **scikit-learn 1.6.1:** Expectation-Maximization (EM) implementation for two-component Gaussian Mixture Models (2-GMM).
- **Chart.js 4.4.1 & Plotly.js 2.35.2:** Client-side charting engines rendering interactive zoomable time-series, histograms, Q-Q plots, and drawdown charts.

### 3.3 AI, Configuration & Export Infrastructure
- **Pydantic 2.10.4:** Strict schema validation enforcing typed numeric boundaries on AI commentary responses.
- **python-dotenv 1.0.1:** Environment variable isolation reading `.env` configuration securely.
- **Pytest 9.0.2:** Automated regression testing harness executing 30 test cases across analytics and API endpoints.

---

## CHAPTER 4: SYSTEM ARCHITECTURE

### 4.1 High-Level Flow
The system adopts a strictly decoupled, modular architecture segregating data ingestion, numerical analytics, business logic, presentation, and exports:

```text
+-------------------------------------------------------------------------+
|                              DATA LAYER                                 |
|  Yahoo Finance Provider  |  Historical NSE Archive  |  CSV Upload / Sample |
+-------------------------------------------------------------------------+
                                    │
                                    ▼
+-------------------------------------------------------------------------+
|                           VALIDATION LAYER                              |
|   Date Parsing  |  Deduplication  |  Price Sanity  |  Calendar Alignment   |
+-------------------------------------------------------------------------+
                                    │
                                    ▼
+-------------------------------------------------------------------------+
|                           ANALYTICS ENGINE                              |
|   returns.py    |   distributions.py   |   risk.py   |   sampling.py    |
+-------------------------------------------------------------------------+
                                    │
                                    ▼
+-------------------------------------------------------------------------+
|                         AI GUIDANCE & BACKTEST                          |
|   Multi-Factor Guidance Engine (ai_agent.py) | SMA Strategy (backtest.py)|
+-------------------------------------------------------------------------+
                                    │
                                    ▼
+-------------------------------------------------------------------------+
|                         WEB PRESENTATION LAYER                          |
|   Flask Controller (app.py)  <--->  Interactive Browser UI (Chart.js)  |
+-------------------------------------------------------------------------+
```

### 4.2 Layer Responsibilities
1. **Data Layer (`data/`):** Unified loader abstracting heterogeneous data inputs into standardized pandas DataFrames indexed by normalized UTC dates.
2. **Analytics Engine (`analytics/`):** Pure Python modules implementing mathematical calculations independently of web controllers, enabling isolated testing and reusability.
3. **Guidance Engine (`analytics/ai_agent.py`):** Deterministic multi-factor scoring algorithm translating statistical signals into transparent, plain-language educational guidance.
4. **Web & Presentation Layer (`templates/`, `static/`, `app.py`):** Flask controllers exposing REST endpoints (`/api/analyze`, `/export/csv`, `/export/report`) and serving responsive HTML/CSS/JS assets.

### 4.3 Local Deployment & Security Architecture
- The application executes locally on loopback address `http://127.0.0.1:5000`.
- All data remains on the user's local machine; no proprietary financial records or student uploads are transmitted to third-party cloud servers.
- AI credentials, if supplied, are accessed exclusively by server-side Python processes via `os.environ`; client-side JavaScript never receives or stores API tokens.

---

## CHAPTER 5: DESIGN

### 5.1 User Flow and Interaction Lifecycle
1. **Configuration Selection:** The user selects a preloaded ticker (e.g., `RELIANCE.NS`), benchmark (`^NSEI`), date range, or uploads a custom CSV file via drag-and-drop.
2. **Pipeline Trigger:** Clicking "Analyze Distribution" initiates an asynchronous AJAX `POST` request to `/api/analyze`.
3. **Execution & Metric Card Update:** The backend processes data through the analytics engine and returns a structured JSON response in $< 200$ ms, updating high-level summary cards (CAGR, Volatility, Max DD, VaR 95%, ES 95%, Signal).
4. **Tab Navigation:** The user explores specialized tabs: Overview, Return Distribution, Tail Risk & Drawdowns, Sampling & CLT Explorer, Walk-Forward Backtest, and Explainable AI Guidance.
5. **Export Generation:** Users download the sanitized dataset as CSV or export a comprehensive Markdown report.

### 5.2 Data Model and State Management
The canonical data record is an aligned time-series DataFrame indexed by date with four mandatory columns:
- `Date` (datetime64[ns], unique, monotonically increasing)
- `Adj Close` (float64, strictly positive, split- and dividend-adjusted)
- `Benchmark` (float64, strictly positive, aligned trading sessions)
- `Volume` (int64/float64, traded volume where available)

Derived columns computed dynamically include: `Simple Return`, `Log Return`, `Cumulative Return`, `Peak Price`, `Drawdown`, and `Rolling Volatility (21d)`.

### 5.3 Charts and Visual Presentation
- **Price Growth:** Rebased asset vs. benchmark series ($100$ at start) on semi-log scale.
- **Return Histogram:** Normalized probability density histogram overlaid with fitted Gaussian Normal and Student-$t$ probability density functions.
- **Quantile-Quantile (Q-Q) Diagnostics:** Side-by-side empirical vs. theoretical quantile plots demonstrating tail divergence.
- **Underwater Drawdown:** Filled area chart highlighting depth and duration of historical capital drawdowns.

---

## CHAPTER 6: IMPLEMENTATION

### 6.1 Data Ingestion and Cleansing Pipeline
- The pipeline (`data/pipeline_fetch_and_clean.py`) downloads Reliance Industries (`RELIANCE.NS`) and NIFTY 50 (`^NSEI`) quotes from Yahoo Finance.
- Pre-2007 NIFTY 50 prices are integrated from the official NSE historical archive.
- The pipeline enforces strict calendar date intersection across all 6,615 sessions, validates positive pricing, and archives raw downloads in `data/raw/` separately from cleaned production files in `data/cleaned/`.

### 6.2 Returns and Summary Moments Engine
- Simple arithmetic and logarithmic returns are computed per session.
- Skewness ($S = +0.3865$) and excess kurtosis ($\kappa = +8.4451$) are calculated using unbiased moment estimators.
- Annualization applies the 252-day market convention ($\text{CAGR} = 18.98\%$, $\sigma_{\text{ann}} = 32.71\%$).

### 6.3 Risk Analytics and Distribution Estimation
- **Parametric vs. Historical VaR:** Gaussian VaR 95% is $3.30\%$, while empirical Historical VaR 95% is **$2.93\%$**. At the 99% level, Historical VaR expands to **$5.26\%$** (exceeding Gaussian VaR of $4.70\%$).
- **Expected Shortfall:** Historical 95% ES reaches **$4.47\%$** ($52.6\%$ larger than Historical VaR). Historical 99% ES reaches **$7.57\%$**.
- **Distribution Estimation:** SciPy `stats.t.fit()` optimizes the Student-$t$ distribution via MLE, yielding $\nu = 3.64$, $\mu = 0.061\%$, and scale $s = 1.258\%$, with $\text{AIC} = -33,890.9$ (compared to Gaussian Normal $\text{AIC} = -32,580.7$).

### 6.4 Sampling and Backtesting Framework
- **Bootstrap Engine:** Runs $1,000$ iterations using both IID and 5-day moving-block resampling to construct 95% confidence intervals for mean and volatility.
- **Backtesting Simulation:** 20-day vs. 50-day SMA crossover executes with a 1-day lag and deducts 10 bps per trade across 166 round-turn trades.

---

## CHAPTER 7: FEATURES

### 7.1 Data Controls and Performance Overview
- Pre-configured dropdowns for Reliance Industries, TCS, Infosys, HDFC Bank, ICICI Bank, and NIFTY 50.
- Custom CSV file uploader supporting standard Yahoo Finance, Google Finance, and NSE export formats.
- Interactive summary cards reporting cumulative growth, CAGR, annual volatility, and beta.

### 7.2 Risk Profile and Distribution Diagnostic Tabs
- Dynamic histogram featuring interactive bin-width adjustments and probability curve overlays.
- Dual Q-Q plots comparing empirical quantiles against standard Normal and fitted Student-$t$ quantiles.
- Historical drawdown tracker detailing peak date, trough date, drawdown percentage, and recovery days.

### 7.3 Sampling, Backtesting, and Technical Exports
- Interactive CLT simulation demonstrating distribution narrowing across sample sizes $N \in \{5, 10, 30, 50\}$.
- Walk-forward backtest equity curve comparing trend-following strategy against Buy & Hold.
- Instant CSV export of processed daily time-series and downloadable Markdown technical reports.

### 7.4 AI Analysis Guidance and Rule-Based Signal Engine
- Multi-factor deterministic scoring producing BUY, HOLD, or SELL educational signals.
- Transparent component breakdown (Trend, Drawdown, Relative Performance, Volatility).
- Enforced data sufficiency guard requiring $N \ge 30$ observations before generating active signals.

---

## CHAPTER 8: TESTING & QUALITY ASSURANCE

### 8.1 Automated Test Suite Execution
The automated test suite (`pytest`) comprises 30 tests executing in **8.77 seconds** with a 100% pass rate:
- `tests/test_returns.py`: Mathematical return invariants and constant price handling.
- `tests/test_risk.py`: Monotonic ordering of VaR and Expected Shortfall ($\text{ES}_{99} \ge \text{VaR}_{99} \ge \text{VaR}_{95}$).
- `tests/test_distributions.py`: MLE Student-$t$ parameter recovery and heavy-tail AIC preference.
- `tests/test_backtest.py`: Zero look-ahead verification via future crash injection and fee deduction checks.
- `tests/test_sampling.py`: Bootstrap reproducibility under seeded pseudo-random states.
- `tests/test_csv_loader.py`: Date coercion, duplicate removal, and non-positive price filtering.
- `tests/test_ai_validation.py`: Data-sufficiency enforcement ($N < 30 \implies \text{HOLD}$).
- `tests/test_api_endpoints.py`: HTTP status codes, JSON response schemas, and export endpoints.

### 8.2 Data Sanitation & Numerical Invariant Verification
- Verified compounding equality: $\prod (1 + R_t) \equiv \exp(\sum r_t)$ to within machine floating-point precision ($10^{-12}$).
- Verified date coverage: 6,615 aligned trading sessions spanning `2000-01-03` to `2026-11-02`.
- Confirmed zero null or NaN values in cleaned production datasets.

### 8.3 Functional Route & AI Safety Tests
- Verified that HTTP `/health` returns status `200 OK` with valid metadata.
- Validated that `/api/analyze` responds with full econometric JSON payload in $< 200$ ms.

---

## CHAPTER 9: DEPLOYMENT & OPERATION

### 9.1 Local Windows Setup & Batch Launchers
The project includes automated Windows batch scripts:
- `setup_windows.bat`: Automates virtual environment (`.venv`) creation and dependency installation via pip.
- `start_dashboard.bat`: Starts the Flask web server and launches the default browser to `http://127.0.0.1:5000`.
- `run_tests.bat`: Executes the 30-case Pytest test suite with verbose reporting.

### 9.2 Environment Configuration & Offline Execution
- Configurable settings reside in `.env` (templated by `.env.example`).
- Full offline capability: Sample CSV files and Plotly.js are bundled locally, eliminating external network dependencies during classroom demonstrations.

---

## CHAPTER 10: CHALLENGES & LIMITATIONS

### 10.1 Data Provenance & Benchmark Pricing Asymmetry
- **Historical Stitching:** Pre-2007 NIFTY 50 data required sourcing from official exchange archives to bridge the gap before Yahoo Finance coverage.
- **Price Return vs. Total Return:** NIFTY 50 is a Price Return index (excluding dividends), whereas Reliance prices are dividend-adjusted. This structural difference slightly flatters relative stock alpha by $1.2\%–1.5\%$ per year.

### 10.2 Econometric Non-Stationarity & Backtest Friction
- Return distributions shift over decadal regimes (2000–2009 vs. 2010–2019 vs. 2020–2026 YTD).
- Backtested 10 bps transaction drag does not capture all market real-world frictions (slippage, liquidity depth, STT taxes).

### 10.3 AI Reasoning Boundaries
- AI-generated text is constrained by strict Pydantic schema validation and numeric checking against server statistics.
- The educational BUY/HOLD/SELL signal is a deterministic historical rule, not an investment recommendation.

---

## CHAPTER 11: FUTURE ENHANCEMENTS

### 11.1 Quantitative Modeling & Dataset Extensions
1. Integrate the **NIFTY 50 Total Return Index (TRI)** for completely symmetric dividend reinvestment comparisons.
2. Implement **GARCH(1,1) and EGARCH** models to capture time-varying conditional volatility clustering.
3. Incorporate high-frequency intraday bar data for microstructure and execution analysis.

### 11.2 Software Product & Educational Features
1. Multi-asset portfolio optimization supporting heavy-tailed risk parity.
2. Supervised multi-user classroom deployment mode with role-based access control.
3. Interactive sensitivity sliders for bootstrap block size ($b$) and VaR confidence intervals ($\alpha$).

---

## CHAPTER 12: CONCLUSION

### 12.1 Project Summary & Achievements
The **Stock Market Distribution Analyzer** delivers a complete, reproducible quantitative research application for analyzing Indian equity return distributions. Key empirical achievements include:
- Establishing that Reliance Industries returns exhibit severe fat tails ($\kappa = +8.4451$), decisively disproving Gaussian assumptions.
- Proving the superiority of the **Student-$t$ distribution ($\nu = 3.64, \Delta\text{AIC} = -1,310.2$)** over Gaussian models.
- Demonstrating that Gaussian models underestimate tail crash risk by up to $61.1\%$ relative to coherent Expected Shortfall.
- Providing an open-source, fully tested (30/30 tests passing) pedagogical tool for data-science education.

### 12.2 Academic Learning Outcomes
Through this project, the team gained deep practical experience in:
- Financial time-series cleaning, date alignment, and corporate action adjustments.
- Numerical Maximum Likelihood Estimation and econometric goodness-of-fit testing.
- Resampling techniques (IID and moving-block bootstrap) and Central Limit Theorem dynamics.
- Full-stack web application engineering with Python Flask, Jinja2, Chart.js, and Plotly.js.
- Automated software validation, regression testing, and responsible AI system design.

---

## CHAPTER 13: REFERENCES

### 13.1 Market Data Providers & Documentation
1. Yahoo Finance API. Historical Market Data (`RELIANCE.NS`, `^NSEI`, `^BSESN`). [https://finance.yahoo.com/](https://finance.yahoo.com/).
2. National Stock Exchange of India (NSE). Historical Index Data Archive. [https://www.nseindia.com/](https://www.nseindia.com/).
3. Python Software Foundation. Python 3.11 Documentation. [https://docs.python.org/3/](https://docs.python.org/3/).
4. Pallets Projects. Flask Documentation (v3.1.x). [https://flask.palletsprojects.com/](https://flask.palletsprojects.com/).
5. SciPy Community. `scipy.stats` Continuous Distributions. [https://docs.scipy.org/doc/scipy/](https://docs.scipy.org/doc/scipy/).
6. KLH University. Faculty Profiles, Department of CSE. [https://klh.edu.in/bhp-faculty/](https://klh.edu.in/bhp-faculty/).

### 13.2 Peer-Reviewed Academic Literature (2018–2026)
1. **López de Prado, M. (2018).** *Advances in Financial Machine Learning*. John Wiley & Sons. DOI: [10.1002/9781119482109](https://doi.org/10.1002/9781119482109).
2. **Taylor, J. W. (2019).** Forecasting Value at Risk and Expected Shortfall. *Journal of Business & Economic Statistics*, 37(1), 121–133. DOI: [10.1080/07350015.2017.1281815](https://doi.org/10.1080/07350015.2017.1281815).
3. **Gu, S., Kelly, B., & Xiu, D. (2020).** Empirical Asset Pricing via Machine Learning. *Review of Financial Studies*, 33(5), 2223–2273. DOI: [10.1093/rfs/hhaa009](https://doi.org/10.1093/rfs/hhaa009).
4. **Arrieta, A. B., et al. (2020).** Explainable Artificial Intelligence (XAI): Concepts, taxonomies, opportunities and challenges. *Information Fusion*, 58, 82–115. DOI: [10.1016/j.inffus.2019.12.012](https://doi.org/10.1016/j.inffus.2019.12.012).
5. **Lim, B., & Zohren, S. (2021).** Time-series forecasting with deep learning: a survey. *Phil. Trans. R. Soc. A*, 379(2194), 20200209. DOI: [10.1098/rsta.2020.0209](https://doi.org/10.1098/rsta.2020.0209).
6. **Pesaran, M. H., & Yamagata, T. (2024).** Testing for Alpha in Linear Factor Pricing Models. *Journal of Financial Econometrics*, 22(2), 407–460. DOI: [10.1093/jjfinec/nbad002](https://doi.org/10.1093/jjfinec/nbad002).

### 13.3 Internal Project Engineering Specifications
- `PROJECT_SCOPE.md`: Mathematical definitions and scope boundaries.
- `ARCHITECTURE.md`: Component layout and data flow diagrams.
- `DATA_SOURCE_AND_QUALITY_REPORT.md`: Sourcing, corporate action audit, and calendar alignment details.
- `VALIDATION_SUMMARY.md`: Automated test matrix and numerical invariant execution log.
- `AI_AND_FINANCIAL_LIMITATIONS.md`: Financial disclaimers and AI boundary definitions.

---

## CHAPTER 14: APPENDICES

### 14.1 Appendix A — Data Dictionary
- **Date:** Calendar date of the exchange trading session (YYYY-MM-DD).
- **Adj Close:** Split- and dividend-adjusted closing price in INR.
- **Close:** Unadjusted raw market closing quote in INR.
- **Volume:** Total traded share volume recorded by the exchange.
- **Simple Return ($R_t$):** Percentage price change from previous session: $(P_t / P_{t-1}) - 1$.
- **Log Return ($r_t$):** Continuously compounded return: $\ln(P_t / P_{t-1})$.
- **Cumulative Return:** Total percentage growth since inception rebased to $100$.
- **Underwater Drawdown:** Percentage decline from historical running peak.
- **Rolling Volatility:** 21-session trailing standard deviation annualized by $\sqrt{252}$.

### 14.2 Appendix B — Formulas and Market Conventions
- $\text{CAGR} = (P_N / P_0)^{252/N} - 1$
- $\sigma_{\text{ann}} = \sigma_{\text{daily}} \times \sqrt{252}$
- $\text{VaR}_{0.95} = -Q_{0.05}(R)$
- $\text{ES}_{0.95} = -\mathbb{E}[R \mid R \le -\text{VaR}_{0.95}]$
- $\text{AIC} = 2k - 2\ln(L)$
- $\text{BIC} = k\ln(N) - 2\ln(L)$

### 14.3 Appendix C — Recorded Validation Summary
- 30 / 30 automated test cases passed in 8.77 seconds.
- Invariants verified: Compounding identity, monotonic tail ordering ($\text{ES}_{99} \ge \text{VaR}_{99} \ge \text{VaR}_{95}$), and zero look-ahead bias.

### 14.4 Appendix D — User Operation Guide
1. Run `setup_windows.bat` to configure Python virtual environment and install dependencies.
2. Run `start_dashboard.bat` to launch the Flask server on `http://127.0.0.1:5000`.
3. Select preloaded stock or upload custom CSV; review summary metrics and analytical tabs.
4. Export data series as CSV or generate technical Markdown reports.
5. Execute `run_tests.bat` to re-run the 30-case validation suite at any time.

### 14.5 Appendix E — Equal Team Contribution Statement
We hereby affirm that this project was completed collaboratively with equal division of effort:
- **A. Srivathsava Reddy (2420030634):** Ingestion pipeline, data sanitation, calendar alignment, return computations, parametric distribution fitting, and coherent risk modeling.
- **Aryan Vinayak Salunkhe (2420030137):** Guidance engine, score weights, safety guards, web UI design, Chart.js integrations, reporting, and technical exports.
- **Collaborative Responsibilities:** System architecture, test engineering, validation auditing, presentation deck, and project report preparation.
