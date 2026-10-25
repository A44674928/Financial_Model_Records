#!/usr/bin/env python3
"""Build a lot-level attribution for the core-integrated 50U Weekend Oil entries.

The supplied weekend ZIP contains annotated IG Weekend Oil / US Crude screenshots,
not a complete OHLC series. The user supplied the TradingView opening marks for
BRENT and USOIL on 2026-10-19. This report isolates those tagged lots for
attribution; the entries and target trims are also replayed in all four core
variants and their downstream composites, so this is not an additional overlay.
"""

import csv
import hashlib
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from urllib.parse import quote
from zipfile import ZipFile

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SOURCE_ARCHIVE = ROOT / "Weekend Oil (10-17 & 10-18).zip"
ENERGY_MARKS = DATA / "energy_provider_eod_marks_v1.csv"
OUTPUT_CSV = DATA / "weekend_oil_50u_positions_v1.csv"
REPORT = ROOT / "Weekend Oil 50U Position Hypothetical.md"
CHART_DIR = ROOT / "Charts" / "CLN25" / "Weekend Oil"
CHART = CHART_DIR / "24-weekend-oil-50u-positions.png"
SOURCE_SCREENSHOTS = {
    "2026-10-17": CHART_DIR / "CLN25 Weekend Oil - 2026-10-17.jpeg",
    "2026-10-18": CHART_DIR / "CLN25 Weekend Oil - 2026-10-18.jpeg",
}
INDEX = CHART_DIR / "README.md"

ENTRY_DATE = "2026-10-19"
UNITS_U = Decimal("50")
UNIT_NOTIONAL_USD = Decimal("10000")
CENT = Decimal("0.01")
POSITIONS = {
    "BRENT": {
        "display_ticker": "BRENT",
        "instrument": "BlackBull Markets Brent Cash EOD marks",
        "entry_price": Decimal("111.412"),
        "entry_source": "User-provided TradingView opening mark for 2026-10-19",
        "trim_units_u": Decimal("10"),
        "trim_price": Decimal("117"),
    },
    "OIL": {
        "display_ticker": "USOIL (repository ticker OIL)",
        "instrument": "TradingView TVC:USOIL EOD marks",
        "entry_price": Decimal("99.04"),
        "entry_source": "User-provided TradingView opening mark for 2026-10-19",
        "trim_units_u": Decimal("10"),
        "trim_price": Decimal("102"),
    },
}
SOURCE_URL = "https://github.com/A44674928/Financial_Model_Records/blob/main/Weekend%20Oil%20(10-17%20%26%2010-18).zip"
SOURCE_COMMIT = "b5d6a9a0d9abb84d108c82f312b5298ecf9f437a"
SOURCE_SHA256 = "7419893a19fa1416a5dd238d48cacf17e22187da9b392b54ae50f5093b377c6f"

BG = "#0d131e"
PANEL = "#141c2b"
GRID = "#26344a"
FG = "#edf2f7"
MUTED = "#93a4bd"
COLORS = {"BRENT": "#38bdf8", "OIL": "#fbbf24", "COMBINED": "#f472b6"}


def _money(value):
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


def load_marks():
    marks = {ticker: [] for ticker in POSITIONS}
    with ENERGY_MARKS.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            ticker = row["Ticker"].strip().upper()
            day = row["Date"].strip()
            if ticker not in POSITIONS or day < ENTRY_DATE:
                continue
            close = Decimal(row["EOD_Close"])
            marks[ticker].append({
                "date": day,
                "close": close,
                "source": row["Source"].strip(),
                "instrument": row["Instrument"].strip(),
            })
    for ticker, values in marks.items():
        values.sort(key=lambda item: item["date"])
        if not values or values[0]["date"] != ENTRY_DATE:
            raise ValueError(f"{ticker} is missing the 2026-10-19 EOD mark")
        if values[-1]["date"] != "2026-10-23":
            raise ValueError(f"{ticker} marks must extend through 2026-10-23")
        if len(values) != 5:
            raise ValueError(f"Expected five EOD marks for {ticker} from {ENTRY_DATE} to 2026-10-23")
    if [row["date"] for row in marks["BRENT"]] != [row["date"] for row in marks["OIL"]]:
        raise ValueError("BRENT and USOIL mark dates must align")
    return marks


