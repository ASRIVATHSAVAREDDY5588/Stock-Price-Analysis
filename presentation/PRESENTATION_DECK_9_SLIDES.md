# Stock Market Return Distribution Analyzer: 9-Slide Review Presentation Deck

> **Course Code:** 24AD3107 (Data Science Project)  
> **Academic Year:** 2026–2027  
> **Institution:** Department of Computer Science and Engineering, KLH University, Hyderabad  
> **Team Members:**  
> - **Srivathsava Reddy** — **2420030634**  
> - **Aryan Salunkhe** — **2420030137**  
> **Project Guide:** **Dr. N. Sunanda**  
> **Source Presentation File:** [`presentation/pptx/Course_24AD3107_Project_Review_9_Slides.pptx`](pptx/Course_24AD3107_Project_Review_9_Slides.pptx)

---

## Slide 1: Title Slide
* **Title:** Stock Market Return Distribution Analyzer
* **Course:** Data Science Project • Course: **24AD3107** • Academic Year: **2026–2027**
* **Authors:**
  * Srivathsava Reddy — **2420030634**
  * Aryan Salunkhe — **2420030137**
* **Project Guide:** Dr. N. Sunanda

---

## Slide 2: Project Overview
* Analyze historical stock market returns using data science and statistical methodologies.
* Collect historical stock prices for selected Indian companies.
* Calculate daily returns from historical closing prices.
* Study statistical properties and continuous probability distributions of returns.
* Present empirical results through visualizations and an interactive web dashboard.

---

## Slide 3: Data Processing & Return Calculation
1. **Historical Data:** Collect historical closing-price data for selected companies (e.g., Reliance Industries, NIFTY 50).
2. **Daily Returns:** Calculate daily stock returns from consecutive closing prices.
3. **Analysis Dataset:** Prepare the return series for statistical and distribution analysis.
* The return series becomes the main input for probability, sampling, and visualization modules.
* The project focuses on understanding the empirical behavior of historical returns.

---

## Slide 4: Statistical Analysis
* **Mean:** Average return of the observed market data.
* **Variance:** Measures the dispersion and spread of returns around the mean.
* **Standard Deviation:** Measures daily and annualized return variability.
* **Skewness:** Describes asymmetry and direction of outliers in the distribution.
* **Kurtosis:** Describes the peakedness, tail thickness, and frequency of extreme market moves.

---

## Slide 5: Return Distribution Analysis
* **Histogram:** Shows how frequently different return values occur across predefined bins.
* **Density Plot:** Provides a smooth continuous view of the empirical return distribution.
* **Q–Q Plot:** Compares observed return quantiles directly with theoretical normal quantiles.
* Statistical goodness-of-fit tests are applied to examine whether stock returns follow a Gaussian normal distribution.
* Different visualizations help compare actual return behavior with theoretical assumptions.

---

## Slide 6: Sampling & Bootstrap
* **Sampling:** Different subsets of historical returns are selected to study sampling variability across market regimes.
* **Bootstrap Sampling:** Repeated resampling with replacement ($B = 1,000$ iterations) is used to estimate empirical distributions of sample statistics.
* Bootstrap methods are used to calculate non-parametric confidence intervals.
* The approach helps students understand estimation uncertainty in sample statistics.

---

## Slide 7: Central Limit Theorem (CLT)
* Repeated samples are drawn from the historical return series.
* Different sample sizes are analyzed ($N = 5, 10, 30, 50$).
* The distribution of sample means is examined as sample size expands.
* Demonstrates how sample-mean distributions converge toward normality and exhibit variance decay by factor $1/\sqrt{N}$.
* The project connects abstract CLT concepts with real-world historical financial data.

---

## Slide 8: Interactive Dashboard
* **Stock Selection:** Users can select preloaded Indian stocks (Reliance, TCS, Infosys, HDFC Bank) or upload custom CSV series.
* **Statistics:** View comprehensive statistical properties, moments, and risk measures.
* **Visualizations:** Explore dynamic distributions, sampling histograms, Q-Q plots, and drawdown charts.
* The dashboard presents quantitative analysis in an intuitive, accessible interface.
* Combines statistical and probability concepts into a unified local web application.

---

## Slide 9: Conclusion & Thank You
* The project provides a practical data-science framework for analyzing stock market return distributions.
* Combines statistical measures, probability distributions, sampling, bootstrap methods, and the Central Limit Theorem.
* Interactive visualizations make the behavior of historical returns easier to understand.
* The interactive dashboard unifies the analysis for user exploration.
* **Thank You!** Questions and discussion welcomed.
