"""Flask application entry point and REST API routes for Stock Market Distribution Analyzer."""

from __future__ import annotations

import os
# Prevent joblib core-count detection delay on Windows
os.environ.setdefault("LOKY_MAX_CPU_COUNT", str(os.cpu_count() or 4))

import io
import json
from typing import Any, Dict
import numpy as np
import pandas as pd
from flask import (
    Flask,
    Response,
    jsonify,
    render_template,
    request,
    send_file,
    send_from_directory,
)

from config import (
    ACTIVE_SAMPLE_PERIOD_LABEL,
    AI_CONFIGURED,
    CLEANED_DATA_DIR,
    DEBUG,
    DEFAULT_BENCHMARK,
    DEFAULT_BENCHMARKS,
    DEFAULT_END_DATE,
    DEFAULT_START_DATE,
    DEFAULT_TICKER,
    DEFAULT_TICKERS,
    HOST,
    LAST_TRADING_DATE,
    OPENAI_MODEL,
    PORT,
    PROJECT_ROOT,
    SAMPLE_DATA_DIR,
    SECRET_KEY,
    TRADING_DAYS_PER_YEAR,
)
from data.loader import load_dataset
from analytics.returns import compute_returns, compute_price_index
from analytics.statistics import compute_descriptive_statistics
from analytics.risk import (
    compute_var_and_es,
    compute_drawdown_series,
    compute_rolling_volatility,
    compute_benchmark_relative_risk,
)
from analytics.distributions import fit_distributions_and_tests
from analytics.sampling import run_bootstrap_simulation, run_clt_explorer
from analytics.backtest import run_walk_forward_backtest
from ai.service import ai_service
from ai.signal_generator import compute_deterministic_baseline_score
from reports.export import generate_returns_csv, generate_markdown_report


import threading

