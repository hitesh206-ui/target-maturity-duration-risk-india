"""Download Indian government yield proxy data from Trading Economics.

Outputs:
    data/processed/gsec_yield_history.csv
    outputs/tables/gsec_yield_download_report.csv

Purpose:
    Populate the yield panel needed for empirical-duration regressions:
        fund_return_t = alpha + beta * delta_yield_t + error_t
        realized_duration ≈ -beta

Notes:
    - This uses Trading Economics market symbols as public proxies.
    - 1Y is represented by the India 52-week yield where available.
    - The data source must be cited as a proxy source, not as an official RBI/CCIL curve.
    - If a symbol is unavailable under guest access, the report records the failure.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_FILE = ROOT / "data" / "processed" / "gsec_yield_history.csv"
REPORT_FILE = ROOT / "outputs" / "tables" / "gsec_yield_download_report.csv"

START_DATE = "2024-01-01"
END_DATE = date.today().isoformat()
API_KEY = "guest:guest"
BASE_URL = "https://api.tradingeconomics.com/markets/historical/{symbol}"

# Symbols use Trading Economics market identifiers.
SYMBOLS = [
    {"tenor_years": 0.25, "symbol": "GIND3M:IND", "label": "India 3M government yield proxy"},
    {"tenor_years": 1.0, "symbol": "GIND52W:IND", "label": "India 52W government yield proxy"},
    {"tenor_years": 2.0, "symbol": "GIND2Y:IND", "label": "India 2Y government yield proxy"},
    {"tenor_years": 3.0, "symbol": "GIND3Y:IND", "label": "India 3Y government yield proxy"},
    {"tenor_years": 5.0, "symbol": "GIND5Y:IND", "label": "India 5Y government yield proxy"},
]

OUTPUT_COLUMNS = ["date", "tenor_years", "yield_percent", "source_id", "notes"]
REPORT_COLUMNS = ["symbol", "tenor_years", "status", "rows", "message"]


def fetch_symbol(symbol: str) -> pd.DataFrame:
    url = BASE_URL.format(symbol=symbol)
    params = {"c": API_KEY, "d1": START_DATE, "d2": END_DATE, "f": "json"}
    response = requests.get(url, params=params, timeout=60, headers={"User-Agent": "Mozilla/5.0"})
    response.raise_for_status()
    data = response.json()
    if isinstance(data, dict):
        # Some TE API errors are JSON dicts rather than lists.
        raise RuntimeError(str(data))
    if not data:
        return pd.DataFrame()
    df = pd.DataFrame(data)
    # Expected fields: Symbol, Date, Open, High, Low, Close
    if "Date" not in df.columns or "Close" not in df.columns:
        raise RuntimeError(f"Unexpected response columns: {list(df.columns)}")
    df["date"] = pd.to_datetime(df["Date"], errors="coerce", dayfirst=True)
    df["yield_percent"] = pd.to_numeric(df["Close"], errors="coerce")
    return df.dropna(subset=["date", "yield_percent"])


def main() -> None:
    frames = []
    reports = []
    for item in SYMBOLS:
        symbol = item["symbol"]
        tenor = item["tenor_years"]
        label = item["label"]
        try:
            raw = fetch_symbol(symbol)
            if raw.empty:
                reports.append({"symbol": symbol, "tenor_years": tenor, "status": "empty", "rows": 0, "message": "No rows returned"})
                continue
            out = pd.DataFrame(
                {
                    "date": raw["date"].dt.date,
                    "tenor_years": tenor,
                    "yield_percent": raw["yield_percent"],
                    "source_id": "TRADING_ECONOMICS_MARKETS_API",
                    "notes": f"{label}; symbol={symbol}; date_range={START_DATE} to {END_DATE}",
                }
            )
            frames.append(out)
            reports.append({"symbol": symbol, "tenor_years": tenor, "status": "ok", "rows": int(out.shape[0]), "message": ""})
        except Exception as exc:
            reports.append({"symbol": symbol, "tenor_years": tenor, "status": "failed", "rows": 0, "message": str(exc)[:500]})

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    if frames:
        result = pd.concat(frames, ignore_index=True).sort_values(["tenor_years", "date"])
        result[OUTPUT_COLUMNS].to_csv(OUTPUT_FILE, index=False)
    else:
        pd.DataFrame(columns=OUTPUT_COLUMNS).to_csv(OUTPUT_FILE, index=False)
    pd.DataFrame(reports, columns=REPORT_COLUMNS).to_csv(REPORT_FILE, index=False)
    print(f"Wrote {OUTPUT_FILE}")
    print(f"Wrote {REPORT_FILE}")


if __name__ == "__main__":
    main()
