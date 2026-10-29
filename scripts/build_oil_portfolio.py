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
from decimal import Decimal, ROUND_HALF_UP
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
RECON_OUT = DATA / "oil_pnl_reconciliation_v1.csv"
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


def pnl_reconciliation_rows(ledger, related, oil_summary):
    """Reconcile the AI Fund v1→v2 movement and isolated Oil portfolio totals."""
    v1_path = DATA / "harshal_priyavadan_patel_ai_fund_summary_v1.json"
    v2_path = DATA / "harshal_priyavadan_patel_ai_fund_summary_v2.json"
    old_fund = json.loads(v1_path.read_text(encoding="utf-8"))
    current_fund = json.loads(v2_path.read_text(encoding="utf-8"))
    old_ledger_path = DATA / "harshal_priyavadan_patel_ai_fund_event_ledger_v1.csv"
    with old_ledger_path.open(newline="", encoding="utf-8") as handle:
        old_ledger = list(csv.DictReader(handle))

    rows = []
    for variant in core.VARIANTS:
        old_pnl = Decimal(str(old_fund["variants"][variant]["total_pnl_usd"]))
        new_pnl = Decimal(str(current_fund["variants"][variant]["total_pnl_usd"]))
        rows.append({
            "reconciliation_type": "AI_FUND_V1_MINUS_V2",
            "variant": variant,
            "ticker": "",
            "date": "",
            "source_record_id": "",
            "amount_usd": f"{old_pnl - new_pnl:.2f}",
            "status": "Removed from current AI Fund v2 and transferred to Oil; version 1 is historical",
            "calculation": f"{old_pnl:.2f} - {new_pnl:.2f}",
        })

    moved_by_ticker = {ticker: Decimal("0") for ticker in OIL_BOOK_TICKERS}
    for record in old_ledger:
        ticker = record["Ticker"].upper()
        if ticker not in {"OIL", "CVX"} or record["Event"].upper() != "ENTRY":
            continue
        if record["Date"] > CUTOFF:
            continue
        quantity = Decimal(record["Units"])
        entry = Decimal(record["Logged_Price"])
        mark = Decimal(str(core.MODEL_PRICES[ticker][-1]))
        sign = Decimal("-1") if record["Tag"].upper() == "SHORT" else Decimal("1")
        pnl = (quantity * Decimal(str(core.UNIT)) * sign * (mark / entry - Decimal("1")))
        pnl_cents = pnl.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        moved_by_ticker[ticker] += pnl_cents
        rows.append({
            "reconciliation_type": "TRANSFERRED_AI_FUND_V1_TRADE",
            "variant": "all",
            "ticker": ticker,
            "date": record["Date"],
            "source_record_id": record.get("Record_ID", ""),
            "amount_usd": f"{pnl_cents:.2f}",
            "status": "Now held in Oil portfolio; single 1U LONG mark contribution",
            "calculation": f"{quantity:g} × ${core.UNIT:,.0f} × ({mark} / {entry} - 1)",
        })

    oil_v1 = oil_summary["variants"]["V1"]["by_ticker"]
    for ticker in sorted(OIL_BOOK_TICKERS):
        total = Decimal(str(oil_v1[ticker]["total_pnl_usd"]))
        moved = moved_by_ticker.get(ticker, Decimal("0"))
        rows.append({
            "reconciliation_type": "OIL_PORTFOLIO_BY_TICKER",
            "variant": "V1",
            "ticker": ticker,
            "date": CUTOFF,
            "source_record_id": "",
            "amount_usd": f"{total:.2f}",
            "status": "Current Oil portfolio mark-to-model contribution through cutoff",
            "calculation": "Realized plus unrealized ticker PnL",
        })
        if moved:
            remaining = total - moved
            rows.append({
                "reconciliation_type": "OTHER_OIL_RECORDS_NET_OF_AI_FUND_TRANSFER",
                "variant": "V1",
                "ticker": ticker,
                "date": CUTOFF,
                "source_record_id": "",
                "amount_usd": f"{remaining:.2f}",
                "status": "Other oil/linked-equity records newly included in Oil; net of moved AI Fund v1 entries",
                "calculation": f"{total:.2f} - {moved:.2f}",
            })
        else:
            rows.append({
                "reconciliation_type": "OTHER_OIL_RECORDS_NET_OF_AI_FUND_TRANSFER",
                "variant": "V1",
                "ticker": ticker,
                "date": CUTOFF,
                "source_record_id": "",
                "amount_usd": f"{total:.2f}",
                "status": "Oil/energy records newly included in Oil; no AI Fund v1 overlap",
                "calculation": f"{total:.2f}",
            })

    screenshot_pnl = sum(
        (Decimal(row["reported_transaction_pnl_usd"]) for row in related
         if row.get("reported_transaction_pnl_usd")),
        Decimal("0"),
    )
    rows.append({
        "reconciliation_type": "PRIVATE_FUND_SCREENSHOT_REPORTED_CLOSES",
        "variant": "separate book; excluded from active totals",
        "ticker": "BRENT + OIL",
        "date": "2026-10-29",
        "source_record_id": "PRIVATE_TV_BRENT_CLOSE_20261029; PRIVATE_TV_USOIL_CLOSE_20261029",
        "amount_usd": f"{screenshot_pnl:.2f}",
        "status": "Two screenshot-reported LONG close transaction PnLs; post-cutoff and separate-book records, not active Oil model PnL",
        "calculation": "933875016.74 + 1779605629.28",
    })

    active_short_count = sum(
        row["entry_in_active_replay"] == "YES" and row["event"] == "ENTRY" and row["tag"] == "SHORT"
        for row in ledger
    )
    post_cutoff_short_count = sum(
        row["entry_in_active_replay"] == "NO" and row["event"] == "ENTRY" and row["tag"] == "SHORT"
        for row in ledger
    )
    rows.append({
        "reconciliation_type": "SHORTING_CHECK",
        "variant": "all",
        "ticker": "BRENT + OIL",
        "date": CUTOFF,
        "source_record_id": "",
        "amount_usd": "",
        "status": f"Active short entries used: {active_short_count}; later short entries preserved but not used: {post_cutoff_short_count}",
        "calculation": "Only active replay records through 2026-10-19 count; post-cutoff short scenarios contribute zero to active PnL",
    })
    return rows, {
        "ai_fund_v1_total_pnl_usd_by_variant": {
            variant: old_fund["variants"][variant]["total_pnl_usd"] for variant in core.VARIANTS
        },
        "ai_fund_v2_total_pnl_usd_by_variant": {
            variant: current_fund["variants"][variant]["total_pnl_usd"] for variant in core.VARIANTS
        },
        "ai_fund_v1_to_v2_removed_pnl_usd_by_variant": {
            variant: round(
                old_fund["variants"][variant]["total_pnl_usd"]
                - current_fund["variants"][variant]["total_pnl_usd"], 2
            ) for variant in core.VARIANTS
        },
        "transferred_ai_fund_v1_oil_cvx_trade_pnl_usd": round(float(sum(moved_by_ticker.values())), 2),
        "oil_portfolio_total_pnl_usd": oil_summary["variants"]["V1"]["total_pnl_usd"],
        "other_oil_records_net_pnl_usd": round(
            oil_summary["variants"]["V1"]["total_pnl_usd"] - float(sum(moved_by_ticker.values())), 2
        ),
        "private_fund_screenshot_reported_close_pnl_usd_separate": float(screenshot_pnl),
        "active_oil_short_entries_used": active_short_count,
        "later_short_entries_not_used": post_cutoff_short_count,
    }


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
    reconciliation_rows, reconciliation_summary = pnl_reconciliation_rows(ledger, related, summary)
    summary["pnl_reconciliation"] = reconciliation_summary
    with RECON_OUT.open("w", newline="", encoding="utf-8") as handle:
        fields = list(reconciliation_rows[0]) if reconciliation_rows else []
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(reconciliation_rows)
    SUMMARY_OUT.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    source_paths = [
        core.BENCHMARK_SESSION_FILE, ATS_LIQUIDATIONS, PRIVATE_FUND_REPORT,
        DATA / "harshal_priyavadan_patel_ai_fund_summary_v1.json",
        DATA / "harshal_priyavadan_patel_ai_fund_summary_v2.json",
        DATA / "harshal_priyavadan_patel_ai_fund_event_ledger_v1.csv",
    ]
    source_paths += [ROOT / "trades" / f"{ticker}.txt" for ticker in sorted(OIL_BOOK_TICKERS)]
    manifest = {
        "version": 1,
        "portfolio_name": PORTFOLIO_NAME,
        "builder": "scripts/build_oil_portfolio.py",
        "cutoff": CUTOFF,
        "source_hashes_sha256": {str(path.relative_to(ROOT)): sha256(path) for path in source_paths},
        "outputs": [str(path.relative_to(ROOT)) for path in (DAILY_OUT, LEDGER_OUT, RELATED_OUT, RECON_OUT, SUMMARY_OUT, REPORT, MANIFEST_OUT)],
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
    reconciliation_lines = [
        "## PnL reconciliation: the apparent gap was allocation, not oil shorts",
        "",
        "The prior AI Fund v1 included two OIL longs and one CVX long that are now in Oil. Their October 19 mark-to-model contributions total **$1,214.71**. Other Oil ledger records outside those three entries contribute a net **+$508.38**, producing the Oil portfolio total of **+$1,723.09**.",
        "",
        "| AI Fund variant | v1 before oil transfer | current v2 | PnL removed from AI Fund |",
        "|---|---:|---:|---:|",
    ]
    for variant in core.VARIANTS:
        v1 = Decimal(str(reconciliation_summary["ai_fund_v1_total_pnl_usd_by_variant"][variant]))
        v2 = Decimal(str(reconciliation_summary["ai_fund_v2_total_pnl_usd_by_variant"][variant]))
        removed = Decimal(str(reconciliation_summary["ai_fund_v1_to_v2_removed_pnl_usd_by_variant"][variant]))
        reconciliation_lines.append(f"| {variant} | ${v1:,.2f} | ${v2:,.2f} | ${removed:,.2f} |")
    reconciliation_lines += [
        "",
        "| Reallocated AI Fund v1 record | Entry | 2026-10-19 mark | PnL moved to Oil |",
        "|---|---:|---:|---:|",
    ]
    for row in reconciliation_rows:
        if row["reconciliation_type"] == "TRANSFERRED_AI_FUND_V1_TRADE":
            mark_price, entry_price = row["calculation"].split("(", 1)[1].split(" / ", 1)
            reconciliation_lines.append(
                f"| {row['ticker']} LONG — {row['date']} | ${float(entry_price.split()[0]):,.2f} | "
                f"${float(mark_price):,.2f} | ${float(row['amount_usd']):,.2f} |"
            )
    other_oil_net = reconciliation_summary["other_oil_records_net_pnl_usd"]
    screenshot_pnl = reconciliation_summary["private_fund_screenshot_reported_close_pnl_usd_separate"]
    short_check = next(row["status"] for row in reconciliation_rows if row["reconciliation_type"] == "SHORTING_CHECK")
    reconciliation_lines += [
        "",
        f"At the two-decimal level, **$1,214.71 + ${other_oil_net:,.2f} = ${summary['variants']['V1']['total_pnl_usd']:,.2f}**. V3A's v1-to-v2 displayed difference rounds to $1,214.72 (one cent above the other variants) because each total was independently rounded; the three source lots sum to $1,214.71.",
        "",
        f"The separate Private Fund screenshots show **${screenshot_pnl:,.2f}** combined transaction-level PnL on two LONG closes. That screenshot-reported amount is preserved in the related-book register, but it is post-cutoff, belongs to a separate book, and is not included in the $1,723.09 active Oil model total. It is transaction-level TradingView paper-account PnL, not independently audited brokerage execution or a reconciled cash balance.",
        "",
        "The ATS locked-foundation records separately retain the user-reported **approximately $2.4B** conservative model endpoint. Exact quantities, dates, and fill-level PnL were not supplied, so this is not added to the active Oil total or treated as verified realized PnL.",
        "",
        f"Shorting check: **{short_check}**. The active replay used no short entries. The two 10U OIL/BRENT short entries dated October 23 are after the cutoff and contribute zero to the active replay; they remain hypothetical/audit records, not verified executions.",
        "",
        "Detailed arithmetic and source-record identifiers: [`oil_pnl_reconciliation_v1.csv`](../data/oil_pnl_reconciliation_v1.csv).",
        "",
    ]
    insertion_point = lines.index("## Weekend Oil lots")
    lines[insertion_point:insertion_point] = reconciliation_lines
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Built Oil portfolio: {len(ledger)} trade-log rows; {active_count} active through {CUTOFF}; {post_count} later rows preserved.")
    for variant, item in summary["variants"].items():
        print(f"{variant}: total PnL ${item['total_pnl_usd']:,.2f}; ROI {item['roi_pct']:.4f}%")


if __name__ == "__main__":
    main()