def build_rows():
    if not SOURCE_ARCHIVE.is_file():
        raise FileNotFoundError(f"Missing supplied source archive: {SOURCE_ARCHIVE}")
    actual_sha = hashlib.sha256(SOURCE_ARCHIVE.read_bytes()).hexdigest()
    if actual_sha != SOURCE_SHA256:
        raise ValueError(f"Weekend Oil source archive SHA-256 mismatch: {actual_sha}")

    marks = load_marks()
    opened_notional = UNITS_U * UNIT_NOTIONAL_USD
    rows = []
    for ticker, details in POSITIONS.items():
        entry = details["entry_price"]
        trim_units = details["trim_units_u"]
        trim_price = details["trim_price"]
        trim_trigger = next((mark for mark in marks[ticker] if mark["close"] >= trim_price), None)
        trim_date = trim_trigger["date"] if trim_trigger else ""
        trim_gross_notional = trim_units * UNIT_NOTIONAL_USD
        trim_realized_pnl = _money(trim_gross_notional * (trim_price / entry - Decimal("1")))

        for session_number, mark in enumerate(marks[ticker], start=1):
            close = mark["close"]
            trim_has_filled = bool(trim_date and mark["date"] >= trim_date)
            sold_units = trim_units if trim_has_filled else Decimal("0")
            open_units = UNITS_U - sold_units
            open_notional = open_units * UNIT_NOTIONAL_USD
            realized_pnl = trim_realized_pnl if trim_has_filled else Decimal("0.00")
            remaining_unrealized_pnl = _money(open_notional * (close / entry - Decimal("1")))
            total_pnl = realized_pnl + remaining_unrealized_pnl
            market_value = _money(open_notional + remaining_unrealized_pnl)
            rows.append({
                "date": mark["date"],
                "ticker": details["display_ticker"],
                "repository_ticker": ticker,
                "side": "LONG",
                "entry_date": ENTRY_DATE,
                "entry_price": f"{entry:f}",
                "entry_price_source": details["entry_source"],
                "opened_units_u": f"{UNITS_U:f}",
                "opened_gross_notional_usd": f"{opened_notional:.2f}",
                "trim_units_u": f"{trim_units:f}",
                "trim_target_price": f"{trim_price:f}",
                "assumed_trim_date": trim_date,
                "units_sold_cumulative_u": f"{sold_units:f}",
                "trim_gross_notional_usd": f"{trim_gross_notional:.2f}" if trim_has_filled else "0.00",
                "realized_pnl_usd": f"{realized_pnl:.2f}",
                "open_units_u": f"{open_units:f}",
                "gross_open_notional_usd": f"{open_notional:.2f}",
                "sessions_marked": str(session_number),
                "eod_close": f"{close:f}",
                "remaining_market_value_usd": f"{market_value:.2f}",
                "remaining_unrealized_pnl_usd": f"{remaining_unrealized_pnl:.2f}",
                "total_realized_plus_unrealized_pnl_usd": f"{total_pnl:.2f}",
                "pnl_to_opening_gross_notional_pct": f"{(total_pnl / opened_notional * Decimal('100')).quantize(Decimal('0.000001'), rounding=ROUND_HALF_UP):.6f}",
                "mark_source": mark["source"],
                "mark_instrument": mark["instrument"],
                "included_in_all_four_core_variants": "yes",
                "attribution_not_additional_overlay": "yes",
            })
    return rows


def write_source_screenshots():
    """File the original CLN25 source screenshots beside the generated attribution chart."""
    CHART_DIR.mkdir(parents=True, exist_ok=True)
    with ZipFile(SOURCE_ARCHIVE) as archive:
        members = [
            name for name in archive.namelist()
            if not name.startswith("__MACOSX/") and name.lower().endswith(".jpeg")
        ]
        for session_date, destination in SOURCE_SCREENSHOTS.items():
            matches = [name for name in members if session_date in name]
            if len(matches) != 1:
                raise ValueError(
                    f"Expected one source screenshot for {session_date}; found {len(matches)}"
                )
            destination.write_bytes(archive.read(matches[0]))
    return list(SOURCE_SCREENSHOTS.values())


