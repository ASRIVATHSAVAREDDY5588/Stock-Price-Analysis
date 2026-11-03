"""Risk analytics: Historical VaR, Expected Shortfall, Maximum Drawdown, Rolling Volatility, and Benchmark Beta."""

from __future__ import annotations

from typing import Any, Dict, Optional, Tuple
import numpy as np
import pandas as pd
from scipy import stats

from config import TRADING_DAYS_PER_YEAR


def compute_var_and_es(
    returns: pd.Series,
    confidence_level: float = 0.95,
) -> Dict[str, float]:
    """Calculate Historical and Parametric Value at Risk (VaR) and Expected Shortfall (CVaR).

    By financial convention, VaR and ES are expressed as positive loss percentages
    representing the minimum and average expected loss in the tail.

    Args:
        returns: Daily return series.
        confidence_level: Confidence level in (0, 1), e.g. 0.95 or 0.99.

    Returns:
        Dict with historical_var, parametric_var, expected_shortfall, tail_observation_count.
    """
    clean_ret = returns.dropna().values
    n = len(clean_ret)
    if n < 5:
        return {
            "confidence_level": confidence_level,
            "historical_var": 0.0,
            "parametric_var": 0.0,
            "expected_shortfall": 0.0,
            "tail_observations": 0,
        }

    alpha = 1.0 - confidence_level

    # 1. Historical VaR
    # Quantile at alpha (e.g. 5th percentile)
    cutoff = float(np.percentile(clean_ret, alpha * 100.0))
    # Reported as positive loss: -cutoff
    historical_var = -cutoff

    # 2. Expected Shortfall (CVaR)
    # Mean of returns in the tail (<= cutoff)
    tail_returns = clean_ret[clean_ret <= cutoff]
    if len(tail_returns) > 0:
        expected_shortfall = -float(np.mean(tail_returns))
    else:
        expected_shortfall = historical_var

    # 3. Parametric VaR (assuming Normal distribution)
    mu = float(np.mean(clean_ret))
    sigma = float(np.std(clean_ret, ddof=1))
    z_score = float(stats.norm.ppf(confidence_level))
    parametric_var = -(mu - z_score * sigma)

    return {
        "confidence_level": confidence_level,
        "historical_var": float(historical_var),
        "parametric_var": float(parametric_var),
        "expected_shortfall": float(expected_shortfall),
        "tail_observations": int(len(tail_returns)),
        "tail_threshold_return": float(cutoff),
    }


def compute_drawdown_series(prices: pd.Series) -> Tuple[pd.Series, Dict[str, Any]]:
    """Compute underwater drawdown series and drawdown extrema.

    Args:
        prices: Historical price series.

    Returns:
        (drawdown_series, drawdown_metadata_dict)
    """
    clean_p = prices.dropna().astype(float)
    if len(clean_p) < 2:
        empty = pd.Series(0.0, index=clean_p.index)
        return empty, {"max_drawdown": 0.0, "peak_date": "N/A", "trough_date": "N/A", "is_recovered": True}

    running_max = clean_p.cummax()
    drawdown = (clean_p - running_max) / running_max
    drawdown.name = "Drawdown"

    max_dd = float(drawdown.min())
    trough_date = drawdown.idxmin()

    # Peak before trough
    peak_date = clean_p.loc[:trough_date].idxmax()

    # Recovery date after trough
    peak_val = clean_p.loc[peak_date]
    after_trough = clean_p.loc[trough_date:]
    recovered_points = after_trough[after_trough >= peak_val]

    if not recovered_points.empty:
        recovery_date = recovered_points.index[0]
        is_recovered = True
        duration_days = (recovery_date - peak_date).days
    else:
        recovery_date = None
        is_recovered = False
        duration_days = (clean_p.index[-1] - peak_date).days

    meta = {
        "max_drawdown": max_dd,
        "peak_date": peak_date.strftime("%Y-%m-%d"),
        "trough_date": trough_date.strftime("%Y-%m-%d"),
        "recovery_date": recovery_date.strftime("%Y-%m-%d") if recovery_date else "Still in Drawdown",
        "is_recovered": is_recovered,
        "drawdown_duration_days": duration_days,
    }

    return drawdown, meta


