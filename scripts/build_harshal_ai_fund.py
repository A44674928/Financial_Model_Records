#!/usr/bin/env python3
"""Build the segregated HARSHAL_PRIYAVADAN_PATEL_AI_FUND replay.

This portfolio receives the records kept out of the screened main replay:
user-approved tickers, explicitly evidenced commentary events, and the DXY
commentary-driven directional sleeve. It remains separate from the screened
portfolio, is capped at the standing October 19, 2026 TradingView cutoff, and
never overwrites the original trade logs or screened outputs.
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from influencer_ai_policy import (  # noqa: E402
    BLOCKED_TICKERS,
    MAX_TRADINGVIEW_INPUT_DATE,
    is_explicit_third_party_commentary,
)

os.environ["PAPER_TRADES_AI_FUND_REPLAY"] = "1"
import model_perf_core as core  # noqa: E402

FUND_NAME = "HARSHAL_PRIYAVADAN_PATEL_AI_FUND"
CUTOFF = MAX_TRADINGVIEW_INPUT_DATE.isoformat()
DATA = ROOT / "data"
REPORT = ROOT / "reports" / f"{FUND_NAME}.md"
DAILY_OUT = DATA / "harshal_priyavadan_patel_ai_fund_daily_v1.csv"
SUMMARY_OUT = DATA / "harshal_priyavadan_patel_ai_fund_summary_v1.json"
LEDGER_OUT = DATA / "harshal_priyavadan_patel_ai_fund_event_ledger_v1.csv"
UNPRICED_OUT = DATA / "harshal_priyavadan_patel_ai_fund_unpriced_events_v1.csv"
MANIFEST_OUT = DATA / "harshal_priyavadan_patel_ai_fund_manifest_v1.json"
FX_MARKS = DATA / "eur_jpy_usd_september_october_2026.csv"
EURUSD_ENTRY = ("2026-09-15", 1.15388)
UNIT = core.UNIT

LINE_RE = re.compile(
    r"^(?P<date>\d{4}-\d{2}-\d{2})\s+(?P<time>\d{2}:\d{2})\s+MST\s*\|\s*"
    r"SIMULATED PAPER\s+\[(?P<tag>[A-Za-z ]+?)\]\s*\|\s*"
    r"(?P<kind>entry|exit):\s*\[Market @ ~\$?(?P<px>[\d,]+\.?\d*%?)\]\s*\|\s*"
    r"size:\s*\[(?P<units>\d+(?:\.\d+)?)\s*units?[^\]]*\]\s*\|\s*"
    r"note:\s*\[(?P<note>.*)\]\s*$"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _transfer_reasons(ticker: str, note: str) -> list[str]:
    reasons = []
    if ticker in BLOCKED_TICKERS:
        reasons.append("user-approved AI-exposure ticker allocation")
    if is_explicit_third_party_commentary(note):
        reasons.append("explicit third-party/community commentary allocation")
    if ticker == "DXY":
        reasons.append("DXY directional sleeve allocation")
    return reasons


def transfer_ledger_rows():
    rows = []
    for path in sorted((ROOT / "trades").glob("*.txt")):
        if path.name == "index.txt":
            continue
        ticker = path.stem.upper()
        for line_number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            text = raw.strip()
            if not text or text.startswith("#"):
                continue
            match = LINE_RE.match(text)
            if not match:
                raise ValueError(f"Unparsed line in transfer ledger: {path.name}:{line_number}: {text}")
            day = match.group("date")
            if day > CUTOFF:
                continue
            reasons = _transfer_reasons(ticker, match.group("note"))
            if not reasons:
                continue
            record_id = hashlib.sha256(f"{path.name}\0{line_number}\0{text}".encode("utf-8")).hexdigest()[:16]
            if ticker in BLOCKED_TICKERS:
                mark_status = "MODELED_FROM_PRE_CUTOFF_TICKER_MARKS"
            elif ticker == "DXY":
                mark_status = "USED_AS_DIRECTIONAL_SLEEVE_SIGNAL; DAILY_DXY_MARKS_PRE_CUTOFF"
            elif ticker == "EURUSD":
                mark_status = "MODELED_FROM_USER-PROVIDED_RAW_FX_MARKS; SOURCE_FEED_UNVERIFIED"
            elif ticker in {"US10Y", "US30Y"}:
                mark_status = "RETAINED_IN_FUND_LEDGER; NOT_PNL-MODELED_FROM_YIELD_ONLY_QUOTES"
            else:
                mark_status = "MODELED_FROM_PRE_CUTOFF_COMMENTARY-RELATED_TICKER_MARKS"
            rows.append({
                "Record_ID": record_id,
                "Source_File": f"trades/{path.name}",
                "Line": line_number,
                "Date": day,
                "Ticker": ticker,
                "Event": match.group("kind").upper(),
                "Tag": match.group("tag").strip().upper(),
                "Logged_Price": match.group("px"),
                "Units": match.group("units"),
                "Transfer_Basis": "; ".join(reasons),
                "Marking_Status": mark_status,
                "Source_Record_Preserved": "YES",
                "Original_Note": match.group("note"),
            })
    return rows


def read_eurusd_marks():
    marks = {}
    with FX_MARKS.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            day = row["Date"].strip()
            if day <= CUTOFF:
                marks[day] = float(row["EUR_USD_Close"])
    missing = [day for day in core.SESSION_DATES if day >= EURUSD_ENTRY[0] and day not in marks]
    if missing:
        raise ValueError(f"User-provided EURUSD mark file lacks fund sessions: {missing}")
    return marks


def add_eurusd_leg(series, marks):
    """Add the documented 1U EURUSD LONG using raw user-provided daily marks."""
    entry_day, entry_px = EURUSD_ENTRY
    entry_idx = core.session_index(entry_day, "entry")
    for variant in core.VARIANTS:
        model = series[variant]
        for idx in range(entry_idx, len(core.SESSION_DATES)):
            pnl = UNIT * (marks[core.SESSION_DATES[idx]] / entry_px - 1.0)
            model["unrealized"][idx] += pnl
            model["total"][idx] += pnl
            model["deployed"][idx] += UNIT
            model["open_units"][idx] += 1.0
            model["roi"][idx] = 100.0 * model["total"][idx] / model["deployed"][idx]
        model["lots"].append({
            "sym": "EURUSD", "side": "long", "qty": 1.0,
            "entry_px": entry_px, "entry_date": entry_day,
            "open": True, "mark_source": FX_MARKS.name,
        })


def build_unpriced_rows(ledger_rows):
    return [row for row in ledger_rows if row["Ticker"] in {"US10Y", "US30Y"}]


def main():
    ledger = transfer_ledger_rows()
    core_events = core.parse_trades()
    series = {variant: core.daily_series(variant, core_events) for variant in core.VARIANTS}
    fx_marks = read_eurusd_marks()
    add_eurusd_leg(series, fx_marks)
    unpriced = build_unpriced_rows(ledger)

    daily_fields = ["Date", "Variant", "Realized_PnL_USD", "Unrealized_PnL_USD", "Total_PnL_USD",
                    "ROI_Pct", "Deployed_Notional_USD", "Open_Units"]
    with DAILY_OUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=daily_fields)
        writer.writeheader()
        for variant in core.VARIANTS:
            model = series[variant]
            for index, day in enumerate(model["dates"]):
                writer.writerow({
                    "Date": day,
                    "Variant": variant,
                    "Realized_PnL_USD": f"{model['realized'][index]:.2f}",
                    "Unrealized_PnL_USD": f"{model['unrealized'][index]:.2f}",
                    "Total_PnL_USD": f"{model['total'][index]:.2f}",
                    "ROI_Pct": f"{model['roi'][index]:.6f}",
                    "Deployed_Notional_USD": f"{model['deployed'][index]:.2f}",
                    "Open_Units": f"{model['open_units'][index]:.6f}",
                })

    ledger_fields = ["Record_ID", "Source_File", "Line", "Date", "Ticker", "Event", "Tag",
                     "Logged_Price", "Units", "Transfer_Basis", "Marking_Status",
                     "Source_Record_Preserved", "Original_Note"]
    with LEDGER_OUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=ledger_fields)
        writer.writeheader()
        writer.writerows(ledger)
    with UNPRICED_OUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=ledger_fields)
        writer.writeheader()
        writer.writerows(unpriced)

    summary = {
        "portfolio_name": FUND_NAME,
        "portfolio_type": "segregated simulated paper-model portfolio",
        "replay_start_date": core.SESSION_DATES[0],
        "replay_end_date": core.SESSION_DATES[-1],
        "standing_tradingview_last_allowed_date": CUTOFF,
        "ticker_screen": sorted(BLOCKED_TICKERS),
        "commentary_event_rows_transferred": sum(
            "explicit third-party/community commentary allocation" in row["Transfer_Basis"]
            for row in ledger
        ),
        "ticker_event_rows_transferred": sum(
            "user-approved AI-exposure ticker allocation" in row["Transfer_Basis"]
            for row in ledger
        ),
        "dxy_signal_rows_transferred": sum(
            "DXY directional sleeve allocation" in row["Transfer_Basis"]
            for row in ledger
        ),
        "unique_transfer_rows": len(ledger),
        "unique_transfer_rows_note": "A record can have multiple transfer bases but is counted once in the event ledger.",
        "direct_price_tickers_modeled": sorted(core.PRICES),
        "eurusd_modeled": True,
        "eurusd_mark_source": "User-provided raw close series; provider/feed and close convention not independently verified.",
        "dxy_directional_sleeve_modeled": True,
        "dxy_sleeve_method": "One 1U ($10,000 notional) lot per active session under the carried logged direction; included once, not again as a separate DXY entry lot.",
        "yield_events_retained_but_not_pnl_modeled": len(unpriced),
        "post_cutoff_tradingview_inputs_used": 0,
        "cash_and_leverage_convention": "All-cash/debit simulation; no funding source, leverage, financing, or actual brokerage execution inferred.",
        "variants": {},
    }
    for variant in core.VARIANTS:
        model = series[variant]
        summary["variants"][variant] = {
            "label": core.VARIANT_LABEL[variant],
            "realized_pnl_usd": round(model["realized"][-1], 2),
            "unrealized_pnl_usd": round(model["unrealized"][-1], 2),
            "total_pnl_usd": round(model["total"][-1], 2),
            "roi_pct": round(model["roi"][-1], 6),
            "deployed_notional_usd": round(model["deployed"][-1], 2),
            "open_units": round(model["open_units"][-1], 6),
            "modeled_lot_count": len(model["lots"]),
        }
    SUMMARY_OUT.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    source_paths = [core.BENCHMARK_SESSION_FILE, FX_MARKS]
    source_paths += [path for path in sorted((ROOT / "trades").glob("*.txt")) if path.name != "index.txt"]
    manifest = {
        "version": 1,
        "portfolio_name": FUND_NAME,
        "builder": "scripts/build_harshal_ai_fund.py",
        "cutoff": CUTOFF,
        "source_hashes_sha256": {str(path.relative_to(ROOT)): sha256(path) for path in source_paths},
        "outputs": [str(path.relative_to(ROOT)) for path in (DAILY_OUT, SUMMARY_OUT, LEDGER_OUT, UNPRICED_OUT, REPORT, MANIFEST_OUT)],
        "screened_main_portfolio_remains_separate": True,
    }
    MANIFEST_OUT.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    lines = [
        f"# {FUND_NAME}",
        "",
        "> Segregated, hypothetical paper-model portfolio containing records kept out of the screened main replay. This is a portfolio allocation, not a claim of a funded legal entity or actual brokerage account.",
        "",
        "## Transfer scope and separation",
        "",
        "- Receives all pre-cutoff ledger events for the seven user-approved tickers: " + ", ".join(f"`{ticker}`" for ticker in sorted(BLOCKED_TICKERS)) + ".",
        "- Receives explicitly evidenced third-party/community commentary events on other modeled instruments. Where a record also belongs to one of the seven tickers, it is transferred once and carries both reasons in the event ledger.",
        "- Receives the DXY directional sleeve as a single segregated component. Its source signal is retained in the transfer ledger; the sleeve is not duplicated as a separate DXY entry lot.",
        f"- Uses sessions through **{CUTOFF}** only, preserving the standing TradingView cutoff. No October 20-or-later TradingView inputs were used.",
        "- The screened main replay remains separate and unchanged. The policy block remains in force for other portfolios; this is the user-requested segregated portfolio for the excluded records.",
        "",
        "## Recomputed fund results",
        "",
        "| Variant | Realized PnL | Unrealized PnL | Total PnL | ROI | Deployed notional | Open units |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for variant in core.VARIANTS:
        item = summary["variants"][variant]
        lines.append(
            f"| {variant} — {item['label']} | ${item['realized_pnl_usd']:,.2f} | ${item['unrealized_pnl_usd']:,.2f} | "
            f"${item['total_pnl_usd']:,.2f} | {item['roi_pct']:.4f}% | ${item['deployed_notional_usd']:,.2f} | {item['open_units']:,.4f} |"
        )
    lines += [
        "",
        "The four variants retain their existing definitions from the core model. These are not brokerage results, realized cash balances, or a statement of actual funding. The all-cash/debit convention remains in force; no leverage or financing is inferred.",
        "",
        "## Transfer and valuation ledger",
        "",
        f"- Unique pre-cutoff event records transferred: **{len(ledger)}**; ticker event rows: **{summary['ticker_event_rows_transferred']}**; explicit commentary rows: **{summary['commentary_event_rows_transferred']}**; DXY signal rows: **{summary['dxy_signal_rows_transferred']}**. Category counts overlap.",
        f"- US10Y/US30Y yield-only event rows retained but not included in PnL: **{len(unpriced)}**. A yield quote is not a bond price; no duration, futures contract, or yield-to-price conversion is inferred. See [unpriced event register](../data/harshal_priyavadan_patel_ai_fund_unpriced_events_v1.csv).",
        "- EURUSD is modeled as a 1U LONG from the logged 2026-09-15 entry using the user-provided daily close series through October 19. The provider/feed and close convention are not independently verified; this leg is identified separately in the builder and manifest.",
        "- [Transferred event ledger](../data/harshal_priyavadan_patel_ai_fund_event_ledger_v1.csv), [daily replay](../data/harshal_priyavadan_patel_ai_fund_daily_v1.csv), [summary JSON](../data/harshal_priyavadan_patel_ai_fund_summary_v1.json), and [SHA-256 manifest](../data/harshal_priyavadan_patel_ai_fund_manifest_v1.json) preserve lineage.",
        "",
        "The user trade logs and prior screened outputs remain unchanged. These portfolio results do not reverse or reinterpret any actual transaction, funding source, or source record; they only segregate and replay the specified historical records.",
        "",
    ]
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Built {FUND_NAME}: {len(ledger)} transfer rows; {len(core.SESSION_DATES)} sessions through {CUTOFF}.")
    for variant in core.VARIANTS:
        item = summary["variants"][variant]
        print(f"{variant}: total PnL ${item['total_pnl_usd']:,.2f}; ROI {item['roi_pct']:.4f}%")


if __name__ == "__main__":
    main()
