"""Update presentation_extraction/slide_facts.json with exact 2000-2026 YTD metrics and modern citations."""

from __future__ import annotations

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SLIDE_FACTS_PATH = PROJECT_ROOT / "presentation" / "slide_facts.json"
if not SLIDE_FACTS_PATH.exists():
    SLIDE_FACTS_PATH = PROJECT_ROOT.parent / "presentation_extraction" / "slide_facts.json"


def update_facts():
    with open(SLIDE_FACTS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    for slide in data:
        num = slide.get("slide_number")
        if num == 4:
            slide["facts"] = [
                {
                    "field": "Foundational Literature",
                    "value": "Mandelbrot (1963) & Fama (1965): Leptokurtosis and heavy tails in asset returns. Artzner et al. (1999): Coherent risk measures & Expected Shortfall. Künsch (1989) / Politis & Romano (1994): Block bootstrap for dependent series.",
                    "status": "VERIFIED",
                    "evidence_path": "Stock_Return_AI_Lab/THIRD_PARTY_NOTICES.md"
                },
                {
                    "field": "Modern Literature 1: Risk & ML Methodology",
                    "value": "López de Prado, M. (2018). Advances in Financial Machine Learning. Wiley. DOI: 10.1002/9781119482109. (Eliminates look-ahead leakage; enforces walk-forward backtesting).",
                    "status": "VERIFIED",
                    "evidence_path": "Wiley Online Library / CrossRef DOI: 10.1002/9781119482109"
                },
                {
                    "field": "Modern Literature 2: Joint VaR & ES Modeling",
                    "value": "Taylor, J. W. (2019). Forecasting Value at Risk and Expected Shortfall. Journal of Business & Economic Statistics, 37(1), 121-133. DOI: 10.1080/07350015.2017.1281815.",
                    "status": "VERIFIED",
                    "evidence_path": "Taylor & Francis / CrossRef DOI: 10.1080/07350015.2017.1281815"
                },
                {
                    "field": "Modern Literature 3: Return Modeling & Regularization",
                    "value": "Gu, S., Kelly, B., & Xiu, D. (2020). Empirical Asset Pricing via Machine Learning. Review of Financial Studies, 33(5), 2223-2273. DOI: 10.1093/rfs/hhaa009.",
                    "status": "VERIFIED",
                    "evidence_path": "Oxford University Press / CrossRef DOI: 10.1093/rfs/hhaa009"
                },
                {
                    "field": "Modern Literature 4: Explainable AI in Finance",
                    "value": "Arrieta, A. B., et al. (2020). Explainable Artificial Intelligence (XAI): Concepts, taxonomies, opportunities and challenges. Information Fusion, 58, 82-115. DOI: 10.1016/j.inffus.2019.12.012.",
                    "status": "VERIFIED",
                    "evidence_path": "Elsevier / CrossRef DOI: 10.1016/j.inffus.2019.12.012"
                },
                {
                    "field": "Modern Literature 5: Time Series Forecasting",
                    "value": "Lim, B., & Zohren, S. (2021). Time-series forecasting with deep learning: a survey. Phil. Trans. R. Soc. A, 379(2194), 20200209. DOI: 10.1098/rsta.2020.0209.",
                    "status": "VERIFIED",
                    "evidence_path": "Royal Society Publishing / CrossRef DOI: 10.1098/rsta.2020.0209"
                },
                {
                    "field": "Modern Literature 6: Alpha & Risk Premia Testing",
                    "value": "Pesaran, M. H., & Yamagata, T. (2024). Testing for Alpha in Linear Factor Pricing Models. Journal of Financial Econometrics, 22(2), 407-460. DOI: 10.1093/jjfinec/nbad002.",
                    "status": "VERIFIED",
                    "evidence_path": "Oxford Academic / CrossRef DOI: 10.1093/jjfinec/nbad002"
                },
                {
                    "field": "Practical Engineering Motivation",
                    "value": "Applied Data Science Workbench: Translates theoretical heavy-tailed distributions and coherent risk measures into an interactive, reproducible educational testbed for Indian equities (2000–2026 YTD).",
                    "status": "VERIFIED",
                    "evidence_path": "Stock_Return_AI_Lab/PROJECT_SCOPE.md"
                }
            ]
        elif num == 8:
            slide["facts"] = [
                {
                    "field": "Primary Sourced Dataset (2000–2026 YTD)",
                    "value": "reliance_cleaned_2000_2026.csv: 6,615 daily records; Columns: Date, Adj Close, Close, Volume; Span: 2000-01-03 to 2026-11-02",
                    "status": "VERIFIED",
                    "evidence_path": "Stock_Return_AI_Lab/data/cleaned/reliance_cleaned_2000_2026.csv"
                },
                {
                    "field": "NIFTY 50 Benchmark Dataset",
                    "value": "nifty50_cleaned_2000_2026.csv: 6,615 daily records; Span: 2000-01-03 to 2026-11-02 (Yahoo Finance 2007-2026 merged with official NSE archive 2000-2007)",
                    "status": "VERIFIED",
                    "evidence_path": "Stock_Return_AI_Lab/data/cleaned/nifty50_cleaned_2000_2026.csv"
                },
                {
                    "field": "Multi-Stock Dataset",
                    "value": "multi_stock_sample.csv: 19,845 records across 3 tickers (INFY.NS, RELIANCE.NS, TCS.NS; 6,615 rows each)",
                    "status": "VERIFIED",
                    "evidence_path": "Stock_Return_AI_Lab/data/sample_data/multi_stock_sample.csv"
                },
                {
                    "field": "Raw vs Cleaned Separation",
                    "value": "Raw datasets preserved unedited in data/raw/ (reliance_raw_2000_2026.csv, nifty50_raw_yahoo_2007_2026.csv, nifty50_raw_historical_archive_1990_2019.csv, bse_sensex_raw_2000_2026.csv)",
                    "status": "VERIFIED",
                    "evidence_path": "Stock_Return_AI_Lab/reports/DATA_SOURCE_AND_QUALITY_REPORT.md"
                },
                {
                    "field": "Data Cleanliness & Corporate Actions",
                    "value": "0 missing values in aligned 6,615 sessions; automatic deduplication and positive price filtering; corporate bonuses (2009, 2017, 2024), splits, and dividends fully accounted for in Adj Close.",
                    "status": "VERIFIED",
                    "evidence_path": "Stock_Return_AI_Lab/reports/DATA_SOURCE_AND_QUALITY_REPORT.md"
                },
                {
                    "field": "Benchmark Limitation Notice",
                    "value": "NIFTY 50 is a Price Return index (PR), omitting dividend reinvestment (~1.2%–1.5% p.a.). Comparison against dividend-adjusted stock returns slightly flatters relative stock alpha.",
                    "status": "VERIFIED",
                    "evidence_path": "Stock_Return_AI_Lab/reports/DATA_SOURCE_AND_QUALITY_REPORT.md"
                }
            ]
        elif num == 9:
            slide["facts"] = [
                {
                    "field": "Cleaning Steps",
                    "value": "1. Multi-format datetime coercion; 2. Strict chronological sorting; 3. Non-positive price filtering; 4. Calendar date inner-intersection (6,615 sessions).",
                    "status": "VERIFIED",
                    "evidence_path": "Stock_Return_AI_Lab/data/pipeline_fetch_and_clean.py"
                },
                {
                    "field": "Return Formulations",
                    "value": "Simple arithmetic return R_t = (P_t / P_{t-1}) - 1; Logarithmic return r_t = ln(P_t / P_{t-1}); Annualization convention = 252 trading sessions.",
                    "status": "VERIFIED",
                    "evidence_path": "Stock_Return_AI_Lab/analytics/returns.py"
                },
                {
                    "field": "Reliance Long-Horizon Statistics (2000–2026 YTD)",
                    "value": "Daily mean: +0.0890%, Annualized Volatility: 32.71%, Cumulative Return: +9,472.5% (Initial ₹13.18 to ₹1,262.00, CAGR: 18.98% vs Benchmark CAGR 10.76%).",
                    "status": "COMPUTED",
                    "evidence_path": "Computed on reliance_cleaned_2000_2026.csv; reports/project_computed_metrics.json"
                },
                {
                    "field": "Shape Moments & Normality Rejection",
                    "value": "Sample Skewness: +0.3865; Excess Kurtosis: +8.4451 (Massive leptokurtosis; severe fat tails); Jarque-Bera Stat: 19,301.9, p < 1e-15 (Normality decisively rejected).",
                    "status": "COMPUTED",
                    "evidence_path": "Computed on reliance_cleaned_2000_2026.csv; reports/project_computed_metrics.json"
                },
                {
                    "field": "Cross-Period Historical Contrast",
                    "value": "2000-2009: CAGR 33.13%, Vol 40.56%, Kurtosis +6.95; 2010-2019: CAGR 12.37%, Vol 26.27%, Kurtosis +2.08; 2020-2026 YTD: CAGR 9.84%, Vol 27.86%, Kurtosis +10.62.",
                    "status": "COMPUTED",
                    "evidence_path": "reports/project_computed_metrics.json"
                }
            ]
        elif num == 14:
            slide["facts"] = [
                {
                    "field": "Normal Fit Results (2000–2026 YTD)",
                    "value": "Log-Likelihood: +16,292.4 | AIC: -32,580.7 | BIC: -32,567.1 | KS Test p-value: 1.79e-23 | Jarque-Bera p < 1e-15 (Gaussian Model Decisively Rejected)",
                    "status": "COMPUTED",
                    "evidence_path": "Computed on reliance_cleaned_2000_2026.csv; reports/project_computed_metrics.json"
                },
                {
                    "field": "Student-t Fit Results (2000–2026 YTD)",
                    "value": "Log-Likelihood: +16,948.5 | AIC: -33,890.9 | BIC: -33,870.5 | KS Test p-value: 0.7796 | Degrees of freedom: nu = 3.64",
                    "status": "COMPUTED",
                    "evidence_path": "Computed on reliance_cleaned_2000_2026.csv; reports/project_computed_metrics.json"
                },
                {
                    "field": "Model Preference & Information Criteria",
                    "value": "Student-t distribution is overwhelmingly preferred by Delta AIC = -1,310.2 and KS p = 0.7796, proving that fat-tail modeling is mathematically indispensable.",
                    "status": "COMPUTED",
                    "evidence_path": "reports/project_computed_metrics.json"
                },
                {
                    "field": "Sub-Period Tail Parameter Evolution",
                    "value": "Estimated nu: 3.44 (2000-2009, Delta AIC -481.1) -> 7.15 (2010-2019, Delta AIC -101.9) -> 3.36 (2020-2026 YTD, Delta AIC -440.2).",
                    "status": "COMPUTED",
                    "evidence_path": "reports/project_computed_metrics.json"
                },
                {
                    "field": "Classifier Metrics Flag",
                    "value": "Accuracy, Precision, Recall, F1, ROC-AUC are N/A: The project models continuous return probability distributions and tail risk, not discrete supervised classification.",
                    "status": "VERIFIED",
                    "evidence_path": "Stock_Return_AI_Lab/PROJECT_SCOPE.md"
                }
            ]
        elif num == 15:
            slide["facts"] = [
                {
                    "field": "Finding 1: Tail Risk Underestimation",
                    "value": "95% Historical VaR is -2.93%, but Expected Shortfall (CVaR) jumps to -4.47% (52.6% larger). 99% Historical VaR is -5.26%, ES is -7.57% (vs Normal VaR of -4.70%).",
                    "status": "COMPUTED",
                    "evidence_path": "reports/project_computed_metrics.json"
                },
                {
                    "field": "Finding 2: Multi-Year Drawdown Cycles",
                    "value": "Reliance experienced a -68.18% maximum drawdown during the 2008 GFC (14-Jan-2008 to 24-Oct-2008; required 3,462 days to recover in Jul 2017) and -44.08% in March 2020 (recovered in 139 days).",
                    "status": "COMPUTED",
                    "evidence_path": "reports/project_computed_metrics.json"
                },
                {
                    "field": "Finding 3: Structural Regime Shifts",
                    "value": "Decadal breakdown reveals structural regime shifts: 2000-2009 (high growth 33.1% CAGR, high vol 40.6%) -> 2010-2019 (consolidation 12.4% CAGR) -> 2020-2026 YTD (heavy tails nu=3.36, Kurtosis +10.62).",
                    "status": "COMPUTED",
                    "evidence_path": "reports/project_computed_metrics.json"
                },
                {
                    "field": "Finding 4: Benchmark Sensitivity (CAPM)",
                    "value": "CAPM Beta = 1.10, Correlation = 0.73, Sharpe Ratio = 0.50 against NIFTY 50 (Rf = 6.50%).",
                    "status": "COMPUTED",
                    "evidence_path": "reports/project_computed_metrics.json"
                },
                {
                    "field": "Finding 5: Walk-Forward Backtesting Under Friction",
                    "value": "Full Sample 20d/50d trend strategy achieved 9.24% CAGR (166 trades, 43.4% win rate) vs 18.98% buy-and-hold with 10 bps fees. In-Sample Train (2000-2015): 11.03% vs 19.65%; Out-of-Sample Test (2016-2026 YTD): 7.79% vs 18.20%.",
                    "status": "COMPUTED",
                    "evidence_path": "reports/project_computed_metrics.json"
                }
            ]
        elif num == 21:
            slide["facts"] = [
                {
                    "field": "Foundational Citations",
                    "value": "Mandelbrot (1963), Fama (1965), Artzner et al. (1999), Künsch (1989), Politis & Romano (1994).",
                    "status": "VERIFIED",
                    "evidence_path": "Stock_Return_AI_Lab/THIRD_PARTY_NOTICES.md"
                },
                {
                    "field": "Modern Citations (2018–2026)",
                    "value": "López de Prado (2018, Wiley DOI: 10.1002/9781119482109), Taylor (2019, JBES DOI: 10.1080/07350015.2017.1281815), Gu et al. (2020, RFS DOI: 10.1093/rfs/hhaa009), Arrieta et al. (2020, Info Fusion DOI: 10.1016/j.inffus.2019.12.012), Lim & Zohren (2021, Phil Trans A DOI: 10.1098/rsta.2020.0209), Pesaran & Yamagata (2024, J. Fin. Econometrics DOI: 10.1093/jjfinec/nbad002).",
                    "status": "VERIFIED",
                    "evidence_path": "Verified via Publisher DOIs"
                },
                {
                    "field": "Open Source Licenses",
                    "value": "Flask (BSD 3-Clause), NumPy & SciPy (BSD 3-Clause), Plotly.js (MIT), yfinance (Apache 2.0), pytest (MIT)",
                    "status": "VERIFIED",
                    "evidence_path": "Stock_Return_AI_Lab/THIRD_PARTY_NOTICES.md"
                }
            ]

    with open(SLIDE_FACTS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print("slide_facts.json successfully updated!")


if __name__ == "__main__":
    update_facts()
