#!/usr/bin/env python3
"""Model a 1% realized-profit reserve and end-of-month XMR conversion.

Scope follows the current $20B pool bridge's separately funded books: the 32
TOM constituents (counted once each), the separately funded equal-gross winner,
the fixed-$500/EOD and shared-direction 1U/EOD alternatives, plus zero-realized
energy/DXY/chart-DXY books for this window. Alternate sizing views and demo
composites are not additional funded books unless separately authorized.

Unrealized marks are never used. XMR conversion requires a supplied TradingView
Kraken XMR/USD EOM close. Missing EOM marks leave the modeled reserve in USD.
"""
from __future__ import annotations

import csv
import json
from calendar import monthrange
from collections import defaultdict
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
REPORTS = ROOT / "reports"

CORE_DAILY = DATA / "model_performance_daily.csv"
STRATEGY_DAILY = DATA / "strategy_sidecar_comparison_daily_v1.csv"
TOM_SUMMARY = DATA / "the_one_model_split_portfolios_v1_summary.json"
WINNER_SUMMARY = DATA / "the_one_model_vs_winning_model_v1_summary.json"
XMR_EOM_MARKS = DATA / "monero_tradingview_kraken_eom_marks_v1.csv"

DETAIL_OUT = DATA / "monero_realized_pnl_by_book_monthly_v1.csv"
MONTHLY_OUT = DATA / "monero_eom_conversion_monthly_v1.csv"
REPORT_OUT = REPORTS / "Monero Realized-Profit EOM Conversion Overlay — 2026-10-26.md"
PAYOUT_RATE = Decimal("0.01")
MAX_SOURCE_EOM_GAP_DAYS = 3
CENT = Decimal("0.01")
EIGHT_PLACES = Decimal("0.00000001")

