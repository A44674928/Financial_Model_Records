#!/usr/bin/env python3
"""Aggregate the 32 independent THE ONE MODEL split portfolios.

The 32 portfolios are all 4 x 4 Core/variant-specific-1U-EOD pairings, each
run separately with and without its own exact-mark oil sidecar. No capital,
positions, or risk is netted across portfolios.
"""
import csv
import json
from datetime import datetime
from decimal import Decimal
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data" / "strategy_sidecar_comparison_daily_v1.csv"
CSV_OUT = ROOT / "data" / "the_one_model_split_portfolios_v1.csv"
JSON_OUT = ROOT / "data" / "the_one_model_split_portfolios_v1_summary.json"
CHART_OUT = ROOT / "Charts" / "superstructure" / "the-one-model-split-portfolio.png"
VARIANTS = ("V1", "V2", "V3A", "V3B")


def dec(row, key):
    return Decimal(row[key])


def portfolio_definitions():
    portfolios = []
    for core in VARIANTS:
        for force in VARIANTS:
            base = f"{core}_core_plus_{force}_force_1u"
            for oil in (False, True):
                prefix = base + ("_and_oil" if oil else "")
                portfolio_id = f"core_{core.lower()}__1u_{force.lower()}__{'with_oil' if oil else 'no_oil'}"
                portfolios.append({
                    "portfolio_id": portfolio_id,
                    "core_variant": core,
                    "one_unit_eod_variant": force,
                    "oil_sidecar_included": oil,
                    "source_prefix": prefix,
                })
    return portfolios


def _max_drawdown(rows, pnl_field):
    peak = Decimal("0")
    peak_date = "before period"
    max_drawdown = Decimal("0")
    record = {
        "amount": Decimal("0"),
        "peak_date": peak_date,
        "peak_pnl": peak,
        "trough_date": rows[0]["date"],
        "trough_pnl": Decimal("0"),
    }
    for row in rows:
        pnl = Decimal(row[pnl_field])
        if pnl > peak:
            peak, peak_date = pnl, row["date"]
        drawdown = peak - pnl
        if drawdown > max_drawdown:
            max_drawdown = drawdown
            record = {
                "amount": drawdown,
                "peak_date": peak_date,
                "peak_pnl": peak,
                "trough_date": row["date"],
                "trough_pnl": pnl,
            }
    return record


def build_rows():
    with INPUT.open(newline="", encoding="utf-8") as handle:
        source_rows = list(csv.DictReader(handle))
    if not source_rows:
        raise ValueError(f"No source rows in {INPUT}")
    portfolios = portfolio_definitions()
    output_rows = []
    oil_key = "oil_desk_daily_buy_pnl_usd"
    oil_notional_key = "oil_desk_cumulative_notional_usd"
    oil_open_key = "oil_desk_open_notional_usd"

    for source in source_rows:
        row = {"date": source["date"]}
        aggregate_pnl = Decimal("0")
        aggregate_added = Decimal("0")
        aggregate_open = Decimal("0")
        for portfolio in portfolios:
            prefix = portfolio["source_prefix"]
            pnl = dec(source, f"{prefix}_pnl_usd")
            added = dec(source, f"{prefix}_cumulative_notional_usd")
            opened = dec(source, f"{prefix}_open_notional_usd")
            if portfolio["oil_sidecar_included"]:
                base = prefix.removesuffix("_and_oil")
                checks = (
                    (pnl, dec(source, f"{base}_pnl_usd") + dec(source, oil_key), "PnL"),
                    (added, dec(source, f"{base}_cumulative_notional_usd") + dec(source, oil_notional_key), "notional added"),
                    (opened, dec(source, f"{base}_open_notional_usd") + dec(source, oil_open_key), "open notional"),
                )
                for actual, expected, label in checks:
                    if abs(actual - expected) > Decimal("0.01"):
                        raise ValueError(f"Oil sleeve {label} does not reconcile for {portfolio['portfolio_id']} on {source['date']}")
            ratio = pnl / added * Decimal("100") if added else Decimal("0")
            row[f"{portfolio['portfolio_id']}__pnl_usd"] = f"{pnl:.2f}"
            row[f"{portfolio['portfolio_id']}__cumulative_notional_added_usd"] = f"{added:.2f}"
            row[f"{portfolio['portfolio_id']}__open_notional_usd"] = f"{opened:.2f}"
            row[f"{portfolio['portfolio_id']}__deployed_notional_ratio_pct"] = f"{ratio:.6f}"
            aggregate_pnl += pnl
            aggregate_added += added
            aggregate_open += opened
        row["aggregate_pnl_usd"] = f"{aggregate_pnl:.2f}"
        row["aggregate_cumulative_notional_added_usd"] = f"{aggregate_added:.2f}"
        row["aggregate_open_notional_usd"] = f"{aggregate_open:.2f}"
        row["aggregate_deployed_notional_ratio_pct"] = f"{aggregate_pnl / aggregate_added * Decimal('100'):.6f}" if aggregate_added else "0.000000"
        output_rows.append(row)

    if len(output_rows) != 36 or output_rows[0]["date"] != "2026-09-03" or output_rows[-1]["date"] != "2026-10-23":
        raise ValueError("Expected the 36-session comparison period 2026-09-03 through 2026-10-23")
    return portfolios, output_rows


