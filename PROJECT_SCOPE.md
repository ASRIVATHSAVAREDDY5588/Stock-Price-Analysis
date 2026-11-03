# Project Scope & Specifications: Stock Market Distribution Analyzer

---

## 1. Project Purpose

The **Stock Market Distribution Analyzer** is an interactive, educational quantitative laboratory designed to provide university students and data science learners with hands-on experience analyzing Indian equity return distributions, downside tail risk, and sampling theory. It bridges the gap between statistical probability theory and practical market mechanics using verified historical and synthetic data from Indian stock exchanges.

---

## 2. In-Scope Capabilities

1. **Market Data Ingestion:**
   - Ingestion of Indian equity price histories via synthetic modeling, Yahoo Finance, or custom CSV upload.
   - Transparent data source labeling, date range verification, and automated data cleaning (deduplication, chronological sorting, minimum 15-day sample enforcement).
2. **Return & Moment Calculations:**
   - Computation of simple arithmetic returns, logarithmic returns, cumulative returns, and base-100 indexed performance.
   - Calculation of sample descriptive statistics: mean, median, variance, standard deviation, Fisher-Pearson skewness, excess kurtosis, extremes, and percentiles.
   - Standard Indian equity annualization convention: 252 trading days per year ($\sigma_{\text{ann}} = \sigma_{\text{daily}} \times \sqrt{252}$).
3. **Downside Risk Measurement:**
   - Historical and Parametric Value at Risk (VaR) at selectable confidence levels (90%, 95%, 99%).
   - Expected Shortfall (CVaR) evaluating the conditional mean of tail losses.
   - Maximum Drawdown (MDD) tracking peak, trough, and recovery duration.
   - Trailing 21-day rolling volatility.
   - CAPM Beta, Correlation, Sharpe ratio (assuming a 6.5% Indian 10-year G-Sec risk-free rate), and Sortino ratio against the NIFTY 50 benchmark.
4. **Distribution Analysis:**
   - Fitting of Normal and Student-t distributions via Maximum Likelihood Estimation.
   - Two-component Gaussian Mixture Model (GMM) regime analysis.
   - Model selection via Akaike Information Criterion (AIC) and Bayesian Information Criterion (BIC).
   - Goodness-of-fit testing via Kolmogorov-Smirnov and Jarque-Bera normality tests.
   - Interactive theoretical vs. empirical Q-Q diagnostic plotting.
5. **Sampling & Asymptotic Explorers:**
   - IID and Moving-Block Bootstrap confidence intervals (1,000 replications) with user-controlled random seeds for reproducibility.
   - Central Limit Theorem explorer demonstrating asymptotic normality of sample means across sample sizes $n \in \{5, 10, 30, 50\}$.
6. **Chronological Backtesting:**
   - Walk-forward evaluation of a dual moving-average trend rule enforcing strict zero lookahead (signals computed at day $t$, executed at day $t+1$).
   - Explicit transaction fee deduction (10 basis points / 0.10%).
7. **Educational AI Guidance:**
   - Rule-based analysis guide suggesting next investigative steps based exclusively on observed quantitative evidence.
   - Schema-validated educational historical signal (BUY, HOLD, SELL) paired with a transparent deterministic baseline score.
   - Server-side ground truth validation to ensure zero hallucination.
8. **Export Utilities:**
   - Downloadable CSV containing all calculated daily returns, drawdowns, and rolling volatility.
   - Downloadable Markdown technical report summarizing findings.

---

## 3. Explicit Out-of-Scope Boundaries

To maintain focus on educational quantitative learning, the project explicitly excludes:
- **No Literature Reviews or Novelty Claims:** No academic paper comparisons, research-gap claims, or claims of novel scientific breakthroughs.
- **No Real-Time Streaming or Tick Data:** The lab operates on end-of-day daily closing bars. It does not connect to live WebSocket order books, tick feeds, or level-2 quotes.
- **No Algorithmic Trade Execution:** The app does not integrate with broker APIs, place orders, execute live trades, or manage real financial capital.
- **No Financial Advisory Services:** The educational signals are historical statistical diagnostics, not personalized financial or investment advice. No price targets, profit promises, or portfolio allocation recommendations are provided.
- **No Complex External Databases:** The application runs locally using file-based caching (`.cache/`) without requiring PostgreSQL, MySQL, or cloud database clusters.

---

## 4. Key Financial Conventions & Assumptions

| Parameter | Standard Value | Description / Convention |
| :--- | :--- | :--- |
| **Trading Days / Year** | 252 days | Standard Indian National Stock Exchange (NSE) / BSE annual session count. |
| **Risk-Free Rate ($R_f$)** | 6.50% annual | Benchmark yield representative of the Indian 10-Year Government Securities (G-Sec). |
| **Transaction Cost** | 10 basis points (0.10%) | Realistic round-trip slippage, brokerage, and statutory taxes (STT/GST) for liquid equities. |
| **VaR Confidence Level** | 95% (selectable 80–99%) | Standard Basel / quantitative risk management convention. |
| **Rolling Vol Window** | 21 trading sessions | Approximately one calendar month of trading. |
| **Minimum History** | 15 observations | Absolute minimum required to compute basic sample variance. (30+ recommended for distributions; 60+ for signal conviction). |
