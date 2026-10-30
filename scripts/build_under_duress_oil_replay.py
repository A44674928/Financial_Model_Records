#!/usr/bin/env python3
"""Build an auditable, non-destructive under-duress oil close replay overlay."""

import csv
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVENTS = ROOT / "data/under_duress_oil_void_events_v1.csv"
POSITIONS = ROOT / "data/under_duress_oil_restored_positions_v1.csv"
FUNDING = ROOT / "data/under_duress_lcid_scenario_funding_v1.csv"
REPORT = ROOT / "reports/Under-Duress Oil Sale Void Replay.md"


def money(value: Decimal) -> str:
    return str(value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def read_events():
    with EVENTS.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError("void event manifest is empty")
    ids = [row["event_id"] for row in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("void event IDs must be unique")
    return rows


def build_positions(events):
    fields = [
        "event_id", "book", "scenario", "trade_date", "ticker", "void_status",
        "restored_side", "restored_quantity", "quantity_unit", "entry_price_usd",
        "mark_date", "mark_price_usd", "notional_basis_usd",
        "conditional_unrealized_pnl_usd", "reported_realized_pnl_if_sale_stands_usd",
        "source_reported_close_date", "source_reported_close_price_usd", "source_reported_close_pnl_usd",
        "source_artifact", "execution_status", "user_directed_nullification_status", "notes",
    ]
    output = []
    for event in events:
        qty = Decimal(event["restored_quantity"])
        if event["position_effect"] == "NULLIFY_SHORT_NO_POSITION":
            if qty != 0 or event["restored_side"] != "NONE":
                raise ValueError(f"nullified event must produce no position: {event['event_id']}")
            continue
        if event["position_effect"] != "RESTORE_POSITION":
            raise ValueError(f"unsupported position effect in {event['event_id']}")
        entry = Decimal(event["entry_price_usd"])
        mark = Decimal(event["mark_price_usd"]) if event.get("mark_price_usd") else None
        notional = Decimal(event["notional_basis_usd"]) if event.get("notional_basis_usd") else None
        if qty <= 0 or entry <= 0 or (notional is not None and notional <= 0) or (mark is not None and mark <= 0):
            raise ValueError(f"non-positive position input in {event['event_id']}")
        if mark is None:
            # The screenshot close was nullified/voided. Preserve its quote separately,
            # but do not use that invalidated close as a current mark.
            unrealized = None
        elif event["restored_side"] == "LONG":
            if event["quantity_unit"].startswith("U ("):
                unrealized = notional * (mark / entry - Decimal("1"))
            else:
                unrealized = qty * mark - notional
        elif event["restored_side"] == "SHORT":
            unrealized = notional * (Decimal("1") - mark / entry)
        else:
            raise ValueError(f"invalid restored side in {event['event_id']}")
        realized = event.get("reported_realized_pnl_usd", "")
        output.append({
            "event_id": event["event_id"],
            "book": event["book"],
            "scenario": event["scenario"],
            "trade_date": event["trade_date"],
            "ticker": event["ticker"],
            "void_status": (event.get("user_directed_nullification_status") or "").replace(" ", "_") or "VOIDED_IN_UNDER_DURESS_SCENARIO; ORIGINAL_SOURCE_PRESERVED",
            "restored_side": event["restored_side"],
            "restored_quantity": event["restored_quantity"],
            "quantity_unit": event["quantity_unit"],
            "entry_price_usd": event["entry_price_usd"],
            "mark_date": event["mark_date"],
            "mark_price_usd": event["mark_price_usd"],
            "notional_basis_usd": money(notional) if notional is not None else "",
            "conditional_unrealized_pnl_usd": money(unrealized) if unrealized is not None else "",
            "reported_realized_pnl_if_sale_stands_usd": realized,
            "source_reported_close_date": event.get("source_reported_close_date", ""),
            "source_reported_close_price_usd": event.get("source_reported_close_price_usd", ""),
            "source_reported_close_pnl_usd": event.get("source_reported_close_pnl_usd", ""),
            "source_artifact": event["source_artifact"],
            "execution_status": event["execution_status"],
            "user_directed_nullification_status": event.get("user_directed_nullification_status", ""),
            "notes": event["notes"],
        })
    with POSITIONS.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(output)
    return output


def write_report(events, positions):
    with FUNDING.open(newline="", encoding="utf-8") as handle:
        funding = list(csv.DictReader(handle))
    if len(funding) != 1:
        raise ValueError("expected one scenario funding record")
    f = funding[0]
    lines = [
        "# Under-Duress Oil Sale Void Replay",
        "",
        "> **Scenario overlay, not a change to source history.** The user directed that the October 29 Private Fund oil close records be nullified and voided; the earlier BRENT and USOIL longs remain open at their reported entry prices. Other listed oil sales/closes are treated as voidable in this separate under-duress scenario. The private portfolio rows remain separate from public ATS books. Original screenshots, trade logs, ATS reports, and historical records remain preserved. This is not audited brokerage accounting or legal advice.",
        "",
        "## ATS manual-review rationale and scope",
        "",
        "Per the user's report, in the public portfolio the ATS flagged sell orders for manual review under the standing order to ‘buy a few more barrels every couple dollars’. The user says required risk protocols were not satisfied and directs that the affected public-portfolio oil sales be undone in this scenario. This explanation is user-reported; no ATS alert, review ticket, or order-to-book mapping was supplied. See the [Under-Duress Audit / Rollback Log](Under-Duress%20Audit%20Rollback%20Log.md).",
        "",
        "This rationale is scoped to the public portfolio and must not be generalized to private ATS decisions. For the two October 29 Private Fund screenshot close records, the user separately directed that the closes be nullified and voided and that the earlier longs remain open. This status is user-directed; no platform order-status artifact independently confirms the void. Other unlogged or differently personalized ATS events remain outside this replay.",
        "",
        "## Replay policy",
        "",
        "- A voided close is skipped by the replay; its original event remains in the audit trail. Long sales restore their linked long lots. The ATS sensitivity short openings and their linked covers are explicitly nullified per the user's latest direction, so they create no open short positions. No cross-book netting or silent deletion is performed.",
        "- This replay covers the ATS locked $200 LONG foundation liquidation; the documented legacy oil trims; the named October 26 50U cash-outs; the October 29 TradingView Paper Trading closes; and the ATS 10U/20U/30U/40U close sensitivities. ATS scenario rows are alternatives, not additive positions.",
        "- The ATS foundation is restored from the last pre-liquidation modeled allocation snapshot dated October 26, 2026. Its quantity equivalents and values are model outputs, not verified contracts or broker fills; exact liquidation quantities, fills, and timing remain unknown.",
        "- Per-book marks are the event price or last documented pre-liquidation mark where valid. For the two nullified October 29 close records, the displayed close prices are preserved only as source evidence and are not used as marks; no replacement current mark is supplied. Rows do not form one simultaneous portfolio valuation. Contract multipliers, fees, taxes, funding sources, and leverage are not inferred.",
        "",
        "## Restored positions",
        "",
        "The following table is an event-level restoration overlay: it adds back lots affected by the voided closes, while unaffected open lots remain in their original book records. It is not a complete account holdings export. Rows in a sensitivity group are alternatives; do **not** add them together. The two foundation rows, the private-fund paper-trade lots, the legacy core lots, and ATS/manual campaign rows are distinct books and are not combined into one fund total.",
        "",
        "| Book / scenario | Ticker | Restored side | Quantity | Basis | Mark | Conditional unrealized PnL |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for p in positions:
        mark_display = f"${Decimal(p['mark_price_usd']):,.6f} ({p['mark_date']})" if p.get("mark_price_usd") else "Not supplied"
        pnl_display = f"${Decimal(p['conditional_unrealized_pnl_usd']):,.2f}" if p.get("conditional_unrealized_pnl_usd") else "Not calculated"
        entry_display = f"${Decimal(p['entry_price_usd']):,.6f}"
        lines.append(
            f"| {p['book']} / {p['scenario']} | {p['ticker']} | {p['restored_side']} | "
            f"{p['restored_quantity']} {p['quantity_unit']} | {entry_display} | {mark_display} | {pnl_display} |"
        )
    lines.extend([
        "",
        "### Screenshot PnL treatment",
        "",
        "The user directed that both October 29 Private Fund oil closes be **nullified and voided**. Keep the earlier BRENT and USOIL longs open at $114.043 and $99.18, respectively, with quantities as reported in the screenshots. Their entry dates/times are unknown. The screenshot close prices and PnL are preserved as voided-source details only; they are not current marks or realized PnL. No mark-to-market PnL is calculated for these two lots because no valid later mark is supplied. The screenshot source itself remains unchanged, and platform void status is not independently confirmed.",
        "",
        "### ATS campaign sensitivities",
        "",
        "The modeled ATS long exits restore the corresponding 10U, 20U, 30U, or 40U of the tagged 50U campaign lot. Per the user's latest direction, the matching short-opening and subsequent cover/closure lifecycle is nullified in every sensitivity: **the replay has no open ATS shorts**. The eight nullification decisions remain in the event register but do not appear as restored positions. Quantities are user-reported/model sensitivities, not a verified ATS fill history; each scenario remains separate.",
        "",
        "Nullified short-lifecycle records: **8** (BRENT and OIL/USOIL at the 10U, 20U, 30U, and 40U sensitivities). These are audit actions, not positions.",
        "",
        "## LCID buyout consideration as scenario funding",
        "",
        f"| Hypothetical funding component | Amount | Treatment in this replay |",
        f"|---|---:|---|",
        f"| Cash consideration | ${Decimal(f['cash_component_usd']):,.2f} | Scenario cash funding component; not verified as received or allocated |",
        f"| Share/equity consideration | ${Decimal(f['equity_component_usd']):,.2f} | Non-cash scenario value; not treated as spendable cash |",
        f"| **Total consideration pool** | **${Decimal(f['total_consideration_usd']):,.2f}** | **Hypothetical restoration pool; unallocated across books** |",
        "",
        "The LCID terms remain hypothetical, not an actual bid or completed transaction. The $1.31B current market-cap reference is user-provided for 2026-10-29. For this replay only, the full $4.2B consideration is tagged as new scenario funding to compensate for the voided oil-sale scenario, while retaining the $2.2B cash / $2.0B equity distinction. No proceeds are claimed as received; the pool is not assigned to BRENT, OIL, or any specific account, and is not included in a cash balance or reconciled NAV.",
        "",
        "## Source event register and audit limits",
        "",
        f"The versioned event register contains **{len(events)}** scenario actions, including **{sum(row['position_effect'] == 'NULLIFY_SHORT_NO_POSITION' for row in events)}** short-lifecycle nullifications. The restored-position file contains **{len(positions)}** position rows: [`under_duress_oil_restored_positions_v1.csv`](../data/under_duress_oil_restored_positions_v1.csv). The full event register is [`under_duress_oil_void_events_v1.csv`](../data/under_duress_oil_void_events_v1.csv); scenario funding terms are [`under_duress_lcid_scenario_funding_v1.csv`](../data/under_duress_lcid_scenario_funding_v1.csv).",
        "",
        "The user's prior report of zero oil units after the ATS liquidation and the earlier realized-PnL records remain part of the preserved historical source record. This replay is a parallel what-if view that marks selected close events voidable; it does not establish that any broker or ATS reversed an execution. Unknown ATS quantities are not turned into actual holdings; only the last documented modeled allocation is restored as quantity equivalents.",
        "",
    ])
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def main():
    events = read_events()
    positions = build_positions(events)
    write_report(events, positions)
    print(f"Built {len(positions)} under-duress oil replay positions")


if __name__ == "__main__":
    main()
