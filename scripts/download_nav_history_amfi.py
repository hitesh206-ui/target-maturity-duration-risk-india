"""Download and standardize NAV history from AMFI text archives.

This script is designed for reproducible NAV collection. It uses the public AMFI
NAV history endpoint, searches scheme names from `nav_collection_map.csv`, and
writes standardized NAV observations.

Important:
    AMFI scheme-name matching can be messy. Always review the match report before
    using the NAV data in the paper.

Outputs:
    data/processed/nav_history.csv
    outputs/tables/nav_match_report.csv
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from urllib.parse import urlencode

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
MAP_FILE = ROOT / "data" / "documentation" / "nav_collection_map.csv"
NAV_OUTPUT = ROOT / "data" / "processed" / "nav_history.csv"
REPORT_OUTPUT = ROOT / "outputs" / "tables" / "nav_match_report.csv"

# AMFI historical NAV endpoint.
AMFI_URL = "https://portal.amfiindia.com/DownloadNAVHistoryReport_Po.aspx"

# Keep first run manageable. Increase after validating scheme matching.
START_DATE = date(2024, 1, 1)
END_DATE = date.today()


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


def fetch_amfi_range(start: date, end: date) -> pd.DataFrame:
    params = {
        "frmdt": start.strftime("%d-%b-%Y"),
        "todt": end.strftime("%d-%b-%Y"),
    }
    url = AMFI_URL + "?" + urlencode(params)
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    text = response.text
    rows = []
    current_amc = ""
    current_category = ""
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if ";" not in line:
            # Header/category/amc lines are not always consistently marked.
            if "Mutual Fund" in line or "Asset Management" in line:
                current_amc = line
            else:
                current_category = line
            continue
        parts = line.split(";")
        if len(parts) < 8 or parts[0] == "Scheme Code":
            continue
        rows.append(
            {
                "scheme_code": parts[0].strip(),
                "isin_div_payout": parts[1].strip(),
                "isin_growth": parts[2].strip(),
                "scheme_name_amfi": parts[3].strip(),
                "nav": parts[4].strip(),
                "date": parts[7].strip(),
                "amc_from_file": current_amc,
                "category_from_file": current_category,
            }
        )
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"], format="%d-%b-%Y", errors="coerce")
    df["nav"] = pd.to_numeric(df["nav"], errors="coerce")
    return df.dropna(subset=["date", "nav"])


def normalize(text: str) -> str:
    return " ".join(str(text).lower().replace("-", " ").replace("&", " and ").split())


def score_match(scheme_name: str, search_terms: str) -> int:
    hay = normalize(scheme_name)
    terms = normalize(search_terms).split()
    return sum(1 for term in terms if term in hay)


def choose_best_match(all_nav: pd.DataFrame, search_terms: str) -> pd.DataFrame:
    candidates = all_nav.copy()
    candidates["match_score"] = candidates["scheme_name_amfi"].apply(lambda x: score_match(x, search_terms))
    candidates = candidates[candidates["match_score"] > 0]
    if candidates.empty:
        return pd.DataFrame()
    # Prefer direct growth/growth matches when specified in search terms.
    direct_requested = "direct" in normalize(search_terms)
    growth_requested = "growth" in normalize(search_terms)
    if direct_requested:
        candidates["direct_bonus"] = candidates["scheme_name_amfi"].str.lower().str.contains("direct").astype(int)
    else:
        candidates["direct_bonus"] = 0
    if growth_requested:
        candidates["growth_bonus"] = candidates["scheme_name_amfi"].str.lower().str.contains("growth").astype(int)
    else:
        candidates["growth_bonus"] = 0
    scheme_scores = (
        candidates.groupby(["scheme_code", "scheme_name_amfi"], as_index=False)
        .agg(match_score=("match_score", "max"), direct_bonus=("direct_bonus", "max"), growth_bonus=("growth_bonus", "max"), rows=("nav", "size"))
        .sort_values(["match_score", "direct_bonus", "growth_bonus", "rows"], ascending=False)
    )
    best = scheme_scores.iloc[0]
    return all_nav[all_nav["scheme_code"] == best["scheme_code"]].copy()


def main() -> None:
    nav_map = pd.read_csv(MAP_FILE)
    frames = []
    reports: list[MatchResult] = []

    print("Downloading AMFI monthly NAV history...")
    all_months = []
    for start, end in month_ranges(START_DATE, END_DATE):
        print(f"  {start} to {end}")
        month_df = fetch_amfi_range(start, end)
        if not month_df.empty:
            all_months.append(month_df)
    if not all_months:
        raise RuntimeError("No AMFI NAV data returned.")
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
        out = pd.DataFrame(
            {
                "fund_id": fund_id,
                "scheme_name": scheme_name,
                "date": matched["date"].dt.date,
                "nav": matched["nav"],
                "source_id": "AMFI_NAV_HISTORY",
                "notes": "AMFI matched scheme: " + matched_scheme_name + " | code: " + matched_scheme_code,
            }
        )
        frames.append(out)
        reports.append(
            MatchResult(
                fund_id=fund_id,
                scheme_name=scheme_name,
                search_terms=search_terms,
                status="matched",
                matched_scheme_name=matched_scheme_name,
                matched_scheme_code=matched_scheme_code,
                rows=int(out.shape[0]),
            )
        )

    NAV_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    REPORT_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    if frames:
        pd.concat(frames, ignore_index=True).to_csv(NAV_OUTPUT, index=False)
    else:
        pd.DataFrame(columns=["fund_id", "scheme_name", "date", "nav", "source_id", "notes"]).to_csv(NAV_OUTPUT, index=False)
    pd.DataFrame([r.__dict__ for r in reports]).to_csv(REPORT_OUTPUT, index=False)
    print(f"Wrote {NAV_OUTPUT}")
    print(f"Wrote {REPORT_OUTPUT}")


if __name__ == "__main__":
    main()
