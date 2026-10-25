#!/usr/bin/env python3
"""Independently replay and reconcile every actionable ticker through Oct. 23.

This is an audit utility, separate from the report builders. It rebuilds the
four core books including the chart-directed 1U/DAY/DXY sleeve, four
variant-specific 1U/EOD books, shared 1U/EOD book, and fixed-$500/EOD book;
then checks them against generated exports and all 32 composites.
Run with: PYTHONPATH=scripts python3 scripts/audit_actionable_tickers.py
"""

import bisect
import csv
from collections import defaultdict
from pathlib import Path

from daily_closes import OCT23_EOD_FILE
from model_perf_core import DXY_PRICES, PRICES, SESSION_DATES, UNIT, VARIANTS, parse_trades

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
AUDIT_CSV = DATA / "actionable_ticker_reconciliation_20261023_v1.csv"
CENT_TOL = 0.011


def _close(actual, expected, label, tol=CENT_TOL):
    if abs(float(actual) - float(expected)) > tol:
        raise AssertionError(f"{label}: expected {expected:.8f}, got {actual:.8f}")


def _unit_text(value):
    return f"{value:.4f}".rstrip("0").rstrip(".")


def _read_csv(path):
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _close_lots(lots, ticker, side, price, day_idx, realized_by_ticker, realized_by_day):
    for lot in lots[ticker]:
        if lot["open"] and lot["side"] == side:
            sign = 1.0 if side == "long" else -1.0
            pnl = lot["units"] * UNIT * sign * (price / lot["entry_price"] - 1.0)
            lot["open"] = False
            lot["close_idx"] = day_idx
            lot["close_price"] = price
            lot["realized_pnl"] = pnl
            realized_by_ticker[ticker] += pnl
            realized_by_day[day_idx] += pnl


def _dxy_daily_lots_from_export():
    """Independently reconstruct the integrated 1U/DAY DXY sleeve from its audit rows."""
    rows = [row for row in _read_csv(DATA / "dxy_currency_desk_sidecar_daily_20261024.csv")
            if float(row["unit_size_u"]) == 1.0]
    lots = []
    realized = []
    previous_direction = None
    for row in rows:
        idx = SESSION_DATES.index(row["date"])
        direction = row["direction"].lower()
        mark = float(row["eod_close"])
        if previous_direction is not None and direction != previous_direction:
            for lot in lots:
                if lot["open"]:
                    sign = 1.0 if lot["side"] == "long" else -1.0
                    pnl = UNIT * sign * (mark / lot["entry_price"] - 1.0)
                    lot["open"] = False
                    lot["close_idx"] = idx
                    lot["close_price"] = mark
                    lot["realized_pnl"] = pnl
                    realized.append((idx, pnl))
        lots.append({
            "side": direction, "units": 1.0, "entry_price": mark,
            "entry_idx": idx, "close_idx": None, "close_price": None,
            "open": True, "realized_pnl": 0.0,
        })
        previous_direction = direction
    return lots, realized


def _core_replay(variant, events):
    natural = variant in ("V3A", "V3B")
    sar = variant in ("V2", "V3B")
    lots = {ticker: [] for ticker in PRICES}
    lots["DXY"] = []
    realized_by_ticker = defaultdict(float)
    realized_by_day = defaultdict(float)
    last_exit_units = {}

    for event in events:
        if event["date"] > SESSION_DATES[-1]:
            continue
        ticker = event["sym"]
        idx = bisect.bisect_left(SESSION_DATES, event["date"])
        if idx >= len(SESSION_DATES):
            continue
        if event["kind"] == "exit":
            last_exit_units[ticker] = float(event["units"])
            _close_lots(lots, ticker, "long", float(event["px"]), idx,
                        realized_by_ticker, realized_by_day)
        elif event["tag"] == "SHORT":
            units = float(event["units"])
            if natural and "Compounded short" in event["note"] and last_exit_units.get(ticker, 0) > 1:
                units = last_exit_units[ticker]
            lots[ticker].append({
                "side": "short", "units": units, "entry_price": float(event["px"]),
                "entry_idx": idx, "close_idx": None, "close_price": None,
                "open": True, "realized_pnl": 0.0,
            })
        else:  # LONG / REBUY
            if sar:
                _close_lots(lots, ticker, "short", float(event["px"]), idx,
                            realized_by_ticker, realized_by_day)
            lots[ticker].append({
                "side": "long", "units": float(event["units"]),
                "entry_price": float(event["px"]), "entry_idx": idx,
                "close_idx": None, "close_price": None, "open": True,
                "realized_pnl": 0.0,
            })

    dxy_lots, dxy_realized = _dxy_daily_lots_from_export()
    lots["DXY"] = dxy_lots
    for idx, pnl in dxy_realized:
        realized_by_ticker["DXY"] += pnl
        realized_by_day[idx] += pnl

    daily = []
    for idx, day in enumerate(SESSION_DATES):
        realized = sum(value for close_idx, value in
                       ((lot["close_idx"], lot["realized_pnl"])
                        for ticker_lots in lots.values() for lot in ticker_lots)
                       if close_idx is not None and close_idx <= idx)
        unrealized = 0.0
        deployed = 0.0
        open_notional = 0.0
        open_units = 0.0
        for ticker, ticker_lots in lots.items():
            price = DXY_PRICES[idx] if ticker == "DXY" else PRICES[ticker][idx]
            for lot in ticker_lots:
                if lot["entry_idx"] <= idx:
                    deployed += lot["units"] * UNIT
                if lot["entry_idx"] <= idx and (lot["close_idx"] is None or idx < lot["close_idx"]):
                    sign = 1.0 if lot["side"] == "long" else -1.0
                    unrealized += lot["units"] * UNIT * sign * (price / lot["entry_price"] - 1.0)
                    open_notional += lot["units"] * UNIT
                    open_units += lot["units"]
        daily.append({
            "date": day, "realized": realized, "unrealized": unrealized,
            "total": realized + unrealized, "deployed": deployed,
            "open_notional": open_notional, "open_units": open_units,
        })
    return lots, realized_by_ticker, daily


