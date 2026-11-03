"""Chronological walk-forward strategy backtesting engine (strictly zero lookahead)."""

from __future__ import annotations

from typing import Any, Dict, Optional
import numpy as np
import pandas as pd

from config import DEFAULT_TRANSACTION_COST_BPS, TRADING_DAYS_PER_YEAR


def run_walk_forward_backtest(
    stock_prices: pd.Series,
    benchmark_prices: Optional[pd.Series] = None,
    fast_window: int = 20,
    slow_window: int = 50,
    transaction_cost_bps: float = DEFAULT_TRANSACTION_COST_BPS,
    risk_free_rate: float = 0.065,
) -> Dict[str, Any]:
    """Execute a strictly chronological walk-forward backtest of a trend-following rule.

    Lookahead Prevention Rules:
      1. At day t, moving averages and signal are computed ONLY using prices[:t].
      2. The position determined at day t is entered at day t+1.
      3. Slippage / transaction costs are subtracted whenever the position state changes.

    Args:
        stock_prices: Historical adjusted price series.
        benchmark_prices: Optional benchmark index price series.
        fast_window: Lookback for fast moving average (e.g. 20 days).
        slow_window: Lookback for slow moving average (e.g. 50 days).
        transaction_cost_bps: Cost per transaction in basis points (10 bps = 0.0010 = 0.10%).
        risk_free_rate: Annual risk-free rate for Sharpe calculation.

    Returns:
        Dictionary with performance metrics, cumulative return curves, and trade statistics.
    """
    clean_p = stock_prices.dropna().astype(float)
    n = len(clean_p)
    if n < slow_window + 10:
        return {
            "error": f"Insufficient price history for walk-forward backtest ({n} < {slow_window + 10} days needed)."
        }

    cost_pct = transaction_cost_bps / 10000.0

    # Align benchmark if provided
    if benchmark_prices is not None:
        bmk_clean = benchmark_prices.reindex(clean_p.index, method="ffill").bfill()
        bmk_daily_ret = bmk_clean.pct_change().fillna(0.0)
    else:
        bmk_daily_ret = pd.Series(0.0, index=clean_p.index)

    # 1. Compute rolling indicators strictly on trailing data
    fast_sma = clean_p.rolling(window=fast_window, min_periods=fast_window).mean()
    slow_sma = clean_p.rolling(window=slow_window, min_periods=slow_window).mean()

    # Raw signal at close of day t: 1 if fast_sma > slow_sma else 0
    # Note: Shift(1) ensures that the decision at day t governs the exposure from close(t) to close(t+1)
    raw_signal = (fast_sma > slow_sma).astype(int)
    positions = raw_signal.shift(1).fillna(0)  # NO LOOKAHEAD

    # 2. Daily price returns of underlying
    stock_daily_ret = clean_p.pct_change().fillna(0.0)

    # 3. Detect trades (changes in position)
    position_changes = positions.diff().abs().fillna(0)
    transaction_costs = position_changes * cost_pct

    # 4. Strategy daily net returns
    strategy_daily_ret = (positions * stock_daily_ret) - transaction_costs

    # Slice evaluation period starting after slow_window warmup
    eval_slice = positions.index[slow_window:]
    strat_eval_ret = strategy_daily_ret.loc[eval_slice]
    stock_eval_ret = stock_daily_ret.loc[eval_slice]
    bmk_eval_ret = bmk_daily_ret.loc[eval_slice]

    # Cumulative equity paths
    strat_equity = (1.0 + strat_eval_ret).cumprod()
    stock_equity = (1.0 + stock_eval_ret).cumprod()
    bmk_equity = (1.0 + bmk_eval_ret).cumprod()

    # Performance metrics
    days = len(strat_eval_ret)
    years = max(days / TRADING_DAYS_PER_YEAR, 0.05)

    def calc_metrics(ret_series: pd.Series, equity_series: pd.Series) -> dict:
        total_ret = float(equity_series.iloc[-1] - 1.0) if not equity_series.empty else 0.0
        cagr = float((1.0 + total_ret) ** (1.0 / years) - 1.0) if total_ret > -1.0 else -1.0
        ann_vol = float(np.std(ret_series, ddof=1) * np.sqrt(TRADING_DAYS_PER_YEAR))
        excess = cagr - risk_free_rate
        sharpe = float(excess / ann_vol) if ann_vol > 1e-12 else 0.0
        peak = equity_series.cummax()
        dd = (equity_series - peak) / peak
        max_dd = float(dd.min())
        return {
            "total_return": total_ret,
            "cagr": cagr,
            "annual_volatility": ann_vol,
            "sharpe_ratio": sharpe,
            "max_drawdown": max_dd,
        }

    strat_stats = calc_metrics(strat_eval_ret, strat_equity)
    stock_stats = calc_metrics(stock_eval_ret, stock_equity)
    bmk_stats = calc_metrics(bmk_eval_ret, bmk_equity)

    # Trade statistics
    num_trades = int(position_changes.loc[eval_slice].sum())
    active_days = int(positions.loc[eval_slice].sum())
    in_market_pct = float(active_days / days) if days > 0 else 0.0

    # Win rate on active days
    active_returns = strat_eval_ret[positions.loc[eval_slice] == 1]
    win_rate = float((active_returns > 0).mean()) if len(active_returns) > 0 else 0.0

    # Downsampled curve (max 150 points for fast chart transfer)
    step = max(1, len(eval_slice) // 150)
    sample_dates = [d.strftime("%Y-%m-%d") for d in eval_slice[::step]]
    strat_curve = [float(v) for v in strat_equity.iloc[::step]]
    stock_curve = [float(v) for v in stock_equity.iloc[::step]]
    bmk_curve = [float(v) for v in bmk_equity.iloc[::step]]

    return {
        "evaluation_period": f"{eval_slice[0].strftime('%Y-%m-%d')} to {eval_slice[-1].strftime('%Y-%m-%d')} ({days} sessions)",
        "assumptions": {
            "strategy": f"Dual Moving Average Crossover (Fast={fast_window}d, Slow={slow_window}d)",
            "execution_delay": "1-day lag (signal at t, executed at t+1)",
            "transaction_cost_bps": transaction_cost_bps,
            "transaction_cost_pct": cost_pct,
            "risk_free_rate": risk_free_rate,
        },
        "trades": {
            "total_trades": num_trades,
            "days_invested": active_days,
            "time_in_market_pct": in_market_pct,
            "active_day_win_rate": win_rate,
        },
        "strategy_performance": strat_stats,
        "buy_and_hold_stock": stock_stats,
        "benchmark_performance": bmk_stats,
        "equity_curve": {
            "dates": sample_dates,
            "strategy": strat_curve,
            "stock_buy_hold": stock_curve,
            "benchmark": bmk_curve,
        },
        "no_lookahead_guarantee": "Signals generated at time t strictly use historical data up to close(t), and positions take effect at close(t+1).",
    }
