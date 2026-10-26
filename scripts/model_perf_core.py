# -*- coding: utf-8 -*-
"""Core lot-builder + daily mark-to-market engine for the four portfolio models.

Four model variants are compared over the *Fall (Arizona) [2026]* book:

  V1  1U Open  - logged entry units; no LONG-triggered short cover.
  V2  1U SAR   - same logged sizing; LONG / REBUY closes open shorts.
  V3A Nu Open  - natural units (compounded shorts sized to the preceding
                 full exit); positions stay open.
  V3B Nu SAR   - natural units, plus stop-and-reverse on LONG / REBUY.

`1U` is the standard $10,000.00 initial notional; quantity Q = 1U / entry price.
"""

import bisect
import csv
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

from daily_closes import EQUITY_TS

ROOT = Path(__file__).resolve().parents[1]
TRADES_DIR = ROOT / "trades"
DATA_DIR = ROOT / "data"
CHARTS_DIR = ROOT / "Charts" / "performance"

MST = timezone(timedelta(hours=-7))
UNIT = 10_000.00
VARIANTS = ("V1", "V2", "V3A", "V3B")
VARIANT_LABEL = {
    "V1": "Variant 1 — 1U Open",
    "V2": "Variant 2 — 1U SAR",
    "V3A": "Variant 3A — Nu Open",
    "V3B": "Variant 3B — Nu SAR",
}
VARIANT_COLOR = {"V1": "#38bdf8", "V2": "#f472b6", "V3A": "#34d399", "V3B": "#fbbf24"}

# BTC/ETH await TradingView recalibration. DXY is not a direct-price ticker:
# its logged direction drives a separate 1U/day index-return sleeve that is
# integrated into each core portfolio. FX and yield records remain outside.
UNMODELED_SYMBOLS = frozenset({"BTC", "ETH", "DXY", "EURUSD", "JPYUSD", "US10Y", "US30Y"})

# --------------------------------------------------------------------------
# Session calendar and exclusive TradingView benchmark
# --------------------------------------------------------------------------
SESSION_DATES = [datetime.fromtimestamp(t, MST).strftime("%Y-%m-%d") for t in EQUITY_TS]
N_SESS = len(SESSION_DATES)
BENCHMARK_SESSION_FILE = DATA_DIR / "tradingview_benchmark_session_marks_20261024.csv"
_benchmark = {}
_dxy_marks = {}
with BENCHMARK_SESSION_FILE.open(newline="", encoding="utf-8") as _handle:
    for _row in csv.DictReader(_handle):
        _ticker = _row["Ticker"].strip().upper()
        _day = _row["Date"].strip()
        if _day not in SESSION_DATES:
            raise ValueError(f"Benchmark mark is outside the common session calendar: {_ticker} {_day}")
        if _ticker == "DXY":
            _dxy_marks[_day] = float(_row["Close"])
            continue
        _benchmark.setdefault(_ticker, {})[_day] = float(_row["Close"])

if {ticker for ticker in _benchmark} & {"BTC", "ETH"}:
    raise ValueError("BTC and ETH must remain outside the core TradingView benchmark")
if len(_benchmark) != 31:
    raise ValueError(f"Expected 31 direct-price core symbols, found {len(_benchmark)}")
PRICES = {}
for _ticker, _marks in _benchmark.items():
    _missing = [day for day in SESSION_DATES if day not in _marks]
    if _missing:
        raise ValueError(f"TradingView session-mark file is incomplete for {_ticker}: {_missing}")
    _series = [_marks[day] for day in SESSION_DATES]
    if any(price <= 0 for price in _series):
        raise ValueError(f"Non-positive TradingView mark for {_ticker}")
    PRICES[_ticker] = _series
if set(_dxy_marks) != set(SESSION_DATES):
    raise ValueError("DXY TradingView marks must cover the common session calendar")
DXY_PRICES = [_dxy_marks[day] for day in SESSION_DATES]
if any(price <= 0 for price in DXY_PRICES):
    raise ValueError("Non-positive DXY TradingView mark")
MODEL_PRICES = {**PRICES, "DXY": DXY_PRICES}


