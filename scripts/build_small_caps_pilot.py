"""Build the LCID Small Caps Buyout & Reorganization Offering pilot report."""

import csv
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from model_perf_core import ROOT, UNIT, parse_trades  # noqa: E402

DATA = ROOT / "data"
MARK_FILE = DATA / "lcid_small_caps_pilot_daily_marks.csv"
TRADE_LOG = ROOT / "trades" / "LCID.txt"
REPORT = ROOT / "Small Caps [Buyout & Reorganization Offering Test Pilot].md"
DAILY_CSV = DATA / "lcid_small_caps_pilot_daily_pnl.csv"
CHART = ROOT / "Charts" / "performance" / "18-lcid-small-caps-pilot-pnl.png"
TITLE = "Small Caps [Buyout & Reorganization Offering Test Pilot]"

BG = "#0d131e"
PANEL = "#141c2b"
GRID = "#26344a"
FG = "#edf2f7"
MUTED = "#93a4bd"
GREEN = "#34d399"
GOLD = "#fbbf24"


def load_marks():
    marks = {}
    with MARK_FILE.open(newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            day = row["Date"].strip()
            if day in marks:
                raise ValueError(f"Duplicate LCID mark for {day}")
            marks[day] = float(row["Close"])
    if not marks:
        raise ValueError("No LCID pilot marks supplied")
    if list(marks) != sorted(marks):
        raise ValueError("LCID pilot marks must be in ascending date order")
    return marks


def pilot_daily_series():
    marks = load_marks()
    entries = [event for event in parse_trades() if event["sym"] == "LCID"]
    entries.sort(key=lambda event: (event["date"], event["time"], event["order"]))
    if len(entries) != 5:
        raise ValueError(f"Expected five LCID pilot entries; found {len(entries)}")
    if any(event["tag"] != "LONG" or event["kind"] != "entry" for event in entries):
        raise ValueError("LCID pilot currently expects LONG entry events only")

    rows = []
    for day, mark in marks.items():
        active = [event for event in entries if event["date"] <= day]
        notional = sum(event["units"] * UNIT for event in active)
        pnl = sum(
            event["units"] * UNIT * (mark / event["px"] - 1.0)
            for event in active
        )
        rows.append({
            "date": day,
            "lcid_mark_usd": mark,
            "entries_active": len(active),
            "units_open": sum(event["units"] for event in active),
            "deployed_notional_usd": notional,
            "unrealized_pnl_usd": pnl,
            "return_on_deployed_pct": (100.0 * pnl / notional) if notional else 0.0,
        })
    return entries, rows


def write_daily_csv(rows):
    fields = [
        "date", "lcid_mark_usd", "entries_active", "units_open",
        "deployed_notional_usd", "unrealized_pnl_usd", "return_on_deployed_pct",
    ]
    with DAILY_CSV.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def make_chart(rows):
    import matplotlib.dates as mdates
    import matplotlib.pyplot as plt
    from matplotlib.ticker import FuncFormatter

    CHART.parent.mkdir(parents=True, exist_ok=True)
    dates = [date.fromisoformat(row["date"]) for row in rows]
    pnls = [row["unrealized_pnl_usd"] for row in rows]
    marks = [row["lcid_mark_usd"] for row in rows]
    fig, ax = plt.subplots(figsize=(11.5, 6.5))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(PANEL)
    ax.grid(True, color=GRID, alpha=0.75, linewidth=0.7)
    ax.tick_params(colors=MUTED, labelsize=9)
    for side in ("bottom", "left", "top", "right"):
        ax.spines[side].set_color(GRID)
    ax.plot(dates, pnls, marker="o", color=GREEN, lw=2.5, label="Pilot basket unrealized PnL (USD)")
    ax.axhline(0, color=MUTED, lw=0.8, ls="--")
    ax.set_ylabel("Open basket PnL (USD)", color=FG)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda value, _: f"${value/1000:,.1f}k"))
    ax.set_title(TITLE, color=FG, fontsize=15, pad=13)
    ax2 = ax.twinx()
    ax2.plot(dates, marks, marker="s", color=GOLD, lw=2.0, ls=(0, (5, 3)), label="User-provided daily LCID mark")
    ax2.set_ylabel("LCID mark ($/share)", color=GOLD)
    ax2.tick_params(axis="y", colors=GOLD, labelsize=9)
    ax2.spines["right"].set_color(GOLD)
    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    legend = ax.legend(h1 + h2, l1 + l2, loc="upper left", frameon=True, fontsize=9)
    legend.get_frame().set_facecolor(BG)
    legend.get_frame().set_edgecolor(GRID)
    for text in legend.get_texts():
        text.set_color(FG)
    ax.set_xticks(dates)
    ax.set_xlim(dates[0], dates[-1])
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%-m/%-d"))
    ax.tick_params(axis="x", rotation=25)
    ax.set_xlabel("Session close (Arizona / MST)", color=FG)
    fig.text(
        0.5, 0.012,
        "Each entry is a separate $10,000 LONG. Daily PnL marks the active basket to the supplied daily mark.",
        color=MUTED, ha="center", fontsize=9,
    )
    fig.tight_layout(rect=(0.02, 0.04, 0.98, 0.99))
    fig.savefig(CHART, dpi=160, facecolor=BG, bbox_inches="tight")
    plt.close(fig)