def execute_analysis_pipeline(
    source_type: str,
    ticker: str,
    benchmark_ticker: str,
    start_date: str,
    end_date: str | None,
    return_type: str,
    confidence_level: float,
    bootstrap_method: str,
    bootstrap_block_size: int,
    bootstrap_seed: int | None,
    csv_file=None,
) -> Dict[str, Any]:
    """Execute complete mathematical analysis pipeline for given parameters."""
    # 1. Load Data
    payload = load_dataset(
        source_type=source_type,
        ticker=ticker,
        benchmark_ticker=benchmark_ticker,
        start_date=start_date,
        end_date=end_date,
        csv_file=csv_file,
        seed=bootstrap_seed or 42,
    )

    stk_prices = payload.stock_df["Adj Close"]
    bmk_prices = payload.benchmark_df["Adj Close"] if not payload.benchmark_df.empty else None

    # 2. Return Calculations
    stk_ret_simple, stk_cum_ret_simple = compute_returns(stk_prices, return_type="simple")
    stk_ret_log, stk_cum_ret_log = compute_returns(stk_prices, return_type="log")

    active_ret = stk_ret_log if return_type == "log" else stk_ret_simple
    active_cum = stk_cum_ret_log if return_type == "log" else stk_cum_ret_simple

    if bmk_prices is not None:
        bmk_ret, _ = compute_returns(bmk_prices, return_type=return_type)
    else:
        bmk_ret = None

    # 3. Descriptive Statistics
    stats_dict = compute_descriptive_statistics(active_ret, prices=stk_prices)

    # 4. Risk Analytics
    var_es_dict = compute_var_and_es(active_ret, confidence_level=confidence_level)
    dd_series, dd_meta = compute_drawdown_series(stk_prices)
    rolling_vol_series = compute_rolling_volatility(active_ret, window=21)

    rel_risk_dict = {}
    if bmk_ret is not None:
        rel_risk_dict = compute_benchmark_relative_risk(active_ret, bmk_ret, stk_prices)

    risk_dict = {
        **var_es_dict,
        **dd_meta,
        **rel_risk_dict,
        "rolling_vol_min": float(rolling_vol_series.min()) if not rolling_vol_series.empty else 0.0,
        "rolling_vol_max": float(rolling_vol_series.max()) if not rolling_vol_series.empty else 0.0,
        "rolling_vol_current": float(rolling_vol_series.dropna().iloc[-1]) if not rolling_vol_series.dropna().empty else 0.0,
    }

    # 5. Distribution Fitting & Q-Q
    dist_dict = fit_distributions_and_tests(active_ret)

    # 6. Sampling & Bootstrap
    sampling_dict = run_bootstrap_simulation(
        active_ret,
        iterations=1000,
        confidence_level=confidence_level,
        method=bootstrap_method,
        block_size=bootstrap_block_size,
        seed=bootstrap_seed,
    )

    # CLT Explorer
    clt_dict = run_clt_explorer(active_ret, sample_sizes=[5, 10, 30, 50], seed=bootstrap_seed)

    # 7. Walk-Forward Backtest
    backtest_dict = run_walk_forward_backtest(stk_prices, bmk_prices)

    # Unified metadata
    meta_dict = payload.to_dict_summary()

    # Compile intermediate metric bundle for AI
    combined_metrics = {
        "meta": meta_dict,
        "statistics": stats_dict,
        "risk": risk_dict,
        "distribution": dist_dict,
        "sampling": sampling_dict,
    }

    # 8. Analysis Guide & Signal Generation
    guide_dict = ai_service.get_analysis_guide(combined_metrics)
    signal_dict = ai_service.generate_signal(combined_metrics, stk_prices, bmk_prices)

    # 9. Format Timeseries for Client Plotly Rendering (Downsample if > 800 points for speed)
    total_pts = len(active_ret)
    step = max(1, total_pts // 600)
    dates_sample = [d.strftime("%Y-%m-%d") for d in active_ret.index[::step]]
    prices_sample = [float(p) for p in stk_prices.loc[active_ret.index].iloc[::step]]
    ret_sample = [float(r) for r in active_ret.iloc[::step]]
    cum_sample = [float(c) for c in active_cum.iloc[::step]]
    dd_sample = [float(d) for d in dd_series.loc[active_ret.index].iloc[::step]]
    rollvol_sample = [
        float(v) if not pd.isna(v) else None
        for v in rolling_vol_series.loc[active_ret.index].iloc[::step]
    ]

    stk_idx = compute_price_index(stk_prices).loc[active_ret.index].iloc[::step]
    bmk_idx = (
        compute_price_index(bmk_prices).reindex(active_ret.index, method="ffill").iloc[::step]
        if bmk_prices is not None
        else None
    )

    timeseries_data = {
        "dates": dates_sample,
        "prices": prices_sample,
        "returns": ret_sample,
        "cumulative_returns": cum_sample,
        "drawdown": dd_sample,
        "rolling_vol": rollvol_sample,
        "stock_indexed": [float(x) for x in stk_idx],
        "benchmark_indexed": [float(x) for x in bmk_idx] if bmk_idx is not None else [],
    }

    # Return distribution histogram data (60 bins)
    hist_counts, hist_edges = np.histogram(active_ret.dropna().values, bins=60)
    hist_centers = (0.5 * (hist_edges[:-1] + hist_edges[1:])).tolist()

    return {
        "meta": meta_dict,
        "statistics": stats_dict,
        "risk": risk_dict,
        "distribution": dist_dict,
        "sampling": sampling_dict,
        "clt": clt_dict,
        "backtest": backtest_dict,
        "guide": guide_dict,
        "signal": signal_dict,
        "timeseries": timeseries_data,
        "histogram": {
            "counts": hist_counts.tolist(),
            "bin_centers": hist_centers,
        },
    }


def _prewarm_popular_cache(cache_ref: Dict[str, Any]) -> None:
    """Pre-warm popular Indian stocks in a background thread for instant < 1ms response."""
    def worker():
        popular = [
            "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS",
            "TATAMOTORS.NS", "ITC.NS", "SBIN.NS", "LT.NS", "BHARTIARTL.NS"
        ]
        for tick in popular:
            key = f"synthetic_{tick}_^NSEI_{DEFAULT_START_DATE}_{DEFAULT_END_DATE}_simple_0.95_iid_5_42"
            if key not in cache_ref:
                try:
                    res = execute_analysis_pipeline(
                        source_type="synthetic",
                        ticker=tick,
                        benchmark_ticker="^NSEI",
                        start_date=DEFAULT_START_DATE,
                        end_date=DEFAULT_END_DATE,
                        return_type="simple",
                        confidence_level=0.95,
                        bootstrap_method="iid",
                        bootstrap_block_size=5,
                        bootstrap_seed=42,
                    )
                    cache_ref[key] = res
                except Exception:
                    pass
    t = threading.Thread(target=worker, daemon=True)
    t.start()


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = SECRET_KEY
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB max upload
    
    # In-memory fast cache for instantaneous repeat calculations (< 2ms)
    query_cache: Dict[str, Any] = {}
    _prewarm_popular_cache(query_cache)

    @app.route("/")
    def index():
        return render_template(
            "index.html",
            default_tickers=DEFAULT_TICKERS,
            default_benchmarks=DEFAULT_BENCHMARKS,
            selected_ticker=DEFAULT_TICKER,
            selected_benchmark=DEFAULT_BENCHMARK,
            default_start_date=DEFAULT_START_DATE,
            default_end_date=DEFAULT_END_DATE,
            active_sample_period_label=ACTIVE_SAMPLE_PERIOD_LABEL,
            last_trading_date=LAST_TRADING_DATE,
            ai_configured=AI_CONFIGURED,
            openai_model=OPENAI_MODEL,
        )

    @app.route("/health")
    def health_check():
        return jsonify({"status": "ok", "app": "Stock Market Distribution Analyzer", "version": "1.0.0", "sample_period": ACTIVE_SAMPLE_PERIOD_LABEL, "last_trading_date": LAST_TRADING_DATE})

    @app.route("/api/analytics/periods", methods=["GET"])
    def get_period_comparisons():
        """Return recomputed multi-decade performance and distribution fits."""
        metrics_file = PROJECT_ROOT / "reports" / "project_computed_metrics.json"
        if metrics_file.exists():
            try:
                with open(metrics_file, "r", encoding="utf-8") as f:
                    return jsonify(json.load(f))
            except Exception as e:
                return jsonify({"error": f"Failed reading metrics: {str(e)}"}), 500
        return jsonify({"error": "Period metrics not yet computed. Run compute_full_project_metrics.py first."}), 404

    @app.route("/api/analyze", methods=["POST"])
    def analyze():
        """Primary analytics pipeline: loads data, runs stats, distributions, risk, and sampling."""
        try:
            # Check if multipart form (CSV upload) or JSON
            if request.content_type and "multipart/form-data" in request.content_type:
                form = request.form
                source_type = form.get("source", "synthetic")
                ticker = form.get("ticker", DEFAULT_TICKER).strip()
                benchmark_ticker = form.get("benchmark", DEFAULT_BENCHMARK).strip()
                start_date = form.get("start_date", DEFAULT_START_DATE)
                end_date = form.get("end_date", DEFAULT_END_DATE) or None
                return_type = form.get("return_type", "simple")
                confidence_level = float(form.get("confidence_level", "0.95"))
                bootstrap_method = form.get("bootstrap_method", "iid")
                bootstrap_block_size = int(form.get("bootstrap_block_size", "5"))
                bootstrap_seed = int(form.get("bootstrap_seed", "42")) if form.get("bootstrap_seed") else None
                csv_file = request.files.get("csv_file")
            else:
                body = request.get_json(force=True, silent=True) or {}
                source_type = body.get("source", "synthetic")
                ticker = body.get("ticker", DEFAULT_TICKER)
                benchmark_ticker = body.get("benchmark", DEFAULT_BENCHMARK)
                start_date = body.get("start_date", DEFAULT_START_DATE)
                end_date = body.get("end_date", DEFAULT_END_DATE) or None
                return_type = body.get("return_type", "simple")
                confidence_level = float(body.get("confidence_level", 0.95))
                bootstrap_method = body.get("bootstrap_method", "iid")
                bootstrap_block_size = int(body.get("bootstrap_block_size", 5))
                bootstrap_seed = int(body.get("bootstrap_seed", 42)) if body.get("bootstrap_seed") is not None else None
                csv_file = None

            cache_key = None
            if csv_file is None:
                cache_key = f"{source_type}_{ticker}_{benchmark_ticker}_{start_date}_{end_date}_{return_type}_{confidence_level}_{bootstrap_method}_{bootstrap_block_size}_{bootstrap_seed}"
                if cache_key in query_cache:
                    return jsonify(query_cache[cache_key])

            response_data = execute_analysis_pipeline(
                source_type=source_type,
                ticker=ticker,
                benchmark_ticker=benchmark_ticker,
                start_date=start_date,
                end_date=end_date,
                return_type=return_type,
                confidence_level=confidence_level,
                bootstrap_method=bootstrap_method,
                bootstrap_block_size=bootstrap_block_size,
                bootstrap_seed=bootstrap_seed,
                csv_file=csv_file,
            )

            if cache_key is not None:
                query_cache[cache_key] = response_data

            return jsonify(response_data)

        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            return jsonify({
                "error": str(e),
                "hint": "Check ticker symbol, choose synthetic demo data for offline testing, or inspect input CSV columns.",
                "traceback": tb if app.debug else None,
            }), 400

    @app.route("/api/export/csv", methods=["POST"])
    def export_csv():
        """Generate downloadable CSV of calculated returns and risk series."""
        try:
            req = request.get_json(force=True, silent=True) or {}
            source_type = req.get("source", "synthetic")
            ticker = req.get("ticker", DEFAULT_TICKER)
            benchmark_ticker = req.get("benchmark", DEFAULT_BENCHMARK)
            start_date = req.get("start_date", "2021-01-01")
            end_date = req.get("end_date") or None

            payload = load_dataset(
                source_type=source_type,
                ticker=ticker,
                benchmark_ticker=benchmark_ticker,
                start_date=start_date,
                end_date=end_date,
            )

            prices = payload.stock_df["Adj Close"]
            ret_simple, cum_simple = compute_returns(prices, "simple")
            ret_log, _ = compute_returns(prices, "log")
            dd, _ = compute_drawdown_series(prices)
            rvol = compute_rolling_volatility(ret_simple)

            csv_text = generate_returns_csv(prices, ret_simple, ret_log, cum_simple, dd, rvol)
            filename = f"{ticker.replace('^', '').replace('.', '_')}_returns.csv"

            return Response(
                csv_text,
                mimetype="text/csv",
                headers={"Content-Disposition": f"attachment;filename={filename}"},
            )
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    @app.route("/api/export/report", methods=["POST"])
    def export_report():
        """Generate downloadable Markdown analysis report."""
        try:
            req = request.get_json(force=True, silent=True) or {}
            metrics = req.get("metrics", {})
            signal = req.get("signal", {})
            guide = req.get("guide", {})
            backtest = req.get("backtest", {})

            md_content = generate_markdown_report(metrics, signal, guide, backtest)
            ticker = metrics.get("meta", {}).get("ticker", "stock").replace("^", "").replace(".", "_")
            filename = f"{ticker}_analysis_report.md"

            return Response(
                md_content,
                mimetype="text/markdown",
                headers={"Content-Disposition": f"attachment;filename={filename}"},
            )
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    @app.route("/api/sample-csv/<filename>")
    def download_sample_csv(filename: str):
        """Provide direct download of bundled sample CSV files."""
        safe_sample_files = ["reliance_sample.csv", "nifty50_sample.csv", "multi_stock_sample.csv"]
        safe_cleaned_files = ["reliance_cleaned_2000_2026.csv", "nifty50_cleaned_2000_2026.csv", "sensex_cleaned_2000_2026.csv"]
        if filename in safe_sample_files:
            return send_from_directory(SAMPLE_DATA_DIR, filename, as_attachment=True)
        elif filename in safe_cleaned_files:
            return send_from_directory(CLEANED_DATA_DIR, filename, as_attachment=True)
        return jsonify({"error": "File not found"}), 404

    return app


app = create_app()

if __name__ == "__main__":
    print(f"Starting Stock Market Distribution Analyzer on http://{HOST}:{PORT}")
    app.run(host=HOST, port=PORT, debug=DEBUG)
