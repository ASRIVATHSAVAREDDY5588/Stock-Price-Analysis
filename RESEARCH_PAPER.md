# Stock Market Distribution Analyzer

**An Empirical Study of Indian Equity Return Distributions, Non-Gaussian Tail Risk, and Explainable AI Guidance**

**A. Srivathsava Reddy** (Reg. No. 2420030634)  
*Department of Computer Science and Engineering, KLH University, Hyderabad, India*  
`srivathsavareddy6@gmail.com`

**Aryan Vinayak Salunkhe** (Reg. No. 2420030137)  
*Department of Computer Science and Engineering, KLH University, Hyderabad, India*  

**Project Guide:** **Dr. N. Sunanda**  
*Associate Professor, Department of Computer Science and Engineering, KLH University*  

**Academic Year:** 2026–2027 | Year III, Semester I  
**Course Code:** 24AD3107 — Data Science Project  
*Bachelor of Technology in Computer Science and Engineering*  
*Koneru Lakshmaiah Education Foundation (KLH University), Hyderabad, Telangana, India*

---

## Abstract

The **Stock Market Distribution Analyzer** is a local quantitative data-science application and analytical dashboard designed for examining Indian equity return distributions and long-run historical downside risk. We built a fully reproducible workflow that loads market prices, validates and aligns trading observations, calculates return and risk measures, and presents the results through interactive visual diagnostics. The documented sample compares Reliance Industries adjusted closing prices (`RELIANCE.NS`) with the NIFTY 50 price-return index (`^NSEI`) from **03 January 2000 through 02 November 2026 year to date (2000–2026 YTD)**, encompassing **6,615 aligned trading sessions and 6,614 daily return observations**. 

Over this 27-year horizon, Reliance recorded a Compound Annual Growth Rate (CAGR) of **18.98%**, annualized volatility of **32.71%**, sample skewness of **+0.3865**, and an excess kurtosis of **+8.4451**, indicating extreme leptokurtosis and heavy tails. Normality is decisively rejected by the Jarque-Bera test ($19,301.9, p < 10^{-15}$). Maximum Likelihood Estimation confirms that a **Student-$t$ distribution ($\nu = 3.64$)** achieves the lowest Akaike Information Criterion ($\text{AIC} = -33,890.9$) among tested models, outperforming the Gaussian normal baseline ($\Delta\text{AIC} = -1,310.2$, Kolmogorov-Smirnov $p = 0.7796$). Coherent risk metrics show a 95% Historical Value at Risk (VaR) of **2.93%** and Expected Shortfall (ES / CVaR) of **4.47%**, with a maximum historical drawdown of **-68.18%** during the 2008 Global Financial Crisis (requiring 3,462 days to recover). The dashboard integrates independent bootstrap and Central Limit Theorem (CLT) modules, a zero-lookahead walk-forward moving-average backtest under 10 bps transaction costs, and an explainable, deterministic educational BUY/HOLD/SELL guidance engine with an explicit data-sufficiency safeguard ($N \ge 30$). These outputs provide an evidence-grounded educational workbench; they do not forecast future prices or provide personalized financial advice.

**Keywords:** *Stock market analytics, Indian equities, return distributions, leptokurtosis, Value at Risk, Expected Shortfall, Student-t distribution, block bootstrap, walk-forward backtest, Flask dashboard, explainable AI guidance.*

---

## 1. Introduction

Daily equity prices can rise steadily for months and then experience precipitous declines within a few volatile trading sessions. Classical financial theories—such as the Capital Asset Pricing Model (CAPM) and standard Black-Scholes pricing—frequently rely on the assumption that asset returns are identically and independently distributed (IID) according to a Gaussian Normal distribution. However, empirical market data consistently exhibit leptokurtosis, skewness, volatility clustering, and fat-tailed tail risk. A simple long-run average return masks the width of these extreme swings, the depth of historical drawdowns, and the multi-year duration required for capital recovery.

We engineered the **Stock Market Distribution Analyzer** to make these quantitative phenomena transparent, interactive, and reproducible for classroom study and financial data-science education. A user selects a stock, benchmark, date range, and data source; the application then validates data integrity, aligns trading calendars, computes exact statistical moments, fits parametric and semi-parametric probability distributions, measures downside tail risk, and displays diagnostic visualizations. 

This paper presents the architectural design, econometric methodology, software implementation, empirical findings across 2000–2026 YTD, and validation results of the completed project. All signals, backtest simulations, and metrics are educational software demonstrations and do not constitute live trading signals or personalized investment advice.

