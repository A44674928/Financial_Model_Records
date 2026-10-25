#!/usr/bin/env python3
"""Build a standalone 50U long-position hypothetical from the Weekend Oil input.

The supplied weekend ZIP contains annotated IG Weekend Oil / US Crude screenshots,
not a complete OHLC series. The user supplied the separate TradingView opening
marks for BRENT and USOIL on 2026-10-19. Positions are marked thereafter using
the repository's existing energy EOD marks; this overlay is not added to core,
THE ONE MODEL, or the standard energy sidecar composites.
"""

import csv
import hashlib
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from urllib.parse import quote

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SOURCE_ARCHIVE = ROOT / "Weekend Oil (10-17 & 10-18).zip"
ENERGY_MARKS = DATA / "energy_provider_eod_marks_v1.csv"
OUTPUT_CSV = DATA / "weekend_oil_50u_positions_v1.csv"
REPORT = ROOT / "Weekend Oil 50U Position Hypothetical.md"
CHART = ROOT / "Charts" / "performance" / "24-weekend-oil-50u-positions.png"

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
    },
    "OIL": {
        "display_ticker": "USOIL (repository ticker OIL)",
        "instrument": "TradingView TVC:USOIL EOD marks",
        "entry_price": Decimal("99.04"),
        "entry_source": "User-provided TradingView opening mark for 2026-10-19",
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
    gross_notional = UNITS_U * UNIT_NOTIONAL_USD
    rows = []
    for ticker, details in POSITIONS.items():
        entry = details["entry_price"]
        for session_number, mark in enumerate(marks[ticker], start=1):
            close = mark["close"]
            pnl = _money(gross_notional * (close / entry - Decimal("1")))
            market_value = _money(gross_notional + pnl)
            rows.append({
                "date": mark["date"],
                "ticker": details["display_ticker"],
                "repository_ticker": ticker,
                "side": "LONG",
                "entry_date": ENTRY_DATE,
                "entry_price": f"{entry:f}",
                "entry_price_source": details["entry_source"],
                "unit_size_u": f"{UNITS_U:f}",
                "unit_notional_usd": f"{UNIT_NOTIONAL_USD:f}",
                "gross_notional_usd": f"{gross_notional:.2f}",
                "sessions_marked": str(session_number),
                "eod_close": f"{close:f}",
                "market_value_usd": f"{market_value:.2f}",
                "unrealized_pnl_usd": f"{pnl:.2f}",
                "pnl_to_gross_notional_pct": f"{(pnl / gross_notional * Decimal('100')).quantize(Decimal('0.000001'), rounding=ROUND_HALF_UP):.6f}",
                "mark_source": mark["source"],
                "mark_instrument": mark["instrument"],
            })
    return rows


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
        sum(Decimal(next(row for row in rows if row["repository_ticker"] == ticker and row["date"] == day)["unrealized_pnl_usd"])
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
    for ticker, label in (("BRENT", "BRENT 50U long"), ("OIL", "USOIL 50U long")):
        values = [Decimal(row["unrealized_pnl_usd"]) for row in by_ticker[ticker]]
        ax.plot(dates, [float(value) for value in values], marker="o", linewidth=2.3,
                color=COLORS[ticker], label=label)
    ax.plot(dates, [float(value) for value in combined], marker="o", linewidth=2.5,
            color=COLORS["COMBINED"], label="Combined 100U positions")
    ax.axhline(0, color=MUTED, linewidth=1, linestyle="--")
    ax.set_ylabel("Unrealized modeled PnL (USD)", color=FG)
    ax.set_xlabel("TradingView EOD session (MST)", color=FG)
    ax.set_xticks(dates)
    ax.set_xticklabels([day.strftime("%b %d") for day in dates], color=MUTED)
    ax.set_title("Weekend Oil — 50U Long BRENT + 50U Long USOIL", color=FG, loc="left", fontsize=15, pad=14)
    ax.legend(facecolor=BG, edgecolor=GRID, labelcolor=FG)
    terminal = combined[-1]
    ax.annotate(f"Oct 23 combined: ${terminal:,.2f}", (dates[-1], float(terminal)),
                xytext=(-175, 18), textcoords="offset points", color=FG,
                arrowprops={"arrowstyle": "->", "color": MUTED})
    fig.text(0.5, 0.015,
             "Hypothetical open-price marks supplied by user; exact supplied EOD marks thereafter · gross notional $1,000,000 · costs/execution not modeled",
             ha="center", color=MUTED, fontsize=8.5)
    fig.tight_layout(rect=(0.02, 0.06, 0.99, 0.98))
    fig.savefig(CHART, dpi=160, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close(fig)
    return CHART


def write_report(rows):
    lines = [
        "# Weekend Oil 50U Position Hypothetical",
        "",
        "> **Hypothetical educational mark-to-market only.** These are not broker executions, a verified account return, or a recommendation. Both assumed positions remain open through the latest supplied EOD marks, with no costs, financing, slippage, or liquidation modeled.",
        "",
        "## Position assumptions",
        "",
        "The user requested one **50U LONG** position in BRENT and one **50U LONG** position in USOIL, opened at the **2026-10-19 market open**. Under the repository convention of 1U = $10,000 notional, each position starts at $500,000 gross notional; combined gross notional is $1,000,000.",
        "",
        "| Instrument | Internal ticker | Side / size | Assumed 2026-10-19 open | Entry-mark source | Daily EOD mark source | Oct. 23 EOD mark | Oct. 23 unrealized PnL | PnL ÷ gross notional |",
        "|---|---|---:|---:|---|---|---:|---:|---:|",
    ]
    terminal_by_ticker = {}
    for ticker, details in POSITIONS.items():
        ticker_rows = [row for row in rows if row["repository_ticker"] == ticker]
        last = ticker_rows[-1]
        terminal_by_ticker[ticker] = Decimal(last["unrealized_pnl_usd"])
        entry_display = f"${details['entry_price']:,.3f}".rstrip("0").rstrip(".")
        mark_display = f"${Decimal(last['eod_close']):,.3f}".rstrip("0").rstrip(".")
        lines.append(
            f"| {details['display_ticker']} | `{ticker}` | 50U LONG | {entry_display} | User-provided TradingView open | "
            f"{last['mark_source']} | {mark_display} | ${Decimal(last['unrealized_pnl_usd']):+,.2f} | "
            f"{Decimal(last['pnl_to_gross_notional_pct']):.4f}% |"
        )
    combined = sum(terminal_by_ticker.values(), Decimal("0"))
    lines.extend([
        f"| **Combined** | — | **100U LONG** | — | — | — | — | **${combined:+,.2f}** | **{(combined / (UNITS_U * UNIT_NOTIONAL_USD * 2) * 100).quantize(Decimal('0.0001'), rounding=ROUND_HALF_UP):.4f}%** |",
        "",
        "## Session marks and PnL",
        "",
        "PnL is marked using `gross notional × (EOD close ÷ assumed open − 1)`. Both positions are long and remain open. The Oct. 19 result is the first EOD mark after the assumed opening; it is not zero-PnL because the entry prices are the separately supplied market-open marks.",
        "",
        "| EOD date | Instrument | EOD close | Gross notional | Unrealized PnL | PnL / gross notional | Mark source |",
        "|---|---|---:|---:|---:|---:|---|",
    ])
    for row in rows:
        close = Decimal(row["eod_close"])
        lines.append(
            f"| {row['date']} | {row['ticker']} | ${close:,.3f} | ${Decimal(row['gross_notional_usd']):,.2f} | "
            f"${Decimal(row['unrealized_pnl_usd']):+,.2f} | {Decimal(row['pnl_to_gross_notional_pct']):.4f}% | {row['mark_source']} |"
        )
    lines.extend([
        "",
        f"![50U long BRENT and 50U long USOIL hypothetical PnL](Charts/performance/{CHART.name})",
        "",
        f"Session-level export: [`{OUTPUT_CSV.name}`](data/{OUTPUT_CSV.name}).",
        "",
        "## Source and scope notes",
        "",
        f"- Weekend source archive: [`{SOURCE_ARCHIVE.name}`]({quote(SOURCE_ARCHIVE.name)}); [upstream GitHub file]({SOURCE_URL}) at commit `{SOURCE_COMMIT}`; SHA-256 `{SOURCE_SHA256}`.",
        "- The archive contains two annotated IG **Weekend Oil – US Crude (CLN25)** screenshots dated Oct. 17 and Oct. 18, not a complete OHLC history and not separate BRENT/USOIL Monday-open price files. The screenshots are retained as source context, not transcribed as daily marks.",
        "- The two Oct. 19 open prices, BRENT $111.412 and USOIL $99.04, were provided by the user and identified as TradingView. BRENT is stored internally as `BRENT`; USOIL maps to the repository ticker `OIL`.",
        "- Subsequent EOD values come from [`energy_provider_eod_marks_v1.csv`](data/energy_provider_eod_marks_v1.csv): BlackBull Markets Brent Cash for BRENT and TradingView TVC:USOIL for OIL. No new or external daily prices are inserted.",
        "- This one-time 50U-per-instrument overlay is **not included** in the core replay, THE ONE MODEL's 32-portfolio aggregate, or standard 10U energy strategy-comparison composites. It is a separate hypothetical with $1,000,000 combined gross notional, not an account-capital return.",
        "- PnL excludes commissions, spread, slippage, financing, CFD contract multipliers/tracking differences, taxes, margin, and execution constraints. The notional-percentage view is a simple gross-notional ratio, not an account return.",
        "",
    ])
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    return REPORT


def main():
    rows = build_rows()
    write_csv(rows)
    chart = write_chart(rows)
    report = write_report(rows)
    print(f"Wrote {OUTPUT_CSV.relative_to(ROOT)} ({len(rows)} rows)")
    print(f"Wrote {chart.relative_to(ROOT)}")
    print(f"Wrote {report.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
