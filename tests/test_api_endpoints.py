"""Tests for Flask API endpoints and integration pipeline."""

import pytest
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_health_check_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "ok"
    assert data["app"] == "Stock Market Distribution Analyzer"


def test_index_page_loads(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Stock Market Distribution Analyzer" in response.data
    assert b"SYNTHETIC DEMO" in response.data


def test_api_analyze_synthetic_pipeline(client):
    payload = {
        "source": "synthetic",
        "ticker": "RELIANCE.NS",
        "benchmark": "^NSEI",
        "start_date": "2023-01-01",
        "end_date": "2024-01-01",
        "return_type": "simple",
        "confidence_level": 0.95,
        "bootstrap_method": "iid",
        "bootstrap_seed": 42,
    }
    response = client.post("/api/analyze", json=payload)
    assert response.status_code == 200
    data = response.get_json()

    assert data["meta"]["is_synthetic"] is True
    assert data["meta"]["ticker"] == "RELIANCE.NS"
    assert "statistics" in data
    assert "risk" in data
    assert "distribution" in data
    assert "sampling" in data
    assert "signal" in data
    assert "timeseries" in data
    assert "histogram" in data

    # Verify statistical figures
    stats = data["statistics"]
    assert stats["count"] > 100
    assert "annual_volatility" in stats
    assert "mean_daily" in stats

    # Verify distribution fit
    dist = data["distribution"]
    assert "student_t" in dist
    assert "normal" in dist

    # Verify signal presence and educational disclaimer
    sig = data["signal"]
    assert sig["signal"] in ["BUY", "HOLD", "SELL"]
    assert "disclaimer" in sig


def test_api_export_csv(client):
    payload = {
        "source": "synthetic",
        "ticker": "TCS.NS",
        "benchmark": "^NSEI",
        "start_date": "2023-01-01",
        "end_date": "2023-06-01",
    }
    response = client.post("/api/export/csv", json=payload)
    assert response.status_code == 200
    assert response.mimetype == "text/csv"
    assert b"Simple Return" in response.data
    assert b"Cumulative Return" in response.data


def test_api_export_report(client):
    # Dummy metric bundle
    payload = {
        "metrics": {
            "meta": {"ticker": "RELIANCE.NS", "benchmark_ticker": "^NSEI", "source": "Synthetic Demo", "is_synthetic": True},
            "statistics": {"count": 100, "annual_volatility": 0.20, "annual_mean_compound": 0.12},
            "risk": {"max_drawdown": -0.15, "historical_var": 0.02},
            "distribution": {"model_comparison": {"preferred_model_by_aic": "Student-t"}},
        },
        "signal": {"signal": "HOLD", "confidence": "MEDIUM", "rationale": "Test rationale", "disclaimer": "Educational notice"},
        "guide": {"guidance_items": []},
        "backtest": {},
    }
    response = client.post("/api/export/report", json=payload)
    assert response.status_code == 200
    assert response.mimetype == "text/markdown"
    assert b"# Stock Market Distribution Analyzer: Quantitative Analysis Report" in response.data


def test_sample_csv_download(client):
    response = client.get("/api/sample-csv/reliance_sample.csv")
    assert response.status_code == 200
    assert b"Adj Close" in response.data
