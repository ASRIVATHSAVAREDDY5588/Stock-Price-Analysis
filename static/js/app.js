/**
 * Stock Market Distribution Analyzer - Interactive Client Controller
 * Provides both a clean, beginner-friendly Simple Overview and an advanced Quant Lab.
 */

document.addEventListener("DOMContentLoaded", function () {
    // Current analytical state
    let currentMetrics = null;
    let currentSignal = null;
    let currentGuide = null;
    let currentBacktest = null;
    let latestData = null;
    const renderedTabs = new Set();
    const clientCache = new Map(); // Blazing fast client-side cache
    let simpleChartMode = "growth"; // "growth" or "price"

    // Company Names Map
    const STOCK_NAMES = {
        "RELIANCE.NS": "Reliance Industries Ltd",
        "TCS.NS": "Tata Consultancy Services Ltd",
        "INFY.NS": "Infosys Ltd",
        "HDFCBANK.NS": "HDFC Bank Ltd",
        "ICICIBANK.NS": "ICICI Bank Ltd",
        "TATAMOTORS.NS": "Tata Motors Ltd",
        "ITC.NS": "ITC Ltd",
        "SBIN.NS": "State Bank of India",
        "LT.NS": "Larsen & Toubro Ltd",
        "BHARTIARTL.NS": "Bharti Airtel Ltd",
    };

    // UI Element References
    const form = document.getElementById("analyticsForm");
    const sourceSelect = document.getElementById("sourceSelect");
    const quickSourceSelect = document.getElementById("quickSourceSelect");
    const csvUploadGroup = document.getElementById("csvUploadGroup");
    const tickerSelect = document.getElementById("tickerSelect");
    const customTickerInput = document.getElementById("customTickerInput");
    const startDateInput = document.getElementById("startDate");
    const endDateInput = document.getElementById("endDate");
    const confidenceRange = document.getElementById("confidenceRange");
    const confidenceVal = document.getElementById("confidenceVal");
    const bootstrapToggle = document.getElementById("bootstrapToggle");
    const bootstrapBody = document.getElementById("bootstrapBody");
    const loadingOverlay = document.getElementById("loadingOverlay");
    const alertBanner = document.getElementById("alertBanner");
    const alertMessage = document.getElementById("alertMessage");
    const alertCloseBtn = document.getElementById("alertCloseBtn");
    const syntheticWatermark = document.getElementById("syntheticWatermark");

    // Mode Containers & Buttons
    const btnModeSimple = document.getElementById("btnModeSimple");
    const btnModeQuant = document.getElementById("btnModeQuant");
    const simpleViewContainer = document.getElementById("simpleViewContainer");
    const quantLabContainer = document.getElementById("quantLabContainer");
    const simpleGoToQuantBtn = document.getElementById("simpleGoToQuantBtn");

    // Chart toggle buttons in simple view
    const btnToggleChartGrowth = document.getElementById("btnToggleChartGrowth");
    const btnToggleChartPrice = document.getElementById("btnToggleChartPrice");

    // Common Plotly Layout Theme
    const plotlyFont = { family: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif", size: 11, color: "#334155" };
    const plotlyLayoutDefaults = {
        font: plotlyFont,
        margin: { l: 50, r: 25, t: 30, b: 40 },
        paper_bgcolor: "transparent",
        plot_bgcolor: "transparent",
        xaxis: { gridcolor: "#f1f5f9", zerolinecolor: "#cbd5e1" },
        yaxis: { gridcolor: "#f1f5f9", zerolinecolor: "#cbd5e1" },
        legend: { orientation: "h", y: -0.2, x: 0.1 },
        hovermode: "x unified",
    };

    // =========================================================================
    // 1. Navigation & View Mode Switching
    // =========================================================================
    function switchMode(mode) {
        if (mode === "quant") {
            btnModeQuant.classList.add("active");
            btnModeSimple.classList.remove("active");
            quantLabContainer.classList.remove("hidden");
            simpleViewContainer.classList.add("hidden");

            // Render current quant tab
            if (latestData) {
                const activeBtn = document.querySelector(".tab-btn.active");
                const activeTabId = activeBtn ? activeBtn.getAttribute("data-tab") : "tab-overview";
                renderSpecificQuantTab(activeTabId, latestData);
                renderedTabs.add(activeTabId);
            }
        } else {
            btnModeSimple.classList.add("active");
            btnModeQuant.classList.remove("active");
            simpleViewContainer.classList.remove("hidden");
            quantLabContainer.classList.add("hidden");

            // Render simple view
            if (latestData) {
                renderSimpleView(latestData);
            }
        }
        setTimeout(() => window.dispatchEvent(new Event("resize")), 50);
    }

    btnModeSimple.addEventListener("click", () => switchMode("simple"));
    btnModeQuant.addEventListener("click", () => switchMode("quant"));
    if (simpleGoToQuantBtn) {
        simpleGoToQuantBtn.addEventListener("click", () => switchMode("quant"));
    }

    // Quick Stock Chips
    document.querySelectorAll(".stock-chip").forEach((chip) => {
        chip.addEventListener("click", function () {
            document.querySelectorAll(".stock-chip").forEach((c) => c.classList.remove("active"));
            this.classList.add("active");

            const ticker = this.getAttribute("data-ticker");
            tickerSelect.value = ticker;
            customTickerInput.value = ticker;
            customTickerInput.classList.add("hidden");
            runAnalysis();
        });
    });

    // Time Horizon Quick Filters
    document.querySelectorAll(".btn-time").forEach((btn) => {
        btn.addEventListener("click", function () {
            document.querySelectorAll(".btn-time").forEach((b) => b.classList.remove("active"));
            this.classList.add("active");

            const years = parseFloat(this.getAttribute("data-years"));
            const end = new Date();
            const start = new Date();
            start.setDate(end.getDate() - Math.round(years * 365));

            startDateInput.value = start.toISOString().split("T")[0];
            endDateInput.value = end.toISOString().split("T")[0];
            runAnalysis();
        });
    });

    // Quick Source Select synchronization
    quickSourceSelect.addEventListener("change", function () {
        sourceSelect.value = this.value;
        if (this.value === "csv") {
            switchMode("quant");
            csvUploadGroup.classList.remove("hidden");
        } else {
            csvUploadGroup.classList.add("hidden");
            runAnalysis();
        }
    });

    sourceSelect.addEventListener("change", function () {
        quickSourceSelect.value = this.value;
        if (this.value === "csv") {
            csvUploadGroup.classList.remove("hidden");
        } else {
            csvUploadGroup.classList.add("hidden");
        }
    });

    tickerSelect.addEventListener("change", function () {
        if (this.value === "CUSTOM") {
            customTickerInput.classList.remove("hidden");
            customTickerInput.focus();
        } else {
            customTickerInput.classList.add("hidden");
            customTickerInput.value = this.value;
            // Update chip active status
            document.querySelectorAll(".stock-chip").forEach((c) => {
                c.classList.toggle("active", c.getAttribute("data-ticker") === this.value);
            });
        }
    });

    confidenceRange.addEventListener("input", function () {
        const pct = Math.round(parseFloat(this.value) * 100);
        confidenceVal.textContent = pct + "%";
    });

    if (bootstrapToggle && bootstrapBody) {
        bootstrapToggle.addEventListener("click", function () {
            bootstrapBody.classList.toggle("hidden");
        });
    }

    if (alertCloseBtn) {
        alertCloseBtn.addEventListener("click", () => alertBanner.classList.add("hidden"));
    }

    // Modal Handlers
    document.querySelectorAll(".help-link").forEach((link) => {
        link.addEventListener("click", function (e) {
            e.preventDefault();
            const modalId = this.getAttribute("data-modal");
            const modal = document.getElementById(modalId);
            if (modal) modal.classList.remove("hidden");
        });
    });

    document.querySelectorAll(".modal-close").forEach((btn) => {
        btn.addEventListener("click", function () {
            this.closest(".modal-overlay").classList.add("hidden");
        });
    });

    document.querySelectorAll(".modal-overlay").forEach((modal) => {
        modal.addEventListener("click", function (e) {
            if (e.target === this) this.classList.add("hidden");
        });
    });

    // Quant Tab Navigation with lazy rendering
    document.querySelectorAll(".tab-btn").forEach((btn) => {
        btn.addEventListener("click", function () {
            document.querySelectorAll(".tab-btn").forEach((b) => b.classList.remove("active"));
            document.querySelectorAll(".tab-content").forEach((c) => c.classList.remove("active"));

            this.classList.add("active");
            const targetId = this.getAttribute("data-tab");
            const targetContent = document.getElementById(targetId);
            if (targetContent) {
                targetContent.classList.add("active");
                if (latestData && !renderedTabs.has(targetId)) {
                    renderSpecificQuantTab(targetId, latestData);
                    renderedTabs.add(targetId);
                }
                setTimeout(() => window.dispatchEvent(new Event("resize")), 50);
            }
        });
    });

    function renderSpecificQuantTab(tabId, data) {
        if (tabId === "tab-overview") renderOverviewTab(data);
        else if (tabId === "tab-distribution") renderDistributionTab(data);
        else if (tabId === "tab-risk") renderRiskTab(data);
        else if (tabId === "tab-sampling") renderSamplingTab(data);
        else if (tabId === "tab-ai") renderAITab(data);
    }

    // Chart Toggle Buttons in Simple View
    if (btnToggleChartGrowth && btnToggleChartPrice) {
        btnToggleChartGrowth.addEventListener("click", function () {
            this.classList.add("active");
            btnToggleChartPrice.classList.remove("active");
            simpleChartMode = "growth";
            if (latestData) renderSimpleChart(latestData);
        });

        btnToggleChartPrice.addEventListener("click", function () {
            this.classList.add("active");
            btnToggleChartGrowth.classList.remove("active");
            simpleChartMode = "price";
            if (latestData) renderSimpleChart(latestData);
        });
    }

    // =========================================================================
    // 2. Main Analysis Pipeline & Fast Progress
    // =========================================================================
    form.addEventListener("submit", function (e) {
        e.preventDefault();
        runAnalysis(false);
    });

    function startFastProgress() {
        const bar = document.getElementById("topProgressBar");
        if (bar) {
            bar.style.width = "35%";
            bar.classList.add("active");
            setTimeout(() => {
                if (bar.classList.contains("active")) bar.style.width = "75%";
            }, 60);
        }
    }

    function finishFastProgress() {
        const bar = document.getElementById("topProgressBar");
        if (bar) {
            bar.style.width = "100%";
            setTimeout(() => {
                bar.classList.remove("active");
                bar.style.width = "0%";
            }, 120);
        }
    }

    function runAnalysis(useOverlay = false) {
        alertBanner.classList.add("hidden");

        const formData = new FormData(form);

        // Resolve ticker
        let ticker = tickerSelect.value;
        if (tickerSelect.value !== "CUSTOM") {
            formData.set("ticker", tickerSelect.value);
        } else {
            ticker = customTickerInput.value.trim();
            formData.set("ticker", ticker);
        }

        const source = formData.get("source") || "synthetic";
        const start = formData.get("start_date") || "";
        const end = formData.get("end_date") || "";
        const bmk = formData.get("benchmark") || "";
        const retType = formData.get("return_type") || "simple";
        const conf = formData.get("confidence_level") || "0.95";
        const csvInput = document.getElementById("csvFileInput");
        const hasFile = source === "csv" && csvInput && csvInput.files && csvInput.files.length > 0;
        const cacheKey = !hasFile ? `${source}_${ticker}_${bmk}_${start}_${end}_${retType}_${conf}` : null;

        // 1. Instant 0ms render from Client Cache if already visited
        if (cacheKey && clientCache.has(cacheKey)) {
            const cachedData = clientCache.get(cacheKey);
            renderAllResults(cachedData);
            return;
        }

        // 2. Visual feedback
        if (useOverlay) {
            showLoading("Analyzing stock returns...");
        } else {
            startFastProgress();
        }

        fetch("/api/analyze", {
            method: "POST",
            body: formData,
        })
            .then(async (res) => {
                const data = await res.json();
                if (!res.ok) {
                    throw new Error(data.error || "Failed to execute statistical calculations.");
                }
                return data;
            })
            .then((data) => {
                finishFastProgress();
                hideLoading();
                if (cacheKey) {
                    clientCache.set(cacheKey, data);
                }
                renderAllResults(data);
            })
            .catch((err) => {
                finishFastProgress();
                hideLoading();
                showError(err.message);
            });
    }

    function showLoading(msg) {
        document.getElementById("loadingStatusText").textContent = msg;
        loadingOverlay.classList.remove("hidden");
    }

    function hideLoading() {
        loadingOverlay.classList.add("hidden");
    }

    function showError(msg) {
        alertMessage.textContent = msg;
        alertBanner.classList.remove("hidden");
        window.scrollTo({ top: 0, behavior: "smooth" });
    }

    // =========================================================================
    // 3. Render Results Pipeline
    // =========================================================================
    function renderAllResults(data) {
        latestData = data;
        renderedTabs.clear();

        currentMetrics = {
            meta: data.meta,
            statistics: data.statistics,
            risk: data.risk,
            distribution: data.distribution,
            sampling: data.sampling,
        };
        currentSignal = data.signal;
        currentGuide = data.guide;
        currentBacktest = data.backtest;

        updateHeaderStatus(data.meta);
        updateKeyRibbon(data.statistics, data.risk);

        // Render Simple View (always kept up-to-date)
        renderSimpleView(data);

        // If Quant Lab is currently visible, render the active quant tab
        if (!quantLabContainer.classList.contains("hidden")) {
            const activeBtn = document.querySelector(".tab-btn.active");
            const activeTabId = activeBtn ? activeBtn.getAttribute("data-tab") : "tab-overview";
            renderSpecificQuantTab(activeTabId, data);
            renderedTabs.add(activeTabId);
        }
    }

    // Header Badges
    function updateHeaderStatus(meta) {
        const srcBadge = document.getElementById("headerSourceBadge");
        srcBadge.textContent = meta.is_synthetic ? "SYNTHETIC DEMO" : meta.source.toUpperCase();
        srcBadge.className = "badge " + (meta.is_synthetic ? "badge-synthetic" : "badge-ticker");

        document.getElementById("headerTickerBadge").textContent = meta.ticker;
        document.getElementById("headerBenchmarkBadge").textContent = meta.benchmark_ticker;
        document.getElementById("headerLastUpdated").textContent = "Updated: " + (meta.last_updated || "Just now");

        if (meta.is_synthetic) {
            syntheticWatermark.classList.remove("hidden");
        } else {
            syntheticWatermark.classList.add("hidden");
        }
    }

    // =========================================================================
    // 4. Render Simple Overview (Clean & Friendly)
    // =========================================================================
    function renderSimpleView(data) {
        const stats = data.statistics;
        const risk = data.risk;
        const ts = data.timeseries;
        const sig = data.signal;

        // 1. Spotlight Header
        const ticker = data.meta.ticker;
        const companyName = STOCK_NAMES[ticker] || (ticker.replace(".NS", "").replace(".BO", "") + " Ltd");
        document.getElementById("simpleTickerLabel").textContent = ticker;
        document.getElementById("simpleStockName").textContent = companyName;
        document.getElementById("simpleDateRange").textContent = data.meta.date_range;

        // Current Price
        const latestPrice = ts.prices && ts.prices.length > 0 ? ts.prices[ts.prices.length - 1] : 0;
        document.getElementById("simpleCurrentPrice").textContent = "\u20b9" + latestPrice.toLocaleString("en-IN", { minimumFractionDigits: 2, maximumFractionDigits: 2 });

        // Total Growth
        const totGrowth = stats.cumulative_return * 100;
        const growthEl = document.getElementById("simpleTotalGrowth");
        growthEl.textContent = (totGrowth >= 0 ? "+" : "") + totGrowth.toFixed(1) + "%";
        growthEl.style.color = totGrowth >= 0 ? "#15803d" : "#b91c1c";

        // Plain English Risk Rating
        const annVol = stats.annual_volatility;
        const riskPill = document.getElementById("simpleRiskPill");
        if (annVol < 0.18) {
            riskPill.textContent = "Low Risk";
            riskPill.className = "risk-pill pill-low";
        } else if (annVol <= 0.28) {
            riskPill.textContent = "Moderate Risk";
            riskPill.className = "risk-pill pill-moderate";
        } else {
            riskPill.textContent = "Higher Risk";
            riskPill.className = "risk-pill pill-high";
        }

        // 2. Four Friendly Cards
        document.getElementById("simpleCAGR").textContent = (stats.cagr * 100).toFixed(1) + "% / yr";
        document.getElementById("simpleVolatility").textContent = (annVol * 100).toFixed(1) + "%";
        document.getElementById("simpleVaR").textContent = (risk.historical_var * 100).toFixed(1) + "%";
        document.getElementById("simpleMaxDD").textContent = (risk.max_drawdown * 100).toFixed(1) + "%";

        // 3. Simple Chart
        renderSimpleChart(data);

        // 4. Simple AI Card
        const sigBadge = document.getElementById("simpleSignalBadge");
        sigBadge.textContent = sig.signal;
        sigBadge.className = "signal-pill " + (sig.signal === "BUY" ? "pill-buy" : sig.signal === "SELL" ? "pill-sell" : "pill-hold");

        document.getElementById("simpleConfidenceBadge").textContent = "Evidence Quality: " + (sig.confidence || "MEDIUM").replace("_", " ");
        document.getElementById("simpleScoreVal").textContent = (sig.deterministic_baseline ? sig.deterministic_baseline.baseline_score : "0.00");
        document.getElementById("simpleRationaleText").textContent = sig.rationale;

        // Supporting factors list
        const supList = document.getElementById("simpleSupportingList");
        supList.innerHTML = "";
        (sig.supporting_metrics || []).slice(0, 3).forEach((item) => {
            const li = document.createElement("li");
            li.textContent = item;
            supList.appendChild(li);
        });

        // Counter evidence list
        const countList = document.getElementById("simpleCounterList");
        countList.innerHTML = "";
        (sig.counter_evidence || []).slice(0, 2).forEach((item) => {
            const li = document.createElement("li");
            li.textContent = item;
            countList.appendChild(li);
        });
    }

    function renderSimpleChart(data) {
        const ts = data.timeseries;

        let traces = [];
        let yTitle = "";

        if (simpleChartMode === "price") {
            traces.push({
                x: ts.dates,
                y: ts.prices,
                type: "scatter",
                mode: "lines",
                name: data.meta.ticker + " Price (\u20b9)",
                line: { color: "#4338ca", width: 2.5 },
                fill: "tozeroy",
                fillcolor: "rgba(67, 56, 202, 0.05)",
            });
            yTitle = "Price in \u20b9";
        } else {
            // Growth comparison (Base 100)
            traces.push({
                x: ts.dates,
                y: ts.stock_indexed,
                type: "scatter",
                mode: "lines",
                name: data.meta.ticker + " Growth",
                line: { color: "#4338ca", width: 2.5 },
            });
            if (ts.benchmark_indexed && ts.benchmark_indexed.length > 0) {
                traces.push({
                    x: ts.dates,
                    y: ts.benchmark_indexed,
                    type: "scatter",
                    mode: "lines",
                    name: "NIFTY 50 Benchmark",
                    line: { color: "#0284c7", width: 2, dash: "dot" },
                });
            }
            yTitle = "Growth (\u20b9100 Base)";
        }

        const layout = {
            ...plotlyLayoutDefaults,
            height: 380,
            yaxis: { title: yTitle, gridcolor: "#f1f5f9" },
            legend: { orientation: "h", y: -0.15, x: 0.1 },
        };

        Plotly.react("simpleInteractiveChart", traces, layout, { responsive: true, displayModeBar: false });
    }

    // =========================================================================
    // 5. Quant Lab Renderers (Advanced Analytical Tools)
    // =========================================================================
    function updateKeyRibbon(stats, risk) {
        const annRet = (stats.annual_mean_compound * 100).toFixed(2) + "%";
        const dailyRet = (stats.mean_daily * 100).toFixed(3) + "%";
        const annVol = (stats.annual_volatility * 100).toFixed(2) + "%";
        const var95 = (risk.historical_var * 100).toFixed(2) + "%";
        const es95 = (risk.expected_shortfall * 100).toFixed(2) + "%";
        const maxDD = (risk.max_drawdown * 100).toFixed(2) + "%";
        const beta = risk.beta ? risk.beta.toFixed(2) : "1.00";
        const corr = risk.correlation ? risk.correlation.toFixed(2) : "0.00";

        document.getElementById("metricAnnRet").textContent = annRet;
        document.getElementById("metricMeanDaily").textContent = "Daily mean: " + dailyRet;
        document.getElementById("metricAnnVol").textContent = annVol;
        document.getElementById("metricVaR").textContent = var95;
        document.getElementById("metricES").textContent = es95;
        document.getElementById("metricMaxDD").textContent = maxDD;
        document.getElementById("metricDDDuration").textContent = "Trough: " + (risk.trough_date || "--");
        document.getElementById("metricBeta").textContent = beta;
        document.getElementById("metricCorr").textContent = "Corr (\u03c1): " + corr;
    }

    // Tab 1: Overview
    function renderOverviewTab(data) {
        const ts = data.timeseries;
        const stats = data.statistics;

        document.getElementById("chartDateRangeBadge").textContent = data.meta.date_range;

        const traceStock = {
            x: ts.dates,
            y: ts.stock_indexed,
            type: "scatter",
            mode: "lines",
            name: data.meta.ticker + " (Base 100)",
            line: { color: "#4338ca", width: 2.2 },
        };

        const traces = [traceStock];
        if (ts.benchmark_indexed && ts.benchmark_indexed.length > 0) {
            traces.push({
                x: ts.dates,
                y: ts.benchmark_indexed,
                type: "scatter",
                mode: "lines",
                name: data.meta.benchmark_ticker + " (Benchmark Base 100)",
                line: { color: "#0284c7", width: 1.8, dash: "dot" },
            });
        }

        const layoutComp = {
            ...plotlyLayoutDefaults,
            yaxis: { title: "Indexed Level (\u20b9100 Base)" },
        };
        Plotly.react("priceComparisonChart", traces, layoutComp, { responsive: true, displayModeBar: false });

        const traceCum = {
            x: ts.dates,
            y: ts.cumulative_returns.map((v) => v * 100),
            type: "scatter",
            mode: "lines",
            fill: "tozeroy",
            fillcolor: "rgba(67, 56, 202, 0.08)",
            name: "Cumulative Return (%)",
            line: { color: "#4338ca", width: 1.8 },
        };
        const layoutCum = {
            ...plotlyLayoutDefaults,
            yaxis: { title: "Cumulative Growth (%)" },
        };
        Plotly.react("cumulativeReturnChart", [traceCum], layoutCum, { responsive: true, displayModeBar: false });

        // Descriptive Stats Table
        document.getElementById("statObsCount").textContent = "N = " + stats.count + " sessions";
        document.getElementById("statDailyMean").textContent = (stats.mean_daily * 100).toFixed(4) + "%";
        document.getElementById("statDailyMedian").textContent = (stats.median_daily * 100).toFixed(4) + "%";
        document.getElementById("statDailyStd").textContent = (stats.std_daily * 100).toFixed(4) + "%";
        document.getElementById("statDailyVar").textContent = stats.variance_daily.toExponential(4);
        document.getElementById("statSkewness").textContent = stats.skewness.toFixed(4);
        document.getElementById("statKurtosis").textContent = stats.excess_kurtosis.toFixed(4);
        document.getElementById("statMinMax").textContent = (stats.min * 100).toFixed(2) + "% / " + (stats.max * 100).toFixed(2) + "%";
        document.getElementById("statCAGR").textContent = (stats.cagr * 100).toFixed(2) + "%";
        document.getElementById("statCumReturn").textContent = (stats.cumulative_return * 100).toFixed(2) + "%";
        document.getElementById("statAnnualConvention").textContent = stats.annualization_convention;
    }

    // Tab 2: Distribution
    function renderDistributionTab(data) {
        const hist = data.histogram;
        const dist = data.distribution;

        const traceHist = {
            x: hist.bin_centers,
            y: hist.counts,
            type: "bar",
            name: "Empirical Frequencies",
            marker: { color: "#cbd5e1" },
            opacity: 0.7,
        };

        const binWidth = hist.bin_centers.length > 1 ? hist.bin_centers[1] - hist.bin_centers[0] : 0.01;
        const totalN = data.statistics.count;
        const scaleFactor = totalN * binWidth;

        const traceNormPDF = {
            x: dist.density_curves.x_grid,
            y: dist.density_curves.norm_pdf.map((p) => p * scaleFactor),
            type: "scatter",
            mode: "lines",
            name: "Fitted Normal PDF",
            line: { color: "#dc2626", width: 2, dash: "dash" },
        };

        const traceTPDF = {
            x: dist.density_curves.x_grid,
            y: dist.density_curves.t_pdf.map((p) => p * scaleFactor),
            type: "scatter",
            mode: "lines",
            name: "Fitted Student-t PDF (\u03bd=" + dist.student_t.df.toFixed(1) + ")",
            line: { color: "#059669", width: 2.2 },
        };

        const layoutHist = {
            ...plotlyLayoutDefaults,
            xaxis: { title: "Daily Return" },
            yaxis: { title: "Observation Count" },
        };
        Plotly.react("histogramFitChart", [traceHist, traceNormPDF, traceTPDF], layoutHist, { responsive: true, displayModeBar: false });

        // Q-Q Diagnostic Plot
        const qq = dist.qq_plot;
        const traceEmpVsNorm = {
            x: qq.norm_theoretical,
            y: qq.sample_quantiles,
            type: "scatter",
            mode: "markers",
            name: "Normal Q-Q Points",
            marker: { color: "#dc2626", size: 5, symbol: "circle" },
        };

        const traceEmpVsT = {
            x: qq.t_theoretical,
            y: qq.sample_quantiles,
            type: "scatter",
            mode: "markers",
            name: "Student-t Q-Q Points",
            marker: { color: "#059669", size: 5, symbol: "diamond" },
        };

        const minQ = Math.min(...qq.sample_quantiles);
        const maxQ = Math.max(...qq.sample_quantiles);
        const traceLine = {
            x: [minQ, maxQ],
            y: [minQ, maxQ],
            type: "scatter",
            mode: "lines",
            name: "Theoretical 45\u00b0 Line",
            line: { color: "#94a3b8", width: 1.5, dash: "dot" },
        };

        const layoutQQ = {
            ...plotlyLayoutDefaults,
            xaxis: { title: "Theoretical Quantiles" },
            yaxis: { title: "Empirical Sample Quantiles" },
        };
        Plotly.react("qqPlotChart", [traceEmpVsNorm, traceEmpVsT, traceLine], layoutQQ, { responsive: true, displayModeBar: false });

        // Model Comparison Table
        document.getElementById("preferredModelBadge").textContent = "Preferred Model: " + dist.model_comparison.preferred_model_by_aic;
        document.getElementById("normLogLik").textContent = dist.normal.log_likelihood.toFixed(1);
        document.getElementById("normAIC").textContent = dist.normal.aic.toFixed(1);
        document.getElementById("normBIC").textContent = dist.normal.bic.toFixed(1);
        document.getElementById("normParams").textContent = "\u03bc=" + (dist.normal.mu * 100).toFixed(2) + "%, \u03c3=" + (dist.normal.sigma * 100).toFixed(2) + "%";
        document.getElementById("normKSp").textContent = dist.normal.ks_p_value.toFixed(4);

        document.getElementById("tLogLik").textContent = dist.student_t.log_likelihood.toFixed(1);
        document.getElementById("tAIC").textContent = dist.student_t.aic.toFixed(1);
        document.getElementById("tBIC").textContent = dist.student_t.bic.toFixed(1);
        document.getElementById("tParams").textContent = "\u03bd=" + dist.student_t.df.toFixed(2) + ", loc=" + (dist.student_t.loc * 100).toFixed(2) + "%, scale=" + (dist.student_t.scale * 100).toFixed(2) + "%";
        document.getElementById("tKSp").textContent = dist.student_t.ks_p_value.toFixed(4);

        document.getElementById("jbResultText").textContent = dist.plain_language.jarque_bera;
        document.getElementById("dfResultText").textContent = dist.plain_language.degrees_of_freedom;
        document.getElementById("gmmResultText").textContent = dist.gmm.description || "GMM calculation completed.";
    }

    // Tab 3: Risk & Backtesting
    function renderRiskTab(data) {
        const ts = data.timeseries;
        const bt = data.backtest;

        const traceDD = {
            x: ts.dates,
            y: ts.drawdown.map((d) => d * 100),
            type: "scatter",
            mode: "lines",
            fill: "tozeroy",
            fillcolor: "rgba(220, 38, 38, 0.12)",
            name: "Drawdown (%)",
            line: { color: "#dc2626", width: 1.8 },
        };
        const layoutDD = {
            ...plotlyLayoutDefaults,
            yaxis: { title: "Drawdown (%)", range: [-60, 5] },
        };
        Plotly.react("drawdownChart", [traceDD], layoutDD, { responsive: true, displayModeBar: false });

        const traceRVol = {
            x: ts.dates,
            y: ts.rolling_vol.map((v) => (v !== null ? v * 100 : null)),
            type: "scatter",
            mode: "lines",
            name: "Rolling 21-Day Vol (Ann %)",
            line: { color: "#d97706", width: 1.8 },
        };
        const layoutRVol = {
            ...plotlyLayoutDefaults,
            yaxis: { title: "Annualized Volatility (%)" },
        };
        Plotly.react("rollingVolChart", [traceRVol], layoutRVol, { responsive: true, displayModeBar: false });

        if (bt && bt.equity_curve) {
            const eq = bt.equity_curve;
            const traceStrat = {
                x: eq.dates,
                y: eq.strategy,
                type: "scatter",
                mode: "lines",
                name: "Trend Strategy (Zero Lookahead)",
                line: { color: "#059669", width: 2.2 },
            };
            const traceBuyHold = {
                x: eq.dates,
                y: eq.stock_buy_hold,
                type: "scatter",
                mode: "lines",
                name: "Stock Buy & Hold",
                line: { color: "#4338ca", width: 1.6, dash: "dot" },
            };
            const traceBmk = {
                x: eq.dates,
                y: eq.benchmark,
                type: "scatter",
                mode: "lines",
                name: "Benchmark Index",
                line: { color: "#64748b", width: 1.4, dash: "dash" },
            };

            const layoutBT = {
                ...plotlyLayoutDefaults,
                yaxis: { title: "Equity Growth Factor" },
            };
            Plotly.react("backtestEquityChart", [traceStrat, traceBuyHold, traceBmk], layoutBT, { responsive: true, displayModeBar: false });

            document.getElementById("btStratCAGR").textContent = (bt.strategy_performance.cagr * 100).toFixed(1) + "%";
            document.getElementById("btStockCAGR").textContent = (bt.buy_and_hold_stock.cagr * 100).toFixed(1) + "%";
            document.getElementById("btStratMaxDD").textContent = (bt.strategy_performance.max_drawdown * 100).toFixed(1) + "%";
            document.getElementById("btWinRate").textContent = (bt.trades.active_day_win_rate * 100).toFixed(1) + "%";
            document.getElementById("btTrades").textContent = bt.trades.total_trades;
        }
    }

    // Tab 4: Sampling & CLT
    function renderSamplingTab(data) {
        const samp = data.sampling;
        const clt = data.clt;

        document.getElementById("bootstrapMethodBadge").textContent =
            samp.method.toUpperCase() + " Bootstrap \u2022 Iterations: " + samp.iterations + " \u2022 Seed: " + (samp.seed || "None");

        function plotMiniHist(divId, metricObj, isPct) {
            const hist = metricObj.histogram;
            const trace = {
                x: hist.bin_centers.map((x) => (isPct ? x * 100 : x)),
                y: hist.counts,
                type: "bar",
                marker: { color: "#4338ca" },
            };
            const layout = {
                ...plotlyLayoutDefaults,
                margin: { l: 30, r: 15, t: 15, b: 25 },
                xaxis: { title: "" },
                yaxis: { title: "" },
            };
            Plotly.react(divId, [trace], layout, { responsive: true, displayModeBar: false });
        }

        plotMiniHist("bootMeanChart", samp.mean_return, true);
        document.getElementById("bootMeanCI").textContent =
            "Point: " + (samp.mean_return.point_estimate * 100).toFixed(3) + "% | 95% CI: [" +
            (samp.mean_return.ci_lower * 100).toFixed(3) + "%, " + (samp.mean_return.ci_upper * 100).toFixed(3) + "%]";

        plotMiniHist("bootVolChart", samp.annual_volatility, true);
        document.getElementById("bootVolCI").textContent =
            "Point: " + (samp.annual_volatility.point_estimate * 100).toFixed(2) + "% | 95% CI: [" +
            (samp.annual_volatility.ci_lower * 100).toFixed(2) + "%, " + (samp.annual_volatility.ci_upper * 100).toFixed(2) + "%]";

        plotMiniHist("bootVaRChart", samp.var_95, true);
        document.getElementById("bootVaRCI").textContent =
            "Point: " + (samp.var_95.point_estimate * 100).toFixed(2) + "% | 95% CI: [" +
            (samp.var_95.ci_lower * 100).toFixed(2) + "%, " + (samp.var_95.ci_upper * 100).toFixed(2) + "%]";

        const cltGrid = document.getElementById("cltGrid");
        cltGrid.innerHTML = "";

        if (clt && clt.sample_sizes) {
            Object.keys(clt.sample_sizes).forEach((sizeKey) => {
                const sObj = clt.sample_sizes[sizeKey];
                const colDiv = document.createElement("div");
                colDiv.className = "card subcard";
                const plotId = "clt_plot_" + sizeKey;
                colDiv.innerHTML = `
                    <h4>Sample Size n = ${sObj.n}</h4>
                    <div id="${plotId}" class="plot-container-xs"></div>
                    <div class="ci-summary">
                        <strong>Skew:</strong> ${sObj.skewness.toFixed(3)} | <strong>Kurt:</strong> ${sObj.excess_kurtosis.toFixed(3)}<br>
                        <strong>Sim SE:</strong> ${(sObj.simulated_se * 100).toFixed(3)}% (Theo: ${(sObj.theoretical_se * 100).toFixed(3)}%)
                    </div>
                `;
                cltGrid.appendChild(colDiv);

                const traceCLT = {
                    x: sObj.histogram.bin_centers.map((x) => x * 100),
                    y: sObj.histogram.counts,
                    type: "bar",
                    marker: { color: sObj.n >= 30 ? "#059669" : "#0284c7" },
                };
                const layoutCLT = {
                    ...plotlyLayoutDefaults,
                    margin: { l: 25, r: 10, t: 15, b: 25 },
                    xaxis: { title: "Sample Mean (%)" },
                    yaxis: { title: "" },
                };
                Plotly.react(plotId, [traceCLT], layoutCLT, { responsive: true, displayModeBar: false });
            });
        }
    }

    // Tab 5: AI Insights
    function renderAITab(data) {
        const sig = data.signal;
        const guide = data.guide;

        const sigBadge = document.getElementById("signalBadge");
        sigBadge.textContent = sig.signal;
        sigBadge.className = "signal-pill " + (sig.signal === "BUY" ? "pill-buy" : sig.signal === "SELL" ? "pill-sell" : "pill-hold");

        document.getElementById("confidenceBadge").textContent = "Confidence: " + (sig.confidence || "LOW").replace("_", " ");

        if (sig.deterministic_baseline) {
            document.getElementById("baselineScoreVal").textContent = sig.deterministic_baseline.baseline_score;
            document.getElementById("baselineSignalVal").textContent = "(" + sig.deterministic_baseline.baseline_signal + ")";
        }

        document.getElementById("signalRationale").textContent = sig.rationale;

        const supList = document.getElementById("supportingMetricsList");
        supList.innerHTML = "";
        (sig.supporting_metrics || []).forEach((m) => {
            const li = document.createElement("li");
            li.textContent = m;
            supList.appendChild(li);
        });

        const countList = document.getElementById("counterEvidenceList");
        countList.innerHTML = "";
        (sig.counter_evidence || []).forEach((c) => {
            const li = document.createElement("li");
            li.textContent = c;
            countList.appendChild(li);
        });

        document.getElementById("signalRiskNotes").textContent = sig.risk_notes;
        document.getElementById("signalDisclaimer").textContent = sig.disclaimer;

        const guideContainer = document.getElementById("guideItemsContainer");
        guideContainer.innerHTML = "";
        document.getElementById("guideEngineBadge").textContent = guide.engine || "Grounded Evidence Engine";

        (guide.guidance_items || []).forEach((item, idx) => {
            const card = document.createElement("div");
            card.className = "guide-item-card";
            card.innerHTML = `
                <div class="guide-item-title">${idx + 1}. ${item.step_title}</div>
                <div class="guide-item-trigger">Trigger: ${item.trigger_evidence}</div>
                <div class="guide-item-rec">${item.recommendation}</div>
            `;
            guideContainer.appendChild(card);
        });
    }

    // =========================================================================
    // 6. Export Handlers
    // =========================================================================
    function triggerCsvExport() {
        if (!currentMetrics) return;
        const reqPayload = {
            source: sourceSelect.value,
            ticker: tickerSelect.value !== "CUSTOM" ? tickerSelect.value : customTickerInput.value.trim(),
            benchmark: document.getElementById("benchmarkSelect").value,
            start_date: startDateInput.value,
            end_date: endDateInput.value || null,
        };

        fetch("/api/export/csv", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(reqPayload),
        })
            .then((res) => res.blob())
            .then((blob) => {
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement("a");
                a.href = url;
                a.download = (reqPayload.ticker.replace(".", "_") || "stock") + "_returns.csv";
                document.body.appendChild(a);
                a.click();
                a.remove();
            })
            .catch((err) => showError("Export failed: " + err.message));
    }

    function triggerReportExport() {
        if (!currentMetrics) return;
        const reqPayload = {
            metrics: currentMetrics,
            signal: currentSignal,
            guide: currentGuide,
            backtest: currentBacktest,
        };

        fetch("/api/export/report", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(reqPayload),
        })
            .then((res) => res.blob())
            .then((blob) => {
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement("a");
                a.href = url;
                a.download = (currentMetrics.meta.ticker.replace(".", "_") || "stock") + "_analysis_report.md";
                document.body.appendChild(a);
                a.click();
                a.remove();
            })
            .catch((err) => showError("Report download failed: " + err.message));
    }

    document.getElementById("exportCsvBtn").addEventListener("click", triggerCsvExport);
    document.getElementById("exportReportBtn").addEventListener("click", triggerReportExport);
    document.getElementById("simpleExportCsvBtn").addEventListener("click", triggerCsvExport);
    document.getElementById("simpleExportReportBtn").addEventListener("click", triggerReportExport);

    // Initial Execution on Page Load
    runAnalysis();
});