def write_report(entries, rows):
    oct22 = next(row for row in rows if row["date"] == "2026-10-22")
    terminal = rows[-1]
    lines = [
        f"# {TITLE}",
        "",
        "A separate small-cap pilot book for five user-specified LCID LONG entries. All five entries are $10,000 each (five standard units, $50,000 total after Oct. 23). The current four-model daily replay now includes all five entries through the Oct. 23 EOD close; the Oct. 22 historical comparison remains available as an earlier row in the daily exports.",
        "",
        "## Pilot Basket",
        "",
        "| Date | Side | Entry | Notional |",
        "|---|---|---:|---:|",
    ]
    for event in entries:
        lines.append(
            f"| {event['date']} | LONG | ${event['px']:.2f} | ${event['units'] * UNIT:,.0f} |"
        )
    lines.extend([
        "",
        "## User-Provided Daily Marks and Basket PnL",
        "",
        "![LCID small-caps pilot daily PnL and marks](Charts/performance/18-lcid-small-caps-pilot-pnl.png)",
        "",
        "| Date | Daily mark | Active entries | Deployed | Open PnL | Return on deployed |",
        "|---|---:|---:|---:|---:|---:|",
    ])
    for row in rows:
        lines.append(
            f"| {row['date']} | ${row['lcid_mark_usd']:.2f} | {row['entries_active']} | "
            f"${row['deployed_notional_usd']:,.0f} | ${row['unrealized_pnl_usd']:+,.2f} | "
            f"{row['return_on_deployed_pct']:+.3f}% |"
        )
    lines.extend([
        "",
        f"- At the Oct. 22 historical comparison cutoff, four entries are active: **${oct22['deployed_notional_usd']:,.0f} deployed**, marked at **${oct22['lcid_mark_usd']:.2f}**, with **${oct22['unrealized_pnl_usd']:+,.2f}** open PnL.",
        f"- The Oct. 23 EOD view includes all five entries: **${terminal['deployed_notional_usd']:,.0f} deployed**, marked at **${terminal['lcid_mark_usd']:.2f}**, with **${terminal['unrealized_pnl_usd']:+,.2f}** open PnL. This is the LCID mark used in the current four-model daily replay.",
        "- The four model variants have the same LCID contribution because the pilot contains LONG entries only; this adds exposure and PnL but does not alter the variants' relative LCID path.",
        "- Daily marks `$3.27`, `$3.21`, `$3.46`, and `$3.55` map in order to Oct. 20, 21, 22, and 23, as supplied. They are kept separately from the five entry fills in `trades/LCID.txt`.",
        "- Entry fills use the user's provided prices; PnL is `notional × (daily mark / entry price − 1)`. No commissions or other costs are included.",
        "",
        f"Daily export: [`{DAILY_CSV.name}`](data/{DAILY_CSV.name}).",
        "",
        "Ledger: [`trades/LCID.txt`](trades/LCID.txt).",
        "",
        "Main comparison: [`Model Performance Comparison.md`](Model%20Performance%20Comparison.md).",
        "",
    ])
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def main():
    entries, rows = pilot_daily_series()
    write_daily_csv(rows)
    make_chart(rows)
    write_report(entries, rows)
    print(f"Wrote {REPORT.relative_to(ROOT)}")
    print(f"Wrote {DAILY_CSV.relative_to(ROOT)}")
    print(f"Wrote {CHART.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
