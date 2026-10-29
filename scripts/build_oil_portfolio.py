#!/usr/bin/env python3
"""Build a segregated Oil portfolio from all recorded oil/energy trade books.

The active replay uses only allowed pre-October-20, 2026 marks. Later log rows
and separate-book screenshot/liquidation records remain in audit registers and
are not silently revalued or consolidated.
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

from influencer_ai_policy import MAX_TRADINGVIEW_INPUT_DATE  # noqa: E402

os.environ["PAPER_TRADES_OIL_PORTFOLIO_REPLAY"] = "1"
import model_perf_core as core  # noqa: E402

PORTFOLIO_NAME = "Oil"
CUTOFF = MAX_TRADINGVIEW_INPUT_DATE.isoformat()
DATA = ROOT / "data"
REPORT = ROOT / "reports" / "Oil Portfolio.md"
DAILY_OUT = DATA / "oil_portfolio_daily_v1.csv"
LEDGER_OUT = DATA / "oil_portfolio_trade_ledger_v1.csv"
RELATED_OUT = DATA / "oil_portfolio_related_book_records_v1.csv"
SUMMARY_OUT = DATA / "oil_portfolio_summary_v1.json"
MANIFEST_OUT = DATA / "oil_portfolio_manifest_v1.json"
ATS_LIQUIDATIONS = DATA / "ats_oil_liquidation_reported_v1.csv"
PRIVATE_FUND_REPORT = ROOT / "reports" / "Harshal's Private Fund — November 2026++ Experiment.md"

# Direct crude records plus clearly energy/oil-linked equity trade logs present
# in this repository. Equity positions are shown as a separate sleeve in the
# report so they are not mistaken for barrel exposure.
OIL_BOOK_TICKERS = frozenset({"BRENT", "OIL", "CVX", "VLO", "XLE"})
CRUDE_TICKERS = frozenset({"BRENT", "OIL"})
ENERGY_EQUITY_TICKERS = frozenset({"CVX", "VLO", "XLE"})

# Supplementary records are kept at their original book/account boundary. The
# values are copied from the existing report, not added to the core replay.
PRIVATE_SCREENSHOT_RECORDS = [
    {
        "source_record_id": "PRIVATE_TV_BRENT_CLOSE_20261029",
        "source_book": "Harshal's Private Fund — TradingView Paper Trading screenshots",
        "date": "2026-10-29",
        "ticker": "BRENT",
        "event": "Screenshot-reported close long",
        "quantity": "538566907",
        "entry_price": "114.043000",
        "close_price": "115.777",
        "reported_transaction_pnl_usd": "933875016.74",
        "status": "Preserved cross-book source record only; post-cutoff TradingView material; not used in active Oil replay or added to any cash subtotal",
        "provenance": "User-provided screenshot; transaction PnL only; not independently audited brokerage execution; timezone not shown",
    },
    {
        "source_record_id": "PRIVATE_TV_USOIL_CLOSE_20261029",
        "source_book": "Harshal's Private Fund — TradingView Paper Trading screenshots",
        "date": "2026-10-29",
        "ticker": "OIL (USOIL)",
        "event": "Screenshot-reported close long",
        "quantity": "601218118",
        "entry_price": "99.180000",
        "close_price": "102.14",
        "reported_transaction_pnl_usd": "1779605629.28",
        "status": "Preserved cross-book source record only; post-cutoff TradingView material; not used in active Oil replay or added to any cash subtotal",
        "provenance": "User-provided screenshot; transaction PnL only; not independently audited brokerage execution; timezone not shown",
    },
]

LINE_RE = re.compile(
    r"^(?P<date>\d{4}-\d{2}-\d{2})\s+(?P<time>\d{2}:\d{2})\s+MST\s*\|\s*"
    r"SIMULATED PAPER\s+\[(?P<tag>[A-Za-z ]+?)\]\s*\|\s*"
    r"(?P<kind>entry|exit):\s*\[Market @ ~\$?(?P<price>[\d,]+\.?\d*)\]\s*\|\s*"
    r"size:\s*\[(?P<units>\d+(?:\.\d+)?)\s*units?[^\]]*\]\s*\|\s*"
    r"note:\s*\[(?P<note>.*)\]\s*$"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _portfolio_sleeve(ticker: str) -> str:
    return "DIRECT_CRUDE" if ticker in CRUDE_TICKERS else "OIL_LINKED_EQUITY"


def trade_ledger_rows():
    rows = []
    for ticker in sorted(OIL_BOOK_TICKERS):
        path = ROOT / "trades" / f"{ticker}.txt"
        for line_number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            text = raw.strip()
            if not text or text.startswith("#"):
                continue
            match = LINE_RE.match(text)
            if not match:
                raise ValueError(f"Unparsed Oil trade row {path.name}:{line_number}: {text}")
            day = match.group("date")
            active = day <= CUTOFF
            note = match.group("note")
            is_tv = bool(re.search(r"TradingView|TVC:", note, re.I))
            if active:
                status = "ACTIVE_REPLAY_INPUT_PRE_CUTOFF"
                exclusion_reason = ""
            elif is_tv:
                status = "PRESERVED_FLAGGED_TV_POST_CUTOFF_NOT_USED"
                exclusion_reason = "Post-2026-10-19 TradingView block; retained for audit only"
            else:
                status = "PRESERVED_OUTSIDE_ACTIVE_REPLAY_WINDOW_NOT_USED"
                exclusion_reason = "After the active replay cutoff; no later mark/valuation inferred"
            record_id = hashlib.sha256(f"{path.name}\0{line_number}\0{text}".encode()).hexdigest()[:16]
            rows.append({
                "record_id": record_id,
                "portfolio": PORTFOLIO_NAME,
                "portfolio_sleeve": _portfolio_sleeve(ticker),
                "source_book": "trades/ standardized simulated-paper ledger",
                "source_file": f"trades/{path.name}",
                "line": line_number,
                "date": day,
                "time_mst": match.group("time"),
                "ticker": ticker,
                "event": match.group("kind").upper(),
                "tag": match.group("tag").strip().upper(),
                "logged_price": match.group("price").replace(",", ""),
                "units": match.group("units"),
                "entry_in_active_replay": "YES" if active else "NO",
                "record_status": status,
                "exclusion_reason": exclusion_reason,
                "source_record_preserved": "YES",
                "note": note,
            })
    return sorted(rows, key=lambda row: (row["date"], row["time_mst"], row["ticker"], row["line"]))


def related_book_rows():
    rows = [dict(row) for row in PRIVATE_SCREENSHOT_RECORDS]
    with ATS_LIQUIDATIONS.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            rows.append({
                "source_record_id": row["record_id"],
                "source_book": "ATS locked $200 LONG foundation — user-reported liquidation",
                "date": row["execution_date"],
                "ticker": row["ticker"],
                "event": "User-reported liquidation / price group",
                "quantity": row["quantity_sold"],
                "entry_price": "",
                "close_price": row["sale_price_points_as_stated"] or (
                    f"{row['sale_price_min_usd']}–{row['sale_price_max_usd']}"
                    if row["sale_price_min_usd"] or row["sale_price_max_usd"] else ""
                ),
                "reported_transaction_pnl_usd": "",
                "status": "Reference only; no exact quantities/date/fill-level PnL supplied; not merged into active Oil replay",
                "provenance": row["notes"],
            })
    return rows


def ticker_breakdown(model):
    breakdown = {}
    for ticker in sorted(OIL_BOOK_TICKERS):
        realized = sum(item["pnl"] for item in model["realized_trades"] if item["sym"] == ticker)
        open_lots = [lot for lot in model["lots"] if lot["sym"] == ticker and lot["open"]]
        mark = core.MODEL_PRICES[ticker][-1]
        unrealized = sum(
            lot["qty"] * core.UNIT * (1 if lot["side"] == "long" else -1)
            * (mark / lot["entry_px"] - 1.0)
            for lot in open_lots
        )
        breakdown[ticker] = {
            "realized_pnl_usd": round(realized, 2),
            "unrealized_pnl_usd": round(unrealized, 2),
            "total_pnl_usd": round(realized + unrealized, 2),
            "open_units": round(sum(lot["qty"] for lot in open_lots), 6),
            "open_lot_count": len(open_lots),
            "open_notional_usd": round(sum(lot["qty"] * core.UNIT for lot in open_lots), 2),
        }
    return breakdown


def weekend_oil_lots(model):
    rows = []
    for lot in model["lots"]:
        if lot.get("manual_automatic_entry"):
            ticker = lot["sym"]
            final_mark = core.MODEL_PRICES[ticker][-1]
            rows.append({
                "ticker": ticker,
                "side": lot["side"].upper(),
                "entry_date": lot["entry_date"],
                "entry_price": lot["entry_px"],
                "units": lot["qty"],
                "gross_notional_usd": lot["qty"] * core.UNIT,
                "as_of_date": core.SESSION_DATES[-1],
                "as_of_mark": final_mark,
                "unrealized_pnl_usd": lot["qty"] * core.UNIT * (final_mark / lot["entry_px"] - 1.0),
                "live_ats_manual_allocation_verified": False,
            })
    return rows


def main():
    ledger = trade_ledger_rows()
    related = related_book_rows()
    events = core.parse_trades()
    series = {variant: core.daily_series(variant, events) for variant in core.VARIANTS}

    with DAILY_OUT.open("w", newline="", encoding="utf-8") as handle:
        fields = ["date", "variant", "realized_pnl_usd", "unrealized_pnl_usd", "total_pnl_usd",
                  "roi_pct", "deployed_notional_usd", "open_units"]
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for variant in core.VARIANTS:
            model = series[variant]
            for index, day in enumerate(model["dates"]):
                writer.writerow({
                    "date": day,
                    "variant": variant,
                    "realized_pnl_usd": f"{model['realized'][index]:.2f}",
                    "unrealized_pnl_usd": f"{model['unrealized'][index]:.2f}",
                    "total_pnl_usd": f"{model['total'][index]:.2f}",
                    "roi_pct": f"{model['roi'][index]:.6f}",
                    "deployed_notional_usd": f"{model['deployed'][index]:.2f}",
                    "open_units": f"{model['open_units'][index]:.6f}",
                })

    ledger_fields = list(ledger[0]) if ledger else []
    with LEDGER_OUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=ledger_fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(ledger)
    related_fields = list(related[0]) if related else []
    with RELATED_OUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=related_fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(related)

    summary = {
        "portfolio_name": PORTFOLIO_NAME,
        "portfolio_type": "separate simulated paper-model oil/energy portfolio",
        "active_replay_start_date": core.SESSION_DATES[0],
        "active_replay_end_date": core.SESSION_DATES[-1],
        "last_allowed_tradingview_input_date": CUTOFF,
        "active_direct_crude_tickers": sorted(CRUDE_TICKERS),
        "active_oil_linked_equity_tickers": sorted(ENERGY_EQUITY_TICKERS),
        "all_trade_log_rows_indexed": len(ledger),
        "pre_cutoff_trade_log_rows_used": sum(row["entry_in_active_replay"] == "YES" for row in ledger),
        "post_cutoff_trade_log_rows_preserved_not_used": sum(row["entry_in_active_replay"] == "NO" for row in ledger),
        "weekend_oil_tagged_lots_by_variant": {},
        "external_oil_book_records_separate": len(related),
        "external_book_transaction_pnl_included_in_core_model": False,
        "post_cutoff_tradingview_inputs_used": 0,
        "cash_convention": "All-cash/debit paper model; no leverage, financing, or funding source inferred.",
        "variants": {},
    }
    for variant, model in series.items():
        summary["variants"][variant] = {
            "label": core.VARIANT_LABEL[variant],
            "realized_pnl_usd": round(model["realized"][-1], 2),
            "unrealized_pnl_usd": round(model["unrealized"][-1], 2),
            "total_pnl_usd": round(model["total"][-1], 2),
            "roi_pct": round(model["roi"][-1], 6),
            "deployed_notional_usd": round(model["deployed"][-1], 2),
            "open_units": round(model["open_units"][-1], 6),
            "by_ticker": ticker_breakdown(model),
        }
        summary["weekend_oil_tagged_lots_by_variant"][variant] = weekend_oil_lots(model)
    SUMMARY_OUT.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    source_paths = [core.BENCHMARK_SESSION_FILE, ATS_LIQUIDATIONS, PRIVATE_FUND_REPORT]
    source_paths += [ROOT / "trades" / f"{ticker}.txt" for ticker in sorted(OIL_BOOK_TICKERS)]
    manifest = {
        "version": 1,
        "portfolio_name": PORTFOLIO_NAME,
        "builder": "scripts/build_oil_portfolio.py",
        "cutoff": CUTOFF,
        "source_hashes_sha256": {str(path.relative_to(ROOT)): sha256(path) for path in source_paths},
        "outputs": [str(path.relative_to(ROOT)) for path in (DAILY_OUT, LEDGER_OUT, RELATED_OUT, SUMMARY_OUT, REPORT, MANIFEST_OUT)],
        "private_paper_account_records_kept_separate": True,
        "oil_foundation_liquidation_records_kept_separate": True,
    }
    MANIFEST_OUT.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    active_count = summary["pre_cutoff_trade_log_rows_used"]
    post_count = summary["post_cutoff_trade_log_rows_preserved_not_used"]
    lines = [
        "# Oil Portfolio",
        "",
        "> Separate portfolio for all recorded OIL/USOIL and BRENT trade-log events, the Weekend Oil campaign, and oil-linked equity trades. A simulated portfolio ledger is not a claim of a funded account or independently verified brokerage executions.",
        "",
        "## Portfolio scope",
        "",
        "- **Direct crude:** `OIL` (TVC:USOIL / WTI) and `BRENT` (Brent Cash). All their standardized trade-log rows are carried into the Oil ledger, including the 50U Weekend Oil entries and later Weekend Oil adds.",
        "- **Oil/energy-linked equity sleeve:** `CVX`, `VLO`, and `XLE`, kept separately identified from crude exposure. CVX includes the user-recorded Brent-caption-linked position.",
        "- The prior `HARSHAL_PRIYAVADAN_PATEL_AI_FUND` version 1 included two OIL commentary entries and one CVX commentary event. Those entries are now moved into this Oil portfolio in fund version 2; v1 is preserved as history and is not the current fund allocation.",
        f"- Active model window: **{core.SESSION_DATES[0]} through {CUTOFF}**. October 20, 2026 onward remains blocked for TradingView-derived active use. Later oil events are preserved in the event ledger but not used in the active replay.",
        "- The Oil portfolio does not include DXY. Private-fund screenshot closes, user-reported ATS locked-foundation liquidations, and duress scenario rows are indexed separately; they are not merged into this active model or netted across books.",
        "",
        "## Active replay results through October 19, 2026",
        "",
        "| Variant | Realized PnL | Unrealized PnL | Total PnL | ROI | Deployed notional | Open units |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for variant, item in summary["variants"].items():
        lines.append(
            f"| {variant} — {item['label']} | ${item['realized_pnl_usd']:,.2f} | ${item['unrealized_pnl_usd']:,.2f} | "
            f"${item['total_pnl_usd']:,.2f} | {item['roi_pct']:.4f}% | ${item['deployed_notional_usd']:,.2f} | {item['open_units']:,.4f} |"
        )
    lines += [
        "",
        "The four variants retain their existing model definitions. Total return combines the direct-crude and separately labeled energy-equity sleeves; see the per-ticker breakdown in the summary JSON. No funding or account mapping is inferred.",
        "",
        "## Weekend Oil lots",
        "",
        "The 2026-10-19 50U BRENT and 50U OIL Weekend Oil lots are included in all four core variants as separate, additional simulated lots. At the October 19 EOD mark they are marked against their user-provided entry prices; they are not proof of ATS or brokerage fills. The requested ATS/MANUAL 40U/10U split is a ceiling/proxy only, not a verified allocation.",
        "",
        "The October 23 target trims/short entries, October 25 Weekend Oil replenishments/short-cover-linked entries, and October 26 screenshot-linked entries/closes are preserved in the ledger but excluded from active PnL because they are after the current replay cutoff. The screenshot-reported paired 50U close is not converted into an active TradingView input.",
        "",
        "## Ledger, related books, and audit links",
        "",
        f"- Standardized Oil/energy trade-log rows indexed: **{len(ledger)}**; rows used through cutoff: **{active_count}**; later rows preserved but not used: **{post_count}**.",
        f"- Separate-book references retained: **{len(related)}**. [`oil_portfolio_related_book_records_v1.csv`](../data/oil_portfolio_related_book_records_v1.csv) includes the two screenshot-reported October 29 Private Fund oil closes (transaction PnL only, not independently audited) and the three user-reported ATS locked-foundation liquidation records with unknown exact quantities/fills. They are not part of the core totals.",
        "- [All oil/energy trade-log events](../data/oil_portfolio_trade_ledger_v1.csv); [daily model series](../data/oil_portfolio_daily_v1.csv); [summary and per-ticker breakdown](../data/oil_portfolio_summary_v1.json); [SHA-256 source manifest](../data/oil_portfolio_manifest_v1.json).",
        "- Related but distinct scenario: [Under-Duress Oil Sale Void Replay](Under-Duress%20Oil%20Sale%20Void%20Replay.md). That is a hypothetical replay, not an additional Oil holding.",
        "",
        "## Accounting and provenance",
        "",
        "All active results are hypothetical unit-notional model calculations. They are not audited brokerage executions, account balances, or a reconciled total across the public, ATS, and Private Fund books. The all-cash/debit convention remains in force; no leverage or financing is inferred. Screenshot-reported realized PnL from a separate TradingView Paper Trading account remains source-record-only and is not included in these results.",
        "",
    ]
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Built Oil portfolio: {len(ledger)} trade-log rows; {active_count} active through {CUTOFF}; {post_count} later rows preserved.")
    for variant, item in summary["variants"].items():
        print(f"{variant}: total PnL ${item['total_pnl_usd']:,.2f}; ROI {item['roi_pct']:.4f}%")


if __name__ == "__main__":
    main()