def compute_rolling_volatility(
    returns: pd.Series,
    window: int = 21,
    trading_days: int = TRADING_DAYS_PER_YEAR,
) -> pd.Series:
    """Compute rolling annualized volatility over a trailing window (e.g. 21 days ~ 1 trading month)."""
    clean_ret = returns.dropna()
    rolling_std = clean_ret.rolling(window=window, min_periods=max(5, window // 2)).std(ddof=1)
    rolling_ann_vol = rolling_std * np.sqrt(trading_days)
    rolling_ann_vol.name = f"Rolling_{window}d_Vol"
    return rolling_ann_vol


def compute_benchmark_relative_risk(
    stock_returns: pd.Series,
    benchmark_returns: pd.Series,
    stock_prices: Optional[pd.Series] = None,
    risk_free_rate: float = 0.065,  # 6.5% standard Indian 10Y G-Sec yield
    trading_days: int = TRADING_DAYS_PER_YEAR,
) -> Dict[str, Any]:
    """Calculate CAPM Beta, Correlation, Sharpe Ratio, Sortino Ratio, and Tracking Error.

    Args:
        stock_returns: Daily returns of target stock.
        benchmark_returns: Daily returns of benchmark index (e.g. NIFTY 50).
        stock_prices: Optional price series for CAGR.
        risk_free_rate: Annual risk-free rate (default 6.5% for India).
        trading_days: 252 trading days.
    """
    # Align dates
    df = pd.DataFrame({"stock": stock_returns, "bmk": benchmark_returns}).dropna()
    n = len(df)
    if n < 10:
        return {
            "beta": 1.0,
            "correlation": 0.0,
            "r_squared": 0.0,
            "sharpe_ratio": 0.0,
            "sortino_ratio": 0.0,
            "tracking_error": 0.0,
            "information_ratio": 0.0,
            "risk_free_rate": risk_free_rate,
        }

    s_ret = df["stock"].values
    b_ret = df["bmk"].values

    # Covariance & Variance
    cov_matrix = np.cov(s_ret, b_ret, ddof=1)
    cov_sb = cov_matrix[0, 1]
    var_b = cov_matrix[1, 1]
    std_s = np.std(s_ret, ddof=1)
    std_b = np.std(b_ret, ddof=1)

    beta = float(cov_sb / var_b) if var_b > 1e-12 else 1.0
    corr = float(cov_sb / (std_s * std_b)) if (std_s * std_b) > 1e-12 else 0.0
    r_squared = float(corr ** 2)

    # Annual returns
    ann_s_ret = float(np.mean(s_ret) * trading_days)
    ann_s_vol = float(std_s * np.sqrt(trading_days))

    # Sharpe Ratio
    excess_ret = ann_s_ret - risk_free_rate
    sharpe = float(excess_ret / ann_s_vol) if ann_s_vol > 1e-12 else 0.0

    # Sortino Ratio (downside deviation only)
    downside_diff = np.minimum(0.0, s_ret - (risk_free_rate / trading_days))
    downside_dev = float(np.sqrt(np.mean(downside_diff ** 2)) * np.sqrt(trading_days))
    sortino = float(excess_ret / downside_dev) if downside_dev > 1e-12 else 0.0

    # Tracking Error & Information Ratio vs Benchmark
    diff_ret = s_ret - b_ret
    tracking_error = float(np.std(diff_ret, ddof=1) * np.sqrt(trading_days))
    ann_excess_bmk = float(np.mean(diff_ret) * trading_days)
    info_ratio = float(ann_excess_bmk / tracking_error) if tracking_error > 1e-12 else 0.0

    return {
        "beta": beta,
        "correlation": corr,
        "r_squared": r_squared,
        "sharpe_ratio": sharpe,
        "sortino_ratio": sortino,
        "tracking_error": tracking_error,
        "information_ratio": info_ratio,
        "risk_free_rate": risk_free_rate,
        "downside_deviation": downside_dev,
        "period_dependent_note": "Risk measures are sample-specific: calculating over a quiet bull market will understate downside risk, while a crisis window will elevate it.",
    }
