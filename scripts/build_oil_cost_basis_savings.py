#!/usr/bin/env python3
"""Build a cost-basis-credit view for the tagged Weekend Oil cycles.

The basis credit includes the realized 10U target-trim PnL and the separately
realized target-level SHORT-exit PnL for each ticker. Credits are allocated
against the remaining 40U Manual-Automatic lot plus separate manual
replenishment lots. This is a PnL reclassification, not incremental profit.
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


def _replenishment_time_label(event):
    if "17:20–17:25" in event["note"]:
        return "17:20–17:25 MST (modeled at 17:22 midpoint)"
    if "approximate time per user" in event["note"]:
        return f"~{event['time']} MST"
    return f"{event['time']} MST"


def _position_inputs(events):
    positions = {}
    mark_cutoff = SESSION_DATES[-1]
    for ticker in TICKERS:
        ticker_events = [event for event in events if event["sym"] == ticker]
        original = [event for event in ticker_events
                    if event["kind"] == "entry" and "Manual-Automatic Entry" in event["note"]]
        trims = [event for event in ticker_events
                 if event["kind"] == "exit" and "Manual-Automatic target trim" in event["note"]]
        short_entries = [event for event in ticker_events
                         if event["kind"] == "entry" and event["tag"] == "SHORT"
                         and "user-directed hypothetical force-multiplier short" in event["note"]]
        short_exits = [event for event in ticker_events
                       if event["kind"] == "exit"
                       and "Explicit close of the tagged 2026-10-23 10U" in event["note"]]
        replenishments = sorted(
            (event for event in ticker_events
             if event["kind"] == "entry" and "Manual replenishment entry" in event["note"]),
            key=lambda event: (event["date"], event["time"], event["order"]),
        )
        if (len(original) != 1 or len(trims) != 1 or not replenishments
                or len(short_entries) != 1 or len(short_exits) != 1):
            raise ValueError(
                f"{ticker} requires one tagged 50U entry/trim, at least one replenishment, "
                f"and one tagged SHORT entry/exit; found {len(original)}, {len(trims)}, "
                f"{len(replenishments)}, {len(short_entries)}, {len(short_exits)}"
            )
        original, trim = original[0], trims[0]
        short_entry, short_exit = short_entries[0], short_exits[0]
        event_key = lambda event: (event["date"], event["time"], event["order"])
        if not (event_key(original) < event_key(trim) < event_key(short_entry)
                < event_key(replenishments[0]) <= event_key(replenishments[-1])
                < event_key(short_exit)):
            raise ValueError(f"Unexpected long/short trade chronology for {ticker}")
        if _decimal(short_entry["units"]) != _decimal(short_exit["units"]):
            raise ValueError(f"{ticker} tagged SHORT entry and exit units do not match")
        original_units = _decimal(original["units"])
        trim_units = _decimal(trim["units"])
        replenishment_units_by_entry = [_decimal(event["units"]) for event in replenishments]
        replenishment_prices = [_decimal(event["px"]) for event in replenishments]
        if trim_units >= original_units:
            raise ValueError(f"{ticker} target trim must leave an original residual lot")
        remaining_original_units = original_units - trim_units
        replenishment_units = sum(replenishment_units_by_entry, Decimal("0"))
        combined_open_units = remaining_original_units + replenishment_units
        original_price = _decimal(original["px"])
        trim_price = _decimal(trim["px"])
        realized_trim_pnl = trim_units * UNIT_NOTIONAL * (trim_price / original_price - Decimal("1"))
        short_units = _decimal(short_entry["units"])
        short_entry_price = _decimal(short_entry["px"])
        short_exit_price = _decimal(short_exit["px"])
        realized_short_pnl = short_units * UNIT_NOTIONAL * (Decimal("1") - short_exit_price / short_entry_price)
        total_realized_credit = realized_trim_pnl + realized_short_pnl

        gross_open_notional = combined_open_units * UNIT_NOTIONAL
        exposure_quantity_proxy = remaining_original_units * UNIT_NOTIONAL / original_price
        for units, price in zip(replenishment_units_by_entry, replenishment_prices):
            exposure_quantity_proxy += units * UNIT_NOTIONAL / price
        adjusted_net_basis = gross_open_notional - total_realized_credit
        unadjusted_effective_basis_price = gross_open_notional / exposure_quantity_proxy
        unit_weighted_average_price = (
            remaining_original_units * original_price
            + sum((units * price for units, price in zip(replenishment_units_by_entry, replenishment_prices)), Decimal("0"))
        ) / combined_open_units
        adjusted_effective_basis_price = adjusted_net_basis / exposure_quantity_proxy
        last_replenishment_date = replenishments[-1]["date"]
        post_replenishment_marks = [
            (idx, date) for idx, date in enumerate(SESSION_DATES)
            if date >= last_replenishment_date
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
                total_realized_credit
                + remaining_original_units * UNIT_NOTIONAL * (latest_mark / original_price - Decimal("1"))
            )
            for units, price in zip(replenishment_units_by_entry, replenishment_prices):
                standard_total_pnl += units * UNIT_NOTIONAL * (latest_mark / price - Decimal("1"))
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
            "short_entry_date": short_entry["date"],
            "short_entry_price": short_entry_price,
            "short_entry_units": short_units,
            "short_exit_date": short_exit["date"],
            "short_exit_time": short_exit["time"],
            "short_exit_price": short_exit_price,
            "realized_short_pnl": realized_short_pnl,
            "total_realized_credit": total_realized_credit,
            "replenishments": replenishments,
            "replenishment_units_by_entry": replenishment_units_by_entry,
            "replenishment_prices": replenishment_prices,
            "replenishment_units": replenishment_units,
            "remaining_original_units": remaining_original_units,
            "combined_open_units": combined_open_units,
            "gross_open_notional": gross_open_notional,
            "adjusted_net_basis": adjusted_net_basis,
            "exposure_quantity_proxy": exposure_quantity_proxy,
            "unadjusted_effective_basis_price": unadjusted_effective_basis_price,
            "unit_weighted_average_price": unit_weighted_average_price,
            "adjusted_effective_basis_price": adjusted_effective_basis_price,
            "basis_reduction_per_exposure_unit": (
                unadjusted_effective_basis_price - adjusted_effective_basis_price
            ),
            "target_to_rebuy_price_gaps": [trim_price - price for price in replenishment_prices],
            "mark_cutoff": mark_cutoff,
            "trim_within_mark_window": trim["date"] <= mark_cutoff,
            "replenishment_after_cutoff": any(event["date"] > mark_cutoff for event in replenishments),
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
                "short_entry_date": position["short_entry_date"],
                "short_entry_price": f"{position['short_entry_price']:f}",
                "short_entry_units": f"{position['short_entry_units']:g}",
                "short_exit_date": position["short_exit_date"],
                "short_exit_time_mst": position["short_exit_time"],
                "short_exit_price": f"{position['short_exit_price']:f}",
                "realized_short_pnl_credited_usd": f"{_money(position['realized_short_pnl']):.2f}",
                "total_realized_pnl_credited_usd": f"{_money(position['total_realized_credit']):.2f}",
                "replenishment_entry_count": str(len(position["replenishments"])),
                "replenishment_dates": ";".join(event["date"] for event in position["replenishments"]),
                "replenishment_times_mst": ";".join(
                    _replenishment_time_label(event) for event in position["replenishments"]
                ),
                "replenishment_prices": ";".join(f"{price:f}" for price in position["replenishment_prices"]),
                "replenishment_units_by_entry": ";".join(f"{units:g}" for units in position["replenishment_units_by_entry"]),
                "replenishment_units_total": f"{position['replenishment_units']:g}",
                "remaining_original_units": f"{position['remaining_original_units']:g}",
                "combined_open_units": f"{position['combined_open_units']:g}",
                "gross_open_notional_usd": f"{_money(position['gross_open_notional']):.2f}",
                "adjusted_net_cost_basis_usd": f"{_money(position['adjusted_net_basis']):.2f}",
                "derived_unadjusted_effective_basis_price_not_trade_price": f"{_price(position['unadjusted_effective_basis_price']):.6f}",
                "adjusted_effective_basis_price": f"{_price(position['adjusted_effective_basis_price']):.6f}",
                "basis_reduction_per_exposure_unit": f"{_price(position['basis_reduction_per_exposure_unit']):.6f}",
                "target_to_rebuy_price_gaps_not_usd_pnl": ";".join(
                    f"{_price(gap):.6f}" for gap in position["target_to_rebuy_price_gaps"]
                ),
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
    trim_credit_per_portfolio = sum(
        (position["realized_trim_pnl"] for position in positions.values()), Decimal("0")
    )
    short_credit_per_portfolio = sum(
        (position["realized_short_pnl"] for position in positions.values()), Decimal("0")
    )
    combined_credit_per_portfolio = sum(
        (position["total_realized_credit"] for position in positions.values()), Decimal("0")
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
            "The replenishments are recorded, and their effective basis is calculated here; they remain "
            "outside the cutoff. The two modeled short exits at $114.627 BRENT and $100.74 OIL on "
            "2026-10-25 at 20:35 MST are also post-cutoff. Core and 32-portfolio results through the cutoff "
            "include the open shorts' Oct. 23 mark-to-market, but do not include these later replenishment "
            "entries or the realized short-exit PnL. This cost-basis view applies the realized short PnL as a "
            "basis credit only; it does not add it to current core PnL."
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
        "# Oil Cost-Basis Savings Model — Realized PnL Credits",
        "",
        "> **Hypothetical paper-model accounting view only.** This report does not represent verified brokerage executions, an account return, or a recommendation. Costs, commissions, financing, spread, and execution effects are not modeled.",
        "",
        "## Method and scope",
        "",
        "At the user's direction, both the realized 10U Manual-Automatic target-trim PnL and the separate realized 10U SHORT PnL are credited against the combined open long exposure for that ticker: the original tagged 40U residual plus each separate manual replenishment lot. The four replenishments are all recorded on 2026-10-25: the $115.792 BRENT/$101.74 OIL entries use the user-recalled 17:20–17:25 MST window, modeled at a 17:22 midpoint, and the $114.80 BRENT/$101.00 OIL entries use approximately 20:00 MST. These are approximate ordering assumptions, not verified transaction times; the user's supplied replenishment prices are retained. The short exits are modeled at $114.627 BRENT and $100.74 OIL on 2026-10-25 at 20:35 MST, after the four earlier replenishments and simultaneous with separate 35U BRENT and 34U OIL LONG Weekend Oil buys; the lot-specific exits override SAR only for the tagged shorts. Those additional buys count toward weekly buy supply, while closing the 10U shorts does not. After the modeled short closures, the buys raise all-core oil long exposure from 65U BRENT + 66U OIL to 100U each (200U combined); this broader exposure is not the scope of the basis-credit table below. This cost-basis calculation remains scoped to the tagged 40U residual plus the two 10U replenishment lots per ticker (60U); it does not fold the separate 35U/34U post-cutoff buys into that prior basis-credit allocation. The entry/exit records remain intact. Both credits are **reclassifications of PnL already recognized in their respective model events**, not additional gains; the credit must not increase current core PnL a second time. The short exits and their PnL are post-cutoff and are shown here only as basis-credit inputs.",
        "",
        "Because model `1U` is a fixed $10,000 entry-notional tranche, not a fixed number of barrels, the effective price basis is computed using the model-implied exposure quantity: `Q = Σ(entry notional ÷ entry price)`. The derived unadjusted effective basis is `combined open long notional ÷ Q`; the cost-credited effective basis is `(combined open long notional − total realized PnL credits) ÷ Q`, where total credits include the trim and separately modeled SHORT-exit PnL for the ticker. These are blended, PnL-equivalent prices—not logged entry prices or fills. The simple unit-count average for the modeled open lots is $" + f"{positions['BRENT']['unit_weighted_average_price']:,.3f}" + f" for BRENT and ${positions['OIL']['unit_weighted_average_price']:,.3f} for OIL; the ratio-equivalent unadjusted blended bases are {_fmt_price(positions['BRENT']['unadjusted_effective_basis_price'])} and {_fmt_price(positions['OIL']['unadjusted_effective_basis_price'])}, respectively. The distinction occurs because the model's 1U is not a fixed barrel quantity. This report applies only to the tagged long lots' effective basis; the SHORT positions are not included as open long exposure, but their explicitly modeled realized PnL is credited against the corresponding ticker's long basis. At any later supplied mark, the basis view must reconcile to standard realized-plus-unrealized PnL without counting either credit a second time. Target-to-rebuy gaps are shown only as quote differences, not dollar-savings estimates.",
        "",
        "Dollar amounts and prices are rounded independently for display; cent-rounded components may differ by $0.01 from a cent-rounded total. All basis calculations use unrounded event PnL.",
        "",
        "| Core ticker | Original Manual-Automatic entry | 10U target trim | Trim PnL credit | Modeled SHORT exit | SHORT PnL credit | Total PnL credits | Replenishment lots | Open lot combination | Gross open notional | Net cost basis after credits | Derived unadjusted effective basis (not trade price) | Cost-credited basis | Basis reduction per exposure unit | Target-to-rebuy quote gaps |",
        "|---|---:|---|---:|---|---:|---:|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for ticker in TICKERS:
        position = positions[ticker]
        replenishment_lots = "; ".join(
            f"{_decimal(event['units']):g}U at ${_decimal(event['px']):,.3f} on {event['date']} "
            f"{_replenishment_time_label(event)}"
            for event in position["replenishments"]
        )
        quote_gaps = "; ".join(f"${gap:,.3f}" for gap in position["target_to_rebuy_price_gaps"])
        lines.append(
            f"| {position['display_ticker']} | ${position['original_entry_price']:,.3f} ({position['original_entry_units']:g}U) | "
            f"{position['trim_units']:g}U at ${position['trim_price']:,.3f} on {position['trim_date']} | "
            f"{_fmt_money(position['realized_trim_pnl'])} | "
            f"{position['short_entry_units']:g}U SHORT at ${position['short_entry_price']:,.3f} → "
            f"${position['short_exit_price']:,.3f} on {position['short_exit_date']} {position['short_exit_time']} MST | "
            f"{_fmt_money(position['realized_short_pnl'])} | {_fmt_money(position['total_realized_credit'])} | "
            f"{replenishment_lots} | "
            f"{position['remaining_original_units']:g}U residual + {position['replenishment_units']:g}U replenishments | "
            f"{_fmt_money(position['gross_open_notional'])} | {_fmt_money(position['adjusted_net_basis'])} | "
            f"{_fmt_price(position['unadjusted_effective_basis_price'])} | "
            f"{_fmt_price(position['adjusted_effective_basis_price'])} | "
            f"{_fmt_price(position['basis_reduction_per_exposure_unit'])} | "
            f"{quote_gaps} |"
        )
    lines.extend([
        "",
        f"Per full two-ticker core book, the target-trim credit is {_fmt_money(trim_credit_per_portfolio)}, the modeled SHORT-exit credit (combined short PnL before costs) is {_fmt_money(short_credit_per_portfolio)}, and total basis credits are {_fmt_money(combined_credit_per_portfolio)}. The target-trim PnL is already present in current realized results; the SHORT-exit PnL is post-cutoff and is excluded from current terminal PnL. On a later replay, both are realized once and then reclassified into the basis view—not added again as profit. The same ticker credits map to each of THE ONE MODEL's 32 independent core-based portfolios; across all 32 the reclassified basis amount is {_fmt_money(aggregate_credit)}, **not additional portfolio PnL**. It applies only to these tagged core long lots, not the original 1U ticker lots or the separate daily energy/1U sidecars.",
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