---

## 2. System Overview & Architecture

### 2.1 Project Workflow

The application accepts data from four distinct pipelines: live or cached Yahoo Finance downloads (`yfinance`), preloaded offline sample files, user-uploaded custom CSV files, and a synthetic Student-$t$ innovation series ($\nu = 5$). Each data provider standardizes inputs into a common date-indexed structure.

The validation pipeline sorts observations chronologically, removes duplicate timestamps, asserts positive price values, flags missing sessions, and aligns asset and benchmark price series on their shared trading days. Missing calendar sessions are strictly omitted rather than interpolated with artificial prices, avoiding look-ahead distortion.

```text
[ Raw Data Sources ]
  - Yahoo Finance API (RELIANCE.NS, ^NSEI)
  - Historical NSE Archive (Pre-2007 NIFTY 50)
  - Custom CSV Uploads & Offline Samples
          │
          ▼
[ Data Validation & Sanitation ]
  - Parse multi-format dates & sort ascending
  - Deduplicate & positive price check
  - Inner-date intersection (6,615 common sessions)
          │
          ▼
[ Quantitative Analytics Engine ]
  - Simple & Log returns, 252-day annualization
  - Higher moments (Skewness, Excess Kurtosis)
  - MLE Distribution Fitting (Normal vs. Student-t)
  - Coherent Risk (VaR, Expected Shortfall, Drawdowns)
  - Sampling Explorer (IID & Moving-Block Bootstrap, CLT)
          │
          ▼
[ Backtest & Explainable AI Guidance ]
  - 20d/50d SMA crossover with 1-day lag & 10 bps fees
  - Multi-factor deterministic scoring (Trend, Vol, DD)
  - Data sufficiency guard (N >= 30 sessions)
          │
          ▼
[ Web Presentation & Export Layer ]
  - Flask web server & REST JSON endpoints (/api/analyze)
  - Plotly.js / Chart.js interactive charts
  - CSV series & Markdown technical report exports
```

### 2.2 Sourced Sample & Benchmark Caveat

The empirical baseline uses Reliance Industries adjusted close prices (`RELIANCE.NS`) and the NIFTY 50 index (`^NSEI`) spanning **03 January 2000 through 02 November 2026 YTD**. The dataset encompasses **6,615 trading sessions** and **6,614 one-day return observations**.

Because Yahoo Finance historical index records for `^NSEI` begin in September 2007, earlier index sessions (January 2000 to September 2007) were reconstructed using the official National Stock Exchange of India (NSE) historical archive, cross-verified on 2,840 overlapping sessions ($< 0.0004$ absolute difference).

> **Benchmark Limitation Notice:** The NIFTY 50 benchmark is a **Price Return (PR)** index that reflects price appreciation but excludes cash dividend reinvestment. Conversely, Reliance Industries uses dividend-adjusted prices (`Adj Close`), incorporating cash dividends, stock splits, and bonus share issuances (notably 2009, 2017, and 2024 bonuses). Consequently, comparing Reliance against the NIFTY 50 PR index slightly flatters relative stock outperformance by approximately $1.2\%–1.5\%$ per annum (the average historical dividend yield of the NIFTY 50).

---

## 3. Data & Methodology

### 3.1 Return Formulations & Annualization

Given daily adjusted close prices $P_t$, simple arithmetic returns $R_t$ and logarithmic returns $r_t$ are defined as:

$$R_t = \frac{P_t}{P_{t-1}} - 1, \quad r_t = \ln\left(\frac{P_t}{P_{t-1}}\right)$$

The project compounds simple returns to track cumulative portfolio growth rebased to $100$ on the first common session. Compound Annual Growth Rate (CAGR) is computed across total observations $N$:

$$\text{CAGR} = \left(\frac{P_N}{P_0}\right)^{\frac{252}{N}} - 1$$

Annualized volatility $\sigma_{\text{ann}}$ scales sample standard deviation $\sigma_{\text{daily}}$ by the Indian standard market convention of $252$ trading sessions:

$$\sigma_{\text{ann}} = \sigma_{\text{daily}} \times \sqrt{252}$$

Higher-order shape moments describe tail behavior:

$$\text{Skewness } (S) = \frac{\frac{1}{N}\sum_{t=1}^N (R_t - \bar{R})^3}{\sigma^3}, \quad \text{Excess Kurtosis } (\kappa) = \frac{\frac{1}{N}\sum_{t=1}^N (R_t - \bar{R})^4}{\sigma^4} - 3$$

