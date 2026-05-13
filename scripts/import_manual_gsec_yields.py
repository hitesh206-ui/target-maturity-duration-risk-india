"""Import manually downloaded Indian G-Sec yield CSVs.

Inputs in data/raw/yields/:
    india_3m_yield.csv optional
    india_1y_yield.csv required for short-tenor funds
    india_2y_yield.csv optional
    india_3y_yield.csv optional
    india_5y_yield.csv required for 2030/2031 funds

Outputs:
    data/processed/gsec_yield_history.csv
    outputs/tables/gsec_yield_import_report.csv

Accepted input formats:
    1. Investing.com style: Date, Price, Open, High, Low, Change %
    2. Simple style: date, yield_percent
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw" / "yields"
OUTPUT_FILE = ROOT / "data" / "processed" / "gsec_yield_history.csv"
REPORT_FILE = ROOT / "outputs" / "tables" / "gsec_yield_import_report.csv"

FILES = [
    {"file": "india_3m_yield.csv", "tenor_years": 0.25, "required": False},
    {"file": "india_1y_yield.csv", "tenor_years": 1.0, "required": True},
    {"file": "india_2y_yield.csv", "tenor_years": 2.0, "required": False},
    {"file": "india_3y_yield.csv", "tenor_years": 3.0, "required": False},
    {"file": "india_5y_yield.csv", "tenor_years": 5.0, "required": True},
]

OUTPUT_COLUMNS = ["date", "tenor_years", "yield_percent", "source_id", "notes"]
REPORT_COLUMNS = ["file", "tenor_years", "status", "rows", "message"]


def parse_yield_file(path: Path, tenor_years: float) -> pd.DataFrame:
    df = pd.read_csv(path)
    lower_cols = {c.lower().strip(): c for c in df.columns}

    if "date" in lower_cols and "yield_percent" in lower_cols:
        date_col = lower_cols["date"]
        yield_col = lower_cols["yield_percent"]
    elif "date" in lower_cols and "price" in lower_cols:
        date_col = lower_cols["date"]
        yield_col = lower_cols["price"]
    else:
        raise ValueError(f"Could not find Date/Price or date/yield_percent columns in {path.name}: {list(df.columns)}")

    out = pd.DataFrame()
    out["date"] = pd.to_datetime(df[date_col], errors="coerce")
    out["yield_percent"] = pd.to_numeric(df[yield_col].astype(str).str.replace("%", "", regex=False).str.replace(",", "", regex=False), errors="coerce")
    out["tenor_years"] = tenor_years
    out["source_id"] = "MANUAL_PUBLIC_YIELD_CSV"
    out["notes"] = f"Imported manually from {path.name}; verify source in source_log.csv"
    return out.dropna(subset=["date", "yield_percent"])[OUTPUT_COLUMNS]


def main() -> None:
    frames = []
    reports = []
    for item in FILES:
        path = RAW_DIR / item["file"]
        tenor = item["tenor_years"]
        required = item["required"]
        if not path.exists():
            status = "missing_required" if required else "missing_optional"
            reports.append({"file": item["file"], "tenor_years": tenor, "status": status, "rows": 0, "message": "File not found"})
            continue
        try:
            parsed = parse_yield_file(path, tenor)
            frames.append(parsed)
            reports.append({"file": item["file"], "tenor_years": tenor, "status": "ok", "rows": int(parsed.shape[0]), "message": ""})
        except Exception as exc:
            reports.append({"file": item["file"], "tenor_years": tenor, "status": "failed", "rows": 0, "message": str(exc)[:500]})

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    if frames:
        result = pd.concat(frames, ignore_index=True).drop_duplicates().sort_values(["tenor_years", "date"])
        result.to_csv(OUTPUT_FILE, index=False)
    else:
        pd.DataFrame(columns=OUTPUT_COLUMNS).to_csv(OUTPUT_FILE, index=False)
    pd.DataFrame(reports, columns=REPORT_COLUMNS).to_csv(REPORT_FILE, index=False)
    print(f"Wrote {OUTPUT_FILE}")
    print(f"Wrote {REPORT_FILE}")


if __name__ == "__main__":
    main()
