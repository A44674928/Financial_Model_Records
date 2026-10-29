#!/usr/bin/env python3
"""Build TradingView-based energy schedules and DXY currency-desk alternatives.

The standard energy schedules and strategy comparisons retain their 10U size.
THE ONE MODEL uses a derived 11U/DAY energy schedule per active BRENT and OIL
ticker in its 16 energy-inclusive portfolios, matching combined 11U/DAY DXY
exposure. DXY's 1U/DAY core sleeve plus 10U/DAY add-on remains unchanged.
DXY is a non-equity index mark, not a listed security/contract.
"""

import csv
import re
from collections import defaultdict
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

from model_perf_core import (
    BENCHMARK_SESSION_FILE,
    PRICES,
    SESSION_DATES,
    UNIT,
    VARIANTS,
    build_lots,
    parse_trades,
)

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
UNIT_SIZES = (0.05, 1.0, 10.0)
ENERGY_TICKERS = ("BRENT", "OIL")
ENERGY_START = {"BRENT": "2026-09-23", "OIL": "2026-09-10"}
ENERGY_CSV = DATA / "tradingview_energy_sidecar_daily_20261026.csv"
DXY_CSV = DATA / "dxy_currency_desk_sidecar_daily_20261026.csv"
DXY_WITHDRAWAL_CSV = DATA / "dxy_withdrawal_scenario_v1.csv"
DXY_CASH_OIL_CSV = DATA / "dxy_cash_oil_bridge_v1.csv"
REPORT = ROOT / "TradingView Energy and Currency Desk Sidecars.md"
DXY_GRAPH = ROOT / "Charts" / "performance" / "23-dxy-daily-sizing-alternatives.png"
CHART_BG = "#0d131e"
CHART_PANEL = "#141c2b"
CHART_GRID = "#243044"
CHART_FG = "#f1f5f9"
CHART_MUTED = "#93a4bd"
DXY_SIZE_COLORS = {"0.05U": "#38bdf8", "1U": "#fbbf24", "10U": "#f472b6"}


def load_session_marks():
    marks = defaultdict(dict)
    metadata = {}
    with BENCHMARK_SESSION_FILE.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            ticker, day = row["Ticker"], row["Date"]
            marks[ticker][day] = float(row["Close"])
            metadata[(ticker, day)] = row
    return marks, metadata


def _ticker_chart_positions(ticker, day, marks, lots_by_ticker):
    idx = SESSION_DATES.index(day)
    price = marks[ticker][day]
    open_lots = [
        lot for lot in lots_by_ticker.get(ticker, [])
        if lot["entry_idx"] <= idx and (lot["close_idx"] is None or idx < lot["close_idx"])
    ]
    units = sum(float(lot["qty"]) for lot in open_lots)
    pnl = sum(
        float(lot["qty"]) * UNIT * (price / float(lot["entry_px"]) - 1.0)
        * (1.0 if lot["side"] == "long" else -1.0)
        for lot in open_lots
    )
    return units, pnl


def build_oil_rows(unit_size_u=None):
    """Return separate Brent/OIL daily-buy schedules for one or all sizes."""
    marks, meta = load_session_marks()
    events = parse_trades()
    core_lots, _ = build_lots("V1", events)
    lots_by_ticker = defaultdict(list)
    for lot in core_lots:
        lots_by_ticker[lot["sym"]].append(lot)
    sizes = (float(unit_size_u),) if unit_size_u is not None else UNIT_SIZES
    rows = []
    for size in sizes:
        daily_notional = size * UNIT
        for ticker in ENERGY_TICKERS:
            first_day = ENERGY_START[ticker]
            active_days = [day for day in SESSION_DATES if day >= first_day]
            cumulative_pnl = 0.0
            for count, day in enumerate(active_days, start=1):
                mark = marks[ticker][day]
                cumulative_notional = count * daily_notional
                cumulative_pnl = sum(
                    daily_notional * (mark / marks[ticker][entry_day] - 1.0)
                    for entry_day in active_days[:count]
                )
                chart_units, chart_pnl = _ticker_chart_positions(ticker, day, marks, lots_by_ticker)
                source = meta[(ticker, day)]
                rows.append({
                    "unit_size_u": f"{size:g}",
                    "unit_size_label": f"{size:g}U",
                    "date": day,
                    "ticker": ticker,
                    "eod_close": f"{mark:.8f}",
                    "daily_buy_units": f"{size:.8f}",
                    "daily_buy_notional_usd": f"{daily_notional:.2f}",
                    "cumulative_daily_buy_units": f"{count * size:.8f}",
                    "cumulative_daily_buy_notional_usd": f"{cumulative_notional:.2f}",
                    "daily_buys_market_value_usd": f"{cumulative_notional + cumulative_pnl:.2f}",
                    "daily_buys_unrealized_pnl_usd": f"{cumulative_pnl:.2f}",
                    "chart_open_units": f"{chart_units:.8f}",
                    "chart_positions_unrealized_pnl_usd": f"{chart_pnl:.2f}",
                    "mark_status": source["Mark_Status"],
                    "source_file": source["Source_File"],
                    "source_file_url": source["Source_File_URL"],
                })
    return rows


