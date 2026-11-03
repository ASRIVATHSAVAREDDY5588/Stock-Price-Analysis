"""Synthetic market data generator for Indian equities and benchmarks.

Generates realistic, fat-tailed historical price series (Student-t innovations,
volatility clustering, and cross-asset correlation) explicitly labeled as synthetic.
Enables full offline lab operation without network access.
"""

from __future__ import annotations

from typing import Dict, Tuple, Optional
import numpy as np
import pandas as pd
from scipy import stats

# Stock profiles with realistic base prices and annual volatilities
SYNTHETIC_PROFILES: Dict[str, dict] = {
    "^NSEI": {"name": "NIFTY 50 Index (Synthetic)", "base_price": 18000.0, "annual_vol": 0.15, "drift": 0.12, "beta": 1.0},
    "^BSESN": {"name": "SENSEX (Synthetic)", "base_price": 60000.0, "annual_vol": 0.15, "drift": 0.12, "beta": 1.0},
    "^NSEBANK": {"name": "NIFTY Bank (Synthetic)", "base_price": 42000.0, "annual_vol": 0.20, "drift": 0.13, "beta": 1.15},
    "RELIANCE.NS": {"name": "Reliance Industries (Synthetic)", "base_price": 2400.0, "annual_vol": 0.21, "drift": 0.14, "beta": 1.10},
    "TCS.NS": {"name": "Tata Consultancy Services (Synthetic)", "base_price": 3400.0, "annual_vol": 0.18, "drift": 0.13, "beta": 0.85},
    "INFY.NS": {"name": "Infosys Ltd (Synthetic)", "base_price": 1450.0, "annual_vol": 0.22, "drift": 0.12, "beta": 0.95},
    "HDFCBANK.NS": {"name": "HDFC Bank Ltd (Synthetic)", "base_price": 1550.0, "annual_vol": 0.19, "drift": 0.11, "beta": 1.05},
    "ICICIBANK.NS": {"name": "ICICI Bank Ltd (Synthetic)", "base_price": 850.0, "annual_vol": 0.22, "drift": 0.16, "beta": 1.12},
    "BHARTIARTL.NS": {"name": "Bharti Airtel Ltd (Synthetic)", "base_price": 800.0, "annual_vol": 0.20, "drift": 0.17, "beta": 0.90},
    "ITC.NS": {"name": "ITC Ltd (Synthetic)", "base_price": 320.0, "annual_vol": 0.16, "drift": 0.11, "beta": 0.65},
    "SBIN.NS": {"name": "State Bank of India (Synthetic)", "base_price": 550.0, "annual_vol": 0.25, "drift": 0.15, "beta": 1.25},
    "LT.NS": {"name": "Larsen & Toubro Ltd (Synthetic)", "base_price": 2100.0, "annual_vol": 0.21, "drift": 0.15, "beta": 1.08},
    "TATAMOTORS.NS": {"name": "Tata Motors Ltd (Synthetic)", "base_price": 480.0, "annual_vol": 0.32, "drift": 0.18, "beta": 1.40},
}


def generate_synthetic_series(
    ticker: str = "RELIANCE.NS",
    benchmark_ticker: str = "^NSEI",
    start_date: str = "2000-01-01",
    end_date: str = "2026-11-02",
    seed: int = 42,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Generate realistic synthetic price data for a target Indian equity and benchmark.

    Uses a Student-t distribution (nu=5) for heavy tails and realistic jump clustering.
    Returns:
        (stock_df, benchmark_df) with DatetimeIndex, Open, High, Low, Close, Adj Close, Volume.
    """
    rng = np.random.default_rng(seed)

    # Business day calendar
    dates = pd.date_range(start=start_date, end=end_date, freq="B")
    n = len(dates)
    if n < 20:
        dates = pd.date_range(end=pd.Timestamp.today(), periods=500, freq="B")
        n = len(dates)

    dt = 1.0 / 252.0

    # Benchmark profile
    b_prof = SYNTHETIC_PROFILES.get(benchmark_ticker, SYNTHETIC_PROFILES["^NSEI"])
    s_prof = SYNTHETIC_PROFILES.get(ticker, SYNTHETIC_PROFILES["RELIANCE.NS"])

    # Correlated fat-tailed innovations using Student-t (nu=5)
    nu = 5
    # Standardize t-variate so variance is 1: var = nu/(nu-2) = 5/3
    t_scale = np.sqrt((nu - 2) / nu)
    z_market = stats.t.rvs(df=nu, size=n, random_state=rng) * t_scale
    z_idiosyncratic = stats.t.rvs(df=nu, size=n, random_state=rng) * t_scale

    beta = s_prof.get("beta", 1.0)
    # Correlation rho approximately beta * (vol_market / vol_stock)
    rho = min(0.9, max(0.4, beta * (b_prof["annual_vol"] / s_prof["annual_vol"])))
    z_stock = rho * z_market + np.sqrt(max(0.01, 1.0 - rho**2)) * z_idiosyncratic

    # Add negative skewness (market down-shocks are sharper than up-shocks)
    shock_prob = 0.02
    market_shocks = rng.binomial(1, shock_prob, size=n) * -rng.exponential(0.018, size=n)
    stock_shocks = rng.binomial(1, shock_prob * 1.2, size=n) * -rng.exponential(0.025, size=n)

    # Daily log returns
    bmk_daily_drift = (b_prof["drift"] - 0.5 * (b_prof["annual_vol"] ** 2)) * dt
    bmk_daily_vol = b_prof["annual_vol"] * np.sqrt(dt)
    bmk_log_ret = bmk_daily_drift + bmk_daily_vol * z_market + market_shocks

    stk_daily_drift = (s_prof["drift"] - 0.5 * (s_prof["annual_vol"] ** 2)) * dt
    stk_daily_vol = s_prof["annual_vol"] * np.sqrt(dt)
    stk_log_ret = stk_daily_drift + stk_daily_vol * z_stock + stock_shocks

    # Generate price paths
    bmk_prices = b_prof["base_price"] * np.exp(np.cumsum(bmk_log_ret))
    stk_prices = s_prof["base_price"] * np.exp(np.cumsum(stk_log_ret))

    def make_df(prices: np.ndarray, base_vol: float) -> pd.DataFrame:
        intraday_noise = np.abs(rng.normal(0, 0.008, size=n))
        highs = prices * (1.0 + intraday_noise)
        lows = prices * (1.0 - np.abs(rng.normal(0, 0.008, size=n)))
        opens = prices * (1.0 + rng.normal(0, 0.004, size=n))
        # Ensure consistency: low <= open, close <= high
        highs = np.maximum(highs, np.maximum(opens, prices))
        lows = np.minimum(lows, np.minimum(opens, prices))
        volume = (rng.lognormal(mean=14.0, sigma=0.5, size=n)).astype(int)

        df = pd.DataFrame(
            {
                "Open": np.round(opens, 2),
                "High": np.round(highs, 2),
                "Low": np.round(lows, 2),
                "Close": np.round(prices, 2),
                "Adj Close": np.round(prices, 2),
                "Volume": volume,
            },
            index=dates,
        )
        df.index.name = "Date"
        return df

    return make_df(stk_prices, s_prof["annual_vol"]), make_df(bmk_prices, b_prof["annual_vol"])
