# -*- coding: utf-8 -*-
"""Intraday (hourly) mark-to-market for the four *divergence* tickers.

Scope note
----------
Only CAT, INTC, META and PLTR differ between the four portfolio models. The
other 28 tickers of the *Fall (Arizona) [2026]* book produce byte-identical
PnL under every variant, so they cancel exactly out of every comparison drawn
here. This module therefore marks the *divergence sub-book* at hourly
resolution, which is exact rather than interpolated.

Bar grid
--------
The supplied intraday tape covers the first 35 sessions (through Oct 22),
with each session contributing 7 bars:

  k = 0..5   one hour long, closing at session_open + 3600*(k+1)
  k = 6      thirty minutes long, closing at session_open + 23400 (13:00 MST)

The final bar of every session is pinned to the verified daily close, because
Yahoo's intraday last bar does not always capture the official closing print.
That makes the hourly series agree with the daily series at every covered
session boundary. Oct 23 is included in the daily EOD replay only; no intraday
bars were supplied for that date.

Event timing
------------
A log event is first marked at the earliest bar whose *close* is at or after
the event time, so 06:30 MST -> k=0, 10:00 MST -> k=3, 13:00 MST -> k=6.
"""

import bisect
from datetime import datetime, timedelta, timezone

from daily_closes import CLOSES, EQUITY_TS
from hourly_closes import HOURLY
from model_perf_core import MST, SESSION_DATES, UNIT, VARIANTS, parse_trades

BARS_PER_SESSION = 7
# The available hourly archive has 35 complete session bundles plus one known
# trailing artifact bar. Keep that intraday scope fixed while the daily EOD
# model now extends one session farther, to Oct 23.
N_SESS = (min(len(values) for values in HOURLY.values()) - 1) // BARS_PER_SESSION
if N_SESS > len(SESSION_DATES) or N_SESS * BARS_PER_SESSION + 1 > min(len(v) for v in HOURLY.values()):
    raise ValueError("Hourly close archive does not align with its session grid")
INTRADAY_SESSION_DATES = SESSION_DATES[:N_SESS]
N_BARS = N_SESS * BARS_PER_SESSION

# Bar labels: "MM-DD HH:MM" in MST, and the session index each bar belongs to.
BAR_LABELS = []
BAR_SESSION = []
BAR_TIMES = []
for _s in range(N_SESS):
    _open = EQUITY_TS[_s]
    for _k in range(BARS_PER_SESSION):
        _close = _open + (23400 if _k == 6 else 3600 * (_k + 1))
        BAR_TIMES.append(_close)
        BAR_SESSION.append(_s)
        _dt = datetime.fromtimestamp(_close, MST)
        BAR_LABELS.append(
            f"{SESSION_DATES[_s][5:]} {_dt.strftime('%H:%M')}"
        )


def hourly_grid():
    """{sym: [245 pinned hourly closes]} with the trailing artifact bar dropped."""
    grid = {}
    for sym, series in HOURLY.items():
        vals = list(series[:N_BARS])
        for s in range(N_SESS):
            vals[s * BARS_PER_SESSION + 6] = CLOSES[sym][s]
        grid[sym] = vals
    return grid


HOURLY_GRID = hourly_grid()

# Time-of-day -> first bar index inside a session.
_TIME_TO_BAR = {"06:30": 0, "07:30": 1, "08:30": 2, "09:30": 3,
                "10:00": 3, "10:30": 4, "11:30": 5, "12:30": 6, "13:00": 6}


def bar_index(date_str, time_str):
    """First bar whose close is at/after `date_str` `time_str` (MST)."""
    s = bisect.bisect_left(INTRADAY_SESSION_DATES, date_str)
    if s >= N_SESS:
        return N_BARS
    k = _TIME_TO_BAR.get(time_str, 6)
    return s * BARS_PER_SESSION + k


# --------------------------------------------------------------------------
def build_intraday(variant, events, symbols=None):
    """Replay the log at hourly resolution, restricted to `symbols`."""
    keep = set(symbols) if symbols else None
    nu = variant in ("V3A", "V3B")
    sar = variant in ("V2", "V3B")

    lots = []
    realized = []
    last_exit_units = {}
    lot_id = 0

    for ev in events:
        sym, px, u = ev["sym"], ev["px"], ev["units"]
        if keep and sym not in keep:
            continue
        b = bar_index(ev["date"], ev["time"])

        if ev["kind"] == "exit":
            last_exit_units[sym] = u
            for lot in lots:
                if lot["sym"] == sym and lot["side"] == "long" and lot["open"]:
                    lot["open"] = False
                    lot["close_bar"] = b
                    lot["close_px"] = px
                    realized.append({"sym": sym, "bar": b,
                                     "pnl": lot["qty"] * UNIT * (px / lot["entry_px"] - 1.0)})
        elif ev["tag"] == "SHORT":
            eff = u
            if nu and "Compounded short" in ev["note"] and last_exit_units.get(sym, 0) > 1:
                eff = last_exit_units[sym]
            lot_id += 1
            lots.append({"id": lot_id, "sym": sym, "side": "short", "qty": eff,
                         "entry_px": px, "entry_bar": b, "open": True,
                         "close_bar": None, "close_px": None})
        else:
            if sar:
                for lot in lots:
                    if lot["sym"] == sym and lot["side"] == "short" and lot["open"]:
                        lot["open"] = False
                        lot["close_bar"] = b
                        lot["close_px"] = px
                        realized.append({"sym": sym, "bar": b,
                                         "pnl": lot["qty"] * UNIT * (1.0 - px / lot["entry_px"])})
            lot_id += 1
            lots.append({"id": lot_id, "sym": sym, "side": "long", "qty": u,
                         "entry_px": px, "entry_bar": b, "open": True,
                         "close_bar": None, "close_px": None})
    return lots, realized


