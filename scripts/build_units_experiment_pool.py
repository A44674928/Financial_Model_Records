"""Build the historical $20B TradingView paper-portfolio allocation.

The user-reported starting pool is not verified capital. Model deductions use
current gross-open notional, not cumulative historical turnover. The winner
comparison is intentionally funded as a separate book alongside THE ONE MODEL
per the user's instruction, although it is selected from THE ONE universe.
"""

from __future__ import annotations

import csv
import json
from decimal import Decimal, ROUND_FLOOR
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ONE_SUMMARY = ROOT / "data/the_one_model_split_portfolios_v1_summary.json"
WINNER_SUMMARY = ROOT / "data/the_one_model_vs_winning_model_v1_summary.json"
STRATEGY_DAILY = ROOT / "data/strategy_sidecar_comparison_daily_v1.csv"
DXY_DAILY = ROOT / "data/dxy_currency_desk_sidecar_daily_20261026.csv"
TRADINGVIEW_MARKS = ROOT / "data/tradingview_benchmark_session_marks_20261026.csv"
OUTPUT_CSV = ROOT / "data/units_experiment_pool_allocation_20261026.csv"
COSTS_CSV = ROOT / "data/units_experiment_model_costs_20261026.csv"
OUTPUT_REPORT = ROOT / "Units Experiment Pool Allocation.md"

STARTING_POOL_USD = Decimal("20000000000.00")
LARGE_UNIT_USD = Decimal("1000000000.00")
SMALL_UNIT_USD = Decimal("10000.00")
ALLOCATION_FRACTION = Decimal("0.5")
# User-reported month/day and entry basis; 2026 is aligned to the active model window.
ENTRY_DATE_TEXT = {"BRENT": "Sep 23", "OIL": "Sep 22"}
ENTRY_DATES = {"BRENT": "2026-09-23", "OIL": "2026-09-22"}
ENTRY_YEAR_NOTE = "2026 model-year alignment; user text supplied month/day but not a year"
BUY_PRICES = {"BRENT": Decimal("102.315"), "OIL": Decimal("89.89")}
LOCK_TARGET_USD = Decimal("200.00")


def dec(value: str | int | float) -> Decimal:
    return Decimal(str(value))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def floor_to_int(value: Decimal) -> int:
    return int(value.to_integral_value(rounding=ROUND_FLOOR))


def current_energy_marks() -> tuple[str, dict[str, Decimal]]:
    """Get latest supplied TradingView EOD closes for the two locked-up legs."""
    rows = read_csv(TRADINGVIEW_MARKS)
    marks: dict[str, tuple[str, Decimal]] = {}
    for row in rows:
        ticker = row["Ticker"]
        if ticker not in ENTRY_DATES or row["Mark_Status"] != "provided_tradingview_close":
            continue
        date = row["Date"]
        if ticker not in marks or date > marks[ticker][0]:
            marks[ticker] = (date, dec(row["Close"]))
    if set(marks) != set(ENTRY_DATES):
        raise ValueError("Latest supplied TradingView closes are required for BRENT and OIL")
    if marks["BRENT"][0] != marks["OIL"][0]:
        raise ValueError("BRENT and OIL lock-status marks must share a session date")
    return marks["BRENT"][0], {ticker: mark[1] for ticker, mark in marks.items()}


