"""Configuration module for Stock Market Distribution Analyzer.

Handles environment variable loading, default constants, pre-configured Indian tickers,
trading day conventions, and server settings.
"""

from __future__ import annotations

import os
# Prevent joblib core-count detection delay on Windows
os.environ.setdefault("LOKY_MAX_CPU_COUNT", str(os.cpu_count() or 4))

from pathlib import Path
from dotenv import load_dotenv

# Base paths
PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"
SAMPLE_DATA_DIR = DATA_DIR / "sample_data"
RAW_DATA_DIR = DATA_DIR / "raw"
CLEANED_DATA_DIR = DATA_DIR / "cleaned"
CACHE_DIR = PROJECT_ROOT / ".cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
CLEANED_DATA_DIR.mkdir(parents=True, exist_ok=True)

# Load environment variables from .env if present
load_dotenv(PROJECT_ROOT / ".env")

# Server settings
HOST = os.environ.get("LAB_HOST", "127.0.0.1")
PORT = int(os.environ.get("LAB_PORT", "5000"))
DEBUG = os.environ.get("LAB_DEBUG", "False").lower() in ("true", "1", "yes")
SECRET_KEY = os.environ.get("SECRET_KEY", "india-stock-lab-insecure-dev-key-change-in-prod")

# Data & Market Conventions
TRADING_DAYS_PER_YEAR = 252  # Standard Indian equity market annualization convention
CACHE_TTL_SECONDS = int(os.environ.get("CACHE_TTL_SECONDS", "3600"))  # 1 hour default
DOWNLOAD_TIMEOUT_SECONDS = int(os.environ.get("DOWNLOAD_TIMEOUT_SECONDS", "10"))
MIN_OBSERVATIONS_REQUIRED = 15
RECOMMENDED_MIN_OBSERVATIONS = 30

# Active Sourced Sample Coverage
DEFAULT_START_DATE = "2000-01-01"
DEFAULT_END_DATE = "2026-11-02"
ACTIVE_SAMPLE_PERIOD_LABEL = "2000–2026 YTD"
LAST_TRADING_DATE = "2026-11-02"

# Pre-configured Indian Equity Tickers & Benchmarks
DEFAULT_TICKERS = {
    "RELIANCE.NS": "Reliance Industries Ltd",
    "TCS.NS": "Tata Consultancy Services Ltd",
    "INFY.NS": "Infosys Ltd",
    "HDFCBANK.NS": "HDFC Bank Ltd",
    "ICICIBANK.NS": "ICICI Bank Ltd",
    "BHARTIARTL.NS": "Bharti Airtel Ltd",
    "ITC.NS": "ITC Ltd",
    "SBIN.NS": "State Bank of India",
    "LT.NS": "Larsen & Toubro Ltd",
    "TATAMOTORS.NS": "Tata Motors Ltd",
}

DEFAULT_BENCHMARKS = {
    "^NSEI": "NIFTY 50 Index",
    "^BSESN": "S&P BSE SENSEX",
    "^NSEBANK": "NIFTY Bank Index",
}

DEFAULT_TICKER = "RELIANCE.NS"
DEFAULT_BENCHMARK = "^NSEI"

# AI Settings
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "").strip()
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini").strip()
AI_CONFIGURED = bool(OPENAI_API_KEY and not OPENAI_API_KEY.startswith("your_"))

# Transaction cost for walk-forward backtesting (10 basis points = 0.10%)
DEFAULT_TRANSACTION_COST_BPS = 10.0  # 10 bps
