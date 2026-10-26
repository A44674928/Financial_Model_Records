#!/usr/bin/env python3
"""Build a cost-basis-credit view for the tagged Weekend Oil trim/replenishment cycles.

The credit is the realized PnL from the earlier 10U target trim. It is allocated
against the remaining 40U Manual-Automatic lot plus the separate 10U manual
replenishment lot. This is a PnL reclassification, not incremental profit.
"""

import csv
import json
from collections import Counter
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

from model_perf_core import PRICES, SESSION_DATES, parse_trades

ROOT = Path(__file__).resolve().parents[1]
UNIT_NOTIONAL = Decimal("10000")
CENT = Decimal("0.01")
PRICE_QUANTUM = Decimal("0.000001")
PORTFOLIO_SUMMARY = ROOT / "data" / "the_one_model_split_portfolios_v1_summary.json"
OUTPUT_CSV = ROOT / "data" / "oil_cost_basis_savings_v1.csv"
REPORT = ROOT / "Oil Cost Basis Savings Model.md"
TICKERS = ("BRENT", "OIL")


def _decimal(value):
    return Decimal(str(value))


def _money(value):
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


def _price(value):
    return value.quantize(PRICE_QUANTUM, rounding=ROUND_HALF_UP)


def _fmt_money(value):
    return f"${_money(value):,.2f}"


def _fmt_price(value):
    return f"${_price(value):,.6f}"


def _position_inputs(events):
    positions = {}
    mark_cutoff = SESSION_DATES[-1]
    for ticker in TICKERS:
        ticker_events = [event for event in events if event["sym"] == ticker]
        original = [event for event in ticker_events
                    if event["kind"] == "entry" and "Manual-Automatic Entry" in event["note"]]
        trims = [event for event in ticker_events
                 if event["kind"] == "exit" and "Manual-Automatic target trim" in event["note"]]
        replenishments = [event for event in ticker_events
                          if event["kind"] == "entry" and "Manual replenishment entry" in event["note"]]
        if len(original) != 1 or len(trims) != 1 or len(replenishments) != 1:
            raise ValueError(
                f"{ticker} requires exactly one tagged 50U entry, trim, and replenishment; "
                f"found {len(original)}, {len(trims)}, {len(replenishments)}"
            )
        original, trim, replenishment = original[0], trims[0], replenishments[0]
        if not (original["date"] <= trim["date"] < replenishment["date"]):
            raise ValueError(f"Unexpected trade chronology for {ticker}")
        original_units = _decimal(original["units"])
        trim_units = _decimal(trim["units"])
        replenishment_units = _decimal(replenishment["units"])
        if trim_units >= original_units:
            raise ValueError(f"{ticker} target trim must leave an original residual lot")
        remaining_original_units = original_units - trim_units
        original_price = _decimal(original["px"])
        trim_price = _decimal(trim["px"])
        replenishment_price = _decimal(replenishment["px"])
        realized_trim_pnl = trim_units * UNIT_NOTIONAL * (trim_price / original_price - Decimal("1"))

        gross_open_notional = (remaining_original_units + replenishment_units) * UNIT_NOTIONAL
        exposure_quantity_proxy = (
            remaining_original_units * UNIT_NOTIONAL / original_price
            + replenishment_units * UNIT_NOTIONAL / replenishment_price
        )
        adjusted_net_basis = gross_open_notional - realized_trim_pnl
        unadjusted_effective_basis_price = gross_open_notional / exposure_quantity_proxy
        unit_weighted_average_price = (
            remaining_original_units * original_price + replenishment_units * replenishment_price
        ) / (remaining_original_units + replenishment_units)
        adjusted_effective_basis_price = adjusted_net_basis / exposure_quantity_proxy
        post_replenishment_marks = [
            (idx, date) for idx, date in enumerate(SESSION_DATES)
            if date >= replenishment["date"]
        ]
        latest_mark_date = post_replenishment_marks[-1][1] if post_replenishment_marks else ""
        latest_mark = (
            _decimal(PRICES[ticker][post_replenishment_marks[-1][0]])
            if post_replenishment_marks else None
        )
        standard_total_pnl = None
        basis_view_total_pnl = None
        if latest_mark is not None:
            standard_total_pnl = (
                realized_trim_pnl
                + remaining_original_units * UNIT_NOTIONAL * (latest_mark / original_price - Decimal("1"))
                + replenishment_units * UNIT_NOTIONAL * (latest_mark / replenishment_price - Decimal("1"))
            )
            basis_view_total_pnl = exposure_quantity_proxy * (
                latest_mark - adjusted_effective_basis_price
            )
            if abs(standard_total_pnl - basis_view_total_pnl) > Decimal("0.000001"):
                raise AssertionError(f"Cost-basis view does not reconcile to standard lots for {ticker}")
        positions[ticker] = {
            "ticker": ticker,
            "display_ticker": "USOIL (internal ticker OIL)" if ticker == "OIL" else "BRENT",
            "original_entry_date": original["date"],
            "original_entry_price": original_price,
            "original_entry_units": original_units,
            "trim_date": trim["date"],
            "trim_price": trim_price,
            "trim_units": trim_units,
            "realized_trim_pnl": realized_trim_pnl,
            "replenishment_date": replenishment["date"],
            "replenishment_price": replenishment_price,
            "replenishment_units": replenishment_units,
            "remaining_original_units": remaining_original_units,
            "combined_open_units": remaining_original_units + replenishment_units,
            "gross_open_notional": gross_open_notional,
            "adjusted_net_basis": adjusted_net_basis,
            "exposure_quantity_proxy": exposure_quantity_proxy,
            "unadjusted_effective_basis_price": unadjusted_effective_basis_price,
            "unit_weighted_average_price": unit_weighted_average_price,
            "adjusted_effective_basis_price": adjusted_effective_basis_price,
            "basis_reduction_per_exposure_unit": (
                unadjusted_effective_basis_price - adjusted_effective_basis_price
            ),
            "target_to_rebuy_price_gap": trim_price - replenishment_price,
            "mark_cutoff": mark_cutoff,
            "trim_within_mark_window": trim["date"] <= mark_cutoff,
            "replenishment_after_cutoff": replenishment["date"] > mark_cutoff,
            "latest_post_replenishment_mark_date": latest_mark_date,
            "latest_post_replenishment_mark": latest_mark,
            "standard_total_pnl_at_latest_mark": standard_total_pnl,
            "basis_view_total_pnl_at_latest_mark": basis_view_total_pnl,
        }
    return positions


