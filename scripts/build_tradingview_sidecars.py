#!/usr/bin/env python3
"""Build TradingView-based energy schedules and DXY currency-desk alternatives.

Energy sizes are standalone. The 1U/DAY/DXY index-return schedule is integrated
into each core variant; 0.05U and 10U DXY schedules are separate alternatives.
DXY is a non-equity index mark, not a listed security/contract.
"""

import csv
import re
from collections import defaultdict
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
ENERGY_CSV = DATA / "tradingview_energy_sidecar_daily_20261024.csv"
DXY_CSV = DATA / "dxy_currency_desk_sidecar_daily_20261024.csv"
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
    unit_tags = {"0.05U": "STANDALONE", "1U": "INTEGRATED IN EACH CORE", "10U": "STANDALONE"}
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
        "Each panel uses its own dollar scale for readability. 1U/DAY is already in core PnL; 0.05U and 10U are standalone alternatives.",
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


def write_report(oil_rows, dxy_rows):
    oil_summary = _terminal_rows(oil_rows, "daily_buys_unrealized_pnl_usd", "cumulative_daily_buy_notional_usd", ("unit_size_label", "ticker"))
    dxy_summary = _terminal_rows(dxy_rows, "daily_investment_unrealized_pnl_usd", "cumulative_notional_added_usd", ("unit_size_label", "ticker"))
    lines = [
        "# TradingView Energy and Currency Desk Sidecars",
        "",
        "> **TradingView sidecar schedules — 2026-10-24 benchmark.** Prices use only the user-provided Part A/Part B TradingView lists. 1U = $10,000 notional; displayed daily allocations are 0.05U ($500), 1U ($10,000), and 10U ($100,000). The 1U/DAY/DXY schedule is integrated into every core variant; its 0.05U and 10U rows are standalone alternatives. These are hypothetical dollar-notional/index-return exposures, not broker fills or account returns.",
        "",
        "## Energy desk: separate Brent and WTI daily-buy schedules",
        "",
        "Each size option adds a fixed-notional long lot at that session's EOD mark beginning with the first logged chart position for the instrument. The purchase-day mark-to-market is zero. Energy-sidecar PnL below includes only the new daily-buy lots; the pre-existing chart position PnL is displayed separately for context and is not counted again in model composites.",
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
        "![Three DXY daily-investment sizing options](Charts/performance/23-dxy-daily-sizing-alternatives.png)",
        "",
        "*Three-panel view of the 0.05U, 1U, and 10U DXY daily-lot PnL paths. Each panel uses its own dollar scale for readability; the size labels show daily and cumulative notional. The 1U/DAY schedule is included in every core model, while 0.05U and 10U are standalone alternatives.*",
        "",
        "The 0.05U, 1U, and 10U rows are alternative sizing views. The 1U/DAY/DXY PnL and notional are already included in each core model; do not add them a second time. The 0.05U and 10U rows are standalone alternatives, not core positions. Do not treat the one-time chart-position context as included in the daily-investment results.",
        "",
        "The crypto positions have been removed from the core comparison pending source calibration. See [`Crypto Sidecar — Pending TradingView Recalibration.md`](Crypto%20Sidecar%20%E2%80%94%20Pending%20TradingView%20Recalibration.md); no BTC/ETH marks or PnL are used here.",
        "",
        "Machine-readable daily schedules: [`tradingview_energy_sidecar_daily_20261024.csv`](data/tradingview_energy_sidecar_daily_20261024.csv), [`dxy_currency_desk_sidecar_daily_20261024.csv`](data/dxy_currency_desk_sidecar_daily_20261024.csv). Price source/mark flags: [`tradingview_benchmark_session_marks_20261024.csv`](data/tradingview_benchmark_session_marks_20261024.csv).",
        "",
    ])
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def main():
    oil_rows = build_oil_rows()
    dxy_rows = build_dxy_rows()
    write_rows(ENERGY_CSV, oil_rows)
    write_rows(DXY_CSV, dxy_rows)
    write_dxy_sizing_graph(dxy_rows)
    write_report(oil_rows, dxy_rows)
    print(f"Wrote {ENERGY_CSV.relative_to(ROOT)} ({len(oil_rows)} rows)")
    print(f"Wrote {DXY_CSV.relative_to(ROOT)} ({len(dxy_rows)} rows)")
    print(f"Wrote {DXY_GRAPH.relative_to(ROOT)}")
    print(f"Wrote {REPORT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
