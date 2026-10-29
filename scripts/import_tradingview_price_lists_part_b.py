#!/usr/bin/env python3
"""Normalize the user-provided Part B TradingView price-list archive."""

import argparse
import csv
import hashlib
import json
import re
import zipfile
from pathlib import Path
from urllib.parse import quote

from import_tradingview_price_lists import _parse_price_file, _ticker_from_filename
from model_perf_core import BASE_SESSION_DATES as SESSION_DATES, PRICES
from tradingview_policy import (
    POLICY_EFFECTIVE_DATE,
    STATUS_BLOCKED,
    STATUS_LEGACY_EXCEPTION,
    classify_existing_record,
    classify_source_date,
)

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
ARCHIVE = DATA / "benchmark_tradingview_price_lists_part_b_source_20261024.zip"
REPO = "A44674928/Financial_Model_Records"
COMMIT = "d5228326d034c8d515f1a8ca1c484c70c738904f"
ARCHIVE_URL = (
    "https://github.com/A44674928/Financial_Model_Records/blob/main/"
    "PART%20B%20PRICE%20LISTS%20TRADING%20VIEW.zip"
)
PRICE_CSV = DATA / "tradingview_benchmark_price_lists_part_b_20261024.csv"
COVERAGE_CSV = DATA / "tradingview_benchmark_coverage_part_b_20261024.csv"
MANIFEST_JSON = DATA / "tradingview_benchmark_source_manifest_part_b_20261024.json"
EXPECTED_PART_B = (set(PRICES) - {"BTC", "ETH", "BRENT", "OIL", "CAT", "GEV", "HD", "INTC", "LCID", "LMT", "LULU", "META", "ORCL", "PLTR", "SPCX", "TSLA", "VLO"}) | {"DXY"}


