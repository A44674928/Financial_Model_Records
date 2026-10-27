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
ATS_OUTPUT_CSV = ROOT / "data" / "ats_oil_cost_basis_adjustment_v1.csv"
REPORT = ROOT / "Oil Cost Basis Savings Model.md"
TICKERS = ("BRENT", "OIL")
ATS_SHORT_SCENARIOS = (10, 20, 30, 40)
ATS_LOTS = {
    "BRENT": {
        "entry": Decimal("111.412"), "short_entry": Decimal("118.00"),
        "cover": Decimal("114.627"), "manual_order_units": 35,
        "new_ats_units": 50, "new_ats_entry": Decimal("115.00"),
        "replenishments": [(10, Decimal("115.792")), (10, Decimal("114.80"))],
        "later_user_entries": [(10, Decimal("115.025")), (16, Decimal("114.90"))],
        "cashout": (50, Decimal("115.51"), Decimal("117.409")),
    },
    "OIL": {
        "entry": Decimal("99.04"), "short_entry": Decimal("103.50"),
        "cover": Decimal("100.74"), "manual_order_units": 34,
        "new_ats_units": 50, "new_ats_entry": Decimal("101.00"),
        "replenishments": [(10, Decimal("101.74")), (10, Decimal("101.00"))],
        "later_user_entries": [(10, Decimal("100.96")), (17, Decimal("100.85"))],
        "cashout": (50, Decimal("101.11"), Decimal("102.71")),
    },
}


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


def build_ats_basis_rows():
    """Build scenario-only cost-basis adjustments for the revised ATS short closure."""
    rows = []
    for ticker, spec in ATS_LOTS.items():
        for short_units in ATS_SHORT_SCENARIOS:
            initial_cover = min(10, short_units)
            short_after_initial = short_units - initial_cover
            manual_cover = min(spec["manual_order_units"], short_after_initial)
            residual_manual_long = spec["manual_order_units"] - manual_cover
            # Open long basket: unexecuted ATS portion, 10U manual remainder,
            # four 10U replenishments, and any excess from the closure order.
            open_lots = (
                [(40 - short_units, spec["entry"]), (10, spec["entry"])]
                + spec["replenishments"]
                + [(residual_manual_long, spec["cover"])]
                + [(spec["new_ats_units"], spec["new_ats_entry"])]
                + spec["later_user_entries"]
            )
            gross_open_notional = sum(
                (Decimal(units) * UNIT_NOTIONAL for units, _ in open_lots), Decimal("0")
            )
            exposure_quantity = sum(
                (Decimal(units) * UNIT_NOTIONAL / price for units, price in open_lots), Decimal("0")
            )
            short_close_pnl = (
                Decimal(short_units) * UNIT_NOTIONAL
                * (Decimal("1") - spec["cover"] / spec["short_entry"])
            )
            cashout_units, cashout_entry, cashout_exit = spec["cashout"]
            cashout_pnl = (
                Decimal(cashout_units) * UNIT_NOTIONAL
                * (cashout_exit / cashout_entry - Decimal("1"))
            )
            total_basis_credit = short_close_pnl + cashout_pnl
            net_basis = gross_open_notional - short_close_pnl
            fully_credited_net_basis = gross_open_notional - total_basis_credit
            unadjusted_effective_basis = gross_open_notional / exposure_quantity
            adjusted_effective_basis = net_basis / exposure_quantity
            fully_credited_effective_basis = fully_credited_net_basis / exposure_quantity
            rows.append({
                "ticker": ticker,
                "scenario": f"{short_units}U short opened per ticker",
                "ats_short_opened_units": str(short_units),
                "initial_cover_units": str(initial_cover),
                "manual_approved_short_close_units": str(manual_cover),
                "total_short_closed_units": str(initial_cover + manual_cover),
                "ats_short_units_remaining": str(short_units - initial_cover - manual_cover),
                "short_entry_price": f"{spec['short_entry']:.3f}" if ticker == "BRENT" else f"{spec['short_entry']:.2f}",
                "short_cover_price": f"{spec['cover']:.3f}" if ticker == "BRENT" else f"{spec['cover']:.2f}",
                "short_close_pnl_credit_usd": f"{_money(short_close_pnl):.2f}",
                "cashout_pnl_basis_credit_usd": f"{_money(cashout_pnl):.2f}",
                "total_basis_credit_usd": f"{_money(total_basis_credit):.2f}",
                "manual_closure_order_units": str(spec["manual_order_units"]),
                "residual_long_units_from_manual_order": str(residual_manual_long),
                "new_ats_long_units": str(spec["new_ats_units"]),
                "new_ats_long_entry_price": f"{spec['new_ats_entry']:.3f}" if ticker == "BRENT" else f"{spec['new_ats_entry']:.2f}",
                "new_ats_long_entry_date": "2026-10-26",
                "new_ats_long_entry_time": "not supplied",
                "later_user_reported_long_units": str(sum(units for units, _ in spec["later_user_entries"])),
                "later_user_reported_long_lots": "; ".join(f"{units}U@{price:f}" for units, price in spec["later_user_entries"]),
                "user_reported_cashout_units": str(spec["cashout"][0]),
                "cashout_lot_entry_price": f"{spec['cashout'][1]:.3f}" if ticker == "BRENT" else f"{spec['cashout'][1]:.2f}",
                "cashout_exit_price": f"{spec['cashout'][2]:.3f}" if ticker == "BRENT" else f"{spec['cashout'][2]:.2f}",
                "cashout_realized_pnl_usd": f"{_money(Decimal(spec['cashout'][0]) * UNIT_NOTIONAL * (spec['cashout'][2] / spec['cashout'][1] - Decimal('1'))):.2f}",
                "unit_weighted_average_entry_price": f"{_price(sum((Decimal(units) * price for units, price in open_lots), Decimal('0')) / sum(units for units, _ in open_lots)):.6f}",
                "open_long_units_in_basis_scope": str(sum(units for units, _ in open_lots)),
                "gross_open_long_notional_usd": f"{_money(gross_open_notional):.2f}",
                "unadjusted_effective_basis_price": f"{_price(unadjusted_effective_basis):.6f}",
                "short_close_credit_adjusted_effective_basis_price": f"{_price(adjusted_effective_basis):.6f}",
                "cashout_credit_adjusted_effective_basis_price": f"{_price(fully_credited_effective_basis):.6f}",
                "basis_reduction_per_exposure_unit": f"{_price(unadjusted_effective_basis - adjusted_effective_basis):.6f}",
                "total_basis_reduction_per_exposure_unit": f"{_price(unadjusted_effective_basis - fully_credited_effective_basis):.6f}",
                "mark_status": f"User-provided EOD marks through {SESSION_DATES[-1]}; ATS size/fills remain unverified",
                "status": "Scenario only; 40U per ticker is the ceiling, actual ATS size/fills unverified",
            })
    return rows