def _variant_force_replay(variant, events):
    natural = variant in ("V3A", "V3B")
    sar = variant in ("V2", "V3B")
    by_day = defaultdict(list)
    for event in events:
        if event["date"] > SESSION_DATES[-1]:
            continue
        idx = bisect.bisect_left(SESSION_DATES, event["date"])
        if idx < len(SESSION_DATES):
            by_day[SESSION_DATES[idx]].append(event)
    for day in by_day:
        by_day[day].sort(key=lambda event: (event["date"], event["time"], event["sym"], event["order"]))

    directions = {}
    lots = {ticker: [] for ticker in PRICES}
    realized_by_ticker = defaultdict(float)
    realized_by_day = defaultdict(float)
    last_exit_units = {}
    daily = []
    position_rows = []
    cumulative_added = 0.0

    for idx, day in enumerate(SESSION_DATES):
        event_day_units = {}
        for event in by_day.get(day, []):
            ticker = event["sym"]
            if event["kind"] == "exit":
                last_exit_units[ticker] = float(event["units"])
                _close_lots(lots, ticker, "long", float(event["px"]), idx,
                            realized_by_ticker, realized_by_day)
            elif event["tag"] in {"LONG", "REBUY"}:
                if sar:
                    _close_lots(lots, ticker, "short", float(event["px"]), idx,
                                realized_by_ticker, realized_by_day)
                directions[ticker] = "long"
                event_day_units[ticker] = 1.0
            elif event["tag"] == "SHORT":
                units = 1.0
                if natural and "Compounded short" in event["note"] and last_exit_units.get(ticker, 0) > 1:
                    units = last_exit_units[ticker]
                directions[ticker] = "short"
                event_day_units[ticker] = units

        daily_adds = 0.0
        for ticker, direction in directions.items():
            units = event_day_units.get(ticker, 1.0)
            lots[ticker].append({
                "side": direction, "units": units, "entry_price": PRICES[ticker][idx],
                "entry_idx": idx, "close_idx": None, "close_price": None,
                "open": True, "realized_pnl": 0.0,
            })
            daily_adds += units * UNIT
            cumulative_added += units * UNIT

        realized = sum(realized_by_day[close_idx] for close_idx in range(idx + 1))
        unrealized = 0.0
        open_notional = 0.0
        active_symbols = 0
        per_ticker_unrealized = {}
        for ticker, ticker_lots in lots.items():
            price = PRICES[ticker][idx]
            open_lots = [lot for lot in ticker_lots if lot["open"] and lot["entry_idx"] <= idx]
            ticker_unrealized = sum(
                lot["units"] * UNIT * (1 if lot["side"] == "long" else -1)
                * (price / lot["entry_price"] - 1.0)
                for lot in open_lots
            )
            per_ticker_unrealized[ticker] = ticker_unrealized
            unrealized += ticker_unrealized
            if open_lots:
                active_symbols += 1
            open_notional += sum(lot["units"] * UNIT for lot in open_lots)
            position_rows.append({
                "variant": variant, "date": day, "ticker": ticker,
                "direction": directions.get(ticker, ""),
                "eod_close": price,
                "daily_tranche_units": event_day_units.get(ticker, 1.0) if ticker in directions else 0.0,
                "daily_add_notional": (event_day_units.get(ticker, 1.0) if ticker in directions else 0.0) * UNIT,
                "open_lot_count": len(open_lots),
                "open_notional": sum(lot["units"] * UNIT for lot in open_lots),
                "unrealized": ticker_unrealized,
            })
        daily.append({
            "date": day, "realized": realized, "unrealized": unrealized,
            "total": realized + unrealized, "added": cumulative_added,
            "daily_adds": daily_adds, "open_notional": open_notional,
            "active_symbols": active_symbols,
        })
    return lots, realized_by_ticker, daily, position_rows


