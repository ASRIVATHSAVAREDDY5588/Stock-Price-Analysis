"""Tests for distribution fitting (Normal, Student-t, GMM) and goodness-of-fit tests."""

import numpy as np
import pandas as pd
import pytest
from scipy import stats
from analytics.distributions import fit_distributions_and_tests


def test_student_t_fit_recovers_heavy_tails():
    # Draw from Student-t with nu=4 (fat tails)
    rng = np.random.default_rng(42)
    sample = stats.t.rvs(df=4.0, loc=0.0005, scale=0.015, size=800, random_state=rng)
    returns = pd.Series(sample)

    res = fit_distributions_and_tests(returns)

    # 1. Degrees of freedom estimated should be close to 4 (e.g. 2.5 to 7.0)
    assert 2.0 <= res["student_t"]["df"] <= 8.0

    # 2. For fat-tailed data, Student-t AIC should be lower than Normal AIC
    assert res["student_t"]["aic"] < res["normal"]["aic"]
    assert res["model_comparison"]["preferred_model_by_aic"] == "Student-t"

    # 3. Jarque-Bera should reject normality
    assert res["jarque_bera"]["reject_normality_at_5pct"] is True

    # 4. GMM should be present
    assert "gmm" in res


def test_gaussian_data_prefers_normal_or_high_df():
    # Draw from Normal distribution
    rng = np.random.default_rng(999)
    sample = rng.normal(loc=0.0008, scale=0.012, size=500)
    returns = pd.Series(sample)

    res = fit_distributions_and_tests(returns)

    # Degrees of freedom for normal data should be large (> 20)
    assert res["student_t"]["df"] > 15.0


def test_plain_language_disclaimer_present():
    rng = np.random.default_rng(123)
    returns = pd.Series(rng.normal(0, 0.01, size=100))
    res = fit_distributions_and_tests(returns)

    assert "epistemological_disclaimer" in res["plain_language"]
    assert "DOES NOT prove" in res["plain_language"]["epistemological_disclaimer"]
