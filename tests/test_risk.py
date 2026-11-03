"""Tests for risk measures: VaR, Expected Shortfall, Maximum Drawdown, and Benchmark Relative Risk."""

import numpy as np
import pandas as pd
import pytest
from analytics.risk import (
    compute_var_and_es,
    compute_drawdown_series,
    compute_rolling_volatility,
    compute_benchmark_relative_risk,
)


def test_var_and_expected_shortfall_ordering():
    # 100 observations drawn from N(0, 0.02)
    rng = np.random.default_rng(42)
    sample = rng.normal(0.0005, 0.02, size=100)
    returns = pd.Series(sample)

    risk_95 = compute_var_and_es(returns, confidence_level=0.95)
    risk_99 = compute_var_and_es(returns, confidence_level=0.99)

    # 1. By definition, Expected Shortfall >= VaR (average of tail is worse than tail cutoff)
    assert risk_95["expected_shortfall"] >= risk_95["historical_var"]
    assert risk_99["expected_shortfall"] >= risk_99["historical_var"]

    # 2. 99% VaR is greater than 95% VaR (deeper loss)
    assert risk_99["historical_var"] > risk_95["historical_var"]
    assert risk_99["expected_shortfall"] > risk_95["expected_shortfall"]


def test_maximum_drawdown_peak_and_trough():
    # Peak at 100, drops to 70 (-30%), then rises to 90
    dates = pd.date_range("2024-01-01", periods=5, freq="B")
    prices = pd.Series([80.0, 100.0, 70.0, 85.0, 90.0], index=dates)

    dd_series, meta = compute_drawdown_series(prices)

    # Max DD is (70 - 100)/100 = -0.30
    assert pytest.approx(meta["max_drawdown"], rel=1e-5) == -0.30
    assert meta["peak_date"] == dates[1].strftime("%Y-%m-%d")
    assert meta["trough_date"] == dates[2].strftime("%Y-%m-%d")
    assert not meta["is_recovered"]  # Has not surpassed 100 yet


def test_rolling_volatility():
    # Constant volatility series
    rng = np.random.default_rng(101)
    returns = pd.Series(rng.normal(0, 0.01, size=50))
    rvol = compute_rolling_volatility(returns, window=21, trading_days=252)

    # First 20 will have rolling std computed once min_periods is satisfied
    assert not rvol.dropna().empty
    # Daily std ~ 0.01 -> Ann vol ~ 0.01 * sqrt(252) ~ 0.1587 (15.87%)
    mean_ann_vol = rvol.dropna().mean()
    assert 0.10 <= mean_ann_vol <= 0.22


def test_benchmark_relative_risk():
    # Benchmark with 1% std, stock is 1.5x benchmark + small noise -> beta ~ 1.5
    rng = np.random.default_rng(202)
    bmk_ret = pd.Series(rng.normal(0.0005, 0.01, size=200))
    stk_ret = 1.5 * bmk_ret + pd.Series(rng.normal(0, 0.002, size=200))

    rel_risk = compute_benchmark_relative_risk(stk_ret, bmk_ret, risk_free_rate=0.065)

    assert pytest.approx(rel_risk["beta"], abs=0.15) == 1.50
    assert rel_risk["correlation"] > 0.90
    assert "period_dependent_note" in rel_risk
