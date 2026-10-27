#!/usr/bin/env python3
"""Normalize the supplied TradingView price-list RTFs without filling gaps.

The input archive is the user-provided GitHub artifact, retained byte-for-byte in
`data/benchmark_tradingview_price_lists_source_20261024.zip`. The example RTF
and macOS metadata files are intentionally not treated as price data.
Run with: PYTHONPATH=scripts python3 scripts/import_tradingview_price_lists.py
"""

import csv
import hashlib
import json
import re
import zipfile
from datetime import date
from pathlib import Path
from urllib.parse import quote

from model_perf_core import BASE_SESSION_DATES as SESSION_DATES, PRICES

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
ARCHIVE = DATA / "benchmark_tradingview_price_lists_source_20261024.zip"
REPO = "A44674928/Financial_Model_Records"
COMMIT = "22540a55b08214460bb6cd7e64d8174c1ee1e1c2"
USER_ARCHIVE_URL = (
    "https://github.com/A44674928/Financial_Model_Records/blob/main/"
    "PART%20A%20PRICE%20LISTS%20TRADING%20VIEW.zip"
)
PRICE_CSV = DATA / "tradingview_benchmark_price_lists_part_a_20261024.csv"
COVERAGE_CSV = DATA / "tradingview_benchmark_coverage_part_a_20261024.csv"
MANIFEST_JSON = DATA / "tradingview_benchmark_source_manifest_part_a_20261024.json"
MONTHS = {"september": 9, "october": 10}


def _text_from_rtf(data):
    text = data.decode("cp1252")
    text = re.sub(r"\\\r?\n", "\n", text)
    text = re.sub(r"\\[a-zA-Z]+-?\d*\s?", " ", text)
    text = re.sub(r"\\([{}\\])", r"\1", text)
    return text.replace("{", " ").replace("}", " ")


def _ticker_from_filename(filename):
    match = re.match(r"^([A-Z0-9]+) PRICE (?:LIST|CHART) \(TRADINGVIEW\)\.rtf$", filename)
    if not match:
        return None
    ticker = match.group(1)
    return "OIL" if ticker == "USOIL" else ticker


def _parse_price_file(filename, data):
    text = _text_from_rtf(data)
    month = None
    rows = []
    for line in text.splitlines():
        line = line.strip()
        month_match = re.fullmatch(r"(September|October)", line, flags=re.IGNORECASE)
        if month_match:
            month = MONTHS[month_match.group(1).lower()]
            continue
        value_match = re.fullmatch(r"(\d{1,2})\s+\$?([\d,]+(?:\.\d+)?)", line)
        if not month or not value_match:
            continue
        day = int(value_match.group(1))
        close = float(value_match.group(2).replace(",", ""))
        dt = date(2026, month, day).isoformat()
        if close <= 0:
            raise ValueError(f"Non-positive close in {filename}: {line}")
        rows.append((dt, close))
    if not rows:
        raise ValueError(f"No daily closes parsed from {filename}")
    dates = [row[0] for row in rows]
    if dates != sorted(set(dates)):
        raise ValueError(f"Duplicate or out-of-order dates in {filename}")
    return rows