def _direction_force_replay(events, tranche_notional):
    by_day = defaultdict(list)
    for event in events:
        if event["date"] > SESSION_DATES[-1] or event["kind"] != "entry":
            continue
        direction = "long" if event["tag"] in {"LONG", "REBUY"} else "short" if event["tag"] == "SHORT" else None
        if direction is None:
            continue
        idx = bisect.bisect_left(SESSION_DATES, event["date"])
        if idx < len(SESSION_DATES):
            by_day[SESSION_DATES[idx]].append((event, direction))
    for day in by_day:
        by_day[day].sort(key=lambda pair: (pair[0]["date"], pair[0]["time"], pair[0]["sym"], pair[0]["order"]))

    directions = {}
    lots = {ticker: [] for ticker in PRICES}
    realized_by_ticker = defaultdict(float)
    realized_by_day = defaultdict(float)
    daily, position_rows = [], []
    cumulative_added = 0.0

    for idx, day in enumerate(SESSION_DATES):
        day_signals = {}
        for event, direction in by_day.get(day, []):
            day_signals[event["sym"]] = direction
        for ticker, direction in day_signals.items():
            previous = directions.get(ticker)
            if previous is not None and previous != direction:
                _close_lots(lots, ticker, previous, PRICES[ticker][idx], idx,
                            realized_by_ticker, realized_by_day)
            directions[ticker] = direction

        daily_adds = 0.0
        for ticker, direction in directions.items():
            lots[ticker].append({
                "side": direction, "units": tranche_notional / UNIT,
                "entry_price": PRICES[ticker][idx], "entry_idx": idx,
                "close_idx": None, "close_price": None, "open": True,
                "realized_pnl": 0.0,
            })
            daily_adds += tranche_notional
            cumulative_added += tranche_notional

        realized = sum(realized_by_day[close_idx] for close_idx in range(idx + 1))
        unrealized = 0.0
        open_notional = 0.0
        active_symbols = 0
        for ticker, ticker_lots in lots.items():
            open_lots = [lot for lot in ticker_lots if lot["open"] and lot["entry_idx"] <= idx]
            price = PRICES[ticker][idx]
            ticker_unrealized = sum(
                lot["units"] * UNIT * (1 if lot["side"] == "long" else -1)
                * (price / lot["entry_price"] - 1.0)
                for lot in open_lots
            )
            unrealized += ticker_unrealized
            open_notional += sum(lot["units"] * UNIT for lot in open_lots)
            if open_lots:
                active_symbols += 1
            position_rows.append({
                "date": day, "ticker": ticker, "direction": directions.get(ticker, ""),
                "eod_close": price, "daily_add_notional": tranche_notional if ticker in directions else 0.0,
                "open_lot_count": len(open_lots),
                "open_notional": sum(lot["units"] * UNIT for lot in open_lots),
                "unrealized": ticker_unrealized,
            })
        daily.append({
            "date": day, "realized": realized, "unrealized": unrealized,
            "total": realized + unrealized, "added": cumulative_added,
            "daily_adds": daily_adds, "open_notional": open_notional,
            "active_symbols": active_symbols,
        })
    return lots, realized_by_ticker, daily, position_rows


def terminal_ticker_metrics(lots, realized_by_ticker):
    terminal_idx = len(SESSION_DATES) - 1
    rows = {}
    for ticker, ticker_lots in lots.items():
        realized = realized_by_ticker[ticker]
        unrealized = 0.0
        deployed_units = sum(lot["units"] for lot in ticker_lots)
        open_lots = [lot for lot in ticker_lots if lot["open"]]
        for lot in open_lots:
            sign = 1.0 if lot["side"] == "long" else -1.0
            unrealized += lot["units"] * UNIT * sign * (
                (DXY_PRICES[terminal_idx] if ticker == "DXY" else PRICES[ticker][terminal_idx]) / lot["entry_price"] - 1.0
            )
        rows[ticker] = {
            "realized": realized,
            "unrealized": unrealized,
            "total": realized + unrealized,
            "deployed_units": deployed_units,
            "open_units": sum(lot["units"] for lot in open_lots),
            "open_lots": len(open_lots),
            "open_notional": sum(lot["units"] * UNIT for lot in open_lots),
        }
    return rows


