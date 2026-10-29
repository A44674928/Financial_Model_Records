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
FOUNDATION_LOTS_CSV = ROOT / "data/units_experiment_oil_foundation_lots_20261027.csv"
OUTPUT_REPORT = ROOT / "Units Experiment Pool Allocation.md"

STARTING_POOL_USD = Decimal("20000000000.00")
SUPPLEMENTAL_ORDER_USD = Decimal("20000000000.00")
SUPPLEMENTAL_ORDER_PRICES = {"BRENT": Decimal("115.00"), "OIL": Decimal("101.00")}
SUPPLEMENTAL_ORDER_DATE = "not supplied"
LARGE_UNIT_USD = Decimal("1000000000.00")
SMALL_UNIT_USD = Decimal("10000.00")
TRANSFERRED_UNITS_PER_TICKER = Decimal("50")
TRANSFERRED_NOTIONAL_PER_TICKER = TRANSFERRED_UNITS_PER_TICKER * SMALL_UNIT_USD
ALLOCATION_FRACTION = Decimal("0.5")
# User-reported month/day and entry basis; 2026 is aligned to the active model window.
ENTRY_DATE_TEXT = {"BRENT": "Sep 23", "OIL": "Sep 22"}
ENTRY_DATES = {"BRENT": "2026-09-23", "OIL": "2026-09-22"}
ENTRY_YEAR_NOTE = "2026 model-year alignment; user text supplied month/day but not a year"
BUY_PRICES = {"BRENT": Decimal("102.315"), "OIL": Decimal("89.89")}
LOCK_TARGET_USD = Decimal("200.00")
# User-reported sale-price extrema for the later ATS liquidation; not TradingView EOD marks.
REPORTED_EXIT_PRICE_RANGES = {
    "BRENT": (Decimal("114.670"), Decimal("117.345")),
    "OIL": (Decimal("101.500"), Decimal("103.400")),
}


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


def build_foundation_lots(allocation_rows: list[dict]) -> list[dict]:
    """Return earlier, retained, transferred, and combined oil-foundation rows."""
    rows = []
    order_leg_gross = SUPPLEMENTAL_ORDER_USD * ALLOCATION_FRACTION
    transferred_notional = TRANSFERRED_NOTIONAL_PER_TICKER
    retained_order_leg = order_leg_gross - transferred_notional
    for base in allocation_rows:
        ticker = base["ticker"]
        mark = dec(base["current_tradingview_mark_usd"])
        mark_date = base["current_tradingview_mark_date"]
        earlier_notional = dec(base["allocation_usd"])
        earlier_price = BUY_PRICES[ticker]
        earlier_quantity = earlier_notional / earlier_price
        order_price = SUPPLEMENTAL_ORDER_PRICES[ticker]
        retained_quantity = retained_order_leg / order_price
        transferred_quantity = transferred_notional / order_price
        combined_notional = earlier_notional + retained_order_leg
        combined_quantity = earlier_quantity + retained_quantity
        blended_basis = combined_notional / combined_quantity

        lot_definitions = [
            (
                "EARLIER_20B_POOL_ALLOCATION",
                "Earlier residual-pool foundation lot",
                ENTRY_DATE_TEXT[ticker],
                "LOCKED_OIL_FOUNDATION",
                earlier_price,
                earlier_notional,
                earlier_quantity,
                "Earlier user-reported entry-basis allocation; full-pool sizing is hypothetical; no order/fill is verified.",
            ),
            (
                "SUPPLEMENTAL_ORDER_FOUNDATION_REMAINDER",
                "Retained supplemental $20B-order foundation leg after 50U transfer",
                SUPPLEMENTAL_ORDER_DATE,
                "LOCKED_OIL_FOUNDATION",
                order_price,
                retained_order_leg,
                retained_quantity,
                "Remainder of the user-directed hypothetical order; no large-order date/time or brokerage execution is supplied or represented.",
            ),
            (
                "TRANSFERRED_50U_TO_WINNING_MODEL",
                "Existing 50U lot reallocated from oil foundation to THE WINNING MODEL",
                "2026-10-26; time unspecified per source ATS record",
                "THE_WINNING_MODEL",
                order_price,
                transferred_notional,
                transferred_quantity,
                "User-directed allocation reclassification of the existing 50U source lot; preserve ATS provenance; not a new fill or duplicate position.",
            ),
            (
                "COMBINED_LOCKED_FOUNDATION",
                "Combined earlier pool lot + retained supplemental foundation leg",
                "combined lots; see component rows",
                "LOCKED_OIL_FOUNDATION",
                blended_basis,
                combined_notional,
                combined_quantity,
                "Arithmetic aggregation only; preserves component entry prices in the rows above; excludes the 50U lot reassigned to THE WINNING MODEL.",
            ),
        ]
        source_provenance = {
            "EARLIER_20B_POOL_ALLOCATION": "User-reported earlier pool-allocation entry basis; modeled quantity is hypothetical.",
            "SUPPLEMENTAL_ORDER_FOUNDATION_REMAINDER": "User-directed hypothetical supplemental order; date/time unspecified; no order or fill is verified.",
            "TRANSFERRED_50U_TO_WINNING_MODEL": "ATS source; existing user-reported 50U LONG lot dated 2026-10-26; time unspecified.",
            "COMBINED_LOCKED_FOUNDATION": "Derived arithmetic summary; see component source rows; not an additional position.",
        }
        for lot_id, description, entry_date, destination, entry_price, notional, quantity, status in lot_definitions:
            current_value = quantity * mark
            rows.append({
                "source_provenance": source_provenance[lot_id],
                "lot_id": lot_id,
                "ticker": ticker,
                "allocation_destination": destination,
                "lot_description": description,
                "entry_date_or_timing": entry_date,
                "entry_or_blended_basis_usd": f"{entry_price:.8f}",
                "funded_notional_usd": f"{notional:.2f}",
                "quantity_equivalent_not_shares_or_contracts": f"{quantity:.8f}",
                "current_tradingview_mark_date": mark_date,
                "current_tradingview_mark_usd": f"{mark:.2f}",
                "modeled_current_mark_value_usd": f"{current_value:.2f}",
                "modeled_unrealized_mark_change_usd": f"{current_value - notional:.2f}",
                "execution_status": status,
            })
    return rows


