"""Complete project metrics computation across 2000-2026 YTD and sub-periods.

Computes:
1. Full sample: 2000–2026 YTD (2000-01-03 to 2026-11-02)
2. Period 1: 2000–2009
3. Period 2: 2010–2019
4. Period 3: 2020–2026 YTD (2020-01-01 to 2026-11-02)

Metrics include return moments, tail risk (VaR/ES), drawdown dynamics,
distribution goodness-of-fit (Normal vs Student-t), CAPM relatives,
and zero-lookahead backtest with train/test splits.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.mixture import GaussianMixture

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CLEANED_DIR = PROJECT_ROOT / "data" / "cleaned"
REPORTS_DIR = PROJECT_ROOT / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def compute_metrics_for_slice(
    stk_prices: pd.Series,
    bmk_prices: pd.Series,
    period_label: str,
    rf_annual: float = 0.065,
    tx_cost_bps: float = 10.0,
) -> Dict[str, Any]:
    """Compute complete quantitative metrics for a specific slice."""
    # Common alignment
    common = stk_prices.dropna().index.intersection(bmk_prices.dropna().index).sort_values()
    p = stk_prices.loc[common].astype(float)
    b = bmk_prices.loc[common].astype(float)
    n_days = len(p)

    # Returns
    ret_simple = p.pct_change().dropna()
    bmk_simple = b.pct_change().dropna()
    common_ret = ret_simple.index.intersection(bmk_simple.index)
    r = ret_simple.loc[common_ret]
    rb = bmk_simple.loc[common_ret]
    n_obs = len(r)

    # 1. Return Statistics
    cum_ret = float((p.iloc[-1] / p.iloc[0]) - 1.0)
    years = n_days / 252.0
    cagr = float(((p.iloc[-1] / p.iloc[0]) ** (1.0 / years)) - 1.0) if years > 0 else 0.0

    bmk_cum_ret = float((b.iloc[-1] / b.iloc[0]) - 1.0)
    bmk_cagr = float(((b.iloc[-1] / b.iloc[0]) ** (1.0 / years)) - 1.0) if years > 0 else 0.0

    daily_mean = float(r.mean())
    daily_std = float(r.std(ddof=1))
    ann_vol = float(daily_std * np.sqrt(252.0))

    bmk_daily_std = float(rb.std(ddof=1))
    bmk_ann_vol = float(bmk_daily_std * np.sqrt(252.0))

    skewness = float(stats.skew(r))
    excess_kurtosis = float(stats.kurtosis(r))  # Fisher's definition: Normal = 0
    jb_stat, jb_p = stats.jarque_bera(r)

    # 2. Drawdowns
    running_max = p.cummax()
    drawdown_series = (p - running_max) / running_max
    max_dd = float(drawdown_series.min())
    trough_date = drawdown_series.idxmin()
    peak_date = p.loc[:trough_date].idxmax()

    # Recovery date
    post_trough = p.loc[trough_date:]
    peak_val = p.loc[peak_date]
    recovered_series = post_trough[post_trough >= peak_val]
    recovery_date = recovered_series.index[0] if len(recovered_series) > 0 else None
    recovery_days = (recovery_date - peak_date).days if recovery_date is not None else None

    # Benchmark Drawdown
    bmk_running_max = b.cummax()
    bmk_drawdown = (b - bmk_running_max) / bmk_running_max
    bmk_max_dd = float(bmk_drawdown.min())

    # 3. Value at Risk & Expected Shortfall
    var95_hist = float(-np.percentile(r, 5.0))
    var99_hist = float(-np.percentile(r, 1.0))
    es95 = float(-r[r <= -var95_hist].mean())
    es99 = float(-r[r <= -var99_hist].mean())

    # Parametric Normal VaR
    norm_mu, norm_sigma = stats.norm.fit(r)
    var95_norm = float(-(norm_mu + norm_sigma * stats.norm.ppf(0.05)))
    var99_norm = float(-(norm_mu + norm_sigma * stats.norm.ppf(0.01)))

    # 4. Distribution Fitting & Tests
    # Normal
    norm_loglik = float(np.sum(stats.norm.logpdf(r, loc=norm_mu, scale=norm_sigma)))
    norm_aic = float(2 * 2 - 2 * norm_loglik)
    norm_bic = float(2 * np.log(n_obs) - 2 * norm_loglik)
    ks_norm_stat, ks_norm_p = stats.kstest(r, "norm", args=(norm_mu, norm_sigma))

    # Student-t
    t_df, t_loc, t_scale = stats.t.fit(r)
    t_df, t_loc, t_scale = float(t_df), float(t_loc), float(t_scale)
    t_loglik = float(np.sum(stats.t.logpdf(r, df=t_df, loc=t_loc, scale=t_scale)))
    t_aic = float(2 * 3 - 2 * t_loglik)
    t_bic = float(3 * np.log(n_obs) - 2 * t_loglik)
    ks_t_stat, ks_t_p = stats.kstest(r, "t", args=(t_df, t_loc, t_scale))

    delta_aic = float(t_aic - norm_aic)

    # Gaussian Mixture (2 components)
    try:
        gmm = GaussianMixture(n_components=2, random_state=42)
        gmm.fit(r.values.reshape(-1, 1))
        gmm_loglik = float(gmm.score(r.values.reshape(-1, 1)) * n_obs)
        gmm_k = 2 * 2 + 1  # 2 weights, 2 means, 2 variances (5 params - 1 constraint = 5)
        gmm_aic = float(2 * gmm_k - 2 * gmm_loglik)
        gmm_bic = float(gmm_k * np.log(n_obs) - 2 * gmm_loglik)
        gmm_weights = [float(w) for w in gmm.weights_]
        gmm_vols = [float(np.sqrt(c[0][0]) * np.sqrt(252)) for c in gmm.covariances_]
    except Exception:
        gmm_loglik, gmm_aic, gmm_bic = norm_loglik, norm_aic, norm_bic
        gmm_weights = [0.5, 0.5]
        gmm_vols = [ann_vol, ann_vol]

    # 5. CAPM & Benchmark Comparison
    cov_matrix = np.cov(r, rb)
    var_b = cov_matrix[1, 1]
    beta = float(cov_matrix[0, 1] / var_b) if var_b > 0 else 1.0
    alpha_daily = daily_mean - beta * float(rb.mean())
    alpha_ann = float(alpha_daily * 252.0)
    corr = float(np.corrcoef(r, rb)[0, 1])

    rf_daily = rf_annual / 252.0
    excess_r = r - rf_daily
    sharpe = float((excess_r.mean() / daily_std) * np.sqrt(252.0)) if daily_std > 0 else 0.0

    excess_rb = rb - rf_daily
    bmk_sharpe = float((excess_rb.mean() / bmk_daily_std) * np.sqrt(252.0)) if bmk_daily_std > 0 else 0.0

    tracking_error = float((r - rb).std(ddof=1) * np.sqrt(252.0))
    info_ratio = float((cagr - bmk_cagr) / tracking_error) if tracking_error > 0 else 0.0

    # 6. Walk-Forward Backtest (20d / 50d trend following, 10 bps transaction cost)
    fast_sma = p.rolling(20, min_periods=20).mean()
    slow_sma = p.rolling(50, min_periods=50).mean()
    # Zero-lookahead: position at day t entered at close of t-1
    raw_signal = (fast_sma > slow_sma).astype(int)
    pos = raw_signal.shift(1).fillna(0)

    trades = (pos.diff().abs() > 0).astype(int)
    cost_series = trades * (tx_cost_bps / 10000.0)

    daily_strategy_ret = pos * r - cost_series.loc[r.index]
    strat_cum = (1.0 + daily_strategy_ret).cumprod()
    strat_cum_ret = float(strat_cum.iloc[-1] - 1.0)
    strat_cagr = float((strat_cum.iloc[-1] ** (1.0 / years)) - 1.0) if years > 0 else 0.0
    strat_ann_vol = float(daily_strategy_ret.std(ddof=1) * np.sqrt(252.0))

    trade_count = int(trades.sum())
    trade_ret_list = []
    in_pos = False
    entry_p = 0.0
    for dt, row_pos in pos.items():
        if row_pos == 1 and not in_pos:
            in_pos = True
            entry_p = p.loc[dt]
        elif row_pos == 0 and in_pos:
            in_pos = False
            exit_p = p.loc[dt]
            trade_ret_list.append((exit_p / entry_p) - 1.0)
    win_trades = [tr for tr in trade_ret_list if tr > 0]
    win_rate = float(len(win_trades) / len(trade_ret_list)) if len(trade_ret_list) > 0 else 0.0

    return {
        "period_label": period_label,
        "start_date": common[0].strftime("%Y-%m-%d"),
        "end_date": common[-1].strftime("%Y-%m-%d"),
        "trading_days": n_days,
        "return_observations": n_obs,
        "years": round(years, 2),
        "asset": {
            "initial_price": float(p.iloc[0]),
            "final_price": float(p.iloc[-1]),
            "cumulative_return": cum_ret,
            "cagr": cagr,
            "daily_mean": daily_mean,
            "annualized_volatility": ann_vol,
            "skewness": skewness,
            "excess_kurtosis": excess_kurtosis,
            "jarque_bera": {"stat": float(jb_stat), "p_value": float(jb_p)},
            "max_drawdown": max_dd,
            "mdd_peak_date": peak_date.strftime("%Y-%m-%d"),
            "mdd_trough_date": trough_date.strftime("%Y-%m-%d"),
            "mdd_recovery_date": recovery_date.strftime("%Y-%m-%d") if recovery_date else "Not yet recovered",
            "mdd_recovery_days": recovery_days,
            "var_95_hist": var95_hist,
            "var_99_hist": var99_hist,
            "var_95_norm": var95_norm,
            "var_99_norm": var99_norm,
            "es_95": es95,
            "es_99": es99,
            "sharpe_ratio": sharpe,
        },
        "benchmark": {
            "initial_level": float(b.iloc[0]),
            "final_level": float(b.iloc[-1]),
            "cumulative_return": bmk_cum_ret,
            "cagr": bmk_cagr,
            "annualized_volatility": bmk_ann_vol,
            "max_drawdown": bmk_max_dd,
            "sharpe_ratio": bmk_sharpe,
        },
        "capm_relative": {
            "beta": beta,
            "alpha_ann": alpha_ann,
            "correlation": corr,
            "tracking_error": tracking_error,
            "information_ratio": info_ratio,
        },
        "distribution_fit": {
            "normal": {
                "mu": float(norm_mu),
                "sigma": float(norm_sigma),
                "loglik": norm_loglik,
                "aic": norm_aic,
                "bic": norm_bic,
                "ks_stat": float(ks_norm_stat),
                "ks_p": float(ks_norm_p),
            },
            "student_t": {
                "df": t_df,
                "loc": t_loc,
                "scale": t_scale,
                "loglik": t_loglik,
                "aic": t_aic,
                "bic": t_bic,
                "ks_stat": float(ks_t_stat),
                "ks_p": float(ks_t_p),
            },
            "delta_aic_t_vs_norm": delta_aic,
            "gaussian_mixture": {
                "loglik": gmm_loglik,
                "aic": gmm_aic,
                "bic": gmm_bic,
                "weights": gmm_weights,
                "annual_vols": gmm_vols,
            },
        },
        "backtest_strategy": {
            "fast_sma": 20,
            "slow_sma": 50,
            "transaction_cost_bps": tx_cost_bps,
            "strat_cum_return": strat_cum_ret,
            "strat_cagr": strat_cagr,
            "strat_annual_vol": strat_ann_vol,
            "trade_count": trade_count,
            "win_rate": win_rate,
        },
    }


def run_all_computations() -> Dict[str, Any]:
    """Run computations across full 2000-2026 YTD period and all 3 decades."""
    # Load cleaned data
    rel_path = CLEANED_DIR / "reliance_cleaned_2000_2026.csv"
    nifty_path = CLEANED_DIR / "nifty50_cleaned_2000_2026.csv"

    rel_df = pd.read_csv(rel_path, parse_dates=["Date"], index_col="Date")
    nifty_df = pd.read_csv(nifty_path, parse_dates=["Date"], index_col="Date")

    stk_prices = rel_df["Adj Close"]
    bmk_prices = nifty_df["Close"]

    slices = {
        "full_2000_2026_ytd": (stk_prices, bmk_prices, "2000–2026 YTD"),
        "period_2000_2009": (stk_prices.loc["2000-01-01":"2009-12-31"], bmk_prices.loc["2000-01-01":"2009-12-31"], "2000–2009"),
        "period_2010_2019": (stk_prices.loc["2010-01-01":"2019-12-31"], bmk_prices.loc["2010-01-01":"2019-12-31"], "2010–2019"),
        "period_2020_2026_ytd": (stk_prices.loc["2020-01-01":], bmk_prices.loc["2020-01-01":], "2020–2026 YTD"),
    }

    # Train / Test split evaluation (Train: 2000-2015, Test: 2016-2026 YTD)
    train_stk = stk_prices.loc[:"2015-12-31"]
    train_bmk = bmk_prices.loc[:"2015-12-31"]
    test_stk = stk_prices.loc["2016-01-01":]
    test_bmk = bmk_prices.loc["2016-01-01":]

    slices["train_2000_2015"] = (train_stk, train_bmk, "Train (2000–2015)")
    slices["test_2016_2026_ytd"] = (test_stk, test_bmk, "Out-of-Sample Test (2016–2026 YTD)")

    results: Dict[str, Any] = {}
    for key, (s, b, label) in slices.items():
        print(f"Computing metrics for {label} ({len(s)} days)...")
        results[key] = compute_metrics_for_slice(s, b, label)

    out_file = REPORTS_DIR / "project_computed_metrics.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"\nAll computations finished successfully! Saved to {out_file}\n")
    return results


if __name__ == "__main__":
    run_all_computations()
