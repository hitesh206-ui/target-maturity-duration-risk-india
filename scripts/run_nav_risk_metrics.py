"""Compute NAV-based risk metrics for target maturity funds.

Inputs:
    data/processed/nav_history.csv

Outputs:
    outputs/tables/nav_risk_metrics.csv
    data/processed/nav_returns.csv
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.duration_metrics import (
    annualized_volatility,
    downside_month_frequency,
    maximum_drawdown,
    simple_returns,
    worst_period_return,
)

ROOT = Path(__file__).resolve().parents[1]
INPUT_FILE = ROOT / "data" / "processed" / "nav_history.csv"
OUTPUT_DIR = ROOT / "outputs" / "tables"
PROCESSED_DIR = ROOT / "data" / "processed"
RISK_FILE = OUTPUT_DIR / "nav_risk_metrics.csv"
RETURNS_FILE = PROCESSED_DIR / "nav_returns.csv"


def main() -> None:
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Missing input file: {INPUT_FILE}")

    df = pd.read_csv(INPUT_FILE)
    required = {"fund_id", "scheme_name", "date", "nav"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["nav"] = pd.to_numeric(df["nav"], errors="coerce")
    df = df.dropna(subset=["fund_id", "date", "nav"]).sort_values(["fund_id", "date"])

    returns_frames = []
    risk_rows = []

    for fund_id, group in df.groupby("fund_id"):
        group = group.sort_values("date").copy()
        group["return"] = simple_returns(group["nav"])
        returns_frames.append(group)

        scheme_name = group["scheme_name"].iloc[0]
        returns = group["return"]
        nav = group["nav"]
        risk_rows.append(
            {
                "fund_id": fund_id,
                "scheme_name": scheme_name,
                "start_date": group["date"].min().date(),
                "end_date": group["date"].max().date(),
                "observations": int(group.shape[0]),
                "annualized_volatility": annualized_volatility(returns, periods_per_year=12),
                "maximum_drawdown": maximum_drawdown(nav),
                "worst_monthly_return": worst_period_return(returns),
                "downside_month_frequency": downside_month_frequency(returns),
            }
        )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    pd.concat(returns_frames, ignore_index=True).to_csv(RETURNS_FILE, index=False)
    pd.DataFrame(risk_rows).to_csv(RISK_FILE, index=False)
    print(f"Wrote {RETURNS_FILE}")
    print(f"Wrote {RISK_FILE}")


if __name__ == "__main__":
    main()
