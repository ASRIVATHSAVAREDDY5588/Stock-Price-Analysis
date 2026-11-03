"""Return calculations, formulas, and cumulative series transformations."""

from __future__ import annotations

from typing import Dict, Tuple
import numpy as np
import pandas as pd


RETURN_FORMULAS = {
    "simple": {
        "name": "Simple (Arithmetic) Return",
        "latex": r"R_t = \frac{P_t}{P_{t-1}} - 1",
        "description": "Percentage change in asset price from period t-1 to period t. Additive across portfolio components at a single point in time.",
    },
    "log": {
        "name": "Logarithmic (Continuously Compounded) Return",
        "latex": r"r_t = \ln\left(\frac{P_t}{P_{t-1}}\right) = \ln(P_t) - \ln(P_{t-1})",
        "description": "Logarithmic change in price. Additive through time (the cumulative log return over T periods is the sum of daily log returns).",
    },
    "cumulative_simple": {
        "name": "Cumulative Simple Return",
        "latex": r"R_{0, T} = \prod_{t=1}^T (1 + R_t) - 1",
        "description": "Compound growth of an initial investment over the entire period.",
    },
}


def compute_returns(
    prices: pd.Series,
    return_type: str = "simple",
) -> Tuple[pd.Series, pd.Series]:
    """Calculate daily returns and cumulative return series from adjusted closing prices.

    Args:
        prices: Series of prices indexed by Date.
        return_type: 'simple' or 'log'.

    Returns:
        (daily_returns_series, cumulative_returns_series)
    """
    clean_prices = prices.dropna().astype(float)
    if len(clean_prices) < 2:
        empty = pd.Series(dtype=float)
        return empty, empty

    # Filter non-positive prices to avoid zero division or log domain errors
    clean_prices = clean_prices[clean_prices > 0]

    if return_type == "log":
        # r_t = ln(P_t / P_{t-1})
        daily_returns = np.log(clean_prices / clean_prices.shift(1)).dropna()
        # Cumulative simple return from log returns: exp(sum(r_t)) - 1
        cumulative_returns = np.exp(daily_returns.cumsum()) - 1.0
    else:
        # Simple return: R_t = (P_t / P_{t-1}) - 1
        daily_returns = (clean_prices / clean_prices.shift(1) - 1.0).dropna()
        # Cumulative return: prod(1 + R_t) - 1
        cumulative_returns = (1.0 + daily_returns).cumprod() - 1.0

    daily_returns.name = f"{prices.name or 'Price'}_daily_return"
    cumulative_returns.name = f"{prices.name or 'Price'}_cumulative_return"

    return daily_returns, cumulative_returns


def compute_price_index(prices: pd.Series, base: float = 100.0) -> pd.Series:
    """Normalize a price series to start at base value (e.g. 100) for visual comparison."""
    clean = prices.dropna().astype(float)
    if clean.empty or clean.iloc[0] <= 0:
        return clean
    indexed = (clean / clean.iloc[0]) * base
    indexed.name = f"{prices.name or 'Asset'}_indexed"
    return indexed
