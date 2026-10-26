#!/usr/bin/env python3
"""Build a per-asset exposure and PnL breakdown for the four core portfolios."""

import csv
from collections import defaultdict
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

from model_perf_core import (
    DXY_PRICES,
    PRICES,
    SESSION_DATES,
    UNIT,
    VARIANTS,
    build_dxy_daily_lots,
    build_lots,
    parse_trades,
)

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_CSV = ROOT / "data" / "core_portfolio_asset_breakdown_20261023.csv"
REPORT = ROOT / "Core Portfolio Asset Breakdown.md"
UNIT_NOTIONAL = Decimal("10000")
CENT = Decimal("0.01")


def _decimal(value):
    return Decimal(str(value))


def _money(value):
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


def _fmt_money(value):
    return f"${_money(value):,.2f}"


def _fmt_units(value):
    return f"{value.normalize():f}"


def _asset_class(ticker):
    if ticker == "DXY":
        return "Integrated currency-index return proxy"
    if ticker in {"BRENT", "OIL"}:
        return "Energy commodity / cash-CFD price series"
    return "Direct-price TradingView ticker"


def build_rows():
    events = parse_trades()
    cutoff_index = len(SESSION_DATES) - 1
    cutoff_date = SESSION_DATES[cutoff_index]
    dxy_lots, _ = build_dxy_daily_lots()
    daily_totals = {}
    with (ROOT / "data" / "model_performance_daily.csv").open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row["session_date"] == cutoff_date:
                daily_totals[row["variant"]] = _decimal(row["total_pnl_usd"])

    rows = []
    summaries = {}
    for variant in VARIANTS:
        lots, realized = build_lots(variant, events)
        grouped = {
            ticker: {
                "long_units": Decimal("0"), "short_units": Decimal("0"),
                "long_notional": Decimal("0"), "short_notional": Decimal("0"),
                "long_unrealized": Decimal("0"), "short_unrealized": Decimal("0"),
                "long_lots": 0, "short_lots": 0,
            }
            for ticker in PRICES
        }
        realized_by_ticker = defaultdict(Decimal)
        for item in realized:
            realized_by_ticker[item["sym"]] += _decimal(item["pnl"])

        for lot in lots:
            if not lot["open"]:
                continue
            ticker = lot["sym"]
            side = lot["side"]
            units = _decimal(lot["qty"])
            entry_price = _decimal(lot["entry_px"])
            mark = _decimal(PRICES[ticker][cutoff_index])
            notional = units * UNIT_NOTIONAL
            pnl = notional * (
                mark / entry_price - Decimal("1")
                if side == "long" else Decimal("1") - mark / entry_price
            )
            grouped[ticker][f"{side}_units"] += units
            grouped[ticker][f"{side}_notional"] += notional
            grouped[ticker][f"{side}_unrealized"] += pnl
            grouped[ticker][f"{side}_lots"] += 1

        dxy_summary = {
            "long_units": Decimal("0"), "short_units": Decimal("0"),
            "long_notional": Decimal("0"), "short_notional": Decimal("0"),
            "long_unrealized": Decimal("0"), "short_unrealized": Decimal("0"),
            "long_lots": 0, "short_lots": 0,
        }
        for lot in dxy_lots:
            if not lot["open"]:
                continue
            units = _decimal(lot["qty"])
            entry_price = _decimal(lot["entry_px"])
            mark = _decimal(DXY_PRICES[cutoff_index])
            notional = units * UNIT_NOTIONAL
            pnl = notional * (mark / entry_price - Decimal("1"))
            dxy_summary["long_units"] += units
            dxy_summary["long_notional"] += notional
            dxy_summary["long_unrealized"] += pnl
            dxy_summary["long_lots"] += 1

        for ticker in list(PRICES) + ["DXY"]:
            values = dxy_summary if ticker == "DXY" else grouped[ticker]
            realized_pnl = Decimal("0") if ticker == "DXY" else realized_by_ticker[ticker]
            unrealized_pnl = values["long_unrealized"] + values["short_unrealized"]
            gross_open = values["long_notional"] + values["short_notional"]
            net_open = values["long_notional"] - values["short_notional"]
            rows.append({
                "as_of_date": cutoff_date,
                "variant": variant,
                "ticker": ticker,
                "asset_class": _asset_class(ticker),
                "eod_mark": f"{DXY_PRICES[cutoff_index] if ticker == 'DXY' else PRICES[ticker][cutoff_index]}",
                "long_open_units": _fmt_units(values["long_units"]),
                "short_open_units": _fmt_units(values["short_units"]),
                "long_open_notional_usd": f"{_money(values['long_notional']):.2f}",
                "short_open_notional_usd": f"{_money(values['short_notional']):.2f}",
                "gross_open_notional_usd": f"{_money(gross_open):.2f}",
                "net_entry_notional_usd": f"{_money(net_open):.2f}",
                "open_long_lots": str(values["long_lots"]),
                "open_short_lots": str(values["short_lots"]),
                "realized_pnl_usd": f"{_money(realized_pnl):.2f}",
                "unrealized_pnl_usd": f"{_money(unrealized_pnl):.2f}",
                "total_pnl_usd": f"{_money(realized_pnl + unrealized_pnl):.2f}",
            })

        direct_rows = [row for row in rows if row["variant"] == variant and row["ticker"] != "DXY"]
        dxy_row = next(row for row in rows if row["variant"] == variant and row["ticker"] == "DXY")
        direct_long = sum(_decimal(row["long_open_notional_usd"]) for row in direct_rows)
        direct_short = sum(_decimal(row["short_open_notional_usd"]) for row in direct_rows)
        direct_gross = direct_long + direct_short
        dxy_gross = _decimal(dxy_row["gross_open_notional_usd"])
        all_gross = direct_gross + dxy_gross
        combined_oil_gross = sum(
            _decimal(row["gross_open_notional_usd"])
            for row in direct_rows if row["ticker"] in {"BRENT", "OIL"}
        )
        exact_direct_total_pnl = (
            sum(realized_by_ticker.values(), Decimal("0"))
            + sum((value["long_unrealized"] + value["short_unrealized"] for value in grouped.values()), Decimal("0"))
        )
        exact_dxy_total_pnl = dxy_summary["long_unrealized"] + dxy_summary["short_unrealized"]
        total_pnl = exact_direct_total_pnl + exact_dxy_total_pnl
        if variant not in daily_totals or abs(total_pnl - daily_totals[variant]) > Decimal("0.02"):
            raise AssertionError(f"{variant} asset breakdown does not reconcile to the core daily output")
        summaries[variant] = {
            "direct_long": direct_long,
            "direct_short": direct_short,
            "direct_gross": direct_gross,
            "dxy_gross": dxy_gross,
            "gross": all_gross,
            "oil_gross": combined_oil_gross,
            "direct_lots": sum(int(row["open_long_lots"]) + int(row["open_short_lots"]) for row in direct_rows),
            "open_lots": sum(int(row["open_long_lots"]) + int(row["open_short_lots"]) for row in direct_rows) + int(dxy_row["open_long_lots"]),
            "pnl": total_pnl,
        }
    return rows, summaries