# --------------------------------------------------------------------------
# Raw log parsing
# --------------------------------------------------------------------------
LINE_RE = re.compile(
    r"^(?P<date>\d{4}-\d{2}-\d{2})\s+(?P<time>\d{2}:\d{2})\s+MST\s*\|\s*"
    r"SIMULATED PAPER\s+\[(?P<tag>[A-Za-z ]+?)\]\s*\|\s*"
    r"(?P<kind>entry|exit):\s*\[Market @ ~\$?(?P<px>[\d,]+\.?\d*)\]\s*\|\s*"
    r"size:\s*\[(?P<units>\d+(?:\.\d+)?)\s*units?[^\]]*\]\s*\|\s*"
    r"note:\s*\[(?P<note>.*)\]\s*$"
)


def parse_trades():
    """Return every standardized log event, ordered chronologically."""
    events = []
    for path in sorted(TRADES_DIR.glob("*.txt")):
        if path.name == "index.txt":
            continue
        sym = path.stem
        if sym in UNMODELED_SYMBOLS:
            continue
        if sym not in PRICES:
            raise ValueError(f"No configured daily price series for modeled symbol {sym!r}")
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines()):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            m = LINE_RE.match(line)
            if not m:
                raise ValueError(f"Unparsed line {path.name}:{lineno + 1}: {line}")
            parsed_units = float(m.group("units"))
            units = int(parsed_units) if parsed_units.is_integer() else parsed_units
            events.append(
                {
                    "sym": sym,
                    "date": m.group("date"),
                    "time": m.group("time"),
                    "tag": m.group("tag").strip().upper(),
                    "kind": m.group("kind"),
                    "px": float(m.group("px").replace(",", "")),
                    "units": units,
                    "note": m.group("note"),
                    "order": lineno,
                }
            )
    events.sort(key=lambda e: (e["date"], e["time"], e["sym"], e["order"]))
    return events


def session_index(date_str, kind):
    """First session whose date is >= `date_str` (entries) — see callers."""
    i = bisect.bisect_left(SESSION_DATES, date_str)
    if kind == "entry":
        return min(i, N_SESS - 1) if i < N_SESS else N_SESS - 1
    return i if i < N_SESS else N_SESS