def modeled_exit_price_envelope(foundation_lot_rows: list[dict]) -> dict[str, dict[str, Decimal]]:
    """Calculate endpoint scenarios using model bases and user-reported sale prices."""
    component_ids = {"EARLIER_20B_POOL_ALLOCATION", "SUPPLEMENTAL_ORDER_FOUNDATION_REMAINDER"}
    components = [
        row for row in foundation_lot_rows
        if row["lot_id"] in component_ids and row["allocation_destination"] == "LOCKED_OIL_FOUNDATION"
    ]
    result: dict[str, dict[str, Decimal]] = {}
    for ticker, (low_price, high_price) in REPORTED_EXIT_PRICE_RANGES.items():
        ticker_rows = [row for row in components if row["ticker"] == ticker]
        if not ticker_rows:
            raise ValueError(f"Missing modeled locked-foundation lots for {ticker}")
        low_pnl = sum(
            dec(row["funded_notional_usd"])
            * (low_price / dec(row["entry_or_blended_basis_usd"]) - Decimal("1"))
            for row in ticker_rows
        )
        high_pnl = sum(
            dec(row["funded_notional_usd"])
            * (high_price / dec(row["entry_or_blended_basis_usd"]) - Decimal("1"))
            for row in ticker_rows
        )
        result[ticker] = {
            "low_price": low_price, "high_price": high_price,
            "low_pnl": low_pnl, "high_pnl": high_pnl,
        }
    result["COMBINED"] = {
        "low_pnl": result["BRENT"]["low_pnl"] + result["OIL"]["low_pnl"],
        "high_pnl": result["BRENT"]["high_pnl"] + result["OIL"]["high_pnl"],
    }
    return result


