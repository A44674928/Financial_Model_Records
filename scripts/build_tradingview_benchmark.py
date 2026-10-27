#!/usr/bin/env python3
"""Merge Part A/B lists and align the interim TradingView benchmark.

No external price source is used. The five gaps in XRH0 are carried forward
from the previous user-supplied TradingView close and are flagged in the
session-mark table. BTC/ETH remain pending and outside the core universe.
"""

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

from model_perf_core import PRICES, SESSION_DATES

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
PART_A = DATA / "tradingview_benchmark_price_lists_part_a_20261024.csv"
PART_B = DATA / "tradingview_benchmark_price_lists_part_b_20261024.csv"
COMBINED = DATA / "tradingview_benchmark_price_lists_20261024.csv"
EOD_UPDATE = DATA / "tradingview_eod_marks_20261026.csv"
SESSION_MARKS = DATA / "tradingview_benchmark_session_marks_20261026.csv"
COVERAGE = DATA / "tradingview_benchmark_coverage_20261026.csv"
MANIFEST = DATA / "tradingview_benchmark_source_manifest_20261026.json"
PENDING_CRYPTO = {"BTC", "ETH"}
DXY = "DXY"


def _read(path):
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def build():
    part_a = _read(PART_A)
    part_b = _read(PART_B)
    raw_rows = part_a + part_b
    raw_by_key = {}
    by_ticker = defaultdict(dict)
    for row in raw_rows:
        key = (row["Ticker"], row["Date"])
        if key in raw_by_key:
            raise AssertionError(f"Duplicate TradingView price-list observation: {key}")
        raw_by_key[key] = row
        by_ticker[row["Ticker"]][row["Date"]] = row

    update_rows = _read(EOD_UPDATE)
    supplied_updates = [row for row in update_rows if row["Status"] == "supplied"]
    expected_update_symbols = set(PRICES) | {DXY}
    if (
        len(supplied_updates) != len(expected_update_symbols)
        or {row["Ticker"].strip().upper() for row in supplied_updates} != expected_update_symbols
        or {row["Date"].strip() for row in supplied_updates} != {"2026-10-26"}
    ):
        raise AssertionError("The 2026-10-26 update must contain all 31 core marks and DXY exactly once")
    for row in supplied_updates:
        ticker, day = row["Ticker"].strip().upper(), row["Date"].strip()
        if day in by_ticker[ticker]:
            raise AssertionError(f"Duplicate supplied TradingView update: {ticker} {day}")
        close = float(row["EOD_Close"])
        if close <= 0:
            raise AssertionError(f"Nonpositive supplied close for {ticker} on {day}")
        by_ticker[ticker][day] = {
            "Ticker": ticker,
            "Date": day,
            "Close": f"{close:.8f}",
            "Source_File": EOD_UPDATE.name,
            "Source_File_URL": "",
            "Archive_SHA256": "",
        }

    core_symbols = set(PRICES) - PENDING_CRYPTO
    missing_core_files = core_symbols - set(by_ticker)
    unexpected_core_files = (set(by_ticker) - {DXY}) - set(PRICES)
    if missing_core_files or unexpected_core_files:
        raise AssertionError(f"Core price coverage mismatch: missing={sorted(missing_core_files)} unexpected={sorted(unexpected_core_files)}")
    if DXY not in by_ticker or not PENDING_CRYPTO.isdisjoint(by_ticker):
        raise AssertionError("DXY must be present, while BTC/ETH must remain pending")

    with COMBINED.open("w", newline="", encoding="utf-8") as handle:
        fields = list(raw_rows[0])
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(sorted(raw_rows, key=lambda row: (row["Ticker"], row["Date"])))

    session_rows = []
    coverage_rows = []
    for ticker in sorted(core_symbols | {DXY}):
        supplied = by_ticker[ticker]
        last_price = None
        last_source_date = None
        source_dates = sorted(supplied)
        missing_sessions = [day for day in SESSION_DATES if day not in supplied]
        if ticker == DXY and missing_sessions:
            raise AssertionError(f"DXY sidecar is missing comparison sessions: {missing_sessions}")
        if ticker != "XRH0" and missing_sessions:
            raise AssertionError(f"{ticker} is missing supplied comparison marks: {missing_sessions}")
        if ticker == "XRH0" and not source_dates:
            raise AssertionError("XRH0 has no user-provided observations")

        for day in SESSION_DATES:
            source = supplied.get(day)
            if source:
                close = float(source["Close"])
                mark_status = "provided_tradingview_close"
                source_file = source["Source_File"]
                source_url = source["Source_File_URL"]
                archive_sha = source["Archive_SHA256"]
                last_price = close
                last_source_date = day
            else:
                if ticker != "XRH0" or last_price is None:
                    raise AssertionError(f"No permitted mark for {ticker} on {day}")
                close = last_price
                mark_status = f"carry_forward_from_{last_source_date}"
                prior = supplied[last_source_date]
                source_file = prior["Source_File"]
                source_url = prior["Source_File_URL"]
                archive_sha = prior["Archive_SHA256"]
            session_rows.append({
                "Ticker": ticker,
                "Date": day,
                "Close": f"{close:.8f}",
                "Mark_Status": mark_status,
                "Source_File": source_file,
                "Source_File_URL": source_url,
                "Archive_SHA256": archive_sha,
            })

        role = "currency_desk_sidecar" if ticker == DXY else "core_price_symbol"
        if ticker == "XRH0":
            status = "complete_with_user_TV_carry_forward"
        else:
            status = "complete_source_marks"
        coverage_rows.append({
            "Ticker": ticker,
            "Role": role,
            "Coverage_Status": status,
            "Provided_Source_Rows": len(supplied),
            "Comparison_Session_Rows": len(SESSION_DATES),
            "Missing_Comparison_Sessions": ";".join(missing_sessions),
            "First_Provided_Date": source_dates[0],
            "Last_Provided_Date": source_dates[-1],
            "2026-10-23_Close": f"{float(supplied['2026-10-23']['Close']):.8f}" if "2026-10-23" in supplied else "",
            "Source_Files": ";".join(sorted({r["Source_File"] for r in supplied.values()})),
        })

    for ticker in sorted(PENDING_CRYPTO):
        coverage_rows.append({
            "Ticker": ticker,
            "Role": "pending_crypto_sidecar",
            "Coverage_Status": "pending_tradingview_recalibration",
            "Provided_Source_Rows": 0,
            "Comparison_Session_Rows": 0,
            "Missing_Comparison_Sessions": ";".join(SESSION_DATES),
            "First_Provided_Date": "",
            "Last_Provided_Date": "",
            "2026-10-23_Close": "",
            "Source_Files": "",
        })

    with SESSION_MARKS.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(session_rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(session_rows)
    with COVERAGE.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(coverage_rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(sorted(coverage_rows, key=lambda row: row["Ticker"]))

    part_a_sha = hashlib.sha256((DATA / "benchmark_tradingview_price_lists_source_20261024.zip").read_bytes()).hexdigest()
    part_b_sha = hashlib.sha256((DATA / "benchmark_tradingview_price_lists_part_b_source_20261024.zip").read_bytes()).hexdigest()
    manifest = {
        "benchmark_name": "User-provided TradingView benchmark — Parts A and B",
        "comparison_session_count": len(SESSION_DATES),
        "comparison_session_start": SESSION_DATES[0],
        "comparison_session_end": SESSION_DATES[-1],
        "core_symbol_count": len(core_symbols),
        "core_symbols": sorted(core_symbols),
        "dxy_sidecar_symbol": DXY,
        "pending_crypto_symbols": sorted(PENDING_CRYPTO),
        "pending_crypto_status": "Pending TradingView recalibration; excluded from core package and no PnL is calculated",
        "raw_price_rows": len(raw_rows),
        "aligned_session_mark_rows": len(session_rows),
        "part_a_archive_sha256": part_a_sha,
        "part_b_archive_sha256": part_b_sha,
        "raw_price_data_path": str(COMBINED.relative_to(ROOT)),
        "supplemental_eod_update_path": str(EOD_UPDATE.relative_to(ROOT)),
        "supplemental_eod_update_date": "2026-10-26",
        "supplemental_eod_update_mark_count": len(supplied_updates),
        "aligned_session_marks_path": str(SESSION_MARKS.relative_to(ROOT)),
        "coverage_path": str(COVERAGE.relative_to(ROOT)),
        "latest_direct_price_date": SESSION_DATES[-1],
        "source_reconciliation": {
            "LLY": "The updated Part B archive supplies a 2026-10-20 close of 1283.66, replacing the prior archive's 12833.66 mark; all downstream outputs use the updated row.",
            "XRH0": "Five missing common-session marks are carried forward from the previous supplied TradingView close; each row is explicitly flagged.",
            "DXY": "Provided in Part B through Oct. 23 and supplemented with the user-provided TradingView Oct. 26 close of 102.017; its chart-directed 1U/DAY index-return sleeve is integrated into each core portfolio variant, not double-counted.",
            "BTC_ETH": "No legacy Yahoo or previous project marks enter the core model or pending sidecar calculations.",
        },
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def main():
    result = build()
    print(f"Combined {result['raw_price_rows']} user-provided price observations for {result['core_symbol_count']} core symbols and DXY.")
    print(f"Aligned {result['aligned_session_mark_rows']} session marks across {result['comparison_session_count']} sessions.")
    print("BTC and ETH remain outside the core benchmark, pending TradingView recalibration.")
    print(f"Wrote {COVERAGE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
