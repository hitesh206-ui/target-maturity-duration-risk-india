# Data Dictionary

## `fund_master.csv`

| Variable | Description |
|---|---|
| `fund_id` | Unique fund identifier used in the project. |
| `scheme_name` | Full scheme name. |
| `amc` | Asset management company. |
| `scheme_type` | Index fund, ETF, FoF, or other target maturity structure. |
| `benchmark` | Target maturity index or benchmark. |
| `target_maturity_year` | Stated target maturity year. |
| `target_maturity_date` | Exact maturity date if available. |
| `asset_class_focus` | G-Sec, SDL, PSU, corporate bond, or mixed. |
| `included_in_study` | Yes/No flag for final inclusion. |
| `notes` | Additional comments. |

## `fund_factsheet_metrics.csv`

| Variable | Description |
|---|---|
| `obs_id` | Observation identifier. |
| `fund_id` | Fund identifier linked to `fund_master.csv`. |
| `scheme_name` | Full scheme name. |
| `amc` | Asset management company. |
| `factsheet_date` | Date of factsheet observation. |
| `modified_duration` | Modified duration in years. |
| `macaulay_duration` | Macaulay duration in years, if available. |
| `average_maturity` | Average maturity in years. |
| `ytm_percent` | Yield to maturity in percent. |
| `expense_ratio_percent` | Expense ratio in percent. |
| `aum_crore` | Assets under management in INR crore. |
| `sovereign_weight_percent` | Government/security sovereign exposure. |
| `aaa_weight_percent` | AAA or equivalent exposure. |
| `aa_and_below_weight_percent` | AA and below exposure, if available. |
| `cash_weight_percent` | Cash, TREPS, or equivalent exposure. |
| `source_id` | Source identifier. |
| `notes` | Comments or caveats. |

## `nav_history.csv`

| Variable | Description |
|---|---|
| `fund_id` | Fund identifier. |
| `scheme_name` | Full scheme name. |
| `date` | NAV date. |
| `nav` | Net asset value. |
| `source_id` | Source identifier. |
| `notes` | Comments or caveats. |

## Output Files

Planned output files:

- `duration_risk_summary.csv`
- `stress_loss_scenarios.csv`
- `nav_risk_metrics.csv`
- `duration_scorecard.csv`