def current_costs() -> tuple[dict, dict, list[dict]]:
    one = json.loads(ONE_SUMMARY.read_text(encoding="utf-8"))
    winner = json.loads(WINNER_SUMMARY.read_text(encoding="utf-8"))
    if one["period_end"] != "2026-10-26" or winner["period_end"] != "2026-10-26":
        raise ValueError("Pool budget requires current Oct. 26 model summaries")

    strategy = read_csv(STRATEGY_DAILY)[-1]
    dxy = read_csv(DXY_DAILY)
    dxy_005 = [row for row in dxy if row["unit_size_label"] == "0.05U"][-1]

    # These standalone comparison books are not in THE ONE 32-portfolio
    # aggregate: fixed-$500/EOD, shared-direction 1U/EOD, generic 10U energy,
    # the 0.05U DXY alternative, and the separate one-time chart DXY position.
    chart_dxy_notional = dec(dxy_005["logged_chart_position_units"]) * Decimal("10000")
    costs = [
        {
            "model_book": "THE ONE MODEL — aggregate of 32 independent portfolios",
            "current_open_gross_notional_usd": one["aggregate_gross_open_notional_usd"],
            "historical_cumulative_gross_additions_usd": one["aggregate_cumulative_gross_notional_added_usd"],
            "pool_deduction_usd": one["aggregate_gross_open_notional_usd"],
            "scope_note": "Current gross-open notional across all 32 modeled books; includes core, variant-specific 1U/EOD, 11U energy in 16 portfolios, and 10U DXY in all 32.",
        },
        {
            "model_book": "THE WINNING MODEL — selected portfolio scaled 27.201116x",
            "current_open_gross_notional_usd": winner["winning_model_equal_gross_gross_open_notional_usd"],
            "historical_cumulative_gross_additions_usd": winner["winning_model_equal_gross_cumulative_gross_notional_added_usd"],
            "pool_deduction_usd": winner["winning_model_equal_gross_gross_open_notional_usd"],
            "scope_note": "Separately funded scaled book per user direction; it is selected from THE ONE universe, so this is an additional modeled allocation, not a unique signal set.",
        },
        {
            "model_book": "Fixed-$500/EOD direction-following alternative",
            "current_open_gross_notional_usd": strategy["exponential_open_notional_usd"],
            "historical_cumulative_gross_additions_usd": strategy["exponential_cumulative_notional_added_usd"],
            "pool_deduction_usd": strategy["exponential_open_notional_usd"],
            "scope_note": "Separate fixed-tranche comparison book; not a THE ONE constituent.",
        },
        {
            "model_book": "Shared-direction 1U/EOD force alternative",
            "current_open_gross_notional_usd": strategy["force_multiplier_open_notional_usd"],
            "historical_cumulative_gross_additions_usd": strategy["force_multiplier_cumulative_notional_added_usd"],
            "pool_deduction_usd": strategy["force_multiplier_open_notional_usd"],
            "scope_note": "Separate shared-direction comparison book; THE ONE includes variant-specific 1U/EOD books instead.",
        },
        {
            "model_book": "Generic 10U/DAY TradingView energy sidecar",
            "current_open_gross_notional_usd": strategy["oil_desk_open_notional_usd"],
            "historical_cumulative_gross_additions_usd": strategy["oil_desk_cumulative_notional_usd"],
            "pool_deduction_usd": strategy["oil_desk_open_notional_usd"],
            "scope_note": "Separate 10U/DAY comparison book; THE ONE energy-inclusive portfolios use 11U/DAY.",
        },
        {
            "model_book": "0.05U/DAY DXY alternative",
            "current_open_gross_notional_usd": dxy_005["open_notional_usd"],
            "historical_cumulative_gross_additions_usd": dxy_005["cumulative_notional_added_usd"],
            "pool_deduction_usd": dxy_005["open_notional_usd"],
            "scope_note": "Alternative DXY sizing, excluded from THE ONE; 1U core and 10U sidecar schedules are already included there and are not counted again.",
        },
        {
            "model_book": "One-time chart-opened DXY position",
            "current_open_gross_notional_usd": f"{chart_dxy_notional:.2f}",
            "historical_cumulative_gross_additions_usd": f"{chart_dxy_notional:.2f}",
            "pool_deduction_usd": f"{chart_dxy_notional:.2f}",
            "scope_note": "Separate logged position outside core and THE ONE daily DXY schedules; counted once, not once per sizing row.",
        },
    ]
    return one, winner, costs