def _audit_price_sources(events):
    """Validate the active user-supplied TradingView universe and marks."""
    mark_rows = _read_csv(DATA / "tradingview_benchmark_session_marks_20261024.csv")
    by_ticker_day = {(row["Ticker"], row["Date"]): row for row in mark_rows}
    symbols = set(PRICES)
    expected_sessions = set(SESSION_DATES)
    if len(symbols) != 31 or len(SESSION_DATES) != 36:
        raise AssertionError(f"Unexpected TradingView core/session count: {len(symbols)}/{len(SESSION_DATES)}")
    if symbols & {"BTC", "ETH", "DXY"}:
        raise AssertionError("BTC/ETH and DXY must remain outside the direct-price core")
    if not {"DXY"}.issubset({ticker for ticker, _ in by_ticker_day}):
        raise AssertionError("DXY currency-desk marks are missing")
    if {ticker for ticker, _ in by_ticker_day} & {"BTC", "ETH"}:
        raise AssertionError("Pending crypto marks must not enter the benchmark session file")
    for ticker, series in PRICES.items():
        if len(series) != len(SESSION_DATES) or any(price <= 0 for price in series):
            raise AssertionError(f"Invalid price path for {ticker}")
        for idx, day in enumerate(SESSION_DATES):
            row = by_ticker_day.get((ticker, day))
            if row is None:
                raise AssertionError(f"Benchmark mark missing for {ticker} {day}")
            _close(series[idx], float(row["Close"]), f"{ticker} TradingView mark {day}", tol=1e-8)
    for ticker in (set(PRICES) | {"DXY"}):
        dates = {day for symbol, day in by_ticker_day if symbol == ticker}
        if dates != expected_sessions:
            raise AssertionError(f"{ticker} benchmark session set differs from the core calendar")
    xrh0_carries = [row for row in mark_rows if row["Ticker"] == "XRH0" and row["Mark_Status"].startswith("carry_forward_")]
    if len(xrh0_carries) != 5:
        raise AssertionError(f"Expected five explicitly flagged XRH0 carries, got {len(xrh0_carries)}")

    actionable = {event["sym"] for event in events}
    if actionable != symbols:
        raise AssertionError(f"Actionable symbols and priced symbols differ: {actionable ^ symbols}")
    eod = {ticker: {"EOD_Close": f"{PRICES[ticker][-1]:.8f}"} for ticker in symbols}
    registry = {ticker: {"2026-10-23_Source": by_ticker_day[(ticker, SESSION_DATES[-1])]["Source_File"]}
                for ticker in symbols}
    return eod, registry, mark_rows


def _audit_daily_exports(core_daily, force_daily, shared_daily, fixed_daily):
    daily_rows = _read_csv(DATA / "model_performance_daily.csv")
    keymap = {(row["variant"], row["session_date"]): row for row in daily_rows}
    if len(keymap) != len(VARIANTS) * len(SESSION_DATES):
        raise AssertionError("Core daily export has an unexpected row count")
    for variant in VARIANTS:
        for idx, expected in enumerate(core_daily[variant]):
            row = keymap[(variant, expected["date"])]
            for field, actual in (("realized_cum_usd", expected["realized"]),
                                  ("total_pnl_usd", expected["total"]),
                                  ("deployed_usd", expected["deployed"]),
                                  ("open_units", expected["open_units"])):
                _close(float(row[field]), actual, f"core {variant} {expected['date']} {field}")
            _close(float(row["unrealized_usd"]), expected["unrealized"],
                   f"core {variant} {expected['date']} unrealized", tol=0.02)

    strategy = _read_csv(DATA / "strategy_sidecar_comparison_daily_v1.csv")
    if len(strategy) != len(SESSION_DATES):
        raise AssertionError("Strategy daily export has an unexpected row count")
    shared_fields = {
        "force_multiplier": "force_multiplier",
        "exponential": "exponential",
    }
    for idx, row in enumerate(strategy):
        if row["date"] != SESSION_DATES[idx]:
            raise AssertionError(f"Strategy daily date mismatch at index {idx}")
        for model, daily in (("force_multiplier", shared_daily), ("exponential", fixed_daily)):
            expected = daily[idx]
            for suffix, key in (("realized_pnl_usd", "realized"),
                                ("unrealized_pnl_usd", "unrealized"),
                                ("total_pnl_usd", "total"),
                                ("cumulative_notional_added_usd", "added"),
                                ("open_notional_usd", "open_notional"),
                                ("daily_adds_usd", "daily_adds"),
                                ("active_symbols", "active_symbols")):
                _close(float(row[f"{model}_{suffix}"]), expected[key],
                       f"{model} {expected['date']} {suffix}", tol=0.02)
        for variant in VARIANTS:
            expected = force_daily[variant][idx]
            for suffix, key in (("realized_pnl_usd", "realized"),
                                ("unrealized_pnl_usd", "unrealized"),
                                ("pnl_usd", "total"),
                                ("cumulative_notional_added_usd", "added"),
                                ("open_notional_usd", "open_notional"),
                                ("daily_adds_usd", "daily_adds"),
                                ("active_symbols", "active_symbols")):
                _close(float(row[f"{variant}_force_1u_{suffix}"]), expected[key],
                       f"{variant} force {expected['date']} {suffix}", tol=0.02)
    return strategy


