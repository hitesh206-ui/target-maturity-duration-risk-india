"""Download and standardize NAV history from AMFI text archives.

Outputs:
    data/processed/nav_history.csv
    outputs/tables/nav_match_report.csv

AMFI historical NAV rows usually follow this layout:
    Scheme Code;Scheme Name;ISIN Div Payout/ISIN Growth;ISIN Div Reinvestment;
    Net Asset Value;Repurchase Price;Sale Price;Date

The parser below uses that layout and falls back defensively when extra fields
appear.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from urllib.parse import urlencode

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
MAP_FILE = ROOT / "data" / "documentation" / "nav_collection_map.csv"
NAV_OUTPUT = ROOT / "data" / "processed" / "nav_history.csv"
REPORT_OUTPUT = ROOT / "outputs" / "tables" / "nav_match_report.csv"
AMFI_URL = "https://portal.amfiindia.com/DownloadNAVHistoryReport_Po.aspx"
START_DATE = date(2024, 1, 1)
END_DATE = date.today()

NAV_COLUMNS = ["fund_id", "scheme_name", "date", "nav", "source_id", "notes"]
REPORT_COLUMNS = ["fund_id", "scheme_name", "search_terms", "status", "matched_scheme_name", "matched_scheme_code", "rows", "message"]


@dataclass
class MatchResult:
    fund_id: str
    scheme_name: str
    search_terms: str
    status: str
    matched_scheme_name: str = ""
    matched_scheme_code: str = ""
    rows: int = 0
    message: str = ""


def month_ranges(start: date, end: date):
    cursor = date(start.year, start.month, 1)
    while cursor <= end:
        next_month = date(cursor.year + (cursor.month // 12), (cursor.month % 12) + 1, 1)
        month_end = min(end, next_month - timedelta(days=1))
        yield cursor, month_end
        cursor = next_month


def parse_amfi_line(parts: list[str], current_amc: str, current_category: str) -> dict | None:
    parts = [p.strip() for p in parts]
    if len(parts) < 8 or parts[0] == "Scheme Code":
        return None

    # Standard AMFI layout:
    # 0 Scheme Code, 1 Scheme Name, 2 ISIN Div/ISIN Growth, 3 ISIN Reinvestment,
    # 4 NAV, 5 Repurchase, 6 Sale, 7 Date
    scheme_code = parts[0]
    scheme_name = parts[1]
    nav_text = parts[4]
    date_text = parts[-1]
    isin_fields = parts[2:4]

    return {
        "scheme_code": scheme_code,
        "isin_fields": "|".join(isin_fields),
        "scheme_name_amfi": scheme_name,
        "nav": nav_text,
        "date": date_text,
        "amc_from_file": current_amc,
        "category_from_file": current_category,
    }


def fetch_amfi_range(start: date, end: date) -> pd.DataFrame:
    # AMFI examples often include tp=1, and the portal says historical NAV can
    # be downloaded for up to 90 days at a time. Monthly chunks are safe.
    params = {"tp": "1", "frmdt": start.strftime("%d-%b-%Y"), "todt": end.strftime("%d-%b-%Y")}
    url = AMFI_URL + "?" + urlencode(params)
    try:
        response = requests.get(url, timeout=60, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
    except Exception as exc:
        print(f"AMFI request failed for {start} to {end}: {exc}")
        return pd.DataFrame()

    rows = []
    current_amc = ""
    current_category = ""
    for line in response.text.splitlines():
        line = line.strip()
        if not line:
            continue
        if ";" not in line:
            if "Mutual Fund" in line or "Asset Management" in line:
                current_amc = line
            else:
                current_category = line
            continue
        parsed = parse_amfi_line(line.split(";"), current_amc, current_category)
        if parsed is not None:
            rows.append(parsed)
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"], format="%d-%b-%Y", errors="coerce")
    df["nav"] = pd.to_numeric(df["nav"], errors="coerce")
    return df.dropna(subset=["date", "nav", "scheme_name_amfi"])


def normalize(text: str) -> str:
    return " ".join(str(text).lower().replace("-", " ").replace("&", " and ").replace(":", " ").replace("/", " ").replace("(", " ").replace(")", " ").split())


def score_match(scheme_name: str, search_terms: str) -> int:
    hay = normalize(scheme_name)
    terms = normalize(search_terms).split()
    return sum(1 for term in terms if term in hay)


def choose_best_match(all_nav: pd.DataFrame, search_terms: str) -> pd.DataFrame:
    candidates = all_nav.copy()
    candidates["match_score"] = candidates["scheme_name_amfi"].apply(lambda x: score_match(x, search_terms))
    candidates = candidates[candidates["match_score"] >= 4]
    if candidates.empty:
        return pd.DataFrame()

    terms_norm = normalize(search_terms)
    direct_requested = "direct" in terms_norm
    growth_requested = "growth" in terms_norm
    etf_requested = "etf" in terms_norm
    fof_requested = "fof" in terms_norm or "fund of fund" in terms_norm

    candidates["direct_bonus"] = candidates["scheme_name_amfi"].str.lower().str.contains("direct", na=False).astype(int) if direct_requested else 0
    candidates["growth_bonus"] = candidates["scheme_name_amfi"].str.lower().str.contains("growth", na=False).astype(int) if growth_requested else 0
    candidates["etf_bonus"] = candidates["scheme_name_amfi"].str.lower().str.contains("etf", na=False).astype(int) if etf_requested else 0
    candidates["fof_bonus"] = candidates["scheme_name_amfi"].str.lower().str.contains("fof|fund of fund", regex=True, na=False).astype(int) if fof_requested else 0

    scheme_scores = candidates.groupby(["scheme_code", "scheme_name_amfi"], as_index=False).agg(
        match_score=("match_score", "max"),
        direct_bonus=("direct_bonus", "max"),
        growth_bonus=("growth_bonus", "max"),
        etf_bonus=("etf_bonus", "max"),
        fof_bonus=("fof_bonus", "max"),
        rows=("nav", "size"),
    ).sort_values(["match_score", "direct_bonus", "growth_bonus", "etf_bonus", "fof_bonus", "rows"], ascending=False)

    best = scheme_scores.iloc[0]
    return all_nav[all_nav["scheme_code"].astype(str) == str(best["scheme_code"])].copy()


def write_outputs(frames: list[pd.DataFrame], reports: list[MatchResult]) -> None:
    NAV_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    REPORT_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    if frames:
        pd.concat(frames, ignore_index=True)[NAV_COLUMNS].to_csv(NAV_OUTPUT, index=False)
    else:
        pd.DataFrame(columns=NAV_COLUMNS).to_csv(NAV_OUTPUT, index=False)
    pd.DataFrame([r.__dict__ for r in reports], columns=REPORT_COLUMNS).to_csv(REPORT_OUTPUT, index=False)


def main() -> None:
    nav_map = pd.read_csv(MAP_FILE)
    reports: list[MatchResult] = []
    frames: list[pd.DataFrame] = []

    all_months = []
    for start, end in month_ranges(START_DATE, END_DATE):
        print(f"Downloading AMFI NAV: {start} to {end}")
        month_df = fetch_amfi_range(start, end)
        if not month_df.empty:
            all_months.append(month_df)

    if not all_months:
        for _, row in nav_map.iterrows():
            reports.append(MatchResult(str(row["fund_id"]), str(row["scheme_name"]), str(row["amfi_search_terms"]), "amfi_unavailable", message="No AMFI NAV data returned"))
        write_outputs(frames, reports)
        print("No AMFI NAV data returned; wrote empty NAV output and report.")
        return

    all_nav = pd.concat(all_months, ignore_index=True).drop_duplicates()
    for _, row in nav_map.iterrows():
        fund_id = str(row["fund_id"])
        scheme_name = str(row["scheme_name"])
        search_terms = str(row["amfi_search_terms"])
        matched = choose_best_match(all_nav, search_terms)
        if matched.empty:
            reports.append(MatchResult(fund_id, scheme_name, search_terms, "no_match", message="No AMFI scheme match"))
            continue
        matched_scheme_name = matched["scheme_name_amfi"].iloc[0]
        matched_scheme_code = str(matched["scheme_code"].iloc[0])
        out = pd.DataFrame({
            "fund_id": fund_id,
            "scheme_name": scheme_name,
            "date": matched["date"].dt.date,
            "nav": matched["nav"],
            "source_id": "AMFI_NAV_HISTORY",
            "notes": "AMFI matched scheme: " + matched_scheme_name + " | code: " + matched_scheme_code,
        })
        frames.append(out)
        reports.append(MatchResult(fund_id, scheme_name, search_terms, "matched", matched_scheme_name, matched_scheme_code, int(out.shape[0])))

    write_outputs(frames, reports)
    print(f"Wrote {NAV_OUTPUT}")
    print(f"Wrote {REPORT_OUTPUT}")


if __name__ == "__main__":
    main()