def _dxy_signal():
    path = ROOT / "trades" / "DXY.txt"
    from model_perf_core import LINE_RE

    events = []
    for line_no, raw in enumerate(path.read_text(encoding="utf-8").splitlines()):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        match = LINE_RE.match(line)
        if not match:
            raise ValueError(f"Unparsed DXY event {line_no + 1}: {line}")
        events.append({
            "date": match.group("date"),
            "tag": match.group("tag").strip().upper(),
            "kind": match.group("kind"),
            "px": float(match.group("px").replace(",", "")),
            "units": float(match.group("units")),
            "note": match.group("note"),
        })
    return events


def build_dxy_rows(unit_size_u=None):
    """Build DXY daily accumulation alternatives and show logged-lot context."""
    marks, metadata = load_session_marks()
    if "DXY" not in marks:
        raise ValueError("DXY TradingView price list is missing from the aligned benchmark")
    events = _dxy_signal()
    directional = [event for event in events if event["tag"] in {"LONG", "SHORT", "REBUY"}]
    if not directional:
        raise ValueError("No direction-bearing DXY event exists to activate the currency sidecar")
    signal = directional[0]
    direction = "SHORT" if signal["tag"] == "SHORT" else "LONG"
    side_sign = -1.0 if direction == "SHORT" else 1.0
    first_day = signal["date"]
    active_days = [day for day in SESSION_DATES if day >= first_day]
    sizes = (float(unit_size_u),) if unit_size_u is not None else UNIT_SIZES
    logged_entry_pnl = {
        day: signal["units"] * UNIT * side_sign * (marks["DXY"][day] / signal["px"] - 1.0)
        for day in active_days
    }
    rows = []
    for size in sizes:
        daily_notional = size * UNIT
        for count, day in enumerate(active_days, start=1):
            mark = marks["DXY"][day]
            pnl = sum(
                daily_notional * side_sign * (mark / marks["DXY"][entry_day] - 1.0)
                for entry_day in active_days[:count]
            )
            source = metadata[("DXY", day)]
            rows.append({
                "unit_size_u": f"{size:g}",
                "unit_size_label": f"{size:g}U",
                "date": day,
                "ticker": "DXY",
                "direction": direction,
                "eod_close": f"{mark:.8f}",
                "daily_investment_units": f"{size:.8f}",
                "daily_investment_notional_usd": f"{daily_notional:.2f}",
                "cumulative_investment_units": f"{count * size:.8f}",
                "cumulative_notional_added_usd": f"{count * daily_notional:.2f}",
                "open_notional_usd": f"{count * daily_notional:.2f}",
                "daily_investment_unrealized_pnl_usd": f"{pnl:.2f}",
                "logged_chart_position_units": f"{signal['units']:.8f}",
                "logged_chart_entry_price": f"{signal['px']:.8f}",
                "logged_chart_position_unrealized_pnl_usd": f"{logged_entry_pnl[day]:.2f}",
                "signal_note": signal["note"],
                "mark_status": source["Mark_Status"],
                "source_file": source["Source_File"],
                "source_file_url": source["Source_File_URL"],
            })
    return rows


