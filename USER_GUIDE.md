# User Guide: Stock Market Distribution Analyzer

The **Stock Market Distribution Analyzer** provides an interactive quantitative workbench for exploring asset price histories, probability distributions, downside risk, and sampling theory. This user guide explains each section of the application in detail.

---

## 1. Parameters & Data Controls

Located in the left sidebar, the parameters panel governs data ingestion and statistical parameters.

### Data Sources
1. **Synthetic Demo Data (Offline / Deterministic):**
   - Modeled using a calibrated Student-t stochastic process ($\nu = 5$) with jump-diffusion and cross-asset correlation.
   - Operates 100% offline without network requests.
   - Prominently marked with an orange `DEMO MODE ACTIVE` banner to clearly distinguish it from real market quotes.
2. **Yahoo Finance (Live / Cached):**
   - Downloads daily quotes for Indian equities using the National Stock Exchange (`.NS`) or BSE (`.BO`) convention.
   - Employs a 10-second timeout with retry logic.
   - Successful downloads are cached on disk for 1 hour to prevent redundant requests and enable disconnected repeat visits.
   - If an external network failure occurs, a clear warning banner prompts you to switch to Synthetic Demo mode.
3. **CSV File Upload:**
   - Accepts custom price series.
   - Supported schemas:
     - Single-series: `Date` and `Adj Close` (or `Close`).
     - Multi-series: `Date`, `Ticker`, and `Adj Close`.
   - Automatically parses date formats, sorts chronologically, removes duplicates, and removes non-positive or missing prices.
   - Minimum threshold: At least 15 valid trading sessions are required.

### Asset & Benchmark Selection
- **Indian Stock Ticker:** Select from pre-configured leading Indian companies (e.g., `RELIANCE.NS`, `TCS.NS`, `INFY.NS`, `HDFCBANK.NS`, `ICICIBANK.NS`, `ITC.NS`, `SBIN.NS`, `LT.NS`, `TATAMOTORS.NS`) or enter any custom ticker symbol.
- **Benchmark Index:** Choose between `^NSEI` (NIFTY 50), `^BSESN` (S&P BSE SENSEX), or `^NSEBANK` (NIFTY Bank).

### Return Calculation Convention
- **Simple Arithmetic Return:** $R_t = \frac{P_t}{P_{t-1}} - 1$. Additive across assets in a portfolio at a single point in time.
- **Logarithmic Return:** $r_t = \ln\left(\frac{P_t}{P_{t-1}}\right) = \ln(P_t) - \ln(P_{t-1})$. Additive through time.

### VaR Confidence Level Slider
- Adjust between 80% and 99% (default 95%). Modifies the tail cutoff for Historical VaR, Parametric VaR, and Expected Shortfall.

### Bootstrap & Resampling Options
- **IID Bootstrap:** Standard independent resampling with replacement.
- **Moving-Block Bootstrap:** Resamples contiguous blocks of trading days (e.g., 5 or 10 days) to preserve serial autocorrelation and volatility clustering.
- **Random Seed:** Set a fixed integer (e.g., 42) for exact reproducibility.

---

## 2. Key Metrics Ribbon

Six critical summary metrics are displayed at the top of the dashboard:
1. **Annualized Return:** Compound annual growth rate assuming 252 trading sessions per year.
2. **Annualized Volatility:** Daily standard deviation scaled by $\sqrt{252}$ ($\sigma_{\text{ann}} = \sigma_{\text{daily}} \times \sqrt{252}$).
3. **Historical VaR (95%):** Positive loss percentage indicating that 95% of trading days experienced a better return than this cutoff.
4. **Expected Shortfall (CVaR):** The average loss sustained on the 5% worst days. Always $\ge$ VaR.
5. **Maximum Drawdown:** The deepest peak-to-trough decline experienced over the selected window.
6. **CAPM Beta vs Benchmark:** Sensitivity of the stock's excess returns relative to the NIFTY 50 index.

---

## 3. Overview & Price History Tab

- **Price History & Benchmark (Base 100):** Both the stock and benchmark are normalized to 100 on the first common observation date to facilitate visual relative performance analysis.
- **Cumulative Growth of ₹100:** Illustrates the growth of a hypothetical ₹100 investment over time.
- **Descriptive Statistics Table:** Reports daily mean, median, standard deviation, variance, Fisher-Pearson skewness, excess kurtosis, CAGR, and total return.