# --------------------------------------------------------------------------
# Lot builder
# --------------------------------------------------------------------------
def build_lots(variant, events):
    """Replay the log under one model variant and return (lots, realized)."""
    nu = variant in ("V3A", "V3B")
    sar = variant in ("V2", "V3B")

    lots = []
    realized = []
    last_exit_units = {}
    lot_id = 0

    for ev in events:
        # Keep later dated events in the ledger, but never clamp them onto the
        # final historical session; they belong to a later valuation window.
        if ev["date"] > SESSION_DATES[-1]:
            continue
        sym, px, u = ev["sym"], ev["px"], ev["units"]
        idx = session_index(ev["date"], ev["kind"])

        if ev["kind"] == "exit":
            # Tagged Manual-Automatic trims are lot-scoped: unlike generic exits,
            # they reduce only the explicitly tagged entry and leave every other
            # open long lot in the ticker untouched. The exit's units are the
            # quantity trimmed, not a replacement size for the whole position.
            if "Explicit close of the tagged 2026-10-23 10U" in ev["note"]:
                remaining = u
                targets = [
                    lot for lot in lots
                    if lot["sym"] == sym and lot["side"] == "short" and lot["open"]
                    and lot.get("oil_target_short", False)
                ]
                for lot in targets:
                    if remaining <= 1e-12:
                        break
                    qty = min(lot["qty"], remaining)
                    if qty <= 0:
                        continue
                    if qty < lot["qty"]:
                        lot["qty"] -= qty
                        lot_id += 1
                        closed = {**lot, "id": lot_id, "qty": qty}
                        lots.append(closed)
                    else:
                        closed = lot
                    closed["open"] = False
                    closed["close_idx"] = idx
                    closed["close_date"] = ev["date"]
                    closed["close_px"] = px
                    realized.append({
                        "sym": sym,
                        "idx": idx,
                        "date": ev["date"],
                        "qty": qty,
                        "pnl": qty * UNIT * (1.0 - px / closed["entry_px"]),
                    })
                    remaining -= qty
                if remaining > 1e-8:
                    raise ValueError(
                        f"{sym} explicit SHORT close exceeds tagged open units by {remaining:g}"
                    )
            elif "Manual-Automatic target trim" in ev["note"]:
                remaining = u
                targets = [
                    lot for lot in lots
                    if lot["sym"] == sym and lot["side"] == "long" and lot["open"]
                    and lot.get("manual_automatic_entry", False)
                ]
                for lot in targets:
                    if remaining <= 1e-12:
                        break
                    qty = min(lot["qty"], remaining)
                    if qty <= 0:
                        continue
                    if qty < lot["qty"]:
                        lot["qty"] -= qty
                        lot_id += 1
                        closed = {**lot, "id": lot_id, "qty": qty}
                        lots.append(closed)
                    else:
                        closed = lot
                    closed["open"] = False
                    closed["close_idx"] = idx
                    closed["close_px"] = px
                    realized.append({
                        "sym": sym,
                        "idx": idx,
                        "date": ev["date"],
                        "qty": qty,
                        "pnl": qty * UNIT * (px / closed["entry_px"] - 1.0),
                    })
                    remaining -= qty
                if remaining > 1e-8:
                    raise ValueError(
                        f"{sym} Manual-Automatic trim exceeds tagged open units by {remaining:g}"
                    )
            else:
                last_exit_units[sym] = u
                for lot in lots:
                    if lot["sym"] == sym and lot["side"] == "long" and lot["open"]:
                        lot["open"] = False
                        lot["close_idx"] = idx
                        lot["close_px"] = px
                        realized.append(
                            {
                                "sym": sym,
                                "idx": idx,
                                "date": ev["date"],
                                "qty": lot["qty"],
                                "pnl": lot["qty"] * UNIT * (px / lot["entry_px"] - 1.0),
                            }
                        )

        elif ev["tag"] == "SHORT":
            eff = u
            if nu and "Compounded short" in ev["note"] and last_exit_units.get(sym, 0) > 1:
                eff = last_exit_units[sym]
            lot_id += 1
            lots.append(
                {
                    "id": lot_id, "sym": sym, "side": "short", "qty": eff,
                    "entry_px": px, "entry_idx": idx, "entry_date": ev["date"],
                    "open": True, "close_idx": None, "close_px": None,
                    "oil_target_short": "user-directed hypothetical force-multiplier short" in ev["note"],
                }
            )

        else:  # LONG / REBUY
            if sar:
                for lot in lots:
                    if (
                        lot["sym"] == sym and lot["side"] == "short" and lot["open"]
                        and not lot.get("oil_target_short", False)
                    ):
                        lot["open"] = False
                        lot["close_idx"] = idx
                        lot["close_px"] = px
                        realized.append(
                            {
                                "sym": sym,
                                "idx": idx,
                                "date": ev["date"],
                                "qty": lot["qty"],
                                "pnl": lot["qty"] * UNIT * (1.0 - px / lot["entry_px"]),
                            }
                        )
            lot_id += 1
            lots.append(
                {
                    "id": lot_id, "sym": sym, "side": "long", "qty": u,
                    "entry_px": px, "entry_idx": idx, "entry_date": ev["date"],
                    "open": True, "close_idx": None, "close_px": None,
                    "manual_automatic_entry": "Manual-Automatic Entry" in ev["note"],
                }
            )

    return lots, realized


