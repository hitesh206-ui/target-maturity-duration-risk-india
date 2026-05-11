"""Generate charts for the target maturity duration risk project.

Inputs:
    outputs/tables/duration_risk_summary.csv
    outputs/tables/stress_loss_scenarios.csv
    outputs/tables/nav_risk_metrics.csv

Outputs:
    outputs/charts/ytm_vs_duration.png
    outputs/charts/stress_loss_100bps.png
    outputs/charts/nav_volatility.png
    outputs/charts/maximum_drawdown.png
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
TABLE_DIR = ROOT / "outputs" / "tables"
CHART_DIR = ROOT / "outputs" / "charts"

DURATION_FILE = TABLE_DIR / "duration_risk_summary.csv"
STRESS_FILE = TABLE_DIR / "stress_loss_scenarios.csv"
NAV_RISK_FILE = TABLE_DIR / "nav_risk_metrics.csv"


def _save(fig: plt.Figure, filename: str) -> None:
    CHART_DIR.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(CHART_DIR / filename, dpi=200)
    plt.close(fig)


def ytm_vs_duration() -> None:
    if not DURATION_FILE.exists():
        return
    df = pd.read_csv(DURATION_FILE)
    df = df.dropna(subset=["modified_duration", "ytm_percent"])
    if df.empty:
        return
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(df["modified_duration"], df["ytm_percent"])
    for _, row in df.iterrows():
        ax.annotate(str(row["fund_id"]), (row["modified_duration"], row["ytm_percent"]), fontsize=8)
    ax.set_title("YTM versus Modified Duration")
    ax.set_xlabel("Modified Duration (years)")
    ax.set_ylabel("YTM (%)")
    _save(fig, "ytm_vs_duration.png")


def stress_loss_100bps() -> None:
    if not STRESS_FILE.exists():
        return
    df = pd.read_csv(STRESS_FILE)
    df = df[df["yield_shock_bps"] == 100]
    df = df.dropna(subset=["estimated_nav_impact_percent"])
    if df.empty:
        return
    df = df.sort_values("estimated_nav_impact_percent")
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(df["fund_id"], df["estimated_nav_impact_percent"])
    ax.set_title("Estimated NAV Impact Under +100 bps Yield Shock")
    ax.set_xlabel("Fund")
    ax.set_ylabel("Estimated NAV Impact (%)")
    ax.tick_params(axis="x", rotation=45)
    _save(fig, "stress_loss_100bps.png")


def nav_volatility() -> None:
    if not NAV_RISK_FILE.exists():
        return
    df = pd.read_csv(NAV_RISK_FILE)
    df = df.dropna(subset=["annualized_volatility"])
    if df.empty:
        return
    df = df.sort_values("annualized_volatility", ascending=False)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(df["fund_id"], df["annualized_volatility"])
    ax.set_title("Annualized NAV Volatility by Fund")
    ax.set_xlabel("Fund")
    ax.set_ylabel("Annualized Volatility")
    ax.tick_params(axis="x", rotation=45)
    _save(fig, "nav_volatility.png")


def maximum_drawdown_chart() -> None:
    if not NAV_RISK_FILE.exists():
        return
    df = pd.read_csv(NAV_RISK_FILE)
    df = df.dropna(subset=["maximum_drawdown"])
    if df.empty:
        return
    df = df.sort_values("maximum_drawdown")
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(df["fund_id"], df["maximum_drawdown"])
    ax.set_title("Maximum Drawdown by Fund")
    ax.set_xlabel("Fund")
    ax.set_ylabel("Maximum Drawdown")
    ax.tick_params(axis="x", rotation=45)
    _save(fig, "maximum_drawdown.png")


def main() -> None:
    ytm_vs_duration()
    stress_loss_100bps()
    nav_volatility()
    maximum_drawdown_chart()
    print("Chart generation complete.")


if __name__ == "__main__":
    main()
