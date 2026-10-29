#!/usr/bin/env python3
"""Index existing TradingView-sourced records dated on/after the policy cutoff.

This builder only flags artifacts; it never deletes, edits, or recalculates their
values. The source-date policy is enforced separately before active use.
"""

import csv
import re
from pathlib import Path

from tradingview_policy import POLICY_EFFECTIVE_DATE, is_tradingview_source

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUTPUT = DATA / "tradingview_post_cutoff_exceptions_v1.csv"
CUTOFF = POLICY_EFFECTIVE_DATE.isoformat()
DATE_RE = re.compile(r"20\d\d-\d\d-\d\d")
SOURCE_HEADER_RE = re.compile(r"source|provider|platform|origin|provenance|url", re.I)


def _exception_row(artifact, category, count, first, last, notes):
    safe = re.sub(r"[^A-Za-z0-9]+", "-", artifact).strip("-").upper()
    return {
        "exception_id": f"TV-POST-CUTOFF-{safe}",
        "artifact": artifact,
        "record_category": category,
        "post_cutoff_record_count": str(count),
        "first_post_cutoff_date": first,
        "last_post_cutoff_date": last,
        "policy_status": "EXISTING_EXCEPTION_FLAGGED; PRESERVED; NOT_RECOMPUTED",
        "notes": notes,
    }


def scan_csv(path):
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        fieldnames = reader.fieldnames or []
        rows = list(reader)
    if not rows:
        return None
    source_fields = [name for name in fieldnames if SOURCE_HEADER_RE.search(name)]
    source_is_tv_file = is_tradingview_source(path.name)
    affected_dates = []
    affected_rows = 0
    for row in rows:
        source_evidence = [path.name] if source_is_tv_file else []
        source_evidence.extend(row.get(name, "") for name in source_fields)
        if not any(is_tradingview_source(value) for value in source_evidence):
            continue
        date_values = []
        for name, value in row.items():
            if not re.search(r"date|timestamp|time", name or "", re.I):
                continue
            date_values.extend(DATE_RE.findall(value or ""))
        post_cutoff = [value for value in date_values if value >= CUTOFF]
        if post_cutoff:
            affected_rows += 1
            affected_dates.extend(post_cutoff)
    if not affected_rows:
        return None
    category = "TradingView source/mark artifact" if source_is_tv_file else "Dataset with TradingView provenance (input or dependent output)"
    return _exception_row(
        path.relative_to(ROOT).as_posix(), category, affected_rows,
        min(affected_dates), max(affected_dates),
        "Pre-existing post-cutoff rows retained and flagged. No source rows or dependent PnL outputs were changed by this policy addition.",
    )


def scan_trade_logs(path):
    lines = path.read_text(encoding="utf-8").splitlines()
    affected = []
    for line in lines:
        match = DATE_RE.search(line)
        if not match or match.group() < CUTOFF:
            continue
        # All post-cutoff simulated paper-trade rows are flagged conservatively;
        # not every legacy line contains a platform field.
        if "SIMULATED PAPER" in line or is_tradingview_source(line):
            affected.append(match.group())
    if not affected:
        return None
    return _exception_row(
        path.relative_to(ROOT).as_posix(), "Trade-log rows", len(affected), min(affected), max(affected),
        "Post-cutoff simulated-paper/TradingView-referenced rows are preserved; some source notes do not identify the platform individually.",
    )


def scan_reports(path):
    text = path.read_text(encoding="utf-8", errors="ignore")
    if not is_tradingview_source(text):
        return None
    dates = [value for value in DATE_RE.findall(text) if value >= CUTOFF]
    if not dates:
        return None
    return _exception_row(
        path.relative_to(ROOT).as_posix(), "Dependent report/output", 1, min(dates), max(dates),
        "Existing report may depend on post-cutoff TradingView inputs. Preserved as-is pending review; this index does not recalculate it.",
    )


def scan_known_screenshots():
    known = [
        ("Archive/November_2026_Experiment_Oil_Closes_2026-10-29/IMG_1217.png", "TradingView Paper Trading oil close screenshot", "2026-10-29"),
        ("Archive/November_2026_Experiment_Oil_Closes_2026-10-29/IMG_1218.png", "TradingView Paper Trading oil close screenshot", "2026-10-29"),
        ("Archive/Private_Fund_LCID_Position/IMG_1225.png", "TradingView Paper Trading LCID order screenshot", "2026-10-29"),
    ]
    rows = []
    for artifact, category, day in known:
        if (ROOT / artifact).is_file():
            rows.append(_exception_row(
                artifact, category, 1, day, day,
                "Known screenshot retained and flagged under the post-cutoff TradingView policy; no transaction or position data recalculated.",
            ))
    return rows


def build():
    rows = []
    for path in sorted(DATA.glob("*.csv")):
        if path.name == OUTPUT.name:
            continue
        row = scan_csv(path)
        if row:
            rows.append(row)
    for path in sorted((ROOT / "trades").glob("*.txt")):
        row = scan_trade_logs(path)
        if row:
            rows.append(row)
    for directory in (ROOT, ROOT / "reports"):
        for path in sorted(directory.glob("*.md")):
            if path.name == "README.md" or path.name.startswith("TradingView Post-October 19 Block Policy") or path.name.startswith("TradingView Post-Cutoff"):
                continue
            row = scan_reports(path)
            if row:
                rows.append(row)
    rows.extend(scan_known_screenshots())
    deduped = {row["exception_id"]: row for row in rows}
    output_rows = sorted(deduped.values(), key=lambda row: (row["artifact"], row["exception_id"]))
    fields = [
        "exception_id", "artifact", "record_category", "post_cutoff_record_count",
        "first_post_cutoff_date", "last_post_cutoff_date", "policy_status", "notes",
    ]
    with OUTPUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(output_rows)
    return output_rows


if __name__ == "__main__":
    results = build()
    print(f"Flagged {len(results)} existing TradingView-dependent artifacts in {OUTPUT.relative_to(ROOT)}")