# --------------------------------------------------------------------------
# Chart-directed 1U/DAY/DXY sleeve, integrated in every core variant
# --------------------------------------------------------------------------
def build_dxy_daily_lots():
    """Create one 1U DXY index-return lot per session under the carried chart direction."""
    path = TRADES_DIR / "DXY.txt"
    signals = []
    for lineno, raw in enumerate(path.read_text(encoding="utf-8").splitlines()):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        match = LINE_RE.match(line)
        if not match:
            raise ValueError(f"Unparsed DXY signal {path.name}:{lineno + 1}: {line}")
        tag = match.group("tag").strip().upper()
        if tag not in {"LONG", "REBUY", "SHORT"}:
            continue
        day = match.group("date")
        if day > SESSION_DATES[-1]:
            continue
        signals.append({"date": day, "time": match.group("time"), "tag": tag, "order": lineno})
    signals.sort(key=lambda event: (event["date"], event["time"], event["order"]))

    signals_by_session = {}
    for signal in signals:
        idx = session_index(signal["date"], "entry")
        signals_by_session.setdefault(idx, []).append(signal)

    lots = []
    realized = []
    current_direction = None
    for idx, day in enumerate(SESSION_DATES):
        day_signals = signals_by_session.get(idx, [])
        if day_signals:
            signal = day_signals[-1]
            new_direction = "short" if signal["tag"] == "SHORT" else "long"
            if current_direction is not None and current_direction != new_direction:
                mark = DXY_PRICES[idx]
                for lot in lots:
                    if lot["open"]:
                        sign = 1.0 if lot["side"] == "long" else -1.0
                        pnl = lot["qty"] * UNIT * sign * (mark / lot["entry_px"] - 1.0)
                        lot["open"] = False
                        lot["close_idx"] = idx
                        lot["close_px"] = mark
                        realized.append({"sym": "DXY", "idx": idx, "date": day,
                                         "qty": lot["qty"], "pnl": pnl})
            current_direction = new_direction
        if current_direction is not None:
            lots.append({
                "id": len(lots) + 1,
                "sym": "DXY",
                "side": current_direction,
                "qty": 1.0,
                "entry_px": DXY_PRICES[idx],
                "entry_idx": idx,
                "entry_date": day,
                "open": True,
                "close_idx": None,
                "close_px": None,
                "signal_basis": "latest charted LONG/REBUY/SHORT direction; 1U added each active EOD",
            })
    return lots, realized


# --------------------------------------------------------------------------
# Daily mark-to-market series
# --------------------------------------------------------------------------
def daily_series(variant, events):
    lots, realized = build_lots(variant, events)
    dxy_lots, dxy_realized = build_dxy_daily_lots()
    lots.extend(dxy_lots)
    realized.extend(dxy_realized)

    realized_cum = [0.0] * N_SESS
    for r in realized:
        for i in range(min(r["idx"], N_SESS - 1), N_SESS):
            realized_cum[i] += r["pnl"]

    unrealized = [0.0] * N_SESS
    open_units = [0.0] * N_SESS
    deployed = [0.0] * N_SESS

    for lot in lots:
        e = min(lot["entry_idx"], N_SESS - 1)
        c = lot["close_idx"] if lot["close_idx"] is not None else N_SESS
        sign = 1.0 if lot["side"] == "long" else -1.0
        notional = lot["qty"] * UNIT
        for i in range(e, min(c, N_SESS)):
            px = MODEL_PRICES[lot["sym"]][i]
            unrealized[i] += sign * notional * (px / lot["entry_px"] - 1.0)
            open_units[i] += lot["qty"]
        for i in range(e, N_SESS):
            deployed[i] += notional

    total = [realized_cum[i] + unrealized[i] for i in range(N_SESS)]
    roi = [100.0 * total[i] / deployed[i] if deployed[i] else 0.0 for i in range(N_SESS)]
    return {
        "variant": variant,
        "dates": SESSION_DATES,
        "realized": realized_cum,
        "unrealized": unrealized,
        "total": total,
        "roi": roi,
        "deployed": deployed,
        "open_units": open_units,
        "lots": lots,
        "realized_trades": realized,
    }


def all_series():
    events = parse_trades()
    return {v: daily_series(v, events) for v in VARIANTS}, events


if __name__ == "__main__":
    series, events = all_series()
    print(f"{len(events)} log events, {N_SESS} sessions "
          f"{SESSION_DATES[0]} .. {SESSION_DATES[-1]}")
    for v in VARIANTS:
        s = series[v]
        units = sum(l["qty"] for l in s["lots"])
        print(f"{v:4s} units={units:5.0f}  R={s['realized'][-1]:12,.2f}  "
              f"U={s['unrealized'][-1]:12,.2f}  T={s['total'][-1]:12,.2f}  "
              f"ROI={s['roi'][-1]:6.2f}%  deployed=${s['deployed'][-1]:,.0f}")