def build_rows() -> tuple[dict, dict, list[dict], list[dict]]:
    one, winner, costs = current_costs()
    total_deductions = sum((dec(row["pool_deduction_usd"]) for row in costs), Decimal("0"))
    remaining = STARTING_POOL_USD - total_deductions
    if remaining < 0:
        raise ValueError("Current modeled open notional exceeds the user-stated starting pool")

    mark_date, current_marks = current_energy_marks()
    lock_status = "LOCKED" if not all(mark >= LOCK_TARGET_USD for mark in current_marks.values()) else "LOCK CONDITION MET"
    allocation_rows = []
    for ticker, price in BUY_PRICES.items():
        allocation = remaining * ALLOCATION_FRACTION
        large_units = floor_to_int(allocation / LARGE_UNIT_USD)
        after_large = allocation - Decimal(large_units) * LARGE_UNIT_USD
        small_units = floor_to_int(after_large / SMALL_UNIT_USD)
        large_notional = Decimal(large_units) * LARGE_UNIT_USD
        small_notional = Decimal(small_units) * SMALL_UNIT_USD
        cash_remainder = allocation - large_notional - small_notional
        quantity_equivalent = allocation / price
        current_value = quantity_equivalent * current_marks[ticker]
        mark_change = current_value - allocation
        allocation_rows.append({
            "ticker": ticker,
            "user_reported_entry_date_text": ENTRY_DATE_TEXT[ticker],
            "modeled_entry_date": ENTRY_DATES[ticker],
            "entry_year_assumption": ENTRY_YEAR_NOTE,
            "user_reported_entry_price_usd": str(price),
            "starting_profit_pool_usd": f"{STARTING_POOL_USD:.2f}",
            "total_active_model_deductions_usd": f"{total_deductions:.2f}",
            "allocation_fraction": f"{ALLOCATION_FRACTION:.4f}",
            "allocation_usd": f"{allocation:.2f}",
            "large_unit_value_usd": f"{LARGE_UNIT_USD:.2f}",
            "large_unit_count": str(large_units),
            "large_unit_notional_usd": f"{large_notional:.2f}",
            "small_unit_value_usd": f"{SMALL_UNIT_USD:.2f}",
            "small_unit_count": str(small_units),
            "small_unit_notional_usd": f"{small_notional:.2f}",
            "residual_cash_under_small_unit_usd": f"{cash_remainder:.2f}",
            "modeled_instrument_quantity_equivalent": f"{quantity_equivalent:.8f}",
            "current_tradingview_mark_date": mark_date,
            "current_tradingview_mark_usd": f"{current_marks[ticker]:.2f}",
            "modeled_current_mark_value_usd": f"{current_value:.2f}",
            "modeled_unrealized_mark_change_usd": f"{mark_change:.2f}",
            "modeled_price_return_pct": f"{mark_change / allocation * Decimal('100'):.6f}",
            "lock_target_mark_usd": f"{LOCK_TARGET_USD:.2f}",
            "lock_status_as_of_current_marks": lock_status,
            "execution_status": "user-reported entry basis; allocation math is hypothetical; no order or brokerage execution is represented; actual quantity is unspecified",
        })
    modeled_change_total = sum((dec(row["modeled_unrealized_mark_change_usd"]) for row in allocation_rows), Decimal("0"))
    totals = {
        "starting_pool_usd": f"{STARTING_POOL_USD:.2f}",
        "total_deductions_usd": f"{total_deductions:.2f}",
        "remaining_pool_usd": f"{remaining:.2f}",
        "the_one_open_notional_usd": one["aggregate_gross_open_notional_usd"],
        "winner_open_notional_usd": winner["winning_model_equal_gross_gross_open_notional_usd"],
        "winner_scale_factor": winner["equal_gross_scale_factor"],
        "deduction_method": "Current open gross notional; historical cumulative gross additions shown separately and not deducted.",
        "mark_date": allocation_rows[0]["current_tradingview_mark_date"],
        "locked_status": allocation_rows[0]["lock_status_as_of_current_marks"],
        "modeled_unrealized_mark_change_usd": f"{modeled_change_total:.2f}",
    }
    return totals, winner, costs, allocation_rows