def _audit_position_exports(force_positions, shared_positions, fixed_positions):
    sources = [
        ("force_multiplier_variant_eod_positions_v1.csv", force_positions, "variant"),
        ("force_multiplier_eod_positions_v1.csv", shared_positions, None),
        ("exponential_eod_positions_v1.csv", fixed_positions, None),
    ]
    for filename, expected_rows, variant_key in sources:
        actual_rows = _read_csv(DATA / filename)
        actual = {}
        for row in actual_rows:
            key = (row[variant_key], row["date"], row["ticker"]) if variant_key else (row["date"], row["ticker"])
            actual[key] = row
        if len(actual) != len(expected_rows):
            raise AssertionError(f"{filename} row count mismatch: {len(actual)} vs {len(expected_rows)}")
        for expected in expected_rows:
            key = ((expected[variant_key], expected["date"], expected["ticker"])
                   if variant_key else (expected["date"], expected["ticker"]))
            row = actual[key]
            if row["direction"] != expected["direction"]:
                raise AssertionError(f"{filename} {key} direction: {row['direction']!r} vs {expected['direction']!r}")
            if int(row["open_lot_count"]) != int(expected["open_lot_count"]):
                raise AssertionError(f"{filename} {key} open_lot_count: {row['open_lot_count']} vs {expected['open_lot_count']}")
            if variant_key:
                for field in ("eod_close", "daily_tranche_units", "daily_add_notional_usd",
                              "open_notional_usd", "ticker_unrealized_pnl_usd"):
                    _close(float(row[field]), float(expected[{
                        "eod_close": "eod_close", "daily_tranche_units": "daily_tranche_units",
                        "daily_add_notional_usd": "daily_add_notional",
                        "open_notional_usd": "open_notional", "ticker_unrealized_pnl_usd": "unrealized",
                    }[field]]), f"{filename} {key} {field}", tol=0.02)
            else:
                for field, key_name in (("eod_close", "eod_close"),
                                        ("daily_add_notional_usd", "daily_add_notional"),
                                        ("open_notional_usd", "open_notional"),
                                        ("ticker_unrealized_pnl_usd", "unrealized")):
                    _close(float(row[field]), float(expected[key_name]),
                           f"{filename} {key} {field}", tol=0.02)


def _audit_energy_sidecar(benchmark_rows):
    """Reconcile all 0.05U/1U/10U daily energy schedules to supplied marks."""
    benchmark = {(row["Ticker"], row["Date"]): row for row in benchmark_rows}
    rows = _read_csv(DATA / "tradingview_energy_sidecar_daily_20261024.csv")
    if len(rows) != 165:
        raise AssertionError(f"Expected 165 energy sidecar rows, got {len(rows)}")
    groups = defaultdict(list)
    for row in rows:
        size = float(row["unit_size_u"])
        ticker, day = row["ticker"], row["date"]
        source = benchmark.get((ticker, day))
        if size not in (0.05, 1.0, 10.0) or ticker not in ("BRENT", "OIL") or source is None:
            raise AssertionError(f"Unexpected energy sidecar record {size}/{ticker}/{day}")
        mark = float(source["Close"])
        if abs(float(row["eod_close"]) - mark) > 1e-8:
            raise AssertionError(f"Energy sidecar mark mismatch {ticker} {day}")
        if row["mark_status"] != source["Mark_Status"] or row["source_file"] != source["Source_File"]:
            raise AssertionError(f"Energy sidecar provenance mismatch {ticker} {day}")
        groups[(size, ticker)].append(row)
    for (size, ticker), schedule in groups.items():
        schedule.sort(key=lambda row: row["date"])
        notional = size * UNIT
        entry_prices = []
        for count, row in enumerate(schedule, 1):
            mark = float(row["eod_close"])
            entry_prices.append(mark)
            expected_pnl = sum(notional * (mark / price - 1.0) for price in entry_prices)
            _close(float(row["daily_buy_notional_usd"]), notional, f"energy daily buy {ticker} {row['date']}")
            _close(float(row["cumulative_daily_buy_notional_usd"]), count * notional,
                   f"energy cumulative notional {ticker} {row['date']}")
            _close(float(row["daily_buys_unrealized_pnl_usd"]), round(expected_pnl, 2),
                   f"energy daily-buy PnL {ticker} {row['date']}")
    if set(size for size, _ in groups) != {0.05, 1.0, 10.0}:
        raise AssertionError("The energy sidecar must contain all 0.05U, 1U, and 10U alternatives")
    return len(rows)