def build_summary(portfolios, rows):
    last = rows[-1]
    details = []
    for portfolio in portfolios:
        portfolio_id = portfolio["portfolio_id"]
        pnl_field = f"{portfolio_id}__pnl_usd"
        pnl = Decimal(last[pnl_field])
        added = Decimal(last[f"{portfolio_id}__cumulative_notional_added_usd"])
        opened = Decimal(last[f"{portfolio_id}__open_notional_usd"])
        dd = _max_drawdown(rows, pnl_field)
        details.append({
            "portfolio_id": portfolio_id,
            "core_variant": portfolio["core_variant"],
            "variant_specific_1u_eod_variant": portfolio["one_unit_eod_variant"],
            "oil_sidecar_included": portfolio["oil_sidecar_included"],
            "terminal_pnl_usd": f"{pnl:.2f}",
            "cumulative_gross_notional_added_usd": f"{added:.2f}",
            "gross_open_notional_usd": f"{opened:.2f}",
            "deployed_notional_ratio_pct": f"{pnl / added * Decimal('100'):.6f}" if added else "0.000000",
            "max_peak_to_trough_pnl_drawdown_usd": f"{dd['amount']:.2f}",
            "max_drawdown_peak_date": dd["peak_date"],
            "max_drawdown_peak_pnl_usd": f"{dd['peak_pnl']:.2f}",
            "max_drawdown_trough_date": dd["trough_date"],
            "max_drawdown_trough_pnl_usd": f"{dd['trough_pnl']:.2f}",
        })
    details_by_pnl = sorted(details, key=lambda item: Decimal(item["terminal_pnl_usd"]))
    agg_dd = _max_drawdown(rows, "aggregate_pnl_usd")
    terminal_pnl = Decimal(last["aggregate_pnl_usd"])
    terminal_added = Decimal(last["aggregate_cumulative_notional_added_usd"])
    terminal_open = Decimal(last["aggregate_open_notional_usd"])
    pnl_values = sorted(Decimal(item["terminal_pnl_usd"]) for item in details)
    median = (pnl_values[15] + pnl_values[16]) / Decimal("2")
    summary = {
        "label": "THE ONE MODEL — 32 independent split portfolios",
        "period_start": rows[0]["date"],
        "period_end": last["date"],
        "sessions": len(rows),
        "portfolio_count": len(portfolios),
        "construction": "4 Core variants x 4 variant-specific 1U/EOD variants x 2 oil-sidecar states (without oil / with exact-mark oil sidecar)",
        "portfolio_funding_and_netting": "Each of the 32 is modeled as an independent portfolio. PnL and gross exposure are summed; positions, risk, and capital are not netted or shared.",
        "oil_sidecar_treatment": "Oil is included once in each of the 16 with-oil portfolios; the 16 repetitions represent distinct funded portfolios, not one sidecar counted twice within a portfolio.",
        "aggregate_terminal_pnl_usd": f"{terminal_pnl:.2f}",
        "aggregate_cumulative_gross_notional_added_usd": f"{terminal_added:.2f}",
        "aggregate_gross_open_notional_usd": f"{terminal_open:.2f}",
        "aggregate_deployed_notional_ratio_pct": f"{terminal_pnl / terminal_added * Decimal('100'):.6f}" if terminal_added else "0.000000",
        "aggregate_max_peak_to_trough_pnl_drawdown_usd": f"{agg_dd['amount']:.2f}",
        "aggregate_max_drawdown_peak_date": agg_dd["peak_date"],
        "aggregate_max_drawdown_peak_pnl_usd": f"{agg_dd['peak_pnl']:.2f}",
        "aggregate_max_drawdown_trough_date": agg_dd["trough_date"],
        "aggregate_max_drawdown_trough_pnl_usd": f"{agg_dd['trough_pnl']:.2f}",
        "profitable_portfolios_at_terminal": sum(Decimal(item["terminal_pnl_usd"]) > 0 for item in details),
        "average_terminal_pnl_per_portfolio_usd": f"{sum(pnl_values) / Decimal(len(pnl_values)):.2f}",
        "median_terminal_pnl_per_portfolio_usd": f"{median:.2f}",
        "best_terminal_pnl_portfolio": details_by_pnl[-1],
        "lowest_terminal_pnl_portfolio": details_by_pnl[0],
        "individual_portfolios": details,
        "exclusions": ["DXY conversion/weighting", "US10Y/US30Y yield scenarios", "CPI adjustment", "options"],
        "caveat": "Historical hypothetical paper-model output, not actual brokerage execution or account return. The 32-way aggregate assumes distinct capital and gross exposures for every portfolio; costs, financing, margin, taxes, and slippage are not fully modeled.",
    }
    return summary


