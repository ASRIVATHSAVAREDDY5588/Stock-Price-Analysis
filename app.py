from __future__ import annotations

import os
import re
import calendar
from datetime import date, timedelta

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
import yfinance as yf
from streamlit.errors import StreamlitSecretNotFoundError


st.set_page_config(page_title="India Stock Lab", page_icon="📈", layout="wide")

UNIVERSE = {
    "Energy & diversified": {
        "RELIANCE.NS": "Reliance Industries",
        "ONGC.NS": "Oil and Natural Gas Corporation",
        "NTPC.NS": "NTPC",
        "ADANIENT.NS": "Adani Enterprises",
        "COALINDIA.NS": "Coal India",
    },
    "Banks & financial services": {
        "HDFCBANK.NS": "HDFC Bank",
        "ICICIBANK.NS": "ICICI Bank",
        "SBIN.NS": "State Bank of India",
        "AXISBANK.NS": "Axis Bank",
        "KOTAKBANK.NS": "Kotak Mahindra Bank",
        "BAJFINANCE.NS": "Bajaj Finance",
        "BAJAJFINSV.NS": "Bajaj Finserv",
    },
    "Information technology": {
        "TCS.NS": "Tata Consultancy Services",
        "INFY.NS": "Infosys",
        "WIPRO.NS": "Wipro",
        "HCLTECH.NS": "HCL Technologies",
    },
    "Automobiles": {
        "MARUTI.NS": "Maruti Suzuki",
        "TATAMOTORS.NS": "Tata Motors",
        "M&M.NS": "Mahindra & Mahindra",
    },
    "Consumer & retail": {
        "ITC.NS": "ITC",
        "HINDUNILVR.NS": "Hindustan Unilever",
        "ASIANPAINT.NS": "Asian Paints",
        "TITAN.NS": "Titan Company",
    },
    "Pharmaceuticals": {
        "SUNPHARMA.NS": "Sun Pharmaceutical",
        "DRREDDY.NS": "Dr. Reddy's Laboratories",
        "CIPLA.NS": "Cipla",
    },
    "Infrastructure & telecom": {
        "LT.NS": "Larsen & Toubro",
        "BHARTIARTL.NS": "Bharti Airtel",
    },
}
STOCKS = {symbol: name for group in UNIVERSE.values() for symbol, name in group.items()}
STOCK_SECTORS = {symbol: sector for sector, group in UNIVERSE.items() for symbol in group}
BENCHMARK = "^NSEI"
BENCHMARK_NAME = "NIFTY 50"
DATA_SOURCE = "Yahoo Finance via yfinance (unofficial wrapper)"
MIN_DATE = date(2000, 1, 1)
HORIZONS = {"Short term (3 months)": 63, "Medium term (1 year)": 252, "Long term (3 years)": 756}


def empty_prices(symbols: tuple[str, ...]) -> pd.DataFrame:
    return pd.DataFrame(columns=list(symbols), dtype=float)


def extract_closes(raw: pd.DataFrame, symbols: tuple[str, ...]) -> pd.DataFrame:
    if raw.empty:
        return empty_prices(symbols)

    if isinstance(raw.columns, pd.MultiIndex):
        close = None
        for level in range(raw.columns.nlevels):
            labels = raw.columns.get_level_values(level)
            if "Close" in labels:
                close = raw.xs("Close", axis=1, level=level)
                break
        if close is None:
            return empty_prices(symbols)
    elif "Close" in raw.columns:
        close = raw["Close"]
    else:
        return empty_prices(symbols)

    if isinstance(close, pd.Series):
        name = close.name if close.name in symbols else symbols[0]
        close = close.to_frame(name=name)
    if isinstance(close.columns, pd.MultiIndex):
        close.columns = [str(column[-1]) for column in close.columns]
    close.columns = [str(column) for column in close.columns]
    close = close.loc[:, ~pd.Index(close.columns).duplicated()]
    close = close.reindex(columns=list(symbols))
    close.index = pd.to_datetime(close.index)
    if close.index.tz is not None:
        close.index = close.index.tz_localize(None)
    close = close[~close.index.duplicated(keep="last")].sort_index()
    return close.apply(pd.to_numeric, errors="coerce").dropna(how="all")


@st.cache_data(ttl=1800, show_spinner=False)
def _download_prices(symbols: tuple[str, ...], start: date, end: date) -> pd.DataFrame:
    """Download adjusted daily closes, preserving provider gaps rather than filling them."""
    if not symbols:
        raise ValueError("Select at least one ticker.")
    raw = yf.download(
        tickers=list(symbols),
        start=start,
        end=end + timedelta(days=1),
        interval="1d",
        auto_adjust=True,
        progress=False,
        group_by="column",
        threads=False,
    )
    if raw.empty:
        raise ValueError("Yahoo Finance returned no daily price rows for this selection.")

    closes = extract_closes(raw, symbols)
    if closes.empty:
        raise ValueError("Yahoo Finance returned no usable daily closing prices for this date range.")
    return closes


