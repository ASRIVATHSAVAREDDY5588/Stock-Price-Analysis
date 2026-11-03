"""Bootstrap confidence intervals (IID & Moving-Block) and Central Limit Theorem explorer."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd
from scipy import stats

from config import TRADING_DAYS_PER_YEAR


def run_bootstrap_simulation(
    returns: pd.Series,
    iterations: int = 1000,
    confidence_level: float = 0.95,
    method: str = "iid",  # 'iid' or 'block'
    block_size: int = 5,
    seed: Optional[int] = 42,
) -> Dict[str, Any]:
    """Calculate bootstrap confidence intervals for Mean, Volatility, and 95% VaR.

    Supports both standard IID resampling and Moving-Block resampling (to preserve time-series dependence).

    Args:
        returns: Clean daily return series.
        iterations: Number of bootstrap replications (e.g. 1000).
        confidence_level: Nominal CI coverage, e.g. 0.95.
        method: 'iid' or 'block'.
        block_size: Window length for moving block bootstrap (e.g. 5 or 10 days).
        seed: Random seed for reproducibility.

    Returns:
        Structured dictionary with point estimates, standard errors, confidence intervals,
        and resampled arrays for visual distribution plotting.
    """
    clean_ret = returns.dropna().values.astype(float)
    n = len(clean_ret)

    if n < 15:
        return {"error": "Insufficient observations for bootstrap (N < 15)."}

    rng = np.random.default_rng(seed)

    # Point estimates on observed sample
    obs_mean = float(np.mean(clean_ret))
    obs_std = float(np.std(clean_ret, ddof=1))
    obs_ann_vol = float(obs_std * np.sqrt(TRADING_DAYS_PER_YEAR))
    obs_var95 = float(-np.percentile(clean_ret, 5.0))

    boot_means = np.empty(iterations)
    boot_vols = np.empty(iterations)
    boot_vars = np.empty(iterations)

    alpha = 1.0 - confidence_level
    lower_pct = (alpha / 2.0) * 100.0
    upper_pct = (1.0 - alpha / 2.0) * 100.0

    if method == "block" and block_size > 1 and block_size < n:
        # High-performance vectorized block bootstrap
        num_blocks = int(np.ceil(n / block_size))
        max_start = n - block_size + 1
        start_indices = rng.integers(0, max_start, size=(iterations, num_blocks))
        blocks = np.empty((iterations, n), dtype=clean_ret.dtype)
        for b_idx in range(num_blocks):
            col_start = b_idx * block_size
            col_end = min(n, col_start + block_size)
            actual_len = col_end - col_start
            starts = start_indices[:, b_idx]
            for i in range(actual_len):
                blocks[:, col_start + i] = clean_ret[starts + i]
        boot_means = np.mean(blocks, axis=1)
        boot_vols = np.std(blocks, axis=1, ddof=1) * np.sqrt(TRADING_DAYS_PER_YEAR)
        boot_vars = -np.percentile(blocks, 5.0, axis=1)
    else:
        # High-performance 2D vectorized IID bootstrap (< 15ms)
        idx_matrix = rng.integers(0, n, size=(iterations, n))
        resamples = clean_ret[idx_matrix]
        boot_means = np.mean(resamples, axis=1)
        boot_vols = np.std(resamples, axis=1, ddof=1) * np.sqrt(TRADING_DAYS_PER_YEAR)
        boot_vars = -np.percentile(resamples, 5.0, axis=1)

    def summarize_metric(point: float, boot_arr: np.ndarray, is_annualized: bool = False) -> dict:
        se = float(np.std(boot_arr, ddof=1))
        ci_low = float(np.percentile(boot_arr, lower_pct))
        ci_high = float(np.percentile(boot_arr, upper_pct))
        # Return 25-bin histogram for dashboard visualization
        counts, bin_edges = np.histogram(boot_arr, bins=25)
        bin_centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])
        return {
            "point_estimate": point,
            "standard_error": se,
            "ci_lower": ci_low,
            "ci_upper": ci_high,
            "confidence_level": confidence_level,
            "histogram": {
                "counts": counts.tolist(),
                "bin_centers": bin_centers.tolist(),
            },
        }

    limitations_note = (
        "Standard IID bootstrap treats daily returns as independent and identically distributed. "
        "Real financial returns exhibit volatility clustering (autocorrelated variance). "
        "Moving-block bootstrap resamples contiguous blocks of trading days to partially preserve serial dependency."
    )

    return {
        "method": method,
        "iterations": iterations,
        "seed": seed,
        "sample_size": n,
        "mean_return": summarize_metric(obs_mean, boot_means),
        "annual_volatility": summarize_metric(obs_ann_vol, boot_vols),
        "var_95": summarize_metric(obs_var95, boot_vars),
        "limitations_note": limitations_note,
    }


def run_clt_explorer(
    returns: pd.Series,
    sample_sizes: Optional[List[int]] = None,
    num_trials: int = 1000,
    seed: Optional[int] = 123,
) -> Dict[str, Any]:
    """Central Limit Theorem explorer.

    Draws repeated random samples of sizes n in [5, 10, 30, 50, 100] from the empirical
    daily returns and records the distribution of the sample mean, illustrating asymptotic normality.
    """
    clean_ret = returns.dropna().values.astype(float)
    n_pop = len(clean_ret)
    if n_pop < 30:
        return {"error": "Insufficient sample size (N < 30) for CLT demonstration."}

    if sample_sizes is None:
        sample_sizes = [5, 10, 30, 50]

    rng = np.random.default_rng(seed)

    pop_mean = float(np.mean(clean_ret))
    pop_std = float(np.std(clean_ret, ddof=1))
    pop_skew = float(stats.skew(clean_ret, bias=False))
    pop_kurt = float(stats.kurtosis(clean_ret, fisher=True, bias=False))

    results_by_n = {}
    for n in sample_sizes:
        if n >= n_pop:
            continue
        # Draw num_trials samples of size n
        idx = rng.integers(0, n_pop, size=(num_trials, n))
        sample_means = np.mean(clean_ret[idx], axis=1)

        s_mean = float(np.mean(sample_means))
        s_std = float(np.std(sample_means, ddof=1))
        s_skew = float(stats.skew(sample_means, bias=False))
        s_kurt = float(stats.kurtosis(sample_means, fisher=True, bias=False))

        # Theoretical standard error: sigma / sqrt(n)
        theoretical_se = pop_std / np.sqrt(n)

        counts, bin_edges = np.histogram(sample_means, bins=25)
        bin_centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])

        results_by_n[str(n)] = {
            "n": n,
            "simulated_mean": s_mean,
            "simulated_se": s_std,
            "theoretical_se": float(theoretical_se),
            "skewness": s_skew,
            "excess_kurtosis": s_kurt,
            "histogram": {
                "counts": counts.tolist(),
                "bin_centers": bin_centers.tolist(),
            },
        }

    return {
        "num_trials": num_trials,
        "seed": seed,
        "population": {
            "mean": pop_mean,
            "std": pop_std,
            "skewness": pop_skew,
            "excess_kurtosis": pop_kurt,
        },
        "sample_sizes": results_by_n,
        "clt_summary": (
            "As sample size n increases, the distribution of the sample mean becomes increasingly symmetric "
            "and bell-shaped, with skewness and excess kurtosis converging toward 0, and variance decaying as sigma^2 / n."
        ),
    }