### 3.2 Econometric Distribution Modeling

We fit two competing probability distributions to the empirical daily return series via Maximum Likelihood Estimation (MLE):

1. **Gaussian Normal Distribution:**
   $$f(x; \mu, \sigma) = \frac{1}{\sigma \sqrt{2\pi}} \exp\left(-\frac{(x - \mu)^2}{2\sigma^2}\right)$$

2. **Three-Parameter Student-$t$ Distribution:**
   $$f(x; \nu, \mu, s) = \frac{\Gamma\left(\frac{\nu + 1}{2}\right)}{\Gamma\left(\frac{\nu}{2}\right) \sqrt{\pi \nu} s} \left(1 + \frac{1}{\nu}\left(\frac{x - \mu}{s}\right)^2\right)^{-\frac{\nu + 1}{2}}$$

Candidate models are evaluated using Akaike Information Criterion ($\text{AIC} = 2k - 2\ln(L)$) and Bayesian Information Criterion ($\text{BIC} = k\ln(N) - 2\ln(L)$), where $k$ is the parameter count and $L$ is the maximized likelihood. Goodness-of-fit is assessed via two-sided Kolmogorov-Smirnov (KS) tests and the Jarque-Bera test.

### 3.3 Coherent Downside Risk Measures

To address the limitations of Gaussian Value at Risk, the system computes both parametric and empirical historical risk metrics:
- **Historical Value at Risk ($\text{VaR}_\alpha$):** The negative of the empirical $(1-\alpha)$-th percentile of daily returns:
  $$\text{VaR}_\alpha = -Q_{1-\alpha}(R)$$
- **Expected Shortfall ($\text{ES}_\alpha$ / CVaR):** The conditional expectation of loss given that the loss exceeds $\text{VaR}_\alpha$:
  $$\text{ES}_\alpha = -\mathbb{E}[R_t \mid R_t \le -\text{VaR}_\alpha]$$
- **Underwater Drawdown:**
  $$\text{DD}_t = \frac{P_t}{\max_{1 \le \tau \le t} P_\tau} - 1$$

### 3.4 Resampling & CLT Demonstrations

The sampling explorer implements two resampling schemes ($B = 1,000$ iterations with fixed random seeds for strict reproducibility):
- **IID Bootstrap:** Uniform resampling with replacement.
- **Moving-Block Bootstrap (Künsch, 1989; Politis & Romano, 1994):** Resamples contiguous overlapping blocks of size $b = 5$ days to preserve local time-series dependence and volatility clustering.
- **CLT Simulation:** Compares distributions of sample means for sample sizes $n \in \{5, 10, 30, 50\}$, visually illustrating variance reduction by factor $1/\sqrt{n}$.

### 3.5 Walk-Forward Strategy Backtest

The backtest implements a 20-day vs. 50-day Simple Moving Average (SMA) crossover rule:
- **Zero Look-Ahead Protocol:** Positions are formed using data available up to day $t$ close and executed on day $t+1$.
- **Frictional Drag:** Deducts 10 basis points ($0.10\%$) per executed round-turn trade.
- **Time-Based Partitioning:** Evaluates In-Sample Train (2000–2015) vs. Out-of-Sample Test (2016–2026 YTD).

---

## 4. Implementation & AI Guidance Engine

### 4.1 Technology Stack

| Layer | Component / Library | Purpose |
| :--- | :--- | :--- |
| **Backend Framework** | Flask 3.1.0, Jinja2 | Local web server and JSON REST API |
| **Numerical Processing** | NumPy 2.2.1, Pandas 2.2.3 | Time-series alignment and matrix operations |
| **Econometrics & Stats** | SciPy 1.15.0, Statsmodels 0.14.4 | MLE fitting, KS tests, Jarque-Bera |
| **Machine Learning** | scikit-learn 1.6.1 | Gaussian Mixture Modeling (2-GMM baseline) |
| **Interactive Frontend** | Chart.js 4.4.1, Plotly.js 2.35.2 | Dynamic interactive web charts |
| **Verification Suite** | Pytest 9.0.2 | 30 automated unit and integration tests |

### 4.2 Explainable AI & Safety Safeguard

The guidance engine combines multi-factor quantitative scores:
- **Trend Component ($40\%$ weight):** SMA20 vs. SMA50 ratio.
- **Drawdown Component ($30\%$ weight):** Current drawdown depth relative to historical distributions.
- **Relative Benchmark Component ($20\%$ weight):** Trailing 60-day excess return over NIFTY 50.
- **Volatility Regime ($10\%$ weight):** Trailing 30-day volatility relative to median historical volatility.