def build_dxy_withdrawal_scenario(dxy_rows, withdrawal_fraction=Decimal("0.40")):
    """Value the requested withdrawal at the latest DXY close, excluding later lots.

    The request predates the Oct. 26 close. Only daily lots accumulated through
    the 2026-10-25 request date are eligible for the 40% withdrawal; those lots
    are marked at the latest supplied DXY close. The following daily addition
    remains outside the withdrawal base. This is a modeled valuation, not proof
    that any withdrawal or cash transfer occurred.
    """
    fraction = Decimal(str(withdrawal_fraction))
    if not Decimal("0") < fraction <= Decimal("1"):
        raise ValueError("Withdrawal fraction must be greater than 0 and at most 1")

    request_date = "2026-10-25"
    latest_date = max(row["date"] for row in dxy_rows if row["ticker"] == "DXY")
    latest = {
        row["unit_size_label"]: row
        for row in dxy_rows
        if row["ticker"] == "DXY" and row["date"] == latest_date
        and row["unit_size_label"] in {"1U", "10U"}
    }
    if set(latest) != {"1U", "10U"}:
        raise ValueError("Withdrawal scenario requires terminal 1U and 10U DXY marks")

    cent = Decimal("0.01")
    def money(value):
        return value.quantize(cent, rounding=ROUND_HALF_UP)

    components = []
    for size_label, component in (("1U", "Integrated core sleeve"), ("10U", "THE ONE add-on")):
        entries = [
            row for row in dxy_rows
            if row["ticker"] == "DXY" and row["unit_size_label"] == size_label
            and row["date"] <= request_date
        ]
        if not entries:
            raise ValueError(f"No pre-request daily DXY lots for {size_label}")
        mark_row = latest[size_label]
        direction_sign = Decimal("-1") if mark_row["direction"] == "SHORT" else Decimal("1")
        latest_close = Decimal(mark_row["eod_close"])
        units = sum(Decimal(row["daily_investment_units"]) for row in entries)
        basis = sum(Decimal(row["daily_investment_notional_usd"]) for row in entries)
        pnl = sum(
            Decimal(row["daily_investment_notional_usd"]) * direction_sign
            * (latest_close / Decimal(row["eod_close"]) - Decimal("1"))
            for row in entries
        )
        market_value = basis + pnl
        withdrawal_units = units * fraction
        withdrawal_basis = basis * fraction
        withdrawal_value = money(market_value * fraction)
        withdrawal_pnl = money(pnl * fraction)
        remaining_units = units - withdrawal_units
        remaining_basis = basis - withdrawal_basis
        remaining_value = money(market_value - withdrawal_value)
        remaining_pnl = money(pnl - withdrawal_pnl)
        components.append({
            "requested_date": request_date,
            "valuation_date": latest_date,
            "valuation_dxy_close": f"{latest_close:.3f}",
            "portfolio_scope": "Per THE ONE portfolio; 1U core + 10U add-on",
            "component": component,
            "withdrawal_fraction": f"{fraction:.4f}",
            "sessions": len(entries),
            "units_before": f"{units:.4f}",
            "notional_basis_before_usd": f"{basis:.2f}",
            "pnl_before_usd": f"{money(pnl):.2f}",
            "marked_value_before_usd": f"{money(market_value):.2f}",
            "units_planned_for_withdrawal": f"{withdrawal_units:.4f}",
            "notional_basis_planned_for_withdrawal_usd": f"{withdrawal_basis:.2f}",
            "reference_withdrawal_mark_value_usd": f"{withdrawal_value:.2f}",
            "pnl_share_at_reference_mark_usd": f"{withdrawal_pnl:.2f}",
            "units_remaining": f"{remaining_units:.4f}",
            "notional_basis_remaining_usd": f"{remaining_basis:.2f}",
            "marked_value_remaining_usd": f"{remaining_value:.2f}",
            "pnl_remaining_at_reference_mark_usd": f"{remaining_pnl:.2f}",
            "status": "valued at supplied 2026-10-26 DXY EOD close; withdrawal/cash transfer not reported executed",
        })

    total = {"sessions": components[0]["sessions"]}
    for key in (
        "units_before", "notional_basis_before_usd", "pnl_before_usd",
        "marked_value_before_usd", "units_planned_for_withdrawal", "notional_basis_planned_for_withdrawal_usd",
        "reference_withdrawal_mark_value_usd", "pnl_share_at_reference_mark_usd", "units_remaining",
        "notional_basis_remaining_usd", "marked_value_remaining_usd", "pnl_remaining_at_reference_mark_usd",
    ):
        values = [Decimal(row[key]) for row in components]
        value = sum(values)
        total[key] = f"{money(value):.2f}" if key.endswith("_usd") or key in {"notional_basis_before_usd"} else f"{value:.4f}"
    components.append({
        "requested_date": request_date,
        "valuation_date": latest_date,
        "valuation_dxy_close": f"{Decimal(latest['1U']['eod_close']):.3f}",
        "portfolio_scope": "Per THE ONE portfolio; combined 11U/DAY",
        "component": "Combined DXY allocation",
        "withdrawal_fraction": f"{fraction:.4f}",
        **total,
        "status": "valued at supplied 2026-10-26 DXY EOD close; withdrawal/cash transfer not reported executed",
    })
    return components


