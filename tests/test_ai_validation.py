"""Tests for AI response validation, safety downgrades, and deterministic scoring."""

import pytest
from ai.validator import validate_ai_signal
from ai.signal_generator import compute_deterministic_baseline_score
import pandas as pd
import numpy as np


def test_validation_enforces_hold_on_short_history():
    # Only 35 observations (< 60 conviction threshold)
    metrics = {
        "statistics": {"count": 35, "annual_volatility": 0.18, "annual_mean_compound": 0.15},
        "risk": {"max_drawdown": -0.10},
    }
    candidate = {
        "signal": "BUY",
        "confidence": "HIGH",
        "rationale": "Strong historical return observed.",
    }

    validated, adjustments = validate_ai_signal(candidate, metrics, min_observations_for_conviction=60)

    # Must be downgraded to HOLD with INSUFFICIENT_EVIDENCE
    assert validated["signal"] == "HOLD"
    assert validated["confidence"] == "INSUFFICIENT_EVIDENCE"
    assert any("conviction" in a.lower() for a in adjustments)


def test_validation_enforces_enum_values():
    metrics = {
        "statistics": {"count": 120, "annual_volatility": 0.18, "annual_mean_compound": 0.15},
        "risk": {"max_drawdown": -0.10},
    }
    candidate = {
        "signal": "STRONG_BUY_GUARANTEED",  # Invalid enum
        "confidence": "SUPER_HIGH",          # Invalid enum
        "rationale": "Buy now for profit with target price of 3000.",
    }

    validated, adjustments = validate_ai_signal(candidate, metrics)

    # Replaced with allowed enums
    assert validated["signal"] in ["BUY", "HOLD", "SELL"]
    assert validated["confidence"] in ["HIGH", "MEDIUM", "LOW", "INSUFFICIENT_EVIDENCE"]
    # Promotional language sanitized
    assert "target price" not in validated["rationale"].lower()


def test_deterministic_baseline_score_direction():
    # Strongly trending upward price series
    prices_up = pd.Series(np.linspace(100, 200, 100))
    base_up = compute_deterministic_baseline_score(prices_up)
    assert base_up["baseline_score"] > 0
    assert base_up["baseline_signal"] == "BUY"

    # Strongly trending downward price series
    prices_down = pd.Series(np.linspace(200, 100, 100))
    base_down = compute_deterministic_baseline_score(prices_down)
    assert base_down["baseline_score"] < 0
    assert base_down["baseline_signal"] == "SELL"
