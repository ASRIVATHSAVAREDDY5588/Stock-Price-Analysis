"""Export utilities for processed return data and summary analysis reports."""

from __future__ import annotations

import io
from typing import Any, Dict
import pandas as pd


def generate_returns_csv(
    prices: pd.Series,
    returns_simple: pd.Series,
    returns_log: pd.Series,
    cum_returns: pd.Series,
    drawdown: pd.Series,
    rolling_vol: pd.Series,
) -> str:
    """Generate CSV string containing all aligned historical series."""
    df = pd.DataFrame(
        {
            "Adj Close (INR)": prices,
            "Simple Return": returns_simple,
            "Log Return": returns_log,
            "Cumulative Return": cum_returns,
            "Drawdown": drawdown,
            "Rolling 21d Volatility (Ann)": rolling_vol,
        }
    ).dropna(how="all")

    output = io.StringIO()
    df.to_csv(output, index=True, index_label="Date")
    return output.getvalue()


def generate_markdown_report(
    metrics: Dict[str, Any],
    signal_data: Dict[str, Any],
    guide_data: Dict[str, Any],
    backtest_data: Dict[str, Any] | None = None,
) -> str:
    """Produce a concise, professional technical Markdown report for university demonstration."""
    meta = metrics.get("meta", {})
    stats = metrics.get("statistics", {})
    risk = metrics.get("risk", {})
    dist = metrics.get("distribution", {})
    sampling = metrics.get("sampling", {})

    ticker = meta.get("ticker", "N/A")
    bmk = meta.get("benchmark_ticker", "N/A")
    source = meta.get("source", "N/A")
    is_synth = meta.get("is_synthetic", False)
    date_range = meta.get("date_range", "N/A")
    n = stats.get("count", 0)

    supporting_items = "\n".join(f"- {item}" for item in signal_data.get('supporting_metrics', []))
    counter_items = "\n".join(f"- {item}" for item in signal_data.get('counter_evidence', []))
    
    guide_lines = []
    for idx, g in enumerate(guide_data.get('guidance_items', [])):
        guide_lines.append(f"### {idx+1}. {g.get('step_title')}\n- **Trigger:** {g.get('trigger_evidence')}\n- **Recommendation:** {g.get('recommendation')}\n")
    guide_text = "\n".join(guide_lines)

    report = f"""# Stock Market Distribution Analyzer: Quantitative Analysis Report

**Asset Symbol:** {ticker}  
**Benchmark:** {bmk}  
**Data Source:** {source} {'*(SYNTHETIC DEMO DATA)*' if is_synth else ''}  
**Coverage Period:** {date_range} ({n} sessions)  
**Report Generated:** {meta.get('last_updated', 'N/A')}  

---

## 1. Executive Statistical Summary

| Metric | Daily Value | Annualized Convention ({stats.get('annualization_convention', '252 days')}) |
| :--- | :--- | :--- |
| **Mean Return** | {stats.get('mean_daily', 0)*100:.3f}% | {stats.get('annual_mean_compound', 0)*100:.2f}% (Compound) / {stats.get('annual_mean_arithmetic', 0)*100:.2f}% (Arithmetic) |
| **Median Return** | {stats.get('median_daily', 0)*100:.3f}% | — |
| **Volatility (Std Dev)** | {stats.get('std_daily', 0)*100:.3f}% | {stats.get('annual_volatility', 0)*100:.2f}% (Daily scaled by sqrt(252)) |
| **Cumulative Return** | — | {stats.get('cumulative_return', 0)*100:.2f}% |
| **CAGR** | — | {stats.get('cagr', 0)*100:.2f}% |
| **Skewness (Fisher-Pearson)** | {stats.get('skewness', 0):.3f} | {'Negative (Downside asymmetry)' if stats.get('skewness', 0) < 0 else 'Positive (Upside skew)'} |
| **Excess Kurtosis** | {stats.get('excess_kurtosis', 0):.3f} | {'Leptokurtic (Fat-tailed)' if stats.get('excess_kurtosis', 0) > 0 else 'Platykurtic (Thin-tailed)'} |
| **Min / Max 1-Day Return** | {stats.get('min', 0)*100:.2f}% / {stats.get('max', 0)*100:.2f}% | — |

---

## 2. Downside & Relative Risk Profile

- **Historical 95% 1-Day VaR:** `{risk.get('historical_var', 0)*100:.2f}%` (On 95% of days, loss does not exceed this cutoff).
- **Historical 95% Expected Shortfall (CVaR):** `{risk.get('expected_shortfall', 0)*100:.2f}%` (Average loss when tail is breached).
- **Maximum Drawdown:** `{risk.get('max_drawdown', 0)*100:.2f}%` (Peak: {risk.get('peak_date')}, Trough: {risk.get('trough_date')}).
- **CAPM Beta vs Benchmark:** `{risk.get('beta', 1.0):.2f}` (Market sensitivity).
- **Correlation with Benchmark:** `{risk.get('correlation', 0.0):.2f}` ($R^2$: {risk.get('r_squared', 0.0):.2f}).
- **Sharpe Ratio (Rf=6.5%):** `{risk.get('sharpe_ratio', 0.0):.2f}`.
- **Sortino Ratio:** `{risk.get('sortino_ratio', 0.0):.2f}`.

> *Note on Period Dependence:* Risk metrics are conditional on the chosen observation window. Historical periods excluding structural market crises understate extreme tail risk.

---

## 3. Distribution Modeling: Normal vs Student-t

| Diagnostic Test / Metric | Normal Model | Student-t Model | Plain-Language Interpretation |
| :--- | :--- | :--- | :--- |
| **Log-Likelihood** | {dist.get('normal', {}).get('log_likelihood', 0):.1f} | {dist.get('student_t', {}).get('log_likelihood', 0):.1f} | Higher indicates closer fit to empirical data. |
| **AIC (Akaike Criterion)** | {dist.get('normal', {}).get('aic', 0):.1f} | {dist.get('student_t', {}).get('aic', 0):.1f} | Lower is preferred. Student-t delta: {dist.get('model_comparison', {}).get('aic_difference', 0):.1f}. |
| **Degrees of Freedom (nu)**| Normal | {dist.get('student_t', {}).get('df', 100):.2f} | nu < 10 indicates heavy tails and jump susceptibility. |
| **KS Test p-value** | {dist.get('normal', {}).get('ks_p_value', 0):.4f} | {dist.get('student_t', {}).get('ks_p_value', 0):.4f} | Tests empirical CDF congruence. |
| **Jarque-Bera Normality Test** | Stat: {dist.get('jarque_bera', {}).get('statistic', 0):.1f} | p-value: {dist.get('jarque_bera', {}).get('p_value', 1.0):.4e} | {'Rejects normality (p < 0.05).' if dist.get('jarque_bera', {}).get('reject_normality_at_5pct') else 'Fails to reject normality.'} |

*Preferred Distribution by Information Criterion:* **{dist.get('model_comparison', {}).get('preferred_model_by_aic', 'Normal')}**.  
*Epistemological Note:* Statistical testing selects the superior approximation; it does not prove the actual generating mechanism is literally identical to the model.

---

## 4. Sampling & Bootstrap Analysis

- **Bootstrap Method:** {sampling.get('method', 'iid').upper()} (Iterations: {sampling.get('iterations', 1000)}, Seed: {sampling.get('seed', 'None')})
- **Mean Daily Return 95% CI:** `[{sampling.get('mean_return', {}).get('ci_lower', 0)*100:.3f}%, {sampling.get('mean_return', {}).get('ci_upper', 0)*100:.3f}%]`
- **Annualized Volatility 95% CI:** `[{sampling.get('annual_volatility', {}).get('ci_lower', 0)*100:.2f}%, {sampling.get('annual_volatility', {}).get('ci_upper', 0)*100:.2f}%]`
- **Historical 95% VaR 95% CI:** `[{sampling.get('var_95', {}).get('ci_lower', 0)*100:.2f}%, {sampling.get('var_95', {}).get('ci_upper', 0)*100:.2f}%]`

---

## 5. Educational Historical Signal & AI Analysis

- **Educational Signal:** **{signal_data.get('signal', 'HOLD')}**
- **Evidence Stability / Confidence:** `{signal_data.get('confidence', 'LOW')}`
- **Engine Used:** {signal_data.get('engine', 'Deterministic')}
- **Deterministic Baseline Score:** `{signal_data.get('deterministic_baseline', {}).get('baseline_score', 0.0)}` (Rule-based: {signal_data.get('deterministic_baseline', {}).get('baseline_signal', 'HOLD')})

**Analytical Rationale:**  
{signal_data.get('rationale', 'N/A')}

**Key Supporting Factors:**  
{supporting_items}

**Counter-Evidence & Downside Risks:**  
{counter_items}

> **Regulatory & Educational Notice:**  
> *{signal_data.get('disclaimer', 'Educational analysis of historical data, not personalized financial advice. Past returns do not predict future results.')}*

---

## 6. Actionable Next Analysis Steps (Analysis Guide)

{guide_text}

---
*Report compiled automatically by Stock Market Distribution Analyzer. Academic & research demonstration software.*
"""
    return report