def write_csv(rows):
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return OUTPUT_CSV


def write_report(rows, summaries):
    cutoff_date = SESSION_DATES[-1]
    by_variant_ticker = {(row["variant"], row["ticker"]): row for row in rows}
    variants = list(VARIANTS)
    lines = [
        "# Core Portfolio Asset Breakdown — EOD " + cutoff_date,
        "",
        "> **Historical hypothetical paper-model snapshot.** This is the four-variant core, not THE ONE MODEL's 32-book aggregate. Gross open notional is the sum of original entry-notional units, before netting; it is not account equity, cash, current market value, or a verified live position report.",
        "",
        f"## Portfolio-level exposure through {cutoff_date}",
        "",
        "The core contains **31 direct-price TradingView tickers** plus the integrated **1U/DAY/DXY index-return sleeve** (35 active daily lots, $350,000 gross notional). DXY is shown as a separate index proxy, not as a directly traded security. BTC and ETH are excluded pending TradingView recalibration.",
        "",
        "| Core variant | Direct long gross | Direct short gross | Direct gross (not netted) | Integrated DXY | Total core gross open | Open lots incl. DXY | Terminal PnL at cutoff |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for variant in variants:
        s = summaries[variant]
        lines.append(
            f"| {variant} | ${s['direct_long']:,.0f} | ${s['direct_short']:,.0f} | "
            f"${s['direct_gross']:,.0f} | ${s['dxy_gross']:,.0f} | ${s['gross']:,.0f} | "
            f"{s['open_lots']} | ${s['pnl']:+,.2f} |"
        )
    direct_oil_shares = [summaries[variant]["oil_gross"] / summaries[variant]["direct_gross"] * 100 for variant in variants]
    core_oil_shares = [summaries[variant]["oil_gross"] / summaries[variant]["gross"] * 100 for variant in variants]
    lines.extend([
        "",
        "## Concentration flags",
        "",
        "BRENT and OIL are the largest combined core positions: their "
        f"{_fmt_money(summaries['V1']['oil_gross'])} gross open notional is "
        f"{min(direct_oil_shares):.1f}%–{max(direct_oil_shares):.1f}% of direct-price gross exposure "
        f"(depending on variant), or {min(core_oil_shares):.1f}%–{max(core_oil_shares):.1f}% of total core gross including DXY. "
        "Each ticker also has a separate modeled 10U SHORT opened at its Oct. 23 target level ($117 BRENT; $102 OIL), in addition to the remaining and trimmed long lots; gross exposure shown here is not netted. The four later 10U LONG replenishments (two per ticker) add $200,000 per ticker, $400,000 combined, after the cutoff and remain excluded pending later EOD marks. The $115.792 BRENT/$101.74 OIL entries use the user-recalled 17:20–17:25 MST window, represented by a 17:22 MST midpoint; the $114.80 BRENT/$101.00 OIL entries use an approximate 20:00 MST timestamp. The two tagged shorts are explicitly modeled to exit at $114.627 BRENT and $100.74 OIL on Oct. 25 at 20:35 MST, after the four earlier LONG replenishments and simultaneously with separate 35U BRENT and 34U OIL LONG Weekend Oil buys. The new buy lots are distinct and count toward buy-side weekly supply, while the short closures do not. After the modeled short closures, the existing 65U BRENT + 66U OIL all-core long exposure plus these 35U/34U buys totals 100U per ticker, 200U combined ($2,000,000 fixed-unit notional); all such post-cutoff activity is excluded from this Oct. 23 snapshot. These hypothetical price/time assumptions override SAR only for those tagged shorts.",
        "",
        "| Asset | V1 gross open | V2 gross open | V3A gross open | V3B gross open |",
        "|---|---:|---:|---:|---:|",
    ])
    for ticker in ("BRENT", "OIL", "DXY"):
        display = "USOIL (OIL)" if ticker == "OIL" else ticker
        vals = [by_variant_ticker[(variant, ticker)]["gross_open_notional_usd"] for variant in variants]
        lines.append(f"| {display} | " + " | ".join(f"${float(v):,.0f}" for v in vals) + " |")
    lines.extend([
        "",
        "### Full asset exposure by core variant",
        "",
        "Each cell gives **long units / short units · gross open notional**. A zero short or long side means no open lots on that side. The full export also includes realized, unrealized, and total PnL by ticker and variant.",
        "",
        "| Asset | V1 L/S · Gross | V2 L/S · Gross | V3A L/S · Gross | V3B L/S · Gross | V1 asset PnL |",
        "|---|---:|---:|---:|---:|---:|",
    ])
    direct_rows = [row for row in rows if row["variant"] == "V1" and row["ticker"] != "DXY"]
    direct_rows.sort(key=lambda row: (-float(row["gross_open_notional_usd"]), row["ticker"]))
    for row in direct_rows:
        ticker = row["ticker"]
        display = "USOIL (OIL)" if ticker == "OIL" else ticker
        cells = []
        for variant in variants:
            item = by_variant_ticker[(variant, ticker)]
            cells.append(
                f"{item['long_open_units']}/{item['short_open_units']}U · "
                f"${float(item['gross_open_notional_usd']):,.0f}"
            )
        lines.append(
            f"| {display} | " + " | ".join(cells) +
            f" | ${float(row['total_pnl_usd']):+,.2f} |"
        )
    dxy_cells = []
    for variant in variants:
        item = by_variant_ticker[(variant, "DXY")]
        dxy_cells.append(
            f"{item['long_open_units']}/{item['short_open_units']}U · "
            f"${float(item['gross_open_notional_usd']):,.0f}"
        )
    dxy_row = by_variant_ticker[("V1", "DXY")]
    lines.append(
        "| DXY index proxy | " + " | ".join(dxy_cells) +
        f" | ${float(dxy_row['total_pnl_usd']):+,.2f} |"
    )
    pending = [event for event in parse_trades() if event["date"] > cutoff_date and event["sym"] in {"BRENT", "OIL"}]
    lines.extend([
        "",
        "## Post-cutoff ledger entries",
        "",
    ])
    if pending:
        lines.append("These are logged after the last EOD mark and are not included in any exposure or PnL figures above:")
        lines.append("")
        lines.append("| Date | Time (MST; approx. where noted) | Asset | Side | Units | Entry/exit price | Gross notional |")
        lines.append("|---|---|---|---|---:|---:|---:|")
        for event in pending:
            display = "USOIL (OIL)" if event["sym"] == "OIL" else event["sym"]
            time_text = f"~{event['time']}" if "approximate time per user" in event["note"] else event["time"]
            lines.append(
                f"| {event['date']} | {time_text} | {display} | {event['tag']} | {event['units']:g}U | "
                f"${event['px']:,.3f} | ${float(event['units']) * UNIT:,.0f} |"
            )
    else:
        lines.append("No direct-price entries fall after the current mark cutoff.")
    lines.extend([
        "",
        f"Machine-readable detail: [`{OUTPUT_CSV.name}`](data/{OUTPUT_CSV.name}) ({len(rows)} asset/variant rows).",
        "",
        "### Reading notes",
        "",
        "- Gross notionals are based on each open lot's logged units × $10,000; they are intentionally not netted across long and short lots. Net entry notional is in the CSV.",
        "- Asset-level PnL includes both realized PnL from earlier closes and unrealized PnL on open lots. DXY PnL is a separate notional/index-return proxy but is included in each core variant's total. Per-asset values are rounded to cents, so their displayed sum may differ from the core total by a few cents; unrounded values reconcile.",
        "- This report excludes the separate 10U energy daily-buy sidecars and the other strategy-comparison force models. THE ONE MODEL's 32 independent portfolios multiply their core books and include their own sidecars; those totals are not shown here.",
        "- Entry records dated after the final EOD mark are listed separately, but cannot be marked or included in the historical terminal PnL without a subsequent supplied close.",
        "",
    ])
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    return REPORT


def main():
    rows, summaries = build_rows()
    csv_path = write_csv(rows)
    report_path = write_report(rows, summaries)
    print(f"Wrote {csv_path.relative_to(ROOT)} ({len(rows)} rows)")
    print(f"Wrote {report_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
