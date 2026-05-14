# Disclosed Duration and Realized NAV Risk in Indian Target Maturity Debt Funds

## Working paper title

**Disclosed Duration and Realized NAV Risk in Indian Target Maturity Debt Funds: A Public-Data Pilot Study of Target Maturity Funds, Stress Loss, and Proxy Yield Sensitivity**

## Authors

Hitesh Dabi — Independent Researcher  
MSc in International Management  
Email: hiteshdabi@ymail.com

Himanshu Dabi — Independent Researcher  
MSc in International Management  
Email: dabihithim@gmail.com

## Project objective

This repository supports a public-data working paper that studies whether factsheet-disclosed modified duration is associated with realized NAV risk in Indian target maturity debt funds and ETFs.

The project is designed as a **pilot, methodological, reproducible research framework** rather than an investment product review. It uses public factsheets, AMFI NAV histories, public government-yield proxies, and Python-generated outputs to distinguish three related but different concepts:

1. **Disclosed duration** from fund factsheets.
2. **Realized NAV risk** from AMFI daily NAV histories.
3. **Proxy realized rate sensitivity** from regressions of NAV returns on matched government-yield changes.

## Core research questions

1. Do higher disclosed modified durations correspond to higher realized NAV volatility and drawdown?
2. How large are first-order stress losses under parallel yield shocks of +25, +50, +100, +150, and +200 basis points?
3. Do daily NAV returns display measurable sensitivity to changes in matched Indian government-yield proxies?
4. Does fund structure matter when two products report the same disclosed duration, especially in the BHARAT Bond ETF versus FOF comparison?

## Pilot sample

The pilot sample contains eight Indian target maturity products across 2026, 2027, 2030, and 2031 maturity buckets:

- BHARAT Bond ETF - April 2030
- BHARAT Bond FOF - April 2030
- BHARAT Bond ETF - April 2031
- ICICI Prudential Nifty G-Sec Dec 2030 Index Fund
- HDFC Nifty G-Sec Jun 2027 Index Fund
- HDFC Nifty SDL Plus G-Sec Jun 2027 40:60 Index Fund
- Nippon India ETF Nifty SDL Apr 2026 Top 20 Equal Weight
- Axis CRISIL IBX SDL May 2027 Index Fund

The sample is purposive and should not be interpreted as the full Indian target maturity fund universe.

## Main empirical outputs

The repository currently produces or stores the following research outputs:

- `outputs/tables/duration_risk_summary.csv` — factsheet-based duration, maturity, YTM, expense, AUM, and exposure variables.
- `outputs/tables/stress_loss_scenarios.csv` — first-order NAV impact estimates for +25 to +200 bps shocks.
- `outputs/tables/nav_risk_metrics.csv` — annualized NAV volatility, maximum drawdown, worst daily return, downside-day frequency, and NAV observation counts.
- `outputs/tables/empirical_duration_regression.csv` — proxy realized-duration regressions using matched 1Y and 5Y government-yield proxies.
- `outputs/tables/gsec_yield_import_report.csv` — yield import validation.
- `data/processed/gsec_yield_history.csv` — standardized 1Y and 5Y yield-history panel used in the regression layer.

## Key findings from the current working-paper version

- Disclosed modified duration is strongly associated with realized NAV risk in rank terms. Spearman rho is approximately 0.80 for annualized NAV volatility and absolute maximum drawdown.
- The longest-duration fund in the pilot sample, BHARAT Bond ETF April 2031, has an estimated first-order stress loss of about -4.58% under a +100 bps shock and -9.16% under a +200 bps shock.
- Proxy realized-duration regressions produce positive duration estimates for seven funds.
- ICICI Prudential Nifty G-Sec Dec 2030 Index Fund has the strongest proxy-yield explanatory power in the pilot sample.
- BHARAT Bond ETF April 2030 and BHARAT Bond FOF April 2030 report the same modified duration, but the FOF exhibits materially higher realized annualized NAV volatility and maximum drawdown. This is treated as an N=1 fund-structure puzzle, not as a general law about all FOFs.

## Repository structure

```text
data/
  raw/
  processed/
  documentation/

src/
  duration_metrics.py
  regression_metrics.py
  disclosure_cleaning.py

scripts/
  download_nav_history_amfi.py
  import_manual_gsec_yields.py
  run_duration_analysis.py
  run_empirical_duration_regression.py
  generate_tables.py
  generate_charts.py

outputs/
  tables/
  charts/

docs/
  methodology.md
  data_dictionary.md
  project_checklist.md
  source_log.csv
  ssrn_submission_checklist.md

paper/
  working_paper/
```

## Methodology overview

The project uses three empirical layers:

1. **Stress-loss layer**
   - Estimated NAV impact = -Modified Duration × Yield Shock.
   - Shocks are tested at +25, +50, +100, +150, and +200 bps.
   - Convexity, carry, roll-down, and non-parallel curve shifts are excluded from the main stress table and treated as limitations.

2. **NAV-risk layer**
   - Daily NAV returns are computed from AMFI NAV histories.
   - Annualized volatility uses daily standard deviation × sqrt(252).
   - Maximum drawdown, worst daily return, downside-day frequency, and observation counts are reported.

3. **Proxy realized-duration layer**
   - Daily fund returns are regressed on daily changes in matched government-yield proxies.
   - 2030/2031 funds are mapped to the 5-year yield proxy.
   - 2027 funds are mapped to the 1-year yield proxy.
   - F007 is excluded from regression because no 0.25-year or 3-month proxy is currently available.
   - Realized duration is approximately `-beta` from the regression.

## How to reproduce

A reader should be able to audit the project by reviewing:

1. The factsheet extraction and source notes.
2. The AMFI NAV matching report and scheme-code mapping.
3. The G-Sec yield import report.
4. The generated output tables.
5. The chart outputs.
6. The paper tables and figures.

Before public release or citation, rerun the workflow and confirm that:

- NAV matches show proper scheme names, not ISIN-like strings.
- Yield import reports show adequate row counts for 1Y and 5Y proxies.
- Annualized volatility uses sqrt(252).
- F005's missing YTM is footnoted rather than filled by guesswork.
- The regression is described as proxy realized duration, not exact key-rate duration.

## Research boundary

This project is for educational and research purposes only. It does not provide investment advice, financial planning advice, tax advice, legal advice, or any buy, sell, hold, switch, or redeem recommendation for any fund or security.

The analysis relies on public data, manual downloads, and code-based processing. It may contain errors despite reasonable validation. Investors should consult qualified professionals and official fund documents before making financial decisions.

## Status

**SSRN-ready working-paper repository after final manuscript formatting and upload.**

Recommended public framing: **pilot, public-data, proxy, methodological working paper.**
