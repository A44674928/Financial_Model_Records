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
        "additional_user_entries": [
            ("2026-10-26", "not supplied; date-level assumption only", "MANUALLY APPROVED ATS ORDER; user-reported LONG entry", 10, 115.025, "Manually approved ATS order; user-reported, not independently verified"),
            ("2026-10-26", "not supplied; date-level assumption only", "User-reported LONG entry; category not specified", 16, 114.90, "User-reported open long; strategy classification and execution not independently verified"),
            ("2026-10-26", "07:51:14 MST (TradingView screenshot)", "MANUAL LIVE TEST POSITION; LONG inferred from handwritten PICK UP OPPORTUNITY annotation", 50, 115.51, "Date inferred as 2026-10-26 from conversation/chart context; TradingView 1-minute Brent Cash screenshot shows $115.510 at 07:51:14 UTC−7 and handwritten PICK UP OPPORTUNITY. A second screenshot shows $117.409 at 08:58:03 UTC−7; it is a later intraday chart observation, not an EOD mark or verified execution. LONG is inferred, not explicitly stated; not a verified brokerage fill."),
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
        "additional_user_entries": [
            ("2026-10-26", "not supplied; date-level assumption only", "MANUALLY APPROVED ATS ORDER; user-reported LONG entry", 10, 100.96, "Manually approved ATS order; user-reported, not independently verified"),
            ("2026-10-26", "not supplied; date-level assumption only", "User-reported LONG entry; category not specified", 17, 100.85, "User-reported open long; strategy classification and execution not independently verified"),
            ("2026-10-26", "07:51 MST (synchronized with BRENT; seconds not supplied)", "AUTOMATED TRADING SYSTEM LIVE POSITIONS; separate 50U USOIL ATS mirror LONG synchronized with the user's BRENT 50U buy", 50, 101.11, "Separate, additional 50U ATS USOIL LONG at $101.11, synchronized with the user's 50U manual BRENT LONG at 07:51 MST. TradingView 1-minute USOIL screenshot shows $101.110000 and handwritten ATS WAIT; chart date is Mon 26 Oct 2026. This is distinct from the previously recorded 50U ATS OIL lot at $101.00. Actual brokerage execution is not independently verified."),
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
            "scenario": "Separate fixed-price Oct. 26 addition; modeled, not verified fill" if ticker == "BRENT" else "Earlier 50U ATS OIL lot at $101.00; separate from the later $101.11 mirror entry",
            "ticker": ticker,
            "date": "2026-10-26",
            "time_mst": "not supplied",
            "event": "ATS LONG entry at fixed user-supplied price; earlier separate $101.00 OIL lot" if ticker == "OIL" else "ATS LONG entry at fixed user-supplied price",
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
            "status": "Hypothetical modeled ATS position per user direction; no execution is verified; no later EOD mark supplied; time unspecified" if ticker == "OIL" else "Hypothetical modeled ATS position per user direction; no execution is verified; no later EOD mark supplied",
            "notes": "Earlier separate 50U ATS OIL LONG @ $101.00, time unspecified. Distinct from the additional user-reported ATS mirror LONG @ $101.11 at 07:51 MST. Brokerage execution is not independently verified." if ticker == "OIL" else "Separate 50U fixed-price long addition after the modeled short closures; do not classify as part of the 35U/34U closure orders.",
        })
        for date, time, event, units, price, notes in lot["additional_user_entries"]:
            is_manual = "MANUAL LIVE TEST POSITION" in event
            is_ats_mirror = "AUTOMATED TRADING SYSTEM LIVE POSITIONS" in event
            result.append({
                "record_type": (
                    "MANUAL LIVE TEST POSITION" if is_manual else
                    "AUTOMATED TRADING SYSTEM LIVE POSITIONS — user-reported mirror" if is_ats_mirror else
                    "User-reported additional LONG position"
                ),
                "scenario": (
                    "Separate user-reported ATS mirror LONG; additional to the earlier 50U OIL @ $101.00 entry"
                    if is_ats_mirror else "Separate user-reported post-cutoff long addition; not verified"
                ),
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
                "buy_supply_units_counted_as_new_long": str(units),
                "status": (
                    "User-reported ATS USOIL mirror LONG at 07:51 MST; separate from the earlier 50U @ $101.00; not a confirmed fill; execution not independently verified"
                    if is_ats_mirror else "User-reported post-cutoff position; category/side/date details disclosed in event and notes; no brokerage execution independently verified"
                ),
                "notes": notes,
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
    cashouts = [
        ("BRENT", "2026-10-26", "13:00 MST (ordering placeholder)", 50, 117.409,
         "50U manual BRENT LONG @ $115.51 entered 07:51 MST; closes this lot only."),
        ("OIL", "2026-10-26", "13:00 MST (ordering placeholder)", 50, 102.71,
         "50U ATS USOIL mirror LONG @ $101.11 entered 07:51 MST; closes this mirror only, not the earlier 50U @ $101.00 lot."),
    ]
    for ticker, date, time, units, price, notes in cashouts:
        result.append({
            "record_type": "User-reported post-cutoff LONG liquidation",
            "scenario": "Specific paired manual BRENT / ATS OIL mirror lots; execution unverified",
            "ticker": ticker,
            "date": date,
            "time_mst": time,
            "event": "User-reported executed cash-out of named LONG lot",
            "units": str(units),
            "price": f"{price:.3f}" if ticker == "BRENT" else f"{price:.2f}",
            "reference_lot_units": "50",
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
            "status": "User-reported executed sale; not independently verified; modeled as closing only the specified tagged lot",
            "notes": notes + " Date inferred as 2026-10-26; execution time not supplied; 13:00 MST is only an ordering placeholder.",
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
        "The ledger retains the earlier **50U LONG ATS lots per ticker** at the previously supplied model prices of **$115.00 BRENT** and **$101.00 OIL**, dated 2026-10-26 with time not supplied. The user has clarified that the synchronized mirror move is a **separate additional 50U ATS USOIL LONG @ $101.11 at 07:51 MST**, synchronized with the 50U manual BRENT buy at $115.51. The mirror description applies to this new $101.11 lot, not the older $101.00 lot. The attached TradingView 1-minute USOIL chart shows $101.110000, the date Mon 26 Oct 2026, and a handwritten “ATS WAIT” annotation. This new $101.11 lot is distinct from—and added on top of—the earlier $101.00 ATS USOIL lot; the screenshot supports quote/time context but not a verified brokerage fill. Additional user-reported post-cutoff LONG entries include 10U per ticker through a MANUALLY APPROVED ATS ORDER at $115.025 BRENT / $100.96 OIL (date assumed 2026-10-26 from context; time not supplied), plus 16U BRENT at $114.90 and 17U OIL at $100.85 (date assumed 2026-10-26; strategy category and time not specified). These are user-reported, not independently verified, and retained separately from the fixed-price ATS entries. A further 50U manual BRENT LONG at $115.51 is included from the TradingView Brent Cash 1-minute screenshot: it shows $115.510 at 07:51:14 UTC−7 on a date inferred as 2026-10-26 from conversation/chart context, with a handwritten “PICK UP OPPORTUNITY” note. LONG is inferred from that annotation and was not explicitly stated in text; this is not a verified brokerage fill. Before the latest reported cash-out, the maximum 40U-per-ticker scenario included **161U BRENT / 161U OIL** in the tagged campaign. The user now reports selling the specifically paired **50U manual BRENT lot @ $115.51** at **$117.409** and the synchronized **50U ATS OIL mirror @ $101.11** at **$102.71**; these sales leave **111U BRENT / 111U OIL** in that maximum-scenario campaign. The older 50U ATS OIL lot @ $101.00 is not closed. Modeled realized PnL is $8,220.07 BRENT + $7,912.17 OIL = **$16,132.24 before costs**. These exits are user-reported but not independently verified; date is inferred as 2026-10-26 and 13:00 MST is an ordering placeholder because execution time was not supplied. No post-entry EOD mark is available.",
        "",
        "| Ticker | Existing lots in maximum ATS scenario | Additional open lots counted | Updated tagged-campaign total |",
        "|---|---|---|---:|",
        "| BRENT | 10U @ $111.412; 10U @ $115.792; 10U @ $114.800; 5U @ $114.627 | 50U @ $115.00 ATS + 10U @ $115.025 ATS order + 16U @ $114.90 (classification unspecified); 50U @ $115.51 manual lot sold at $117.409 | 111U remaining |",
        "| OIL (USOIL) | 10U @ $99.04; 10U @ $101.74; 10U @ $101.00; 4U @ $100.74 | Existing 50U @ $101.00 ATS + 10U @ $100.96 ATS order + 17U @ $100.85 (classification unspecified); 50U @ $101.11 ATS mirror sold at $102.71 | 111U remaining |",
        "",
        "These totals are for the tagged campaign and ATS/manual reconciliation only; they exclude other core lots and the daily energy schedule. If the ATS short execution was smaller than the 40U-per-ticker ceiling, additional unsold ATS long units remain, so even after the paired 50U sales the total holdings would be larger than 111U per ticker. The OIL @ $101.11 mirror entry is additional to the existing 50U @ $101.00 ATS lot. The 10U/10U manually approved ATS order and 16U/17U user-reported additions are dated 2026-10-26 by conversation context because the user did not supply dates or times; their classification is preserved as stated or left unspecified. The screenshot-supported 50U BRENT entry is distinguished as a manual live test position with LONG inferred from the handwritten annotation.",
        "",
        "## MANUAL LIVE TEST POSITIONS",
        "",
        "The four later 10U replenishment entries remain separate manual long lots and are labeled accordingly in the trade logs. The additional 50U BRENT manual position is recorded as a separate MANUAL LIVE TEST POSITION from the screenshot; its LONG direction is inferred from the handwritten annotation. Its date is inferred from conversation/chart context. A second screenshot later shows $117.409 at 08:58:03 UTC−7; that is a later intraday chart observation only, not a verified fill or EOD valuation. The other 16U BRENT / 17U OIL additions remain outside the manual classification because the user did not specify their strategy category. The 17:22 times are modeled midpoints of the user-recalled 17:20–17:25 window; the 20:00 times are approximate. User-supplied prices remain model inputs, not verified transaction reports.",
        "",
        "| Date | Time (MST) | Ticker | Manual event | Units | Modeled price |",
        "|---|---|---|---|---:|---:|",
        "| 2026-10-25 | ~17:22 | BRENT | Replenishment | 10U | $115.792 |",
        "| 2026-10-25 | ~20:00 | BRENT | Replenishment | 10U | $114.800 |",
        "| 2026-10-25 | ~17:22 | OIL (USOIL) | Replenishment | 10U | $101.740 |",
        "| 2026-10-25 | ~20:00 | OIL (USOIL) | Replenishment | 10U | $101.000 |",
        "| 2026-10-26* | 07:51:14 | BRENT | Manual LONG inferred from TradingView annotation; screenshot-supported | 50U | $115.510 |",
        "",
        "* Date inferred from conversation context. Screenshot times are UTC−7 (MST). The 08:58:03 screenshot observation at $117.409 is not used as an EOD mark. The separate 10U BRENT / 10U OIL entries are MANUALLY APPROVED ATS ORDER entries shown in the supplemental records above, not part of this manual-only table.",
        "",
        "## Additional user-reported entries — strategy classification unspecified",
        "",
        "The user reported opening these LONG additions but did not specify whether they were ATS or manual. They are counted in the campaign totals but deliberately left outside both strategy labels. Date is inferred as 2026-10-26 from conversation context; timestamps were not supplied.",
        "",
        "| Date (inferred) | Time | Ticker | User-reported position | Units | Price |",
        "|---|---|---|---|---:|---:|",
        "| 2026-10-26 | not supplied | BRENT | LONG; strategy classification unspecified | 16U | $114.900 |",
        "| 2026-10-26 | not supplied | OIL (USOIL) | LONG; strategy classification unspecified | 17U | $100.850 |",
        "",
        "## Scope boundaries and audit trail",
        "",
        "- This is a separate reconciliation layer. It does not rewrite the Oct. 23 historical core PnL, DXY bridge, or the 32 independent THE ONE model alternatives; those are not a single live account.",
        "- The 50U per-ticker lot is only the sizing proxy selected for this oil reconciliation. Other portfolio holdings are not multiplied by 80%, and the 32-book aggregate must not be used as an actual account denominator.",
        "- The 40U ATS ceiling is not a claim that 40U executed. The exact sale/short quantity, order timing, fills, fees, financing, spread, slippage, and broker position remain unverified.",
        "- The manually approved order sizes are retained as given; modeled closure amounts are capped at the open short. Residual long units are separated from closed-short units.",
        "- The Oct. 25 replenishments and Oct. 26 user-reported additions are post-Oct. 23 and have no subsequent EOD mark in this ledger. No post-entry PnL is reported. Dates/times or categories not supplied by the user remain explicitly marked as assumed or unspecified.",
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
