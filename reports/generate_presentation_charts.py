"""Generate high-resolution presentation charts for Stock Market Distribution Analyzer.

Recomputes and saves all presentation assets in presentation_extraction/assets/
using the full 2000-2026 YTD dataset (6,615 daily sessions).
"""

from __future__ import annotations

import os
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
from scipy import stats

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CLEANED_DIR = PROJECT_ROOT / "data" / "cleaned"
if (PROJECT_ROOT / "presentation").exists():
    ASSETS_DIR = PROJECT_ROOT / "presentation" / "assets"
else:
    ASSETS_DIR = PROJECT_ROOT.parent / "presentation_extraction" / "assets"
ASSETS_DIR.mkdir(parents=True, exist_ok=True)

# Set clean financial style
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams["font.sans-serif"] = ["Segoe UI", "DejaVu Sans", "Arial"]
plt.rcParams["axes.edgecolor"] = "#cccccc"
plt.rcParams["axes.linewidth"] = 0.8


def generate_all_slide_charts():
    # 1. Load data
    rel_df = pd.read_csv(CLEANED_DIR / "reliance_cleaned_2000_2026.csv", parse_dates=["Date"], index_col="Date")
    nifty_df = pd.read_csv(CLEANED_DIR / "nifty50_cleaned_2000_2026.csv", parse_dates=["Date"], index_col="Date")

    p = rel_df["Adj Close"]
    b = nifty_df["Close"]
    common = p.dropna().index.intersection(b.dropna().index).sort_values()
    p = p.loc[common]
    b = b.loc[common]

    r_simple = p.pct_change().dropna()
    start_date_str = common[0].strftime("%d-%b-%Y")
    end_date_str = common[-1].strftime("%d-%b-%Y")
    n_days = len(common)

    print(f"Generating charts for period: {start_date_str} to {end_date_str} (N={n_days} days)...")

    # -------------------------------------------------------------
    # Slide 02: Price Growth (Indexed ₹100 from 2000 to 2026 YTD)
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(11, 5.5), dpi=300)
    idx_p = (p / p.iloc[0]) * 100.0
    idx_b = (b / b.iloc[0]) * 100.0

    ax.plot(idx_p.index, idx_p, label=f"Reliance Industries (CAGR: 18.98%, Final: ₹{idx_p.iloc[-1]:,.0f})", color="#0052cc", linewidth=2.0)
    ax.plot(idx_b.index, idx_b, label=f"NIFTY 50 Benchmark (CAGR: 10.76%, Final: ₹{idx_b.iloc[-1]:,.0f})", color="#ff7043", linewidth=1.8, linestyle="--")

    ax.set_yscale("log")
    ax.set_title(f"Indexed Growth of ₹100: Reliance Industries vs NIFTY 50 (2000–2026 YTD)\nDaily Bars: N={n_days:,} sessions ({start_date_str} to {end_date_str})", fontsize=13, fontweight="bold", pad=12)
    ax.set_ylabel("Indexed Value (₹, Log Scale)", fontsize=11)
    ax.xaxis.set_major_locator(mdates.YearLocator(4))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.grid(True, which="both", linestyle=":", alpha=0.6)
    ax.legend(frameon=True, facecolor="#ffffff", framealpha=0.9, fontsize=10, loc="upper left")

    # Annotations for key shocks
    ax.annotate("2008 GFC Crash\n(-68.2% Drawdown)", xy=(pd.to_datetime("2008-10-24"), idx_p.loc["2008-10-24"]),
                xytext=(pd.to_datetime("2004-01-01"), 600),
                arrowprops=dict(facecolor="#d32f2f", arrowstyle="->", lw=1.2),
                fontsize=9, color="#d32f2f", fontweight="bold")
    ax.annotate("March 2020\nCOVID Shock\n(-44.1%)", xy=(pd.to_datetime("2020-03-23"), idx_p.loc["2020-03-23"]),
                xytext=(pd.to_datetime("2016-01-01"), 1500),
                arrowprops=dict(facecolor="#d32f2f", arrowstyle="->", lw=1.2),
                fontsize=9, color="#d32f2f", fontweight="bold")

    plt.tight_layout()
    s2_path = ASSETS_DIR / "slide02_price_growth.png"
    plt.savefig(s2_path)
    plt.close()
    print(f" -> Saved {s2_path}")

    # -------------------------------------------------------------
    # Slide 09: Return Histogram with Fitted Normal vs Student-t
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(10, 5.5), dpi=300)
    ret_vals = r_simple.values

    # Histogram
    counts, bins, _ = ax.hist(ret_vals, bins=120, density=True, alpha=0.45, color="#1e88e5", edgecolor="#1565c0", label="Empirical Daily Returns")

    # Fit Normal
    mu_norm, sigma_norm = stats.norm.fit(ret_vals)
    x_grid = np.linspace(-0.12, 0.12, 1000)
    pdf_norm = stats.norm.pdf(x_grid, loc=mu_norm, scale=sigma_norm)

    # Fit Student-t
    df_t, loc_t, scale_t = stats.t.fit(ret_vals)
    pdf_t = stats.t.pdf(x_grid, df=df_t, loc=loc_t, scale=scale_t)

    ax.plot(x_grid, pdf_norm, label=f"Normal Fit (AIC: -32,580.7, KS p: 1.8e-23)", color="#e53935", linestyle="--", linewidth=2.0)
    ax.plot(x_grid, pdf_t, label=f"Student-t Fit (df={df_t:.2f}, AIC: -33,890.9, KS p: 0.7796)", color="#2e7d32", linewidth=2.2)

    ax.set_xlim(-0.10, 0.10)
    ax.set_ylim(0, max(pdf_t) * 1.15)
    ax.set_title(f"Empirical Daily Return Distribution vs Parametric Fits (2000–2026 YTD)\nReliance Industries | N={len(ret_vals):,} returns | Excess Kurtosis = +8.45 (Fat Tails)", fontsize=12, fontweight="bold", pad=12)
    ax.set_xlabel("Daily Simple Return", fontsize=11)
    ax.set_ylabel("Probability Density", fontsize=11)
    ax.grid(True, linestyle=":", alpha=0.6)
    ax.legend(frameon=True, facecolor="#ffffff", framealpha=0.9, fontsize=10, loc="upper right")

    plt.tight_layout()
    s9_path = ASSETS_DIR / "slide09_return_histogram_fit.png"
    plt.savefig(s9_path)
    plt.close()
    print(f" -> Saved {s9_path}")

    # -------------------------------------------------------------
    # Slide 14: Q-Q Diagnostic Plot (Normal vs Student-t)
    # -------------------------------------------------------------
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.5), dpi=300)

    # Normal Q-Q
    norm_quantiles = stats.probplot(ret_vals, dist="norm", plot=None)
    osm_norm, osr_norm = norm_quantiles[0]
    ax1.scatter(osm_norm, osr_norm, alpha=0.4, color="#1e88e5", s=10, label="Daily Returns")
    slope_norm, intercept_norm, r_norm = norm_quantiles[1]
    ax1.plot(osm_norm, slope_norm * osm_norm + intercept_norm, color="#e53935", lw=2, label="Theoretical Normal")
    ax1.set_title("Normal Q-Q Plot: Severe S-Curve\n(Parametric Gaussian Rejection, p < 0.001)", fontsize=11, fontweight="bold")
    ax1.set_xlabel("Theoretical Standard Normal Quantiles", fontsize=10)
    ax1.set_ylabel("Sample Return Quantiles", fontsize=10)
    ax1.grid(True, linestyle=":", alpha=0.6)
    ax1.legend(loc="upper left")

    # Student-t Q-Q
    t_quantiles = stats.probplot(ret_vals, dist=stats.t(df=df_t), plot=None)
    osm_t, osr_t = t_quantiles[0]
    ax2.scatter(osm_t, osr_t, alpha=0.4, color="#2e7d32", s=10, label="Daily Returns")
    slope_t, intercept_t, r_t = t_quantiles[1]
    ax2.plot(osm_t, slope_t * osm_t + intercept_t, color="#1565c0", lw=2, label=f"Theoretical Student-t (df={df_t:.2f})")
    ax2.set_title(f"Student-t Q-Q Plot: Near-Linear Alignment\n(High Conformance, KS p = 0.7796)", fontsize=11, fontweight="bold")
    ax2.set_xlabel(f"Theoretical Student-t Quantiles (df={df_t:.2f})", fontsize=10)
    ax2.set_ylabel("Sample Return Quantiles", fontsize=10)
    ax2.grid(True, linestyle=":", alpha=0.6)
    ax2.legend(loc="upper left")

    fig.suptitle("Quantile-Quantile (Q-Q) Diagnostics: Gaussian vs Heavy-Tailed Student-t (2000–2026 YTD)", fontsize=13, fontweight="bold", y=0.98)
    plt.tight_layout()
    s14_path = ASSETS_DIR / "slide14_qq_diagnostic_plot.png"
    plt.savefig(s14_path)
    plt.close()
    print(f" -> Saved {s14_path}")

    # -------------------------------------------------------------
    # Slide 15: Drawdown Curve (2000-2026 YTD)
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(11, 5.5), dpi=300)
    cummax_p = p.cummax()
    dd_p = ((p - cummax_p) / cummax_p) * 100.0

    ax.plot(dd_p.index, dd_p, color="#c62828", linewidth=1.5, label="Reliance Drawdown (%)")
    ax.fill_between(dd_p.index, 0, dd_p, color="#ef5350", alpha=0.35)

    ax.set_title(f"Underwater Peak-to-Trough Drawdown Dynamics (2000–2026 YTD)\nReliance Industries | N={n_days:,} sessions | Max Drawdown = -68.18% (2008 GFC)", fontsize=12, fontweight="bold", pad=12)
    ax.set_ylabel("Drawdown from Historical Peak (%)", fontsize=11)
    ax.set_ylim(-75, 5)
    ax.xaxis.set_major_locator(mdates.YearLocator(4))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.grid(True, linestyle=":", alpha=0.6)
    ax.legend(loc="lower left", frameon=True, facecolor="#ffffff", framealpha=0.9)

    ax.annotate("2008 Financial Crisis Trough\n(-68.18% on 24-Oct-2008)\nRecovery: 3,462 days (Jul 2017)",
                xy=(pd.to_datetime("2008-10-24"), -68.18),
                xytext=(pd.to_datetime("2002-01-01"), -40),
                arrowprops=dict(facecolor="#b71c1c", arrowstyle="->", lw=1.3),
                fontsize=9, color="#b71c1c", fontweight="bold")
    ax.annotate("March 2020 COVID Crash\n(-44.08% on 23-Mar-2020)\nSwift Recovery: 139 days",
                xy=(pd.to_datetime("2020-03-23"), -44.08),
                xytext=(pd.to_datetime("2014-06-01"), -65),
                arrowprops=dict(facecolor="#b71c1c", arrowstyle="->", lw=1.3),
                fontsize=9, color="#b71c1c", fontweight="bold")

    plt.tight_layout()
    s15_path = ASSETS_DIR / "slide15_drawdown_risk.png"
    plt.savefig(s15_path)
    plt.close()
    print(f" -> Saved {s15_path}")

    # -------------------------------------------------------------
    # Slide 15 (Bonus): Period Comparison (2000-09 vs 2010-19 vs 2020-26 YTD)
    # -------------------------------------------------------------
    fig, ((ax_cagr, ax_vol), (ax_mdd, ax_aic)) = plt.subplots(2, 2, figsize=(11, 7.5), dpi=300)
    periods = ["2000–2009", "2010–2019", "2020–2026 YTD"]
    colors = ["#1976d2", "#388e3c", "#f57c00"]

    # Data
    cagrs = [33.13, 12.37, 9.84]
    vols = [40.56, 26.27, 27.86]
    mdds = [-68.18, -39.15, -44.08]
    t_dfs = [3.44, 7.15, 3.36]

    # Bar 1: CAGR
    ax_cagr.bar(periods, cagrs, color=colors, width=0.55)
    ax_cagr.set_title("Annualized Return (CAGR, %)", fontsize=11, fontweight="bold")
    ax_cagr.set_ylabel("CAGR (%)")
    for i, v in enumerate(cagrs):
        ax_cagr.text(i, v + 0.8, f"{v:.1f}%", ha="center", fontweight="bold")
    ax_cagr.set_ylim(0, 40)
    ax_cagr.grid(True, linestyle=":", alpha=0.6)

    # Bar 2: Volatility
    ax_vol.bar(periods, vols, color=colors, width=0.55)
    ax_vol.set_title("Annualized Volatility (%)", fontsize=11, fontweight="bold")
    ax_vol.set_ylabel("Volatility (%)")
    for i, v in enumerate(vols):
        ax_vol.text(i, v + 0.8, f"{v:.1f}%", ha="center", fontweight="bold")
    ax_vol.set_ylim(0, 48)
    ax_vol.grid(True, linestyle=":", alpha=0.6)

    # Bar 3: Max Drawdown
    ax_mdd.bar(periods, mdds, color="#d32f2f", width=0.55)
    ax_mdd.set_title("Maximum Peak-to-Trough Drawdown (%)", fontsize=11, fontweight="bold")
    ax_mdd.set_ylabel("Max Drawdown (%)")
    for i, v in enumerate(mdds):
        ax_mdd.text(i, v - 3.5, f"{v:.1f}%", ha="center", fontweight="bold", color="#d32f2f")
    ax_mdd.set_ylim(-80, 0)
    ax_mdd.grid(True, linestyle=":", alpha=0.6)

    # Bar 4: Student-t df (Tail Heaviness)
    ax_aic.bar(periods, t_dfs, color="#7b1fa2", width=0.55)
    ax_aic.set_title("Student-t Tail Parameter (ν degrees of freedom)", fontsize=11, fontweight="bold")
    ax_aic.set_ylabel("Estimated ν (Lower = Fatter Tails)")
    for i, v in enumerate(t_dfs):
        ax_aic.text(i, v + 0.2, f"ν = {v:.2f}", ha="center", fontweight="bold")
    ax_aic.set_ylim(0, 9)
    ax_aic.grid(True, linestyle=":", alpha=0.6)

    fig.suptitle("Cross-Period Structural Regime Comparison: Reliance Industries Across Decades", fontsize=13, fontweight="bold", y=0.99)
    plt.tight_layout()
    s_period_path = ASSETS_DIR / "slide15_period_comparison.png"
    plt.savefig(s_period_path)
    plt.close()
    print(f" -> Saved {s_period_path}")

    # -------------------------------------------------------------
    # Slide 16: CLT Convergence
    # -------------------------------------------------------------
    fig, axes = plt.subplots(1, 4, figsize=(14, 3.8), dpi=300)
    sample_sizes = [5, 10, 30, 50]
    rng = np.random.default_rng(42)

    for i, n_s in enumerate(sample_sizes):
        means = [float(np.mean(rng.choice(ret_vals, size=n_s, replace=True))) for _ in range(1500)]
        axes[i].hist(means, bins=35, density=True, color="#0288d1", alpha=0.6, edgecolor="#01579b")
        mu_m, std_m = np.mean(means), np.std(means)
        xm = np.linspace(mu_m - 3.5 * std_m, mu_m + 3.5 * std_m, 200)
        axes[i].plot(xm, stats.norm.pdf(xm, mu_m, std_m), color="#d32f2f", lw=2)
        axes[i].set_title(f"Sample Size n = {n_s}\nStd Err = {std_m:.4f}", fontsize=10, fontweight="bold")
        axes[i].set_xlabel("Sample Mean Return", fontsize=9)
        axes[i].grid(True, linestyle=":", alpha=0.5)

    fig.suptitle("Central Limit Theorem (CLT) Empirical Demonstration: Asymptotic Normality of Sample Means", fontsize=12, fontweight="bold", y=1.02)
    plt.tight_layout()
    s16_path = ASSETS_DIR / "slide16_clt_convergence.png"
    plt.savefig(s16_path)
    plt.close()
    print(f" -> Saved {s16_path}")

    print("All slide charts successfully generated!")


if __name__ == "__main__":
    generate_all_slide_charts()