def write_index():
    links = [
        "# CLN25 Weekend Oil filing",
        "",
        "Original annotated source screenshots and the generated 50U position attribution chart are grouped here.",
        "",
        "| Date | File |",
        "|---|---|",
    ]
    for session_date, path in SOURCE_SCREENSHOTS.items():
        links.append(f"| {session_date} | [`{path.name}`]({quote(path.name)}) |")
    links.extend([
        f"| Model attribution | [`{CHART.name}`]({quote(CHART.name)}) |",
        "",
        "The two dated JPEGs are source screenshots from the Weekend Oil ZIP, retained as source context; the PNG is a later modeled PnL visualization, not a screenshot or proof of an execution.",
        "",
        f"Source archive: [`{SOURCE_ARCHIVE.name}`](../../../{quote(SOURCE_ARCHIVE.name)}).",
        "",
    ])
    INDEX.write_text("\n".join(links), encoding="utf-8")
    return INDEX


def write_csv(rows):
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return OUTPUT_CSV


def write_chart(rows):
    days = sorted({row["date"] for row in rows})
    by_ticker = {
        ticker: [next(row for row in rows if row["repository_ticker"] == ticker and row["date"] == day)
                 for day in days]
        for ticker in POSITIONS
    }
    combined = [
        sum(Decimal(next(row for row in rows if row["repository_ticker"] == ticker and row["date"] == day)["total_realized_plus_unrealized_pnl_usd"])
            for ticker in POSITIONS)
        for day in days
    ]
    dates = [__import__("datetime").datetime.strptime(day, "%Y-%m-%d") for day in days]

    CHART.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(12.5, 6.8))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(PANEL)
    ax.grid(True, color=GRID, alpha=0.85)
    ax.tick_params(colors=MUTED)
    for spine in ax.spines.values():
        spine.set_color(GRID)
    for ticker, label in (("BRENT", "BRENT total PnL (10U trimmed)"), ("OIL", "USOIL total PnL (10U trimmed)")):
        values = [Decimal(row["total_realized_plus_unrealized_pnl_usd"]) for row in by_ticker[ticker]]
        ax.plot(dates, [float(value) for value in values], marker="o", linewidth=2.3,
                color=COLORS[ticker], label=label)
    ax.plot(dates, [float(value) for value in combined], marker="o", linewidth=2.5,
            color=COLORS["COMBINED"], label="Combined realized + open PnL")
    ax.axhline(0, color=MUTED, linewidth=1, linestyle="--")
    ax.set_ylabel("Modeled PnL: realized + unrealized (USD)", color=FG)
    ax.set_xlabel("TradingView EOD session (MST)", color=FG)
    ax.set_xticks(dates)
    ax.set_xticklabels([day.strftime("%b %d") for day in dates], color=MUTED)
    ax.set_title("Core-Integrated Weekend Oil — 50U Long Each; Trim 10U at Targets", color=FG, loc="left", fontsize=15, pad=14)
    ax.legend(facecolor=BG, edgecolor=GRID, labelcolor=FG)
    terminal = combined[-1]
    ax.annotate(f"Oct 23 combined: ${terminal:,.2f}", (dates[-1], float(terminal)),
                xytext=(-175, 18), textcoords="offset points", color=FG,
                arrowprops={"arrowstyle": "->", "color": MUTED})
    fig.text(0.5, 0.015,
             "Integrated in all four core variants; attribution only, not an extra overlay · assumed 10U trims on first EOD mark at/above target · intraday touch/fill unverified",
             ha="center", color=MUTED, fontsize=8.5)
    fig.tight_layout(rect=(0.02, 0.06, 0.99, 0.98))
    fig.savefig(CHART, dpi=160, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close(fig)
    return CHART


def write_report(rows):
    lines = [
        "# Weekend Oil 50U Position Hypothetical — Core-Integrated Attribution",
        "",
        "> **Hypothetical educational mark-to-market only.** These tagged entries and assumed partial exits are modeled paper trades, not broker executions, verified account returns, or recommendations. Costs, financing, slippage, and liquidation are not modeled.",
        "",
        "> **Core scope:** The two new 50U entries and their 10U target trims are integrated in all four core variants and flow through their downstream model outputs. This report isolates the new lots for attribution; it is **not an additional overlay** and must not be added again to core or aggregate results. The pre-existing Oct. 19 1U BRENT and 1U OIL core lots remain separate and untouched by these trims.",
        "",
        "## Position and trim assumptions",
        "",
        "The user specified a **50U LONG** position each in BRENT and USOIL at the **2026-10-19 market open**, with entry marks of $111.412 and $99.04 respectively. The thesis instruction is modeled as selling **10U of BRENT at $117** and **10U of USOIL at $102**, leaving **40U open in each new lot** after the assumed trims. Each ticker also retains its separate original 1U core lot. At $10,000 notional per unit, the new entries open $1,000,000 total gross notional; $200,000 of unit-basis gross notional is trimmed and $800,000 remains open in the new lots."
        "",
        "| Instrument | Entry price | Trim instruction | Modeled trigger session | Realized PnL on 10U sale | Oct. 23 EOD mark | Remaining 40U unrealized PnL | Total realized + unrealized PnL | Remaining gross open notional |",
        "|---|---:|---|---|---:|---:|---:|---:|---:|",
    ]
    terminal_by_ticker = {}
    for ticker, details in POSITIONS.items():
        ticker_rows = [row for row in rows if row["repository_ticker"] == ticker]
        last = ticker_rows[-1]
        terminal_by_ticker[ticker] = {
            "realized": Decimal(last["realized_pnl_usd"]),
            "unrealized": Decimal(last["remaining_unrealized_pnl_usd"]),
            "total": Decimal(last["total_realized_plus_unrealized_pnl_usd"]),
            "open_notional": Decimal(last["gross_open_notional_usd"]),
        }
        entry_display = f"${details['entry_price']:,.3f}".rstrip("0").rstrip(".")
        trim_display = f"${details['trim_price']:,.3f}".rstrip("0").rstrip(".")
        mark_display = f"${Decimal(last['eod_close']):,.3f}".rstrip("0").rstrip(".")
        lines.append(
            f"| {details['display_ticker']} | {entry_display} | Sell 10U at {trim_display} | {last['assumed_trim_date']} | "
            f"${terminal_by_ticker[ticker]['realized']:+,.2f} | {mark_display} | "
            f"${terminal_by_ticker[ticker]['unrealized']:+,.2f} | ${terminal_by_ticker[ticker]['total']:+,.2f} | "
            f"${terminal_by_ticker[ticker]['open_notional']:,.2f} |"
        )
    combined_realized = sum((v["realized"] for v in terminal_by_ticker.values()), Decimal("0"))
    combined_unrealized = sum((v["unrealized"] for v in terminal_by_ticker.values()), Decimal("0"))
    combined_total = combined_realized + combined_unrealized
    combined_ratio = (combined_total / (UNITS_U * UNIT_NOTIONAL_USD * 2) * 100).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
    lines.extend([
        f"| **Combined** | — | **Sell 20U total** | **2026-10-23 assumed** | **${combined_realized:+,.2f}** | — | **${combined_unrealized:+,.2f}** | **${combined_total:+,.2f}** | **$800,000.00** |",
        "",
        f"The combined realized PnL is **${combined_realized:,.2f}**; the remaining open positions carry **${combined_unrealized:,.2f}** unrealized PnL at the Oct. 23 marks. Total modeled PnL is **${combined_total:,.2f}**, or {combined_ratio:.4f}% of the original $1,000,000 gross notional—not an account return.",
        "",
        "## Session marks and PnL",
        "",
        "For the open portion, PnL is `open gross notional × (EOD close ÷ entry price − 1)`. When an EOD mark first equals or exceeds its trim target, the model assumes the specified 10U sale occurred at the target price, realizes that tranche's PnL, and marks the remaining 40U at the session close. Available daily data are closes only: Oct. 23 is the first recorded EOD at/above either target, so the report assigns that modeled trigger session. It does **not** verify the intraday touch, fill time, or actual execution at the target.",
        "",
        "| EOD date | Instrument | EOD close | Units sold cumulative | Units open | Realized PnL | Remaining unrealized PnL | Total PnL | Mark source |",
        "|---|---|---:|---:|---:|---:|---:|---:|---|",
    ])
    for row in rows:
        close = Decimal(row["eod_close"])
        lines.append(
            f"| {row['date']} | {row['ticker']} | ${close:,.3f} | {Decimal(row['units_sold_cumulative_u']):g}U | "
            f"{Decimal(row['open_units_u']):g}U | ${Decimal(row['realized_pnl_usd']):+,.2f} | "
            f"${Decimal(row['remaining_unrealized_pnl_usd']):+,.2f} | "
            f"${Decimal(row['total_realized_plus_unrealized_pnl_usd']):+,.2f} | {row['mark_source']} |"
        )
    lines.extend([
        "",
        f"![50U long BRENT and USOIL positions with assumed 10U trims](Charts/CLN25/Weekend%20Oil/{CHART.name})",
        "",
        f"Session-level export: [`{OUTPUT_CSV.name}`](data/{OUTPUT_CSV.name}).",
        "",
        "## Source and scope notes",
        "",
        f"- Weekend source archive: [`{SOURCE_ARCHIVE.name}`]({quote(SOURCE_ARCHIVE.name)}); [upstream GitHub file]({SOURCE_URL}) at commit `{SOURCE_COMMIT}`; SHA-256 `{SOURCE_SHA256}`.",
        "- The archive contains two annotated IG **Weekend Oil – US Crude (CLN25)** screenshots dated Oct. 17 and Oct. 18, not a complete OHLC history and not separate BRENT/USOIL Monday-open price files. The screenshots are retained as source context, not transcribed as daily marks.",
        "- The two Oct. 19 open prices, BRENT $111.412 and USOIL $99.04, and the trim levels/size were provided by the user. BRENT is stored internally as `BRENT`; USOIL maps to repository ticker `OIL`.",
        "- Subsequent EOD values come from [`energy_provider_eod_marks_v1.csv`](data/energy_provider_eod_marks_v1.csv): BlackBull Markets Brent Cash for BRENT and TradingView TVC:USOIL for OIL. No new or external daily prices are inserted.",
        "- The tagged entries/trim are recorded in [`trades/BRENT.txt`](trades/BRENT.txt) and [`trades/OIL.txt`](trades/OIL.txt), integrated in all four core variants, and therefore flow once through downstream core-based outputs, including THE ONE MODEL's 32-book aggregate. This document and CSV are a lot-level attribution only, not a second position allocation.",
        "- The first recorded EOD marks at/above the target are dated 2026-10-23. The daily-close source cannot establish an intraday touch or actual fill; the target execution is an explicit model assumption.",
        "- PnL excludes commissions, spread, slippage, financing, CFD contract multipliers/tracking differences, taxes, margin, and execution constraints. The percentage shown is measured against opening gross notional, not account equity.",
        "",
    ])
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    return REPORT


def main():
    rows = build_rows()
    write_csv(rows)
    screenshots = write_source_screenshots()
    chart = write_chart(rows)
    report = write_report(rows)
    index = write_index()
    print(f"Wrote {OUTPUT_CSV.relative_to(ROOT)} ({len(rows)} rows)")
    for screenshot in screenshots:
        print(f"Filed {screenshot.relative_to(ROOT)}")
    print(f"Wrote {chart.relative_to(ROOT)}")
    print(f"Wrote {index.relative_to(ROOT)}")
    print(f"Wrote {report.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
