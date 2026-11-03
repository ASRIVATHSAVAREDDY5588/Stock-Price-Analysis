import json

with open('reports/project_computed_metrics.json') as f:
    d = json.load(f)

for k, v in d.items():
    lbl = v['period_label']
    s = v['start_date']
    e = v['end_date']
    td = v['trading_days']
    ro = v['return_observations']
    print(f"=== {lbl} ({s} to {e}, N={td} days, {ro} returns) ===")
    ast = v['asset']
    bmk = v['benchmark']
    capm = v['capm_relative']
    dist = v['distribution_fit']
    bt = v['backtest_strategy']
    print(f"  Asset CAGR: {ast['cagr']*100:.2f}%, Vol: {ast['annualized_volatility']*100:.2f}%, Skew: {ast['skewness']:.4f}, Kurt: {ast['excess_kurtosis']:.4f}")
    print(f"  MDD: {ast['max_drawdown']*100:.2f}% (Peak: {ast['mdd_peak_date']}, Trough: {ast['mdd_trough_date']}, Rec: {ast['mdd_recovery_date']}, Days: {ast['mdd_recovery_days']})")
    print(f"  VaR95 (Hist / Norm): {ast['var_95_hist']*100:.2f}% / {ast['var_95_norm']*100:.2f}%, ES95: {ast['es_95']*100:.2f}%")
    print(f"  VaR99 (Hist / Norm): {ast['var_99_hist']*100:.2f}% / {ast['var_99_norm']*100:.2f}%, ES99: {ast['es_99']*100:.2f}%")
    print(f"  Bmk CAGR: {bmk['cagr']*100:.2f}%, Vol: {bmk['annualized_volatility']*100:.2f}%, Beta: {capm['beta']:.2f}, Corr: {capm['correlation']:.2f}, Sharpe: {ast['sharpe_ratio']:.2f}")
    print(f"  Normal: LogLik: {dist['normal']['loglik']:.1f}, AIC: {dist['normal']['aic']:.1f}, KS-p: {dist['normal']['ks_p']:.4e}")
    print(f"  Student-t: df={dist['student_t']['df']:.2f}, LogLik: {dist['student_t']['loglik']:.1f}, AIC: {dist['student_t']['aic']:.1f}, KS-p: {dist['student_t']['ks_p']:.4f}, Delta AIC: {dist['delta_aic_t_vs_norm']:.1f}")
    print(f"  Strategy CAGR: {bt['strat_cagr']*100:.2f}%, Trades: {bt['trade_count']}, WinRate: {bt['win_rate']*100:.1f}%")
    print()