def write_outputs(portfolios, rows, summary):
    CSV_OUT.parent.mkdir(parents=True, exist_ok=True)
    fields = ["date"]
    for portfolio in portfolios:
        prefix = portfolio["portfolio_id"]
        fields.extend([
            f"{prefix}__pnl_usd",
            f"{prefix}__cumulative_notional_added_usd",
            f"{prefix}__open_notional_usd",
            f"{prefix}__deployed_notional_ratio_pct",
        ])
    fields.extend([
        "aggregate_pnl_usd",
        "aggregate_cumulative_notional_added_usd",
        "aggregate_open_notional_usd",
        "aggregate_deployed_notional_ratio_pct",
    ])
    with CSV_OUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    with JSON_OUT.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2)
        handle.write("\n")


def write_chart(rows, summary):
    CHART_OUT.parent.mkdir(parents=True, exist_ok=True)
    dates = [datetime.strptime(row["date"], "%Y-%m-%d") for row in rows]
    pnl = [float(row["aggregate_pnl_usd"]) for row in rows]
    added = [float(row["aggregate_cumulative_notional_added_usd"]) for row in rows]
    opened = [float(row["aggregate_open_notional_usd"]) for row in rows]
    ratio = [float(row["aggregate_deployed_notional_ratio_pct"]) for row in rows]
    bg, panel, grid = "#0b1220", "#111c2e", "#273449"
    fg, muted, teal, amber, blue = "#f8fafc", "#a8b6ca", "#2dd4bf", "#fbbf24", "#60a5fa"
    fig, axes = plt.subplots(3, 1, figsize=(13.5, 10), sharex=True,
                             gridspec_kw={"height_ratios": [1.3, 1, 0.8]})
    fig.patch.set_facecolor(bg)
    for ax in axes:
        ax.set_facecolor(panel)
        ax.grid(True, color=grid, linewidth=0.75, alpha=0.85)
        ax.set_axisbelow(True)
        ax.tick_params(colors=muted, labelsize=9)
        for spine in ax.spines.values():
            spine.set_color(grid)

    ax = axes[0]
    ax.plot(dates, pnl, color=teal, linewidth=2.5, marker="o", markersize=3.3)
    ax.axhline(0, color=muted, linewidth=1, linestyle="--")
    ax.fill_between(dates, pnl, 0, where=[value >= 0 for value in pnl], color=teal, alpha=0.12)
    ax.set_ylabel("Aggregate modeled PnL (USD)", color=muted)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda value, _: f"${value / 1e6:.1f}M"))
    ax.set_title("THE ONE MODEL — 32-Portfolio Split Strategy (Historical)",
                 color=fg, fontsize=15, fontweight="bold", loc="left", pad=12)
    ax.annotate(f"${pnl[-1]:,.2f}", (dates[-1], pnl[-1]), xytext=(-8, 10),
                textcoords="offset points", color=fg, fontsize=9, fontweight="bold", ha="right")
    peak_date = datetime.strptime(summary["aggregate_max_drawdown_peak_date"], "%Y-%m-%d")
    trough_date = datetime.strptime(summary["aggregate_max_drawdown_trough_date"], "%Y-%m-%d")
    peak_pnl = float(summary["aggregate_max_drawdown_peak_pnl_usd"])
    trough_pnl = float(summary["aggregate_max_drawdown_trough_pnl_usd"])
    ax.scatter([peak_date, trough_date], [peak_pnl, trough_pnl], color=amber, s=24, zorder=5)
    ax.annotate(
        f"Peak-to-trough PnL drawdown ${float(summary['aggregate_max_peak_to_trough_pnl_drawdown_usd']):,.0f}",
        xy=(trough_date, trough_pnl), xytext=(-145, -30), textcoords="offset points",
        color=amber, fontsize=8, ha="right",
        arrowprops={"arrowstyle": "->", "color": amber, "lw": 1.0},
    )

    ax = axes[1]
    ax.plot(dates, added, color=blue, linewidth=2, label="Cumulative gross notional added")
    ax.plot(dates, opened, color=amber, linewidth=1.8, linestyle="--", label="Gross open notional")
    ax.set_ylabel("Gross notional (USD)", color=muted)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda value, _: f"${value / 1e6:.0f}M"))
    ax.legend(facecolor=panel, edgecolor=grid, labelcolor=fg, fontsize=8, loc="upper left")

    ax = axes[2]
    ax.plot(dates, ratio, color=teal, linewidth=2, marker="o", markersize=3)
    ax.set_ylabel("PnL / gross additions (%)", color=muted)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{value:.1f}%"))
    ax.set_xlabel("Session (MST)", color=muted)
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    fig.autofmt_xdate(rotation=0, ha="center")
    fig.text(
        0.5, 0.012,
        "Sep 3–Oct 23, 2026 · 36 sessions · 4×4 Core/1U-EOD pairings, each with and without oil · "
        "independent gross portfolios; no netting · deployed-notional ratio, not account return · costs/execution not fully modeled",
        color=muted, fontsize=7.8, ha="center",
    )
    fig.tight_layout(rect=(0.015, 0.045, 0.99, 0.985))
    fig.savefig(CHART_OUT, dpi=170, facecolor=bg, bbox_inches="tight")
    plt.close(fig)


def main():
    portfolios, rows = build_rows()
    summary = build_summary(portfolios, rows)
    write_outputs(portfolios, rows, summary)
    write_chart(rows, summary)
    print(f"Wrote {CSV_OUT.relative_to(ROOT)}")
    print(f"Wrote {JSON_OUT.relative_to(ROOT)}")
    print(f"Wrote {CHART_OUT.relative_to(ROOT)}")
    print(f"Terminal aggregate PnL: ${Decimal(summary['aggregate_terminal_pnl_usd']):,.2f}")
    print(f"Aggregate deployed-notional ratio: {summary['aggregate_deployed_notional_ratio_pct']}%")


if __name__ == "__main__":
    main()
