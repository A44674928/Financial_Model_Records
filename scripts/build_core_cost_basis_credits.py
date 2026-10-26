#!/usr/bin/env python3
"""Apply designated realized close PnL as economic basis credits by core variant.

This is a separate cost-basis reclassification view. It does not change the
historical core PnL series, broker records, or the separate maximum-ATS oil
scenario.
"""
from __future__ import annotations

import csv
import sys
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import model_perf_core as core  # noqa: E402
import build_oil_cost_basis_savings as oil_basis  # noqa: E402

CSV_PATH = ROOT / "data" / "core_cost_basis_closure_credits_v1.csv"
REPORT_PATH = ROOT / "Core Cost Basis After Closure Credits.md"
UNIT_NOTIONAL = Decimal("10000")
MONEY = Decimal("0.01")
PRICE = Decimal("0.000001")
TICKERS = ("BRENT", "OIL", "META", "INTC")
VARIANTS = ("V1", "V2", "V3A", "V3B")

FIELDS = [
    "ticker", "variant", "open_long_units", "gross_open_long_notional_usd",
    "open_exposure_quantity_proxy", "unit_weighted_average_entry_price",
    "unadjusted_effective_basis_price", "closure_credit_usd",
    "adjusted_net_basis_usd", "adjusted_effective_basis_price",
    "basis_reduction_per_exposure_unit", "credit_scope", "as_of_date",
    "mark_status", "execution_status",
]


def _d(value) -> Decimal:
    return Decimal(str(value))


def _money(value: Decimal) -> Decimal:
    return value.quantize(MONEY, rounding=ROUND_HALF_UP)


def _price(value: Decimal) -> Decimal:
    return value.quantize(PRICE, rounding=ROUND_HALF_UP)


def replay_latest(events):
    """Replay dated model actions through the latest logged date, then restore globals."""
    original_dates = core.SESSION_DATES
    original_n = core.N_SESS
    latest_dates = sorted({event["date"] for event in events if event["date"] > original_dates[-1]})
    try:
        core.SESSION_DATES = original_dates + latest_dates
        core.N_SESS = len(core.SESSION_DATES)
        return {variant: core.build_lots(variant, events) for variant in VARIANTS}
    finally:
        core.SESSION_DATES = original_dates
        core.N_SESS = original_n


def _closure_credits(ticker, variant, lots, oil_positions):
    if ticker in ("BRENT", "OIL"):
        # Same tagged-cycle treatment as Oil Cost Basis Savings Model:
        # realized 10U target trim plus the explicit tagged short closure.
        return oil_positions[ticker]["total_realized_credit"], (
            "10U Manual-Automatic target-trim PnL, tagged 10U short-cover PnL, and paired 50U cash-out PnL "
            "reclassified against remaining core oil longs; not the separate ATS/manual scenario"
        )

    relevant = [
        lot for lot in lots
        if lot["sym"] == ticker and lot["side"] == "short"
        and lot.get("close_date") == "2026-10-26"
        and lot.get("close_px") is not None
    ]
    credit = sum(
        (_d(lot["qty"]) * UNIT_NOTIONAL
         * (Decimal("1") - _d(lot["close_px"]) / _d(lot["entry_px"]))
         for lot in relevant),
        Decimal("0"),
    )
    return credit, (
        "realized user-directed 2026-10-26 short covers actually applied in this variant; "
        "earlier SAR covers are excluded"
    )


def build_rows():
    events = core.parse_trades()
    replay = replay_latest(events)
    oil_positions = oil_basis._position_inputs(events)
    rows = []
    latest_date = max(event["date"] for event in events)

    for variant in VARIANTS:
        lots, _realized = replay[variant]
        for ticker in TICKERS:
            open_longs = [
                lot for lot in lots
                if lot["sym"] == ticker and lot["side"] == "long" and lot["open"]
            ]
            units = sum((_d(lot["qty"]) for lot in open_longs), Decimal("0"))
            gross = units * UNIT_NOTIONAL
            exposure_qty = sum(
                (_d(lot["qty"]) * UNIT_NOTIONAL / _d(lot["entry_px"])
                 for lot in open_longs),
                Decimal("0"),
            )
            weighted_entry = (
                sum((_d(lot["qty"]) * _d(lot["entry_px"])
                     for lot in open_longs), Decimal("0")) / units
                if units else Decimal("0")
            )
            raw_effective = gross / exposure_qty if exposure_qty else Decimal("0")
            credit, scope = _closure_credits(ticker, variant, lots, oil_positions)
            net_basis = gross - credit
            adjusted = net_basis / exposure_qty if exposure_qty else Decimal("0")
            rows.append({
                "ticker": ticker,
                "variant": variant,
                "open_long_units": str(units),
                "gross_open_long_notional_usd": f"{_money(gross):.2f}",
                "open_exposure_quantity_proxy": f"{exposure_qty:.12f}",
                "unit_weighted_average_entry_price": f"{_price(weighted_entry):.6f}",
                "unadjusted_effective_basis_price": f"{_price(raw_effective):.6f}",
                "closure_credit_usd": f"{_money(credit):.2f}",
                "adjusted_net_basis_usd": f"{_money(net_basis):.2f}",
                "adjusted_effective_basis_price": f"{_price(adjusted):.6f}",
                "basis_reduction_per_exposure_unit": f"{_price(raw_effective - adjusted):.6f}",
                "credit_scope": scope,
                "as_of_date": latest_date,
                "mark_status": "No post-Oct. 23 EOD mark supplied; this is entry/economic basis, not mark-to-market value",
                "execution_status": "Hypothetical paper-model positions and user-directed close inputs; brokerage executions are not independently verified",
            })
    return rows


