"""Descriptive statistics and annualization conventions for return series."""

from __future__ import annotations

from typing import Any, Dict
import numpy as np
import pandas as pd
from scipy import stats

from config import TRADING_DAYS_PER_YEAR


def compute_descriptive_statistics(
    returns: pd.Series,
    prices: pd.Series | None = None,
    trading_days: int = TRADING_DAYS_PER_YEAR,
) -> Dict[str, Any]:
    """Compute comprehensive descriptive statistics for daily returns.

    Args:
        returns: Clean series of daily returns (simple or log).
        prices: Optional series of underlying asset prices for CAGR calculation.
        trading_days: Number of trading sessions per year (252 for Indian markets).

    Returns:
        Dictionary of raw and human-readable metrics.
    """
    clean_ret = returns.dropna().astype(float)
    n = len(clean_ret)

    if n < 2:
        return {
            "count": n,
            "error": "Insufficient observations to compute descriptive statistics.",
        }

    # Central moments
    mean_daily = float(np.mean(clean_ret))
    median_daily = float(np.median(clean_ret))
    variance_daily = float(np.var(clean_ret, ddof=1))
    std_daily = float(np.std(clean_ret, ddof=1))

    # Higher moments (Fisher-Pearson, unbiased)
    skewness = float(stats.skew(clean_ret, bias=False)) if std_daily > 1e-12 else 0.0
    excess_kurtosis = float(stats.kurtosis(clean_ret, fisher=True, bias=False)) if std_daily > 1e-12 else 0.0

    # Range and extremes
    min_val = float(np.min(clean_ret))
    max_val = float(np.max(clean_ret))

    # Percentiles
    percentile_levels = [1, 5, 10, 25, 50, 75, 90, 95, 99]
    percentiles_raw = {f"p{p}": float(np.percentile(clean_ret, p)) for p in percentile_levels}

    # Annualization conventions
    # Compound annual mean: (1 + mean_daily)^252 - 1
    # Arithmetic annual mean: mean_daily * 252
    if mean_daily > -1.0:
        annual_mean_compound = float((1.0 + mean_daily) ** trading_days - 1.0)
    else:
        annual_mean_compound = -1.0
    annual_mean_arithmetic = float(mean_daily * trading_days)

    # Annualized volatility: std_daily * sqrt(252)
    annual_volatility = float(std_daily * np.sqrt(trading_days))

    # Cumulative return
    cum_return = float(np.prod(1.0 + clean_ret) - 1.0)

    # CAGR if prices are provided
    cagr = None
    if prices is not None and len(prices) >= 2:
        p_start = float(prices.iloc[0])
        p_end = float(prices.iloc[-1])
        if p_start > 0 and p_end > 0:
            years = max(n / trading_days, 1e-4)
            cagr = float((p_end / p_start) ** (1.0 / years) - 1.0)

    return {
        "count": n,
        "mean_daily": mean_daily,
        "median_daily": median_daily,
        "variance_daily": variance_daily,
        "std_daily": std_daily,
        "annual_mean_compound": annual_mean_compound,
        "annual_mean_arithmetic": annual_mean_arithmetic,
        "annual_volatility": annual_volatility,
        "skewness": skewness,
        "excess_kurtosis": excess_kurtosis,
        "min": min_val,
        "max": max_val,
        "percentiles": percentiles_raw,
        "cumulative_return": cum_return,
        "cagr": cagr if cagr is not None else annual_mean_compound,
        "annualization_convention": f"{trading_days} trading days per year (Indian National Stock Exchange / BSE convention: volatility scales as sigma * sqrt({trading_days})).",
    }