def load_prices(symbols: tuple[str, ...], start: date, end: date) -> tuple[pd.DataFrame, str | None]:
    try:
        return _download_prices(symbols, start, end), None
    except Exception as exc:
        message = str(exc).strip().replace("\n", " ")
        if len(message) > 220:
            message = message[:217] + "..."
        rate_limit_note = " This may be a temporary provider rate limit; wait and retry." if any(
            word in message.lower() for word in ("rate", "too many", "429")
        ) else ""
        return empty_prices(symbols), f"Yahoo Finance could not return daily data: {message}.{rate_limit_note}"


def daily_returns(prices: pd.Series, max_gap_days: int = 7) -> pd.Series:
    """Return simple daily changes; skip gaps longer than a normal holiday weekend."""
    clean = prices.dropna().sort_index()
    if len(clean) < 2:
        return pd.Series(dtype=float)
    changes = clean.pct_change(fill_method=None)
    elapsed_days = clean.index.to_series().diff().dt.days
    return changes.where(elapsed_days <= max_gap_days).replace([np.inf, -np.inf], np.nan).dropna()


def daily_log_returns(prices: pd.Series, max_gap_days: int = 7) -> pd.Series:
    simple = daily_returns(prices, max_gap_days=max_gap_days)
    return np.log1p(simple).replace([np.inf, -np.inf], np.nan).dropna()


def drawdown_series(prices: pd.Series) -> pd.Series:
    clean = prices.dropna()
    if clean.empty:
        return pd.Series(dtype=float)
    return clean / clean.cummax() - 1


def max_drawdown(prices: pd.Series) -> float:
    values = drawdown_series(prices)
    return float(values.min()) if not values.empty else float("nan")


def safe_ratio(numerator: float, denominator: float) -> float:
    if pd.isna(numerator) or pd.isna(denominator) or np.isclose(denominator, 0):
        return float("nan")
    return float(numerator / denominator)


def calculate_metrics(prices: pd.Series, benchmark: pd.Series | None, annual_risk_free: float) -> dict[str, float | int]:
    clean = prices.dropna().sort_index()
    if len(clean) < 2:
        return {}

    simple = daily_returns(clean)
    if simple.empty:
        return {}
    daily_rf = annual_risk_free / 252
    excess = simple - daily_rf
    volatility = float(simple.std(ddof=1) * np.sqrt(252)) if len(simple) > 1 else float("nan")
    downside = np.minimum(excess.to_numpy(dtype=float), 0.0)
    downside_deviation = float(np.sqrt(np.mean(np.square(downside))) * np.sqrt(252))
    annual_excess_return = float(excess.mean() * 252)
    total_return = float(clean.iloc[-1] / clean.iloc[0] - 1)
    years = (clean.index[-1] - clean.index[0]).days / 365.25
    cagr = float((clean.iloc[-1] / clean.iloc[0]) ** (1 / years) - 1) if years > 0 else float("nan")
    var_cutoff = float(simple.quantile(0.05))
    tail = simple[simple <= var_cutoff]

    beta = float("nan")
    if benchmark is not None and not benchmark.dropna().empty:
        benchmark_returns = daily_returns(benchmark)
        aligned = pd.concat([simple.rename("stock"), benchmark_returns.rename("market")], axis=1).dropna()
        if len(aligned) > 1 and not np.isclose(aligned["market"].var(ddof=1), 0):
            beta = float(aligned["stock"].cov(aligned["market"]) / aligned["market"].var(ddof=1))

    return {
        "Total return": total_return,
        "CAGR": cagr,
        "Annualized volatility": volatility,
        "Sharpe ratio": safe_ratio(annual_excess_return, volatility),
        "Sortino ratio": safe_ratio(annual_excess_return, downside_deviation),
        "Beta": beta,
        "Maximum drawdown": max_drawdown(clean),
        "95% historical VaR": max(0.0, -var_cutoff),
        "95% historical CVaR": max(0.0, -float(tail.mean())) if not tail.empty else float("nan"),
        "Best day": float(simple.max()),
        "Worst day": float(simple.min()),
        "Positive days": float((simple > 0).mean()),
        "Mean daily log return": float(daily_log_returns(clean).mean()),
        "Median daily log return": float(daily_log_returns(clean).median()),
        "Log-return skewness": float(daily_log_returns(clean).skew()),
        "Log-return kurtosis": float(daily_log_returns(clean).kurt()),
        "Observation count": int(len(simple)),
    }


def fmt_pct(value: float) -> str:
    return "—" if pd.isna(value) else f"{value:.2%}"


def fmt_num(value: float) -> str:
    return "—" if pd.isna(value) else f"{value:.2f}"


def get_openai_key() -> str | None:
    key = os.getenv("OPENAI_API_KEY")
    if key:
        return key
    try:
        return st.secrets.get("OPENAI_API_KEY")
    except StreamlitSecretNotFoundError:
        return None


