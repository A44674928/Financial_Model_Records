#!/usr/bin/env python3
"""Build the user-directed BRENT full-exit record at $119 (2026-10-30).

Scope per user direction: REAL positions only. The Under-Duress scenario overlay
and the 10U/20U/30U/40U ATS exit sensitivities are deliberately excluded and are
not modified by this builder.

The 2026-10-29 Private Fund BRENT close at $115.777 was previously nullified and
voided per user instruction. The user now directs that this exit SUPERSEDES that
void: the real exit price is $119. The superseded screenshot close price and its
displayed PnL are preserved as source evidence only, not as marks or realized PnL.

PnL is price-only, before costs, and per lot. Books are kept separate; their unit
conventions are not verified as interchangeable, so no cross-book grand total is
asserted.
"""

import csv
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/brent_sold_119_20261030_v1.csv"

TICKER = "BRENT"
SALE_PRICE = Decimal("119")
SALE_DATE = "2026-10-30"
SALE_TIME = "not supplied; 13:00 MST used only as a chronology ordering placeholder"
UNIT_NOTIONAL = Decimal("10000")

POLICY_LABEL = "USER_DIRECTED_POST_CUTOFF_EXIT_SCOPED_EXCEPTION_20261030"
EXEC_STATUS = (
    "User-reported sale price; not an independently verified brokerage fill, "
    "execution, or audited account record"
)

SUPERSEDED_CLOSE_PRICE = Decimal("115.777")
SUPERSEDED_CLOSE_PNL = Decimal("933875016.74")

FIELDS = [
    "record_id", "book_or_model", "book_scope", "ticker", "side", "lot_id",
    "entry_date", "entry_time", "entry_price_usd", "quantity", "quantity_unit",
    "quantity_convention", "gross_basis_usd", "sale_date", "sale_price_usd",
    "model_implied_gross_proceeds_usd", "price_only_realized_pnl_usd",
    "pnl_formula", "prior_status", "supersedes_record_id",
    "superseded_close_price_evidence_usd", "superseded_close_pnl_evidence_usd",
    "position_state_after", "overlap_flag", "book_subtotal_treatment",
    "additivity_rule", "execution_verification_status", "policy_label",
    "source_file", "notes",
]

NO_OVERLAP = "NONE"

# PRIMARY rows count toward their own book's subtotal. WITHIN_BOOK_COMPONENT rows
# are detail for another row in the SAME book and are excluded from that subtotal
# to avoid double counting. A cross-book overlap is still PRIMARY in its own book:
# it counts there, but the two books must never be summed together.
PRIMARY = "PRIMARY — counts in this book's subtotal"
COMPONENT = "WITHIN_BOOK_COMPONENT — detail of another row in this book; excluded from the subtotal"
ADDITIVITY = "Within-book lots are additive; do NOT sum across books — unit conventions differ and are not verified as interchangeable"