---

## 4. Distribution & Fitting Tab

This tab evaluates whether the asset's returns follow Gaussian assumptions or heavy-tailed alternatives.

1. **Return Distribution vs. Fitted Curves:**
   - Empirical frequency histogram of daily returns.
   - Red dashed line: Fitted Gaussian (Normal) Probability Density Function (PDF).
   - Green solid line: Fitted Student-t PDF with estimated degrees of freedom ($\nu$).
2. **Q-Q Diagnostic Plot:**
   - Plots empirical sample quantiles against theoretical quantiles.
   - S-shaped deviations at the extremes reveal fat tails and skewness.
3. **Parametric Goodness-of-Fit Table:**
   - **Log-Likelihood ($\ln L$):** Higher indicates better fit.
   - **AIC & BIC:** Penalize model complexity. Lower is preferred. The model with lower AIC is highlighted as the preferred model.
   - **Degrees of Freedom ($\nu$):** Values below 10 indicate heavy tails. As $\nu \to \infty$, Student-t converges to Normal.
   - **Kolmogorov-Smirnov (KS) Test:** Measures maximum distance between empirical and theoretical CDFs.
   - **Jarque-Bera Test:** Tests joint null hypothesis that skewness and excess kurtosis are zero. A p-value $< 0.05$ rejects normality.
4. **Gaussian Mixture Model (GMM):**
   - Decomposes returns into two distinct market regimes: a low-volatility "calm" regime and a high-volatility "shock" regime.

---

## 5. Risk & Backtesting Tab

1. **Underwater Drawdown History:**
   - Displays continuous equity drawdowns from historical high-water marks.
   - Shaded in red to emphasize capital preservation risk.
2. **Rolling 21-Day Annualized Volatility:**
   - Computes 21-day trailing standard deviation scaled by $\sqrt{252}$. Highlights volatility regimes and clustering.
3. **Walk-Forward Trend Strategy (Zero Lookahead):**
   - Evaluates a 20-day vs. 50-day moving average crossover rule.
   - At day $t$, signal is computed strictly using trailing prices up to close($t$). Trade is executed at close($t+1$).
   - Subtracts realistic transaction costs (default 10 bps / 0.10%).
   - Displays Strategy equity vs. Stock Buy & Hold and Benchmark Index, along with CAGR, Sharpe ratio, win rate, and trade counts.

---

## 6. Sampling & Central Limit Theorem Tab

1. **Bootstrap Confidence Intervals:**
   - Replicates 1,000 bootstrap draws for Mean Return, Annual Volatility, and 95% VaR.
   - Visualizes empirical sampling histograms and reports 95% confidence intervals.
2. **Central Limit Theorem (CLT) Convergence Explorer:**
   - Demonstrates asymptotic normality for a university classroom.
   - Draws repeated samples of size $n \in \{5, 10, 30, 50\}$ from the skewed daily returns.
   - Shows how sample averages become symmetric and Gaussian, with skewness and kurtosis converging to 0 as $n$ grows.

---

## 7. AI Insights & Historical Signal Tab

1. **Actionable Analysis Guide:**
   - Rule-based diagnosis based on observed metrics (e.g., excess kurtosis $> 1.5$, negative skewness, volatility spikes).
   - Generates specific recommendations citing exact quantitative triggers.
2. **Educational Historical Signal (BUY / HOLD / SELL):**
   - Synthesizes statistical evidence into an educational evaluation.
   - Displays a transparent **Deterministic Baseline Score** (-1.0 to +1.0) beside the AI signal.
   - Strict confidence labels: `HIGH`, `MEDIUM`, `LOW`, or `INSUFFICIENT_EVIDENCE`.
   - **Non-Advisory Notice:** Educational historical analysis only. Past performance does not predict future results.

---

## 8. Exporting Data and Reports

- **Export Returns CSV:** Generates a clean CSV file containing Date, Adj Close, Simple Return, Log Return, Cumulative Return, Drawdown, and Rolling Volatility.
- **Download Report:** Generates a comprehensive technical Markdown report containing executive summaries, metric tables, distribution comparisons, and signal analysis suitable for submission or printing.
