# -*- coding: utf-8 -*-
"""Core lot-builder + daily mark-to-market engine for the four portfolio models.

Four model variants are compared over the *Fall (Arizona) [2026]* book:

  V1  1u Open  - every log line is 1 unit ($10,000); positions stay open.
  V2  1u SAR   - 1 unit; a LONG / REBUY stops-and-reverses open shorts.
  V3A Nu Open  - natural units (compounded shorts sized to the preceding
                 full exit); positions stay open.
  V3B Nu SAR   - natural units, plus stop-and-reverse on LONG / REBUY.

`1 unit` = $10,000.00 initial notional; quantity Q = $10,000 / entry price.
"""

import bisect
import csv
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

from daily_closes import BTC_CLOSES, CLOSES, CRYPTO_TS, EQUITY_TS, ETH_CLOSES

ROOT = Path(__file__).resolve().parents[1]
TRADES_DIR = ROOT / "trades"
DATA_DIR = ROOT / "data"
CHARTS_DIR = ROOT / "Charts" / "performance"

MST = timezone(timedelta(hours=-7))
UNIT = 10_000.00
VARIANTS = ("V1", "V2", "V3A", "V3B")
VARIANT_LABEL = {
    "V1": "Variant 1 — 1u Open",
    "V2": "Variant 2 — 1u SAR",
    "V3A": "Variant 3A — Nu Open",
    "V3B": "Variant 3B — Nu SAR",
}
VARIANT_COLOR = {"V1": "#38bdf8", "V2": "#f472b6", "V3A": "#34d399", "V3B": "#fbbf24"}

# These books are recorded in trades/, but the four comparison variants have no
# compatible daily mark series / valuation model for them. Keep them in the
# canonical ledger while excluding them explicitly from model PnL replay.
UNMODELED_SYMBOLS = frozenset({"DXY", "EURUSD", "JPYUSD", "US10Y", "US30Y"})

# Oct 22, 2026 BTC/ETH historical marks pinned to the verified settlement set
# used by `Trades Zip PnL.md` (Yahoo's crypto snapshot drifts from settlement).
# Energy marks instead come from the user-provided exact BlackBull/TVC EOD rows
# from the first active position date onward; only pre-entry context remains a
# labeled BZ=F/CL=F proxy. Approximate energy quotes remain a separate overlay.
VERIFIED_OCT22 = {
    "BTC": 81263.73,
    "ETH": 2381.38,
}

# --------------------------------------------------------------------------
# Session calendar
# --------------------------------------------------------------------------
SESSION_DATES = [datetime.fromtimestamp(t, MST).strftime("%Y-%m-%d") for t in EQUITY_TS]
N_SESS = len(SESSION_DATES)

_CRYPTO_DATES = [
    datetime.fromtimestamp(t, timezone.utc).strftime("%Y-%m-%d") for t in CRYPTO_TS
]
_CRYPTO_SERIES = {"BTC": BTC_CLOSES, "ETH": ETH_CLOSES}

# price[sym] -> list of closes aligned to SESSION_DATES
PRICES = {}
for _sym, _series in CLOSES.items():
    PRICES[_sym] = list(_series)
for _sym, _series in _CRYPTO_SERIES.items():
    _mapped = []
    for _d in SESSION_DATES:
        _i = bisect.bisect_right(_CRYPTO_DATES, _d) - 1
        _mapped.append(_series[max(_i, 0)] if _i >= 0 else _series[0])
    PRICES[_sym] = _mapped

# Keep the previous Oct 22 cutoff reproducible as a historical observation;
# the Oct 23 EOD source supplies the new terminal session instead.
_OCT22_INDEX = SESSION_DATES.index("2026-10-22")
for _sym, _px in VERIFIED_OCT22.items():
    PRICES[_sym][_OCT22_INDEX] = _px
for _sym, _px in {
    "AAPL": 348.22, "AMZN": 250.38, "CAT": 704.05, "CVX": 226.68,
    "DIS": 113.13, "GEV": 827.42, "HD": 327.73, "INTC": 85.49, "LLY": 1306.69,
    "LMT": 589.91, "LULU": 104.06, "META": 648.85, "NET": 303.61, "NFLX": 67.05,
    "NVDA": 212.21, "ORCL": 125.54, "PEP": 138.83, "PLTR": 196.19,
    "RIVN": 12.06, "SPCX": 144.75, "TMO": 676.54, "TSLA": 374.58, "UPS": 101.52,
    "V": 414.34, "VLO": 426.28, "WMT": 121.12, "XLE": 67.57, "XRH0": 790.00,
}.items():
    PRICES[_sym][_OCT22_INDEX] = _px

# User-provided LCID pilot marks, kept in their own auditable daily CSV. The
# history before the first LCID entry is irrelevant to PnL; seed it with the
# first available mark so the shared session array remains fully populated.
LCID_MARK_FILE = DATA_DIR / "lcid_small_caps_pilot_daily_marks.csv"
_lcid_marks = {}
with LCID_MARK_FILE.open(newline="", encoding="utf-8") as _fh:
    for _row in csv.DictReader(_fh):
        _day = _row["Date"].strip()
        if _day in _lcid_marks:
            raise ValueError(f"Duplicate LCID pilot mark for {_day}")
        _lcid_marks[_day] = float(_row["Close"])
if not _lcid_marks:
    raise ValueError(f"No LCID marks found in {LCID_MARK_FILE}")
_lcid_mark_days = sorted(_lcid_marks)
_lcid_last = _lcid_marks[_lcid_mark_days[0]]
_lcid_prices = []
for _day in SESSION_DATES:
    for _mark_day in _lcid_mark_days:
        if _mark_day > _day:
            break
        _lcid_last = _lcid_marks[_mark_day]
    _lcid_prices.append(_lcid_last)
PRICES["LCID"] = _lcid_prices


# --------------------------------------------------------------------------
# Raw log parsing
# --------------------------------------------------------------------------
LINE_RE = re.compile(
    r"^(?P<date>\d{4}-\d{2}-\d{2})\s+(?P<time>\d{2}:\d{2})\s+MST\s*\|\s*"
    r"SIMULATED PAPER\s+\[(?P<tag>[A-Za-z ]+?)\]\s*\|\s*"
    r"(?P<kind>entry|exit):\s*\[Market @ ~\$(?P<px>[\d,]+\.?\d*)\]\s*\|\s*"
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
                }
            )

        else:  # LONG / REBUY
            if sar:
                for lot in lots:
                    if lot["sym"] == sym and lot["side"] == "short" and lot["open"]:
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
                }
            )

    return lots, realized


# --------------------------------------------------------------------------
# Daily mark-to-market series
# --------------------------------------------------------------------------
def daily_series(variant, events):
    lots, realized = build_lots(variant, events)

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
            px = PRICES[lot["sym"]][i]
            unrealized[i] += sign * notional * (px / lot["entry_px"] - 1.0)
        for i in range(e, N_SESS):
            open_units[i] += lot["qty"]
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
