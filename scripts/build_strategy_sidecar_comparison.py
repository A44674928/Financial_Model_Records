"""Compare the four core variants with the fixed-$500/EOD direction-following model.

The "Exponential" label follows the user's name for the model. Each new tranche
is fixed at $500 notional (not compounded). Direction is the latest LONG/SHORT/
REBUY entry in that ticker's trade log, carried forward each EOD. When it changes,
all open opposite-direction model lots close at that day's EOD mark before a new
$500 tranche is opened. The oil-desk component adds only its daily-buy lots when
combined with a core variant; core chart positions are already present there.
"""

import bisect
import csv
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from model_perf_core import (
    PRICES,
    SESSION_DATES,
    UNIT,
    VARIANTS,
    VARIANT_COLOR,
    VARIANT_LABEL,
    all_series,
    parse_trades,
)
from build_oil_desk_hypothetical import build_rows as build_oil_rows

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
CHARTS = ROOT / "Charts" / "performance"
DAILY_CSV = DATA / "strategy_sidecar_comparison_daily_v1.csv"
POSITION_CSV = DATA / "exponential_eod_positions_v1.csv"
REPORT = ROOT / "Strategy and Sidecar Comparison.md"
GRAPH = CHARTS / "20-strategy-sidecar-comparison.png"
EXPONENTIAL_TRANCHE_USD = 500.0
OIL_SIDE_CAR_LABEL = "Oil desk daily-buy add-on"
VARIANT_COLORS = {
    "V1": VARIANT_COLOR["V1"],
    "V2": VARIANT_COLOR["V2"],
    "V3A": VARIANT_COLOR["V3A"],
    "V3B": VARIANT_COLOR["V3B"],
}
EXP_COLOR = "#f97316"
OIL_COLOR = "#22c55e"
BOTH_COLOR = "#f8fafc"


def _direction(tag):
    tag = tag.upper()
    if tag in {"LONG", "REBUY"}:
        return "long"
    if tag == "SHORT":
        return "short"
    return None