def import_archive():
    if not ARCHIVE.is_file():
        raise FileNotFoundError(ARCHIVE)
    archive_bytes = ARCHIVE.read_bytes()
    archive_sha256 = hashlib.sha256(archive_bytes).hexdigest()
    source_rows = []
    file_coverage = {}
    source_files = {}

    with zipfile.ZipFile(ARCHIVE) as bundle:
        for member in bundle.infolist():
            name = Path(member.filename).name
            ticker = _ticker_from_filename(name)
            if not ticker or member.is_dir() or member.filename.startswith("__MACOSX/"):
                continue
            if ticker not in PRICES:
                raise ValueError(f"Price-list file names an unknown model ticker: {ticker}")
            if ticker in file_coverage:
                raise ValueError(f"Multiple user price lists map to the same model ticker: {ticker}")
            parsed = _parse_price_file(name, bundle.read(member))
            source_files[ticker] = name
            file_coverage[ticker] = parsed
            source_file_url = (
                f"https://github.com/{REPO}/blob/{COMMIT}/" + quote(name)
            )
            tradingview_symbol = "TVC:USOIL" if ticker == "OIL" else ticker
            for day, close in parsed:
                source_rows.append({
                    "Ticker": ticker,
                    "Date": day,
                    "Close": f"{close:.8f}",
                    "TradingView_Label": tradingview_symbol,
                    "Source_File": name,
                    "Source_File_URL": source_file_url,
                    "Archive_SHA256": archive_sha256,
                })

    ticker_coverage = []
    for ticker in sorted(PRICES):
        values = file_coverage.get(ticker, [])
        by_date = dict(values)
        expected_session_dates = [day for day in SESSION_DATES if day in by_date]
        missing_sessions = [day for day in SESSION_DATES if day not in by_date]
        ticker_coverage.append({
            "Ticker": ticker,
            "Coverage_Status": "complete_for_comparison_sessions" if not missing_sessions and values else "missing_user_price_list",
            "Source_File": source_files.get(ticker, ""),
            "Source_Row_Count": len(values),
            "Comparison_Session_Rows": len(expected_session_dates),
            "Missing_Comparison_Sessions": ";".join(missing_sessions) if values else "all 36 sessions (no supplied list)",
            "First_Provided_Date": values[0][0] if values else "",
            "Last_Provided_Date": values[-1][0] if values else "",
            "2026-10-23_Close": f"{by_date['2026-10-23']:.8f}" if "2026-10-23" in by_date else "",
            "Source": "User-provided TradingView price list" if values else "Awaiting user-provided ticker data; not to be substituted",
        })

    missing = [row["Ticker"] for row in ticker_coverage if row["Coverage_Status"] != "complete_for_comparison_sessions"]
    if len(missing) != 16:
        raise AssertionError(f"Expected 16 core symbols awaiting Part B data, found {len(missing)}: {missing}")
    for ticker, values in file_coverage.items():
        dates = {day for day, _ in values}
        missing_dates = [day for day in SESSION_DATES if day not in dates]
        if missing_dates:
            raise AssertionError(f"Supplied {ticker} list is missing comparison dates: {missing_dates}")
        if "2026-10-23" not in dates:
            raise AssertionError(f"Supplied {ticker} list has no Oct. 23 terminal mark")

    PRICE_CSV.parent.mkdir(parents=True, exist_ok=True)
    with PRICE_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(source_rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(sorted(source_rows, key=lambda row: (row["Ticker"], row["Date"])))
    with COVERAGE_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(ticker_coverage[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(ticker_coverage)

    manifest = {
        "benchmark_name": "User-provided TradingView price lists",
        "source_archive_url": USER_ARCHIVE_URL,
        "source_archive_path": str(ARCHIVE.relative_to(ROOT)),
        "source_archive_sha256": archive_sha256,
        "source_repository_commit": COMMIT,
        "price_data_path": str(PRICE_CSV.relative_to(ROOT)),
        "coverage_path": str(COVERAGE_CSV.relative_to(ROOT)),
        "model_comparison_sessions": [SESSION_DATES[0], SESSION_DATES[-1]],
        "model_comparison_session_count": len(SESSION_DATES),
        "provided_symbols": sorted(file_coverage),
        "provided_symbol_count": len(file_coverage),
        "missing_symbols": missing,
        "missing_symbol_count": len(missing),
        "excluded_archive_entries": [
            "TICKER PRICE LIST (EXAMPLE).rtf (template/example, not a ticker-specific file)",
            "__MACOSX/ metadata entries",
        ],
        "notes": [
            "No missing ticker prices are filled from Yahoo Finance or earlier project data.",
            "The September 7 Brent observation is preserved in the normalized source CSV but is outside the 36-session U.S. equity comparison calendar.",
            "The GEV source filename is ticker-specific; its RTF body heading reads TICKER and the filename is used as the symbol key.",
            "Part A covers 15 of 31 direct-price core symbols; Part B supplies the remaining 16. BTC and ETH are excluded from the core and remain pending TradingView recalibration.",
        ],
    }
    MANIFEST_JSON.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def main():
    manifest = import_archive()
    print(f"Imported {manifest['provided_symbol_count']} ticker-specific TradingView lists and {len(_read_rows(PRICE_CSV))} daily price rows.")
    print(f"Part A coverage: {manifest['provided_symbol_count']}/31 core symbols; {manifest['missing_symbol_count']} core lists are supplied in Part B. BTC/ETH remain pending separately.")
    print(f"Wrote {PRICE_CSV.relative_to(ROOT)}")
    print(f"Wrote {COVERAGE_CSV.relative_to(ROOT)}")
    print(f"Wrote {MANIFEST_JSON.relative_to(ROOT)}")


def _read_rows(path):
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


if __name__ == "__main__":
    main()