def local_explanation(name: str, metrics: dict[str, float | int], rank: int | None = None) -> str:
    prefix = f"{name} ranks #{rank}. " if rank is not None else f"For {name}, "
    return (
        prefix
        + f"over the observed period it returned {fmt_pct(metrics.get('Total return', float('nan')))} "
        + f"({fmt_pct(metrics.get('CAGR', float('nan')))} CAGR), with "
        + f"{fmt_pct(metrics.get('Annualized volatility', float('nan')))} annualized volatility "
        + f"and a {fmt_pct(metrics.get('Maximum drawdown', float('nan')))} maximum drawdown. "
        + f"The historical Sharpe and Sortino ratios were {fmt_num(metrics.get('Sharpe ratio', float('nan')))} "
        + f"and {fmt_num(metrics.get('Sortino ratio', float('nan')))}. These describe the selected "
        + "historical sample only and do not predict future performance."
    )


def explain_with_openai(name: str, metrics: dict[str, float | int], rank: int | None = None) -> str:
    from openai import OpenAI

    supplied_metrics = {
        key: value for key, value in metrics.items()
        if key != "Observation count" and isinstance(value, (int, float)) and np.isfinite(value)
    }
    client = OpenAI(api_key=get_openai_key())
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "Write a concise explanation using only the supplied name, rank, and metric values. "
                    "Clearly separate historical facts from interpretation. Do not add news, current prices, "
                    "external facts, forecasts, personalized advice, or buy/sell recommendations. "
                    "State that historical results do not predict future performance."
                ),
            },
            {
                "role": "user",
                "content": f"Name: {name}. Rank: {rank}. Supplied historical metrics: {supplied_metrics}",
            },
        ],
        max_completion_tokens=220,
    )
    content = response.choices[0].message.content
    if not content:
        raise ValueError("The AI service returned an empty explanation.")
    return content


def build_screener(prices: pd.DataFrame, horizon_days: int, annual_risk_free: float) -> pd.DataFrame:
    benchmark_series = prices[BENCHMARK] if BENCHMARK in prices else None
    rows: list[dict[str, float | str]] = []
    for symbol in prices.columns:
        if symbol == BENCHMARK:
            continue
        series = prices[symbol].dropna().tail(horizon_days)
        metrics = calculate_metrics(series, benchmark_series, annual_risk_free)
        if not metrics or metrics["Observation count"] < 30:
            continue
        rows.append(
            {
                "Symbol": symbol,
                "Company": STOCKS.get(symbol, symbol),
                "Return": float(metrics["Total return"]),
                "Sharpe": float(metrics["Sharpe ratio"]),
                "Volatility": float(metrics["Annualized volatility"]),
                "Max drawdown": float(metrics["Maximum drawdown"]),
            }
        )
    if not rows:
        return pd.DataFrame()

    ranking = pd.DataFrame(rows)

    def relative_score(series: pd.Series, higher_is_better: bool) -> pd.Series:
        series = series.replace([np.inf, -np.inf], np.nan)
        lowest, highest = series.min(), series.max()
        if pd.isna(lowest) or pd.isna(highest):
            return pd.Series(0.5, index=series.index)
        if np.isclose(lowest, highest):
            return pd.Series(0.5, index=series.index)
        scaled = (series - lowest) / (highest - lowest)
        return scaled.fillna(0.5) if higher_is_better else (1 - scaled).fillna(0.5)

    ranking["Score"] = 100 * (
        0.40 * relative_score(ranking["Return"], True)
        + 0.30 * relative_score(ranking["Sharpe"], True)
        + 0.20 * relative_score(ranking["Volatility"], False)
        + 0.10 * relative_score(ranking["Max drawdown"], True)
    )
    ranking = ranking.sort_values(["Score", "Symbol"], ascending=[False, True]).reset_index(drop=True)
    ranking.insert(0, "Rank", np.arange(1, len(ranking) + 1))
    return ranking


def normalize_ticker(value: str) -> str | None:
    ticker = value.strip().upper()
    if not ticker or not re.fullmatch(r"[A-Z0-9&.-]+", ticker):
        return None
    if ticker.startswith("^"):
        return None
    return ticker if ticker.endswith(".NS") else f"{ticker}.NS"


def years_ago(day: date, years: int) -> date:
    year = day.year - years
    return date(year, day.month, min(day.day, calendar.monthrange(year, day.month)[1]))


def display_name(symbol: str) -> str:
    if symbol == BENCHMARK:
        return BENCHMARK_NAME
    return STOCKS.get(symbol, f"Custom NSE symbol {symbol.removesuffix('.NS')}")


def add_chart_note():
    st.caption(
        "Charts use adjusted daily closing prices. Provider gaps remain missing; returns across gaps "
        "longer than seven calendar days are excluded from daily risk calculations."
    )


st.title("India Stock Lab")
st.caption(
    "Historical NSE market analysis for education and research. "
    f"Data source: {DATA_SOURCE}. Data is not live; coverage and terms are controlled by Yahoo Finance."
)

