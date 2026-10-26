#!/usr/bin/env python3
"""Build a separate, explicitly uncertain ATS/manual oil-position reconciliation.

The output is a scenario ledger, not a verified execution record. It intentionally
stays separate from the historical core replay, whose Oct. 23 model remains the
previous baseline until actual quantities/fills can be reconciled.
"""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "data" / "ats_manual_live_positions_v1.csv"
REPORT_PATH = ROOT / "ATS and Manual Live Position Reconciliation.md"

# The user selected the tagged 50U Weekend Oil lots as a proxy denominator.
# ATS execution sizes below are sensitivities, not probabilities or known fills.
LOTS = {
    "BRENT": {
        "ats_exit": 118.0,
        "short_cover": 114.627,
        "manual_closure_order_units": 35,
        "new_ats_units": 50,
        "new_ats_entry_price": 115.0,
        "manual_adds": [
            ("2026-10-25", "17:22 MST (modeled midpoint)", "Manual replenishment", 10, 115.792),
            ("2026-10-25", "20:00 MST (approx.)", "Manual replenishment", 10, 114.80),
        ],
    },
    "OIL": {
        "ats_exit": 103.50,
        "short_cover": 100.74,
        "manual_closure_order_units": 34,
        "new_ats_units": 50,
        "new_ats_entry_price": 101.0,
        "manual_adds": [
            ("2026-10-25", "17:22 MST (modeled midpoint)", "Manual replenishment", 10, 101.74),
            ("2026-10-25", "20:00 MST (approx.)", "Manual replenishment", 10, 101.00),
        ],
    },
}
SCENARIOS = [(10, "25% of ATS ceiling"), (20, "50% of ATS ceiling"), (30, "75% of ATS ceiling"), (40, "100% of ATS ceiling")]
FIELDS = [
    "record_type", "scenario", "ticker", "date", "time_mst", "event",
    "units", "price", "reference_lot_units", "ats_allocation_ceiling_units",
    "manual_reference_allocation_units", "ats_long_units_remaining_from_reference_lot",
    "manual_long_units_remaining_from_reference_lot", "ats_short_open_units",
    "initial_ats_cover_units", "ats_short_units_after_initial_cover",
    "manual_approved_buy_order_units", "manual_approved_short_close_units",
    "ats_short_units_remaining_after_manual_close", "residual_long_units_from_approved_buy",
    "buy_supply_units_counted_as_new_long", "status", "notes",
]


def records() -> list[dict[str, str]]:
    result: list[dict[str, str]] = []
    for ticker, lot in LOTS.items():
        for executed_units, scenario in SCENARIOS:
            after_initial_cover = max(executed_units - 10, 0)
            approved_cover = min(lot["manual_closure_order_units"], after_initial_cover)
            remaining_short = after_initial_cover - approved_cover
            residual_long = lot["manual_closure_order_units"] - approved_cover
            result.append({
                "record_type": "AUTOMATED TRADING SYSTEM LIVE POSITIONS — scenario",
                "scenario": scenario,
                "ticker": ticker,
                "date": "2026-10-23",
                "time_mst": "not supplied; date-level assumption only",
                "event": "ATS LONG exit and equal-size SHORT opening; then 10U modeled cover and MANUALLY APPROVED SHORT CLOSURE",
                "units": str(executed_units),
                "price": f"{lot['ats_exit']:.3f}" if ticker == "BRENT" else f"{lot['ats_exit']:.2f}",
                "reference_lot_units": "50",
                "ats_allocation_ceiling_units": "40",
                "manual_reference_allocation_units": "10",
                "ats_long_units_remaining_from_reference_lot": str(40 - executed_units),
                "manual_long_units_remaining_from_reference_lot": "10",
                "ats_short_open_units": str(executed_units),
                "initial_ats_cover_units": "10",
                "ats_short_units_after_initial_cover": str(after_initial_cover),
                "manual_approved_buy_order_units": str(lot["manual_closure_order_units"]),
                "manual_approved_short_close_units": str(approved_cover),
                "ats_short_units_remaining_after_manual_close": str(remaining_short),
                "residual_long_units_from_approved_buy": str(residual_long),
                "buy_supply_units_counted_as_new_long": str(residual_long),
                "status": "User-reported ATS activity; quantity unverified; scenario only, not a confirmed fill",
                "notes": (
                    f"ATS exit/short price supplied by user; fixed-notional proxy. The 40U ATS ceiling and 10U manual remainder "
                    f"are an 80/20 split of the tagged 50U lot. After the initial 10U modeled cover at ${lot['short_cover']:.3f}, "
                    f"the user-directed {lot['manual_closure_order_units']}U MANUALLY APPROVED SHORT CLOSURE order is first allocated "
                    f"to the remaining ATS short. Any unused order units remain LONG and alone count as new long buy supply."
                ),
            })
        new_price = lot["new_ats_entry_price"]
        result.append({
            "record_type": "ATS modeled open position",
            "scenario": "Separate fixed-price Oct. 26 addition; modeled, not verified fill",
            "ticker": ticker,
            "date": "2026-10-26",
            "time_mst": "not supplied",
            "event": "ATS LONG entry at fixed user-supplied price",
            "units": str(lot["new_ats_units"]),
            "price": f"{new_price:.3f}" if ticker == "BRENT" else f"{new_price:.2f}",
            "reference_lot_units": "",
            "ats_allocation_ceiling_units": "",
            "manual_reference_allocation_units": "",
            "ats_long_units_remaining_from_reference_lot": "",
            "manual_long_units_remaining_from_reference_lot": "",
            "ats_short_open_units": "",
            "initial_ats_cover_units": "",
            "ats_short_units_after_initial_cover": "",
            "manual_approved_buy_order_units": "",
            "manual_approved_short_close_units": "",
            "ats_short_units_remaining_after_manual_close": "",
            "residual_long_units_from_approved_buy": "",
            "buy_supply_units_counted_as_new_long": str(lot["new_ats_units"]),
            "status": "Hypothetical modeled ATS position per user direction; no execution is verified; no later EOD mark supplied",
            "notes": "Separate 50U fixed-price long addition after the modeled short closures; do not classify as part of the 35U/34U closure orders.",
        })
        for date, time, event, units, price in lot["manual_adds"]:
            result.append({
                "record_type": "MANUAL LIVE TEST POSITION",
                "scenario": "User-directed manual entry; separate from ATS sensitivity",
                "ticker": ticker,
                "date": date,
                "time_mst": time,
                "event": event,
                "units": str(units),
                "price": f"{price:.3f}" if ticker == "BRENT" else f"{price:.2f}",
                "reference_lot_units": "",
                "ats_allocation_ceiling_units": "",
                "manual_reference_allocation_units": "",
                "ats_long_units_remaining_from_reference_lot": "",
                "manual_long_units_remaining_from_reference_lot": "",
                "ats_short_open_units": "",
                "initial_ats_cover_units": "",
                "ats_short_units_after_initial_cover": "",
                "manual_approved_buy_order_units": "",
                "manual_approved_short_close_units": "",
                "ats_short_units_remaining_after_manual_close": "",
                "residual_long_units_from_approved_buy": "",
                "buy_supply_units_counted_as_new_long": "",
                "status": "User-labeled manual live test input; model entry is not independently verified; post-Oct. 23 cutoff",
                "notes": "Separate manual replenishment lot. User-supplied price/time is retained; no post-entry EOD mark is supplied here.",
            })
    return result