def exponential_daily_model(events=None):
    """Return EOD $500-lot model daily totals and an auditable symbol/session ledger."""
    events = events if events is not None else parse_trades()
    events_by_date = defaultdict(list)
    for event in events:
        if event["date"] > SESSION_DATES[-1] or event["kind"] != "entry":
            continue
        direction = _direction(event["tag"])
        if not direction:
            continue
        # Match the core replay convention: weekend/holiday events take effect
        # at the first priced EOD session on or after the logged date.
        target_index = bisect.bisect_left(SESSION_DATES, event["date"])
        if target_index < len(SESSION_DATES):
            target_day = SESSION_DATES[target_index]
            events_by_date[target_day].append((event, direction))
    for day in events_by_date:
        events_by_date[day].sort(key=lambda pair: (pair[0]["date"], pair[0]["time"], pair[0]["sym"], pair[0]["order"]))

    symbols = sorted(PRICES)
    current_direction = {}
    lots = {symbol: [] for symbol in symbols}
    realized_total = 0.0
    cumulative_added = 0.0
    daily_rows = []
    position_rows = []

    for index, day in enumerate(SESSION_DATES):
        day_signals = {}
        for event, direction in events_by_date.get(day, []):
            day_signals[event["sym"]] = direction

        # Apply the last authorized directional event for each ticker at the
        # EOD. Non-directional exits/take-profit log rows do not clear state.
        for symbol, direction in day_signals.items():
            previous = current_direction.get(symbol)
            if previous is not None and previous != direction:
                price = PRICES[symbol][index]
                for lot in lots[symbol]:
                    if not lot["open"]:
                        continue
                    side_sign = 1.0 if lot["direction"] == "long" else -1.0
                    realized_total += lot["notional_usd"] * side_sign * (price / lot["entry_price"] - 1.0)
                    lot["open"] = False
                    lot["close_date"] = day
                    lot["close_price"] = price
            current_direction[symbol] = direction

        # Add one fresh fixed-notional tranche per symbol with a known direction.
        for symbol in symbols:
            direction = current_direction.get(symbol)
            if direction is None:
                continue
            price = PRICES[symbol][index]
            lots[symbol].append({
                "entry_date": day,
                "entry_price": price,
                "direction": direction,
                "notional_usd": EXPONENTIAL_TRANCHE_USD,
                "open": True,
                "close_date": None,
                "close_price": None,
            })
            cumulative_added += EXPONENTIAL_TRANCHE_USD

        unrealized = 0.0
        open_notional = 0.0
        active_symbols = 0
        for symbol in symbols:
            price = PRICES[symbol][index]
            symbol_open = [lot for lot in lots[symbol] if lot["open"]]
            if symbol_open:
                active_symbols += 1
            symbol_unrealized = sum(
                lot["notional_usd"]
                * (1.0 if lot["direction"] == "long" else -1.0)
                * (price / lot["entry_price"] - 1.0)
                for lot in symbol_open
            )
            symbol_open_notional = sum(lot["notional_usd"] for lot in symbol_open)
            unrealized += symbol_unrealized
            open_notional += symbol_open_notional
            position_rows.append({
                "date": day,
                "ticker": symbol,
                "direction": current_direction.get(symbol, ""),
                "eod_close": f"{price:.8f}",
                "daily_add_notional_usd": f"{EXPONENTIAL_TRANCHE_USD:.2f}" if current_direction.get(symbol) else "0.00",
                "open_lot_count": len(symbol_open),
                "open_notional_usd": f"{symbol_open_notional:.2f}",
                "ticker_unrealized_pnl_usd": f"{symbol_unrealized:.2f}",
                "signal_basis": "Latest trade-log LONG/SHORT/REBUY entry carried forward",
            })

        total = realized_total + unrealized
        daily_rows.append({
            "date": day,
            "exponential_realized_pnl_usd": f"{realized_total:.2f}",
            "exponential_unrealized_pnl_usd": f"{unrealized:.2f}",
            "exponential_total_pnl_usd": f"{total:.2f}",
            "exponential_cumulative_notional_added_usd": f"{cumulative_added:.2f}",
            "exponential_open_notional_usd": f"{open_notional:.2f}",
            "exponential_active_symbols": active_symbols,
            "exponential_daily_adds_usd": f"{active_symbols * EXPONENTIAL_TRANCHE_USD:.2f}",
        })

    return daily_rows, position_rows


def oil_sidecar_daily_pnl():
    """Return only new oil-desk daily-buy PnL; core maintenance lots are not duplicated."""
    by_date = defaultdict(float)
    rows = build_oil_rows()
    for row in rows:
        by_date[row["date"]] += float(row["daily_buys_unrealized_pnl_usd"])
    terminal_notional = sum(
        float(row["cumulative_daily_buy_notional_usd"])
        for row in rows if row["date"] == SESSION_DATES[-1]
    )
    return {day: by_date.get(day, 0.0) for day in SESSION_DATES}, terminal_notional


def comparison_rows():
    core, events = all_series()
    exp_daily, position_rows = exponential_daily_model(events)
    oil_pnl, oil_notional = oil_sidecar_daily_pnl()
    rows = []
    for i, day in enumerate(SESSION_DATES):
        exp = exp_daily[i]
        row = {
            "date": day,
            "exponential_pnl_usd": exp["exponential_total_pnl_usd"],
            "oil_desk_daily_buy_pnl_usd": f"{oil_pnl[day]:.2f}",
            "both_sidecars_pnl_usd": f"{float(exp['exponential_total_pnl_usd']) + oil_pnl[day]:.2f}",
            "oil_desk_cumulative_notional_usd": f"{oil_notional:.2f}",
            "oil_desk_open_notional_usd": f"{oil_notional:.2f}",
            "both_sidecars_cumulative_notional_usd": f"{float(exp['exponential_cumulative_notional_added_usd']) + oil_notional:.2f}",
            "both_sidecars_open_notional_usd": f"{float(exp['exponential_open_notional_usd']) + oil_notional:.2f}",
        }
        for variant in VARIANTS:
            base = core[variant]["total"][i]
            row[f"{variant}_core_pnl_usd"] = f"{base:.2f}"
            row[f"{variant}_plus_exponential_pnl_usd"] = f"{base + float(exp['exponential_total_pnl_usd']):.2f}"
            row[f"{variant}_plus_oil_desk_pnl_usd"] = f"{base + oil_pnl[day]:.2f}"
            row[f"{variant}_plus_both_sidecars_pnl_usd"] = f"{base + float(exp['exponential_total_pnl_usd']) + oil_pnl[day]:.2f}"
        row.update({key: value for key, value in exp.items() if key != "date"})
        rows.append(row)
    return rows, position_rows, core


