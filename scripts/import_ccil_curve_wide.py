"""Import CCIL NSS/zero-coupon curve files in wide format.

Input:
    data/raw/yields/ccil_nss_curve_wide.csv

Expected wide format:
    Date,0.0,1.0,2.0,3.0,4.0,5.0,...,50.0

Output:
    data/processed/gsec_yield_history.csv
    outputs/tables/ccil_curve_import_report.csv

The importer extracts tenors needed for the empirical-duration regression:
    0.25 (if available), 1.0, 2.0, 3.0, 5.0

If 0.25 is unavailable, near-maturity funds can be excluded from regression or
mapped to 1Y with an explicit caveat.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
INPUT_FILE = ROOT / "data" / "raw" / "yields" / "ccil_nss_curve_wide.csv"
OUTPUT_FILE = ROOT / "data" / "processed" / "gsec_yield_history.csv"
REPORT_FILE = ROOT / "outputs" / "tables" / "ccil_curve_import_report.csv"

TENORS_TO_EXTRACT = [0.25, 1.0, 2.0, 3.0, 5.0]
OUTPUT_COLUMNS = ["date", "tenor_years", "yield_percent", "source_id", "notes"]
REPORT_COLUMNS = ["tenor_years", "status", "rows", "message"]


def find_date_column(df: pd.DataFrame) -> str:
    for col in df.columns:
        if str(col).strip().lower() == "date":
            return col
    raise ValueError("No Date column found in CCIL wide curve file")


def find_tenor_column(df: pd.DataFrame, tenor: float) -> str | None:
    candidates = [str(tenor), f"{tenor:.1f}", f"{int(tenor)}.0" if tenor.is_integer() else str(tenor)]
    cleaned = {str(c).strip(): c for c in df.columns}
    for candidate in candidates:
        if candidate in cleaned:
            return cleaned[candidate]
    return None


def main() -> None:
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)

    if not INPUT_FILE.exists():
        pd.DataFrame(columns=OUTPUT_COLUMNS).to_csv(OUTPUT_FILE, index=False)
        pd.DataFrame(
            [{"tenor_years": "all", "status": "missing_input", "rows": 0, "message": f"Missing file: {INPUT_FILE}"}],
            columns=REPORT_COLUMNS,
        ).to_csv(REPORT_FILE, index=False)
        print(f"Missing input file: {INPUT_FILE}")
        return

    df = pd.read_csv(INPUT_FILE)
    date_col = find_date_column(df)
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce", dayfirst=True)
    frames = []
    reports = []

    for tenor in TENORS_TO_EXTRACT:
        col = find_tenor_column(df, tenor)
        if col is None:
            reports.append({"tenor_years": tenor, "status": "missing_column", "rows": 0, "message": "Tenor column not present in CCIL file"})
            continue
        temp = pd.DataFrame(
            {
                "date": df[date_col],
                "tenor_years": tenor,
                "yield_percent": pd.to_numeric(df[col], errors="coerce"),
                "source_id": "CCIL_NSS_CURVE_MANUAL_CSV",
                "notes": f"Imported from CCIL NSS curve wide file; extracted tenor {tenor}",
            }
        )
        temp = temp.dropna(subset=["date", "yield_percent"])
        # Drop placeholder zero values at long tenors, but preserve real short-end values.
        temp = temp[temp["yield_percent"] > 0]
        frames.append(temp[OUTPUT_COLUMNS])
        reports.append({"tenor_years": tenor, "status": "ok", "rows": int(temp.shape[0]), "message": ""})

    if frames:
        out = pd.concat(frames, ignore_index=True).drop_duplicates().sort_values(["tenor_years", "date"])
        out.to_csv(OUTPUT_FILE, index=False)
    else:
        pd.DataFrame(columns=OUTPUT_COLUMNS).to_csv(OUTPUT_FILE, index=False)
    pd.DataFrame(reports, columns=REPORT_COLUMNS).to_csv(REPORT_FILE, index=False)
    print(f"Wrote {OUTPUT_FILE}")
    print(f"Wrote {REPORT_FILE}")


if __name__ == "__main__":
    main()
