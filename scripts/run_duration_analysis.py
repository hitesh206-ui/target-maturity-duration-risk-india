"""Run duration-risk calculations for target maturity funds.

Inputs:
    data/processed/fund_factsheet_metrics.csv

Outputs:
    outputs/tables/duration_risk_summary.csv
    outputs/tables/stress_loss_scenarios.csv
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.duration_metrics import stress_loss_percent, ytm_to_duration_ratio


ROOT = Path(__file__).resolve().parents[1]
INPUT_FILE = ROOT / "data" / "processed" / "fund_factsheet_metrics.csv"
OUTPUT_DIR = ROOT / "outputs" / "tables"
SUMMARY_FILE = OUTPUT_DIR / "duration_risk_summary.csv"
STRESS_FILE = OUTPUT_DIR / "stress_loss_scenarios.csv"

SHOCKS_BPS = [25, 50, 100, 150, 200]


def main() -> None:
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Missing input file: {INPUT_FILE}")

    df = pd.read_csv(INPUT_FILE)
    required = {"fund_id", "scheme_name", "modified_duration", "ytm_percent"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    df["modified_duration"] = pd.to_numeric(df["modified_duration"], errors="coerce")
    df["ytm_percent"] = pd.to_numeric(df["ytm_percent"], errors="coerce")
    df["ytm_to_duration_ratio"] = df.apply(
        lambda r: ytm_to_duration_ratio(r["ytm_percent"], r["modified_duration"]), axis=1
    )

    stress_rows = []
    for _, row in df.iterrows():
        for shock in SHOCKS_BPS:
            stress_rows.append(
                {
                    "fund_id": row["fund_id"],
                    "scheme_name": row["scheme_name"],
                    "factsheet_date": row.get("factsheet_date", ""),
                    "modified_duration": row["modified_duration"],
                    "yield_shock_bps": shock,
                    "estimated_nav_impact_percent": stress_loss_percent(row["modified_duration"], shock)
                    if pd.notna(row["modified_duration"])
                    else None,
                }
            )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(SUMMARY_FILE, index=False)
    pd.DataFrame(stress_rows).to_csv(STRESS_FILE, index=False)
    print(f"Wrote {SUMMARY_FILE}")
    print(f"Wrote {STRESS_FILE}")


if __name__ == "__main__":
    main()
