"""Build an Oct. 22 DXY-equivalent portfolio snapshot from the standardized book.

The DXY/FX terminal marks are user-provided. US30Y uses the user-provided daily
close series through Oct. 22. Since daily DXY/FX histories were not supplied, this
is a terminal snapshot, not a complete daily PnL replay for those instruments.
"""

import csv
import sys
from bisect import bisect_left
from collections import defaultdict
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from model_perf_core import (  # noqa: E402
    UNIT,
    VARIANTS,
    VARIANT_LABEL,
    SESSION_DATES,
    PRICES,
    all_series,
    build_lots,
    parse_trades,
)
from us10y_adjustment import (  # noqa: E402
    BASELINE_PCT,
    START_DATE as US10Y_START_DATE,
    align_session_yields,
    load_source_yields,
)

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
REPORT_PATH = ROOT / "DXY-Equivalent Portfolio Snapshot.md"
SUMMARY_CSV = DATA_DIR / "dxy_portfolio_summary_oct22.csv"
POSITIONS_CSV = DATA_DIR / "dxy_portfolio_open_positions_oct22.csv"
US30Y_DAILY_CSV = DATA_DIR / "us30y_short_mark_to_market_daily_2026.csv"
US30Y_FILES = (
    DATA_DIR / "us30y_close_september_2026.csv",
    DATA_DIR / "us30y_close_october_2026.csv",
)
DXY_FX_MARKS = DATA_DIR / "dxy_fx_oct22_marks_2026.csv"
TERMINAL_DATE = "2026-10-22"
DXY_POINT_USD = 1000.0  # User-selected ICE DX futures-equivalent reporting scale.
QUOTE_UNITS = {
    "DXY": "DXY index points",
    "EURUSD": "USD per EUR",
    "JPYUSD": "USD per JPY",
    "US30Y": "yield percent",
    "US10Y": "yield percent",
}

# Each entry adds one standard $10,000 portfolio unit. PnL is calculated as the
# side-adjusted proportional change in the quoted instrument, consistent with
# the model's $10,000-notional convention.
EXTRA_MARKED_POSITIONS = (
    {"symbol": "DXY", "entry_date": "2026-09-04", "entry_price": 99.087,
     "side": "LONG", "units": 1, "mark_key": "DXY"},
    {"symbol": "EURUSD", "entry_date": "2026-09-15", "entry_price": 1.15388,
     "side": "LONG", "units": 1, "mark_key": "EURUSD"},
    {"symbol": "JPYUSD", "entry_date": "2026-09-07", "entry_price": 0.010160,
     "side": "LONG", "units": 1, "mark_key": "JPYUSD"},
    {"symbol": "US30Y", "entry_date": "2026-09-15", "entry_price": 5.35,
     "side": "SHORT", "units": 1, "mark_key": "US30Y"},
)
# Yield entries are treated as carry-context notional, not separate price PnL.
CARRY_REFERENCE_POSITIONS = (
    {"symbol": "US10Y", "entry_date": "2026-09-10", "entry_price": 4.865,
     "side": "LONG", "units": 1},
    {"symbol": "US10Y", "entry_date": "2026-09-24", "entry_price": 5.208,
     "side": "LONG", "units": 1},
)