def write_outputs() -> None:
    totals, winner, costs, allocation_rows = build_rows()
    COSTS_CSV.parent.mkdir(parents=True, exist_ok=True)
    with COSTS_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(costs[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(costs)
    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(allocation_rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(allocation_rows)

    start = dec(totals["starting_pool_usd"])
    deductions = dec(totals["total_deductions_usd"])
    remaining = dec(totals["remaining_pool_usd"])
    each = remaining * ALLOCATION_FRACTION
    large_total = sum(int(row["large_unit_count"]) for row in allocation_rows)
    small_total = sum(int(row["small_unit_count"]) for row in allocation_rows)
    cash_left = sum((dec(row["residual_cash_under_small_unit_usd"]) for row in allocation_rows), Decimal("0"))
    model_cost_rows = "\n".join(
        f"| {row['model_book']} | ${dec(row['current_open_gross_notional_usd']):,.2f} | ${dec(row['historical_cumulative_gross_additions_usd']):,.2f} | ${dec(row['pool_deduction_usd']):,.2f} |"
        for row in costs
    )
    report = f"""# $20B Paper Portfolio — Units Experiment

> **User-estimated, hypothetical paper portfolio.** The $20,000,000,000 starting pool is not independently verified profit, cash, or account equity. No live orders or brokerage executions are represented.

## Historical record and two-stage process

The user describes this as a paper portfolio built over approximately the prior **45 days** through TradingView Paper Trading. The current GitHub core replay covers **37 regular-session marks from 2026-09-03 through 2026-10-26**; the user-reported 45-day TradingView history is maintained by manually porting records into this repository. The workflow has two stages: (1) manual paper trading and observation in TradingView; then (2) manual transcription/normalization of the activity into the GitHub trade ledger, price records, and model reports. The GitHub copy is the durable historical record after it is updated; it does not sync automatically and does not establish independently verified fills. TradingView account resets do not erase records already archived here.

## Model-capital deductions

For pool budgeting, “price” means **current open gross notional** as of the latest model snapshot, not cumulative historical turnover. Cumulative additions are displayed for context but are not deducted, because closed lots can recycle modeled capital. THE ONE MODEL and the 27.201116× WINNING MODEL are funded as separate books per the requested construction; the winner is selected from THE ONE MODEL’s 32-portfolio universe, so it repeats that model lineage by design.

| Model book | Current open gross notional | Historical cumulative additions (reference only) | Deducted from pool |
|---|---:|---:|---:|
{model_cost_rows}
| **All selected model books** | — | — | **${deductions:,.2f}** |

Minor books are included only when separately maintained outside THE ONE/WINNING allocations: the fixed-$500/EOD alternative, shared-direction 1U/EOD force alternative, generic 10U energy schedule, 0.05U/DAY DXY alternative, and the separate one-time chart-opened DXY position. The integrated 1U/DAY DXY sleeve, THE ONE 10U/DAY DXY add-on, its variant-specific 1U/EOD components, and its 11U/DAY energy sleeves are already represented in THE ONE and are not charged again. Whole-portfolio DXY/yield views are historical comparison views, and the ATS/manual maximum-size reconciliation is an uncertain separate scenario with potential overlap; neither is charged as an additional active book.

| Pool bridge | Amount |
|---|---:|
| User-estimated starting pool | ${start:,.2f} |
| Less: selected model-book active gross notional | (${deductions:,.2f}) |
| **Remaining pool for the $200 LONG PORTFOLIO** | **${remaining:,.2f}** |
| BRENT allocation — 50%, using its reported entry basis | ${each:,.2f} |
| OIL allocation — 50%, using its reported entry basis | ${each:,.2f} |
| Residual cash below the $10,000 denomination | ${cash_left:,.2f} |

## $200 LONG PORTFOLIO — balanced OIL/BRENT allocation

The $20B pool experiment's residual is split equally by dollar notional. Per your supplied entry data, the modeled BRENT leg uses **Sep. 23 at $102.315** and the OIL/USOIL leg uses **Sep. 22 at $89.89**. The year was not stated in your text; this run maps both dates to **2026** to align with the accompanying September 2026 TradingView/model context. These are user-reported historical entry-basis inputs, not independently verified fills. The Sep. 22 USOIL screenshot supports ticker context; its “Trade active / Target hit” note is not modeled as a fill or close event. The $200 label is the **price lock threshold**, not the funding amount; the experiment continues to use the $20B pool bridge and its hypothetical allocations. Each ticker allocation is converted into $1,000,000,000 Large Units first, then $10,000 Small Units; sub-$10,000 balances remain cash.

| Ticker | User-stated date / entry basis (2026 model alignment*) | Dollar allocation | Large Units | Small Units | Residual cash | Quantity equivalent (not contracts/barrels) | 2026-10-26 TradingView mark | Modeled unrealized mark change* |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| BRENT | Sep. 23 / $102.315 | ${each:,.2f} | {allocation_rows[0]['large_unit_count']} | {int(allocation_rows[0]['small_unit_count']):,} | ${dec(allocation_rows[0]['residual_cash_under_small_unit_usd']):,.2f} | {dec(allocation_rows[0]['modeled_instrument_quantity_equivalent']):,.8f} | ${dec(allocation_rows[0]['current_tradingview_mark_usd']):,.2f} | ${dec(allocation_rows[0]['modeled_unrealized_mark_change_usd']):,.2f} |
| OIL (USOIL) | Sep. 22 / $89.89 | ${each:,.2f} | {allocation_rows[1]['large_unit_count']} | {int(allocation_rows[1]['small_unit_count']):,} | ${dec(allocation_rows[1]['residual_cash_under_small_unit_usd']):,.2f} | {dec(allocation_rows[1]['modeled_instrument_quantity_equivalent']):,.8f} | ${dec(allocation_rows[1]['current_tradingview_mark_usd']):,.2f} | ${dec(allocation_rows[1]['modeled_unrealized_mark_change_usd']):,.2f} |
| **Total** | — | **${remaining:,.2f}** | **{large_total}** | **{small_total:,}** | **${cash_left:,.2f}** | — | — | **${dec(totals['modeled_unrealized_mark_change_usd']):,.2f}** |

**Current lock status:** **{totals['locked_status']}** as of supplied TradingView marks dated **{totals['mark_date']}**. Keep the portfolio locked until **both** supplied BRENT and OIL EOD marks reach **$200.00**; the current marks are BRENT ${dec(allocation_rows[0]['current_tradingview_mark_usd']):,.2f} and OIL ${dec(allocation_rows[1]['current_tradingview_mark_usd']):,.2f}. The *modeled unrealized mark change* is a simple, linear price-equivalent calculation on the hypothetical residual-pool allocations; it is not actual account PnL, a verified fill, liquid/withdrawable cash, or an addition to pool deductions. The quantity equivalents are allocation dollars divided by the reported entry basis; they are **not** contract, barrel, share, or broker-order quantities because contract multipliers, execution quality, fees, financing, and market impact are unspecified.

CSV audits: [model-book deductions](data/{COSTS_CSV.name}) and [balanced allocation](data/{OUTPUT_CSV.name}). The winner scale factor is {winner['equal_gross_scale_factor']}× on cumulative gross additions; the pool deduction uses its scaled current open notional of ${dec(totals['winner_open_notional_usd']):,.2f}.
"""
    OUTPUT_REPORT.write_text(report, encoding="utf-8")
    print(f"Wrote {COSTS_CSV.relative_to(ROOT)}")
    print(f"Wrote {OUTPUT_CSV.relative_to(ROOT)}")
    print(f"Wrote {OUTPUT_REPORT.relative_to(ROOT)}")
    print(f"Model deductions: ${deductions:,.2f}; residual: ${remaining:,.2f}")


if __name__ == "__main__":
    write_outputs()
