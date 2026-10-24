"""Compare core variants with fixed-$500 and 1-unit EOD direction-following models.

The "Exponential" and "Force Multiplier" labels follow the user's naming. Each
model adds a fixed-notional tranche per EOD: $500 for Exponential and $10,000
(1 unit) for Force Multiplier. The latest LONG/SHORT/REBUY trade-log direction
carries forward; when it changes, opposite open lots close at that day's EOD.
Oil-desk composites add only its daily-buy lots because chart positions already
exist in the core books.
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
FORCE_POSITION_CSV = DATA / "force_multiplier_eod_positions_v1.csv"
REPORT = ROOT / "Strategy and Sidecar Comparison.md"
GRAPH = CHARTS / "20-strategy-sidecar-comparison.png"
EXPONENTIAL_TRANCHE_USD = 500.0
FORCE_MULTIPLIER_TRANCHE_USD = UNIT
VARIANT_COLORS = {
    "V1": VARIANT_COLOR["V1"],
    "V2": VARIANT_COLOR["V2"],
    "V3A": VARIANT_COLOR["V3A"],
    "V3B": VARIANT_COLOR["V3B"],
}
EXP_COLOR = "#f97316"
FORCE_COLOR = "#ec4899"
OIL_COLOR = "#22c55e"
BOTH_COLOR = "#f8fafc"


def _direction(tag):
    tag = tag.upper()
    if tag in {"LONG", "REBUY"}:
        return "long"
    if tag == "SHORT":
        return "short"
    return None


def direction_following_daily_model(events=None, tranche_notional_usd=EXPONENTIAL_TRANCHE_USD, model_key="exponential"):
    """Return daily totals and symbol/session audit rows for a fixed-tranche model."""
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
                "notional_usd": tranche_notional_usd,
                "open": True,
                "close_date": None,
                "close_price": None,
            })
            cumulative_added += tranche_notional_usd

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
                "model": model_key,
                "date": day,
                "ticker": symbol,
                "direction": current_direction.get(symbol, ""),
                "eod_close": f"{price:.8f}",
                "tranche_notional_usd": f"{tranche_notional_usd:.2f}",
                "daily_add_notional_usd": f"{tranche_notional_usd:.2f}" if current_direction.get(symbol) else "0.00",
                "open_lot_count": len(symbol_open),
                "open_notional_usd": f"{symbol_open_notional:.2f}",
                "ticker_unrealized_pnl_usd": f"{symbol_unrealized:.2f}",
                "signal_basis": "Latest trade-log LONG/SHORT/REBUY entry carried forward",
            })

        total = realized_total + unrealized
        daily_rows.append({
            "date": day,
            f"{model_key}_realized_pnl_usd": f"{realized_total:.2f}",
            f"{model_key}_unrealized_pnl_usd": f"{unrealized:.2f}",
            f"{model_key}_total_pnl_usd": f"{total:.2f}",
            f"{model_key}_cumulative_notional_added_usd": f"{cumulative_added:.2f}",
            f"{model_key}_open_notional_usd": f"{open_notional:.2f}",
            f"{model_key}_active_symbols": active_symbols,
            f"{model_key}_daily_adds_usd": f"{active_symbols * tranche_notional_usd:.2f}",
        })

    return daily_rows, position_rows


def exponential_daily_model(events=None):
    """The originally requested fixed-$500/EOD exponential strategy."""
    return direction_following_daily_model(events, EXPONENTIAL_TRANCHE_USD, "exponential")


def force_multiplier_daily_model(events=None):
    """The force-multiplier alternative, using one $10,000 unit per active EOD."""
    return direction_following_daily_model(events, FORCE_MULTIPLIER_TRANCHE_USD, "force_multiplier")


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
    exp_daily, exp_positions = exponential_daily_model(events)
    force_daily, force_positions = force_multiplier_daily_model(events)
    oil_pnl, oil_notional = oil_sidecar_daily_pnl()
    rows = []
    for i, day in enumerate(SESSION_DATES):
        exp = exp_daily[i]
        force = force_daily[i]
        exp_pnl = float(exp["exponential_total_pnl_usd"])
        force_pnl = float(force["force_multiplier_total_pnl_usd"])
        exp_added = float(exp["exponential_cumulative_notional_added_usd"])
        force_added = float(force["force_multiplier_cumulative_notional_added_usd"])
        exp_open = float(exp["exponential_open_notional_usd"])
        force_open = float(force["force_multiplier_open_notional_usd"])
        oil_today = oil_pnl[day]
        row = {
            "date": day,
            "exponential_500_pnl_usd": f"{exp_pnl:.2f}",
            "force_multiplier_10k_pnl_usd": f"{force_pnl:.2f}",
            "oil_desk_daily_buy_pnl_usd": f"{oil_today:.2f}",
            "exponential_500_plus_oil_pnl_usd": f"{exp_pnl + oil_today:.2f}",
            "force_multiplier_plus_oil_pnl_usd": f"{force_pnl + oil_today:.2f}",
            "oil_desk_cumulative_notional_usd": f"{oil_notional:.2f}",
            "oil_desk_open_notional_usd": f"{oil_notional:.2f}",
            "exponential_500_plus_oil_cumulative_notional_usd": f"{exp_added + oil_notional:.2f}",
            "exponential_500_plus_oil_open_notional_usd": f"{exp_open + oil_notional:.2f}",
            "force_multiplier_plus_oil_cumulative_notional_usd": f"{force_added + oil_notional:.2f}",
            "force_multiplier_plus_oil_open_notional_usd": f"{force_open + oil_notional:.2f}",
        }
        for variant in VARIANTS:
            base = core[variant]["total"][i]
            row[f"{variant}_core_pnl_usd"] = f"{base:.2f}"
            row[f"{variant}_plus_exponential_500_pnl_usd"] = f"{base + exp_pnl:.2f}"
            row[f"{variant}_plus_force_multiplier_pnl_usd"] = f"{base + force_pnl:.2f}"
            row[f"{variant}_plus_oil_desk_pnl_usd"] = f"{base + oil_today:.2f}"
            row[f"{variant}_plus_exponential_500_and_oil_pnl_usd"] = f"{base + exp_pnl + oil_today:.2f}"
            row[f"{variant}_plus_force_multiplier_and_oil_pnl_usd"] = f"{base + force_pnl + oil_today:.2f}"
        row.update(exp)
        row.update(force)
        rows.append(row)
    return rows, exp_positions, force_positions, core


def _write_dict_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise ValueError(f"Cannot write empty CSV: {path.name}")
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_csvs(rows, exponential_positions, force_positions):
    _write_dict_csv(DAILY_CSV, rows)
    _write_dict_csv(POSITION_CSV, exponential_positions)
    _write_dict_csv(FORCE_POSITION_CSV, force_positions)
    return DAILY_CSV, POSITION_CSV, FORCE_POSITION_CSV


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
    exp = [float(row["exponential_500_pnl_usd"]) for row in rows]
    force = [float(row["force_multiplier_10k_pnl_usd"]) for row in rows]
    oil = [float(row["oil_desk_daily_buy_pnl_usd"]) for row in rows]
    exp_oil = [float(row["exponential_500_plus_oil_pnl_usd"]) for row in rows]
    force_oil = [float(row["force_multiplier_plus_oil_pnl_usd"]) for row in rows]
    exp_composites = {
        variant: [float(row[f"{variant}_plus_exponential_500_pnl_usd"]) for row in rows]
        for variant in VARIANTS
    }
    force_composites = {
        variant: [float(row[f"{variant}_plus_force_multiplier_pnl_usd"]) for row in rows]
        for variant in VARIANTS
    }
    oil_composites = {
        variant: [float(row[f"{variant}_plus_oil_desk_pnl_usd"]) for row in rows]
        for variant in VARIANTS
    }
    exp_oil_composites = {
        variant: [float(row[f"{variant}_plus_exponential_500_and_oil_pnl_usd"]) for row in rows]
        for variant in VARIANTS
    }
    force_oil_composites = {
        variant: [float(row[f"{variant}_plus_force_multiplier_and_oil_pnl_usd"]) for row in rows]
        for variant in VARIANTS
    }
    drawdown_lines = {variant: _drawdown(values) for variant, values in core_lines.items()}
    drawdown_lines["Exponential (500 USD)"] = _drawdown(exp)
    drawdown_lines["Force multiplier (10,000 USD)"] = _drawdown(force)

    panels = [
        ("Core variants and both direction-following sizes", [
            (VARIANT_LABEL[v], core_lines[v], VARIANT_COLORS[v]) for v in VARIANTS
        ] + [("Exponential — 500 USD/EOD", exp, EXP_COLOR), ("Force multiplier — 10,000 USD/EOD", force, FORCE_COLOR)]),
        ("Standalone models and sidecar combinations", [
            ("Exponential — 500 USD/EOD", exp, EXP_COLOR),
            ("Force multiplier — 10,000 USD/EOD", force, FORCE_COLOR),
            ("Oil-desk daily buys", oil, OIL_COLOR),
            ("500 USD model + oil buys", exp_oil, "#a3e635"),
            ("10,000 USD model + oil buys", force_oil, BOTH_COLOR),
        ]),
        ("Each core variant + 500 USD exponential model", [
            (f"{VARIANT_LABEL[v]} + 500 USD", exp_composites[v], VARIANT_COLORS[v]) for v in VARIANTS
        ]),
        ("Each core variant + 10,000 USD force multiplier", [
            (f"{VARIANT_LABEL[v]} + 10,000 USD", force_composites[v], VARIANT_COLORS[v]) for v in VARIANTS
        ]),
        ("Each core variant + oil-desk daily-buy sidecar", [
            (f"{VARIANT_LABEL[v]} + oil desk", oil_composites[v], VARIANT_COLORS[v]) for v in VARIANTS
        ]),
        ("Each core variant + 500 USD model + oil-desk daily buys", [
            (f"{VARIANT_LABEL[v]} + 500 USD + oil", exp_oil_composites[v], VARIANT_COLORS[v]) for v in VARIANTS
        ]),
        ("Each core variant + 10,000 USD force multiplier + oil-desk daily buys", [
            (f"{VARIANT_LABEL[v]} + 10,000 USD + oil", force_oil_composites[v], VARIANT_COLORS[v]) for v in VARIANTS
        ]),
        ("Drawdown from running PnL peak — core and direction-following models", [
            (VARIANT_LABEL[v], drawdown_lines[v], VARIANT_COLORS[v]) for v in VARIANTS
        ] + [("Exponential (500 USD)", drawdown_lines["Exponential (500 USD)"], EXP_COLOR),
             ("Force multiplier (10,000 USD)", drawdown_lines["Force multiplier (10,000 USD)"], FORCE_COLOR)]),
    ]

    fig, axes = plt.subplots(len(panels), 1, figsize=(16, 29), sharex=True)
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
        ax.legend(facecolor="#0d131e", edgecolor="#26344a", labelcolor="#edf2f7", fontsize=8, ncol=3 if len(lines) > 4 else 2)
    axes[-1].set_xlabel("EOD session date", color="#edf2f7")
    axes[-1].tick_params(axis="x", rotation=25)
    fig.suptitle("Core Variants, 500 USD Exponential Model, 10,000 USD Force Multiplier, and Oil Sidecar", color="#edf2f7", fontsize=15)
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    fig.savefig(GRAPH, dpi=150, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close(fig)
    return GRAPH


def write_report(rows):
    last = rows[-1]
    exp_realized = float(last["exponential_realized_pnl_usd"])
    exp_unrealized = float(last["exponential_unrealized_pnl_usd"])
    force_realized = float(last["force_multiplier_realized_pnl_usd"])
    force_unrealized = float(last["force_multiplier_unrealized_pnl_usd"])
    lines = [
        "# Strategy and Sidecar Comparison",
        "",
        "![Core models, both direction-following model sizes, and sidecar combinations](Charts/performance/20-strategy-sidecar-comparison.png)",
        "",
        "Calculation detail for the core variants and daily lot rules: [`Model Calculation Guide.md`](Model%20Calculation%20Guide.md).",
        "",
        "## Model rules and combination math",
        "",
        "- **Core variants:** existing V1, V2, V3A, and V3B model replays from the main comparison.",
        "- **Exponential ($500/EOD):** after a ticker first has a logged direction, add a new fixed **$500 notional** lot in its latest LONG/SHORT/REBUY direction each EOD. $500 does not compound.",
        "- **Force multiplier ($10,000/EOD):** same direction state, EOD additions, and close/reverse rule, but each new tranche is **1 unit = $10,000 notional**. It is an alternative 20× sizing of the $500 model—not an extra tranche stacked on top of it.",
        "- **Direction and reversal:** carry the latest direction-bearing entry tag in `trades/*.txt`; REBUY is LONG. On a direction change, close all prior opposite-direction lots at that EOD close before adding the new tranche. EXIT / TAKE PROFIT events do not clear the direction. Weekend/holiday signals apply at the first priced EOD on or after the event date. The repository has no separate authorization feed.",
        "- **Oil-desk sidecar:** adds only its daily-buy lots to composites. Its chart-opened maintenance positions are already in each core replay and are not counted twice.",
        "- **Composite lines:** each core model is compared with each sizing variant, oil buys, and the two valid model-plus-oil combinations. The two direction-following sizes are alternatives and are never summed together. Composites are additive USD PnL, not capital-normalized account simulations.",
        "- Universe: all 33 directly price-covered core tickers; DXY, EURUSD, JPYUSD, US10Y, and US30Y are outside this price-position comparison.",
        "",
        "## Standalone model and sidecar terminal comparison — Oct. 23, 2026",
        "",
        "| Component/scenario | Terminal PnL | Cumulative notional added | Open notional |",
        "|---|---:|---:|---:|",
    ]
    standalone = [
        ("Exponential — fixed $500/EOD", float(last["exponential_500_pnl_usd"]), float(last["exponential_cumulative_notional_added_usd"]), float(last["exponential_open_notional_usd"])),
        ("Force multiplier — $10,000 / 1 unit per EOD", float(last["force_multiplier_10k_pnl_usd"]), float(last["force_multiplier_cumulative_notional_added_usd"]), float(last["force_multiplier_open_notional_usd"])),
        ("Oil-desk daily-buy add-on", float(last["oil_desk_daily_buy_pnl_usd"]), float(last["oil_desk_cumulative_notional_usd"]), float(last["oil_desk_open_notional_usd"])),
        ("$500 model + oil daily buys", float(last["exponential_500_plus_oil_pnl_usd"]), float(last["exponential_500_plus_oil_cumulative_notional_usd"]), float(last["exponential_500_plus_oil_open_notional_usd"])),
        ("$10,000 model + oil daily buys", float(last["force_multiplier_plus_oil_pnl_usd"]), float(last["force_multiplier_plus_oil_cumulative_notional_usd"]), float(last["force_multiplier_plus_oil_open_notional_usd"])),
    ]
    for name, pnl, added, open_notional in standalone:
        lines.append(f"| {name} | ${pnl:+,.2f} | ${added:,.2f} | ${open_notional:,.2f} |")

    lines.extend([
        "",
        f"The $500 model ends at **${float(last['exponential_500_pnl_usd']):+,.2f}** (realized ${exp_realized:+,.2f}; unrealized ${exp_unrealized:+,.2f}). The force-multiplier model ends at **${float(last['force_multiplier_10k_pnl_usd']):+,.2f}** (realized ${force_realized:+,.2f}; unrealized ${force_unrealized:+,.2f}). With identical direction state and no tranche compounding, force-multiplier PnL and exposure are exactly 20× the $500 model before display rounding.",
        "",
        "## Core variants with add-ons — terminal PnL",
        "",
        "| Core variant | Core only | + $500 model | + $10,000 force multiplier | + oil desk | + $500 and oil | + force multiplier and oil |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ])
    for variant in VARIANTS:
        lines.append(
            f"| {VARIANT_LABEL[variant]} | ${float(last[f'{variant}_core_pnl_usd']):+,.2f} | "
            f"${float(last[f'{variant}_plus_exponential_500_pnl_usd']):+,.2f} | "
            f"${float(last[f'{variant}_plus_force_multiplier_pnl_usd']):+,.2f} | "
            f"${float(last[f'{variant}_plus_oil_desk_pnl_usd']):+,.2f} | "
            f"${float(last[f'{variant}_plus_exponential_500_and_oil_pnl_usd']):+,.2f} | "
            f"${float(last[f'{variant}_plus_force_multiplier_and_oil_pnl_usd']):+,.2f} |"
        )
    lines.extend([
        "",
        "The oil desk sidecar alone adds **$499,705.92** on $5.5M of daily-buy notional, so its scale can dominate the raw-PnL composite panels. Use the cumulative/open notional columns and the drawdown panel when comparing risk and scale; these composites do not apply a common capital base.",
        "",
        "## Data and output files",
        "",
        "- Daily all-strategy PnL and exposure comparison: [`strategy_sidecar_comparison_daily_v1.csv`](data/strategy_sidecar_comparison_daily_v1.csv).",
        "- Exponential $500 per-symbol EOD audit: [`exponential_eod_positions_v1.csv`](data/exponential_eod_positions_v1.csv).",
        "- Force multiplier $10,000 per-symbol EOD audit: [`force_multiplier_eod_positions_v1.csv`](data/force_multiplier_eod_positions_v1.csv).",
        "- Price source map: [`active_price_source_registry_v2.csv`](data/active_price_source_registry_v2.csv); exact energy closes: [`energy_provider_eod_marks_v1.csv`](data/energy_provider_eod_marks_v1.csv).",
        "- Core models: [`Model Performance Comparison.md`](Model%20Performance%20Comparison.md). Oil sidecar assumptions and source rows: [`Oil Desk EOD Accumulation Hypothetical.md`](Oil%20Desk%20EOD%20Accumulation%20Hypothetical.md).",
        "",
        "**Scope note:** new direction-following models and composites are unadjusted USD PnL comparisons; they are not included in the existing whole-portfolio DXY/yield account scenarios. This historical paper-trade replay is not a live system, risk forecast, or investment recommendation.",
    ])
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return REPORT


def main():
    rows, exponential_positions, force_positions, core = comparison_rows()
    write_csvs(rows, exponential_positions, force_positions)
    graph = write_chart(rows)
    report = write_report(rows)
    print(f"Wrote {DAILY_CSV.relative_to(ROOT)}")
    print(f"Wrote {POSITION_CSV.relative_to(ROOT)}")
    print(f"Wrote {FORCE_POSITION_CSV.relative_to(ROOT)}")
    print(f"Wrote {graph.relative_to(ROOT)}")
    print(f"Wrote {report.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
