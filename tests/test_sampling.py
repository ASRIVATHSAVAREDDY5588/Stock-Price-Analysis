"""Tests for Bootstrap reproducibility and Central Limit Theorem explorer."""

import numpy as np
import pandas as pd
import pytest
from analytics.sampling import run_bootstrap_simulation, run_clt_explorer


def test_bootstrap_reproducibility_with_seed():
    rng = np.random.default_rng(77)
    returns = pd.Series(rng.normal(0.001, 0.015, size=150))

    # Run twice with same seed
    res1 = run_bootstrap_simulation(returns, iterations=200, seed=42)
    res2 = run_bootstrap_simulation(returns, iterations=200, seed=42)

    # All confidence interval bounds and point estimates should be identical
    assert res1["mean_return"]["ci_lower"] == res2["mean_return"]["ci_lower"]
    assert res1["mean_return"]["ci_upper"] == res2["mean_return"]["ci_upper"]
    assert res1["annual_volatility"]["ci_lower"] == res2["annual_volatility"]["ci_lower"]
    assert res1["var_95"]["ci_lower"] == res2["var_95"]["ci_lower"]

    # Run with different seed -> should produce slightly different resamples
    res3 = run_bootstrap_simulation(returns, iterations=200, seed=99)
    assert res1["mean_return"]["ci_lower"] != res3["mean_return"]["ci_lower"]


def test_block_bootstrap_execution():
    rng = np.random.default_rng(88)
    returns = pd.Series(rng.normal(0.001, 0.015, size=150))

    res_block = run_bootstrap_simulation(returns, iterations=200, method="block", block_size=5, seed=42)
    assert res_block["method"] == "block"
    assert "mean_return" in res_block
    assert res_block["mean_return"]["ci_lower"] < res_block["mean_return"]["point_estimate"] < res_block["mean_return"]["ci_upper"]


def test_clt_explorer_variance_decay():
    # Draw highly skewed / non-normal data
    rng = np.random.default_rng(123)
    sample = rng.exponential(scale=0.02, size=300) - 0.02  # Skewed
    returns = pd.Series(sample)

    clt = run_clt_explorer(returns, sample_sizes=[5, 10, 30, 50], num_trials=500, seed=42)

    sizes = clt["sample_sizes"]
    # Standard error should decay inversely with sqrt(n)
    # SE(5) > SE(10) > SE(30) > SE(50)
    se_5 = sizes["5"]["simulated_se"]
    se_10 = sizes["10"]["simulated_se"]
    se_30 = sizes["30"]["simulated_se"]
    se_50 = sizes["50"]["simulated_se"]

    assert se_5 > se_10 > se_30 > se_50

    # Skewness of sample mean should be closer to 0 for n=50 than for n=5
    assert abs(sizes["50"]["skewness"]) < abs(sizes["5"]["skewness"])