ZERO_REALIZED_BOOKS = {
    "GENERIC_10U_ENERGY_DAILY": ("energy_sidecar", "Daily-buy positions remain unrealized in the supplied window; no realized close source is present."),
    "DXY_0.05U_DAILY": ("dxy_sidecar", "Standalone daily DXY position has no realized close in the supplied window."),
    "CHART_DXY_OPEN_POSITION": ("dxy_position", "One-time chart DXY position remains open in the supplied record."),
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def money(value: Decimal) -> Decimal:
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


def fmt(value: Decimal) -> str:
    return f"{money(value):.2f}"


def cumulative_deltas(rows: list[dict[str, str]], date_field: str, value_field: str) -> dict[str, Decimal]:
    """Turn a cumulative realized-PnL path into dated, realized-only changes."""
    previous = Decimal("0")
    result: dict[str, Decimal] = {}
    for row in rows:
        current = Decimal(row[value_field])
        result[row[date_field]] = current - previous
        previous = current
    return result


def load_inputs():
    core_rows = read_csv(CORE_DAILY)
    strategy_rows = read_csv(STRATEGY_DAILY)
    if not strategy_rows:
        raise ValueError("No strategy-sidecar daily rows")
    dates = [row["date"] for row in strategy_rows]
    core_by_variant: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in core_rows:
        core_by_variant[row["variant"]].append(row)
    if set(core_by_variant) != {"V1", "V2", "V3A", "V3B"}:
        raise ValueError("Expected the four core variants for the realized-PnL overlay")
    core_delta = {}
    for variant, rows in core_by_variant.items():
        if [row["session_date"] for row in rows] != dates:
            raise ValueError(f"Core/strategy calendar mismatch for {variant}")
        core_delta[variant] = cumulative_deltas(rows, "session_date", "realized_cum_usd")

    force_delta: dict[str, dict[str, Decimal]] = {}
    for variant in ("V1", "V2", "V3A", "V3B"):
        force_delta[variant] = cumulative_deltas(
            strategy_rows, "date", f"{variant}_force_1u_realized_pnl_usd"
        )
    fixed_500_delta = cumulative_deltas(strategy_rows, "date", "exponential_realized_pnl_usd")
    shared_force_delta = cumulative_deltas(strategy_rows, "date", "force_multiplier_realized_pnl_usd")

    tom = json.loads(TOM_SUMMARY.read_text(encoding="utf-8"))
    winner = json.loads(WINNER_SUMMARY.read_text(encoding="utf-8"))
    if tom["period_end"] != dates[-1] or winner["period_end"] != dates[-1]:
        raise ValueError("The TOM/winner snapshots must align to the realized-PnL source endpoint")
    members = tom["individual_portfolios"]
    if len(members) != 32:
        raise ValueError(f"Expected 32 TOM constituent books, found {len(members)}")
    winner_id = winner["winning_portfolio_id"]
    winner_member = next((item for item in members if item["portfolio_id"] == winner_id), None)
    if winner_member is None:
        raise ValueError("Winning portfolio is not a TOM constituent")
    winner_scale = Decimal(winner["equal_gross_scale_factor_exact"])

    return dates, strategy_rows, core_delta, force_delta, fixed_500_delta, shared_force_delta, members, winner, winner_member, winner_scale


def build_monthly_book_rows() -> tuple[list[str], list[dict[str, str]]]:
    (
        dates, _strategy_rows, core_delta, force_delta, fixed_500_delta,
        shared_force_delta, members, winner, winner_member, winner_scale,
    ) = load_inputs()
    per_book_daily: dict[str, dict[str, Decimal]] = {}
    per_book_type: dict[str, tuple[str, str]] = {}

    # TOM contains 32 independently funded books. Each member's realized path is
    # the sum of its core model and its variant-specific 1U/EOD force book;
    # daily DXY/energy purchases remain open and contribute no realized PnL.
    for member in members:
        book_id = f"TOM::{member['portfolio_id']}"
        core_variant = member["core_variant"]
        force_variant = member["variant_specific_1u_eod_variant"]
        per_book_daily[book_id] = {
            day: core_delta[core_variant][day] + force_delta[force_variant][day]
            for day in dates
        }
        per_book_type[book_id] = (
            "tom_constituent",
            f"{core_variant} core + {force_variant} variant-specific 1U/EOD; sidecars excluded until realized",
        )

    # The winning constituent is a separately funded book in the current pool
    # bridge, so its equal-gross realized PnL is an additional distinct ledger.
    winner_id = f"WINNER_EQUAL_GROSS::{winner['winning_portfolio_id']}"
    core_variant = winner_member["core_variant"]
    force_variant = winner_member["variant_specific_1u_eod_variant"]
    per_book_daily[winner_id] = {
        day: (core_delta[core_variant][day] + force_delta[force_variant][day]) * winner_scale
        for day in dates
    }
    per_book_type[winner_id] = (
        "separately_funded_scaled_winner",
        f"Selected TOM member scaled by {winner_scale}×; same-window winner selection is ex post",
    )

    per_book_daily["FIXED_500_EOD"] = fixed_500_delta
    per_book_type["FIXED_500_EOD"] = ("strategy_alternative", "Standalone fixed-$500/EOD model realized closes")
    per_book_daily["SHARED_FORCE_1U_EOD"] = shared_force_delta
    per_book_type["SHARED_FORCE_1U_EOD"] = ("strategy_alternative", "Standalone shared-direction 1U/EOD model realized closes")
    for book_id, metadata in ZERO_REALIZED_BOOKS.items():
        per_book_daily[book_id] = {day: Decimal("0") for day in dates}
        per_book_type[book_id] = metadata

    monthly_sums: dict[tuple[str, str], Decimal] = defaultdict(Decimal)
    for book_id, daily in per_book_daily.items():
        for day in dates:
            monthly_sums[(day[:7], book_id)] += daily[day]

    rows = []
    months = sorted({day[:7] for day in dates})
    for month in months:
        month_dates = [day for day in dates if day[:7] == month]
        for book_id in per_book_daily:
            category, scope = per_book_type[book_id]
            rows.append({
                "month": month,
                "book_id": book_id,
                "book_type": category,
                "realized_pnl_usd": fmt(monthly_sums[(month, book_id)]),
                "source_window_start_date": month_dates[0],
                "source_window_end_date": month_dates[-1],
                "source_scope": scope,
            })
    return dates, rows


def load_eom_marks() -> dict[str, dict[str, str]]:
    if not XMR_EOM_MARKS.exists():
        XMR_EOM_MARKS.parent.mkdir(parents=True, exist_ok=True)
        with XMR_EOM_MARKS.open("w", encoding="utf-8", newline="") as handle:
            csv.writer(handle, lineterminator="\n").writerow([
                "mark_date", "symbol", "exchange", "close_usd", "mark_status", "source_file", "source_file_url"
            ])
    marks = {}
    for row in read_csv(XMR_EOM_MARKS):
        if row["symbol"].upper().replace("/", "") != "XMRUSD":
            raise ValueError(f"Unexpected conversion symbol: {row['symbol']}")
        if row["exchange"].upper() != "KRAKEN":
            raise ValueError("Monero conversion marks must use the TradingView Kraken XMR/USD close")
        if row["mark_status"] != "provided_tradingview_eom_close":
            raise ValueError("Only explicitly supplied TradingView EOM closes can trigger conversion")
        try:
            parsed_date = date.fromisoformat(row["mark_date"])
        except ValueError as error:
            raise ValueError(f"Invalid EOM mark date: {row['mark_date']}") from error
        price = Decimal(row["close_usd"])
        if price <= 0:
            raise ValueError("XMR/USD close must be positive")
        month = parsed_date.strftime("%Y-%m")
        if parsed_date.day != monthrange(parsed_date.year, parsed_date.month)[1]:
            raise ValueError(f"EOM mark date must be the final calendar day of its month: {row['mark_date']}")
        if month in marks:
            raise ValueError(f"Duplicate EOM XMR mark for {month}")
        marks[month] = row
    return marks


def build_outputs() -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    dates, book_rows = build_monthly_book_rows()
    marks = load_eom_marks()
    books_by_month: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in book_rows:
        books_by_month[row["month"]].append(row)

    monthly_rows = []
    pending_usd = Decimal("0")
    for month in sorted(books_by_month):
        month_book_rows = books_by_month[month]
        net_realized = sum((Decimal(row["realized_pnl_usd"]) for row in month_book_rows), Decimal("0"))
        month_start = min(row["source_window_start_date"] for row in month_book_rows)
        month_end = max(row["source_window_end_date"] for row in month_book_rows)
        eligible = max(net_realized, Decimal("0"))
        reserve = money(eligible * PAYOUT_RATE)
        mark = marks.get(month)
        if mark:
            mark_date_value = date.fromisoformat(mark["mark_date"])
            source_month_end = date.fromisoformat(month_end)
            if source_month_end > mark_date_value or (mark_date_value - source_month_end).days > MAX_SOURCE_EOM_GAP_DAYS:
                raise ValueError(
                    f"Cannot convert {month}: model realized-PnL history ends {source_month_end}, "
                    f"too far from the supplied EOM mark {mark_date_value}"
                )
            eom_price = Decimal(mark["close_usd"])
            convert_usd = pending_usd + reserve
            xmr_equivalent = (convert_usd / eom_price).quantize(EIGHT_PLACES, rounding=ROUND_HALF_UP)
            pending_usd = Decimal("0")
            conversion_status = "modeled conversion at supplied TradingView Kraken EOM close; not a verified purchase"
            mark_date = mark["mark_date"]
            mark_source = mark["source_file"]
        else:
            eom_price = None
            convert_usd = Decimal("0")
            xmr_equivalent = Decimal("0")
            pending_usd += reserve
            conversion_status = "USD reserve carried; no supplied TradingView Kraken EOM close"
            mark_date = ""
            mark_source = ""

        if month == dates[0][:7]:
            coverage = f"partial history from {dates[0]}"
        elif month == dates[-1][:7] and not mark:
            coverage = f"month-to-date through {dates[-1]} (no EOM source mark)"
        else:
            coverage = "model-source month; inspect source-window dates for coverage"
        monthly_rows.append({
            "month": month,
            "source_window_start_date": month_start,
            "source_window_end_date": month_end,
            "coverage_note": coverage,
            "aggregate_net_realized_pnl_usd": fmt(net_realized),
            "positive_net_realized_profit_base_usd": fmt(eligible),
            "monero_allocation_rate": f"{PAYOUT_RATE:.4f}",
            "usd_reserve_generated_this_month": fmt(reserve),
            "eom_mark_date": mark_date,
            "xmr_usd_eom_close": f"{eom_price:.8f}" if eom_price is not None else "",
            "usd_converted_this_eom": fmt(convert_usd),
            "modeled_xmr_equivalent": f"{xmr_equivalent:.8f}",
            "pending_usd_reserve_after_eom": fmt(pending_usd),
            "net_realized_pnl_after_reserve_usd": fmt(net_realized - reserve),
            "conversion_status": conversion_status,
            "mark_source_file": mark_source,
        })

    return book_rows, monthly_rows


def write_outputs() -> None:
    book_rows, monthly_rows = build_outputs()
    DETAIL_OUT.parent.mkdir(parents=True, exist_ok=True)
    with DETAIL_OUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(book_rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(book_rows)
    with MONTHLY_OUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(monthly_rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(monthly_rows)
    write_report(book_rows, monthly_rows)
    print(f"Wrote {len(book_rows)} monthly book rows to {DETAIL_OUT.relative_to(ROOT)}")
    print(f"Wrote {len(monthly_rows)} conversion months to {MONTHLY_OUT.relative_to(ROOT)}")
    print(f"Pending USD reserve: ${Decimal(monthly_rows[-1]['pending_usd_reserve_after_eom']):,.2f}")


def write_report(book_rows: list[dict[str, str]], monthly_rows: list[dict[str, str]]) -> None:
    REPORT_OUT.parent.mkdir(parents=True, exist_ok=True)
    table = "\n".join(
        f"| {row['month']} | {row['coverage_note']} | ${Decimal(row['aggregate_net_realized_pnl_usd']):,.2f} | "
        f"${Decimal(row['usd_reserve_generated_this_month']):,.2f} | "
        f"${Decimal(row['net_realized_pnl_after_reserve_usd']):,.2f} | {row['eom_mark_date'] or 'missing'} | "
        f"{row['xmr_usd_eom_close'] or 'pending'} | {row['modeled_xmr_equivalent'] if row['eom_mark_date'] else '—'} | "
        f"${Decimal(row['pending_usd_reserve_after_eom']):,.2f} |"
        for row in monthly_rows
    )
    pending = Decimal(monthly_rows[-1]["pending_usd_reserve_after_eom"])
    converted_months = [row for row in monthly_rows if Decimal(row["usd_converted_this_eom"]) > 0]
    if converted_months:
        conversion_summary = "; ".join(
            f"{row['month']}: ${Decimal(row['usd_converted_this_eom']):,.2f} at "
            f"${Decimal(row['xmr_usd_eom_close']):,.2f}/XMR = {row['modeled_xmr_equivalent']} XMR-equivalent"
            for row in converted_months
        )
        conversion_summary = f"Modeled EOM conversion equivalent(s): {conversion_summary} (not a verified crypto purchase)."
    else:
        conversion_summary = "No supplied EOM mark triggered a modeled XMR-equivalent conversion."
    missing_mark_months = [row["month"] for row in monthly_rows if not row["eom_mark_date"]]
    if missing_mark_months:
        missing_mark_summary = f"No qualifying EOM close is supplied for {', '.join(missing_mark_months)}; reserve remains in USD."
    else:
        missing_mark_summary = "A qualifying EOM close is supplied for each modeled month."
    tom_members = len({row["book_id"] for row in book_rows if row["book_type"] == "tom_constituent"})
    report = f'''# Monero Realized-Profit EOM Conversion Overlay — 2026-10-26

## Rule requested

This model records the user-stated assumption that **1% of aggregate net realized profit across the included books** is reserved for a USD-to-Monero conversion at the end of each month. This is a modeled allocation rule, not an independently confirmed payment, payer, brokerage cash flow, or Monero receipt.

1. Sum **realized PnL only** across all included, separately identified books for each calendar month. Realized losses in one included book offset realized gains in other included books for that same month, as directed. Positions and capital are not netted; only the monthly payout base is aggregated.
2. If monthly aggregate realized PnL is positive, set the eligible base to that positive net amount and reserve **1%**. If monthly net realized PnL is zero or negative, reserve **$0**. No unrealized PnL or mark-to-market gain enters the base.
3. At EOM, convert the pending USD reserve (including any reserve carried from an earlier missing-mark month) using the **supplied TradingView Kraken XMR/USD EOD close** dated on that month's final calendar day. The model also requires the realized-PnL source window to extend to within {MAX_SOURCE_EOM_GAP_DAYS} calendar days of that mark; stale partial-month history cannot trigger conversion. It reports XMR quantity equivalent, not a purchase or receipt.
4. If that EOM mark is missing, leave the reserve in USD and carry it forward. No screenshot price, outside price, interpolation, or legacy mark is substituted. The model currently assumes no cross-month loss carryforward; each month is netted independently.
5. Record the 1% reserve separately from gross additions and funded capital. Only the residual realized net profit after reserve remains available for modeled reinvestment, subject to the existing explicit cash-flow rules.

The source strategy/model PnL series remain **gross of this overlay**. The conversion reserve is a separate monthly cash-flow deduction from available realized profit; it does not alter position PnL, additions, open notional, or unrealized marks. The machine-readable monthly file exposes both gross monthly realized PnL and the after-reserve amount.

## Included book scope

The first implementation follows the independent books explicitly listed in the current $20B pool bridge:

- Each of the **{tom_members} TOM member books**, with its own core and variant-specific 1U/EOD realized trade events. Their monthly totals are added once as the 32-book portfolio set; the TOM aggregate is not added a second time.
- The separately funded, equal-gross scaled WINNING MODEL as one additional book (the selected winner is ex post from the same period; this is still subject to same-period selection bias).
- The separate fixed-$500/EOD and shared-direction 1U/EOD force alternatives.
- Generic energy, 0.05U/DAY DXY, and one-time chart-opened DXY books. They contribute zero realized PnL in this supplied window because no realized close is present for those positions; their unrealized mark PnL is excluded.

The individual core series and variant-force paths are source components within TOM books, not extra funded books in this pool scope. TWM_1M sizing views, randomly composed demo mixes, and other comparison-only charts are not added as separate simultaneous books unless their separate funding is explicitly specified. This prevents alternative sizing views of the same model history from being counted as extra profits by default. The locked BRENT/OIL foundation contributes no realized profit until a qualifying close is explicitly modeled; its current mark does not count.

## Current historical illustration

The underlying model window is **{monthly_rows[0]['source_window_start_date']}–{monthly_rows[-1]['source_window_end_date']}**. September starts on Sep. 3, so its record is a partial-month history; October is month-to-date through Oct. 26. {conversion_summary} {missing_mark_summary} The current pending USD reserve is **${pending:,.2f}**. These are modeled amounts, not a cash withdrawal or proof of received income. The 2026-09-30 close of **$544.86** was supplied by the user in chat as the TradingView Kraken XMR/USD EOD mark; no chart capture/export was attached for independent validation.

| Month | Model coverage | Aggregate net realized PnL | 1% reserve generated | Net realized PnL after reserve | Supplied EOM mark date | XMR/USD EOM close | XMR equivalent | Pending USD reserve |
|---|---|---:|---:|---:|---|---:|---:|---:|
{table}

September's reserve is based only on the Sep. 3–30 available source window. October's figure is provisional month-to-date; it is not a completed October EOM payout. The month-end reserve is not converted using the supplied screenshots because they show intraday 15-minute chart contexts around Sep. 20–22, not EOM closes.

## Screenshot/source archive

The three user-supplied TradingView posts are preserved in [`Archive/Monero_EOM_conversion/`](../Archive/Monero_EOM_conversion/README.md). They identify Monero / U.S. Dollar on **Kraken, 15-minute** charts, with displayed intraday quotes around $542.83–$569.45. They are context only and are **not** used as month-end valuation marks.

## Machine-readable files and rebuild

- [`data/monero_realized_pnl_by_book_monthly_v1.csv`](../data/monero_realized_pnl_by_book_monthly_v1.csv) — monthly realized PnL by independently counted book.
- [`data/monero_eom_conversion_monthly_v1.csv`](../data/monero_eom_conversion_monthly_v1.csv) — aggregate net, 1% reserve, EOM mark, modeled XMR equivalent, and pending USD balance.
- [`data/monero_tradingview_kraken_eom_marks_v1.csv`](../data/monero_tradingview_kraken_eom_marks_v1.csv) — input records user-supplied TradingView Kraken XMR/USD month-end EOD marks; September's close was entered from the user's chat statement.
- Builder: [`scripts/build_monero_eom_conversion_overlay.py`](../scripts/build_monero_eom_conversion_overlay.py). Rebuild with `python scripts/build_monero_eom_conversion_overlay.py`.

> The source models are hypothetical paper replays, not verified brokerage books. The 1% reserve and XMR equivalent are consequently modeled amounts—not confirmed income, tax treatment, external payment, or crypto transaction.
'''
    REPORT_OUT.write_text(report, encoding="utf-8")


if __name__ == "__main__":
    write_outputs()