def _write_dict_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise ValueError(f"Cannot write empty CSV: {path.name}")
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_csvs(rows, position_rows):
    _write_dict_csv(DAILY_CSV, rows)
    _write_dict_csv(POSITION_CSV, position_rows)
    return DAILY_CSV, POSITION_CSV


def _drawdown(values):
    peak = values[0] if values else 0.0
    out = []
    for value in values:
        peak = max(peak, value)
        out.append(value - peak)
    return out


def write_chart(rows):
    CHARTS.mkdir(parents=True, exist_ok=True)
    dates = [row["date"] for row in rows]
    core_lines = {variant: [float(row[f"{variant}_core_pnl_usd"]) for row in rows] for variant in VARIANTS}
    exp = [float(row["exponential_pnl_usd"]) for row in rows]
    oil = [float(row["oil_desk_daily_buy_pnl_usd"]) for row in rows]
    both = [float(row["both_sidecars_pnl_usd"]) for row in rows]
    exp_composites = {
        variant: [float(row[f"{variant}_plus_exponential_pnl_usd"]) for row in rows]
        for variant in VARIANTS
    }
    oil_composites = {
        variant: [float(row[f"{variant}_plus_oil_desk_pnl_usd"]) for row in rows]
        for variant in VARIANTS
    }
    both_composites = {
        variant: [float(row[f"{variant}_plus_both_sidecars_pnl_usd"]) for row in rows]
        for variant in VARIANTS
    }
    drawdown_lines = {variant: _drawdown(values) for variant, values in core_lines.items()}
    drawdown_lines["Exponential"] = _drawdown(exp)

    panels = [
        ("Core variants and exponential model", [
            (VARIANT_LABEL[v], core_lines[v], VARIANT_COLORS[v]) for v in VARIANTS
        ] + [("Exponential — $500 fixed tranche/EOD", exp, EXP_COLOR)]),
        ("Standalone sidecars (incremental PnL)", [
            ("Exponential only", exp, EXP_COLOR),
            ("Oil-desk daily buys only", oil, OIL_COLOR),
            ("Both sidecars", both, BOTH_COLOR),
        ]),
        ("Each core variant + exponential sidecar", [
            (f"{VARIANT_LABEL[v]} + exponential", exp_composites[v], VARIANT_COLORS[v]) for v in VARIANTS
        ]),
        ("Each core variant + oil-desk daily-buy sidecar", [
            (f"{VARIANT_LABEL[v]} + oil desk", oil_composites[v], VARIANT_COLORS[v]) for v in VARIANTS
        ]),
        ("Each core variant + both sidecars", [
            (f"{VARIANT_LABEL[v]} + both", both_composites[v], VARIANT_COLORS[v]) for v in VARIANTS
        ]),
        ("Drawdown from running PnL peak — core and exponential", [
            (VARIANT_LABEL[v], drawdown_lines[v], VARIANT_COLORS[v]) for v in VARIANTS
        ] + [("Exponential", drawdown_lines["Exponential"], EXP_COLOR)]),
    ]

    fig, axes = plt.subplots(len(panels), 1, figsize=(15, 23), sharex=True)
    fig.patch.set_facecolor("#0d131e")
    for ax, (title, lines) in zip(axes, panels):
        ax.set_facecolor("#141c2b")
        ax.grid(True, color="#26344a", alpha=0.8)
        ax.tick_params(colors="#93a4bd")
        for spine in ax.spines.values():
            spine.set_color("#26344a")
        for label, values, color in lines:
            ax.plot(dates, values, color=color, linewidth=1.8, label=label)
        ax.axhline(0, color="#93a4bd", linewidth=0.8)
        ax.set_title(title, color="#edf2f7", loc="left", fontsize=11)
        ax.set_ylabel("Drawdown (USD)" if "Drawdown" in title else "Cumulative PnL (USD)", color="#edf2f7")
        ax.legend(facecolor="#0d131e", edgecolor="#26344a", labelcolor="#edf2f7", fontsize=8, ncol=2)
    axes[-1].set_xlabel("EOD session date", color="#edf2f7")
    axes[-1].tick_params(axis="x", rotation=25)
    fig.suptitle("Core Variants, Exponential EOD Model, and Oil-Desk Sidecar", color="#edf2f7", fontsize=15)
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    fig.savefig(GRAPH, dpi=150, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close(fig)
    return GRAPH


def write_report(rows, position_rows, core):
    last = rows[-1]
    active_symbols = int(last["exponential_active_symbols"])
    exp_realized = float(last["exponential_realized_pnl_usd"])
    exp_unrealized = float(last["exponential_unrealized_pnl_usd"])
    lines = [
        "# Strategy and Sidecar Comparison",
        "",
        "![Core models, exponential model, and sidecar combinations](Charts/performance/20-strategy-sidecar-comparison.png)",
        "",
        "## Model rules and combination math",
        "",
        "- **Core variants:** existing V1, V2, V3A, and V3B model replays from the main comparison.",
        "- **Exponential model (user's label):** on every EOD after a ticker first has a logged direction, add a new **fixed $500 notional** lot in that ticker's most recent LONG/SHORT/REBUY direction. $500 does not compound. Carry direction forward until a new LONG/SHORT/REBUY entry occurs.",
        "- **Risk rule:** when the carried direction changes, close all previously open exponential lots for that ticker at the current EOD close, then open the new $500 tranche in the newly authorized direction. Same-direction signals do not close existing lots. Trade-log EXIT / TAKE PROFIT events are non-directional here and do not clear the carried state, per the selected last-direction rule.",
        "- **Signal basis:** the repository has no separate authorization feed, so the model uses the latest direction-bearing entry tag in `trades/*.txt` as the authorization record. REBUY is treated as LONG; weekend/holiday events take effect at the first priced EOD session on or after the logged date. Symbols do not accumulate $500 lots before their first directional log event.",
        "- **Oil-desk sidecar:** uses only the daily-buy lots from the prior 10-unit / $100,000-per-ticker-per-EOD hypothetical. The sidecar's chart-opened maintenance positions are not added to composites because the core model already contains chart positions; this avoids double counting.",
        "- **Graph combinations:** compare each core variant with each sidecar alone and with both sidecars together. The exponential and oil-desk lines also appear separately and as an incremental sidecar-only total. These are additive USD subtotals; they do not assume shared capital, funding, fees, or margin offsets.",
        "- Universe: all 33 directly price-covered core tickers; DXY, EURUSD, JPYUSD, US10Y, and US30Y remain outside this price-position model.",
        "",
        "## Terminal comparison — Oct. 23, 2026",
        "",
        "| Strategy | Terminal PnL | Cumulative notional added | Open notional |",
        "|---|---:|---:|---:|",
    ]
    summary = []
    summary.append(("Exponential ($500 fixed/EOD)", float(last["exponential_total_pnl_usd"]), f"${float(last['exponential_cumulative_notional_added_usd']):,.2f}", f"${float(last['exponential_open_notional_usd']):,.2f}"))
    summary.append(("Oil-desk daily-buy sidecar only", float(last["oil_desk_daily_buy_pnl_usd"]), f"${float(last['oil_desk_cumulative_notional_usd']):,.2f}", f"${float(last['oil_desk_open_notional_usd']):,.2f}"))
    summary.append(("Both sidecars (incremental)", float(last["both_sidecars_pnl_usd"]), f"${float(last['both_sidecars_cumulative_notional_usd']):,.2f}", f"${float(last['both_sidecars_open_notional_usd']):,.2f}"))
    exp_added = float(last["exponential_cumulative_notional_added_usd"])
    exp_open = float(last["exponential_open_notional_usd"])
    oil_added = float(last["oil_desk_cumulative_notional_usd"])
    oil_open = float(last["oil_desk_open_notional_usd"])
    for variant in VARIANTS:
        core_deployed = float(core[variant]["deployed"][-1])
        core_open = sum(lot["qty"] * UNIT for lot in core[variant]["lots"] if lot["open"])
        summary.append((f"{VARIANT_LABEL[variant]} — core", float(last[f"{variant}_core_pnl_usd"]), f"${core_deployed:,.2f}", f"${core_open:,.2f}"))
        summary.append((f"{VARIANT_LABEL[variant]} + exponential", float(last[f"{variant}_plus_exponential_pnl_usd"]), f"${core_deployed + exp_added:,.2f}", f"${core_open + exp_open:,.2f}"))
        summary.append((f"{VARIANT_LABEL[variant]} + oil desk", float(last[f"{variant}_plus_oil_desk_pnl_usd"]), f"${core_deployed + oil_added:,.2f}", f"${core_open + oil_open:,.2f}"))
        summary.append((f"{VARIANT_LABEL[variant]} + both sidecars", float(last[f"{variant}_plus_both_sidecars_pnl_usd"]), f"${core_deployed + float(last['both_sidecars_cumulative_notional_usd']):,.2f}", f"${core_open + float(last['both_sidecars_open_notional_usd']):,.2f}"))
    for name, pnl, added, open_notional in summary:
        lines.append(f"| {name} | ${pnl:+,.2f} | {added} | {open_notional} |")
    lines.extend([
        "",
        f"The exponential model ends at **${float(last['exponential_total_pnl_usd']):+,.2f}** (realized ${exp_realized:+,.2f}; unrealized ${exp_unrealized:+,.2f}), with **{active_symbols} active symbols** and ${float(last['exponential_open_notional_usd']):,.2f} open notional. It added ${float(last['exponential_cumulative_notional_added_usd']):,.2f} notional over the window.",
        "",
        "## Data and output files",
        "",
        "- Daily all-strategy comparison: [`strategy_sidecar_comparison_daily_v1.csv`](data/strategy_sidecar_comparison_daily_v1.csv).",
        "- Per-symbol, per-session exponential directions, adds, open lots, and unrealized PnL: [`exponential_eod_positions_v1.csv`](data/exponential_eod_positions_v1.csv).",
        "- Price series and source limitations: [`active_price_source_registry_v2.csv`](data/active_price_source_registry_v2.csv); exact energy EOD marks: [`energy_provider_eod_marks_v1.csv`](data/energy_provider_eod_marks_v1.csv).",
        "- Existing core report: [`Model Performance Comparison.md`](Model%20Performance%20Comparison.md). Existing oil-desk assumptions/details: [`Oil Desk EOD Accumulation Hypothetical.md`](Oil%20Desk%20EOD%20Accumulation%20Hypothetical.md).",
        "",
        "**Interpretation caveat:** this is a historical paper-trade replay under the requested direction-state and tranche rules, not a live trading system, risk forecast, or investment recommendation. Since $500 is fixed per EOD, the model's dollar exposure grows by accumulation rather than by compounding the tranche size.",
    ])
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return REPORT


def main():
    rows, position_rows, core = comparison_rows()
    write_csvs(rows, position_rows)
    graph = write_chart(rows)
    report = write_report(rows, position_rows, core)
    print(f"Wrote {DAILY_CSV.relative_to(ROOT)}")
    print(f"Wrote {POSITION_CSV.relative_to(ROOT)}")
    print(f"Wrote {graph.relative_to(ROOT)}")
    print(f"Wrote {report.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