def import_part_b(*, allow_flagged_legacy=False):
    """Import the pinned archive; post-cutoff records need an explicit audit override."""
    if not ARCHIVE.is_file():
        raise FileNotFoundError(ARCHIVE)
    archive_sha = hashlib.sha256(ARCHIVE.read_bytes()).hexdigest()
    file_rows = {}
    source_names = {}
    all_rows = []
    with zipfile.ZipFile(ARCHIVE) as archive:
        for member in archive.infolist():
            if member.is_dir() or member.filename.startswith("__MACOSX/"):
                continue
            name = Path(member.filename).name
            ticker = _ticker_from_filename(name)
            if ticker is None:
                continue
            if ticker not in EXPECTED_PART_B:
                raise ValueError(f"Unexpected Part B ticker file: {ticker} ({name})")
            if ticker in file_rows:
                raise ValueError(f"Duplicate Part B list for {ticker}")
            parsed = _parse_price_file(name, archive.read(member))
            file_rows[ticker] = parsed
            source_names[ticker] = name
            file_url = f"https://github.com/{REPO}/blob/{COMMIT}/" + quote(member.filename)
            label = "TVC:DXY" if ticker == "DXY" else ("TVC:USOIL" if ticker == "OIL" else ticker)
            for day, close in parsed:
                status = classify_source_date("TradingView", day)
                if status == STATUS_BLOCKED:
                    if not allow_flagged_legacy:
                        raise ValueError(
                            f"TradingView input dated {day} is blocked by the post-2026-10-19 policy; "
                            "use the existing-exception audit path only when preserving the pinned archive."
                        )
                    status = classify_existing_record("TradingView", day)
                all_rows.append({
                    "Ticker": ticker,
                    "Date": day,
                    "Close": f"{close:.8f}",
                    "TradingView_Label": label,
                    "Source_File": name,
                    "Source_File_URL": file_url,
                    "Archive_SHA256": archive_sha,
                    "Policy_Status": status,
                })

    if set(file_rows) != EXPECTED_PART_B:
        raise AssertionError(f"Part B coverage mismatch; missing {sorted(EXPECTED_PART_B - set(file_rows))}; unexpected {sorted(set(file_rows) - EXPECTED_PART_B)}")

    coverage = []
    for ticker in sorted(EXPECTED_PART_B):
        values = file_rows[ticker]
        by_date = dict(values)
        missed = [day for day in SESSION_DATES if day not in by_date]
        status = "complete_for_comparison_sessions" if not missed else "source_has_session_gaps"
        coverage.append({
            "Ticker": ticker,
            "Coverage_Status": status,
            "Source_File": source_names[ticker],
            "Source_Row_Count": len(values),
            "Comparison_Session_Rows": len(SESSION_DATES) - len(missed),
            "Missing_Comparison_Sessions": ";".join(missed),
            "First_Provided_Date": values[0][0],
            "Last_Provided_Date": values[-1][0],
            "2026-10-23_Close": f"{by_date['2026-10-23']:.8f}" if "2026-10-23" in by_date else "",
            "Source": "User-provided TradingView price list",
            "Policy_Status": (
                STATUS_LEGACY_EXCEPTION
                if any(day >= POLICY_EFFECTIVE_DATE.isoformat() for day, _ in values)
                else "ALLOWED_PRE_CUTOFF"
            ),
        })

    PRICE_CSV.parent.mkdir(parents=True, exist_ok=True)
    with PRICE_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(all_rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(sorted(all_rows, key=lambda row: (row["Ticker"], row["Date"])))
    with COVERAGE_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(coverage[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(coverage)

    manifest = {
        "benchmark_name": "User-provided TradingView price lists — Part B",
        "source_archive_url": ARCHIVE_URL,
        "source_archive_path": str(ARCHIVE.relative_to(ROOT)),
        "source_archive_sha256": archive_sha,
        "source_repository_commit": COMMIT,
        "price_data_path": str(PRICE_CSV.relative_to(ROOT)),
        "coverage_path": str(COVERAGE_CSV.relative_to(ROOT)),
        "comparison_session_count": len(SESSION_DATES),
        "tradingview_policy_cutoff_date": POLICY_EFFECTIVE_DATE.isoformat(),
        "flagged_post_cutoff_rows": sum(row["Policy_Status"] == STATUS_LEGACY_EXCEPTION for row in all_rows),
        "legacy_exception_preservation_override": bool(allow_flagged_legacy),
        "provided_symbols": sorted(file_rows),
        "provided_symbol_count": len(file_rows),
        "missing_comparison_sessions": {row["Ticker"]: row["Missing_Comparison_Sessions"].split(";") for row in coverage if row["Missing_Comparison_Sessions"]},
        "notes": [
            "Post-2026-10-19 TradingView rows are blocked by default; the explicit legacy override only preserves and flags existing rows for audit.",
            "Updated Part B archive is pinned to the recorded repository commit; it corrects the LLY 2026-10-20 source close to 1283.66 (superseding the prior archive's 12833.66).",
            "DXY is a separate non-equity index mark; its chart-directed 1U/DAY sleeve is integrated into core portfolio PnL rather than treated as a direct-price ticker.",
            "The XRH0 list has five missing dates on the common session calendar; no external prices are inserted. The interim model carries forward the previous supplied TradingView mark on those dates and flags each carry-forward.",
            "BTC and ETH are intentionally absent from Part B and remain pending TradingView recalibration outside the core comparison.",
        ],
    }
    MANIFEST_JSON.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--preserve-flagged-legacy", action="store_true",
        help="Preserve pinned post-cutoff rows for audit only; flags them as ineligible for active use.",
    )
    args = parser.parse_args()
    result = import_part_b(allow_flagged_legacy=args.preserve_flagged_legacy)
    print(f"Imported {result['provided_symbol_count']} Part B lists: {len(_read(PRICE_CSV))} raw price rows.")
    for ticker, dates in result["missing_comparison_sessions"].items():
        print(f"{ticker}: {len(dates)} missing comparison-session marks ({', '.join(dates)})")
    print(f"Wrote {PRICE_CSV.relative_to(ROOT)}")
    print(f"Wrote {COVERAGE_CSV.relative_to(ROOT)}")
    print(f"Wrote {MANIFEST_JSON.relative_to(ROOT)}")


def _read(path):
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


if __name__ == "__main__":
    main()