def read_user_marks():
    marks = {}
    with DXY_FX_MARKS.open(newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            if row["mark_date"] != TERMINAL_DATE:
                raise ValueError(f"Unexpected terminal date for {row['symbol']}: {row['mark_date']}")
            marks[row["symbol"]] = float(row["close"])
    for symbol in ("DXY", "EURUSD", "JPYUSD"):
        if symbol not in marks:
            raise ValueError(f"Missing user-provided Oct. 22 mark for {symbol}")
    return marks


def read_us30y_closes():
    closes = {}
    for path in US30Y_FILES:
        with path.open(newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            if not reader.fieldnames or "Date" not in reader.fieldnames:
                raise ValueError(f"Missing Date field in {path.name}")
            value_col = next((c for c in reader.fieldnames if c != "Date"), None)
            if value_col is None:
                raise ValueError(f"Missing yield field in {path.name}")
            for row in reader:
                day = row["Date"].strip()
                value = float(row[value_col].strip())
                if day in closes:
                    raise ValueError(f"Duplicate US30Y close for {day}")
                if not 0 < value < 20:
                    raise ValueError(f"Implausible US30Y yield {value} on {day}")
                closes[day] = value
    if TERMINAL_DATE not in closes:
        raise ValueError(f"US30Y series has no {TERMINAL_DATE} close")
    return dict(sorted(closes.items()))


def align_us30y(session_dates, closes):
    """Forward-fill an explicitly source-dated close to equity comparison dates."""
    aligned = []
    last_source = None
    sorted_observations = sorted(closes)
    for session in session_dates:
        for observed in sorted_observations:
            if observed > session:
                break
            last_source = observed
        if last_source is None:
            aligned.append({"date": session, "yield_pct": None,
                            "source_date": None, "carried_forward": False})
        else:
            aligned.append({"date": session, "yield_pct": closes[last_source],
                            "source_date": last_source,
                            "carried_forward": last_source != session})
    return aligned


def _entry_session(entry_date):
    idx = bisect_left(SESSION_DATES, entry_date)
    return min(idx, len(SESSION_DATES) - 1)


def build_positions(series, core_events, user_marks, us30y_rows):
    """Return open position-level PnL rows for each variant at Oct. 22."""
    us30y_mark_row = next(row for row in us30y_rows if row["date"] == TERMINAL_DATE)
    us30y_mark = us30y_mark_row["yield_pct"]
    positions_by_variant = {v: [] for v in VARIANTS}

    for variant in VARIANTS:
        lots, _ = build_lots(variant, core_events)
        for lot in lots:
            if not lot["open"]:
                continue
            mark = PRICES[lot["sym"]][-1]
            direction = 1.0 if lot["side"] == "long" else -1.0
            notional = lot["qty"] * UNIT
            pnl = direction * notional * (mark / lot["entry_px"] - 1.0)
            positions_by_variant[variant].append({
                "variant": variant,
                "symbol": lot["sym"],
                "quote_units": "USD quote",
                "side": lot["side"].upper(),
                "entry_date": lot["entry_date"],
                "entry_price": lot["entry_px"],
                "mark_date": TERMINAL_DATE,
                "mark_price": mark,
                "mark_source_date": TERMINAL_DATE,
                "mark_carried_forward": False,
                "units": lot["qty"],
                "notional_usd": notional,
                "unrealized_pnl_usd": pnl,
                "dxy_point_equivalent": pnl / DXY_POINT_USD,
                "pnl_status": "valued; model daily close/settlement",
            })

        for pos in EXTRA_MARKED_POSITIONS:
            mark = user_marks[pos["mark_key"]] if pos["symbol"] != "US30Y" else us30y_mark
            direction = 1.0 if pos["side"] == "LONG" else -1.0
            notional = pos["units"] * UNIT
            pnl = direction * notional * (mark / pos["entry_price"] - 1.0)
            source_date = (
                us30y_mark_row["source_date"] if pos["symbol"] == "US30Y" else TERMINAL_DATE
            )
            carried = (
                us30y_mark_row["carried_forward"] if pos["symbol"] == "US30Y" else False
            )
            positions_by_variant[variant].append({
                "variant": variant,
                "symbol": pos["symbol"],
                "quote_units": QUOTE_UNITS[pos["symbol"]],
                "side": pos["side"],
                "entry_date": pos["entry_date"],
                "entry_price": pos["entry_price"],
                "mark_date": TERMINAL_DATE,
                "mark_price": mark,
                "mark_source_date": source_date,
                "mark_carried_forward": carried,
                "units": pos["units"],
                "notional_usd": notional,
                "unrealized_pnl_usd": pnl,
                "dxy_point_equivalent": pnl / DXY_POINT_USD,
                "pnl_status": (
                    "user-provided Oct. 22 close; proportional $10,000-notional return"
                    if pos["symbol"] != "US30Y"
                    else "daily US30Y yield close; proportional quote-return proxy"
                ),
            })

        for pos in CARRY_REFERENCE_POSITIONS:
            positions_by_variant[variant].append({
                "variant": variant,
                "symbol": pos["symbol"],
                "quote_units": QUOTE_UNITS[pos["symbol"]],
                "side": pos["side"],
                "entry_date": pos["entry_date"],
                "entry_price": pos["entry_price"],
                "mark_date": TERMINAL_DATE,
                "mark_price": None,
                "mark_source_date": None,
                "mark_carried_forward": False,
                "units": pos["units"],
                "notional_usd": pos["units"] * UNIT,
                "unrealized_pnl_usd": None,
                "dxy_point_equivalent": None,
                "pnl_status": "US10Y carry reference; no standalone position PnL",
            })

    return positions_by_variant


def expanded_carry(series, extra_notional_by_session, yield_rows):
    """Recalculate US10Y carry on core plus all added $10,000 deployed notionals."""
    day_carry = {v: [0.0] * len(SESSION_DATES) for v in VARIANTS}
    cumulative = {v: [0.0] * len(SESSION_DATES) for v in VARIANTS}
    for i in range(len(SESSION_DATES) - 1):
        start_day, end_day = SESSION_DATES[i], SESSION_DATES[i + 1]
        if start_day < US10Y_START_DATE or not yield_rows[i]["active"]:
            continue
        days = (date.fromisoformat(end_day) - date.fromisoformat(start_day)).days
        spread = (yield_rows[i]["yield_pct"] - BASELINE_PCT) / 100.0
        for variant in VARIANTS:
            notional = series[variant]["deployed"][i] + extra_notional_by_session[i]
            day_carry[variant][i + 1] = notional * spread * days / 365.0
    for variant in VARIANTS:
        running = 0.0
        cumulative[variant] = []
        for amount in day_carry[variant]:
            running += amount
            cumulative[variant].append(running)
    return day_carry, cumulative


def extra_deployed_schedule():
    """Schedule DXY/FX/US30Y marks and US10Y carry-reference units."""
    schedule = [0.0] * len(SESSION_DATES)
    extra_positions = list(EXTRA_MARKED_POSITIONS) + list(CARRY_REFERENCE_POSITIONS)
    for pos in extra_positions:
        i = _entry_session(pos["entry_date"])
        for j in range(i, len(schedule)):
            schedule[j] += pos["units"] * UNIT
    return schedule


def write_positions_csv(positions_by_variant):
    fields = [
        "variant", "symbol", "quote_units", "side", "entry_date", "entry_price", "mark_date",
        "mark_price", "mark_source_date", "mark_carried_forward", "units",
        "notional_usd", "unrealized_pnl_usd", "dxy_point_equivalent", "pnl_status",
    ]
    with POSITIONS_CSV.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        for variant in VARIANTS:
            for row in sorted(positions_by_variant[variant], key=lambda x: (x["symbol"], x["entry_date"])):
                writer.writerow(row)


def write_us30y_daily_csv(us30y_rows):
    fields = [
        "date", "position", "side", "entry_yield_pct", "close_yield_pct",
        "source_date", "carried_forward", "units", "notional_usd",
        "unrealized_pnl_usd", "dxy_point_equivalent", "valuation_note",
    ]
    with US30Y_DAILY_CSV.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        for row in us30y_rows:
            if row["date"] < "2026-09-15" or row["yield_pct"] is None:
                continue
            pnl = -UNIT * (row["yield_pct"] / 5.35 - 1.0)
            writer.writerow({
                "date": row["date"],
                "position": "US30Y Sep 15 SHORT",
                "side": "SHORT",
                "entry_yield_pct": 5.35,
                "close_yield_pct": row["yield_pct"],
                "source_date": row["source_date"],
                "carried_forward": row["carried_forward"],
                "units": 1,
                "notional_usd": UNIT,
                "unrealized_pnl_usd": pnl,
                "dxy_point_equivalent": pnl / DXY_POINT_USD,
                "valuation_note": "Proportional quote-return proxy; not bond-duration PnL",
            })
        writer.writerow({
            "date": "2026-10-23",
            "position": "US30Y Oct 23 LONG (new entry; outside Oct 22 snapshot)",
            "side": "LONG",
            "entry_yield_pct": 5.311,
            "close_yield_pct": 5.311,
            "source_date": "2026-10-23",
            "carried_forward": False,
            "units": 1,
            "notional_usd": UNIT,
            "unrealized_pnl_usd": 0.0,
            "dxy_point_equivalent": 0.0,
            "valuation_note": "User-provided entry mark; no later close supplied",
        })


def write_summary_csv(summary):
    fields = [
        "variant", "cumulative_deployed_units", "open_units_including_yield_refs",
        "deployed_notional_usd", "base_realized_pnl_usd", "base_unrealized_pnl_usd",
        "additional_marked_unrealized_pnl_usd", "total_unrealized_pnl_usd",
        "pnl_before_us10y_carry_usd", "us10y_carry_adjustment_usd",
        "adjusted_total_pnl_usd", "adjusted_roi_pct", "adjusted_total_dxy_point_equivalent",
    ]
    with SUMMARY_CSV.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        for variant in VARIANTS:
            writer.writerow({"variant": variant, **summary[variant]})


def build_report(summary, positions_by_variant, user_marks, us30y_rows):
    last30 = next(row for row in us30y_rows if row["date"] == TERMINAL_DATE)
    lines = [
        "# DXY-Equivalent Portfolio Snapshot — Oct. 22, 2026",
        "",
        "A terminal portfolio view at the agreed Oct. 22 historical close. It adds the user-provided DXY, EUR/USD, and JPY/USD marks and the daily-marked US30Y SHORT to the four core model variants, then recalculates the US10Y spread carry over the expanded deployed-notional base.",
        "",
        "> **DXY units:** PnL equivalents use the user-selected ICE DX futures-equivalent scale of **$1,000 per DXY index point**. This is a reporting conversion only; the logged DXY position is TVC:DXY, not an actual ICE futures contract. Standard portfolio units remain **$10,000 notional each**.",
        "",
        "## Oct. 22 Portfolio Totals",
        "",
        "| Variant | Deployed units | Open units incl. US10Y refs | Deployed notional | Base realized | Total unrealized | US10Y carry | **Adjusted total USD** | **Adjusted DXY-point equivalent** | **Adjusted ROI** |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for variant in VARIANTS:
        s = summary[variant]
        lines.append(
            f"| **{VARIANT_LABEL[variant]}** | {s['cumulative_deployed_units']:.0f}u | "
            f"{s['open_units_including_yield_refs']:.0f}u | ${s['deployed_notional_usd']:,.2f} | "
            f"${s['base_realized_pnl_usd']:,.2f} | ${s['total_unrealized_pnl_usd']:,.2f} | "
            f"${s['us10y_carry_adjustment_usd']:,.2f} | **${s['adjusted_total_pnl_usd']:,.2f}** | "
            f"**{s['adjusted_total_dxy_point_equivalent']:+.3f}** | **{s['adjusted_roi_pct']:.3f}%** |"
        )

    lines.extend([
        "",
        "## Added Terminal Marks and Unrealized PnL",
        "",
        "| Position | Side | Entry | Oct. 22 mark | Units | Unrealized USD | DXY-point equivalent |",
        "|---|---|---:|---:|---:|---:|---:|",
    ])
    terminal_positions = positions_by_variant["V1"]
    for symbol in ("DXY", "EURUSD", "JPYUSD", "US30Y"):
        row = next(r for r in terminal_positions if r["symbol"] == symbol)
        lines.append(
            f"| {symbol} | {row['side']} | {row['entry_price']:,.6f} {row['quote_units']} | "
            f"{row['mark_price']:,.6f} {row['quote_units']} | {row['units']:g} | "
            f"${row['unrealized_pnl_usd']:+,.2f} | {row['dxy_point_equivalent']:+.3f} |"
        )
    lines.extend([
        "",
        "EUR/USD and JPY/USD PnL is calculated in USD using each pair's quoted USD-per-base-currency close and the standard $10,000 entry notional. DXY and the US30Y yield are valued by proportional quote return on the same $10,000 notional; the US30Y result is a quote-return proxy, not a bond-duration or futures-contract valuation.",
        "",
        f"US30Y Oct. 22 close: `{last30['yield_pct']:.3f}%` (source date `{last30['source_date']}`; carried-forward flag `{last30['carried_forward']}`). The missing Oct. 12 Treasury observation is transparently carried from Oct. 9 (`5.600%`) for that session, consistent with the confirmed US10Y holiday treatment.",
        "",
        "## All Open Unrealized PnL by Symbol",
        "",
        "The full position-level ledger (including every open core lot and the added DXY/FX/US30Y marks) is in [`data/dxy_portfolio_open_positions_oct22.csv`](data/dxy_portfolio_open_positions_oct22.csv). US10Y entries are included as two $10,000 carry-reference units but deliberately have no standalone yield-quote PnL; their role is represented by the US10Y portfolio carry.",
        "",
    ])
    for variant in VARIANTS:
        grouped = defaultdict(lambda: {"units": 0.0, "pnl": 0.0})
        for row in positions_by_variant[variant]:
            if row["unrealized_pnl_usd"] is None:
                continue
            grouped[row["symbol"]]["units"] += row["units"]
            grouped[row["symbol"]]["pnl"] += row["unrealized_pnl_usd"]
        lines.extend([
            f"### {VARIANT_LABEL[variant]}",
            "",
            "| Symbol | Open units | Unrealized USD | DXY-point equivalent |",
            "|---|---:|---:|---:|",
        ])
        for symbol in sorted(grouped):
            item = grouped[symbol]
            lines.append(
                f"| {symbol} | {item['units']:g} | ${item['pnl']:+,.2f} | "
                f"{item['pnl'] / DXY_POINT_USD:+.3f} |"
            )
        lines.append("")

    lines.extend([
        "## Carry, Scope, and Date Notes",
        "",
        f"- The US10Y carry is recalculated on the core model's cumulative deployed notional plus all six additional $10,000 units deployed by Oct. 22: DXY, EUR/USD, JPY/USD, the Sep. 15 US30Y SHORT, and both US10Y carry-reference entries. Each interval uses deployed notional × ((US10Y close − {BASELINE_PCT:.3f}%) / 100) × elapsed calendar days / 365; above-baseline yields add and below-baseline yields subtract.",
        "- The Oct. 23 US30Y LONG at 5.311% is a separate new one-unit position and is not included in Oct. 22 totals.",
        "- User-provided DXY/FX marks are terminal-only. No daily DXY/EURUSD/JPYUSD closes were supplied, so this file is a terminal snapshot and does not invent daily paths for those positions.",
        "- The US10Y LONGs are carry references rather than standalone quote-return positions in this view. The 30Y PnL is shown separately using a proportional quote-return proxy on $10,000; a bond-duration valuation would require a separate instrument/duration model.",
        "- The exported detail lists the Oct. 22 close for each open core position and the source date for the US30Y mark. All currency PnL is shown in USD first, then as DXY-point equivalents using $1,000 per point.",
        "",
        f"Machine-readable portfolio totals: [`{SUMMARY_CSV.name}`](data/{SUMMARY_CSV.name}).",
        "",
        f"Position-level unrealized ledger: [`{POSITIONS_CSV.name}`](data/{POSITIONS_CSV.name}).",
        "",
        f"Daily US30Y SHORT marks and PnL recalibration: [`{US30Y_DAILY_CSV.name}`](data/{US30Y_DAILY_CSV.name}).",
        "",
    ])
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main():
    if not any(path.exists() for path in US30Y_FILES):
        raise FileNotFoundError("User-provided US30Y daily close CSVs are required")
    user_marks = read_user_marks()
    us30y_closes = read_us30y_closes()
    us30y_rows = align_us30y(SESSION_DATES, us30y_closes)
    us10y_rows = align_session_yields(SESSION_DATES)
    series, core_events = all_series()
    positions = build_positions(series, core_events, user_marks, us30y_rows)
    extra_schedule = extra_deployed_schedule()
    _, carry_series = expanded_carry(series, extra_schedule, us10y_rows)

    summary = {}
    for variant in VARIANTS:
        valued_rows = [row for row in positions[variant] if row["unrealized_pnl_usd"] is not None]
        extra_unrealized = sum(
            row["unrealized_pnl_usd"] for row in valued_rows
            if row["symbol"] in {"DXY", "EURUSD", "JPYUSD", "US30Y"}
        )
        base_unrealized = series[variant]["unrealized"][-1]
        total_unrealized = base_unrealized + extra_unrealized
        realized = series[variant]["realized"][-1]
        carry = carry_series[variant][-1]
        deployed = series[variant]["deployed"][-1] + extra_schedule[-1]
        open_units = sum(row["units"] for row in positions[variant])
        total_before_carry = realized + total_unrealized
        adjusted_total = total_before_carry + carry
        summary[variant] = {
            "cumulative_deployed_units": deployed / UNIT,
            "open_units_including_yield_refs": open_units,
            "deployed_notional_usd": deployed,
            "base_realized_pnl_usd": realized,
            "base_unrealized_pnl_usd": base_unrealized,
            "additional_marked_unrealized_pnl_usd": extra_unrealized,
            "total_unrealized_pnl_usd": total_unrealized,
            "pnl_before_us10y_carry_usd": total_before_carry,
            "us10y_carry_adjustment_usd": carry,
            "adjusted_total_pnl_usd": adjusted_total,
            "adjusted_roi_pct": 100.0 * adjusted_total / deployed if deployed else 0.0,
            "adjusted_total_dxy_point_equivalent": adjusted_total / DXY_POINT_USD,
        }

    write_positions_csv(positions)
    write_us30y_daily_csv(us30y_rows)
    write_summary_csv(summary)
    build_report(summary, positions, user_marks, us30y_rows)
    for variant in VARIANTS:
        s = summary[variant]
        print(
            f"{variant}: {s['cumulative_deployed_units']:.0f} deployed units; "
            f"unrealized=${s['total_unrealized_pnl_usd']:,.2f}; "
            f"US10Y carry=${s['us10y_carry_adjustment_usd']:,.2f}; "
            f"adjusted=${s['adjusted_total_pnl_usd']:,.2f} "
            f"({s['adjusted_total_dxy_point_equivalent']:+.3f} DXY-point eq.)"
        )
    print(f"Wrote {REPORT_PATH.relative_to(ROOT)}")
    print(f"Wrote {SUMMARY_CSV.relative_to(ROOT)}")
    print(f"Wrote {POSITIONS_CSV.relative_to(ROOT)}")
    print(f"Wrote {US30Y_DAILY_CSV.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