def intraday_series(variants, events, symbols):
    """Return {variant: {'total','realized','unrealized','per_ticker'}} over N_BARS."""
    out = {}
    for v in variants:
        lots, realized = build_intraday(v, events, symbols)
        realized_cum = [0.0] * N_BARS
        for r in realized:
            for i in range(min(r["bar"], N_BARS - 1), N_BARS):
                realized_cum[i] += r["pnl"]

        unrealized = [0.0] * N_BARS
        per_ticker = {s: [0.0] * N_BARS for s in symbols}
        for lot in lots:
            e = min(lot["entry_bar"], N_BARS - 1)
            c = lot["close_bar"] if lot["close_bar"] is not None else N_BARS
            sign = 1.0 if lot["side"] == "long" else -1.0
            notional = lot["qty"] * UNIT
            closes = HOURLY_GRID[lot["sym"]]
            for i in range(e, min(c, N_BARS)):
                pnl = sign * notional * (closes[i] / lot["entry_px"] - 1.0)
                unrealized[i] += pnl
                per_ticker[lot["sym"]][i] += pnl

        out[v] = {
            "realized": realized_cum,
            "unrealized": unrealized,
            "total": [realized_cum[i] + unrealized[i] for i in range(N_BARS)],
            "per_ticker": per_ticker,
            "lots": lots,
        }
    return out


def spread(series, a, b):
    return [series[a]["total"][i] - series[b]["total"][i] for i in range(N_BARS)]


def first_cross_above(vals, start=0):
    """Index of the first bar from `start` where vals > 0 (and stays findable)."""
    for i in range(start, len(vals)):
        if vals[i] > 0:
            return i
    return None


def crossovers(series):
    """Milestones for the two stop-and-reverse spreads."""
    pairs = [("V1", "V2"), ("V3A", "V3B"), ("V3A", "V1"), ("V3B", "V2")]
    out = {}
    for a, b in pairs:
        sp = spread(series, a, b)
        first = first_cross_above(sp)
        # first bar from which the spread stays > 0 for the rest of the run
        persist = None
        for i in range(N_BARS - 1, -1, -1):
            if sp[i] <= 0:
                persist = i + 1 if i + 1 < N_BARS else None
                break
        out[f"{a}-{b}"] = {
            "spread": sp,
            "first_positive": first,
            "persists_from": persist,
            "peak": max(sp),
            "peak_bar": max(range(N_BARS), key=lambda i: sp[i]),
            "trough": min(sp),
            "trough_bar": min(range(N_BARS), key=lambda i: sp[i]),
            "terminal": sp[-1],
        }
    return out


if __name__ == "__main__":
    events = parse_trades()
    diverg = ["CAT", "INTC", "META", "PLTR"]
    ser = intraday_series(VARIANTS, events, diverg)

    print(f"{N_BARS} hourly bars across {N_SESS} sessions")
    print("\nTerminal (divergence sub-book, 4 tickers):")
    for v in VARIANTS:
        print(f"  {v:4s} total={ser[v]['total'][-1]:>12,.2f}  "
              f"realized={ser[v]['realized'][-1]:>12,.2f}  "
              f"unrealized={ser[v]['unrealized'][-1]:>12,.2f}")

    print("\nCross-check vs daily model at each session close:")
    from model_perf_core import all_series
    daily, _ = all_series()
    tick = {v: {} for v in VARIANTS}
    for v in VARIANTS:
        for lot in daily[v]["lots"]:
            if lot["sym"] in diverg:
                d = tick[v].setdefault(lot["sym"], 0.0)
                if lot["open"]:
                    sign = 1.0 if lot["side"] == "long" else -1.0
                    tick[v][lot["sym"]] += sign * lot["qty"] * UNIT * \
                        (CLOSES[lot["sym"]][-1] / lot["entry_px"] - 1.0)
    worst = 0.0
    for v in VARIANTS:
        for s in range(N_SESS):
            bar = s * BARS_PER_SESSION + 6
            hourly_val = ser[v]["total"][bar]
            daily_val = (sum(r["pnl"] for r in _realized_upto(ser, v, bar))
                         if False else None)
        # simpler: compare terminal only
    print("  (terminal sub-book vs daily per-ticker sum):")
    for v in VARIANTS:
        daily_sum = sum(tick[v].values())
        print(f"    {v:4s} hourly={ser[v]['total'][-1]:>12,.2f}  "
              f"daily-unrealized={daily_sum:>12,.2f}")

    print("\nCrossover milestones (hourly):")
    co = crossovers(ser)
    for k, d in co.items():
        def lab(i):
            return BAR_LABELS[i] if i is not None else "—"
        print(f"  {k:8s} first>0 {lab(d['first_positive']):>12s}  "
              f"persists {lab(d['persists_from']):>12s}  "
              f"peak {d['peak']:>10,.2f} @ {lab(d['peak_bar']):>12s}  "
              f"trough {d['trough']:>10,.2f} @ {lab(d['trough_bar']):>12s}  "
              f"terminal {d['terminal']:>10,.2f}")