with st.sidebar:
    st.header("Analysis")
    today = date.today()
    st.caption("Daily prices · dates from 2000-01-01 through today")
    range_choice = st.selectbox(
        "Date range",
        ["Maximum available history", "10 years", "5 years", "3 years", "1 year", "Custom range"],
        key="date_range_mode",
        help="Maximum history requests prices from 2000-01-01; each stock uses only dates the provider actually has.",
    )
    if range_choice == "Custom range":
        if "custom_from" not in st.session_state:
            st.session_state["custom_from"] = MIN_DATE
        if "custom_to" not in st.session_state:
            st.session_state["custom_to"] = today
        from_date = st.date_input(
            "From",
            min_value=MIN_DATE,
            max_value=today,
            key="custom_from",
        )
        to_date = st.date_input(
            "To",
            min_value=from_date,
            max_value=today,
            key="custom_to",
        )
    else:
        years = {
            "Maximum available history": None,
            "10 years": 10,
            "5 years": 5,
            "3 years": 3,
            "1 year": 1,
        }[range_choice]
        from_date = MIN_DATE if years is None else max(MIN_DATE, years_ago(today, years))
        to_date = today
        st.caption(f"From **{from_date:%d %b %Y}** to **{to_date:%d %b %Y}**")

    custom_ticker = st.text_input(
        "Add custom NSE ticker",
        placeholder="e.g. ZOMATO or ZOMATO.NS",
        help="Enter an NSE Yahoo Finance ticker. The .NS suffix is added if omitted.",
    )
    if st.button("Add ticker", key="add_ticker"):
        normalized = normalize_ticker(custom_ticker)
        if normalized is None:
            st.error("Enter a valid ticker using letters, numbers, dots, hyphens, or ampersands.")
        else:
            customs = st.session_state.get("custom_tickers", [])
            if normalized not in customs and normalized not in STOCKS:
                customs.append(normalized)
                st.session_state["custom_tickers"] = customs
            selected = st.session_state.get(
                "stock_selection", ["RELIANCE.NS", "TCS.NS", "INFY.NS"]
            )
            st.session_state["stock_selection"] = list(dict.fromkeys([*selected, normalized]))
            st.success(f"Added {normalized}.")

    symbols_available = [*STOCKS, *st.session_state.get("custom_tickers", [])]
    symbols_available = list(dict.fromkeys(symbols_available))
    default_symbols = ["RELIANCE.NS", "TCS.NS", "INFY.NS"]
    default_symbols = [symbol for symbol in default_symbols if symbol in symbols_available]
    if "stock_selection" not in st.session_state:
        st.session_state["stock_selection"] = default_symbols
    selected_stocks = st.multiselect(
        "Stocks to compare",
        options=symbols_available,
        key="stock_selection",
        format_func=display_name,
        help="Choose company names from the curated NSE list or add a custom symbol above.",
    )
    if selected_stocks:
        focus_stock = st.selectbox(
            "Focus company for individual charts",
            options=selected_stocks,
            key="focus_stock",
            format_func=display_name,
        )
    else:
        focus_stock = None
    include_benchmark = st.checkbox("Include NIFTY 50 benchmark", value=True)
    annual_risk_free = st.slider(
        "Annual risk-free rate",
        min_value=0.0,
        max_value=15.0,
        value=4.5,
        step=0.25,
        format="%.2f%%",
        help="Assumed annual rate used for Sharpe and Sortino calculations; not a live government yield.",
    ) / 100
    horizon_label = st.selectbox("Screener horizon", options=list(HORIZONS))

start_date, end_date = from_date, to_date
if start_date > end_date:
    st.error("The To date must be on or after the From date. Adjust the custom date range to continue.")
    st.stop()

requested_symbols = [*selected_stocks, BENCHMARK]

with st.spinner("Loading adjusted daily prices from Yahoo Finance..."):
    prices, data_error = load_prices(tuple(dict.fromkeys(requested_symbols)), start_date, end_date)

if data_error:
    st.warning(data_error)
if include_benchmark and (BENCHMARK not in prices or prices[BENCHMARK].dropna().empty):
    st.warning("NIFTY 50 benchmark data is unavailable for this date range.")
if not selected_stocks:
    st.info("Select at least one NSE stock in the sidebar to explore the charts and statistics.")
    st.stop()

if prices.empty or not any(prices.get(symbol, pd.Series(dtype=float)).notna().any() for symbol in selected_stocks):
    st.error("No usable prices were returned for the selected stocks and date range.")
    st.stop()