def build_dxy_cash_oil_bridge(dxy_rows, withdrawal_rows):
    """Value the planned DXY withdrawal-to-cash-to-oil scenario without implying execution."""
    combined = next(row for row in withdrawal_rows if row["component"] == "Combined DXY allocation")
    oil_buys = [
        event for event in parse_trades()
        if event["date"] == "2026-10-25" and event["kind"] == "entry"
        and event["sym"] in {"BRENT", "OIL"}
        and "Additional Weekend Oil buy / sentiment-direction change" in event["note"]
    ]
    if {(event["sym"], event["units"]) for event in oil_buys} != {("BRENT", 35), ("OIL", 34)}:
        raise ValueError("The DXY-to-oil bridge expects the logged 35U BRENT and 34U OIL Weekend Oil buys")
    oil_target = sum(Decimal(str(event["units"])) * Decimal(str(UNIT)) for event in oil_buys)
    proceeds = Decimal(combined["reference_withdrawal_mark_value_usd"])
    oil_allocation = min(proceeds, oil_target)
    excess = max(Decimal("0"), proceeds - oil_target)
    shortfall = max(Decimal("0"), oil_target - proceeds)
    return [{
        "request_date": combined["requested_date"],
        "status": "valued at supplied 2026-10-26 DXY EOD close; no withdrawal/cash transfer is reported executed",
        "portfolio_scope": "Per THE ONE portfolio; combined integrated 1U/DAY core + 10U/DAY add-on",
        "current_reference_mark_date": combined["valuation_date"],
        "current_reference_dxy_close": combined["valuation_dxy_close"],
        "existing_combined_dxy_units_before_withdrawal": combined["units_before"],
        "one_time_withdrawal_fraction": combined["withdrawal_fraction"],
        "dxy_units_to_withdraw": combined["units_planned_for_withdrawal"],
        "dxy_notional_basis_to_withdraw_usd": combined["notional_basis_planned_for_withdrawal_usd"],
        "dxy_withdrawal_proceeds_at_next_eod_usd": f"{proceeds:.2f}",
        "reference_withdrawal_mark_value_at_current_mark_usd": f"{proceeds:.2f}",
        "oil_buys_to_fund": "BRENT 35U at 114.627; OIL 34U at 100.74",
        "oil_cash_allocation_target_usd": f"{oil_target:.2f}",
        "oil_cash_allocation_at_next_eod_usd": f"{oil_allocation:.2f}",
        "excess_cash_support_for_existing_positions_at_next_eod_usd": f"{excess:.2f}",
        "reference_excess_cash_support_at_current_mark_usd": f"{excess:.2f}",
        "oil_cash_shortfall_at_next_eod_usd": f"{shortfall:.2f}",
        "remaining_dxy_units_before_future_daily_lots": combined["units_remaining"],
        "future_combined_dxy_schedule_u_per_eod": "11",
        "incremental_portfolio_size_from_internal_transfer_usd": "0.00",
        "cash_method": "Scenario: DXY withdrawal proceeds -> cash -> fund up to the logged $690,000 oil-buy notional; any excess is separate cash support for existing positions, not new position size",
        "valuation_note": "Valued at the user-provided 2026-10-26 DXY close of 102.017; withdrawal, cash balance, and oil funding remain modeled only and are not reported as executed",
    }]