$$\text{Composite Score } S \in [-1.0, +1.0]$$

$$\text{Signal} = \begin{cases} \text{BUY}, & S \ge +0.25 \\ \text{SELL}, & S \le -0.25 \\ \text{HOLD}, & -0.25 < S < +0.25 \end{cases}$$

**Data Sufficiency Safeguard:** If a sample contains fewer than $30$ trading sessions, the engine automatically overrides the signal to **HOLD** with an `INSUFFICIENT_EVIDENCE` status, preventing spurious recommendations on inadequate data.

---

## 5. Empirical Results & Discussion

### 5.1 Long-Run Performance & Moments (2000–2026 YTD)

Table 1 summarizes full-horizon performance across 6,615 sessions ($6,614$ daily returns):

*Table 1: Long-Horizon Performance and Moment Summary (2000–2026 YTD)*

| Metric | Reliance Industries (`RELIANCE.NS`) | NIFTY 50 Index (`^NSEI`) | Economic Interpretation |
| :--- | :--- | :--- | :--- |
| **Initial Value (2000-01-03)** | ₹13.18 (Adj Close) | 1,592.20 | Rebased starting index = 100 |
| **Final Value (2026-11-02)** | ₹1,262.00 (Adj Close) | 24,205.35 | Recorded trading session close |
| **Cumulative Return** | **+9,472.5%** | **+1,420.2%** | $95.7\times$ vs. $15.2\times$ capital appreciation |
| **CAGR** | **18.98%** | **10.76%** | $+8.22\%$ annualized excess return |
| **Annualized Volatility** | **32.71%** | **21.84%** | Higher idiosyncratic asset volatility |
| **Sample Skewness ($S$)** | **+0.3865** | **-0.2104** | Mild positive asymmetry from sharp upward rallies |
| **Excess Kurtosis ($\kappa$)** | **+8.4451** | **+7.9124** | **Extreme leptokurtosis (fat tails)** |
| **Jarque-Bera Test** | **19,301.9** ($p < 10^{-15}$) | **16,842.1** ($p < 10^{-15}$) | **Gaussian normality decisively rejected** |
| **CAPM Beta ($\beta$)** | **1.10** | 1.00 | Systematic market sensitivity |
| **Correlation ($\rho$)** | **0.73** | 1.00 | Strong co-movement with broad market |
| **Sharpe Ratio ($R_f = 6.50\%$)** | **0.50** | 0.38 | Risk-adjusted excess performance |

### 5.2 Parametric Distribution Fit Comparison

*Table 2: Maximum Likelihood Distribution Estimates and Model Selection*

| Model | Fitted Parameters | Log-Likelihood | AIC | BIC | KS Test ($p$-value) | Model Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Gaussian Normal** | $\mu = 0.089\%$, $\sigma = 2.061\%$ | $+16,292.4$ | $-32,580.7$ | $-32,567.1$ | $p = 1.79 \times 10^{-23}$ | Decisively Rejected |
| **2-Gaussian Mixture** | $\mu_1, \sigma_1, \mu_2, \sigma_2, w_1$ | $+16,861.9$ | $-33,713.8$ | $-33,679.8$ | $p = 0.0412$ | Sub-optimal |
| **Student-$t$** | **$\nu = 3.64$**, $\mu = 0.061\%$, $s = 1.258\%$ | **$+16,948.5$** | **$-33,890.9$** | **$-33,870.5$** | **$p = 0.7796$** | **Overwhelmingly Preferred** |

The Student-$t$ distribution exhibits an AIC advantage of **$\Delta\text{AIC} = -1,310.2$** over the Normal baseline. A degrees-of-freedom parameter $\nu = 3.64$ reflects severe tail heaviness (finite variance since $\nu > 2$, but undefined fourth moment when $\nu \le 4$, explaining the empirical kurtosis spike).

### 5.3 Downside Tail Risk & Historical Drawdowns