coverage_rows = []
for symbol in requested_symbols:
    if symbol in prices and prices[symbol].notna().any():
        observed = prices[symbol].dropna()
        first_seen, last_seen = observed.index[0].date(), observed.index[-1].date()
        note = "Starts after 2000-01-01" if first_seen > MIN_DATE else ""
        if first_seen > start_date:
            note = (note + "; " if note else "") + "Provider has no earlier observations in this selection"
        coverage_rows.append(
            {
                "Ticker": symbol,
                "Company": BENCHMARK_NAME if symbol == BENCHMARK else STOCKS.get(symbol, symbol),
                "First available": first_seen.isoformat(),
                "Last available": last_seen.isoformat(),
                "Coverage note": note,
            }
        )
    else:
        coverage_rows.append(
            {
                "Ticker": symbol,
                "Company": BENCHMARK_NAME if symbol == BENCHMARK else STOCKS.get(symbol, symbol),
                "First available": "—",
                "Last available": "—",
                "Coverage note": "No usable data returned",
            }
        )

latest_available = max(
    (pd.Timestamp(row["Last available"]) for row in coverage_rows if row["Last available"] != "—"),
    default=None,
)
latest_text = latest_available.date().isoformat() if latest_available is not None else "not available"
st.caption(f"Latest available observation in this selection: **{latest_text}** · Source: {DATA_SOURCE}")

for symbol in selected_stocks:
    if symbol not in prices or prices[symbol].dropna().empty:
        st.warning(f"No usable historical data was returned for {symbol}.")

analysis_prices = prices.copy()
benchmark_prices = analysis_prices[BENCHMARK] if BENCHMARK in analysis_prices else None
metrics_by_symbol = {
    symbol: calculate_metrics(
        analysis_prices[symbol],
        benchmark_prices if symbol != BENCHMARK else None,
        annual_risk_free,
    )
    for symbol in selected_stocks
    if symbol in analysis_prices and analysis_prices[symbol].notna().any()
}

if focus_stock and focus_stock in analysis_prices and analysis_prices[focus_stock].notna().any():
    observed_focus = analysis_prices[focus_stock].dropna()
    st.caption(
        f"Requested date range: **{start_date:%d %b %Y} – {end_date:%d %b %Y}** · "
        f"{display_name(focus_stock)} available observations: **{observed_focus.index[0]:%d %b %Y} – "
        f"{observed_focus.index[-1]:%d %b %Y}** · Latest available date in selection: **{latest_text}**"
    )
    if observed_focus.index[0].date() > start_date:
        st.info(
            f"{display_name(focus_stock)} has no returned price history before "
            f"{observed_focus.index[0]:%d %b %Y} in this range. The selected dates remain unchanged."
        )

with st.expander("Details: ticker symbols and Yahoo Finance format"):
    st.caption("For example, RELIANCE.NS is the Yahoo Finance NSE symbol for Reliance Industries.")
    st.dataframe(
        pd.DataFrame(
            [
                {
                    "Company": display_name(symbol),
                    "Ticker symbol": symbol,
                    "Sector": STOCK_SECTORS.get(symbol, "Custom NSE symbol"),
                }
                for symbol in [*selected_stocks, *([BENCHMARK] if include_benchmark else [])]
            ]
        ),
        hide_index=True,
        width="stretch",
    )

overview_tab, returns_tab, normalized_tab, volatility_tab, drawdown_tab, sharpe_tab, correlation_tab, more_tab, coverage_tab, screener_tab = st.tabs(
    [
        "Overview",
        "Log Returns Dist",
        "Normalized Price",
        "Rolling Volatility",
        "Drawdown",
        "Sharpe Ratio",
        "Correlation",
        "More analysis",
        "Data coverage",
        "Research screen",
    ]
)

focus_name = display_name(focus_stock) if focus_stock else "Selected company"
focus_metrics = metrics_by_symbol.get(focus_stock, {}) if focus_stock else {}
focus_prices = analysis_prices[focus_stock].dropna() if focus_stock in analysis_prices else pd.Series(dtype=float)
focus_returns = daily_returns(focus_prices)
focus_log_returns = daily_log_returns(focus_prices)

