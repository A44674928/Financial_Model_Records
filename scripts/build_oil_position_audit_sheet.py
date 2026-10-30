#!/usr/bin/env python3
"""Build one filterable audit sheet for all known Oil and related scenario positions.

Small units are <=1U ($10,000 standard model notional); large units are >1U.
Scenario alternatives and cross-book records are preserved but never netted.
"""

from __future__ import annotations

import csv
import hashlib
import os
import re
import sys
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = DATA / "oil_position_audit_sheet_v1.csv"
CUTOFF = "2026-10-19"
MARK_DATE = "2026-10-26"
UNIT_NOTIONAL = Decimal("10000")
OIL_TICKERS = {"BRENT", "OIL", "CVX", "VLO", "XLE"}
MARKS = {"BRENT": Decimal("115.38"), "OIL": Decimal("101.30"), "CVX": Decimal("232.01"), "VLO": Decimal("426.76"), "XLE": Decimal("69.64")}

# The active Oil model uses only the pre-cutoff trade-event set, but is marked
# through the latest complete user-authorized EOD dataset.
os.environ["PAPER_TRADES_INFLUENCER_AI_SCREEN"] = "0"
os.environ["PAPER_TRADES_AI_FUND_REPLAY"] = "0"
os.environ["PAPER_TRADES_OIL_PORTFOLIO_REPLAY"] = "1"
os.environ["PAPER_TRADES_OIL_PORTFOLIO_MARK_MAX_DATE"] = MARK_DATE
os.environ["PAPER_TRADES_OIL_PORTFOLIO_EVENT_MAX_DATE"] = CUTOFF
os.environ["PAPER_TRADES_OIL_PORTFOLIO_ALLOW_POST_CUTOFF_MARKS"] = "1"
sys.path.insert(0, str(ROOT / "scripts"))
import model_perf_core as core  # noqa: E402

FIELDS = [
    "size_group", "size_rule", "position_id", "row_type", "book_or_model", "scenario_id",
    "ticker", "side", "quantity", "quantity_unit", "u_equivalent", "entry_date",
    "entry_time", "entry_price_usd", "gross_basis_usd", "exit_date", "exit_price_usd",
    "valuation_date", "valuation_mark_usd", "market_value_usd", "realized_pnl_usd",
    "conditional_unrealized_pnl_usd", "scenario_total_pnl_usd", "position_state",
    "source_nullification_state", "test_override_state", "additivity_rule", "count_in_core_v2",
    "source_record_id", "source_file", "audit_notes",
]


