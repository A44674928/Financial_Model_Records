"""Build a separate daily EOD accumulation hypothetical for Brent and USOIL.

For each exact user-supplied energy EOD, the hypothetical buys 10 units at that
close (one 1U lot) and holds all daily lots through Oct. 23. The
logged chart positions are shown separately and in the combined energy subtotal.
This sidecar is intentionally excluded from the four core strategy/DXY account
bases because it is a separate hypothetical capital deployment.
"""

import csv
from collections import defaultdict
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from model_perf_core import UNIT, SESSION_DATES, build_lots, parse_trades

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
CHARTS = ROOT / "Charts" / "performance"
INPUT = DATA / "energy_provider_eod_marks_v1.csv"
OUTPUT = DATA / "oil_desk_eod_accumulation_v1.csv"
REPORT = ROOT / "Oil Desk EOD Accumulation Hypothetical.md"
GRAPH = CHARTS / "19-oil-desk-daily-accumulation.png"
DAILY_UNITS = 10
TICKERS = ("BRENT", "OIL")
COLORS = {"BRENT": "#38bdf8", "OIL": "#fbbf24"}


def load_energy_marks():
    marks = defaultdict(dict)
    with INPUT.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        required = {"Date", "Ticker", "EOD_Close", "Source", "Instrument"}
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise ValueError(f"{INPUT.name} must contain {sorted(required)}")
        for row in reader:
            ticker = row["Ticker"].strip().upper()
            day = row["Date"].strip()
            close = float(row["EOD_Close"])
            if ticker not in TICKERS or day not in SESSION_DATES or close <= 0:
                raise ValueError(f"Invalid energy benchmark row: {row}")
            if day in marks[ticker]:
                raise ValueError(f"Duplicate {ticker} mark on {day}")
            marks[ticker][day] = {"close": close, "source": row["Source"].strip(), "instrument": row["Instrument"].strip()}
    starts = {"BRENT": "2026-09-23", "OIL": "2026-09-10"}
    for ticker, start in starts.items():
        expected = [day for day in SESSION_DATES if day >= start]
        if sorted(marks[ticker]) != expected:
            raise ValueError(f"{ticker} marks must cover {start} through {SESSION_DATES[-1]} without gaps")
    return marks


def build_rows(marks=None):
    marks = marks or load_energy_marks()
    events = parse_trades()
    chart_lots, _ = build_lots("V1", events)
    chart_lots = [lot for lot in chart_lots if lot["sym"] in TICKERS]
    rows = []
    for ticker in TICKERS:
        cumulative_daily_pnl = 0.0
        cumulative_units = 0
        cumulative_notional = 0.0
        for day in SESSION_DATES:
            if day not in marks[ticker]:
                continue
            mark = marks[ticker][day]["close"]
            # A new EOD lot is bought at today's mark, so it has zero PnL at
            # today's close and starts participating in the next session.
            cumulative_units += DAILY_UNITS
            cumulative_notional += DAILY_UNITS * UNIT
            cumulative_daily_pnl = sum(
                DAILY_UNITS * UNIT * (mark / marks[ticker][entry_day]["close"] - 1.0)
                for entry_day in SESSION_DATES
                if entry_day in marks[ticker] and entry_day <= day
            )
            daily_market_value = cumulative_notional + cumulative_daily_pnl
            chart_open = [
                lot for lot in chart_lots
                if lot["sym"] == ticker and lot["open"] and lot["entry_date"] <= day
            ]
            chart_pnl = sum(
                lot["qty"] * UNIT * (mark / lot["entry_px"] - 1.0)
                * (1 if lot["side"] == "long" else -1)
                for lot in chart_open
            )
            chart_units = sum(lot["qty"] for lot in chart_open)
            rows.append({
                "date": day,
                "ticker": ticker,
                "instrument": marks[ticker][day]["instrument"],
                "eod_close": f"{mark:.3f}".rstrip("0").rstrip("."),
                "daily_buy_units": DAILY_UNITS,
                "cumulative_daily_buy_units": cumulative_units,
                "cumulative_daily_buy_notional_usd": f"{cumulative_notional:.2f}",
                "daily_buys_market_value_usd": f"{daily_market_value:.2f}",
                "daily_buys_unrealized_pnl_usd": f"{cumulative_daily_pnl:.2f}",
                "chart_open_units": f"{chart_units:g}",
                "chart_positions_unrealized_pnl_usd": f"{chart_pnl:.2f}",
                "combined_energy_unrealized_pnl_usd": f"{cumulative_daily_pnl + chart_pnl:.2f}",
                "source": marks[ticker][day]["source"],
            })
    return rows