with overview_tab:
    st.subheader("Historical snapshot")
    if focus_metrics:
        st.caption(f"{focus_name} · based on available daily adjusted prices in the selected range")
        primary = st.columns(4)
        primary[0].metric("Total return", fmt_pct(focus_metrics["Total return"]), help="Adjusted-price change from the first to last observed price.")
        primary[1].metric("CAGR", fmt_pct(focus_metrics["CAGR"]), help="Annualized compound return over the observed calendar span.")
        primary[2].metric("Annualized volatility", fmt_pct(focus_metrics["Annualized volatility"]), help="Daily-return standard deviation annualized using √252.")
        primary[3].metric("Maximum drawdown", fmt_pct(focus_metrics["Maximum drawdown"]), help="Largest observed peak-to-trough price decline.")

        with st.expander("More metrics"):
            secondary_specs = [
                ("Sharpe ratio", fmt_num, "Annualized excess return divided by annualized volatility, using the selected risk-free rate."),
                ("Sortino ratio", fmt_num, "Annualized excess return divided by downside deviation below the selected risk-free rate."),
                ("Beta vs. NIFTY 50", fmt_num, "Covariance of aligned daily returns divided by NIFTY 50 return variance."),
                ("95% historical VaR", fmt_pct, "Positive loss magnitude at the 5th percentile of included daily returns."),
                ("95% historical CVaR", fmt_pct, "Average loss magnitude for returns at or below the 5th percentile."),
                ("Best day", fmt_pct, "Largest included daily simple return."),
                ("Worst day", fmt_pct, "Smallest included daily simple return."),
                ("Positive-day percentage", fmt_pct, "Share of included daily returns greater than zero."),
            ]
            secondary = st.columns(4)
            for index, (label, formatter, help_text) in enumerate(secondary_specs):
                value_key = "Beta" if label == "Beta vs. NIFTY 50" else (
                    "Positive days" if label == "Positive-day percentage" else label
                )
                secondary[index % 4].metric(
                    label,
                    formatter(focus_metrics.get(value_key, float("nan"))),
                    help=help_text,
                )
            st.caption(
                f"Risk-free assumption for Sharpe/Sortino: **{annual_risk_free:.2%} annualized**. "
                f"Daily calculations use {focus_metrics.get('Observation count', 0)} included returns."
            )

    if metrics_by_symbol:
        st.subheader("Selected-stock summary")
        table_rows = []
        for symbol, metrics in metrics_by_symbol.items():
            table_rows.append(
                {
                    "Company": display_name(symbol),
                    "Total return": metrics.get("Total return", float("nan")),
                    "CAGR": metrics.get("CAGR", float("nan")),
                    "Volatility": metrics.get("Annualized volatility", float("nan")),
                    "Sharpe": metrics.get("Sharpe ratio", float("nan")),
                    "Max drawdown": metrics.get("Maximum drawdown", float("nan")),
                }
            )
        summary = pd.DataFrame(table_rows).set_index("Company")
        st.dataframe(
            summary.style.format(
                {
                    "Total return": "{:.2%}",
                    "CAGR": "{:.2%}",
                    "Volatility": "{:.2%}",
                    "Sharpe": "{:.2f}",
                    "Max drawdown": "{:.2%}",
                },
                na_rep="—",
            ),
            width="stretch",
        )

with returns_tab:
    st.subheader("Log Returns Dist")
    st.caption(f"Daily log returns for {focus_name}; intervals spanning gaps longer than seven calendar days are excluded.")
    if not focus_log_returns.empty:
        distribution = st.columns(4)
        distribution[0].metric("Mean", fmt_pct(focus_log_returns.mean()), help="Arithmetic mean of included daily log returns.")
        distribution[1].metric("Median", fmt_pct(focus_log_returns.median()), help="Median of included daily log returns.")
        distribution[2].metric("Skewness", fmt_num(focus_log_returns.skew()), help="Asymmetry of the historical return distribution.")
        distribution[3].metric("Kurtosis", fmt_num(focus_log_returns.kurt()), help="Fisher excess kurtosis; a normal distribution is approximately 0.")
        histogram = px.histogram(
            x=focus_log_returns * 100,
            nbins=50,
            labels={"x": "Daily log return (%)", "count": "Trading observations"},
            title=f"Daily log-return distribution — {focus_name}",
        )
        histogram.update_layout(hovermode="x unified")
        st.plotly_chart(histogram, width="stretch")
    else:
        st.info("Not enough valid daily returns for this distribution.")

with normalized_tab:
    st.subheader("Normalized Price")
    st.caption("Adjusted daily closing prices indexed to 100 at each ticker's first available observation.")
    normalized = pd.DataFrame(index=analysis_prices.index)
    chart_symbols = list(selected_stocks)
    if include_benchmark and BENCHMARK in analysis_prices:
        chart_symbols.append(BENCHMARK)
    for symbol in chart_symbols:
        if symbol in analysis_prices and analysis_prices[symbol].notna().any():
            series = analysis_prices[symbol]
            normalized[display_name(symbol)] = series / series.dropna().iloc[0] * 100
    if not normalized.empty:
        fig = px.line(
            normalized,
            x=normalized.index,
            y=normalized.columns,
            labels={"x": "Date", "value": "Indexed adjusted price (first observation = 100)", "variable": "Company"},
            title="Normalized price performance vs. NIFTY 50",
        )
        fig.update_layout(hovermode="x unified", legend_title="Company")
        st.plotly_chart(fig, width="stretch")
        add_chart_note()
    else:
        st.info("No normalized prices are available for the selected stocks.")

with volatility_tab:
    st.subheader("Rolling Volatility")
    st.caption(f"21-trading-day rolling annualized volatility for {focus_name}.")
    if len(focus_returns) >= 21:
        rolling_vol = focus_returns.rolling(21).std(ddof=1) * np.sqrt(252)
        vol_chart = px.line(
            x=rolling_vol.index,
            y=rolling_vol,
            labels={"x": "Date", "y": "Annualized volatility"},
            title=f"21-trading-day rolling volatility — {focus_name}",
        )
        vol_chart.update_yaxes(tickformat=".0%")
        st.plotly_chart(vol_chart, width="stretch")
        add_chart_note()
    else:
        st.info("At least 21 valid daily returns are needed to calculate rolling volatility.")