def _audit_dxy_sidecar(benchmark_rows):
    """Reconcile the separate DXY currency-desk schedule and its three sizes."""
    benchmark = {(row["Ticker"], row["Date"]): row for row in benchmark_rows}
    rows = _read_csv(DATA / "dxy_currency_desk_sidecar_daily_20261024.csv")
    if len(rows) != 105:
        raise AssertionError(f"Expected 105 DXY sidecar rows, got {len(rows)}")
    groups = defaultdict(list)
    for row in rows:
        size = float(row["unit_size_u"])
        day = row["date"]
        source = benchmark.get(("DXY", day))
        if size not in (0.05, 1.0, 10.0) or row["ticker"] != "DXY" or source is None:
            raise AssertionError(f"Unexpected DXY sidecar record {size}/{day}")
        if abs(float(row["eod_close"]) - float(source["Close"])) > 1e-8:
            raise AssertionError(f"DXY sidecar mark mismatch on {day}")
        if row["mark_status"] != source["Mark_Status"] or row["source_file"] != source["Source_File"]:
            raise AssertionError(f"DXY sidecar provenance mismatch on {day}")
        groups[size].append(row)
    if set(groups) != {0.05, 1.0, 10.0}:
        raise AssertionError("DXY sidecar must contain 0.05U, 1U, and 10U alternatives")
    for size, schedule in groups.items():
        schedule.sort(key=lambda row: row["date"])
        notional = size * UNIT
        entry_prices = []
        for count, row in enumerate(schedule, 1):
            mark = float(row["eod_close"])
            entry_prices.append(mark)
            expected_pnl = sum(notional * (mark / price - 1.0) for price in entry_prices)
            _close(float(row["daily_investment_notional_usd"]), notional,
                   f"DXY daily investment {row['date']}")
            _close(float(row["cumulative_notional_added_usd"]), count * notional,
                   f"DXY cumulative investment {row['date']}")
            _close(float(row["daily_investment_unrealized_pnl_usd"]), round(expected_pnl, 2),
                   f"DXY sidecar PnL {size}U {row['date']}")
    return len(rows)


def _audit_composites(core_daily, force_daily, shared_daily, fixed_daily):
    strategy = _read_csv(DATA / "strategy_sidecar_comparison_daily_v1.csv")
    energy = [row for row in _read_csv(DATA / "tradingview_energy_sidecar_daily_20261024.csv")
              if float(row["unit_size_u"]) == 10.0]
    energy_by_day = defaultdict(list)
    for energy_row in energy:
        energy_by_day[energy_row["date"]].append(energy_row)
    oil_pnl_by_day = {}
    oil_added_by_day = {}
    oil_open_by_day = {}
    last_pnl = last_added = last_open = 0.0
    for day in SESSION_DATES:
        if day in energy_by_day:
            day_rows = energy_by_day[day]
            last_pnl = sum(float(row["daily_buys_unrealized_pnl_usd"]) for row in day_rows)
            last_added = sum(float(row["cumulative_daily_buy_notional_usd"]) for row in day_rows)
            last_open = last_added
        oil_pnl_by_day[day] = last_pnl
        oil_added_by_day[day] = last_added
        oil_open_by_day[day] = last_open

    aggregate_rows = _read_csv(DATA / "the_one_model_split_portfolios_v1.csv")
    if len(aggregate_rows) != len(SESSION_DATES):
        raise AssertionError("THE ONE MODEL aggregate has an unexpected row count")
    for idx, (row, split_row) in enumerate(zip(strategy, aggregate_rows)):
        day = SESSION_DATES[idx]
        aggregate_pnl = aggregate_added = aggregate_open = 0.0
        for core_variant in VARIANTS:
            core = core_daily[core_variant][idx]
            for force_variant in VARIANTS:
                force = force_daily[force_variant][idx]
                prefix = f"{core_variant}_core_plus_{force_variant}_force_1u"
                for with_oil in (False, True):
                    suffix = "_and_oil" if with_oil else ""
                    actual_pnl = float(row[f"{prefix}{suffix}_pnl_usd"])
                    actual_added = float(row[f"{prefix}{suffix}_cumulative_notional_usd"])
                    actual_open = float(row[f"{prefix}{suffix}_open_notional_usd"])
                    # Match the public composite's documented presentation boundary:
                    # force and oil input series are stored to cents before addition.
                    expected_pnl = round(core["total"] + float(f"{force['total']:.2f}"), 2)
                    if with_oil:
                        expected_pnl = round(expected_pnl + oil_pnl_by_day[day], 2)
                    expected_added = core["deployed"] + force["added"] + (oil_added_by_day[day] if with_oil else 0.0)
                    expected_open = core["open_notional"] + force["open_notional"] + (oil_open_by_day[day] if with_oil else 0.0)
                    _close(actual_pnl, expected_pnl, f"composite {prefix}{suffix} {day}", tol=0.03)
                    _close(actual_added, expected_added, f"composite additions {prefix}{suffix} {day}", tol=0.02)
                    _close(actual_open, expected_open, f"composite open notional {prefix}{suffix} {day}", tol=0.02)
                    aggregate_pnl += expected_pnl
                    aggregate_added += expected_added
                    aggregate_open += expected_open
        _close(float(split_row["aggregate_pnl_usd"]), aggregate_pnl, f"32-book aggregate PnL {day}", tol=0.03)
        _close(float(split_row["aggregate_cumulative_notional_added_usd"]), aggregate_added,
               f"32-book aggregate additions {day}", tol=0.03)
        _close(float(split_row["aggregate_open_notional_usd"]), aggregate_open,
               f"32-book aggregate open notional {day}", tol=0.03)
    return aggregate_rows


