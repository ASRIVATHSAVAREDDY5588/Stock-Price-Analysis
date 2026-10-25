# India Stock Lab

India Stock Lab is a Streamlit application for exploring historical daily prices for NSE-listed stocks. Compare adjusted price performance with the NIFTY 50, inspect return and risk charts, review actual data coverage, and use a transparent historical research screen.

## Windows setup and run

1. Install Python 3.10 or later from [python.org](https://www.python.org/downloads/windows/). During installation, enable **Add Python to PATH**.
2. Open PowerShell in this project folder.
3. Create and activate a virtual environment:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   If PowerShell blocks activation, run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once, then activate again.

4. Install dependencies and start the app:

   ```powershell
   python -m pip install -r requirements.txt
   streamlit run app.py
   ```

5. Open the local address printed by Streamlit, usually [http://localhost:8501](http://localhost:8501). Stop the server with **Ctrl+C** in PowerShell.

## Using the app

- **Date range:** defaults to **Maximum available history**, requesting dates from 2000-01-01 through today. Choose 10 years, 5 years, 3 years, 1 year, or **Custom range**. Custom dates have separate **From** and **To** calendars; To cannot precede From. The app shows the requested range and each stock's actual observed dates. A company's history may start later than the selected start date.
- **Sidebar:** select NSE companies by name, choose a focus company for single-stock charts, include NIFTY 50 in comparison charts, and select a short-, medium-, or long-term research-screen horizon. Add a custom NSE ticker if it is not in the curated list; the app appends `.NS` when omitted. Ticker codes are available under **Details**.
- **Overview:** see a compact set of primary metrics. Expand **More metrics** for Sharpe, Sortino, beta, historical VaR/CVaR, best/worst day, and positive-day percentage.
- **Six chart views:** **Log Returns Dist**, **Normalized Price**, **Rolling Volatility**, **Drawdown**, **Sharpe Ratio**, and **Correlation** each have their own tab. **More analysis** adds cumulative returns, a monthly returns heatmap, and historical risk-versus-return comparison.
- **Data coverage:** check the actual first and last available daily prices for selected stocks and whether history begins later than the requested period.
- **Research screen:** compare selectable short-, medium-, and long-term horizons using historical return and risk metrics. The score is relative to the selected stocks and period, not a prediction or personalized buy/sell recommendation.

The displayed annual risk-free rate is an adjustable assumption used in Sharpe and Sortino calculations; it is not a live government yield. VaR and CVaR are historical daily loss measures based on the 5th percentile. Beta compares aligned daily returns with the NIFTY 50.

## Data source and limitations

Prices come from Yahoo Finance through [yfinance](https://github.com/ranaroussi/yfinance), an **unofficial Yahoo Finance data wrapper**. The app uses daily adjusted closing prices, not live or real-time quotes. The data provider controls coverage, availability, and terms; data may be delayed, incomplete, or unavailable, and historical coverage varies by company. The app displays actual observed first and last dates, does not invent prices or forward-fill gaps, and excludes return observations spanning gaps longer than seven calendar days from daily risk calculations. Weekends and exchange holidays normally have no daily bar. A maximum-history request begins on 2000-01-01, but a given company may have started trading later. The app also requests NIFTY 50 under Yahoo Finance's `^NSEI` symbol.

Risk measures and historical returns depend on the selected dates and available observations. They do not account for transaction costs, taxes, or an individual's circumstances.

## Optional OpenAI explanations

The app always gives a local explanation using its displayed metrics. To request an additional GPT-generated explanation, configure `OPENAI_API_KEY` locally; never paste or share the key in chat.

**PowerShell environment variable for the current terminal:**

```powershell
$env:OPENAI_API_KEY = "your-key-goes-here"
streamlit run app.py
```

Or copy `.streamlit\secrets.toml.example` to `.streamlit\secrets.toml` and replace the placeholder on your computer:

```toml
OPENAI_API_KEY = "your-key-goes-here"
```

The app reads the key from the environment or Streamlit secrets and never displays it. The key and local `.env` files are ignored by Git. When requested, the AI receives only the selected stock's calculated historical metrics and ranking; its output is labeled AI-generated research information. It is instructed not to add news, current prices, forecasts, or personalized recommendations. Without a key, all other features and the local explanation remain available.

## Educational-use disclaimer

This app is for educational and informational use only. It is not financial, investment, tax, or legal advice and is not personalized to your objectives, financial situation, or needs. Historical performance does not guarantee or reliably predict future results. Do your own research and consult a qualified financial professional before making investment decisions.