with drawdown_tab:
    st.subheader("Drawdown")
    st.caption(f"Peak-to-trough decline in adjusted daily closing price for {focus_name}.")
    if not focus_prices.empty:
        drawdowns = drawdown_series(focus_prices)
        drawdown_chart = px.area(
            x=drawdowns.index,
            y=drawdowns,
            labels={"x": "Date", "y": "Drawdown from peak"},
            title=f"Drawdown over time — {focus_name}",
        )
        drawdown_chart.update_yaxes(tickformat=".0%")
        st.plotly_chart(drawdown_chart, width="stretch")
        add_chart_note()
    else:
        st.info("No price observations are available for this stock.")

with sharpe_tab:
    st.subheader("Sharpe Ratio")
    st.caption(
        f"Rolling 63-trading-day Sharpe ratio for {focus_name}. "
        f"Annual risk-free rate assumption: **{annual_risk_free:.2%}** "
        "(adjust it in the sidebar)."
    )
    if len(focus_returns) >= 63:
        excess_returns = focus_returns - annual_risk_free / 252
        rolling_sharpe = (
            excess_returns.rolling(63).mean()
            / focus_returns.rolling(63).std(ddof=1)
            * np.sqrt(252)
        )
        sharpe_chart = px.line(
            x=rolling_sharpe.index,
            y=rolling_sharpe,
            labels={"x": "Date", "y": "Annualized Sharpe ratio"},
            title=f"63-trading-day rolling Sharpe ratio — {focus_name}",
        )
        sharpe_chart.add_hline(y=0, line_dash="dot", line_color="gray")
        st.plotly_chart(sharpe_chart, width="stretch")
        st.caption("Sharpe = annualized average return above the assumed risk-free rate ÷ annualized volatility.")
    else:
        st.info("At least 63 valid daily returns are needed to calculate the rolling Sharpe ratio.")

with correlation_tab:
    st.subheader("Correlation")
    st.caption("Pairwise correlation of selected stocks' valid daily simple returns.")
    returns_frame = pd.DataFrame(
        {
            display_name(symbol): daily_returns(analysis_prices[symbol])
            for symbol in selected_stocks
            if symbol in analysis_prices
        }
    )
    correlation = returns_frame.corr(min_periods=30)
    if len(correlation.columns) >= 2:
        correlation_chart = px.imshow(
            correlation,
            text_auto=".2f",
            zmin=-1,
            zmax=1,
            color_continuous_scale="RdBu",
            labels={"color": "Correlation"},
            title="Daily return correlation (pairwise observations)",
            aspect="auto",
        )
        st.plotly_chart(correlation_chart, width="stretch")
        st.caption("Each cell uses dates shared by its stock pair and at least 30 aligned daily returns.")
    else:
        st.info("Select at least two stocks with enough overlapping history to show a correlation heatmap.")

with more_tab:
    st.subheader("More analysis")
    st.markdown("#### Cumulative returns")
    cumulative = pd.DataFrame(index=analysis_prices.index)
    for symbol in chart_symbols:
        if symbol in analysis_prices and analysis_prices[symbol].notna().any():
            series = analysis_prices[symbol]
            cumulative[display_name(symbol)] = series / series.dropna().iloc[0] - 1
    if not cumulative.empty:
        cumulative_chart = px.line(
            cumulative,
            x=cumulative.index,
            y=cumulative.columns,
            labels={"x": "Date", "value": "Cumulative adjusted-price return", "variable": "Company"},
            title="Cumulative return from each company's first available price",
        )
        cumulative_chart.update_yaxes(tickformat=".0%")
        cumulative_chart.update_layout(hovermode="x unified")
        st.plotly_chart(cumulative_chart, width="stretch")

    st.markdown("#### Monthly returns heatmap")
    if not focus_prices.empty:
        monthly_prices = focus_prices.resample("ME").last().dropna()
        month_numbers = pd.Series(monthly_prices.index.year * 12 + monthly_prices.index.month, index=monthly_prices.index)
        monthly_returns = monthly_prices.pct_change(fill_method=None).where(month_numbers.diff() == 1).dropna()
        if not monthly_returns.empty:
            month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
            heatmap_data = pd.DataFrame(
                {"year": monthly_returns.index.year, "month": monthly_returns.index.month, "return": monthly_returns}
            ).pivot(index="year", columns="month", values="return").reindex(columns=range(1, 13))
            heatmap = px.imshow(
                heatmap_data * 100,
                labels={"x": "Month", "y": "Year", "color": "Return (%)"},
                x=month_names,
                color_continuous_scale="RdYlGn",
                color_continuous_midpoint=0,
                aspect="auto",
                title=f"Monthly returns — {focus_name}",
            )
            st.plotly_chart(heatmap, width="stretch")
            st.caption("Months without adjacent available month-end observations are left blank.")
        else:
            st.info("Not enough consecutive available month-end prices for monthly returns.")

    st.markdown("#### Historical risk versus return")
    risk_points = [
        {
            "Company": display_name(symbol),
            "Annualized volatility": values["Annualized volatility"],
            "CAGR": values["CAGR"],
        }
        for symbol, values in metrics_by_symbol.items()
        if pd.notna(values.get("Annualized volatility", float("nan")))
        and pd.notna(values.get("CAGR", float("nan")))
    ]
    if risk_points:
        risk_chart = px.scatter(
            pd.DataFrame(risk_points),
            x="Annualized volatility",
            y="CAGR",
            hover_name="Company",
            labels={"Annualized volatility": "Annualized volatility", "CAGR": "CAGR"},
            title="Historical risk versus return",
        )
        risk_chart.update_xaxes(tickformat=".0%")
        risk_chart.update_yaxes(tickformat=".0%")
        st.plotly_chart(risk_chart, width="stretch")
        st.caption("Each point summarizes the selected date range; historical risk and return are not forecasts.")