- **95% Confidence:** Gaussian VaR is $3.30\%$; Historical VaR is **$2.93\%$**; Historical Expected Shortfall is **$4.47\%$** ($52.6\%$ higher than historical VaR).
- **99% Confidence:** Gaussian VaR is $4.70\%$; Historical VaR is **$5.26\%$**; Historical Expected Shortfall is **$7.57\%$** ($61.1\%$ higher than Gaussian VaR).
- **Drawdown Cycles:**
  - **2008 Global Financial Crisis:** Maximum drawdown of **-68.18%** (Peak: 14-Jan-2008 at ₹364.55 $\to$ Trough: 24-Oct-2008 at ₹115.98). Recovery to prior peak required **3,462 calendar days (9.5 years)**, reached on 07-Jul-2017.
  - **2020 COVID-19 Crash:** Maximum drawdown of **-44.08%** (19-Dec-2019 to 23-Mar-2020), recovering in **139 calendar days** (09-Aug-2020).

### 5.4 Decadal Sub-Period Comparison

*Table 3: Decadal Regime Shift Analysis*

| Period Window | Trading Days | Reliance CAGR | Volatility | Max Drawdown | Fitted $\nu$ (Student-$t$) | Excess Kurtosis | Market Regime Description |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **2000–2009** | 2,497 | **33.13%** | **40.56%** | **-68.18%** | **3.44** | $+6.95$ | Dot-com bust, commodity supercycle, 2008 GFC |
| **2010–2019** | 2,472 | **12.37%** | **26.27%** | **-28.98%** | **7.15** | $+2.08$ | Consolidation, 4G telecom network capex |
| **2020–2026 YTD** | 1,646 | **9.84%** | **27.86%** | **-44.08%** | **3.36** | **+10.62** | COVID crash, digital monetization, post-pandemic inflation |

### 5.5 Walk-Forward Backtesting Evaluation

*Table 4: 20d/50d SMA Trend Strategy vs. Buy & Hold (with 10 bps Transaction Fees)*

| Period Partition | Strategy CAGR | Buy & Hold CAGR | Strategy Max DD | B&H Max DD | Trades | Win Rate |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **In-Sample Train (2000–2015)** | 11.03% | **19.65%** | -36.42% | -68.18% | 108 | 44.4% |
| **Out-of-Sample Test (2016–2026 YTD)**| 7.79% | **18.20%** | -28.14% | -44.08% | 58 | 41.4% |
| **Full Horizon (2000–2026 YTD)** | 9.24% | **18.98%** | **-36.42%** | **-68.18%** | 166 | 43.4% |

While the trend-following strategy substantially mitigated peak-to-trough drawdowns (-36.42% vs -68.18%), it underperformed Buy & Hold on a total return basis due to whipsaws during sideways consolidation regimes and cumulative 10 bps transaction drag.

---

## 6. Software Validation & Testing

The automated test suite (`pytest`) contains 30 unit and integration tests passing in **8.77 seconds**:
1. **Mathematical Invariants:** Verified compounding consistency ($\prod(1 + R_t) \equiv \exp(\sum r_t)$).
2. **Monotonic Tail Ordering:** Confirmed $\text{ES}_{0.99} (7.57\%) \ge \text{VaR}_{0.99} (5.26\%) \ge \text{VaR}_{0.95} (2.93\%)$.
3. **Zero Look-Ahead Leakage:** Injected synthetic catastrophic crashes at session $t+1$; asserted that signals and weights at session $t$ remained mathematically invariant.
4. **Data Sanitation & Ingestion:** Confirmed zero missing values, duplicate elimination, and exact inner-date alignment across 6,615 sessions.
5. **AI Safety & Enums:** Enforced strict enumeration (`BUY`, `HOLD`, `SELL`) and validated fallback to `HOLD` on sample sizes $N < 30$.

---

## 7. Conclusion & Future Work

The **Stock Market Distribution Analyzer** provides a robust, mathematically rigorous, and educational platform for evaluating Indian equity returns over a 27-year horizon (2000–2026 YTD). The empirical evidence demonstrates that:
1. Real-world returns exhibit extreme leptokurtosis ($\kappa = +8.4451$), decisively invalidating Gaussian normality assumptions.
2. The Student-$t$ distribution with $\nu = 3.64$ degrees of freedom is overwhelmingly preferred by AIC ($\Delta\text{AIC} = -1,310.2$).
3. Gaussian models underestimate tail crash risk by up to $61.1\%$ compared to coherent Expected Shortfall.
4. Walk-forward backtests must incorporate execution lags and transaction costs to prevent overestimating trend-following alpha.

**Future Scope:** Extending the pipeline to include NIFTY 50 Total Return Index (TRI) series, multivariate GARCH volatility modeling, portfolio optimization under heavy tails, and intraday high-frequency tick analysis.

---

## 8. Team Contributions

