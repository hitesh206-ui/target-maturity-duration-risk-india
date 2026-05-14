"""Estimate realized duration from NAV returns and matched-tenor yield changes.

Inputs:
    data/processed/nav_returns.csv
    data/processed/gsec_yield_history.csv
    data/documentation/yield_regression_map.csv
    outputs/tables/duration_risk_summary.csv

Outputs:
    outputs/tables/empirical_duration_regression.csv

Model:
    fund_return_t = alpha + beta * delta_yield_t + error_t

Unit convention:
    The stored yield series is in percent form (for example, 7.05 for 7.05%).
    The script converts this to decimal form before differencing:
        yield_decimal = yield_percent / 100
        delta_yield_decimal = diff(yield_decimal)
    Therefore, a +100 basis point move is coded as 0.01.
    Under this convention, realized duration is approximately -beta.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.regression_metrics import ols_beta_alpha

ROOT = Path(__file__).resolve().parents[1]
NAV_RETURNS_FILE = ROOT / "data" / "processed" / "nav_returns.csv"
YIELD_FILE = ROOT / "data" / "processed" / "gsec_yield_history.csv"
MAP_FILE = ROOT / "data" / "documentation" / "yield_regression_map.csv"
DURATION_FILE = ROOT / "outputs" / "tables" / "duration_risk_summary.csv"
OUTPUT_FILE = ROOT / "outputs" / "tables" / "empirical_duration_regression.csv"

OUTPUT_COLUMNS = [
    "fund_id",
    "scheme_name",
    "matched_tenor_years",
    "observations",
    "alpha",
    "beta",
    "realized_duration_minus_beta",
    "r_squared",
    "disclosed_modified_duration",
    "duration_gap_realized_minus_disclosed",
    "status",
    "notes",
]


def write_empty(reason: str) -> None:
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(columns=OUTPUT_COLUMNS).to_csv(OUTPUT_FILE, index=False)
    print(reason)
    print(f"Wrote empty output: {OUTPUT_FILE}")


def main() -> None:
    missing = [p for p in [NAV_RETURNS_FILE, YIELD_FILE, MAP_FILE, DURATION_FILE] if not p.exists()]
    if missing:
        write_empty("Missing required files: " + ", ".join(str(p) for p in missing))
        return

    nav = pd.read_csv(NAV_RETURNS_FILE)
    yld = pd.read_csv(YIELD_FILE)
    mapping = pd.read_csv(MAP_FILE)
    duration = pd.read_csv(DURATION_FILE)

    if nav.empty or yld.empty:
        write_empty("NAV returns or G-Sec yield history is empty. Regression not run.")
        return

    nav["date"] = pd.to_datetime(nav["date"], errors="coerce")
    nav["return"] = pd.to_numeric(nav["return"], errors="coerce")
    yld["date"] = pd.to_datetime(yld["date"], errors="coerce")
    yld["tenor_years"] = pd.to_numeric(yld["tenor_years"], errors="coerce")
    yld["yield_percent"] = pd.to_numeric(yld["yield_percent"], errors="coerce")
    yld = yld.dropna(subset=["date", "tenor_years", "yield_percent"]).sort_values(["tenor_years", "date"])
    yld["yield_decimal"] = yld["yield_percent"] / 100
    yld["delta_yield_decimal"] = yld.groupby("tenor_years")["yield_decimal"].diff()

    duration_lookup = duration.set_index("fund_id")["modified_duration"].to_dict() if "modified_duration" in duration.columns else {}
    rows = []

    for _, m in mapping.iterrows():
        fund_id = str(m["fund_id"])
        scheme_name = str(m["scheme_name"])
        tenor = float(m["matched_tenor_years"])
        fund_nav = nav[nav["fund_id"].astype(str) == fund_id][["date", "return"]].copy()
        tenor_yield = yld[yld["tenor_years"] == tenor][["date", "delta_yield_decimal"]].copy()
        merged = fund_nav.merge(tenor_yield, on="date", how="inner")
        reg = ols_beta_alpha(merged["delta_yield_decimal"], merged["return"])
        realized_duration = -reg["beta"] if pd.notna(reg["beta"]) else None
        disclosed_duration = duration_lookup.get(fund_id)
        gap = None
        if realized_duration is not None and disclosed_duration is not None and pd.notna(disclosed_duration):
            gap = realized_duration - float(disclosed_duration)
        status = "ok" if reg["observations"] >= 30 and pd.notna(reg["beta"]) else "insufficient_data"
        rows.append(
            {
                "fund_id": fund_id,
                "scheme_name": scheme_name,
                "matched_tenor_years": tenor,
                "observations": reg["observations"],
                "alpha": reg["alpha"],
                "beta": reg["beta"],
                "realized_duration_minus_beta": realized_duration,
                "r_squared": reg["r_squared"],
                "disclosed_modified_duration": disclosed_duration,
                "duration_gap_realized_minus_disclosed": gap,
                "status": status,
                "notes": "Proxy regression using matched tenor yield changes. Interpret cautiously if yield proxy differs from portfolio exposures.",
            }
        )

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows, columns=OUTPUT_COLUMNS).to_csv(OUTPUT_FILE, index=False)
    print(f"Wrote {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