with coverage_tab:
    st.subheader("Data coverage")
    st.write(
        "Coverage differs by company. These are actual first and last non-missing adjusted daily prices returned "
        "within the selected date range. The selected dates are not shortened to hide gaps."
    )
    coverage_display = pd.DataFrame(coverage_rows).drop(columns=["Ticker"])
    st.dataframe(coverage_display, hide_index=True, width="stretch")
    st.caption(
        "No prices are invented or forward-filled. Weekends and exchange holidays normally have no daily bar; "
        "provider gaps are preserved. yfinance is an unofficial Yahoo Finance data wrapper; provider coverage "
        "and terms apply."
    )

with screener_tab:
    st.subheader("Research screen")
    st.warning(
        "Ranked names are candidates for further research only — not guaranteed winners or personalized buy/sell recommendations."
    )
    horizon_days = HORIZONS[horizon_label]
    st.caption(
        f"{horizon_label} uses up to {horizon_days} daily price observations from the selected date range, "
        "ending at the last available observation for each stock."
    )
    ranking = build_screener(analysis_prices, horizon_days, annual_risk_free)
    if ranking.empty:
        st.info("At least 30 valid daily returns are needed to rank a selected stock.")
    else:
        st.write(
            "Repeatable relative score (0–100): 40% normalized horizon return, 30% normalized Sharpe ratio, "
            "20% lower normalized volatility, and 10% shallower normalized maximum drawdown. "
            "Each input is compared only within this selected watchlist and horizon; equal inputs receive a neutral score."
        )
        visible_ranking = ranking.rename(
            columns={"Company": "Candidate for further research", "Return": "Horizon return"}
        ).drop(columns=["Symbol"])
        for column in ("Horizon return", "Volatility", "Max drawdown"):
            visible_ranking[column] = visible_ranking[column].map(fmt_pct)
        visible_ranking["Sharpe"] = visible_ranking["Sharpe"].map(fmt_num)
        visible_ranking["Score"] = visible_ranking["Score"].map(lambda value: f"{value:.1f}")
        st.dataframe(visible_ranking, hide_index=True, width="stretch")

        selected_ranked_stock = st.selectbox(
            "Explain a historical ranking",
            options=ranking["Symbol"].tolist(),
            format_func=display_name,
        )
        selected_row = ranking.loc[ranking["Symbol"] == selected_ranked_stock].iloc[0]
        horizon_metrics = calculate_metrics(
            analysis_prices[selected_ranked_stock].dropna().tail(horizon_days),
            benchmark_prices,
            annual_risk_free,
        )
        screen_metrics = {
            metric: float(horizon_metrics.get(metric, float("nan")))
            for metric in (
                "Total return", "CAGR", "Sharpe ratio", "Sortino ratio",
                "Annualized volatility", "Maximum drawdown", "Beta",
            )
        }
        st.write(local_explanation(selected_row["Company"], screen_metrics, int(selected_row["Rank"])))
        if st.button("Generate optional AI explanation", key="generate_ai"):
            if not get_openai_key():
                st.info(
                    "No OPENAI_API_KEY is configured. Use the metrics-based explanation above, or configure a key "
                    "locally using the README instructions."
                )
            else:
                try:
                    st.markdown("**AI-generated research information**")
                    st.write(
                        explain_with_openai(selected_row["Company"], screen_metrics, int(selected_row["Rank"]))
                    )
                    st.caption("Generated only from the historical metrics shown here; not financial advice.")
                except Exception as exc:
                    st.error(f"The AI explanation could not be generated: {exc}")

st.divider()
st.caption(
    "Educational use only. This app is not financial, investment, tax, or legal advice, and it does not account "
    "for your objectives or circumstances. Historical performance does not guarantee future results."
)