def write_outputs(rows):
    CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    with CSV_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    by_key = {(row["ticker"], row["variant"]): row for row in rows}
    lines = [
        "# Core Cost Basis After Closure Credits",
        "",
        "> **Scope and disclosure:** This is an economic cost-basis reclassification of modeled open LONG lots, not a tax-basis statement, brokerage record, verified fill report, or current market valuation. It uses the repository convention of $10,000 fixed notional per unit and the same notional-minus-realized-credit divided by exposure-quantity method used in the oil cost-basis report. No commissions, borrow costs, financing, or slippage are included.",
        "",
        "The core model positions are replayed through the latest logged date, 2026-10-26. Post-Oct. 23 entries and exits have no later supplied EOD mark, so they do not change the historical Oct. 23 performance totals. The paired 50U BRENT manual lot and 50U OIL ATS-mirror lot are closed in each variant, leaving 100U open LONG per ticker. Their user-reported realized cash-out PnL ($8,220.07 BRENT + $7,912.17 OIL) is included as a basis credit against the remaining open-long basket; it is a reclassification, not additional PnL. The $87.55 INTC LONG is included in each model variant; the separate variants are not one combined account.",
        "",
        "## Open-long basis by core variant",
        "",
        "Prices below show both the unit-weighted entry average and the effective basis used for credit allocation. Closure credits are applied only to that ticker's current modeled open LONG basket.",
        "",
        "| Ticker | Open LONG units (each variant) | Unit-weighted entry avg. | Unadjusted effective basis | Closure credit V1 / V2 / V3A / V3B | Adjusted effective basis V1 / V2 / V3A / V3B |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for ticker in TICKERS:
        display = "USOIL" if ticker == "OIL" else ticker
        sample = by_key[(ticker, "V1")]
        credits = " / ".join(f"${float(by_key[(ticker, v)]['closure_credit_usd']):,.2f}" for v in VARIANTS)
        adjusted = " / ".join(f"${float(by_key[(ticker, v)]['adjusted_effective_basis_price']):,.6f}" for v in VARIANTS)
        lines.append(
            f"| {display} | {sample['open_long_units']}U | ${float(sample['unit_weighted_average_entry_price']):,.6f} | "
            f"${float(sample['unadjusted_effective_basis_price']):,.6f} | {credits} | {adjusted} |"
        )

    lines.extend([
        "",
        "### What is credited",
        "",
        "- **BRENT and USOIL:** the 10U Manual-Automatic target-trim PnL, tagged 10U short-cover PnL, and user-reported paired-lot cash-out PnL are credited to each variant's remaining open-long basket, matching the [`Oil Cost Basis Savings Model.md`](Oil%20Cost%20Basis%20Savings%20Model.md) method. This is separate from the uncertain-size maximum-ATS campaign scenario; do not stack that scenario basis with these core rows.",
        "- **INTC:** credits use the user-directed covers at $87.55 applied to the open short lots in each variant (V1's 2U and V3A's 6U). V2 and V3B had no INTC short exposure remaining at the time of those covers, so no new cover credit is assigned there.",
        "- **META:** credits use the explicit $637.20 covers applied in each variant (V1's 1U; V3A's 5U total across the earlier 1U cover and the later 4U close). V2 and V3B had no META short exposure remaining at that time, so no new cover credit is assigned there. This model calculation does not establish the full basis of the user's reported 3U META LONG because the basis of the existing 2U was not supplied.",
        "- Earlier SAR-driven covers for META/INTC are excluded from the new short-cover credit; they are not part of the user-directed close instructions reconciled here. Other realized trades are not added again. The credits reclassify modeled realized PnL and do not create additional portfolio PnL.",
        "- The new credits from user-directed INTC/META covers are post-cutoff model results. They are not included in Oct. 23 terminal PnL and are not evidence of executed fills. The 13:00 MST log times for the new INTC/META actions are chronology placeholders because no times were supplied.",
        "",
        f"Machine-readable per-variant rows: [`{CSV_PATH.name}`](data/{CSV_PATH.name}).",
        "",
    ])
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main():
    rows = build_rows()
    write_outputs(rows)
    print(f"Wrote {CSV_PATH.relative_to(ROOT)} ({len(rows)} rows)")
    print(f"Wrote {REPORT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