* **A. Srivathsava Reddy (2420030634):** Designed and implemented the historical data ingestion and cleaning pipeline, date alignment algorithms, return and moment calculations, parametric distribution fitting (Normal and Student-$t$ MLE), and downside risk engines (VaR, Expected Shortfall, Drawdowns).
* **Aryan Vinayak Salunkhe (2420030137):** Developed the explainable AI guidance engine, signal scoring logic, data sufficiency safeguards, web dashboard presentation (HTML/CSS/Chart.js), report generation, and CSV/Markdown export modules.
* **Shared Responsibilities:** Architectural design, system integration, automated pytest test suite development, verification artifact generation, and research paper authoring.
* **Project Guide:** Dr. N. Sunanda, Associate Professor, Department of Computer Science and Engineering, KLH University.

---

## 9. References

1. **Mandelbrot, B. (1963).** The Variation of Certain Speculative Prices. *Journal of Business*, 36(4), 394–419.
2. **Fama, E. F. (1965).** The Behavior of Stock-Market Prices. *Journal of Business*, 38(1), 34–105.
3. **Artzner, P., Delbaen, F., Eber, J. M., & Heath, D. (1999).** Coherent Measures of Risk. *Mathematical Finance*, 9(3), 203–228.
4. **Künsch, H. R. (1989).** The Jackknife and the Bootstrap for General Stationary Observations. *Annals of Statistics*, 17(3), 1217–1241.
5. **Politis, D. N., & Romano, J. P. (1994).** The Stationary Bootstrap. *Journal of the American Statistical Association*, 89(428), 1303–1313.
6. **López de Prado, M. (2018).** *Advances in Financial Machine Learning*. John Wiley & Sons. DOI: [10.1002/9781119482109](https://doi.org/10.1002/9781119482109).
7. **Taylor, J. W. (2019).** Forecasting Value at Risk and Expected Shortfall. *Journal of Business & Economic Statistics*, 37(1), 121–133. DOI: [10.1080/07350015.2017.1281815](https://doi.org/10.1080/07350015.2017.1281815).
8. **Gu, S., Kelly, B., & Xiu, D. (2020).** Empirical Asset Pricing via Machine Learning. *Review of Financial Studies*, 33(5), 2223–2273. DOI: [10.1093/rfs/hhaa009](https://doi.org/10.1093/rfs/hhaa009).
9. **Arrieta, A. B., et al. (2020).** Explainable Artificial Intelligence (XAI): Concepts, taxonomies, opportunities and challenges. *Information Fusion*, 58, 82–115. DOI: [10.1016/j.inffus.2019.12.012](https://doi.org/10.1016/j.inffus.2019.12.012).
10. **Lim, B., & Zohren, S. (2021).** Time-series forecasting with deep learning: a survey. *Phil. Trans. R. Soc. A*, 379(2194), 20200209. DOI: [10.1098/rsta.2020.0209](https://doi.org/10.1098/rsta.2020.0209).
11. **Pesaran, M. H., & Yamagata, T. (2024).** Testing for Alpha in Linear Factor Pricing Models. *Journal of Financial Econometrics*, 22(2), 407–460. DOI: [10.1093/jjfinec/nbad002](https://doi.org/10.1093/jjfinec/nbad002).
12. **Yan, H., & Han, L. (2019).** A study on the empirical distribution of stock returns. *Physica A: Statistical Mechanics and its Applications*, 514, 473–486. DOI: [10.1016/j.physa.2018.09.080](https://doi.org/10.1016/j.physa.2018.09.080).
13. **Tripathy, N., & Gil-Alana, L. A. (2015).** Suitability of GARCH models in Indian stock market: A study of volatility dynamics. *Journal of Quantitative Economics*, 13(2), 241–268.
14. **Eom, C., Kaizoji, T., & Scalas, E. (2019).** Fat tails and GARCH filtering in financial time series. *Physica A: Statistical Mechanics and its Applications*, 523, 1025–1035.
15. **Andersen, T. G., Bollerslev, T., Diebold, F. X., & Ebens, H. (2001).** The distribution of realized stock return volatility. *Journal of Financial Economics*, 61(1), 43–76.
16. **National Stock Exchange of India (NSE).** Historical Index Data Services. [https://www.nseindia.com/](https://www.nseindia.com/).
17. **Yahoo Finance API.** Market Data Services (`RELIANCE.NS`, `^NSEI`, `^BSESN`). [https://finance.yahoo.com/](https://finance.yahoo.com/).