def write_ats_basis_csv(rows):
    ATS_OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with ATS_OUTPUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return ATS_OUTPUT_CSV


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
        cashout_exits = [event for event in ticker_events
                         if event["kind"] == "exit"
                         and "Explicit close of the specified paired 50U LONG lot" in event["note"]]
        replenishments = sorted(
            (event for event in ticker_events
             if event["kind"] == "entry" and "Manual replenishment entry" in event["note"]),
            key=lambda event: (event["date"], event["time"], event["order"]),
        )
        if (len(original) != 1 or len(trims) != 1 or not replenishments
                or len(short_entries) != 1 or len(short_exits) != 1 or len(cashout_exits) != 1):
            raise ValueError(
                f"{ticker} requires one tagged 50U entry/trim, at least one replenishment, "
                f"one tagged SHORT entry/exit, and one paired 50U cash-out; found "
                f"{len(original)}, {len(trims)}, {len(replenishments)}, {len(short_entries)}, "
                f"{len(short_exits)}, {len(cashout_exits)}"
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
        cashout = cashout_exits[0]
        cashout_units = _decimal(cashout["units"])
        cashout_entry_price = ATS_LOTS[ticker]["cashout"][1]
        cashout_exit_price = _decimal(cashout["px"])
        if (cashout_units != Decimal(ATS_LOTS[ticker]["cashout"][0])
                or cashout_exit_price != ATS_LOTS[ticker]["cashout"][2]):
            raise ValueError(f"{ticker} paired cash-out does not match the designated lot/price")
        realized_cashout_pnl = cashout_units * UNIT_NOTIONAL * (
            cashout_exit_price / cashout_entry_price - Decimal("1")
        )
        total_realized_credit = realized_trim_pnl + realized_short_pnl + realized_cashout_pnl

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
            "cashout_date": cashout["date"],
            "cashout_units": cashout_units,
            "cashout_entry_price": cashout_entry_price,
            "cashout_exit_price": cashout_exit_price,
            "realized_cashout_pnl": realized_cashout_pnl,
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
                "cashout_date": position["cashout_date"],
                "cashout_units": f"{position['cashout_units']:g}",
                "cashout_entry_price": f"{position['cashout_entry_price']:f}",
                "cashout_exit_price": f"{position['cashout_exit_price']:f}",
                "realized_cashout_pnl_credited_usd": f"{_money(position['realized_cashout_pnl']):.2f}",
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


def write_report(rows, positions, portfolios, ats_basis_rows):
    count_by_variant = Counter(portfolio["core_variant"] for portfolio in portfolios)
    trim_credit_per_portfolio = sum(
        (position["realized_trim_pnl"] for position in positions.values()), Decimal("0")
    )
    short_credit_per_portfolio = sum(
        (position["realized_short_pnl"] for position in positions.values()), Decimal("0")
    )
    cashout_credit_per_portfolio = sum(
        (position["realized_cashout_pnl"] for position in positions.values()), Decimal("0")
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
            "entries or the realized short-exit and paired cash-out PnL. This cost-basis view applies the realized "
            "short and cash-out PnL as basis credits only; it does not add them to current core PnL."
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
        "At the user's direction, the realized 10U Manual-Automatic target-trim PnL, separate realized 10U SHORT PnL, and paired 50U cash-out PnL are credited against the combined remaining open-long basis for that ticker. The legacy target-trim/short basis table below retains its narrower 60U tagged basket (the original 40U residual plus two manual replenishment lots); the separate cash-out is an additional credit reclassified against that basket. The four replenishments are all recorded on 2026-10-25: the $115.792 BRENT/$101.74 OIL entries use the user-recalled 17:20–17:25 MST window, modeled at a 17:22 midpoint, and the $114.80 BRENT/$101.00 OIL entries use approximately 20:00 MST. These are approximate ordering assumptions, not verified transaction times; the user's supplied replenishment prices are retained. The short exits are modeled at $114.627 BRENT and $100.74 OIL on 2026-10-25 at 20:35 MST, after the four earlier replenishments and simultaneous with separate 35U BRENT and 34U OIL LONG Weekend Oil buys; the lot-specific exits override SAR only for the tagged shorts. Those additional buys count toward weekly buy supply, while closing the 10U shorts does not. After the modeled short closures, the buys raise all-core oil long exposure from 65U BRENT + 66U OIL to 100U each (200U combined); this broader exposure is not the scope of the basis-credit table below. This cost-basis calculation remains scoped to the tagged 40U residual plus the two 10U replenishment lots per ticker (60U); it does not fold the separate 35U/34U post-cutoff buys into that prior basis-credit allocation. The entry/exit records remain intact. The target-trim, short-close, and paired cash-out credits are **reclassifications of PnL already recognized in their respective model events**, not additional gains; they must not increase current core PnL a second time. The short exits and paired 50U cash-out are post-cutoff; their realized PnL is folded into this basis-credit reconciliation but remains realized only once in total PnL.",
        "",
        "Because model `1U` is a fixed $10,000 entry-notional tranche, not a fixed number of barrels, the effective price basis is computed using the model-implied exposure quantity: `Q = Σ(entry notional ÷ entry price)`. The derived unadjusted effective basis is `combined open long notional ÷ Q`; the cost-credited effective basis is `(combined open long notional − total realized PnL credits) ÷ Q`, where total credits include the trim, separately modeled SHORT-exit PnL, and the specified paired-lot cash-out PnL for the ticker. These are blended, PnL-equivalent prices—not logged entry prices or fills. The simple unit-count average for the modeled open lots is $" + f"{positions['BRENT']['unit_weighted_average_price']:,.3f}" + f" for BRENT and ${positions['OIL']['unit_weighted_average_price']:,.3f} for OIL; the ratio-equivalent unadjusted blended bases are {_fmt_price(positions['BRENT']['unadjusted_effective_basis_price'])} and {_fmt_price(positions['OIL']['unadjusted_effective_basis_price'])}, respectively. The distinction occurs because the model's 1U is not a fixed barrel quantity. This report applies only to the tagged long lots' effective basis; the SHORT positions are not included as open long exposure, but their explicitly modeled realized PnL is credited against the corresponding ticker's long basis. At any later supplied mark, the basis view must reconcile to standard realized-plus-unrealized PnL without counting either credit a second time. Target-to-rebuy gaps are shown only as quote differences, not dollar-savings estimates.",
        "",
        "Dollar amounts and prices are rounded independently for display; cent-rounded components may differ by $0.01 from a cent-rounded total. All basis calculations use unrounded event PnL.",
        "",
        "| Core ticker | Original Manual-Automatic entry | 10U target trim | Trim PnL credit | Modeled SHORT exit | SHORT PnL credit | Paired 50U cash-out PnL credit | Total PnL basis credits | Replenishment lots | Open lot combination | Gross open notional | Net cost basis after credits | Derived unadjusted effective basis (not trade price) | Cost-credited basis | Basis reduction per exposure unit | Target-to-rebuy quote gaps |",
        "|---|---:|---|---:|---|---:|---:|---:|---:|---|---|---:|---:|---:|---:|---:|",
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
            f"{_fmt_money(position['realized_short_pnl'])} | {_fmt_money(position['realized_cashout_pnl'])} | "
            f"{_fmt_money(position['total_realized_credit'])} | {replenishment_lots} | "
            f"{position['remaining_original_units']:g}U residual + {position['replenishment_units']:g}U replenishments | "
            f"{_fmt_money(position['gross_open_notional'])} | {_fmt_money(position['adjusted_net_basis'])} | "
            f"{_fmt_price(position['unadjusted_effective_basis_price'])} | "
            f"{_fmt_price(position['adjusted_effective_basis_price'])} | "
            f"{_fmt_price(position['basis_reduction_per_exposure_unit'])} | "
            f"{quote_gaps} |"
        )
    lines.extend([
        "",
        f"Per full two-ticker core book, the target-trim credit is {_fmt_money(trim_credit_per_portfolio)}, the modeled SHORT-exit credit is {_fmt_money(short_credit_per_portfolio)}, and the paired 50U cash-out credit is {_fmt_money(cashout_credit_per_portfolio)}; total basis credits are {_fmt_money(combined_credit_per_portfolio)}. The target-trim, short-exit, and cash-out PnL remain realized exactly once; their basis credits are reclassifications, not additional PnL. The post-cutoff short exits and cash-out do not change Oct. 23 historical terminal totals. The same ticker credits map to each of THE ONE MODEL's 32 independent core-based portfolios; across all 32 the reclassified basis amount is {_fmt_money(aggregate_credit)}, **not additional portfolio PnL**. It applies only to these tagged core long lots, not the original 1U ticker lots or the separate daily energy/1U sidecars.",
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
    max_scenario = [row for row in ats_basis_rows if row["ats_short_opened_units"] == "40"]
    max_by_ticker = {row["ticker"]: row for row in max_scenario}
    ats_short_credit_total = sum(
        (
            Decimal(row["ats_short_opened_units"]) * UNIT_NOTIONAL
            * (Decimal("1") - ATS_LOTS[row["ticker"]]["cover"] / ATS_LOTS[row["ticker"]]["short_entry"])
            for row in max_scenario
        ),
        Decimal("0"),
    )
    ats_cashout_credit_total = sum(
        (
            Decimal(ATS_LOTS[row["ticker"]]["cashout"][0]) * UNIT_NOTIONAL
            * (ATS_LOTS[row["ticker"]]["cashout"][2] / ATS_LOTS[row["ticker"]]["cashout"][1] - Decimal("1"))
            for row in max_scenario
        ),
        Decimal("0"),
    )
    ats_total_basis_credit = ats_short_credit_total + ats_cashout_credit_total
    lines.extend([
        "## ATS full-size short-closure basis adjustment (separate scenario)",
        "",
        "This additional calculation uses the **maximum 80U ATS scenario**: 40U SHORT opened per ticker at $118.00 BRENT / $103.50 OIL and fully closed at $114.627 / $100.74. It applies the model's short PnL formula `units × $10,000 × (1 − cover price ÷ entry price)`. Each close is 10U from the earlier modeled partial cover plus 30U allocated from the 35U/34U MANUALLY APPROVED SHORT CLOSURE order. The short-close PnL and specified paired-lot cash-out PnL are credited against the remaining tagged oil longs as basis reductions; each is a reclassification, not additional realized PnL.",
        "",
        "| Ticker | ATS short closed | Short-close PnL credit | Paired-lot cash-out | Cash-out PnL basis credit | Total basis credit | Remaining long basket | Gross open notional | Unadjusted effective basis | After short-close credit | After short-close + cash-out credits |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for ticker in TICKERS:
        row = max_by_ticker[ticker]
        display = "OIL (USOIL)" if ticker == "OIL" else ticker
        lines.append(
            f"| {display} | {row['total_short_closed_units']}U | ${Decimal(row['short_close_pnl_credit_usd']):,.2f} | "
            f"{row['user_reported_cashout_units']}U sale | ${Decimal(row['cashout_realized_pnl_usd']):,.2f} | "
            f"${Decimal(row['total_basis_credit_usd']):,.2f} | {row['open_long_units_in_basis_scope']}U | "
            f"${Decimal(row['gross_open_long_notional_usd']):,.2f} | ${Decimal(row['unadjusted_effective_basis_price']):,.6f} | "
            f"${Decimal(row['short_close_credit_adjusted_effective_basis_price']):,.6f} | "
            f"${Decimal(row['cashout_credit_adjusted_effective_basis_price']):,.6f} |"
        )
    lines.extend([
        f"| **Combined basis credits** | **80U** | **${_money(ats_short_credit_total):,.2f}** | — | **${_money(ats_cashout_credit_total):,.2f}** | **${_money(ats_total_basis_credit):,.2f}** | — | — | — | — | — |",
        "",
        f"The full-size short-close credit is **${_money(ats_short_credit_total):,.2f}** and the paired cash-out basis credit is **${_money(ats_cashout_credit_total):,.2f}**, for **${_money(ats_total_basis_credit):,.2f} total basis credits** per modeled two-ticker book. The reported paired-lot cash-out separately sells 50U BRENT from $115.51 at $117.409 (realized PnL **${Decimal(max_by_ticker['BRENT']['cashout_realized_pnl_usd']):,.2f}**) and the synchronized 50U OIL ATS mirror from $101.11 at $102.71 (realized PnL **${Decimal(max_by_ticker['OIL']['cashout_realized_pnl_usd']):,.2f}**), totaling **$16,132.24 before costs**. In the maximum 40U-per-ticker ATS scenario, these exits reduce the tagged-campaign open basket from 161U to **111U BRENT / 111U OIL**. The earlier separate 50U OIL ATS LONG @ $101.00 is not part of the cash-out and remains distinct. The screenshot's $117.409 at 08:58:03 UTC−7 is a later intraday observation only—not an execution timestamp or EOD mark. The reported cash-out PnL is included as an additional basis credit on the remaining basket; it is still realized only once and is not added a second time to PnL. The remaining basket includes the residual oil lots, manual reference lot, replenishments, and unsold ATS/user-reported additions. Straight unit-weighted averages of remaining modeled entry prices are **${Decimal(max_by_ticker['BRENT']['unit_weighted_average_entry_price']):,.6f} BRENT / ${Decimal(max_by_ticker['OIL']['unit_weighted_average_entry_price']):,.6f} OIL**; these are not ratio-equivalent effective bases or current market quotes. The actual ATS size and all brokerage executions remain unverified; the reported 13:00 MST cash-out timestamps are chronology placeholders because execution times were not supplied. These credits do **not** include gains on the separate 40U ATS long liquidation." ,
        "",
        f"This is a separate ATS scenario and **replaces**, rather than stacks with, the legacy 10U-short credit in the table above. The historical legacy table is retained for audit continuity; do not add its old $3,263.50 short credit or old 10U trim credit to this scenario basis. The maximum ATS scenario is marked to the user-provided {SESSION_DATES[-1]} EOD closes (BRENT ${PRICES['BRENT'][-1]:.2f}; OIL/USOIL ${PRICES['OIL'][-1]:.2f}); actual ATS size and brokerage fills remain unverified, so these are scenario marks, not actual account PnL. See [`ATS and Manual Live Position Reconciliation.md`](ATS%20and%20Manual%20Live%20Position%20Reconciliation.md).",
        "",
        f"Machine-readable ATS basis sensitivity: [`{ATS_OUTPUT_CSV.name}`](data/{ATS_OUTPUT_CSV.name}). It includes 10U, 20U, 30U, and 40U short-size scenarios; only the maximum 80U total case is summarized above.",
        "",
    ])
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    return REPORT


def main():
    rows, positions, portfolios = build_rows()
    csv_path = write_csv(rows)
    ats_basis_rows = build_ats_basis_rows()
    ats_csv_path = write_ats_basis_csv(ats_basis_rows)
    report_path = write_report(rows, positions, portfolios, ats_basis_rows)
    print(f"Wrote {csv_path.relative_to(ROOT)} ({len(rows)} rows)")
    print(f"Wrote {ats_csv_path.relative_to(ROOT)} ({len(ats_basis_rows)} rows)")
    print(f"Wrote {report_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
