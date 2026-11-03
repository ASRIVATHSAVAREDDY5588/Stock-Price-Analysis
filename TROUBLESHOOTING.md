# Troubleshooting Guide: Stock Market Distribution Analyzer

This document provides solutions for common issues that may arise during installation, data fetching, or dashboard execution on Windows.

---

## 1. Installation & Environment Issues

### Issue: `'python' is not recognized as an internal or external command`
- **Root Cause:** Python was installed without checking the "Add python.exe to PATH" option.
- **Solution:**
  1. Open Windows "Add or remove programs", find Python, and click "Modify".
  2. Select "Modify", click "Next", and ensure **"Add Python to environment variables"** is checked.
  3. Alternatively, reinstall Python from [python.org](https://www.python.org/) and check the box on the first screen.

### Issue: `setup_windows.bat` fails during `pip install -r requirements.txt`
- **Root Cause:** An unstable network connection or outdated `pip` version.
- **Solution:**
  1. Manually upgrade pip:
     ```cmd
     .venv\Scripts\activate
     python -m pip install --upgrade pip
     ```
  2. Install dependencies one by one to identify any conflicting package:
     ```cmd
     pip install flask pandas numpy scipy scikit-learn plotly yfinance openai pydantic python-dotenv pyarrow requests pytest
     ```

---

## 2. Server Startup & Port Conflicts

### Issue: Port 5000 is occupied or in use
- **Root Cause:** Another application (e.g., Docker, another Flask server, or a local proxy) is already listening on port 5000.
- **Solution:**
  1. `start_dashboard.bat` automatically checks if the existing service is Stock Market Distribution Analyzer. If it is, it will open the browser without crashing.
  2. If an unrelated program is occupying port 5000, edit `.env`:
     ```env
     LAB_PORT=5050
     ```
  3. Re-run `start_dashboard.bat`. The app will now bind to `http://127.0.0.1:5050`.

### Issue: Browser does not open automatically
- **Solution:** Once the Command Prompt displays `[OK] Server is ready and healthy!`, open your browser manually and navigate to `http://127.0.0.1:5000`.

---

## 3. Data Ingestion & Yahoo Finance Errors

### Issue: Yahoo Finance timeout or `YFinanceFetchError`
- **Symptoms:** Alert banner displays: `"Failed to fetch market data for 'RELIANCE.NS' after 2 attempts: Connection timed out"`.
- **Root Causes:**
  - The PC is disconnected from the internet or behind an enterprise firewall/proxy.
  - Yahoo Finance rate-limiting or service degradation.
  - Incorrect ticker symbol (e.g., typing `RELIANCE` instead of `RELIANCE.NS`).
- **Remediation:**
  1. **Switch to Synthetic Demo Data:** In the Data Source dropdown, select **"Synthetic Demo Data"**. The lab will immediately generate realistic fat-tailed data 100% offline.
  2. **Check Symbol Suffix:** For Indian equities on the National Stock Exchange, always ensure the `.NS` suffix is present (e.g., `TCS.NS`, `INFY.NS`). For BSE, use `.BO`.
  3. **Verify Date Range:** Ensure the start date is before the end date and that the selected range includes trading days (not just weekends).

---

## 4. Custom CSV Upload Issues

### Issue: `CSVValidationError: CSV is missing a recognized Date column`
- **Solution:** Ensure your CSV file has a column named `Date`, `timestamp`, or `TradeDate`. Header names are case-insensitive.

### Issue: `CSVValidationError: Insufficient observations (N < 15)`
- **Solution:** The statistical models require at least 15 valid daily trading sessions. Ensure your CSV file contains more than 15 rows of daily data.

### Issue: Duplicate dates or mixed date formats
- **Solution:** The built-in parser automatically sorts dates and keeps the latest entry for duplicates. However, ensure dates follow either ISO (`YYYY-MM-DD`), American (`MM/DD/YYYY`), or Indian (`DD-MM-YYYY`) formats.

---

## 5. OpenAI & AI Signal Troubleshooting

### Issue: Signal shows "Rule-Based Deterministic Engine (AI Not Configured)"
- **Normal Behavior:** This is expected when no OpenAI API key is supplied. The entire application operates completely offline using the deterministic scoring engine.
- **To Enable OpenAI Commentary:**
  1. Open `.env` in the project folder.
  2. Set `OPENAI_API_KEY=sk-...` (your actual OpenAI secret key).
  3. Save the file and refresh or re-run `start_dashboard.bat`.

### Issue: `RateLimitError` or `AuthenticationError` from OpenAI
- **Behavior:** The dashboard automatically captures the error, displays a gentle notice, and seamlessly falls back to the deterministic baseline score.
- **Solution:**
  1. Verify that your API key is active on [platform.openai.com](https://platform.openai.com/).
  2. Confirm your OpenAI account has available usage credits.
  3. You can continue using the dashboard normally; the non-AI analytics are completely unaffected.
