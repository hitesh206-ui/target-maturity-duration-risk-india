# Paper Readiness Criteria

## Current Status

The repository infrastructure is ready, but the full working paper should not be written until real factsheet and NAV data are collected.

## Write Draft Sections Now

The following sections can be drafted before empirical data are complete:

- Introduction
- Institutional background
- Literature review
- Methodology
- Data collection protocol
- Limitations

## Do Not Finalise Yet

The following sections should wait until empirical outputs exist:

- Abstract
- Empirical results
- Conclusion
- Policy/disclosure implications

## Minimum Files Required Before Full Paper Writing

The full empirical paper should be written after these files are populated and reviewed:

```text
data/processed/fund_master.csv
data/processed/fund_factsheet_metrics.csv
data/processed/nav_history.csv
outputs/tables/duration_risk_summary.csv
outputs/tables/stress_loss_scenarios.csv
outputs/tables/nav_risk_metrics.csv
outputs/charts/ytm_vs_duration.png
outputs/charts/stress_loss_100bps.png
```

## Decision Rule

Begin the full empirical paper only after:

1. At least 15-30 target maturity funds are included.
2. Modified duration and YTM are available for most funds.
3. NAV history is available for enough funds to calculate volatility and drawdown.
4. Stress-loss and NAV-risk output tables are generated.
5. Charts are generated and visually reviewed.

Until then, keep the project as a structured working-paper dataset and methodology framework.