def write_outputs() -> None:
    totals, winner, costs, allocation_rows = build_rows()
    foundation_lot_rows = build_foundation_lots(allocation_rows)
    exit_envelope = modeled_exit_price_envelope(foundation_lot_rows)
    COSTS_CSV.parent.mkdir(parents=True, exist_ok=True)
    with COSTS_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(costs[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(costs)
    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(allocation_rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(allocation_rows)
    with FOUNDATION_LOTS_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(foundation_lot_rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(foundation_lot_rows)

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
    supplemental_rows = [row for row in foundation_lot_rows if row["lot_id"] == "SUPPLEMENTAL_ORDER_FOUNDATION_REMAINDER"]
    transfer_rows = [row for row in foundation_lot_rows if row["lot_id"] == "TRANSFERRED_50U_TO_WINNING_MODEL"]
    combined_rows = [row for row in foundation_lot_rows if row["lot_id"] == "COMBINED_LOCKED_FOUNDATION"]
    supplemental_table = "\n".join(
        f"| {row['ticker']} | ${dec(row['funded_notional_usd']) + TRANSFERRED_NOTIONAL_PER_TICKER:,.2f} | "
        f"${dec(next(t['funded_notional_usd'] for t in transfer_rows if t['ticker'] == row['ticker'])):,.2f} | "
        f"${dec(row['funded_notional_usd']):,.2f} | ${dec(row['entry_or_blended_basis_usd']):,.2f} | "
        f"{dec(row['quantity_equivalent_not_shares_or_contracts']):,.8f} | "
        f"{dec(next(t['quantity_equivalent_not_shares_or_contracts'] for t in transfer_rows if t['ticker'] == row['ticker'])):,.8f} | "
        f"${dec(row['current_tradingview_mark_usd']):,.2f} | ${dec(row['modeled_unrealized_mark_change_usd']):,.2f} | "
        f"${dec(next(t['modeled_unrealized_mark_change_usd'] for t in transfer_rows if t['ticker'] == row['ticker'])):,.2f} |"
        for row in supplemental_rows
    )
    combined_table_rows = []
    for combined in combined_rows:
        ticker = combined["ticker"]
        earlier = next(row for row in foundation_lot_rows if row["ticker"] == ticker and row["lot_id"] == "EARLIER_20B_POOL_ALLOCATION")
        added = next(row for row in supplemental_rows if row["ticker"] == ticker)
        combined_table_rows.append(
            f"| {ticker} | ${dec(earlier['funded_notional_usd']):,.2f} @ ${dec(earlier['entry_or_blended_basis_usd']):,.3f} | "
            f"${dec(added['funded_notional_usd']):,.2f} @ ${dec(added['entry_or_blended_basis_usd']):,.2f} | "
            f"${dec(combined['funded_notional_usd']):,.2f} | {dec(combined['quantity_equivalent_not_shares_or_contracts']):,.8f} | "
            f"${dec(combined['entry_or_blended_basis_usd']):,.8f} | ${dec(combined['current_tradingview_mark_usd']):,.2f} | "
            f"${dec(combined['modeled_current_mark_value_usd']):,.2f} | ${dec(combined['modeled_unrealized_mark_change_usd']):,.2f} |"
        )
    combined_table = "\n".join(combined_table_rows)
    combined_foundation_notional = sum((dec(row["funded_notional_usd"]) for row in combined_rows), Decimal("0"))
    combined_foundation_pnl = sum((dec(row["modeled_unrealized_mark_change_usd"]) for row in combined_rows), Decimal("0"))
    supplemental_mark_pnl = sum((dec(row["modeled_unrealized_mark_change_usd"]) for row in supplemental_rows), Decimal("0"))
    supplemental_foundation_notional = sum((dec(row["funded_notional_usd"]) for row in supplemental_rows), Decimal("0"))
    transfer_notional = sum((dec(row["funded_notional_usd"]) for row in transfer_rows), Decimal("0"))
    transfer_mark_pnl = sum((dec(row["modeled_unrealized_mark_change_usd"]) for row in transfer_rows), Decimal("0"))
    winner_base_open = dec(winner["winning_model_equal_gross_gross_open_notional_usd"])
    winner_scenario_open = winner_base_open + transfer_notional
    report = f"""# $20B Paper Portfolio — Units Experiment

> **Historical allocation model and later user-reported exit.** The user clarifies that the underlying money was verified in an account and reports that the ATS liquidated positions automatically; this repository has not independently reviewed account evidence or execution statements. The $20B pool bridge and quantity equivalents below remain model-derived allocations, not a broker ledger.

## Historical record and two-stage process

The user describes this as a TradingView paper-portfolio/modeling record built over approximately the prior **45 days**. The user now clarifies the underlying funds were verified account money, while this repository has not independently reviewed source statements. The current GitHub core replay covers **37 regular-session marks from 2026-09-03 through 2026-10-26**; the user-reported 45-day TradingView history is maintained by manually porting records into this repository. The workflow has two stages: (1) manual paper trading and observation in TradingView; then (2) manual transcription/normalization of the activity into the GitHub trade ledger, price records, and model reports. The GitHub copy is the durable historical record after it is updated; it does not sync automatically and does not establish independently verified fills. TradingView account resets do not erase records already archived here.

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

## Original $20B pool-funded $200 LONG allocation — earlier lots

The $20B pool experiment's residual is split equally by dollar notional. Per your supplied entry data, the modeled BRENT leg uses **Sep. 23 at $102.315** and the OIL/USOIL leg uses **Sep. 22 at $89.89**. The year was not stated in your text; this run maps both dates to **2026** to align with the accompanying September 2026 TradingView/model context. These are user-reported historical entry-basis inputs, not independently verified fills. The Sep. 22 USOIL screenshot supports ticker context; its “Trade active / Target hit” note is not modeled as a fill or close event. The $200 label is the **price lock threshold**, not the funding amount; the experiment continues to use the $20B pool bridge and its hypothetical allocations. Each ticker allocation is converted into $1,000,000,000 Large Units first, then $10,000 Small Units; sub-$10,000 balances remain cash.

| Ticker | User-stated date / entry basis (2026 model alignment*) | Dollar allocation | Large Units | Small Units | Residual cash | Quantity equivalent (not contracts/barrels) | 2026-10-26 TradingView mark | Modeled unrealized mark change* |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| BRENT | Sep. 23 / $102.315 | ${each:,.2f} | {allocation_rows[0]['large_unit_count']} | {int(allocation_rows[0]['small_unit_count']):,} | ${dec(allocation_rows[0]['residual_cash_under_small_unit_usd']):,.2f} | {dec(allocation_rows[0]['modeled_instrument_quantity_equivalent']):,.8f} | ${dec(allocation_rows[0]['current_tradingview_mark_usd']):,.2f} | ${dec(allocation_rows[0]['modeled_unrealized_mark_change_usd']):,.2f} |
| OIL (USOIL) | Sep. 22 / $89.89 | ${each:,.2f} | {allocation_rows[1]['large_unit_count']} | {int(allocation_rows[1]['small_unit_count']):,} | ${dec(allocation_rows[1]['residual_cash_under_small_unit_usd']):,.2f} | {dec(allocation_rows[1]['modeled_instrument_quantity_equivalent']):,.8f} | ${dec(allocation_rows[1]['current_tradingview_mark_usd']):,.2f} | ${dec(allocation_rows[1]['modeled_unrealized_mark_change_usd']):,.2f} |
| **Total** | — | **${remaining:,.2f}** | **{large_total}** | **{small_total:,}** | **${cash_left:,.2f}** | — | — | **${dec(totals['modeled_unrealized_mark_change_usd']):,.2f}** |

## Restored supplemental full-size $20B order at $115 / $101

Per the user's clarification, restore a **full additional $20,000,000,000 order scenario**, split 50/50 under the established foundation design: **$10,000,000,000 BRENT at $115.00** and **$10,000,000,000 OIL/USOIL at $101.00**. Each $10B leg is 10 Large Units ($1B each); the order is 20 Large Units in total. Per the user's latest direction, transfer the existing **50U BRENT / 50U OIL** lots ($500,000 each, $1,000,000 total) from that supplemental foundation allocation to **THE WINNING MODEL**. This leaves $9,999,500,000 of the new order per oil ticker in the locked foundation and assigns $1,000,000 additional notional to the Winner. The oil foundation combines with—not replaces—the original $19,012,754,104.74 residual-pool lots, for a combined locked-oil notional of **${combined_foundation_notional:,.2f}**. The supplemental $20B remains outside the original $20B pool bridge; total scenario capitalization is **$40,000,000,000**, assuming separate fully funded capital with no leverage or financing.

The full-size order date/time was not supplied. The 2026-10-26 mark/PnL columns are illustrative and conditional on the scenario lots being open then; no new execution or fill is inferred. The 50U/50U transfer refers to the existing user-reported ATS source lots dated 2026-10-26 (time unspecified). Their ATS provenance is retained in the reconciliation; THE WINNING MODEL tag is a single allocation reclassification, not a duplicate position or a verified fill.

| Ticker | Original $10B order leg | 50U moved to Winner | Oil-foundation remainder | Entry price | Remaining oil quantity equivalent | Winner transfer quantity equivalent | Oct. 26 mark | Conditional oil-lot price change | Conditional Winner-lot price change |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
{supplemental_table}

| Combined locked-foundation leg | Earlier pool allocation / basis | Retained supplemental-order leg / basis | Combined notional | Combined quantity equivalent | Blended basis | 2026-10-26 TradingView mark | Conditional combined mark value | Conditional price-only change |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
{combined_table}

| Reallocation / Winner burden | Amount |
|---|---:|
| 50U BRENT + 50U OIL transferred from oil foundation | $1,000,000.00 |
| THE WINNING MODEL baseline current open gross notional | ${winner_base_open:,.2f} |
| THE WINNING MODEL scenario allocation after transfer | ${winner_scenario_open:,.2f} |
| Supplemental $20B order remaining in oil foundation | ${supplemental_foundation_notional:,.2f} |

The combined oil position uses the original lot-specific bases plus the remaining $115/$101 order prices; the blended basis is a quantity-weighted summary, not a replacement for component records. Its conditional mark change of **${combined_foundation_pnl:,.2f}** includes **${supplemental_mark_pnl:,.2f}** on the retained supplemental oil portion. The transfer adds **${transfer_mark_pnl:,.2f}** of conditional, unrealized mark change to the Winner-assigned lots, but it does **not** alter THE WINNING MODEL's historical realized PnL or champion-selection result. This is a burden/capital reallocation, not a performance reward, and none of the conditional arithmetic verifies a fill or actual account PnL.

**Historical lock status at the last supplied TradingView close:** **{totals['locked_status']}** as of **{totals['mark_date']}**. At that historical cutoff, the lock rule required both BRENT and OIL EOD marks to reach **$200.00**; marks were BRENT ${dec(allocation_rows[0]['current_tradingview_mark_usd']):,.2f} and OIL ${dec(allocation_rows[1]['current_tradingview_mark_usd']):,.2f}. This historical status predates the later user-reported liquidation. Earlier mark changes remain model-only, not actual account PnL. All quantity equivalents are allocation dollars divided by modeled entry prices; they are **not** contract, barrel, share, or broker-order quantities because contract multipliers, execution quality, fees, financing, and market impact are unspecified.

## Latest user-reported ATS liquidation and organization dissolution

The user states that the money was verified account money and that the ATS automatically liquidated everything at the best available prices, leaving no positions, and that the organization dissolved at a profit due to continued harassment of the organizer. The user accepts approximately **$2.4B** as the conservative endpoint. These are user-reported account, execution, and outcome claims; they have not been independently audited here. The supplied sale prices were BRENT **$114.670–$117.345** across the two marked-price groups and OIL/USOIL **$101.500–$103.400**, with the OIL price-to-lot mapping unspecified.

For context only, applying those extreme sale prices uniformly to the component quantity-equivalents in the **$39,011,754,104.74 modeled locked foundation** yields this price-only envelope. It excludes the separate $1,000,000 source-lot reallocation to THE WINNING MODEL and other separately tracked books. It is not a fill-level accounting of the reported ATS liquidation, and the quantity-equivalents are not independently verified broker quantities.

| Endpoint scenario | BRENT exit input | OIL/USOIL exit input | BRENT modeled price change | OIL modeled price change | Combined modeled price change |
|---|---:|---:|---:|---:|---:|
| Lower endpoint | ${exit_envelope['BRENT']['low_price']:,.3f} | ${exit_envelope['OIL']['low_price']:,.3f} | ${exit_envelope['BRENT']['low_pnl']:,.2f} | ${exit_envelope['OIL']['low_pnl']:,.2f} | **${exit_envelope['COMBINED']['low_pnl']:,.2f}** |
| Upper endpoint | ${exit_envelope['BRENT']['high_price']:,.3f} | ${exit_envelope['OIL']['high_price']:,.3f} | ${exit_envelope['BRENT']['high_pnl']:,.2f} | ${exit_envelope['OIL']['high_pnl']:,.2f} | **${exit_envelope['COMBINED']['high_pnl']:,.2f}** |

The **$870,184,084.04** gap between endpoints is scenario-price uncertainty, not a fee or recorded loss. The user's approximate $2.4B profit characterization aligns with the lower endpoint, but exact realized profit cannot be reconciled without quantities by cohort, individual fill prices, execution timing, costs, and a mapping to account lots. Zero remaining units and dissolution are recorded as the user's reported status; this repository does not execute orders or certify withdrawals.

CSV audits: [model-book deductions](data/{COSTS_CSV.name}), [original balanced pool allocation](data/{OUTPUT_CSV.name}), and [earlier, supplemental, and combined oil-foundation lots](data/{FOUNDATION_LOTS_CSV.name}). The winner scale factor is {winner['equal_gross_scale_factor']}× on cumulative gross additions; the original pool deduction uses its scaled current open notional of ${dec(totals['winner_open_notional_usd']):,.2f}.
"""
    OUTPUT_REPORT.write_text(report, encoding="utf-8")
    print(f"Wrote {COSTS_CSV.relative_to(ROOT)}")
    print(f"Wrote {OUTPUT_CSV.relative_to(ROOT)}")
    print(f"Wrote {FOUNDATION_LOTS_CSV.relative_to(ROOT)}")
    print(f"Wrote {OUTPUT_REPORT.relative_to(ROOT)}")
    print(f"Model deductions: ${deductions:,.2f}; original residual: ${remaining:,.2f}; supplemental order: ${SUPPLEMENTAL_ORDER_USD:,.2f}; 50U/50U transfer to Winner: ${transfer_notional:,.2f}; combined oil foundation: ${combined_foundation_notional:,.2f}; Winner scenario open allocation: ${winner_scenario_open:,.2f}")


if __name__ == "__main__":
    write_outputs()
