"""Compare core variants with fixed-$500 and 1-unit EOD direction-following models.

The "Exponential" and "Force Multiplier" labels follow the user's naming. Each
model adds a fixed-notional tranche per EOD: $500 for Exponential and 1U for Force Multiplier. The latest LONG/SHORT/REBUY trade-log direction
carries forward; when it changes, opposite open lots close at that day's EOD.
Energy-sidecar composites add only its daily-buy lots because chart positions already
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
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
ENERGY_SIDECAR_CSV = DATA / "tradingview_energy_sidecar_daily_20261026.csv"
CHARTS = ROOT / "Charts" / "performance"
DAILY_CSV = DATA / "strategy_sidecar_comparison_daily_v1.csv"
POSITION_CSV = DATA / "exponential_eod_positions_v1.csv"
FORCE_POSITION_CSV = DATA / "force_multiplier_eod_positions_v1.csv"
VARIANT_FORCE_POSITION_CSV = DATA / "force_multiplier_variant_eod_positions_v1.csv"
REPORT = ROOT / "Strategy and Sidecar Comparison.md"
GRAPH = CHARTS / "20-strategy-sidecar-comparison.png"
VARIANT_GRAPH = CHARTS / "21-force-variant-oil-comparison.png"
PERCENT_GAIN_GRAPH = CHARTS / "22-force-variant-oil-percent-gain.png"
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


def _return_on_notional_pct(pnl, notional):
    """Format percentage gain using the PnL/notional values displayed in the CSV."""
    pnl = float(f"{pnl:.2f}")
    notional = float(f"{notional:.2f}")
    return f"{pnl / notional * 100:.6f}" if notional > 0 else ""


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
        if (event["date"] > SESSION_DATES[-1] or event["kind"] != "entry"
                or "CORE MODEL ONLY, not a direction signal or daily sidecar action" in event["note"]):
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
    """The shared direction-following alternative, using one 1U per active EOD."""
    return direction_following_daily_model(events, FORCE_MULTIPLIER_TRANCHE_USD, "force_multiplier")


def variant_force_multiplier_daily_model(variant, events=None, return_realized=False):
    """Run a 1U-per-active-EOD model with one core variant's close/size rules.

    Daily additions remain one 1U lot. On a V3A/V3B compounded-short event,
    only that event-day tranche uses the previous full-exit unit count; later
    carried SHORT days return to 1U additions. Generic explicit exits close
    open longs for every variant; lot-scoped Manual-Automatic trims belong only
    to their tagged core lots and are ignored by this separate daily schedule.
    V2/V3B also close shorts on LONG/REBUY events.
    """
    if variant not in VARIANTS:
        raise ValueError(f"Unknown core variant: {variant}")
    events = events if events is not None else parse_trades()
    natural = variant in ("V3A", "V3B")
    sar = variant in ("V2", "V3B")
    events_by_day = defaultdict(list)
    for event in events:
        if event["date"] > SESSION_DATES[-1]:
            continue
        target = bisect.bisect_left(SESSION_DATES, event["date"])
        if target < len(SESSION_DATES):
            events_by_day[SESSION_DATES[target]].append(event)
    for day in events_by_day:
        events_by_day[day].sort(key=lambda e: (e["date"], e["time"], e["sym"], e["order"]))

    symbols = sorted(PRICES)
    current_direction = {}
    lots = {symbol: [] for symbol in symbols}
    last_exit_units = {}
    realized_total = 0.0
    cumulative_added = 0.0
    daily_rows = []
    position_rows = []
    realized_trades = []

    def close_lots(symbol, side, price, day):
        nonlocal realized_total
        for lot in lots[symbol]:
            if lot["open"] and lot["direction"] == side:
                sign = 1.0 if side == "long" else -1.0
                pnl = lot["notional_usd"] * sign * (price / lot["entry_price"] - 1.0)
                realized_total += pnl
                realized_trades.append({
                    "sym": symbol,
                    "date": day,
                    "idx": SESSION_DATES.index(day),
                    "pnl": pnl,
                    "source": f"{variant}_force_1u",
                })
                lot["open"] = False
                lot["close_date"] = day
                lot["close_price"] = price

    for index, day in enumerate(SESSION_DATES):
        event_day_units = {}
        for event in events_by_day.get(day, []):
            symbol = event["sym"]
            if "CORE MODEL ONLY, not a direction signal or daily sidecar action" in event["note"]:
                continue
            if event["kind"] == "exit":
                if "Manual-Automatic target trim" in event["note"]:
                    continue
                last_exit_units[symbol] = float(event["units"])
                close_lots(symbol, "long", float(event["px"]), day)
            elif event["tag"] in {"LONG", "REBUY"}:
                if sar:
                    close_lots(symbol, "short", float(event["px"]), day)
                current_direction[symbol] = "long"
                event_day_units[symbol] = 1.0
            elif event["tag"] == "SHORT":
                tranche_units = 1.0
                if natural and "Compounded short" in event["note"] and last_exit_units.get(symbol, 0) > 1:
                    tranche_units = last_exit_units[symbol]
                current_direction[symbol] = "short"
                event_day_units[symbol] = tranche_units

        daily_adds = 0.0
        for symbol in symbols:
            direction = current_direction.get(symbol)
            tranche_units = event_day_units.get(symbol, 1.0) if direction else 0.0
            if direction:
                price = PRICES[symbol][index]
                notional = tranche_units * UNIT
                lots[symbol].append({
                    "entry_date": day,
                    "entry_price": price,
                    "direction": direction,
                    "units": tranche_units,
                    "notional_usd": notional,
                    "open": True,
                    "close_date": None,
                    "close_price": None,
                })
                cumulative_added += notional
                daily_adds += notional

        unrealized = 0.0
        open_notional = 0.0
        active_symbols = 0
        for symbol in symbols:
            direction = current_direction.get(symbol)
            tranche_units = event_day_units.get(symbol, 1.0) if direction else 0.0
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
                "model": f"force_multiplier_variant_{variant.lower()}",
                "variant": variant,
                "date": day,
                "ticker": symbol,
                "direction": current_direction.get(symbol, ""),
                "eod_close": f"{price:.8f}",
                "daily_tranche_units": f"{tranche_units if direction else 0.0:.2f}",
                "daily_add_notional_usd": f"{tranche_units * UNIT if direction else 0.0:.2f}",
                "open_lot_count": len(symbol_open),
                "open_notional_usd": f"{symbol_open_notional:.2f}",
                "ticker_unrealized_pnl_usd": f"{symbol_unrealized:.2f}",
                "signal_basis": "Trade-log direction with core variant-specific close and size rules",
            })

        daily_rows.append({
            "date": day,
            f"{variant}_force_1u_realized_pnl_usd": f"{realized_total:.2f}",
            f"{variant}_force_1u_unrealized_pnl_usd": f"{unrealized:.2f}",
            f"{variant}_force_1u_pnl_usd": f"{realized_total + unrealized:.2f}",
            f"{variant}_force_1u_cumulative_notional_added_usd": f"{cumulative_added:.2f}",
            f"{variant}_force_1u_open_notional_usd": f"{open_notional:.2f}",
            f"{variant}_force_1u_active_symbols": active_symbols,
            f"{variant}_force_1u_daily_adds_usd": f"{daily_adds:.2f}",
        })
    if return_realized:
        return daily_rows, position_rows, realized_trades
    return daily_rows, position_rows


def oil_sidecar_daily_pnl():
    """Return the 10U TradingView energy schedule PnL/exposure; exclude chart lots."""
    pnl_marks = defaultdict(float)
    notional_marks = defaultdict(float)
    with ENERGY_SIDECAR_CSV.open(newline="", encoding="utf-8") as handle:
        rows = [row for row in csv.DictReader(handle) if float(row["unit_size_u"]) == 10.0]
    if not rows:
        raise ValueError(f"No 10U records found in {ENERGY_SIDECAR_CSV}")
    for row in rows:
        day = row["date"]
        pnl_marks[day] += float(row["daily_buys_unrealized_pnl_usd"])
        notional_marks[day] += float(row["cumulative_daily_buy_notional_usd"])
    pnl_by_date = {}
    notional_by_date = {}
    last_pnl = 0.0
    last_notional = 0.0
    for day in SESSION_DATES:
        if day in pnl_marks:
            last_pnl = pnl_marks[day]
        if day in notional_marks:
            last_notional = notional_marks[day]
        pnl_by_date[day] = last_pnl
        notional_by_date[day] = last_notional
    return pnl_by_date, notional_by_date


def comparison_rows():
    core, events = all_series()
    exp_daily, exp_positions = exponential_daily_model(events)
    force_daily, force_positions = force_multiplier_daily_model(events)
    variant_daily = {}
    variant_positions = []
    for variant in VARIANTS:
        daily, positions = variant_force_multiplier_daily_model(variant, events)
        variant_daily[variant] = daily
        variant_positions.extend(positions)
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
        oil_open_today = oil_notional[day]
        row = {
            "date": day,
            "exponential_500_pnl_usd": f"{exp_pnl:.2f}",
            "force_multiplier_1u_pnl_usd": f"{force_pnl:.2f}",
            "oil_desk_daily_buy_pnl_usd": f"{oil_today:.2f}",
            "exponential_500_plus_oil_pnl_usd": f"{exp_pnl + oil_today:.2f}",
            "force_multiplier_plus_oil_pnl_usd": f"{force_pnl + oil_today:.2f}",
            "oil_desk_cumulative_notional_usd": f"{oil_open_today:.2f}",
            "oil_desk_open_notional_usd": f"{oil_open_today:.2f}",
            "exponential_500_plus_oil_cumulative_notional_usd": f"{exp_added + oil_open_today:.2f}",
            "exponential_500_plus_oil_open_notional_usd": f"{exp_open + oil_open_today:.2f}",
            "force_multiplier_plus_oil_cumulative_notional_usd": f"{force_added + oil_open_today:.2f}",
            "force_multiplier_plus_oil_open_notional_usd": f"{force_open + oil_open_today:.2f}",
        }
        for variant in VARIANTS:
            base = core[variant]["total"][i]
            variant_row = variant_daily[variant][i]
            variant_pnl = float(variant_row[f"{variant}_force_1u_pnl_usd"])
            variant_added = float(variant_row[f"{variant}_force_1u_cumulative_notional_added_usd"])
            variant_open = float(variant_row[f"{variant}_force_1u_open_notional_usd"])
            row[f"{variant}_core_pnl_usd"] = f"{base:.2f}"
            row[f"{variant}_plus_exponential_500_pnl_usd"] = f"{base + exp_pnl:.2f}"
            row[f"{variant}_plus_force_multiplier_pnl_usd"] = f"{base + force_pnl:.2f}"
            row[f"{variant}_plus_oil_desk_pnl_usd"] = f"{base + oil_today:.2f}"
            row[f"{variant}_plus_exponential_500_and_oil_pnl_usd"] = f"{base + exp_pnl + oil_today:.2f}"
            row[f"{variant}_plus_force_multiplier_and_oil_pnl_usd"] = f"{base + force_pnl + oil_today:.2f}"
            row[f"{variant}_force_1u_plus_oil_pnl_usd"] = f"{variant_pnl + oil_today:.2f}"
            row[f"{variant}_force_1u_plus_oil_cumulative_notional_usd"] = f"{variant_added + oil_open_today:.2f}"
            row[f"{variant}_force_1u_plus_oil_open_notional_usd"] = f"{variant_open + oil_open_today:.2f}"
            row.update({key: value for key, value in variant_row.items() if key != "date"})

        for core_variant in VARIANTS:
            core_pnl = float(core[core_variant]["total"][i])
            core_added = float(core[core_variant]["deployed"][i])
            core_open = sum(
                lot["qty"] * UNIT
                for lot in core[core_variant]["lots"]
                if lot["entry_idx"] <= i
                and (lot["close_idx"] is None or i < lot["close_idx"])
            )
            for force_variant in VARIANTS:
                force_variant_row = variant_daily[force_variant][i]
                force_variant_pnl = float(force_variant_row[f"{force_variant}_force_1u_pnl_usd"])
                force_variant_added = float(
                    force_variant_row[f"{force_variant}_force_1u_cumulative_notional_added_usd"]
                )
                force_variant_open = float(force_variant_row[f"{force_variant}_force_1u_open_notional_usd"])
                no_oil_prefix = f"{core_variant}_core_plus_{force_variant}_force_1u"
                no_oil_pnl = core_pnl + force_variant_pnl
                no_oil_added = core_added + force_variant_added
                row[f"{no_oil_prefix}_pnl_usd"] = f"{no_oil_pnl:.2f}"
                row[f"{no_oil_prefix}_cumulative_notional_usd"] = f"{no_oil_added:.2f}"
                row[f"{no_oil_prefix}_open_notional_usd"] = f"{core_open + force_variant_open:.2f}"
                row[f"{no_oil_prefix}_return_on_cumulative_notional_pct"] = _return_on_notional_pct(
                    no_oil_pnl, no_oil_added
                )

                prefix = f"{core_variant}_core_plus_{force_variant}_force_1u_and_oil"
                oil_composite_pnl = no_oil_pnl + oil_today
                oil_composite_added = no_oil_added + oil_open_today
                row[f"{prefix}_pnl_usd"] = f"{oil_composite_pnl:.2f}"
                row[f"{prefix}_cumulative_notional_usd"] = f"{oil_composite_added:.2f}"
                row[f"{prefix}_open_notional_usd"] = f"{core_open + force_variant_open + oil_open_today:.2f}"
                row[f"{prefix}_return_on_cumulative_notional_pct"] = _return_on_notional_pct(
                    oil_composite_pnl, oil_composite_added
                )
        row.update(exp)
        row.update(force)
        rows.append(row)
    return rows, exp_positions, force_positions, variant_positions, core


def _write_dict_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise ValueError(f"Cannot write empty CSV: {path.name}")
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_csvs(rows, exponential_positions, force_positions, variant_positions):
    _write_dict_csv(DAILY_CSV, rows)
    _write_dict_csv(POSITION_CSV, exponential_positions)
    _write_dict_csv(FORCE_POSITION_CSV, force_positions)
    _write_dict_csv(VARIANT_FORCE_POSITION_CSV, variant_positions)
    return DAILY_CSV, POSITION_CSV, FORCE_POSITION_CSV, VARIANT_FORCE_POSITION_CSV


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
    force = [float(row["force_multiplier_1u_pnl_usd"]) for row in rows]
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
    drawdown_lines["Force multiplier (1U)"] = _drawdown(force)

    panels = [
        ("Core variants and both direction-following sizes", [
            (VARIANT_LABEL[v], core_lines[v], VARIANT_COLORS[v]) for v in VARIANTS
        ] + [("Exponential — 500 USD/EOD", exp, EXP_COLOR), ("Force multiplier — 1U/EOD", force, FORCE_COLOR)]),
        ("Standalone models and sidecar combinations", [
            ("Exponential — 500 USD/EOD", exp, EXP_COLOR),
            ("Force multiplier — 1U/EOD", force, FORCE_COLOR),
            ("10U TradingView energy sidecar", oil, OIL_COLOR),
            ("500 USD model + energy sidecar", exp_oil, "#a3e635"),
            ("1U model + energy sidecar", force_oil, BOTH_COLOR),
        ]),
        ("Each core variant + 500 USD exponential model", [
            (f"{VARIANT_LABEL[v]} + 500 USD", exp_composites[v], VARIANT_COLORS[v]) for v in VARIANTS
        ]),
        ("Each core variant + 1U force multiplier", [
            (f"{VARIANT_LABEL[v]} + 1U", force_composites[v], VARIANT_COLORS[v]) for v in VARIANTS
        ]),
        ("Each core variant + 10U TradingView energy sidecar", [
            (f"{VARIANT_LABEL[v]} + energy desk", oil_composites[v], VARIANT_COLORS[v]) for v in VARIANTS
        ]),
        ("Each core variant + 500 USD model + 10U TradingView energy daily buys", [
            (f"{VARIANT_LABEL[v]} + 500 USD + energy sidecar", exp_oil_composites[v], VARIANT_COLORS[v]) for v in VARIANTS
        ]),
        ("Each core variant + 1U force multiplier + 10U TradingView energy daily buys", [
            (f"{VARIANT_LABEL[v]} + 1U + energy sidecar", force_oil_composites[v], VARIANT_COLORS[v]) for v in VARIANTS
        ]),
        ("Drawdown from running PnL peak — core and direction-following models", [
            (VARIANT_LABEL[v], drawdown_lines[v], VARIANT_COLORS[v]) for v in VARIANTS
        ] + [("Exponential (500 USD)", drawdown_lines["Exponential (500 USD)"], EXP_COLOR),
             ("Force multiplier (1U)", drawdown_lines["Force multiplier (1U)"], FORCE_COLOR)]),
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
    fig.suptitle("Core Variants, 500 USD Exponential Model, 1U Force Multiplier, and TradingView Energy Sidecar", color="#edf2f7", fontsize=15)
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    fig.savefig(GRAPH, dpi=150, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close(fig)
    return GRAPH


def write_variant_chart(rows):
    """Plot every core-variant x 1U-variant pairing with the energy sidecar."""
    CHARTS.mkdir(parents=True, exist_ok=True)
    dates = [row["date"] for row in rows]
    fig, axes = plt.subplots(len(VARIANTS), 1, figsize=(16, 16), sharex=True, sharey=True)
    fig.patch.set_facecolor("#0d131e")
    for ax, core_variant in zip(axes, VARIANTS):
        ax.set_facecolor("#141c2b")
        ax.grid(True, color="#26344a", alpha=0.8)
        ax.tick_params(colors="#93a4bd")
        for spine in ax.spines.values():
            spine.set_color("#26344a")
        for force_variant in VARIANTS:
            prefix = f"{core_variant}_core_plus_{force_variant}_force_1u_and_oil"
            values = [float(row[f"{prefix}_pnl_usd"]) for row in rows]
            pairing = " (matching)" if core_variant == force_variant else ""
            matching = core_variant == force_variant
            ax.plot(
                dates,
                values,
                color=VARIANT_COLORS[force_variant],
                linewidth=2.2 if matching else 1.7,
                linestyle="-" if matching else "--",
                label=f"{force_variant} 1U + energy sidecar{pairing}",
            )
        ax.axhline(0, color="#93a4bd", linewidth=0.8)
        ax.set_title(
            f"Core {core_variant} — {VARIANT_LABEL[core_variant]} paired with each 1U force variant",
            color="#edf2f7",
            loc="left",
            fontsize=11,
        )
        ax.set_ylabel("Cumulative PnL (USD)", color="#edf2f7")
        ax.legend(facecolor="#0d131e", edgecolor="#26344a", labelcolor="#edf2f7", fontsize=8, ncol=2)
    axes[-1].set_xlabel("EOD session date", color="#edf2f7")
    axes[-1].tick_params(axis="x", rotation=25)
    fig.suptitle(
        "All Core Variant × 1U Force Variant Pairings + TradingView Energy Sidecar",
        color="#edf2f7",
        fontsize=15,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    fig.savefig(VARIANT_GRAPH, dpi=150, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close(fig)
    return VARIANT_GRAPH


def percent_gain_scenarios(rows):
    """Return the 32 core/force pairings, ranked by terminal PnL/notional-added ratio."""
    last = rows[-1]
    scenarios = []
    for core_variant in VARIANTS:
        for force_variant in VARIANTS:
            for with_oil in (False, True):
                prefix = f"{core_variant}_core_plus_{force_variant}_force_1u"
                if with_oil:
                    prefix += "_and_oil"
                field = f"{prefix}_return_on_cumulative_notional_pct"
                scenarios.append({
                    "core_variant": core_variant,
                    "force_variant": force_variant,
                    "with_oil": with_oil,
                    "field": field,
                    "name": (
                        f"Core {core_variant} + 1U {force_variant} "
                        f"{'with energy sidecar' if with_oil else 'without energy sidecar'}"
                    ),
                    "terminal_pct": float(last[field]) if last[field] else float("-inf"),
                })
    return sorted(scenarios, key=lambda item: item["terminal_pct"], reverse=True)


def write_percent_gain_chart(rows):
    """Plot all 32 core/1U pairings, with and without the energy sidecar."""
    CHARTS.mkdir(parents=True, exist_ok=True)
    dates = [row["date"] for row in rows]
    ranked = percent_gain_scenarios(rows)
    top = ranked[:4]
    top_keys = {
        (item["core_variant"], item["force_variant"], item["with_oil"]): item
        for item in top
    }
    highlight_colors = ("#22d3ee", "#facc15", "#fb7185", "#a78bfa")
    fig, ax = plt.subplots(figsize=(16, 9))
    fig.patch.set_facecolor("#0d131e")
    ax.set_facecolor("#141c2b")
    ax.grid(True, color="#26344a", alpha=0.8)
    ax.tick_params(colors="#93a4bd")
    for spine in ax.spines.values():
        spine.set_color("#26344a")

    highlighted_handles = []
    for scenario in reversed(ranked):
        core_variant = scenario["core_variant"]
        force_variant = scenario["force_variant"]
        with_oil = scenario["with_oil"]
        key = (core_variant, force_variant, with_oil)
        values = [
            float(row[scenario["field"]]) if row[scenario["field"]] else float("nan")
            for row in rows
        ]
        is_top = key in top_keys
        linestyle = "--" if with_oil else "-"
        if is_top:
            rank = next(i for i, item in enumerate(top) if item == scenario)
            label = f"{scenario['name']} ({scenario['terminal_pct']:.2f}%)"
            (line,) = ax.plot(
                dates,
                values,
                color=highlight_colors[rank],
                linewidth=2.7,
                linestyle=linestyle,
                alpha=0.98,
                zorder=4,
                label=label,
            )
            highlighted_handles.append(line)
        else:
            ax.plot(
                dates,
                values,
                color="#9aa7b8",
                linewidth=0.9,
                linestyle=linestyle,
                alpha=0.30,
                zorder=1,
                label="_nolegend_",
            )
    ax.set_title(
        "All 32 Core × 1U/EOD Pairings — Cumulative PnL / Gross Notional Added",
        color="#edf2f7",
        loc="left",
        fontsize=13,
    )
    ax.set_ylabel("Gain on cumulative gross notional added (%)", color="#edf2f7")
    ax.set_xlabel("EOD session date", color="#edf2f7")
    ax.tick_params(axis="x", rotation=25)
    ax.legend(
        handles=highlighted_handles,
        facecolor="#0d131e",
        edgecolor="#26344a",
        labelcolor="#edf2f7",
        fontsize=9,
        loc="best",
    )
    fig.text(
        0.5,
        0.925,
        "All 32 lines are shown; gray lines are other pairings. Solid = no energy sidecar, dashed = energy sidecar included. "
        "Only the top four terminal gain ratios are named.",
        color="#bdc8d8",
        ha="center",
        fontsize=10,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.90))
    fig.savefig(PERCENT_GAIN_GRAPH, dpi=150, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close(fig)
    return PERCENT_GAIN_GRAPH


def write_report(rows):
    last = rows[-1]
    exp_realized = float(last["exponential_realized_pnl_usd"])
    exp_unrealized = float(last["exponential_unrealized_pnl_usd"])
    force_realized = float(last["force_multiplier_realized_pnl_usd"])
    force_unrealized = float(last["force_multiplier_unrealized_pnl_usd"])
    lines = [
        "# Strategy and Sidecar Comparison",
        "",
        "> **TradingView-only refresh — 2026-10-26.** Core comparisons use 31 supplied direct-price symbols plus the chart-directed 1U/DAY/DXY index-return sleeve integrated into each core variant; BTC/ETH are excluded pending recalibration. TradingView sidecar schedules through 2026-10-26 use the same benchmark, with the generic energy add-on held at 10U/DAY. XRH0 includes five flagged carry-forward marks; see the benchmark coverage and session-mark files.",
        "> **Updated Part B source:** the revised user-provided archive corrects LLY's Oct. 20 close to `$1,283.66`, superseding the prior `$12,833.66` row; all strategy/core figures below use the revised mark.",
        "",
        "![Core models, both direction-following model sizes, and sidecar combinations](Charts/performance/20-strategy-sidecar-comparison.png)",
        "",
        "Calculation detail for the core variants and daily lot rules: [`Model Calculation Guide.md`](Model%20Calculation%20Guide.md).",
        "",
        "## Model rules and combination math",
        "",
        "- **Core variants:** existing V1, V2, V3A, and V3B model replays from the main comparison. The core logs also contain separate hypothetical 10U SHORT force-multiplier lots in BRENT at $117 and OIL at $102, modeled at the Oct. 23 target-level EOD trigger (not a verified intraday execution). Their explicit modeled exits are $114.627 BRENT and $100.74 OIL at 2026-10-25 20:35 MST, after the four earlier Oct. 25 replenishments and simultaneous with separate 35U BRENT/34U OIL LONG Weekend Oil buys; the buys count toward weekly supply, but the short closures do not. They raise post-close all-core oil long exposure from 65U BRENT + 66U OIL to 100U each (200U combined). The $115.792 BRENT/$101.74 OIL lots use the user-recalled 17:20–17:25 MST window, modeled at 17:22; the $114.80 BRENT/$101.00 OIL lot times are approximate around 20:00 MST per the user's recollection. These lot-specific exits override SAR only for the two tagged shorts; prices and timings are hypothetical model inputs, not verified executions. The Oct. 25 events and short exits are included in the current core replay through Oct. 26 and remain separate from the preserved Oct. 23 historical baseline. These short positions are part of core, not the energy sidecar.",
        "- **Exponential ($500/EOD):** after a ticker first has a logged direction, add a new fixed **$500 notional** lot in its latest LONG/SHORT/REBUY direction each EOD. $500 does not compound.",
        "- **Shared-direction force multiplier (1U/EOD):** one 1U tranche per symbol with a carried direction each priced EOD; close all prior lots at the EOD mark on any LONG/SHORT flip. This remains a separate alternative to the $500 model.",
        "- **Variant-specific 1U/EOD force family:** four separate daily-addition replays apply V1, V2, V3A, or V3B position handling to the 1U schedule. Explicit EXIT/TAKE PROFIT records close open long lots at their logged prices in all four; the carried direction remains active, so the scheduled EOD addition still occurs. V1/V3A leave opposite-side lots open on direction changes. V2/V3B cover shorts on LONG/REBUY at the logged signal price; as in the core implementation, SHORT does not close open longs. A qualifying V3A/V3B compounded-short entry uses the preceding full-exit unit count for that event-day tranche only; subsequent carried days return to 1U additions.",
        "- **Signal timing:** direction-bearing LONG/SHORT/REBUY events map to the first priced session on or after their log date; the last directional event for a ticker on that session selects the EOD addition direction. EXIT / TAKE PROFIT rows do not clear carried direction. No separate authorization feed exists.",
        "- **Additive comparisons:** each core base already contains the 1U/DAY/DXY index-return sleeve. The comparison adds shared $500/1U alternatives and the 10U TradingView energy schedule; variant-specific force models are shown alone, with energy, and in all 16 core-variant × 1U-variant pairings plus energy. Matching and cross-variant combinations are included. Do not add the DXY 1U sleeve a second time, net positions/capital, duplicate chart-opened energy positions, or stack alternative force models or variant rules.",
        "- Universe: all 31 directly price-covered TradingView core tickers plus DXY as an integrated index-return sleeve; BTC/ETH are pending recalibration, and EURUSD, JPYUSD, US10Y, and US30Y are outside this portfolio comparison.",
        "",
        "## Standalone model and sidecar terminal comparison — Oct. 26, 2026",
        "",
        "| Component/scenario | Terminal PnL | Cumulative notional added | Open notional |",
        "|---|---:|---:|---:|",
    ]
    standalone = [
        ("Exponential — fixed $500/EOD", float(last["exponential_500_pnl_usd"]), float(last["exponential_cumulative_notional_added_usd"]), float(last["exponential_open_notional_usd"])),
        ("Shared-direction force — 1U per EOD", float(last["force_multiplier_1u_pnl_usd"]), float(last["force_multiplier_cumulative_notional_added_usd"]), float(last["force_multiplier_open_notional_usd"])),
        ("10U TradingView energy daily-buy sidecar", float(last["oil_desk_daily_buy_pnl_usd"]), float(last["oil_desk_cumulative_notional_usd"]), float(last["oil_desk_open_notional_usd"])),
        ("$500 model + 10U energy sidecar", float(last["exponential_500_plus_oil_pnl_usd"]), float(last["exponential_500_plus_oil_cumulative_notional_usd"]), float(last["exponential_500_plus_oil_open_notional_usd"])),
        ("1U model + 10U energy sidecar", float(last["force_multiplier_plus_oil_pnl_usd"]), float(last["force_multiplier_plus_oil_cumulative_notional_usd"]), float(last["force_multiplier_plus_oil_open_notional_usd"])),
    ]
    for name, pnl, added, open_notional in standalone:
        lines.append(f"| {name} | ${pnl:+,.2f} | ${added:,.2f} | ${open_notional:,.2f} |")

    lines.extend([
        "",
        f"The $500 model ends at **${float(last['exponential_500_pnl_usd']):+,.2f}** (realized ${exp_realized:+,.2f}; unrealized ${exp_unrealized:+,.2f}). The shared-direction 1U force model ends at **${float(last['force_multiplier_1u_pnl_usd']):+,.2f}** (realized ${force_realized:+,.2f}; unrealized ${force_unrealized:+,.2f}). With identical direction state and no tranche compounding, its PnL and exposure are 20× the $500 model before display rounding.",
        "",
        "## Variant-specific 1U/EOD force models and energy combinations — terminal",
        "",
        "The four separate 1U/EOD models apply V1, V2, V3A, or V3B exit/SAR/short-compounding behavior. The energy sidecar contributes only its daily-buy PnL and gross notional. The graph below covers all 16 core-variant × 1U-variant pairings; each panel fixes the core variant and plots all four 1U models. Matching pairings are labeled, while the cross-variant pairings expose alternative position-management combinations.",
        "",
        "The generated CSV retains legacy `oil` suffixes for compatibility; these now refer to the 10U TradingView energy schedule. All composite PnL/notional figures are additive USD totals. Positions and capital are not netted, and energy chart-opened core positions are not duplicated in the sidecar.",
        "",
        "![All core variant and 1U force variant pairings with energy sidecar](Charts/performance/21-force-variant-oil-comparison.png)",
        "",
        "| 1U/EOD variant rule | Standalone force PnL | Cumulative notional added | Open notional |",
        "|---|---:|---:|---:|",
    ])
    for variant in VARIANTS:
        lines.append(
            f"| {VARIANT_LABEL[variant]} | ${float(last[f'{variant}_force_1u_pnl_usd']):+,.2f} | "
            f"${float(last[f'{variant}_force_1u_cumulative_notional_added_usd']):,.2f} | "
            f"${float(last[f'{variant}_force_1u_open_notional_usd']):,.2f} |"
        )
    lines.extend([
        "",
        "| 1U/EOD variant rule | Force model + energy PnL | Combined cumulative notional | Combined open notional |",
        "|---|---:|---:|---:|",
    ])
    for variant in VARIANTS:
        lines.append(
            f"| {VARIANT_LABEL[variant]} + energy | ${float(last[f'{variant}_force_1u_plus_oil_pnl_usd']):+,.2f} | "
            f"${float(last[f'{variant}_force_1u_plus_oil_cumulative_notional_usd']):,.2f} | "
            f"${float(last[f'{variant}_force_1u_plus_oil_open_notional_usd']):,.2f} |"
        )
    lines.extend([
        "",
        "## All core + 1U force variant pairings + 10U energy schedule — terminal",
        "",
    ])
    for core_variant in VARIANTS:
        lines.extend([
            f"### Core {core_variant} — {VARIANT_LABEL[core_variant]}",
            "",
            f"Core PnL: **${float(last[f'{core_variant}_core_pnl_usd']):+,.2f}**; energy sidecar PnL: **${float(last['oil_desk_daily_buy_pnl_usd']):+,.2f}**.",
            "",
            "| 1U/EOD force variant | Pairing | Force PnL | Composite PnL | Gross cumulative notional | Gross open notional |",
            "|---|---|---:|---:|---:|---:|",
        ])
        for force_variant in VARIANTS:
            prefix = f"{core_variant}_core_plus_{force_variant}_force_1u_and_oil"
            pairing = "Matching" if core_variant == force_variant else "Cross-variant"
            lines.append(
                f"| {VARIANT_LABEL[force_variant]} | {pairing} | "
                f"${float(last[f'{force_variant}_force_1u_pnl_usd']):+,.2f} | "
                f"${float(last[f'{prefix}_pnl_usd']):+,.2f} | "
                f"${float(last[f'{prefix}_cumulative_notional_usd']):,.2f} | "
                f"${float(last[f'{prefix}_open_notional_usd']):,.2f} |"
            )
        lines.append("")
    lines.extend([
        "",
        "## Percent gain across all 32 combinations",
        "",
        "Percent gain is cumulative composite PnL divided by cumulative gross notional added, expressed as a percentage. It is a deployed-notional ratio, not an account return or capital-normalized ROI. The chart plots all 16 core × 1U variant pairings both without energy and with the 10U TradingView energy daily-buy sidecar (32 lines total). Solid lines omit energy; dashed lines include the energy sidecar. The top four terminal gain ratios are named in the legend; the other 28 pairings remain visible in gray.",
        "",
        "![All 32 core and 1U variant pairings with and without energy, shown as percentage gain](Charts/performance/22-force-variant-oil-percent-gain.png)",
        "",
        "| Rank | Pairing | 10U energy sidecar | Terminal gain on cumulative notional added |",
        "|---:|---|---|---:|",
    ])
    for rank, scenario in enumerate(percent_gain_scenarios(rows)[:4], 1):
        lines.append(
            f"| {rank} | Core {scenario['core_variant']} + 1U {scenario['force_variant']} | "
            f"{'Included' if scenario['with_oil'] else 'Omitted'} | {scenario['terminal_pct']:.2f}% |"
        )
    lines.extend([
        "",
        "## Core variants with add-ons — terminal PnL",
        "",
        "| Core variant | Core only | + $500 model | + 1U force multiplier | + energy desk | + $500 and energy | + force multiplier and energy |",
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
        f"The standalone 10U TradingView energy schedule ends at **${float(last['oil_desk_daily_buy_pnl_usd']):+,.2f}** on **${float(last['oil_desk_cumulative_notional_usd']):,.2f}** cumulative daily-buy notional. Use the notional columns when comparing scale; these additive composites do not apply a common capital base.",
        "",
        "## Data and output files",
        "",
        "- Daily all-strategy PnL and exposure comparison: [`strategy_sidecar_comparison_daily_v1.csv`](data/strategy_sidecar_comparison_daily_v1.csv).",
        "- Exponential $500 per-symbol EOD audit: [`exponential_eod_positions_v1.csv`](data/exponential_eod_positions_v1.csv).",
        "- Shared-direction force model audit: [`force_multiplier_eod_positions_v1.csv`](data/force_multiplier_eod_positions_v1.csv).",
        "- Variant-specific 1U EOD position audit: [`force_multiplier_variant_eod_positions_v1.csv`](data/force_multiplier_variant_eod_positions_v1.csv).",
        "- Percent-gain chart for all 32 core/1U pairings with and without energy: [`22-force-variant-oil-percent-gain.png`](Charts/performance/22-force-variant-oil-percent-gain.png).",
        "- Price source map: [`tradingview_benchmark_session_marks_20261026.csv`](data/tradingview_benchmark_session_marks_20261026.csv); sidecar schedule: [`tradingview_energy_sidecar_daily_20261026.csv`](data/tradingview_energy_sidecar_daily_20261026.csv).",
        "- Core models: [`Model Performance Comparison.md`](Model%20Performance%20Comparison.md). Energy schedule and DXY sizing/audit alternatives: [`TradingView Energy and Currency Desk Sidecars.md`](TradingView%20Energy%20and%20Currency%20Desk%20Sidecars.md).",
        "",
        "**Scope note:** new direction-following models and composites are unadjusted USD PnL comparisons; they are not included in the existing whole-portfolio DXY/yield account scenarios. This historical paper-trade replay is not a live system, risk forecast, or investment recommendation.",
    ])
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return REPORT


def main():
    rows, exponential_positions, force_positions, variant_positions, core = comparison_rows()
    write_csvs(rows, exponential_positions, force_positions, variant_positions)
    graph = write_chart(rows)
    variant_graph = write_variant_chart(rows)
    percent_gain_graph = write_percent_gain_chart(rows)
    report = write_report(rows)
    print(f"Wrote {DAILY_CSV.relative_to(ROOT)}")
    print(f"Wrote {POSITION_CSV.relative_to(ROOT)}")
    print(f"Wrote {FORCE_POSITION_CSV.relative_to(ROOT)}")
    print(f"Wrote {VARIANT_FORCE_POSITION_CSV.relative_to(ROOT)}")
    print(f"Wrote {graph.relative_to(ROOT)}")
    print(f"Wrote {variant_graph.relative_to(ROOT)}")
    print(f"Wrote {percent_gain_graph.relative_to(ROOT)}")
    print(f"Wrote {report.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