def write_rows(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return path


def write_dxy_sizing_graph(rows):
    """Plot the three DXY daily-lot size alternatives as readable small multiples."""
    grouped = defaultdict(list)
    for row in rows:
        grouped[row["unit_size_label"]].append(row)
    expected = ("0.05U", "1U", "10U")
    if set(grouped) != set(expected):
        raise ValueError(f"DXY graph requires all three sizing options: {sorted(grouped)}")

    CHARTS = DXY_GRAPH.parent
    CHARTS.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(3, 1, figsize=(13.5, 10), sharex=True)
    fig.patch.set_facecolor(CHART_BG)
    unit_tags = {"0.05U": "ALTERNATIVE", "1U": "INTEGRATED IN EACH CORE", "10U": "THE ONE MODEL ADD-ON"}
    for ax, size in zip(axes, expected):
        values = sorted(grouped[size], key=lambda row: row["date"])
        dates = [datetime.strptime(row["date"], "%Y-%m-%d") for row in values]
        pnl = [float(row["daily_investment_unrealized_pnl_usd"]) for row in values]
        terminal = pnl[-1]
        cumulative_notional = float(values[-1]["cumulative_notional_added_usd"])
        color = DXY_SIZE_COLORS[size]

        ax.set_facecolor(CHART_PANEL)
        ax.plot(dates, pnl, color=color, linewidth=2.2)
        ax.fill_between(dates, pnl, 0, color=color, alpha=0.12)
        ax.axhline(0, color=CHART_MUTED, linewidth=0.9, linestyle="--", alpha=0.7)
        ax.grid(True, color=CHART_GRID, linewidth=0.7, alpha=0.9)
        ax.tick_params(colors=CHART_MUTED, labelsize=9)
        for spine in ax.spines.values():
            spine.set_color(CHART_GRID)
        ax.yaxis.set_major_formatter(FuncFormatter(lambda value, _: f"${value:,.0f}"))
        ax.set_ylabel("Sleeve PnL (USD)", color=CHART_MUTED, fontsize=9)
        ax.set_title(
            f"{size}/DAY — ${float(size[:-1]) * UNIT:,.0f} daily · "
            f"${cumulative_notional:,.0f} cumulative · terminal "
            f"{'+' if terminal >= 0 else '-'}${abs(terminal):,.2f} · {unit_tags[size]}",
            color=CHART_FG,
            fontsize=10.5,
            loc="left",
            pad=7,
        )
        ax.scatter([dates[-1]], [terminal], color=color, edgecolor=CHART_FG, linewidth=0.7, s=36, zorder=5)

    all_dates = [datetime.strptime(row["date"], "%Y-%m-%d") for row in sorted(grouped["1U"], key=lambda row: row["date"])]
    ticks = list(range(0, len(all_dates), 5))
    if len(all_dates) - 1 not in ticks:
        ticks.append(len(all_dates) - 1)
    tick_positions = [all_dates[i] for i in ticks]
    axes[-1].set_xticks(tick_positions)
    axes[-1].set_xticklabels([day.strftime("%m-%d") for day in tick_positions], rotation=0, color=CHART_MUTED)
    axes[-1].set_xlabel("TradingView EOD session (MST)", color=CHART_MUTED, fontsize=10)
    fig.suptitle(
        "DXY Daily-Investment Sizing Options — TradingView EOD Marks",
        color=CHART_FG,
        fontsize=15,
        fontweight="bold",
        y=0.985,
    )
    fig.text(
        0.5,
        0.012,
        "Each panel uses its own dollar scale. 1U/DAY is already in core PnL; THE ONE MODEL adds 10U/DAY on top (11U total), while 0.05U remains an alternative.",
        ha="center",
        color=CHART_MUTED,
        fontsize=9,
    )
    fig.tight_layout(rect=(0.02, 0.04, 0.99, 0.96), h_pad=1.2)
    fig.savefig(DXY_GRAPH, dpi=160, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close(fig)
    return DXY_GRAPH


def _terminal_rows(rows, pnl_field, added_field, key_fields):
    summaries = []
    grouped = defaultdict(list)
    for row in rows:
        key = tuple(row[field] for field in key_fields)
        grouped[key].append(row)
    for key, values in grouped.items():
        last = values[-1]
        summaries.append({
            **dict(zip(key_fields, key)),
            "sessions": len(values),
            "daily_notional_usd": last.get("daily_buy_notional_usd", last.get("daily_investment_notional_usd", "")),
            "cumulative_notional_added_usd": last[added_field],
            "terminal_pnl_usd": last[pnl_field],
        })
    return summaries


def write_report(oil_rows, dxy_rows, withdrawal_rows, cash_bridge_rows):
    oil_summary = _terminal_rows(oil_rows, "daily_buys_unrealized_pnl_usd", "cumulative_daily_buy_notional_usd", ("unit_size_label", "ticker"))
    dxy_summary = _terminal_rows(dxy_rows, "daily_investment_unrealized_pnl_usd", "cumulative_notional_added_usd", ("unit_size_label", "ticker"))
    combined_withdrawal = next(row for row in withdrawal_rows if row["component"] == "Combined DXY allocation")
    bridge = cash_bridge_rows[0]
    valuation_date = combined_withdrawal["valuation_date"]
    lines = [
        "# TradingView Energy and Currency Desk Sidecars",
        "",
        "> **TradingView sidecar schedules through 2026-10-26.** Historical prices use the user-provided Part A/Part B TradingView lists; the Oct. 26 direct-price update and DXY close are user-supplied. 1U = $10,000 notional; displayed standard daily allocations are 0.05U ($500), 1U ($10,000), and 10U ($100,000). The 1U/DAY/DXY schedule is integrated into every core variant. THE ONE MODEL adds 10U/DAY DXY to all 32 portfolios (11U/DAY combined), and uses a derived 11U/DAY energy tranche per active BRENT and OIL ticker in its 16 energy-inclusive portfolios. 0.05U DXY remains an alternative. These are hypothetical dollar-notional/index-return exposures, not an actual DXY security trade, broker fills, or account returns.",

        "",
        "## Energy desk: separate Brent and WTI daily-buy schedules",
        "",
        "Each size option adds a fixed-notional long lot at that session's EOD mark beginning with the first logged chart position for the instrument. The purchase-day mark-to-market is zero. Energy-sidecar PnL below includes only the new daily-buy lots; the pre-existing chart position PnL is displayed separately for context and is not counted again in model composites.",
        "",
        "For THE ONE MODEL only, the 11U/DAY schedule per active ticker is derived from the audited 10U TradingView energy rows so each active energy tranche matches the model's combined 11U/DAY DXY exposure. The 10U schedule remains the size used in the separate strategy-comparison composites. Derived THE ONE MODEL schedule: [`the_one_model_energy_11u_sidecar_daily_v1.csv`](data/the_one_model_energy_11u_sidecar_daily_v1.csv).",
        "",
        "| Daily size | Ticker | Daily notional | Sessions | Cumulative notional added | Daily-buy terminal PnL | Chart-position PnL (separate) |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for summary in oil_summary:
        ticker = summary["ticker"]
        last = next(r for r in oil_rows if r["unit_size_label"] == summary["unit_size_label"] and r["ticker"] == ticker and r["date"] == SESSION_DATES[-1])
        lines.append(
            f"| {summary['unit_size_label']} | {ticker} | ${float(summary['daily_notional_usd']):,.2f} | {summary['sessions']} | "
            f"${float(summary['cumulative_notional_added_usd']):,.2f} | ${float(summary['terminal_pnl_usd']):+,.2f} | "
            f"${float(last['chart_positions_unrealized_pnl_usd']):+,.2f} |"
        )
    lines.extend([
        "",
        "## One-time Weekend Oil position overlay",
        "",
        "The user-specified 50U LONG BRENT and 50U LONG USOIL Manual-Automatic lots opened at the supplied TradingView marks on 2026-10-19, with 10U target trims at $117 and $102 respectively, are integrated in all four core variants and therefore flow into core-based strategy composites and THE ONE MODEL. Their first recorded EOD marks at/above target are on 2026-10-23; intraday touch and execution are unverified. Separate user-directed hypothetical 10U SHORT lots at those same target levels are recorded as a force-multiplier sentiment overlay. Their explicit modeled exits are $114.627 BRENT and $100.74 OIL on 2026-10-25 at 20:35 MST, after the four earlier Oct. 25 LONG replenishments and simultaneous with distinct 35U BRENT and 34U OIL LONG Weekend Oil buys. The buys count toward weekly buy supply; the 10U short closures do not. After the modeled exits, the all-core oil long exposure reaches 100U BRENT + 100U OIL = 200U combined ($2,000,000 fixed-unit notional). Those lot-specific exits override SAR auto-close only for these shorts and all prices/timing remain hypothetical, not verified executions. [`Weekend Oil 50U Position Hypothetical.md`](Weekend%20Oil%2050U%20Position%20Hypothetical.md) attributes only the tagged long lots, not these separate shorts or the daily-buy schedule. Four separate manual LONG 10U replenishment entries are logged after the preserved Oct. 23 baseline and before the current Oct. 26 EOD mark, all on Oct. 25: BRENT at $115.792 and OIL at $101.74 use the user-recalled 17:20–17:25 MST window, modeled at a 17:22 midpoint, while BRENT at $114.80 and OIL at $101.00 use an approximate 20:00 MST timestamp per the user's recollection. Both times are modeling assumptions, not verified transaction times; the supplied prices remain the modeled replenishment prices. All current BRENT/OIL long lots are marked at the user-supplied Oct. 26 EOD closes ($115.38/$101.30), without claiming verified brokerage positions or execution. The four replenishments, 35U BRENT and 34U OIL approved orders, and explicit Oct. 25 20:35 MST SHORT exits were entered after the preserved Oct. 23 baseline; they are included in the current Oct. 26 replay at supplied marks. The additional buys are distinct LONG lots; their simultaneous short closures do not count toward weekly buy supply. Together with existing post-close all-core exposure of 65U BRENT + 66U OIL, the buys bring the all-core long total to 100U per ticker, 200U combined. The user-specified short-exit prices override SAR only for these two tagged shorts.",


        "",
        "## ATS / manual live-position reconciliation",
        "",
        "A separate user-directed reconciliation uses the tagged 50U-per-ticker Weekend Oil positions as the sizing proxy: up to 40U per ticker in the **AUTOMATED TRADING SYSTEM LIVE POSITIONS** ceiling and a distinct 10U **MANUAL LIVE TEST POSITIONS** remainder. ATS exits/shorts at $118 BRENT / $103.50 OIL are shown at 10U, 20U, 30U, and 40U sensitivities because the user reports the activity but does not know the exact executed quantity. This is separate from the legacy Oct. 23 replay above; the earlier 10U trims/shorts are superseded only in the new reconciliation and must not be stacked. The four Oct. 25 10U replenishments remain MANUAL LIVE TEST POSITIONS; the 35U/34U orders are MANUALLY APPROVED SHORT CLOSURE, allocated to open ATS shorts first, with only any excess remaining long and counted as new buy supply. The existing 50U-per-ticker ATS LONG entries at fixed $115 BRENT / $101 OIL are logged on Oct. 26. The later separate 50U ATS USOIL mirror LONG @ $101.11 at 07:51 MST is synchronized with the 50U manual BRENT entry and distinct from the earlier OIL @ $101.00 lot. Later user-reported adds are 10U each via a manually approved ATS order ($115.025 BRENT / $100.96 OIL), 16U BRENT @ $114.90 and 17U OIL @ $100.85 (classification/time unspecified), and a separate 50U manual BRENT LONG @ $115.51 at 07:51:14 MST from a TradingView screenshot. Dates for the user-reported additions are inferred from the conversation context where not explicitly supplied; LONG on the screenshot-supported lot is inferred from the handwritten “PICK UP OPPORTUNITY” annotation. Actual fills are unverified. In the 40U-per-ticker ceiling scenario, the tagged campaign totals 161U BRENT / 161U OIL. See [`ATS and Manual Live Position Reconciliation.md`](ATS%20and%20Manual%20Live%20Position%20Reconciliation.md) and [`ats_manual_live_positions_v1.csv`](data/ats_manual_live_positions_v1.csv). A later user report states that all ATS-held oil positions were sold; the price bands are in [`ats_oil_liquidation_reported_v1.csv`](data/ats_oil_liquidation_reported_v1.csv). Quantities, exact fill prices, date/time, and realized PnL remain unspecified; the sensitivity rows above are pre-liquidation and do not establish current exposure.",
        "",
        "## DXY currency desk: daily long-investment alternatives",
        "",
        "The DXY log has one LONG badge on Sep. 4 at 99.087 (the original post's caption says the dollar weakens, which conflicts with its LONG badge). The logged badge is treated as the activation signal; daily 1U lots follow the latest charted LONG/REBUY/SHORT direction. The 1U/DAY schedule shown here is the same sleeve integrated into each core variant, not an additional allocation to stack on top. Because DXY is an index rather than a directly investable security, this is a hypothetical notional/index-return proxy; no futures/ETF contract, multiplier, collateral, or tracking error is modeled. The logged one-time 1U chart-position result is shown separately and is not part of the daily sleeve.",
        "",
        "| Daily size | Daily notional | Sessions | Cumulative notional added | Daily-investment terminal PnL | Logged 1U chart-position PnL (separate) |",
        "|---|---:|---:|---:|---:|---:|",
    ])
    for summary in dxy_summary:
        last = next(r for r in dxy_rows if r["unit_size_label"] == summary["unit_size_label"] and r["date"] == SESSION_DATES[-1])
        lines.append(
            f"| {summary['unit_size_label']} | ${float(summary['daily_notional_usd']):,.2f} | {summary['sessions']} | "
            f"${float(summary['cumulative_notional_added_usd']):,.2f} | ${float(summary['terminal_pnl_usd']):+,.2f} | "
            f"${float(last['logged_chart_position_unrealized_pnl_usd']):+,.2f} |"
        )
    lines.extend([
        "",
        "## One-time 40% DXY withdrawal sizing reference",
        "",
        f"This scenario values the user-requested one-time 40% withdrawal from the selected combined DXY allocation: the integrated 1U/DAY core sleeve plus THE ONE MODEL's 10U/DAY add-on. The request predates the Oct. 26 mark, so its 35 active sessions (385U; 154U planned for withdrawal, $1,540,000 initial-notional basis) are valued at the supplied {valuation_date} DXY close of {Decimal(combined_withdrawal['valuation_dxy_close']):.3f}; Oct. 26 daily additions are excluded from the withdrawal base. The modeled withdrawal value is ${Decimal(combined_withdrawal['reference_withdrawal_mark_value_usd']):,.2f}, leaving {Decimal(combined_withdrawal['units_remaining']):g}U / ${Decimal(combined_withdrawal['notional_basis_remaining_usd']):,.2f} basis before later daily additions. This is a valuation scenario only; no withdrawal, cash transfer, or brokerage execution is reported as completed. Future daily sizing stays at 11U/DAY. The one-time chart-position 1U and unselected 0.05U alternative are excluded. The baseline historical results through Oct. 23 remain unchanged; THE ONE's 32 portfolios are alternative modeled books, not one account position.",
        "",
        f"| Component | Units before | Notional basis before | Marked value at {valuation_date} | Units planned to withdraw | Notional basis planned for withdrawal | Estimated value at {valuation_date} mark | 40% PnL share at {valuation_date} mark | Units remaining | Remaining marked value | Remaining PnL |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ])
    def fmt_units(value):
        text = format(Decimal(value).normalize(), "f")
        return text.rstrip("0").rstrip(".") if "." in text else text

    for row in withdrawal_rows:
        units_before = fmt_units(row["units_before"])
        units_planned_for_withdrawal = fmt_units(row["units_planned_for_withdrawal"])
        units_remaining = fmt_units(row["units_remaining"])
        lines.append(
            f"| {row['component']} | {units_before}U | "
            f"${Decimal(row['notional_basis_before_usd']):,.2f} | ${Decimal(row['marked_value_before_usd']):,.2f} | "
            f"{units_planned_for_withdrawal}U | ${Decimal(row['notional_basis_planned_for_withdrawal_usd']):,.2f} | "
            f"${Decimal(row['reference_withdrawal_mark_value_usd']):,.2f} | ${Decimal(row['pnl_share_at_reference_mark_usd']):+,.2f} | "
            f"{units_remaining}U | ${Decimal(row['marked_value_remaining_usd']):,.2f} | "
            f"${Decimal(row['pnl_remaining_at_reference_mark_usd']):+,.2f} |"
        )
    lines.extend([
        "",
        f"Reference export: [`{DXY_WITHDRAWAL_CSV.name}`](data/{DXY_WITHDRAWAL_CSV.name}). The {valuation_date} amount is a modeled valuation—not a verified fill, withdrawal, or cash balance.",
        "",
        "## DXY → cash → oil bridge (modeled valuation; not reported executed)",
        "",
        f"The supplied {valuation_date} DXY close now allows the requested 40% withdrawal scenario to be valued. It uses only the pre-request 385U combined allocation (154U withdrawal; the Oct. 26 daily addition is excluded), then models routing proceeds through cash to fund up to $690,000 of the logged 35U BRENT and 34U OIL buys. Excess is a separate cash-support scenario for existing positions; any shortfall is disclosed without assuming new funding. No actual withdrawal, transfer, or brokerage execution was reported. Future DXY daily additions remain at 11U/DAY.",
        "",
        f"| Bridge item | Modeled treatment at {valuation_date} | Scenario value |",
        "|---|---:|---:|",
        f"| DXY withdrawal value | 40% of pre-request 385U; 154U | ${Decimal(bridge['dxy_withdrawal_proceeds_at_next_eod_usd']):,.2f} |",
        f"| Oil purchases funded from withdrawal cash | Up to $690,000.00 | ${Decimal(bridge['oil_cash_allocation_at_next_eod_usd']):,.2f} |",
        f"| Excess cash support for existing positions | Cash only; no new units | ${Decimal(bridge['excess_cash_support_for_existing_positions_at_next_eod_usd']):,.2f} |",
        f"| Oil-buy funding shortfall | No extra funding assumed | ${Decimal(bridge['oil_cash_shortfall_at_next_eod_usd']):,.2f} |",
        "| New portfolio size from this internal transfer | $0.00 | $0.00 |",
        "",
        f"Bridge ledger: [`{DXY_CASH_OIL_CSV.name}`](data/{DXY_CASH_OIL_CSV.name}). The reference column is not an actual withdrawal or cash balance.",
        "",
        "![Three DXY daily-investment sizing options](Charts/performance/23-dxy-daily-sizing-alternatives.png)",
        "",
        "*Three-panel view of the 0.05U, 1U, and 10U DXY daily-lot PnL paths. Each panel uses its own dollar scale; the size labels show daily and cumulative notional. The 1U/DAY schedule is included in every core model. THE ONE MODEL adds the 10U/DAY schedule on top, for 11U/DAY total; 0.05U remains an alternative.*",
        "",
        "The 0.05U, 1U, and 10U rows show sizing scenarios. The 1U/DAY/DXY PnL and notional are already included in each core model; do not add the 1U schedule a second time. THE ONE MODEL selects the 10U/DAY schedule as a separate add-on in each of its 32 portfolios, making 11U/DAY combined DXY exposure; 0.05U remains an unselected alternative. Other strategy-comparison composites retain their existing scope. Do not treat the one-time chart-position context as included in the daily-investment results.",
        "",
        "The crypto positions have been removed from the core comparison pending source calibration. See [`Crypto Sidecar — Pending TradingView Recalibration.md`](Crypto%20Sidecar%20%E2%80%94%20Pending%20TradingView%20Recalibration.md); no BTC/ETH marks or PnL are used here.",
        "",
        "Machine-readable daily schedules: [`tradingview_energy_sidecar_daily_20261026.csv`](data/tradingview_energy_sidecar_daily_20261026.csv), [`dxy_currency_desk_sidecar_daily_20261026.csv`](data/dxy_currency_desk_sidecar_daily_20261026.csv). Price source/mark flags: [`tradingview_benchmark_session_marks_20261026.csv`](data/tradingview_benchmark_session_marks_20261026.csv).",
        "",
    ])
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def main():
    oil_rows = build_oil_rows()
    dxy_rows = build_dxy_rows()
    withdrawal_rows = build_dxy_withdrawal_scenario(dxy_rows)
    cash_bridge_rows = build_dxy_cash_oil_bridge(dxy_rows, withdrawal_rows)
    write_rows(ENERGY_CSV, oil_rows)
    write_rows(DXY_CSV, dxy_rows)
    write_rows(DXY_WITHDRAWAL_CSV, withdrawal_rows)
    write_rows(DXY_CASH_OIL_CSV, cash_bridge_rows)
    write_dxy_sizing_graph(dxy_rows)
    write_report(oil_rows, dxy_rows, withdrawal_rows, cash_bridge_rows)
    print(f"Wrote {ENERGY_CSV.relative_to(ROOT)} ({len(oil_rows)} rows)")
    print(f"Wrote {DXY_CSV.relative_to(ROOT)} ({len(dxy_rows)} rows)")
    print(f"Wrote {DXY_WITHDRAWAL_CSV.relative_to(ROOT)} ({len(withdrawal_rows)} rows)")
    print(f"Wrote {DXY_CASH_OIL_CSV.relative_to(ROOT)} ({len(cash_bridge_rows)} rows)")
    print(f"Wrote {DXY_GRAPH.relative_to(ROOT)}")
    print(f"Wrote {REPORT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
