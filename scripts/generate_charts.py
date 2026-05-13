"""Generate charts for the target maturity duration risk project.

Inputs:
    outputs/tables/duration_risk_summary.csv
    outputs/tables/stress_loss_scenarios.csv
    outputs/tables/nav_risk_metrics.csv
    outputs/tables/empirical_duration_regression.csv

Outputs:
    outputs/charts/ytm_vs_duration.png
    outputs/charts/stress_loss_100bps.png
    outputs/charts/nav_volatility.png
    outputs/charts/maximum_drawdown.png
    outputs/charts/duration_vs_nav_volatility.png
    outputs/charts/disclosed_vs_realized_duration.png
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
REGRESSION_FILE = TABLE_DIR / "empirical_duration_regression.csv"


def _save(fig: plt.Figure, filename: str) -> None:
    CHART_DIR.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(CHART_DIR / filename, dpi=200)
    plt.close(fig)


def _annotate_with_offsets(ax, df, x_col, y_col, label_col="fund_id") -> None:
    offsets = {
        "F001": (6, 6),
        "F002": (6, -12),
        "F003": (6, 6),
        "F004": (6, 6),
        "F005": (-30, 10),
        "F006": (8, -14),
        "F007": (6, 6),
        "F008": (10, 12),
    }
    for _, row in df.iterrows():
        label = str(row[label_col])
        xytext = offsets.get(label, (6, 6))
        ax.annotate(label, (row[x_col], row[y_col]), textcoords="offset points", xytext=xytext, fontsize=8)


def ytm_vs_duration() -> None:
    if not DURATION_FILE.exists():
        return
    df = pd.read_csv(DURATION_FILE)
    df = df.dropna(subset=["modified_duration", "ytm_percent"])
    if df.empty:
        return
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(df["modified_duration"], df["ytm_percent"])
    _annotate_with_offsets(ax, df, "modified_duration", "ytm_percent")
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
    ax.bar(df["fund_id"], df["annualized_volatility"] * 100)
    ax.set_title("Annualized NAV Volatility by Fund")
    ax.set_xlabel("Fund")
    ax.set_ylabel("Annualized Volatility (%)")
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
    ax.bar(df["fund_id"], df["maximum_drawdown"] * 100)
    ax.set_title("Maximum Drawdown by Fund")
    ax.set_xlabel("Fund")
    ax.set_ylabel("Maximum Drawdown (%)")
    ax.tick_params(axis="x", rotation=45)
    _save(fig, "maximum_drawdown.png")


def duration_vs_nav_volatility() -> None:
    if not DURATION_FILE.exists() or not NAV_RISK_FILE.exists():
        return
    duration = pd.read_csv(DURATION_FILE)[["fund_id", "modified_duration"]]
    nav = pd.read_csv(NAV_RISK_FILE)[["fund_id", "annualized_volatility"]]
    df = duration.merge(nav, on="fund_id", how="inner").dropna()
    if df.empty:
        return
    fig, ax = plt.subplots(figsize=(8, 6))
    df["annualized_volatility_percent"] = df["annualized_volatility"] * 100
    ax.scatter(df["modified_duration"], df["annualized_volatility_percent"])
    _annotate_with_offsets(ax, df, "modified_duration", "annualized_volatility_percent")
    ax.set_title("Disclosed Duration versus Realized NAV Volatility")
    ax.set_xlabel("Modified Duration (years)")
    ax.set_ylabel("Annualized NAV Volatility (%)")
    _save(fig, "duration_vs_nav_volatility.png")


def disclosed_vs_realized_duration() -> None:
    if not REGRESSION_FILE.exists():
        return
    df = pd.read_csv(REGRESSION_FILE)
    df = df[df.get("status", "") == "ok"] if "status" in df.columns else df
    df = df.dropna(subset=["disclosed_modified_duration", "realized_duration_minus_beta"])
    if df.empty:
        return
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(df["disclosed_modified_duration"], df["realized_duration_minus_beta"])
    _annotate_with_offsets(ax, df, "disclosed_modified_duration", "realized_duration_minus_beta")
    min_val = min(df["disclosed_modified_duration"].min(), df["realized_duration_minus_beta"].min())
    max_val = max(df["disclosed_modified_duration"].max(), df["realized_duration_minus_beta"].max())
    ax.plot([min_val, max_val], [min_val, max_val], linestyle="--", linewidth=1)
    ax.set_title("Disclosed versus Realized Duration")
    ax.set_xlabel("Disclosed Modified Duration (years)")
    ax.set_ylabel("Realized Duration from NAV-Yield Regression")
    _save(fig, "disclosed_vs_realized_duration.png")


def main() -> None:
    ytm_vs_duration()
    stress_loss_100bps()
    nav_volatility()
    maximum_drawdown_chart()
    duration_vs_nav_volatility()
    disclosed_vs_realized_duration()
    print("Chart generation complete.")


if __name__ == "__main__":
    main()
