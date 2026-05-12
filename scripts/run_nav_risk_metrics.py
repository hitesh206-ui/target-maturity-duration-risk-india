"""Compute NAV-based risk metrics for target maturity funds.

Inputs:
    data/processed/nav_history.csv

Outputs:
    outputs/tables/nav_risk_metrics.csv
    data/processed/nav_returns.csv

Note:
    AMFI NAV history is daily/near-daily. The output therefore labels downside
    statistics as daily observations, not monthly observations.
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

RETURNS_COLUMNS = ["fund_id", "scheme_name", "date", "nav", "source_id", "notes", "return"]
RISK_COLUMNS = [
    "fund_id",
    "scheme_name",
    "start_date",
    "end_date",
    "observations",
    "annualized_volatility",
    "maximum_drawdown",
    "worst_daily_return",
    "downside_day_frequency",
]


def write_empty_outputs() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(columns=RETURNS_COLUMNS).to_csv(RETURNS_FILE, index=False)
    pd.DataFrame(columns=RISK_COLUMNS).to_csv(RISK_FILE, index=False)


def main() -> None:
    if not INPUT_FILE.exists():
        write_empty_outputs()
        print(f"Missing input file: {INPUT_FILE}. Wrote empty NAV risk outputs.")
        return

    df = pd.read_csv(INPUT_FILE)
    required = {"fund_id", "scheme_name", "date", "nav"}
    missing = required - set(df.columns)
    if missing:
        write_empty_outputs()
        print(f"Missing required columns: {sorted(missing)}. Wrote empty NAV risk outputs.")
        return

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["nav"] = pd.to_numeric(df["nav"], errors="coerce")
    df = df.dropna(subset=["fund_id", "date", "nav"]).sort_values(["fund_id", "date"])

    if df.empty:
        write_empty_outputs()
        print("NAV history is empty after cleaning. Wrote empty NAV risk outputs.")
        return

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
                "annualized_volatility": annualized_volatility(returns, periods_per_year=252),
                "maximum_drawdown": maximum_drawdown(nav),
                "worst_daily_return": worst_period_return(returns),
                "downside_day_frequency": downside_month_frequency(returns),
            }
        )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    pd.concat(returns_frames, ignore_index=True).to_csv(RETURNS_FILE, index=False)
    pd.DataFrame(risk_rows, columns=RISK_COLUMNS).to_csv(RISK_FILE, index=False)
    print(f"Wrote {RETURNS_FILE}")
    print(f"Wrote {RISK_FILE}")


if __name__ == "__main__":
    main()