def audit_all():
    events = parse_trades()
    eod, registry, energy = _audit_price_sources(events)
    event_counts = defaultdict(int)
    event_dates = defaultdict(list)
    for event in events:
        event_counts[event["sym"]] += 1
        event_dates[event["sym"]].append(event["date"])

    core_lots = {}
    core_realized = {}
    core_daily = {}
    for variant in VARIANTS:
        core_lots[variant], core_realized[variant], core_daily[variant] = _core_replay(variant, events)

    force_lots = {}
    force_realized = {}
    force_daily = {}
    force_positions = []
    for variant in VARIANTS:
        force_lots[variant], force_realized[variant], force_daily[variant], rows = _variant_force_replay(variant, events)
        force_positions.extend(rows)

    shared_lots, shared_realized, shared_daily, shared_positions = _direction_force_replay(events, UNIT)
    fixed_lots, fixed_realized, fixed_daily, fixed_positions = _direction_force_replay(events, 500.0)

    strategy_rows = _audit_daily_exports(core_daily, force_daily, shared_daily, fixed_daily)
    _audit_position_exports(force_positions, shared_positions, fixed_positions)
    energy_rows = _audit_energy_sidecar(energy)
    dxy_sidecar_rows = _audit_dxy_sidecar(energy)
    aggregate_rows = _audit_composites(core_daily, force_daily, shared_daily, fixed_daily)

    expected_daily = _read_csv(DATA / "model_performance_daily.csv")
    daily_lookup = {(row["variant"], row["session_date"]): row for row in expected_daily}
    for variant in VARIANTS:
        for idx, expected in enumerate(core_daily[variant]):
            row = daily_lookup[(variant, expected["date"])]
            _close(float(row["total_pnl_usd"]), expected["total"], f"core export {variant} {expected['date']}")

    ticker_export = {(row["variant"], row["ticker"]): row for row in _read_csv(DATA / "model_performance_tickers.csv")}
    audit_rows = []
    for ticker in sorted(set(PRICES) | {"DXY"}):
        if ticker == "DXY":
            dxy_log_events = [line for line in (ROOT / "trades/DXY.txt").read_text(encoding="utf-8").splitlines()
                              if line.strip() and not line.lstrip().startswith("#")]
            dxy_source = next(row for row in energy if row["Ticker"] == "DXY" and row["Date"] == SESSION_DATES[-1])
            row = {
                "Ticker": "DXY",
                "Trade_Log_Events": len(dxy_log_events),
                "First_Trade_Date": dxy_log_events[0][:10],
                "Last_Trade_Date": dxy_log_events[-1][:10],
                "Oct23_Close": f"{DXY_PRICES[-1]:.8f}",
                "Oct23_Source": dxy_source["Source_File"],
            }
        else:
            row = {
                "Ticker": ticker,
                "Trade_Log_Events": event_counts[ticker],
                "First_Trade_Date": min(event_dates[ticker]),
                "Last_Trade_Date": max(event_dates[ticker]),
                "Oct23_Close": f"{PRICES[ticker][-1]:.8f}",
                "Oct23_Source": registry[ticker]["2026-10-23_Source"],
            }
        for variant in VARIANTS:
            core_summary = terminal_ticker_metrics(core_lots[variant], core_realized[variant])[ticker]
            source_ticker = ticker_export[(variant, ticker)]
            for field, value in (("realized_usd", core_summary["realized"]),
                                 ("unrealized_usd", core_summary["unrealized"]),
                                 ("total_usd", core_summary["total"]),
                                 ("units_deployed", core_summary["deployed_units"])):
                _close(float(source_ticker[field]), float(f"{value:.2f}"),
                       f"ticker export {variant} {ticker} {field}", tol=0.02)
            if ticker == "DXY":
                prefix = f"{variant}_Core"
                row.update({
                    f"{prefix}_Realized_USD": f"{core_summary['realized']:.2f}",
                    f"{prefix}_Unrealized_USD": f"{core_summary['unrealized']:.2f}",
                    f"{prefix}_Total_USD": f"{core_summary['total']:.2f}",
                    f"{prefix}_Units_Added": _unit_text(core_summary["deployed_units"]),
                    f"{prefix}_Open_Units": _unit_text(core_summary["open_units"]),
                    f"{prefix}_Open_Lots": core_summary["open_lots"],
                    f"{prefix}_Open_Notional_USD": f"{core_summary['open_notional']:.2f}",
                })
                continue
            force_summary = terminal_ticker_metrics(force_lots[variant], force_realized[variant])[ticker]
            exp_summary = terminal_ticker_metrics(fixed_lots, fixed_realized)[ticker]
            shared_summary = terminal_ticker_metrics(shared_lots, shared_realized)[ticker]
            for model, summary in (("Core", core_summary), ("Variant_1U_EOD", force_summary)):
                prefix = f"{variant}_{model}"
                row.update({
                    f"{prefix}_Realized_USD": f"{summary['realized']:.2f}",
                    f"{prefix}_Unrealized_USD": f"{summary['unrealized']:.2f}",
                    f"{prefix}_Total_USD": f"{summary['total']:.2f}",
                    f"{prefix}_Units_Added": _unit_text(summary["deployed_units"]),
                    f"{prefix}_Open_Units": _unit_text(summary["open_units"]),
                    f"{prefix}_Open_Lots": summary["open_lots"],
                    f"{prefix}_Open_Notional_USD": f"{summary['open_notional']:.2f}",
                })
            if variant == "V1":
                for model, summary in (("Shared_1U_EOD", shared_summary), ("Fixed_500_EOD", exp_summary)):
                    row.update({
                        f"{model}_Realized_USD": f"{summary['realized']:.2f}",
                        f"{model}_Unrealized_USD": f"{summary['unrealized']:.2f}",
                        f"{model}_Total_USD": f"{summary['total']:.2f}",
                        f"{model}_Units_Added": _unit_text(summary["deployed_units"]),
                        f"{model}_Open_Units": _unit_text(summary["open_units"]),
                        f"{model}_Open_Lots": summary["open_lots"],
                        f"{model}_Open_Notional_USD": f"{summary['open_notional']:.2f}",
                    })
        audit_rows.append(row)

    # A compact final check: ticker attributions must reconcile to each model's
    # terminal PnL within normal cent rounding, for both core and force books.
    for variant in VARIANTS:
        idx = len(SESSION_DATES) - 1
        _close(sum(terminal_ticker_metrics(core_lots[variant], core_realized[variant])[t]["total"] for t in (set(PRICES) | {"DXY"})),
               core_daily[variant][idx]["total"], f"all-ticker core reconciliation {variant}", tol=0.05)
        _close(sum(terminal_ticker_metrics(force_lots[variant], force_realized[variant])[t]["total"] for t in PRICES),
               force_daily[variant][idx]["total"], f"all-ticker force reconciliation {variant}", tol=0.05)

    dxy_core = terminal_ticker_metrics(core_lots["V1"], core_realized["V1"])["DXY"]
    return {
        "symbols": len(PRICES), "core_assets": len(PRICES) + 1,
        "dxy_core_units": dxy_core["deployed_units"],
        "dxy_core_terminal_pnl": dxy_core["total"],
        "sessions": len(SESSION_DATES), "events": len(events),
        "energy_rows": energy_rows, "oil_sidecar_rows": energy_rows,
        "dxy_sidecar_rows": dxy_sidecar_rows,
        "core_daily_rows": len(expected_daily),
        "force_daily_rows": len(strategy_rows), "composite_daily_rows": len(aggregate_rows),
        "ticker_rows": audit_rows, "terminal_aggregate": aggregate_rows[-1]["aggregate_pnl_usd"],
        "terminal_notional": aggregate_rows[-1]["aggregate_cumulative_notional_added_usd"],
    }


def write_audit(result):
    rows = result["ticker_rows"]
    if not rows:
        raise AssertionError("No actionable tickers to write")
    AUDIT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with AUDIT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return AUDIT_CSV


def main():
    result = audit_all()
    out = write_audit(result)
    print(f"Audited {result['symbols']} direct-price tickers plus the integrated 1U/DAY/DXY sleeve across {result['sessions']} sessions and {result['events']} direct trade-log events.")
    print(f"DXY core sleeve: {result['dxy_core_units']:.0f} daily units, terminal proxy PnL ${result['dxy_core_terminal_pnl']:+,.2f}.")
    print(f"Reconciled {result['core_daily_rows']} core daily rows, {result['force_daily_rows']} strategy daily rows, {result['energy_rows']} energy-sidecar rows, {result['dxy_sidecar_rows']} DXY-sidecar rows, and {result['composite_daily_rows']} all-32 aggregate rows.")
    print(f"THE ONE MODEL terminal PnL ${float(result['terminal_aggregate']):,.2f} on ${float(result['terminal_notional']):,.2f} gross notional added.")
    print(f"Wrote {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