def build_rows():
    events = parse_trades()
    positions = _position_inputs(events)
    summary = json.loads(PORTFOLIO_SUMMARY.read_text(encoding="utf-8"))
    portfolios = summary["individual_portfolios"]
    if len(portfolios) != 32:
        raise ValueError(f"Expected the current 32 THE ONE MODEL portfolios, found {len(portfolios)}")

    rows = []
    for portfolio in portfolios:
        for ticker in TICKERS:
            position = positions[ticker]
            rows.append({
                "portfolio_id": portfolio["portfolio_id"],
                "core_variant": portfolio["core_variant"],
                "one_unit_eod_variant": portfolio["variant_specific_1u_eod_variant"],
                "energy_sidecar_included": "yes" if portfolio["oil_sidecar_included"] else "no",
                "ticker": ticker,
                "original_entry_date": position["original_entry_date"],
                "original_entry_price": f"{position['original_entry_price']:f}",
                "original_entry_units": f"{position['original_entry_units']:g}",
                "trim_date": position["trim_date"],
                "trim_price": f"{position['trim_price']:f}",
                "trim_units": f"{position['trim_units']:g}",
                "realized_trim_pnl_credited_usd": f"{_money(position['realized_trim_pnl']):.2f}",
                "replenishment_date": position["replenishment_date"],
                "replenishment_price": f"{position['replenishment_price']:f}",
                "replenishment_units": f"{position['replenishment_units']:g}",
                "remaining_original_units": f"{position['remaining_original_units']:g}",
                "combined_open_units": f"{position['combined_open_units']:g}",
                "gross_open_notional_usd": f"{_money(position['gross_open_notional']):.2f}",
                "adjusted_net_cost_basis_usd": f"{_money(position['adjusted_net_basis']):.2f}",
                "derived_unadjusted_effective_basis_price_not_trade_price": f"{_price(position['unadjusted_effective_basis_price']):.6f}",
                "adjusted_effective_basis_price": f"{_price(position['adjusted_effective_basis_price']):.6f}",
                "basis_reduction_per_exposure_unit": f"{_price(position['basis_reduction_per_exposure_unit']):.6f}",
                "target_to_rebuy_price_gap_not_a_usd_pnl": f"{_price(position['target_to_rebuy_price_gap']):.6f}",
                "current_model_mark_cutoff": position["mark_cutoff"],
                "trim_within_current_mark_window": "yes" if position["trim_within_mark_window"] else "no",
                "replenishment_after_cutoff": "yes" if position["replenishment_after_cutoff"] else "no",
                "latest_post_replenishment_mark_date": position["latest_post_replenishment_mark_date"],
                "latest_post_replenishment_mark": (
                    f"{position['latest_post_replenishment_mark']:f}"
                    if position["latest_post_replenishment_mark"] is not None else ""
                ),
                "standard_realized_plus_unrealized_pnl_at_latest_mark_usd": (
                    f"{_money(position['standard_total_pnl_at_latest_mark']):.2f}"
                    if position["standard_total_pnl_at_latest_mark"] is not None else ""
                ),
                "cost_basis_view_pnl_at_latest_mark_usd": (
                    f"{_money(position['basis_view_total_pnl_at_latest_mark']):.2f}"
                    if position["basis_view_total_pnl_at_latest_mark"] is not None else ""
                ),
                "basis_credit_is_additional_pnl": "no",
                "core_pnl_change_from_reclassification_usd": "0.00",
            })
    return rows, positions, portfolios


