"""Tests for walk-forward backtesting and lookahead bias prevention."""

import numpy as np
import pandas as pd
import pytest
from analytics.backtest import run_walk_forward_backtest


def test_no_lookahead_rule():
    """Verify that changing future prices has ZERO effect on signals or equity prior to that point."""
    dates = pd.date_range("2023-01-01", periods=120, freq="B")
    base_prices = 100.0 * np.exp(np.cumsum(np.random.default_rng(42).normal(0.001, 0.015, size=120)))
    series_original = pd.Series(base_prices, index=dates)

    # Run original backtest
    res_orig = run_walk_forward_backtest(series_original, fast_window=20, slow_window=50)

    # Create modified series where prices after day 80 crash violently
    series_future_crash = series_original.copy()
    series_future_crash.iloc[80:] = series_future_crash.iloc[80:] * 0.10

    # Run backtest with modified future
    res_crash = run_walk_forward_backtest(series_future_crash, fast_window=20, slow_window=50)

    # For all dates up to day 80, the equity curves must be IDENTICAL
    eval_dates = res_orig["equity_curve"]["dates"]
    for idx, d_str in enumerate(eval_dates):
        d = pd.to_datetime(d_str)
        if d < dates[80]:
            assert pytest.approx(res_orig["equity_curve"]["strategy"][idx], rel=1e-5) == res_crash["equity_curve"]["strategy"][idx]


def test_transaction_cost_deduction():
    """Verify that higher transaction costs reduce the strategy total return."""
    dates = pd.date_range("2023-01-01", periods=150, freq="B")
    # Oscillating series to trigger multiple trades
    t = np.linspace(0, 10, 150)
    prices = pd.Series(100.0 + 10.0 * np.sin(t) + 0.1 * t, index=dates)

    res_low_cost = run_walk_forward_backtest(prices, fast_window=10, slow_window=25, transaction_cost_bps=0.0)
    res_high_cost = run_walk_forward_backtest(prices, fast_window=10, slow_window=25, transaction_cost_bps=50.0)

    # If trades occurred, high cost return must be strictly lower than zero cost return
    if res_low_cost["trades"]["total_trades"] > 0:
        assert res_high_cost["strategy_performance"]["total_return"] < res_low_cost["strategy_performance"]["total_return"]