def write_csv(rows=None):
    rows = rows or build_rows()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return OUTPUT


def write_chart(rows=None):
    rows = rows or build_rows()
    CHARTS.mkdir(parents=True, exist_ok=True)
    by_ticker = {ticker: [row for row in rows if row["ticker"] == ticker] for ticker in TICKERS}
    fig, axes = plt.subplots(2, 1, figsize=(13, 8), sharex=False)
    fig.patch.set_facecolor("#0d131e")
    for ax, ticker in zip(axes, TICKERS):
        data = by_ticker[ticker]
        dates = [row["date"] for row in data]
        ax.set_facecolor("#141c2b")
        ax.grid(True, color="#26344a", alpha=0.8)
        ax.tick_params(colors="#93a4bd")
        for spine in ax.spines.values():
            spine.set_color("#26344a")
        ax.plot(dates, [float(r["daily_buys_unrealized_pnl_usd"]) for r in data],
                color=COLORS[ticker], linewidth=2, label="10-unit EOD buys only")
        ax.plot(dates, [float(r["chart_positions_unrealized_pnl_usd"]) for r in data],
                color="#a78bfa", linewidth=1.8, linestyle="--", label="Chart-opened positions")
        ax.plot(dates, [float(r["combined_energy_unrealized_pnl_usd"]) for r in data],
                color="#f8fafc", linewidth=1.8, label="Combined")
        ax.axhline(0, color="#93a4bd", linewidth=0.8)
        ax.set_title(f"{ticker} — daily EOD accumulation and chart positions", color="#edf2f7", loc="left")
        ax.set_ylabel("Unrealized PnL (USD)", color="#edf2f7")
        ax.tick_params(axis="x", rotation=25)
        ax.legend(facecolor="#0d131e", edgecolor="#26344a", labelcolor="#edf2f7", fontsize=8)
    axes[-1].set_xlabel("EOD session date", color="#edf2f7")
    fig.suptitle("Oil Desk Hypothetical — 10 Units Bought at Each EOD", color="#edf2f7", fontsize=15)
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    fig.savefig(GRAPH, dpi=150, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close(fig)
    return GRAPH


def write_report(rows=None):
    rows = rows or build_rows()
    write_csv(rows)
    write_chart(rows)
    lines = [
        "# Oil Desk EOD Accumulation Hypothetical",
        "",
        "A separate sidecar model layered on top of the existing chart-opened Brent and TVC:USOIL positions. It does not alter the four core strategy definitions or their DXY/yield account bases.",
        "",
        "For the daily position and PnL methodology across all variants and sidecars, see [`Model Calculation Guide.md`](Model%20Calculation%20Guide.md).",
        "",
        "## Assumptions",
        "",
        f"- Buy **{DAILY_UNITS} units ({DAILY_UNITS}U; $100,000 notional)** in each instrument at every supplied EOD session.",
        "- One new long lot is opened at each session's EOD close and remains open through Oct. 23; no exits, fees, financing, or scaling from PnL.",
        "- The daily buy at a given close starts accruing PnL after that close; therefore it has zero mark-to-market PnL at its purchase EOD.",
        "- Chart-opened positions are shown separately and then added to the daily-buy hypothetical for a combined energy subtotal.",
        "- The supplied benchmark series are exact user-provided BlackBull Brent Cash and TradingView TVC:USOIL EOD marks over the active-position periods. Pre-entry context remains proxy data and is not used to mark these lots.",
        "",
        "## Terminal summary — Oct. 23, 2026",
        "",
        "| Instrument | EOD sessions | Daily-buy units | Daily-buy notional | Daily-buy PnL | Chart units | Chart-position PnL | Combined energy PnL |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    marks = load_energy_marks()
    chart_lots, _ = build_lots("V1", parse_trades())
    total_sessions = total_daily_units = total_chart_units = 0
    total_daily_notional = Decimal("0")
    total_daily_pnl = Decimal("0")
    total_chart_pnl = Decimal("0")
    for ticker in TICKERS:
        terminal = next(row for row in reversed(rows) if row["ticker"] == ticker)
        sessions = sum(row["ticker"] == ticker for row in rows)
        lines.append(
            f"| {ticker} | {sessions} | {terminal['cumulative_daily_buy_units']} | "
            f"${float(terminal['cumulative_daily_buy_notional_usd']):,.2f} | "
            f"${float(terminal['daily_buys_unrealized_pnl_usd']):+,.2f} | "
            f"{terminal['chart_open_units']} | ${float(terminal['chart_positions_unrealized_pnl_usd']):+,.2f} | "
            f"${float(terminal['combined_energy_unrealized_pnl_usd']):+,.2f} |"
        )
        final_close = Decimal(str(marks[ticker][SESSION_DATES[-1]]["close"]))
        total_sessions += sessions
        total_daily_units += int(terminal["cumulative_daily_buy_units"])
        total_daily_notional += Decimal(terminal["cumulative_daily_buy_notional_usd"])
        total_daily_pnl += sum((
            Decimal(DAILY_UNITS * UNIT)
            * (final_close / Decimal(str(marks[ticker][day]["close"])) - 1)
            for day in SESSION_DATES if day in marks[ticker]
        ), Decimal("0"))
        open_chart_lots = [lot for lot in chart_lots if lot["sym"] == ticker and lot["open"]]
        total_chart_units += sum(int(lot["qty"]) for lot in open_chart_lots)
        total_chart_pnl += sum((
            Decimal(str(lot["qty"])) * Decimal(UNIT)
            * (final_close / Decimal(str(lot["entry_px"])) - 1)
            * (Decimal(1) if lot["side"] == "long" else Decimal(-1))
            for lot in open_chart_lots
        ), Decimal("0"))
    cent = Decimal("0.01")
    total_daily_pnl = total_daily_pnl.quantize(cent, rounding=ROUND_HALF_UP)
    total_chart_pnl = total_chart_pnl.quantize(cent, rounding=ROUND_HALF_UP)
    total_combined_pnl = (total_daily_pnl + total_chart_pnl).quantize(cent, rounding=ROUND_HALF_UP)
    lines.append(
        f"| **All energy** | {total_sessions} | {total_daily_units} | "
        f"${total_daily_notional:,.2f} | ${total_daily_pnl:+,.2f} | {total_chart_units} | "
        f"${total_chart_pnl:+,.2f} | ${total_combined_pnl:+,.2f} |"
    )
    lines.extend([
        "",
        f"![Daily EOD accumulation and chart positions]({GRAPH.relative_to(ROOT).as_posix()})",
        "",
        f"Session-level lots and PnL: [`{OUTPUT.name}`](data/{OUTPUT.name}).",
        "",
        "Energy source rows: [`energy_provider_eod_marks_v1.csv`](data/energy_provider_eod_marks_v1.csv). Active source map: [`active_price_source_registry_v2.csv`](data/active_price_source_registry_v2.csv).",
        "",
        "This hypothetical is not combined into the main portfolio DXY/yield multiplier views because it has its own daily capital deployment schedule. Applying those factors to the sidecar requires a separate account-capital convention.",
    ])
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return REPORT


def main():
    rows = build_rows()
    report = write_report(rows)
    print(f"Wrote {OUTPUT.relative_to(ROOT)}")
    print(f"Wrote {GRAPH.relative_to(ROOT)}")
    print(f"Wrote {report.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