def write_csv(rows):
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return OUTPUT_CSV


def write_report(rows, positions, portfolios):
    count_by_variant = Counter(portfolio["core_variant"] for portfolio in portfolios)
    combined_credit_per_portfolio = sum(
        (position["realized_trim_pnl"] for position in positions.values()), Decimal("0")
    )
    aggregate_credit = combined_credit_per_portfolio * Decimal(len(portfolios))
    mark_cutoff = next(iter(positions.values()))["mark_cutoff"]
    pending_tickers = [
        position["display_ticker"] for position in positions.values()
        if position["replenishment_after_cutoff"]
    ]
    if pending_tickers:
        cutoff_note = (
            f"The current EOD model ends on **{mark_cutoff}**. The replenishment entries for "
            f"{', '.join(pending_tickers)} are after that mark cutoff, and there are no post-entry marks "
            "with which to update the reported portfolio PnL, deployed-notional ratios, or drawdowns. "
            "The new entries are recorded and their effective basis is calculated here; current core and "
            "32-portfolio results remain through the existing cutoff and unchanged."
        )
    else:
        latest_mark_date = max(
            position["latest_post_replenishment_mark_date"] for position in positions.values()
        )
        cutoff_note = (
            f"The current EOD model ends on **{mark_cutoff}** and includes post-replenishment marks through "
            f"**{latest_mark_date}**. At the latest available mark, the ordinary separate-lot realized-plus-"
            "unrealized result and the cost-credited basis view reconcile for each oil ticker; the credit is "
            "a PnL reclassification, not an added profit."
        )
    lines = [
        "# Oil Cost-Basis Savings Model — Realized Trim Credit",
        "",
        "> **Hypothetical paper-model accounting view only.** This report does not represent verified brokerage executions, an account return, or a recommendation. Costs, commissions, financing, spread, and execution effects are not modeled.",
        "",
        "## Method and scope",
        "",
        "At the user's direction, realized PnL from each 10U Manual-Automatic target trim is credited against the combined open exposure for that ticker: the original tagged 40U residual plus its separate 10U manual replenishment entry. The entry/exit records remain intact. The credit is a **reclassification of PnL already recognized**, not an additional gain; the model's total PnL must not increase a second time because of the credit.",
        "",
        "Because model `1U` is a fixed $10,000 entry-notional tranche, not a fixed number of barrels, the effective price basis is computed using the model-implied exposure quantity: `Q = Σ(entry notional ÷ entry price)`. The derived unadjusted effective basis is `combined open notional ÷ Q`; the cost-credited effective basis is `(combined open notional − realized trim PnL) ÷ Q`. These are blended, PnL-equivalent prices—not logged entry prices or fills. For BRENT the actual open lots are 40U at $111.412 and 10U at $115.792; a simple unit-count average would be $" + f"{positions['BRENT']['unit_weighted_average_price']:,.3f}" + f", while the ratio-equivalent blended basis is {_fmt_price(positions['BRENT']['unadjusted_effective_basis_price'])}. The distinction occurs because the model's 1U is not a fixed barrel quantity. At any later supplied mark, the credit reclassifies already-realized trim PnL into a lower effective basis while preserving total realized-plus-unrealized PnL. The target-to-rebuy price gap is shown only as a quote difference, not a dollar-savings estimate.",
        "",
        "| Core ticker | Original Manual-Automatic entry | 10U target trim | Realized PnL credited | 10U replenishment entry | Open lot combination | Gross open notional | Net cost basis after credit | Derived unadjusted effective basis (not trade price) | Cost-credited basis | Basis reduction per exposure unit | Target-to-rebuy quote gap |",
        "|---|---:|---|---:|---:|---|---:|---:|---:|---:|---:|---:|",
    ]
    for ticker in TICKERS:
        position = positions[ticker]
        lines.append(
            f"| {position['display_ticker']} | ${position['original_entry_price']:,.3f} ({position['original_entry_units']:g}U) | "
            f"{position['trim_units']:g}U at ${position['trim_price']:,.3f} on {position['trim_date']} | "
            f"{_fmt_money(position['realized_trim_pnl'])} | "
            f"{position['replenishment_units']:g}U at ${position['replenishment_price']:,.3f} on {position['replenishment_date']} | "
            f"{position['remaining_original_units']:g}U residual + {position['replenishment_units']:g}U new lot | "
            f"{_fmt_money(position['gross_open_notional'])} | {_fmt_money(position['adjusted_net_basis'])} | "
            f"{_fmt_price(position['unadjusted_effective_basis_price'])} | "
            f"{_fmt_price(position['adjusted_effective_basis_price'])} | "
            f"{_fmt_price(position['basis_reduction_per_exposure_unit'])} | "
            f"${position['target_to_rebuy_price_gap']:,.3f} |"
        )
    lines.extend([
        "",
        f"The realized trim credit is {_fmt_money(combined_credit_per_portfolio)} per full two-ticker core book, already included in ordinary realized PnL. The same credit maps to each of THE ONE MODEL's 32 independent core-based portfolios; across all 32 the reclassified amount is {_fmt_money(aggregate_credit)}, **not additional portfolio PnL**. It applies only to these tagged core lots, not the original 1U ticker lots or the separate daily energy/1U sidecars.",
        "",
        "## Portfolio propagation and current cutoff",
        "",
        f"The CSV maps each ticker's basis credit to all {len(portfolios)} THE ONE MODEL portfolio IDs and their core variants. Each core variant appears {count_by_variant['V1']} times; its position basis is the same for this specific oil cycle because the variant differences do not change these logged long entries or tagged trims. The basis credit is applied once per ticker within each independently funded portfolio; it is not multiplied again on top of the core PnL.",
        "",
        cutoff_note + " On a future refresh with subsequent marks, total PnL should be computed as either (a) separate-lot realized plus unrealized PnL, or (b) the equivalent cost-credited basis view—not both added together.",

        "",
        f"Machine-readable portfolio mapping: [`{OUTPUT_CSV.name}`](data/{OUTPUT_CSV.name}) ({len(rows)} ticker/portfolio rows). See [`Model Performance Comparison.md`](Model%20Performance%20Comparison.md) and [`Hypothetical Securities Offering Briefing.md`](Hypothetical%20Securities%20Offering%20Briefing.md) for the current mark window and total-PnL scope.",
        "",
    ])
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    return REPORT


def main():
    rows, positions, portfolios = build_rows()
    csv_path = write_csv(rows)
    report_path = write_report(rows, positions, portfolios)
    print(f"Wrote {csv_path.relative_to(ROOT)} ({len(rows)} rows)")
    print(f"Wrote {report_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