def cents(value):
    if value in (None, ""):
        return ""
    try:
        return str(Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
    except Exception:
        # Keep source-described ranges/pairs as text; never coerce them into a price.
        return str(value)


def dec(value):
    return Decimal(str(value)) if value not in (None, "") else None


def normalized_ticker(value):
    ticker = (value or "").upper().strip()
    return "OIL" if ticker in {"USOIL", "OIL (USOIL)", "TVC:USOIL"} else ticker


def position_id(prefix, *parts):
    raw = "|".join(str(p or "") for p in parts)
    return f"{prefix}-{hashlib.sha256(raw.encode()).hexdigest()[:16]}"


def size_class(u_equivalent, unknown_large=False):
    if u_equivalent is None:
        return ("LARGE_UNITS", "Quantity unknown; source describes a whole-fund or large position") if unknown_large else ("LARGE_UNITS", "Size unavailable; flagged for review")
    group = "SMALL_UNITS" if u_equivalent <= Decimal("1") else "LARGE_UNITS"
    return group, "Small <=1U ($10,000); large >1U"


def make_row(**kw):
    row = {field: "" for field in FIELDS}
    row.update(kw)
    ueq = dec(row.get("u_equivalent"))
    row["size_group"], row["size_rule"] = size_class(
        ueq, unknown_large=row.get("row_type") in {"REPORTED_LIQUIDATION_REFERENCE", "ATS_FOUNDATION_RESTORATION"}
    )
    if row.get("row_type") == "UNDER_DURESS_RESTORED_LONG" and row.get("book_or_model", "").startswith("Private fund"):
        row["size_group"] = "UNKNOWN_UNIT_CONVENTION"
        row["size_rule"] = "Platform quantity retained as reported; no contract/unit multiplier inferred"
    if row.get("gross_basis_usd") not in (None, ""):
        row["gross_basis_usd"] = cents(row["gross_basis_usd"])
    for name in ("entry_price_usd", "exit_price_usd", "valuation_mark_usd", "market_value_usd", "realized_pnl_usd", "conditional_unrealized_pnl_usd", "scenario_total_pnl_usd"):
        row[name] = cents(row.get(name))
    if row.get("quantity") not in (None, ""):
        row["quantity"] = str(row["quantity"])
    if row.get("u_equivalent") not in (None, ""):
        row["u_equivalent"] = str(ueq.normalize())
    return row


def read_csv(path):
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def active_oil_rows():
    series, events = core.all_series()
    model = series["V1"]
    ledger = read_csv(DATA / "oil_portfolio_trade_ledger_v2.csv")
    ledger_by_key = {}
    for record in ledger:
        if record["entry_in_active_replay"] != "YES" or record["event"] != "ENTRY":
            continue
        key = (record["ticker"], record["date"], Decimal(record["logged_price"]), Decimal(record["units"]), record["tag"])
        ledger_by_key.setdefault(key, []).append(record)
    events_by_key = {}
    for event in events:
        key = (event["sym"], event["date"], Decimal(str(event["px"])), Decimal(str(event["units"])), event["tag"])
        events_by_key.setdefault(key, []).append(event)

    rows = []
    for lot in model["lots"]:
        if not lot["open"]:
            continue
        ticker = lot["sym"]
        mark = Decimal(str(core.MODEL_PRICES[ticker][-1]))
        entry = Decimal(str(lot["entry_px"]))
        qty = Decimal(str(lot["qty"]))
        pnl = qty * UNIT_NOTIONAL * (mark / entry - Decimal("1"))
        key = (ticker, lot["entry_date"], entry, qty, "LONG")
        source = ledger_by_key.get(key, []).pop(0) if ledger_by_key.get(key) else {}
        event = events_by_key.get(key, []).pop(0) if events_by_key.get(key) else {}
        source_id = source.get("record_id") or position_id("OIL-CORE", ticker, lot["entry_date"], entry, qty)
        rows.append(make_row(
            position_id=source_id, row_type="ACTIVE_OIL_MODEL_POSITION", book_or_model="Oil portfolio v2 — active pre-cutoff lots",
            scenario_id="OIL_BASE_SET_THROUGH_2026-10-19", ticker=ticker, side=lot["side"].upper(),
            quantity=qty, quantity_unit="U ($10,000 model notional)", u_equivalent=qty,
            entry_date=lot["entry_date"], entry_time=event.get("time", ""), entry_price_usd=entry,
            gross_basis_usd=qty * UNIT_NOTIONAL, valuation_date=MARK_DATE, valuation_mark_usd=mark,
            market_value_usd=qty * UNIT_NOTIONAL * mark / entry,
            realized_pnl_usd=0, conditional_unrealized_pnl_usd=pnl, scenario_total_pnl_usd=pnl,
            position_state="OPEN IN MARK-FORWARD MODEL", source_nullification_state="NOT APPLICABLE",
            test_override_state="NONE", additivity_rule="Base Oil model position; one row per source lot",
            count_in_core_v2="YES", source_record_id=source_id,
            source_file=source.get("source_file", f"trades/{ticker}.txt"),
            audit_notes=f"Mark-forward only: active trade-event cutoff {CUTOFF}; EOD mark {MARK_DATE}. No post-cutoff trade events included.",
        ))
    return rows


def restored_long_rows():
    restored = read_csv(DATA / "under_duress_oil_restored_positions_v1.csv")
    rows = []
    for item in restored:
        event_id = item["event_id"]
        ticker = item["ticker"] if event_id in {"PF-BRENT-CLOSE-20261029", "PF-USOIL-CLOSE-20261029"} else normalized_ticker(item["ticker"])
        quantity = dec(item["restored_quantity"])
        quantity_unit = item["quantity_unit"]
        entry = dec(item["entry_price_usd"])
        initial_basis = dec(item["notional_basis_usd"])
        scenario = item["scenario"]
        is_voided_private_close = event_id in {"PF-BRENT-CLOSE-20261029", "PF-USOIL-CLOSE-20261029"}
        is_u = "U (" in quantity_unit
        if is_voided_private_close:
            # Platform quantities are preserved verbatim. Do not convert to U or
            # infer a gross cash basis without a documented contract convention.
            ueq = None
            basis = None
        elif is_u:
            ueq = quantity
            basis = quantity * UNIT_NOTIONAL
        else:
            basis = initial_basis
            ueq = basis / UNIT_NOTIONAL if basis is not None else None
        # Preserve each source book's own mark. For core/ATS scenario rows, use
        # the latest aligned Oct. 26 EOD mark; separate Private Fund screenshot
        # restores retain their reported transaction mark and source boundary.
        if "Private fund" in item["book"]:
            mark_date = item.get("mark_date", "")
            mark = dec(item.get("mark_price_usd", ""))
            pnl = dec(item.get("conditional_unrealized_pnl_usd", ""))
            market_value = (basis + pnl) if basis is not None and pnl is not None else None
        else:
            mark_date = MARK_DATE
            mark = MARKS.get(ticker)
            if is_u and entry is not None and mark is not None:
                pnl = basis * (mark / entry - Decimal("1"))
                market_value = basis + pnl
            elif quantity is not None and entry is not None and mark is not None:
                pnl = quantity * (mark - entry)
                market_value = quantity * mark
            else:
                pnl = dec(item["conditional_unrealized_pnl_usd"])
                market_value = (basis + pnl) if basis is not None and pnl is not None else None
        if "ATS exit sensitivity" in scenario:
            additivity = "ALTERNATIVE SENSITIVITY; do not sum with other unit sizes"
        elif "legacy baseline target trim" in scenario:
            additivity = "OVERLAPS the 50U Weekend Oil base lot; restoration slice only"
        elif "screenshot close" in scenario:
            additivity = "Separate Private Fund paper book; do not net with Oil/ATS"
        elif "paired 50U lot cash-out" in scenario:
            additivity = "Separate named test lot; reopened only for scenario audit"
        else:
            additivity = "Separate source book; verify exact quantities/fills before summing"
        row_type = "ATS_FOUNDATION_RESTORATION" if "ATS locked" in item["book"] else "UNDER_DURESS_RESTORED_LONG"
        audit_row = make_row(
            position_id=event_id, row_type=row_type, book_or_model=item["book"], scenario_id=scenario,
            ticker=ticker, side=item["restored_side"], quantity=quantity, quantity_unit=quantity_unit,
            u_equivalent=ueq, entry_date=("Earlier; exact date/time not supplied" if is_voided_private_close else item["trade_date"]), entry_price_usd=entry,
            gross_basis_usd=basis, valuation_date=mark_date, valuation_mark_usd=mark,
            market_value_usd=market_value, realized_pnl_usd="",
            conditional_unrealized_pnl_usd=pnl, scenario_total_pnl_usd=pnl,
            position_state=("OPEN; 2026-10-29 CLOSE NULLIFIED/VOIDED; NO CURRENT MARK SUPPLIED" if is_voided_private_close else "REOPENED FOR AUDIT TEST; NOT ASSERTED AS ACTUALLY OPEN"),
            source_nullification_state=item.get("user_directed_nullification_status") or item["void_status"],
            test_override_state=("CLOSE NULLIFIED/VOIDED; EARLIER LONG RETAINED OPEN" if is_voided_private_close else "REINSTATED / UN-NULLIFIED FOR THIS TEST SHEET"),
            additivity_rule=additivity, count_in_core_v2="NO — scenario/reference row",
            source_record_id=event_id, source_file=item["source_artifact"],
            audit_notes=(item["notes"] + (" Source screenshot close price and PnL are preserved in source_reported_close_price_usd/source_reported_close_pnl_usd fields only; they are not a valid mark or realized PnL. Platform void status is not independently confirmed." if is_voided_private_close else " Original event/source record remains preserved; restored state is a hypothetical audit view, not a claim of actual short closure or brokerage execution.")),
        )
        if is_voided_private_close:
            audit_row["entry_price_usd"] = item["entry_price_usd"]
        rows.append(audit_row)
    return rows


def reinstated_short_rows():
    sens = read_csv(DATA / "ats_manual_live_positions_v1.csv")
    voids = read_csv(DATA / "under_duress_oil_void_events_v1.csv")
    void_by_id = {row["event_id"]: row for row in voids}
    rows = []
    for item in sens:
        if "scenario" not in item["record_type"].lower() or not item.get("ats_short_open_units"):
            continue
        ticker = normalized_ticker(item["ticker"])
        qty_u = dec(item["ats_short_open_units"])
        if not qty_u:
            continue
        units_text = f"{int(qty_u)}U"
        ticker_id = "OIL" if ticker == "OIL" else "BRENT"
        event_id = f"ATS-{ticker_id}-SHORT-LIFECYCLE-NULL-{units_text}"
        void = void_by_id[event_id]
        entry = dec(item["price"])
        exit_price = Decimal("114.627") if ticker == "BRENT" else Decimal("100.740")
        pnl = qty_u * UNIT_NOTIONAL * (Decimal("1") - exit_price / entry)
        rows.append(make_row(
            position_id=event_id, row_type="REINSTATED_NULLIFIED_SHORT_LIFECYCLE",
            book_or_model="ATS 50U campaign sensitivity — hypothetical only",
            scenario_id=item["scenario"], ticker=ticker, side="SHORT", quantity=qty_u,
            quantity_unit="U ($10,000 model notional)", u_equivalent=qty_u,
            entry_date="2026-10-23", entry_time="not supplied; date-level assumption only",
            entry_price_usd=entry, gross_basis_usd=qty_u * UNIT_NOTIONAL,
            exit_date="2026-10-25", exit_price_usd=exit_price,
            valuation_date="2026-10-25 modeled close", valuation_mark_usd=exit_price,
            market_value_usd=0, realized_pnl_usd=pnl, conditional_unrealized_pnl_usd=0,
            scenario_total_pnl_usd=pnl,
            position_state="CLOSED IN REINSTATED HYPOTHETICAL LIFECYCLE; ending open short = 0U",
            source_nullification_state="NULLIFIED IN ORIGINAL SCENARIO",
            test_override_state="UN-NULLIFIED / REINSTATED FOR AUDIT TEST ONLY",
            additivity_rule="ALTERNATIVE SENSITIVITY; do not sum 10U/20U/30U/40U scenarios",
            count_in_core_v2="NO — hypothetical short sensitivity",
            source_record_id=event_id,
            source_file=f"data/under_duress_oil_void_events_v1.csv; data/ats_manual_live_positions_v1.csv",
            audit_notes=(void["void_reason"] + " Reinstated lifecycle assumes the source-described modeled cover and manual closure at the specified exit mark. This is not evidence an actual short was executed or closed."),
        ))
    return rows


def ats_manual_position_rows():
    source = read_csv(DATA / "ats_manual_live_positions_v1.csv")
    rows = []
    accepted = (
        "ATS LONG entry at fixed user-supplied price",
        "MANUALLY APPROVED ATS ORDER; user-reported LONG entry",
        "User-reported LONG entry; category not specified",
        "Manual replenishment",
    )
    for item in source:
        event = item.get("event", "")
        if not any(text in event for text in accepted):
            continue
        ticker = normalized_ticker(item["ticker"])
        qty = dec(item["units"])
        entry = dec(item["price"])
        mark = MARKS.get(ticker)
        basis = qty * UNIT_NOTIONAL if qty is not None else None
        pnl = basis * (mark / entry - Decimal("1")) if basis is not None and entry and mark else None
        rows.append(make_row(
            position_id=position_id("ATS-MANUAL", ticker, item["date"], item["time_mst"], item["units"], item["price"]),
            row_type="REPORTED_OR_MODELED_ATS_MANUAL_LONG", book_or_model=item["record_type"],
            scenario_id=item["scenario"], ticker=ticker, side="LONG", quantity=qty,
            quantity_unit="U ($10,000 model notional)", u_equivalent=qty, entry_date=item["date"],
            entry_time=item["time_mst"], entry_price_usd=entry, gross_basis_usd=basis,
            valuation_date=MARK_DATE, valuation_mark_usd=mark,
            market_value_usd=(basis + pnl) if basis is not None and pnl is not None else None,
            realized_pnl_usd=0, conditional_unrealized_pnl_usd=pnl, scenario_total_pnl_usd=pnl,
            position_state=item["status"], source_nullification_state="NOT APPLICABLE",
            test_override_state="SOURCE POSITION INCLUDED AS A DISTINCT AUDIT ROW",
            additivity_rule="Separate ATS/manual source lot; not in active Oil v2; verify book mapping before summing",
            count_in_core_v2="NO — later source position",
            source_record_id=position_id("ATS-MANUAL", ticker, item["date"], item["time_mst"], item["units"], item["price"]),
            source_file="data/ats_manual_live_positions_v1.csv",
            audit_notes=item["notes"],
        ))
    return rows


def ats_residual_long_rows():
    source = read_csv(DATA / "ats_manual_live_positions_v1.csv")
    rows = []
    for item in source:
        if "scenario" not in item["record_type"].lower() or not item.get("residual_long_units_from_approved_buy"):
            continue
        ticker = normalized_ticker(item["ticker"])
        qty = dec(item["residual_long_units_from_approved_buy"])
        if not qty:
            continue
        exit_price = Decimal("114.627") if ticker == "BRENT" else Decimal("100.740")
        mark = MARKS[ticker]
        basis = qty * UNIT_NOTIONAL
        pnl = basis * (mark / exit_price - Decimal("1"))
        rows.append(make_row(
            position_id=position_id("ATS-RESIDUAL-LONG", ticker, item["scenario"], qty),
            row_type="ATS_SCENARIO_RESIDUAL_LONG", book_or_model="ATS manual short-closure sensitivity",
            scenario_id=item["scenario"], ticker=ticker, side="LONG", quantity=qty,
            quantity_unit="U ($10,000 model notional)", u_equivalent=qty,
            entry_date="2026-10-25", entry_time="20:35 MST modeled", entry_price_usd=exit_price,
            gross_basis_usd=basis, valuation_date=MARK_DATE, valuation_mark_usd=mark,
            market_value_usd=basis + pnl, realized_pnl_usd=0, conditional_unrealized_pnl_usd=pnl,
            scenario_total_pnl_usd=pnl, position_state="HYPOTHETICAL RESIDUAL LONG IN THIS SENSITIVITY",
            source_nullification_state="SHORT LIFECYCLE UN-NULLIFIED FOR TEST; LONG RESIDUAL AFTER COVER",
            test_override_state="INCLUDED AS SCENARIO POSITION; NOT ACTUAL POSITION CLAIM",
            additivity_rule="ALTERNATIVE SENSITIVITY; do not sum across ATS sizes",
            count_in_core_v2="NO — hypothetical scenario residual",
            source_record_id=position_id("ATS-RESIDUAL-LONG", ticker, item["scenario"], qty),
            source_file="data/ats_manual_live_positions_v1.csv",
            audit_notes=item["notes"],
        ))
    return rows


def legacy_short_rows():
    ledger = read_csv(DATA / "oil_portfolio_trade_ledger_v2.csv")
    rows = []
    for item in ledger:
        if item["event"] != "ENTRY" or item["tag"] != "SHORT":
            continue
        ticker = normalized_ticker(item["ticker"])
        qty = dec(item["units"])
        entry = dec(item["logged_price"])
        rows.append(make_row(
            position_id=item["record_id"], row_type="LEGACY_BASELINE_SHORT_EVENT",
            book_or_model="Oil trade log — superseded legacy baseline", scenario_id="LEGACY_BASELINE_ONLY",
            ticker=ticker, side="SHORT", quantity=qty, quantity_unit="U ($10,000 model notional)",
            u_equivalent=qty, entry_date=item["date"], entry_time=item["time_mst"], entry_price_usd=entry,
            gross_basis_usd=qty * UNIT_NOTIONAL, position_state="SUPERSEDED / NOT ACTIVE IN POSITION REPLAY",
            source_nullification_state="NOT THE ATS SENSITIVITY NULLIFICATIONS",
            test_override_state="PRESERVED FOR AUDIT; NOT REACTIVATED",
            additivity_rule="Source event only; not an open holding",
            count_in_core_v2="NO", source_record_id=item["record_id"], source_file=item["source_file"],
            audit_notes=item["note"],
        ))
    return rows


def liquidation_reference_rows():
    source = read_csv(DATA / "ats_oil_liquidation_reported_v1.csv")
    rows = []
    for item in source:
        ticker = normalized_ticker(item["ticker"])
        event_id = item["record_id"]
        rows.append(make_row(
            position_id=event_id, row_type="REPORTED_LIQUIDATION_REFERENCE",
            book_or_model="ATS locked $200 LONG foundation — user-reported liquidation",
            scenario_id="REPORTED_FULL_LIQUIDATION; EXACT FILLS UNKNOWN", ticker=ticker, side="LONG",
            quantity=item.get("quantity_sold", ""), quantity_unit="reported all-units scope; exact count unknown",
            u_equivalent="", entry_date="", entry_price_usd="", gross_basis_usd="",
            exit_date=item.get("execution_date", ""), exit_price_usd=item.get("sale_price_points_as_stated", ""),
            valuation_date="", valuation_mark_usd="", market_value_usd="", realized_pnl_usd="",
            conditional_unrealized_pnl_usd="", scenario_total_pnl_usd="",
            position_state="USER-REPORTED CLOSED; QUANTITY/FILLS UNRECONCILED",
            source_nullification_state="Original source retained; hypothetical restoration shown separately",
            test_override_state="REFERENCE ROW ONLY",
            additivity_rule="Do not add to modeled-equivalent ATS restoration rows",
            count_in_core_v2="NO", source_record_id=event_id, source_file="data/ats_oil_liquidation_reported_v1.csv",
            audit_notes=item["notes"],
        ))
    return rows


def private_fund_related_positions():
    """Add distinct LCID lots recorded alongside the separate Private Fund oil book."""
    balance = read_csv(DATA / "november_2026_plus_plus_experiment_balance_sheet_v1.csv")
    rows = []
    for index, item in enumerate(balance):
        if item.get("ticker") != "LCID" or item.get("action", "").startswith("Close"):
            continue
        quantity = dec(item.get("quantity"))
        entry = dec(item.get("average_entry_price_usd"))
        mark = dec(item.get("snapshot_price_usd"))
        basis = dec(item.get("cost_basis_usd"))
        market_value = dec(item.get("market_value_usd"))
        pnl = dec(item.get("unrealized_pnl_usd"))
        ueq = (basis / UNIT_NOTIONAL) if basis is not None else None
        row_id = item.get("order_id") or position_id("PRIVATE-FUND-LCID", index, quantity, entry)
        rows.append(make_row(
            position_id=row_id, row_type="PRIVATE_FUND_LCID_POSITION_REFERENCE",
            book_or_model="Private Fund report; account mapping not independently reconciled",
            scenario_id="SEPARATE LCID LOT; DO NOT NET WITH OIL",
            ticker="LCID", side="LONG", quantity=quantity, quantity_unit="screenshot shares",
            u_equivalent=ueq, entry_date=item.get("as_of_date", ""), entry_price_usd=entry,
            gross_basis_usd=basis, valuation_date=item.get("as_of_date", ""), valuation_mark_usd=mark,
            market_value_usd=market_value, realized_pnl_usd=0,
            conditional_unrealized_pnl_usd=pnl,
            scenario_total_pnl_usd=pnl,
            position_state=("OPEN PER POSITION SCREENSHOT; SNAPSHOT DATE NOT SUPPLIED" if mark is not None else "BUY ORDER REPORTED FILLED; OPEN LOT UNMARKED"),
            source_nullification_state="NOT APPLICABLE", test_override_state="SEPARATE BOOK REFERENCE ONLY",
            additivity_rule="Separate LCID lot; account mapping and funding source unknown; do not net with Oil",
            count_in_core_v2="NO", source_record_id=row_id,
            source_file=item.get("source_artifact", "data/november_2026_plus_plus_experiment_balance_sheet_v1.csv"),
            audit_notes=item.get("notes", ""),
        ))
    return rows


def build():
    rows = []
    rows.extend(active_oil_rows())
    rows.extend(restored_long_rows())
    rows.extend(reinstated_short_rows())
    rows.extend(ats_manual_position_rows())
    rows.extend(ats_residual_long_rows())
    rows.extend(legacy_short_rows())
    rows.extend(liquidation_reference_rows())
    rows.extend(private_fund_related_positions())
    rows = sorted(rows, key=lambda r: (
        0 if r["size_group"] == "SMALL_UNITS" else 1,
        r["book_or_model"], r["ticker"], r["scenario_id"], r["entry_date"], r["position_id"],
    ))
    with OUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} position/event rows to {OUT.relative_to(ROOT)}")
    print(f"Small-unit rows: {sum(r['size_group'] == 'SMALL_UNITS' for r in rows)}")
    print(f"Large-unit rows: {sum(r['size_group'] == 'LARGE_UNITS' for r in rows)}")
    print(f"Unknown unit-convention rows: {sum(r['size_group'] == 'UNKNOWN_UNIT_CONVENTION' for r in rows)}")
    print(f"Un-nullified short lifecycle rows: {sum(r['row_type'] == 'REINSTATED_NULLIFIED_SHORT_LIFECYCLE' for r in rows)}")


if __name__ == "__main__":
    build()