def money(value: Decimal) -> str:
    return str(value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def unit_lot(record_id, book, book_scope, lot_id, entry_date, entry_time,
             entry_price, units, source_file, prior_status, overlap, notes,
             supersedes="", sup_price="", sup_pnl="", treatment=PRIMARY):
    """U-denominated model lot: 1U = $10,000 entry notional."""
    entry_price = Decimal(str(entry_price))
    units = Decimal(str(units))
    notional = units * UNIT_NOTIONAL
    pnl = notional * (SALE_PRICE / entry_price - Decimal("1"))
    proceeds = notional + pnl
    return {
        "record_id": record_id, "book_or_model": book, "book_scope": book_scope,
        "ticker": TICKER, "side": "LONG", "lot_id": lot_id,
        "entry_date": entry_date, "entry_time": entry_time,
        "entry_price_usd": str(entry_price), "quantity": str(units),
        "quantity_unit": "U ($10,000 model notional)",
        "quantity_convention": "Fixed-notional model unit; implied exposure Q = notional / entry price",
        "gross_basis_usd": money(notional), "sale_date": SALE_DATE,
        "sale_price_usd": str(SALE_PRICE),
        "model_implied_gross_proceeds_usd": money(proceeds),
        "price_only_realized_pnl_usd": money(pnl),
        "pnl_formula": "units x $10,000 x (sale_price / entry_price - 1)",
        "prior_status": prior_status, "supersedes_record_id": supersedes,
        "superseded_close_price_evidence_usd": sup_price,
        "superseded_close_pnl_evidence_usd": sup_pnl,
        "position_state_after": "CLOSED — SOLD AT $119; zero units remain in this book",
        "overlap_flag": overlap, "book_subtotal_treatment": treatment,
        "additivity_rule": ADDITIVITY,
        "execution_verification_status": EXEC_STATUS,
        "policy_label": POLICY_LABEL, "source_file": source_file, "notes": notes,
    }


def qty_lot(record_id, book, book_scope, lot_id, entry_date, entry_time,
            entry_price, quantity, quantity_unit, quantity_convention,
            source_file, prior_status, overlap, notes,
            supersedes="", sup_price="", sup_pnl="", treatment=PRIMARY,
            infer_basis=True):
    """Quantity-denominated lot: PnL = quantity x (sale - entry)."""
    entry_price = Decimal(str(entry_price))
    quantity = Decimal(str(quantity))
    pnl = quantity * (SALE_PRICE - entry_price)
    if infer_basis:
        basis = money(quantity * entry_price)
        proceeds = money(quantity * SALE_PRICE)
    else:
        # Source book deliberately infers no cash basis or market value for this
        # lot. Price-only realized PnL is still quantity x price change, which
        # needs no basis; do not manufacture one.
        basis = ""
        proceeds = ""
    return {
        "record_id": record_id, "book_or_model": book, "book_scope": book_scope,
        "ticker": TICKER, "side": "LONG", "lot_id": lot_id,
        "entry_date": entry_date, "entry_time": entry_time,
        "entry_price_usd": str(entry_price), "quantity": str(quantity),
        "quantity_unit": quantity_unit, "quantity_convention": quantity_convention,
        "gross_basis_usd": basis, "sale_date": SALE_DATE,
        "sale_price_usd": str(SALE_PRICE),
        "model_implied_gross_proceeds_usd": proceeds,
        "price_only_realized_pnl_usd": money(pnl),
        "pnl_formula": "quantity x (sale_price - entry_price)",
        "prior_status": prior_status, "supersedes_record_id": supersedes,
        "superseded_close_price_evidence_usd": sup_price,
        "superseded_close_pnl_evidence_usd": sup_pnl,
        "position_state_after": "CLOSED — SOLD AT $119; zero units remain in this book",
        "overlap_flag": overlap, "book_subtotal_treatment": treatment,
        "additivity_rule": ADDITIVITY,
        "execution_verification_status": EXEC_STATUS,
        "policy_label": POLICY_LABEL, "source_file": source_file, "notes": notes,
    }


def build_rows():
    rows = []

    # ---- Book A: Private Fund / TradingView Paper Trading -------------------
    rows.append(qty_lot(
        "BRENT119-PF-538566907",
        "Private Fund / TradingView Paper Trading",
        "Harshal's Private Fund — November 2026++ Experiment",
        "PF-BRENT-CLOSE-20261029",
        "Earlier entry; exact date/time not supplied", "not supplied",
        "114.043", "538566907", "platform-reported units",
        "Platform-reported units transcribed from screenshot; no contract multiplier inferred",
        "Archive/November_2026_Experiment_Oil_Closes_2026-10-29/IMG_1218.png",
        "OPEN; 2026-10-29 close at $115.777 previously NULLIFIED AND VOIDED per user instruction",
        NO_OVERLAP,
        "Supersedes the voided 2026-10-29 close per user direction: the real exit price is $119. "
        "The screenshot close price $115.777 and displayed PnL $933,875,016.74 are preserved in the "
        "superseded_* columns as source evidence only and are NOT booked. Separated from the earlier "
        "void so the audit trail is not rewritten.",
        supersedes="PRIVATE_TV_BRENT_CLOSE_20261029",
        sup_price=str(SUPERSEDED_CLOSE_PRICE), sup_pnl=money(SUPERSEDED_CLOSE_PNL),
        infer_basis=False,
    ))

    # ---- Book B: ATS locked $200 LONG foundation / $20B Units Experiment ----
    foundation_scope = (
        "ATS locked $200 LONG foundation, combined from the $20B Units Experiment pool residual "
        "and the restored supplemental $20B order"
    )
    rows.append(qty_lot(
        "BRENT119-ATS-FOUNDATION",
        "ATS locked $200 LONG foundation / $20B Units Experiment pool",
        foundation_scope,
        "ATS-FOUNDATION-BRENT-LIQ",
        "Sep. 23 (pool residual leg) and supplemental order; exact date/time not supplied",
        "not supplied",
        "108.4473117398634879678464199", "179865012.22971259",
        "modeled quantity equivalent",
        "Modeled quantity equivalent = allocation dollars / modeled entry price; NOT contracts, barrels, or verified broker quantities",
        "Units Experiment Pool Allocation.md; data/units_experiment_pool_allocation_20261026.csv",
        "Reported liquidated by the ATS at $114.670-$117.345; user now directs a single $119 exit price",
        "Overlaps the two component legs BRENT119-ATS-POOL-RESIDUAL and BRENT119-ATS-SUPPLEMENTAL — this row is their combination, not an additional position",
        "Blended quantity-weighted basis. Supersedes the earlier user-reported ATS sale-price bands "
        "($114.670-$117.345) for this book. The $2.4B conservative endpoint and the prior price-envelope "
        "estimates are preserved as earlier references and are not restated here. "
        "The user reports that the ATS asked for a price check at $119 and then made the decision "
        "to sell on its own. This decision process is user-reported and not independently verified; "
        "the time and price source of the check were not supplied.",
    ))
    rows.append(qty_lot(
        "BRENT119-ATS-POOL-RESIDUAL",
        "ATS locked $200 LONG foundation / $20B Units Experiment pool",
        foundation_scope + " — component leg 1 of 2",
        "UNITS-POOL-BRENT-RESIDUAL",
        "Sep. 23 (2026 model alignment)", "not supplied",
        "102.315", "92912838.31666911", "modeled quantity equivalent",
        "Modeled quantity equivalent = allocation dollars / modeled entry price; NOT contracts, barrels, or verified broker quantities",
        "Units Experiment Pool Allocation.md; data/units_experiment_pool_allocation_20261026.csv",
        "Reported liquidated by the ATS; component of the combined foundation",
        "COMPONENT of BRENT119-ATS-FOUNDATION — do not add to it",
        "Component leg detail retained for audit continuity. $9,506,377,052.37 allocation at $102.315.",
        treatment=COMPONENT,
    ))
    rows.append(qty_lot(
        "BRENT119-ATS-SUPPLEMENTAL",
        "ATS locked $200 LONG foundation / $20B Units Experiment pool",
        foundation_scope + " — component leg 2 of 2",
        "UNITS-POOL-BRENT-SUPPLEMENTAL",
        "Restored supplemental full-size $20B order; exact date/time not supplied", "not supplied",
        "115.00", "86952173.91304348", "modeled quantity equivalent",
        "Modeled quantity equivalent = allocation dollars / modeled entry price; NOT contracts, barrels, or verified broker quantities",
        "Units Experiment Pool Allocation.md; data/units_experiment_pool_allocation_20261026.csv",
        "Reported liquidated by the ATS; component of the combined foundation",
        "COMPONENT of BRENT119-ATS-FOUNDATION — do not add to it",
        "Component leg detail retained for audit continuity. $9,999,500,000.00 remaining in the oil "
        "foundation after the 50U transfer to THE WINNING MODEL, at $115.00.",
        treatment=COMPONENT,
    ))
    rows.append(qty_lot(
        "BRENT119-WINNER-TRANSFER",
        "THE WINNING MODEL — 50U transferred from the oil foundation",
        "Single allocation reclassification of $500,000 notional carved out of the supplemental order",
        "TWM-BRENT-50U-TRANSFER",
        "2026-10-26 (date-level assumption)", "not supplied",
        "115.00", "4347.82608696", "modeled quantity equivalent",
        "Modeled quantity equivalent = allocation dollars / modeled entry price; NOT contracts, barrels, or verified broker quantities",
        "Units Experiment Pool Allocation.md",
        "Open as a Winner-assigned reallocation burden",
        "Carved OUT of the supplemental $10B leg; already excluded from BRENT119-ATS-SUPPLEMENTAL — do not double count",
        "Recorded because the user directed that ALL BRENT was sold. This is a capital/burden "
        "reallocation, not a performance reward; it does not alter THE WINNING MODEL's historical "
        "realized PnL or champion-selection result.",
    ))

    # ---- Book C: Core ledger replay (trades/BRENT.txt), all four variants ---
    core_scope = "Core paper-trade ledger replay — all four variants (V1/V2/V3A/V3B) share these BRENT lots"
    core_prior = "OPEN LONG in the core replay; marked to the 2026-10-26 supplied EOD close of $115.38"
    core_rows = [
        ("CORE-BRENT-1U-20260923", "1U core entry", "2026-09-23", "06:30 MST", "102.50", 1),
        ("CORE-BRENT-1U-20261002", "1U core entry", "2026-10-02", "06:30 MST", "107.00", 1),
        ("CORE-BRENT-1U-20261004", "1U core entry", "2026-10-04", "06:30 MST", "106.446", 1),
        ("CORE-BRENT-1U-20261009", "1U core entry", "2026-10-09", "06:30 MST", "106.50", 1),
        ("CORE-BRENT-1U-20261019", "1U core entry", "2026-10-19", "06:30 MST", "111.025", 1),
        ("CORE-BRENT-40U-RESIDUAL", "Residual of the tagged 50U Manual-Automatic lot after the 10U target trim at $117.00",
         "2026-10-19", "06:30 MST", "111.412", 40),
        ("CORE-BRENT-10U-20261025-1722", "MANUAL LIVE TEST POSITION replenishment",
         "2026-10-25", "17:22 MST (modeled midpoint)", "115.792", 10),
        ("CORE-BRENT-10U-20261025-2000", "MANUAL LIVE TEST POSITION replenishment",
         "2026-10-25", "20:00 MST (approx.)", "114.80", 10),
        ("CORE-BRENT-35U-20261025-2035", "MANUALLY APPROVED SHORT CLOSURE — unallocated excess left LONG",
         "2026-10-25", "20:35 MST", "114.627", 35),
    ]
    for lot_id, lot_desc, date, time, price, units in core_rows:
        overlap = NO_OVERLAP
        if units == 10 and price in ("115.792", "114.80"):
            overlap = ("Also appears in Book E (ATS/manual live positions) as the same manual "
                       "replenishment lot — do not count twice across books")
        if price == "111.412":
            overlap = ("Also appears in Book D (Oil v2) as the full untrimmed 50U lot; Oil v2 is capped "
                       "at 2026-10-19 trade events so it retains 50U where this book retains 40U")
        rows.append(unit_lot(
            "BRENT119-" + lot_id, "Core paper-trade ledger replay", core_scope, lot_id,
            date, time, price, units, "trades/BRENT.txt", core_prior, overlap,
            f"{lot_desc}. Closed at the user-directed $119 exit.",
        ))

    # ---- Book D: Oil v2 mark-forward + November 2026 Oil Clean Sheet -------
    d_scope = ("Oil portfolio v2 mark-forward and the November 2026 Oil Clean Sheet — four variants "
               "(V1/V2/V3A/V3B) are alternatives, per variant only")
    d_add = ("Per-variant only; the four Oil v2 variants are ALTERNATIVES and are not additive to one another")
    rows.append(unit_lot(
        "BRENT119-OILV2-50U", "Oil portfolio v2 / November 2026 Oil Clean Sheet", d_scope,
        "OILV2-BRENT-50U-LARGE", "2026-10-19", "06:30 MST", "111.412", 50,
        "reports/Oil Portfolio — 2026-10-26 Update.md; data/november_2026_oil_clean_sheet_v1.csv",
        "OPEN IN MARK-FORWARD MODEL; ACTIVE in the November clean sheet; marks stale after 2026-10-26",
        "Same source lot as CORE-BRENT-40U-RESIDUAL but untrimmed in Oil v2 (trade-event cutoff 2026-10-19) — do not add across books",
        "Retains the full 50U because Oil v2's trade-event cutoff is 2026-10-19 and excludes the "
        "post-cutoff 10U trim. Closed at the user-directed $119 exit.",
    ))
    for tranche, price, qty in (
        ("1", "117", "341.8803418803418803418803419"),
        ("2", "118", "338.9830508474576271186440678"),
    ):
        rows.append(qty_lot(
            f"BRENT119-OILV2-CONV-T{tranche}",
            "Oil portfolio v2 / November 2026 Oil Clean Sheet", d_scope,
            f"OILV2-BRENT-CONVERTED-TRANCHE-{tranche}",
            "November 2026 clean-sheet conversion; exact date/time not supplied", "not supplied",
            price, qty, "price-derived calculated units",
            "Clean-sheet conversion equivalent = $40,000 notional / conversion price; a price-derived equivalent, not a verified barrel, contract, or brokerage quantity",
            "reports/November 2026 Oil Clean Sheet.md; data/november_2026_oil_clean_sheet_v1.csv",
            "ACTIVE in the November clean sheet as converted Small Unit notional",
            "Distinct from the U-denominated Oil v2 lots; part of the same per-variant clean-sheet BRENT line",
            f"Conversion tranche {tranche}: $40,000 of the $80,000 BRENT-allocated converted notional "
            f"at ${price}. The conversion was a clean-sheet calculation, not an execution; the $119 "
            "exit is now applied to it.",
        ))

    # ---- Book E: ATS/manual live positions reconciliation ------------------
    e_scope = "ATS and Manual Live Position Reconciliation — real (non-scenario) BRENT lots only"
    e_add = ("Real lots only; the 10U/20U/30U/40U ATS exit sensitivities are EXCLUDED per user direction "
             "and remain alternative scenarios that must not be summed")
    e_rows = [
        ("ATSMANUAL-BRENT-50U-115000", "ATS modeled open position", "2026-10-26", "not supplied",
         "115.00", 50, NO_OVERLAP,
         "Separate 50U fixed-price ATS long addition after the modeled short closures."),
        ("ATSMANUAL-BRENT-10U-115025", "MANUALLY APPROVED ATS ORDER", "2026-10-26",
         "not supplied; date-level assumption only", "115.025", 10, NO_OVERLAP,
         "User-reported post-cutoff long addition; classification disclosed as a manually approved ATS order."),
        ("ATSMANUAL-BRENT-16U-114900", "User-reported LONG entry; category not specified", "2026-10-26",
         "not supplied; date-level assumption only", "114.900", 16, NO_OVERLAP,
         "User-reported open long; strategy classification and execution not independently verified."),
        ("ATSMANUAL-BRENT-10U-115792", "MANUAL LIVE TEST POSITION replenishment", "2026-10-25",
         "17:22 MST (modeled midpoint)", "115.792", 10,
         "Same lot as CORE-BRENT-10U-20261025-1722 in Book C — do not count twice across books",
         "Separate manual replenishment lot recorded in the ATS/manual reconciliation."),
        ("ATSMANUAL-BRENT-10U-114800", "MANUAL LIVE TEST POSITION replenishment", "2026-10-25",
         "20:00 MST (approx.)", "114.800", 10,
         "Same lot as CORE-BRENT-10U-20261025-2000 in Book C — do not count twice across books",
         "Separate manual replenishment lot recorded in the ATS/manual reconciliation."),
    ]
    for lot_id, event, date, time, price, units, overlap, note in e_rows:
        rows.append(unit_lot(
            "BRENT119-" + lot_id, "ATS and Manual Live Position Reconciliation", e_scope,
            lot_id, date, time, price, units,
            "ATS and Manual Live Position Reconciliation.md; data/ats_manual_live_positions_v1.csv",
            "OPEN LONG; user-reported, not independently verified", overlap,
            f"{event}. {note} Closed at the user-directed $119 exit.",
        ))
        rows[-1]["additivity_rule"] = e_add

    return rows


def within_book_subtotals(rows):
    """Subtotal price-only realized PnL per book.

    Only WITHIN_BOOK_COMPONENT rows are excluded, because they are detail for
    another row in the same book. A cross-book overlap stays PRIMARY in its own
    book: it counts there, but the two books must never be summed together.
    """
    books = {}
    for row in rows:
        book = row["book_or_model"]
        kind = ("component" if row["book_subtotal_treatment"].startswith("WITHIN_BOOK_COMPONENT")
                else "primary")
        entry = books.setdefault(book, {"primary": Decimal(0), "component": Decimal(0),
                                        "rows": 0, "overlaps": 0})
        entry[kind] += Decimal(row["price_only_realized_pnl_usd"])
        entry["rows"] += 1
        if row["overlap_flag"] != NO_OVERLAP and kind == "primary":
            entry["overlaps"] += 1
    return books


def main():
    rows = build_rows()
    ids = [row["record_id"] for row in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("record IDs must be unique")
    for row in rows:
        if Decimal(row["sale_price_usd"]) != SALE_PRICE:
            raise ValueError(f"unexpected sale price in {row['record_id']}")
        if row["ticker"] != TICKER:
            raise ValueError(f"unexpected ticker in {row['record_id']}")
        if not row["price_only_realized_pnl_usd"]:
            raise ValueError(f"missing realized PnL in {row['record_id']}")

    # Integrity check: the combined foundation must equal the sum of its component legs.
    by_id = {row["record_id"]: row for row in rows}
    combined = Decimal(by_id["BRENT119-ATS-FOUNDATION"]["quantity"])
    legs = (Decimal(by_id["BRENT119-ATS-POOL-RESIDUAL"]["quantity"])
            + Decimal(by_id["BRENT119-ATS-SUPPLEMENTAL"]["quantity"]))
    if abs(combined - legs) > Decimal("0.000001"):
        raise ValueError(f"foundation quantity does not tie to component legs: {combined} vs {legs}")
    combined_pnl = Decimal(by_id["BRENT119-ATS-FOUNDATION"]["price_only_realized_pnl_usd"])
    leg_pnl = (Decimal(by_id["BRENT119-ATS-POOL-RESIDUAL"]["price_only_realized_pnl_usd"])
               + Decimal(by_id["BRENT119-ATS-SUPPLEMENTAL"]["price_only_realized_pnl_usd"]))
    if abs(combined_pnl - leg_pnl) > Decimal("0.02"):
        raise ValueError(f"foundation PnL does not tie to component legs: {combined_pnl} vs {leg_pnl}")

    # Core ledger must total 100U, matching Core Cost Basis After Closure Credits.
    core_units = sum(Decimal(r["quantity"]) for r in rows
                     if r["book_or_model"] == "Core paper-trade ledger replay")
    if core_units != Decimal("100"):
        raise ValueError(f"core ledger open BRENT must be 100U, got {core_units}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    books = within_book_subtotals(rows)
    print(f"wrote {len(rows)} rows to {OUT.relative_to(ROOT)}\n")
    print("WITHIN-BOOK PRICE-ONLY REALIZED PnL AT $119 (before costs; not additive across books)")
    for book, entry in books.items():
        print(f"\n  {book}")
        print(f"    rows: {entry['rows']}"
              + (f"  ({entry['overlaps']} with a cross-book overlap flag)" if entry["overlaps"] else ""))
        print(f"    BOOK SUBTOTAL (price-only, before costs): ${entry['primary']:,.2f}")
        if entry["component"]:
            print(f"    component detail already inside the subtotal: ${entry['component']:,.2f}")


if __name__ == "__main__":
    main()
