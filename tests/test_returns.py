"""Tests for simple, log, and cumulative return calculations."""

import numpy as np
import pandas as pd
import pytest
from analytics.returns import compute_returns, compute_price_index


def test_simple_and_log_returns_basic():
    # Price path: 100 -> 110 -> 99
    dates = pd.date_range("2024-01-01", periods=3, freq="B")
    prices = pd.Series([100.0, 110.0, 99.0], index=dates)

    ret_simple, cum_simple = compute_returns(prices, "simple")
    ret_log, cum_log = compute_returns(prices, "log")

    # Day 1: 110/100 - 1 = +10.0%
    # Day 2: 99/110 - 1 = -10.0%
    assert len(ret_simple) == 2
    assert pytest.approx(ret_simple.iloc[0], rel=1e-5) == 0.10
    assert pytest.approx(ret_simple.iloc[1], rel=1e-5) == -0.10

    # Cumulative return: (1 + 0.10)*(1 - 0.10) - 1 = 0.99 - 1 = -1.0%
    assert pytest.approx(cum_simple.iloc[-1], rel=1e-5) == -0.01

    # Log returns: ln(1.10) = 0.095310, ln(0.90) = -0.105360
    assert pytest.approx(ret_log.iloc[0], rel=1e-4) == np.log(1.10)
    assert pytest.approx(ret_log.iloc[1], rel=1e-4) == np.log(0.90)

    # Convert log cum back to simple: exp(sum(log)) - 1 == -0.01
    assert pytest.approx(cum_log.iloc[-1], rel=1e-5) == -0.01


def test_constant_prices():
    dates = pd.date_range("2024-01-01", periods=10, freq="B")
    prices = pd.Series([2500.0] * 10, index=dates)

    ret_simple, cum_simple = compute_returns(prices, "simple")
    assert len(ret_simple) == 9
    assert np.allclose(ret_simple.values, 0.0)
    assert np.allclose(cum_simple.values, 0.0)


def test_price_index_normalization():
    dates = pd.date_range("2024-01-01", periods=3, freq="B")
    prices = pd.Series([2000.0, 2200.0, 2400.0], index=dates)

    indexed = compute_price_index(prices, base=100.0)
    assert pytest.approx(indexed.iloc[0]) == 100.0
    assert pytest.approx(indexed.iloc[1]) == 110.0
    assert pytest.approx(indexed.iloc[2]) == 120.0


def test_short_history_edge_case():
    dates = pd.date_range("2024-01-01", periods=1, freq="B")
    prices = pd.Series([100.0], index=dates)

    ret_simple, cum_simple = compute_returns(prices, "simple")
    assert ret_simple.empty
    assert cum_simple.empty