def build_csv(rows: list[dict[str, str]]) -> None:
    CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    with CSV_PATH.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def build_report() -> None:
    lines = [
        "# ATS and Manual Live Position Reconciliation",
        "",
        "> **Status and disclosure:** This is a user-directed hypothetical reconciliation, not a verified brokerage ledger, audited account statement, or investment recommendation. The user reports visual oversight/confirmation of ATS activity, but the exact ATS execution quantity is unknown. The requested category names are preserved while every ATS quantity remains explicitly scenario-based.",
        "",
        "## AUTOMATED TRADING SYSTEM LIVE POSITIONS",
        "",
        "For this reconciliation only, the user selected each tagged Oct. 19 Weekend Oil 50U lot as a sizing proxy for a whole-portfolio 80% ATS / 20% manual framework. That proxy yields a maximum ATS allocation of 40U and a separate 10U manual remainder per ticker. It is **not** evidence that either those exact unit sizes or the broader account allocation were actually held.",
        "",
        "The user-reported Oct. 23 ATS action is modeled as an ATS long exit at **$118.00 BRENT** and **$103.50 OIL**, with an equal-size short opened at the same modeled price. Since the amount is unknown, the ledger shows illustrative ATS executions of 10U, 20U, 30U, and 40U per ticker (25%, 50%, 75%, and 100% of the 40U ATS ceiling). These are sensitivities, not probabilities or a claimed exhaustive bound; actual quantity could be below the shown scenarios, in which case the assumed initial 10U cover would need revision. The manual 10U reference sleeve remains long in each scenario; any unexecuted part of the 40U ATS allocation also remains long.",
        "",
        "The earlier Oct. 23 modeled 10U trims and 10U shorts at $117 BRENT / $102 OIL are superseded—not stacked—in this reconciliation. They remain in the legacy historical core replay for audit continuity, but are not additional ATS or manual events here.",
        "",
        "",
        "## MANUALLY APPROVED SHORT CLOSURE",
        "",
        "The Oct. 25 20:35 MST action is now reconciled closure-first: first apply the modeled 10U cover at $114.627 BRENT / $100.74 OIL, then allocate the 35U BRENT / 34U OIL manually approved orders to any remaining ATS short. Under every shown scenario this closes all remaining ATS shorts. Because the orders are larger than the residual shorts, the excess remains as a separate LONG position; only that excess counts as new long buy supply in this reconciliation. At the maximum 40U ATS scenario, 30U short per ticker remains after the initial 10U cover, so the approved orders close 30U each and leave 5U BRENT / 4U OIL LONG. For smaller ATS scenarios, more of each manual order remains LONG.",
        "",
        "| Ticker | ATS short opened | After initial 10U cover | Manual approved order | Applied to short closure | Short remaining | Excess order left LONG / counted as buy supply |",
        "|---|---:|---:|---:|---:|---:|---:|",
        "| BRENT | 10U | 0U | 35U | 0U | 0U | 35U |",
        "| BRENT | 20U | 10U | 35U | 10U | 0U | 25U |",
        "| BRENT | 30U | 20U | 35U | 20U | 0U | 15U |",
        "| BRENT | 40U | 30U | 35U | 30U | 0U | 5U |",
        "| OIL (USOIL) | 10U | 0U | 34U | 0U | 0U | 34U |",
        "| OIL (USOIL) | 20U | 10U | 34U | 10U | 0U | 24U |",
        "| OIL (USOIL) | 30U | 20U | 34U | 20U | 0U | 14U |",
        "| OIL (USOIL) | 40U | 30U | 34U | 30U | 0U | 4U |",
        "",
        "Thus, the framing matches the position sizes: after the earlier 10U modeled cover, the largest remaining ATS short is 30U per ticker, less than either approved order. The closure applies only up to the open short; the remaining 5U/4U in the maximum scenario are not short closures.",
        "",
        "## Additional modeled ATS fixed-price entries",
        "",
        "Per the user's latest instruction, add a separate **50U LONG ATS entry per ticker** at fixed prices of **$115.00 BRENT** and **$101.00 OIL**, modeled on 2026-10-26. The time was not supplied; these are hypothetical modeled open entries, not verified live fills, and no post-entry EOD mark is available. In the maximum 40U-per-ticker short scenario, these additions raise the tagged-campaign long holdings from 35U BRENT / 34U OIL to **85U BRENT / 84U OIL**.",
        "",
        "| Ticker | Existing lots in maximum ATS scenario | New modeled ATS lot | Updated tagged-campaign total |",
        "|---|---|---|---:|",
        "| BRENT | 10U @ $111.412; 10U @ $115.792; 10U @ $114.800; 5U @ $114.627 | 50U @ $115.00 (2026-10-26; time not supplied) | 85U |",
        "| OIL (USOIL) | 10U @ $99.04; 10U @ $101.74; 10U @ $101.00; 4U @ $100.74 | 50U @ $101.00 (2026-10-26; time not supplied) | 84U |",
        "",
        "These totals are for the tagged campaign and ATS/manual reconciliation only; they exclude other core lots and the daily energy schedule. If the ATS short execution was smaller than the 40U-per-ticker ceiling, additional unsold ATS long units remain, so the total holdings would be larger than 85U/84U.",
        "",
        "## MANUAL LIVE TEST POSITIONS",
        "",
        "The four later 10U replenishment entries remain separate manual long lots and are labeled accordingly in the trade logs. Their sizes are not rescaled or netted against the ATS sensitivity. The 17:22 times are modeled midpoints of the user-recalled 17:20–17:25 window; the 20:00 times are approximate. The user-supplied prices remain model inputs, not verified transaction reports.",
        "",
        "| Date | Time (MST) | Ticker | Manual event | Units | Modeled price |",
        "|---|---|---|---|---:|---:|",
        "| 2026-10-25 | ~17:22 | BRENT | Replenishment | 10U | $115.792 |",
        "| 2026-10-25 | ~20:00 | BRENT | Replenishment | 10U | $114.800 |",
        "| 2026-10-25 | ~17:22 | OIL (USOIL) | Replenishment | 10U | $101.740 |",
        "| 2026-10-25 | ~20:00 | OIL (USOIL) | Replenishment | 10U | $101.000 |",
        "",
        "## Scope boundaries and audit trail",
        "",
        "- This is a separate reconciliation layer. It does not rewrite the Oct. 23 historical core PnL, DXY bridge, or the 32 independent THE ONE model alternatives; those are not a single live account.",
        "- The 50U per-ticker lot is only the sizing proxy selected for this oil reconciliation. Other portfolio holdings are not multiplied by 80%, and the 32-book aggregate must not be used as an actual account denominator.",
        "- The 40U ATS ceiling is not a claim that 40U executed. The exact sale/short quantity, order timing, fills, fees, financing, spread, slippage, and broker position remain unverified.",
        "- The manually approved order sizes are retained as given; modeled closure amounts are capped at the open short. Residual long units are separated from closed-short units.",
        "- The Oct. 25 replenishments are post-Oct. 23 and have no subsequent EOD mark in this ledger. No post-entry PnL is reported.",
        "- Fixed model convention: 1U = $10,000 original notional. Oil unit sizing is not a count of barrels or an account equity percentage.",
        "",
        f"Machine-readable reconciliation: [`{CSV_PATH.name}`](data/{CSV_PATH.name}).",
        "",
    ]
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    rows = records()
    build_csv(rows)
    build_report()
    print(f"Wrote {CSV_PATH.relative_to(ROOT)} ({len(rows)} rows)")
    print(f"Wrote {REPORT_PATH.name}")


if __name__ == "__main__":
    main()
