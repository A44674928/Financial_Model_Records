#!/usr/bin/env python3
"""Build the day-by-day model-performance comparison deliverables.

Reads `trades/` through `model_perf_core.py` and writes:

  data/model_performance_daily.csv      full per-session series, all variants
  data/model_performance_tickers.csv    per-ticker terminal contribution
  data/model_performance_summary.json   machine-readable summary + series
  Charts/performance/*.png              static charts
  Model Performance Comparison.md       written report
  Model Performance Explorer.html       standalone interactive explorer

Run from anywhere:  PYTHONPATH=scripts python3 scripts/build_model_performance.py
"""

import csv
import json
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.ticker import FuncFormatter

from model_perf_core import (  # noqa: E402
    CHARTS_DIR, DATA_DIR, MST, PRICES, ROOT, SESSION_DATES, UNIT, VARIANTS,
    VARIANT_COLOR, VARIANT_LABEL, all_series,
)

BG = "#0d131e"
PANEL = "#141c2b"
GRID = "#243044"
FG = "#f1f5f9"
MUTED = "#93a4bd"

USDFMT = FuncFormatter(lambda v, _: f"${v:,.0f}")
PCTFMT = FuncFormatter(lambda v, _: f"{v:.1f}%")


# --------------------------------------------------------------------------
# Derive the full metric set
# --------------------------------------------------------------------------
def enrich(series):
    """Add daily deltas, drawdown and peak/trough markers to each variant."""
    for v, s in series.items():
        n = len(s["dates"])
        delta = [s["total"][0]] + [s["total"][i] - s["total"][i - 1] for i in range(1, n)]
        s["delta"] = delta
        peak, dd, peak_series = -1e18, [], []
        for val in s["total"]:
            peak = max(peak, val)
            peak_series.append(peak)
            dd.append(val - peak)
        s["peak"] = peak_series
        s["drawdown"] = dd
        best = max(range(n), key=lambda i: delta[i])
        worst = min(range(n), key=lambda i: delta[i])
        trough = min(range(n), key=lambda i: s["total"][i])
        s["stats"] = {
            "best_day": (s["dates"][best], delta[best]),
            "worst_day": (s["dates"][worst], delta[worst]),
            "max_drawdown": min(dd),
            "max_drawdown_day": s["dates"][max(range(n), key=lambda i: -dd[i])],
            "trough": (s["dates"][trough], s["total"][trough]),
            "peak": max(s["total"]),
            "peak_day": s["dates"][max(range(n), key=lambda i: s["total"][i])],
            "units": sum(l["qty"] for l in s["lots"]),
            "deployed": s["deployed"][-1],
            "n_realized": len(s["realized_trades"]),
            "n_open": sum(1 for l in s["lots"] if l["open"]),
            "n_lots": len(s["lots"]),
            "best_roi_day": max(s["roi"]),
        }
    return series


def ticker_contributions(series):
    """Terminal PnL per ticker per variant (realized + unrealized)."""
    out = {}
    for v, s in series.items():
        per = {}
        for lot in s["lots"]:
            sym = lot["sym"]
            notional = lot["qty"] * UNIT
            entry = dict(lot)
            per.setdefault(sym, {"realized": 0.0, "unrealized": 0.0, "units": 0.0})
            if entry["open"]:
                px = PRICES[sym][-1]
                sign = 1.0 if entry["side"] == "long" else -1.0
                per[sym]["unrealized"] += sign * notional * (px / entry["entry_px"] - 1.0)
                per[sym]["units"] += entry["qty"]
            else:
                per[sym]["units"] += entry["qty"]
        for r in s["realized_trades"]:
            per.setdefault(r["sym"], {"realized": 0.0, "unrealized": 0.0, "units": 0.0})
            per[r["sym"]]["realized"] += r["pnl"]
        for sym, d in per.items():
            d["total"] = d["realized"] + d["unrealized"]
        out[v] = per
    return out


# --------------------------------------------------------------------------
# Charts
# --------------------------------------------------------------------------
def _style(ax, title, ylabel, fmt=None):
    ax.set_facecolor(PANEL)
    ax.set_title(title, color=FG, fontsize=13, fontweight="bold", pad=12)
    ax.set_ylabel(ylabel, color=MUTED, fontsize=10)
    ax.set_xlabel("Session (MST)", color=MUTED, fontsize=10)
    ax.grid(True, color=GRID, linewidth=0.7, alpha=0.9)
    ax.set_axisbelow(True)
    for spine in ax.spines.values():
        spine.set_color(GRID)
    ax.tick_params(colors=MUTED, labelsize=8)
    if fmt:
        ax.yaxis.set_major_formatter(fmt)


def _xticks(ax, dates, step=3):
    idx = list(range(0, len(dates), step))
    ax.set_xticks(idx)
    ax.set_xticklabels(
        [datetime.strptime(dates[i], "%Y-%m-%d").strftime("%m/%d") for i in idx],
        rotation=45, ha="right",
    )


def make_charts(series, contrib):
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)
    dates = SESSION_DATES
    x = list(range(len(dates)))
    files = []

    def save(fig, name):
        path = CHARTS_DIR / name
        fig.savefig(path, dpi=150, facecolor=BG, bbox_inches="tight")
        plt.close(fig)
        files.append(path)

    # 1. Cumulative total PnL
    fig, ax = plt.subplots(figsize=(11, 5.6))
    for v in VARIANTS:
        ax.plot(x, series[v]["total"], label=VARIANT_LABEL[v], color=VARIANT_COLOR[v], lw=2.2)
    ax.axhline(0, color=MUTED, lw=1, ls="--", alpha=0.6)
    _style(ax, "Cumulative Total PnL by Session — Fall (Arizona) [2026]", "PnL (USD)", USDFMT)
    _xticks(ax, dates)
    ax.legend(facecolor=PANEL, edgecolor=GRID, labelcolor=FG, fontsize=9, loc="upper left")
    save(fig, "01-cumulative-pnl-by-session.png")

    # 2. Cumulative ROI
    fig, ax = plt.subplots(figsize=(11, 5.6))
    for v in VARIANTS:
        ax.plot(x, series[v]["roi"], label=VARIANT_LABEL[v], color=VARIANT_COLOR[v], lw=2.2)
    ax.axhline(0, color=MUTED, lw=1, ls="--", alpha=0.6)
    _style(ax, "Cumulative Return on Deployed Capital by Session", "ROI (%)", PCTFMT)
    _xticks(ax, dates)
    ax.legend(facecolor=PANEL, edgecolor=GRID, labelcolor=FG, fontsize=9, loc="upper left")
    save(fig, "02-cumulative-roi-by-session.png")

    # 3. Daily PnL change
    fig, ax = plt.subplots(figsize=(11, 5.6))
    w = 0.21
    for k, v in enumerate(VARIANTS):
        ax.bar([i + (k - 1.5) * w for i in x], series[v]["delta"], width=w,
               label=VARIANT_LABEL[v], color=VARIANT_COLOR[v])
    ax.axhline(0, color=MUTED, lw=1)
    _style(ax, "Day-by-Day PnL Change per Session", "Δ PnL (USD)", USDFMT)
    _xticks(ax, dates)
    ax.legend(facecolor=PANEL, edgecolor=GRID, labelcolor=FG, fontsize=9, loc="upper left")
    save(fig, "03-daily-pnl-change.png")

    # 4. Pairwise spreads
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 8.4), sharex=True)
    pairs = [("V1", "V2", "V1 − V2 : stop-and-reverse effect (1-unit book)"),
             ("V3A", "V3B", "V3A − V3B : stop-and-reverse effect (natural-unit book)")]
    for ax, (a, b, title) in zip((ax1, ax2), pairs):
        spread = [series[a]["total"][i] - series[b]["total"][i] for i in x]
        ax.plot(x, spread, color="#a78bfa", lw=2.2)
        ax.fill_between(x, 0, spread, where=[s >= 0 for s in spread],
                        color="#34d399", alpha=0.28, interpolate=True)
        ax.fill_between(x, 0, spread, where=[s < 0 for s in spread],
                        color="#ef4444", alpha=0.28, interpolate=True)
        ax.axhline(0, color=MUTED, lw=1, ls="--", alpha=0.7)
        _style(ax, title, "Spread (USD)", USDFMT)
    _xticks(ax2, dates)
    fig.suptitle("Where the Models Diverge", color=FG, fontsize=14,
                 fontweight="bold", y=0.98)
    save(fig, "04-model-spreads.png")

    # 5. Sizing effect (V3A − V1) and combined (V3B − V2)
    fig, ax = plt.subplots(figsize=(11, 5.6))
    for a, b, col, lab in [
        ("V3A", "V1", "#22d3ee", "V3A − V1 : compounding effect (open books)"),
        ("V3B", "V2", "#f97316", "V3B − V2 : compounding effect (SAR books)"),
    ]:
        ax.plot(x, [series[a]["total"][i] - series[b]["total"][i] for i in x],
                label=lab, color=col, lw=2.2)
    ax.axhline(0, color=MUTED, lw=1, ls="--", alpha=0.7)
    _style(ax, "Effect of Compounding Shorts into Full Exits", "Spread (USD)", USDFMT)
    _xticks(ax, dates)
    ax.legend(facecolor=PANEL, edgecolor=GRID, labelcolor=FG, fontsize=9, loc="upper left")
    save(fig, "05-compounding-effect.png")

    # 6. Drawdown (underwater)
    fig, ax = plt.subplots(figsize=(11, 5.6))
    for v in VARIANTS:
        ax.plot(x, series[v]["drawdown"], label=VARIANT_LABEL[v],
                color=VARIANT_COLOR[v], lw=2.0)
    ax.axhline(0, color=MUTED, lw=1, ls="--", alpha=0.6)
    _style(ax, "Drawdown from Running Peak (Underwater Curve)", "Drawdown (USD)", USDFMT)
    _xticks(ax, dates)
    ax.legend(facecolor=PANEL, edgecolor=GRID, labelcolor=FG, fontsize=9, loc="lower left")
    save(fig, "06-drawdown.png")

    # 7. Realized vs unrealized composition at Oct 22 close
    fig, ax = plt.subplots(figsize=(9.6, 5.4))
    xs = range(len(VARIANTS))
    rz = [series[v]["realized"][-1] for v in VARIANTS]
    un = [series[v]["unrealized"][-1] for v in VARIANTS]
    ax.bar(xs, rz, 0.55, label="Realized (closed)", color="#34d399")
    ax.bar(xs, un, 0.55, bottom=rz, label="Unrealized (open)", color="#60a5fa")
    for i, v in enumerate(VARIANTS):
        ax.text(i, rz[i] + un[i] + 900, f"${rz[i] + un[i]:,.0f}", ha="center",
                color=FG, fontsize=10, fontweight="bold")
    ax.set_xticks(list(xs))
    ax.set_xticklabels([VARIANT_LABEL[v].replace(" — ", "\n") for v in VARIANTS], fontsize=9)
    _style(ax, "Terminal PnL Composition — Oct 22, 2026 Close", "PnL (USD)", USDFMT)
    ax.set_xlabel("")
    ax.legend(facecolor=PANEL, edgecolor=GRID, labelcolor=FG, fontsize=9)
    save(fig, "07-terminal-composition.png")

    # 8. Per-ticker contribution, grouped
    syms = sorted(contrib["V3A"], key=lambda s: -abs(contrib["V3A"][s]["total"]))
    fig, ax = plt.subplots(figsize=(13, 6.4))
    w = 0.21
    for k, v in enumerate(VARIANTS):
        vals = [contrib[v].get(s, {"total": 0.0})["total"] for s in syms]
        ax.bar([i + (k - 1.5) * w for i in range(len(syms))], vals, width=w,
               label=VARIANT_LABEL[v], color=VARIANT_COLOR[v])
    ax.axhline(0, color=MUTED, lw=1)
    ax.set_xticks(range(len(syms)))
    ax.set_xticklabels(syms, rotation=45, ha="right")
    _style(ax, "Terminal PnL Contribution by Ticker", "PnL (USD)", USDFMT)
    ax.set_xlabel("")
    ax.legend(facecolor=PANEL, edgecolor=GRID, labelcolor=FG, fontsize=9)
    save(fig, "08-ticker-contribution.png")

    return files


# --------------------------------------------------------------------------
# Data exports
# --------------------------------------------------------------------------
def write_csv(series):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    path = DATA_DIR / "model_performance_daily.csv"
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["variant", "session_date", "session_index",
                    "realized_cum_usd", "unrealized_usd", "total_pnl_usd",
                    "daily_delta_usd", "roi_pct", "deployed_usd",
                    "open_units", "drawdown_usd"])
        for v in VARIANTS:
            s = series[v]
            for i, d in enumerate(s["dates"]):
                w.writerow([v, d, i,
                            f"{s['realized'][i]:.2f}", f"{s['unrealized'][i]:.2f}",
                            f"{s['total'][i]:.2f}", f"{s['delta'][i]:.2f}",
                            f"{s['roi'][i]:.4f}", f"{s['deployed'][i]:.2f}",
                            f"{s['open_units'][i]:.0f}", f"{s['drawdown'][i]:.2f}"])
    return path


def write_ticker_csv(contrib):
    path = DATA_DIR / "model_performance_tickers.csv"
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["variant", "ticker", "units_deployed",
                    "realized_usd", "unrealized_usd", "total_usd"])
        for v in VARIANTS:
            for sym in sorted(contrib[v], key=lambda s: -contrib[v][s]["total"]):
                d = contrib[v][sym]
                w.writerow([v, sym, f"{d['units']:.0f}",
                            f"{d['realized']:.2f}", f"{d['unrealized']:.2f}",
                            f"{d['total']:.2f}"])
    return path


def write_json(series, contrib):
    path = DATA_DIR / "model_performance_summary.json"
    payload = {
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "cohort": "Fall (Arizona) [2026]",
        "timezone": "America/Phoenix — MST / UTC-07:00 (no DST)",
        "unit_notional_usd": UNIT,
        "sessions": SESSION_DATES,
        "variants": {
            v: {
                "label": VARIANT_LABEL[v],
                "color": VARIANT_COLOR[v],
                "series": {k: series[v][k] for k in
                           ("total", "realized", "unrealized", "roi",
                            "delta", "deployed", "open_units", "drawdown")},
                "stats": series[v]["stats"],
                "tickers": contrib[v],
            }
            for v in VARIANTS
        },
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


# --------------------------------------------------------------------------
# Markdown report
# --------------------------------------------------------------------------
def _money(x):
    return f"${x:,.2f}"


def write_markdown(series, contrib, charts, daily_csv, ticker_csv, summary_json):
    n = len(SESSION_DATES)
    last = n - 1
    term = {v: series[v]["total"][last] for v in VARIANTS}
    roi = {v: series[v]["roi"][last] for v in VARIANTS}
    spread_ab = term["V1"] - term["V2"]
    spread_cd = term["V3A"] - term["V3B"]
    spread_size = term["V3A"] - term["V1"]

    lines = []
    A = lines.append
    A("# Model Performance Comparison — *Fall (Arizona) [2026]*")
    A("")
    A("Day-by-day (and, where market data supports it, intraday) comparison of the four "
      "portfolio models carried on the same standardized book: "
      "**[`trades/`](trades/)** / **[`trades.zip`](trades.zip)** — `32` symbols, "
      "`77` standardized log lines, `1 unit = $10,000.00` initial notional, all timestamps in "
      "Arizona year-round **`MST` / `UTC-07:00`**, marked against the "
      "**Thursday, October 22, 2026** close.")
    A("")
    A("> **Interactive version:** open **[`Model Performance Explorer.html`](Model%20Performance%20Explorer.html)** "
      "for a self-contained explorer with toggleable series, a hover crosshair, and per-ticker "
      "breakdowns. Machine-readable exports live in [`data/`](data/): "
      f"[`{daily_csv.name}`](data/{daily_csv.name}), "
      f"[`{ticker_csv.name}`](data/{ticker_csv.name}), "
      f"[`{summary_json.name}`](data/{summary_json.name}).")
    A("")
    A("## The Four Models")
    A("")
    A("| Model | Rule | Units deployed | Realized | Unrealized | **Total PnL** | **ROI** |")
    A("|---|---|---:|---:|---:|---:|---:|")
    for v in VARIANTS:
        s = series[v]
        A(f"| **{VARIANT_LABEL[v]}** | "
          f"{'every line is 1 unit; positions stay open' if v == 'V1' else ''}"
          f"{'every line is 1 unit; LONG/REBUY stops-and-reverses open shorts' if v == 'V2' else ''}"
          f"{'compounded shorts sized to the preceding full exit; positions stay open' if v == 'V3A' else ''}"
          f"{'compounded shorts *and* stop-and-reverse' if v == 'V3B' else ''} | "
          f"{s['stats']['units']:.0f}u (${s['stats']['deployed']:,.0f}) | "
          f"{_money(s['realized'][last])} | {_money(s['unrealized'][last])} | "
          f"**{_money(term[v])}** | **{roi[v]:.2f}%** |")
    A("")
    A("All four models agree on `28` of the `32` tickers. They diverge only on "
      "**`CAT`, `INTC`, `META` and `PLTR`** — the four symbols where a short is followed by a "
      "long (or a full exit is compounded into a short). Everything below is driven by those four.")
    A("")
    A("## Headline Chart")
    A("")
    A(f"![Cumulative total PnL by session]({charts[0].relative_to(ROOT).as_posix()})")
    A("")
    A("**Reading it:** all four models track each other almost exactly for the first four weeks, "
      "then fan out in October. Ranking is stable from `Oct 6` onward: "
      "**V3A > V3B > V1 > V2** on absolute dollars.")
    A("")
    A("## Return on Capital")
    A("")
    A(f"![Cumulative ROI by session]({charts[1].relative_to(ROOT).as_posix()})")
    A("")
    A("Raw dollars flatter V3A/V3B because they deploy more capital — `81` units "
      "(`$810,000`) against V1/V2's `72` units (`$720,000`). ROI normalises for that, and the "
      "ranking is unchanged: compounding shorts into full exits beats flat sizing on both "
      "capital bases, and *not* stop-and-reversing beats stop-and-reversing on both.")
    A("")
    A("## Day-by-Day Moves")
    A("")
    A(f"![Day-by-day PnL change]({charts[2].relative_to(ROOT).as_posix()})")
    A("")
    A("| Session | " + " | ".join(VARIANTS) + " | Note |")
    A("|---|" + "---:|---:|---:|---:|"[: len("---:|" * 4)] + "---|")
    for i, d in enumerate(SESSION_DATES):
        note = ""
        if i == 0:
            note = "Season open"
        if i == last:
            note = "Terminal mark"
        best = max(VARIANTS, key=lambda v: series[v]["delta"][i])
        worst = min(VARIANTS, key=lambda v: series[v]["delta"][i])
        if series[best]["delta"][i] - series[worst]["delta"][i] > 500:
            note = (note + "; " if note else "") + f"widest split ({best} best, {worst} worst)"
        A(f"| `{d}` | " + " | ".join(
            f"{series[v]['delta'][i]:+,.2f}" for v in VARIANTS) + f" | {note} |")
    A("")
    A("## Where the Models Diverge")
    A("")
    A(f"![Model spreads]({charts[3].relative_to(ROOT).as_posix()})")
    A("")
    A(f"![Compounding effect]({charts[4].relative_to(ROOT).as_posix()})")
    A("")
    A(f"- **Stop-and-reverse (V1 − V2) ends at {_money(spread_ab)}; "
      f"(V3A − V3B) ends at {_money(spread_cd)}.**")
    A(f"- **Compounding (V3A − V1) ends at {_money(spread_size)}** — the single largest "
      "structural effect in the book.")
    A("")
    A("## Risk — Drawdown from Running Peak")
    A("")
    A(f"![Drawdown]({charts[5].relative_to(ROOT).as_posix()})")
    A("")
    A("| Model | Peak | Peak day | Trough | Trough day | Max drawdown | Max DD day | "
      "Best day | Worst day |")
    A("|---|---:|---|---:|---:|---|---:|---|---:|")
    for v in VARIANTS:
        st = series[v]["stats"]
        A(f"| **{VARIANT_LABEL[v]}** | {_money(st['peak'])} | `{st['peak_day']}` | "
          f"{_money(st['trough'][1])} | `{st['trough'][0]}` | "
          f"{_money(st['max_drawdown'])} | `{st['max_drawdown_day']}` | "
          f"{_money(st['best_day'][1])} (`{st['best_day'][0]}`) | "
          f"{_money(st['worst_day'][1])} (`{st['worst_day'][0]}`) |")
    A("")
    A("## Terminal Composition")
    A("")
    A(f"![Terminal composition]({charts[6].relative_to(ROOT).as_posix()})")
    A("")
    A("| Model | Realized (closed) | Unrealized (open) | Closed lots | Open lots |")
    A("|---|---:|---:|---:|---:|")
    for v in VARIANTS:
        s = series[v]
        A(f"| **{VARIANT_LABEL[v]}** | {_money(s['realized'][last])} | "
          f"{_money(s['unrealized'][last])} | {s['stats']['n_realized']} | "
          f"{s['stats']['n_open']} |")
    A("")
    A("## Contribution by Ticker")
    A("")
    A(f"![Ticker contribution]({charts[7].relative_to(ROOT).as_posix()})")
    A("")
    div = ["CAT", "INTC", "META", "PLTR"]
    A("### The four divergence tickers")
    A("")
    A("| Ticker | " + " | ".join(VARIANTS) + " |")
    A("|---|" + "---:|---:|---:|---:|")
    for sym in div:
        A(f"| `{sym}` | " + " | ".join(
            _money(contrib[v].get(sym, {"total": 0.0})["total"]) for v in VARIANTS) + " |")
    A("")
    A("### Top contributors (V3A)")
    A("")
    A("| Ticker | Units | Realized | Unrealized | **Total** |")
    A("|---|---:|---:|---:|---:|")
    top = sorted(contrib["V3A"].items(), key=lambda kv: -kv[1]["total"])[:10]
    for sym, d in top:
        A(f"| `{sym}` | {d['units']:.0f}u | {_money(d['realized'])} | "
          f"{_money(d['unrealized'])} | **{_money(d['total'])}** |")
    A("")
    A("### Bottom contributors (V3A)")
    A("")
    A("| Ticker | Units | Realized | Unrealized | **Total** |")
    A("|---|---:|---:|---:|---:|")
    bot = sorted(contrib["V3A"].items(), key=lambda kv: kv[1]["total"])[:10]
    for sym, d in bot:
        A(f"| `{sym}` | {d['units']:.0f}u | {_money(d['realized'])} | "
          f"{_money(d['unrealized'])} | **{_money(d['total'])}** |")
    A("")
    A("## Method & Caveats")
    A("")
    A("- **Price source:** Yahoo Finance `v8/finance/chart` `interval=1d` for all `32` symbols "
      "(`Brent = BZ=F`, `WTI = CL=F`, `BTC = BTC-USD`, `ETH = ETH-USD`); pulled "
      f"{datetime.now(MST).strftime('%Y-%m-%d')}.")
    A("- **Session calendar:** the `35` U.S. equity regular sessions from "
      f"`{SESSION_DATES[0]}` to `{SESSION_DATES[-1]}`. Futures and crypto are mapped onto the "
      "same session index by trade date.")
    A("- **`XRH0`** (db Physical Rhodium ETC, LSE) is too illiquid for a usable daily history, "
      "so it is held flat at its `$790.00` log entry — matching the "
      "[`Trades Zip PnL.md`](Trades%20Zip%20PnL.md) convention.")
    A("- **Terminal marks** on `2026-10-22` are pinned to the verified settlement set used by "
      "[`Trades Zip PnL.md`](Trades%20Zip%20PnL.md), so the final row reconciles to "
      "**$0.00** against that ledger.")
    A("- **ROI** is cumulative PnL divided by notional deployed *to date* "
      "(units opened on or before that session × `$10,000`), so early sessions show larger "
      "percentages on less capital.")
    A("- Entry fills use the log's own market prices, not session closes; exits are realised on "
      "their log date.")
    A("- Excludes commissions, borrow fees, and overnight financing.")
    A("")
    A("---")
    A("")
    A("Master ledger: **[`Trades Zip PnL.md`](Trades%20Zip%20PnL.md)** · "
      "Chart-signal report: **[`Triangle Signals.md`](Triangle%20Signals.md)** · "
      "Visual book: **[`Unrealized PnL.md`](Unrealized%20PnL.md)** · "
      "Pre-2026: **[`2024 Trades PnL.md`](2024%20Trades%20PnL.md)**")
    A("")

    path = ROOT / "Model Performance Comparison.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


# --------------------------------------------------------------------------
# Standalone HTML explorer
# --------------------------------------------------------------------------
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Model Performance Explorer — Fall (Arizona) [2026]</title>
<style>
  :root{
    --bg:#0d131e; --panel:#141c2b; --panel2:#1b2536; --grid:#243044;
    --fg:#f1f5f9; --muted:#93a4bd; --line:#2c3a52;
    --v1:#38bdf8; --v2:#f472b6; --v3a:#34d399; --v3b:#fbbf24;
  }
  *{box-sizing:border-box}
  body{margin:0;background:var(--bg);color:var(--fg);
       font:15px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
  a{color:#7dd3fc}
  .wrap{max-width:1280px;margin:0 auto;padding:28px 20px 72px}
  h1{font-size:26px;margin:0 0 6px}
  .sub{color:var(--muted);margin:0 0 22px;font-size:14px}
  .card{background:var(--panel);border:1px solid var(--line);border-radius:12px;
        padding:18px 20px;margin-bottom:20px}
  .card h2{font-size:16px;margin:0 0 4px}
  .card .hint{color:var(--muted);font-size:12.5px;margin:0 0 14px}
  .controls{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:14px}
  button{background:var(--panel2);color:var(--fg);border:1px solid var(--line);
         border-radius:8px;padding:7px 13px;font-size:13px;cursor:pointer;
         font-family:inherit;transition:.15s}
  button:hover{border-color:#3d5070}
  button.on{background:#1e3a5f;border-color:#4a86c8}
  button.metric.on{background:#24405e;border-color:#5aa0e0}
  .legend{display:flex;flex-wrap:wrap;gap:14px;margin:12px 0 4px;font-size:13px}
  .legend label{display:flex;align-items:center;gap:7px;cursor:pointer;user-select:none;
                opacity:.45;transition:.15s}
  .legend label.on{opacity:1}
  .swatch{width:13px;height:13px;border-radius:3px;display:inline-block}
  canvas{width:100%;display:block;border-radius:8px}
  .tip{position:absolute;pointer-events:none;background:#0a0f18ee;border:1px solid var(--line);
       border-radius:9px;padding:9px 12px;font-size:12.5px;line-height:1.55;
       white-space:nowrap;opacity:0;transition:opacity .1s;z-index:9;
       box-shadow:0 8px 24px #0009}
  .tip b{color:#fff}
  .row{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:12px}
  .stat{background:var(--panel2);border:1px solid var(--line);border-radius:9px;padding:12px 14px}
  .stat .k{color:var(--muted);font-size:11.5px;text-transform:uppercase;letter-spacing:.05em}
  .stat .v{font-size:19px;font-weight:650;margin-top:3px;font-variant-numeric:tabular-nums}
  table{width:100%;border-collapse:collapse;font-size:13px;font-variant-numeric:tabular-nums}
  th,td{padding:7px 9px;text-align:right;border-bottom:1px solid var(--line)}
  th:first-child,td:first-child{text-align:left}
  th{color:var(--muted);font-weight:600;font-size:11.5px;text-transform:uppercase;
     letter-spacing:.04em;position:sticky;top:0;background:var(--panel)}
  tbody tr:hover{background:#1a2434}
  .scroll{max-height:520px;overflow-y:auto}
  .pos{color:#4ade80}.neg{color:#f87171}
  .tw{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:12px}
  footer{color:var(--muted);font-size:12.5px;margin-top:26px;border-top:1px solid var(--line);
         padding-top:16px}
  code{background:#0a0f18;padding:1px 5px;border-radius:4px;font-size:12.5px}
</style>
</head>
<body>
<div class="wrap">
  <h1>Model Performance Explorer</h1>
  <p class="sub">*Fall (Arizona) [2026]* paper-trade book &middot; __NSESS__ sessions
     (__START__ &rarr; __END__, MST) &middot; 32 symbols &middot; 1 unit = $10,000.00
     &middot; marked to the Oct 22, 2026 close</p>

  <div class="card">
    <h2>Terminal results</h2>
    <p class="hint">Oct 22, 2026 close. ROI = total PnL &divide; notional deployed.</p>
    <div class="row" id="terminal"></div>
  </div>

  <div class="card">
    <h2>Day-by-day series</h2>
    <p class="hint">Pick a metric, toggle models, then hover the chart for exact values.</p>
    <div class="controls" id="metrics"></div>
    <div class="legend" id="legend"></div>
    <div style="position:relative">
      <canvas id="chart" height="430"></canvas>
      <div class="tip" id="tip"></div>
    </div>
  </div>

  <div class="card">
    <h2>Contribution by ticker</h2>
    <p class="hint">Terminal PnL per symbol. Only <code>CAT</code>, <code>INTC</code>,
       <code>META</code> and <code>PLTR</code> differ between models.</p>
    <div class="tw" id="tmet"></div>
    <div style="position:relative">
      <canvas id="bars" height="330"></canvas>
      <div class="tip" id="tip2"></div>
    </div>
  </div>

  <div class="card">
    <h2>Full session table</h2>
    <p class="hint">Cumulative total PnL and day-over-day change, all four models.</p>
    <div class="scroll"><table id="tbl"></table></div>
  </div>

  <footer>
    Generated __GEN__. Prices: Yahoo Finance <code>interval=1d</code>.
    Terminal marks pinned to the verified settlement set so the final row reconciles to
    $0.00 against <b>Trades Zip PnL.md</b>. Excludes commissions, borrow fees and financing.
  </footer>
</div>
<script>
const DATA = __DATA__;
const VARS = ["V1","V2","V3A","V3B"];
const METRICS = {
  total:      {label:"Cumulative total PnL", fmt:v=>(v>=0?"+":"−")+"$"+Math.abs(v).toLocaleString(undefined,{minimumFractionDigits:2,maximumFractionDigits:2}), axis:v=>"$"+Math.round(v).toLocaleString()},
  roi:        {label:"Return on deployed capital", fmt:v=>(v>=0?"+":"")+v.toFixed(3)+"%", axis:v=>v.toFixed(1)+"%"},
  realized:   {label:"Realized PnL (cumulative)", fmt:v=>(v>=0?"+":"−")+"$"+Math.abs(v).toLocaleString(undefined,{minimumFractionDigits:2,maximumFractionDigits:2}), axis:v=>"$"+Math.round(v).toLocaleString()},
  unrealized: {label:"Unrealized PnL", fmt:v=>(v>=0?"+":"−")+"$"+Math.abs(v).toLocaleString(undefined,{minimumFractionDigits:2,maximumFractionDigits:2}), axis:v=>"$"+Math.round(v).toLocaleString()},
  delta:      {label:"Day-over-day change", fmt:v=>(v>=0?"+":"−")+"$"+Math.abs(v).toLocaleString(undefined,{minimumFractionDigits:2,maximumFractionDigits:2}), axis:v=>"$"+Math.round(v).toLocaleString()},
  drawdown:   {label:"Drawdown from peak", fmt:v=>"−$"+Math.abs(v).toLocaleString(undefined,{minimumFractionDigits:2,maximumFractionDigits:2}), axis:v=>"$"+Math.round(v).toLocaleString()},
  deployed:   {label:"Notional deployed", fmt:v=>"$"+v.toLocaleString(undefined,{maximumFractionDigits:0}), axis:v=>"$"+Math.round(v/1000).toLocaleString()+"k"},
  open_units: {label:"Open units", fmt:v=>v+"u", axis:v=>v+"u"}
};
let metric = "total", shown = new Set(VARS), tmetric = "total";

const usd = v => (v<0?"−":"")+"$"+Math.abs(v).toLocaleString(undefined,{minimumFractionDigits:2,maximumFractionDigits:2});
const pct = v => (v>=0?"+":"")+v.toFixed(2)+"%";

/* ---------- terminal stat cards ---------- */
(function(){
  const el = document.getElementById("terminal");
  el.innerHTML = VARS.map(v=>{
    const d = DATA.variants[v], s = d.series;
    return `<div class="stat" style="border-left:3px solid ${d.color}">
      <div class="k">${d.label}</div>
      <div class="v ${s.total[s.total.length-1]>=0?'pos':'neg'}">${usd(s.total[s.total.length-1])}</div>
      <div class="k" style="margin-top:8px">ROI</div>
      <div class="v" style="font-size:16px;color:${s.roi[s.roi.length-1]>=0?'#4ade80':'#f87171'}">${pct(s.roi[s.roi.length-1])}</div>
      <div class="k" style="margin-top:8px">realized / unrealized</div>
      <div style="font-size:13px;font-variant-numeric:tabular-nums">${usd(s.realized[s.realized.length-1])} / ${usd(s.unrealized[s.unrealized.length-1])}</div>
      <div class="k" style="margin-top:8px">max drawdown</div>
      <div style="font-size:13px" class="neg">${usd(d.stats.max_drawdown)}</div>
    </div>`;
  }).join("");
})();

/* ---------- controls ---------- */
const mEl = document.getElementById("metrics");
mEl.innerHTML = Object.entries(METRICS).map(([k,m])=>
  `<button class="metric${k===metric?" on":""}" data-m="${k}">${m.label}</button>`).join("");
mEl.onclick = e => { const b=e.target.closest("button"); if(!b) return;
  metric=b.dataset.m; [...mEl.children].forEach(c=>c.classList.toggle("on",c===b)); draw(); };

const lEl = document.getElementById("legend");
lEl.innerHTML = VARS.map(v=>
  `<label class="on" data-v="${v}"><span class="swatch" style="background:${DATA.variants[v].color}"></span>${DATA.variants[v].label}</label>`).join("");
lEl.onclick = e => { const l=e.target.closest("label"); if(!l) return;
  const v=l.dataset.v;
  if(shown.has(v) && shown.size>1){ shown.delete(v); l.classList.remove("on"); }
  else { shown.add(v); l.classList.add("on"); }
  draw(); };

const tmEl = document.getElementById("tmet");
tmEl.innerHTML = [["total","Total PnL"],["realized","Realized"],["unrealized","Unrealized"]]
  .map(([k,l])=>`<button class="${k===tmetric?"on":""}" data-t="${k}">${l}</button>`).join("");
tmEl.onclick = e => { const b=e.target.closest("button"); if(!b) return;
  tmetric=b.dataset.t; [...tmEl.children].forEach(c=>c.classList.toggle("on",c===b)); drawBars(); };

/* ---------- line chart ---------- */
const cv = document.getElementById("chart"), ctx = cv.getContext("2d");
const tip = document.getElementById("tip");
let geom = null;

function sizeCanvas(c, h){
  const r = window.devicePixelRatio||1, w = c.clientWidth;
  c.width = w*r; c.height = h*r; c.style.height = h+"px";
  c.getContext("2d").setTransform(r,0,0,r,0,0);
}

function niceTicks(lo,hi,n){
  if(lo===hi){ lo-=1; hi+=1; }
  const span=hi-lo, step0=span/n, mag=Math.pow(10,Math.floor(Math.log10(step0)));
  const norm=step0/mag; let step = (norm<1.5?1:norm<3?2:norm<7?5:10)*mag;
  const out=[]; for(let t=Math.ceil(lo/step)*step; t<=hi+step*1e-9; t+=step) out.push(t);
  return out;
}

function draw(){
  sizeCanvas(cv,430);
  const W=cv.clientWidth, H=430, L=76, R=16, T=16, B=52;
  const n=DATA.sessions.length, pw=W-L-R, ph=H-T-B;
  ctx.clearRect(0,0,W,H);
  ctx.fillStyle="#141c2b"; ctx.fillRect(0,0,W,H);

  let vals=[];
  VARS.filter(v=>shown.has(v)).forEach(v=>DATA.variants[v].series[metric].forEach(x=>vals.push(x)));
  if(!vals.length) return;
  let lo=Math.min(0,...vals), hi=Math.max(0,...vals);
  const pad=(hi-lo)*0.08||1; lo-=pad; hi+=pad;

  const X=i=>L+(n===1?pw/2:i*pw/(n-1));
  const Y=v=>T+ph-(v-lo)/(hi-lo)*ph;

  ctx.strokeStyle="#243044"; ctx.lineWidth=1; ctx.fillStyle="#93a4bd";
  ctx.font="11px ui-monospace,SFMono-Regular,Menlo,monospace"; ctx.textAlign="right";
  niceTicks(lo,hi,6).forEach(t=>{
    const y=Y(t);
    ctx.beginPath(); ctx.moveTo(L,y); ctx.lineTo(L+pw,y); ctx.stroke();
    ctx.fillText(METRICS[metric].axis(t), L-8, y+4);
  });
  ctx.textAlign="center";
  DATA.sessions.forEach((d,i)=>{ if(i%3===0||i===n-1){
    ctx.fillText(d.slice(5), X(i), H-B+18); }});
  ctx.save(); ctx.translate(16,T+ph/2); ctx.rotate(-Math.PI/2);
  ctx.textAlign="center"; ctx.fillStyle="#93a4bd"; ctx.font="11px sans-serif";
  ctx.fillText(METRICS[metric].label,0,0); ctx.restore();

  ctx.strokeStyle="#3f4d66"; ctx.lineWidth=1;
  ctx.beginPath(); ctx.moveTo(L,Y(0)); ctx.lineTo(L+pw,Y(0)); ctx.stroke();

  VARS.filter(v=>shown.has(v)).forEach(v=>{
    const s=DATA.variants[v].series[metric], c=DATA.variants[v].color;
    if(metric==="delta"){
      const w=pw/n*0.8, off=L+pw/n/2;
      ctx.fillStyle=c;
      for(let i=0;i<n;i++){
        const y0=Y(0), y1=Y(s[i]), h=Math.abs(y1-y0);
        ctx.globalAlpha=.85;
        ctx.fillRect(X(i)-w/2, Math.min(y0,y1), w, Math.max(h,1));
        ctx.globalAlpha=1;
      }
    } else {
      ctx.strokeStyle=c; ctx.lineWidth=2.2; ctx.beginPath();
      s.forEach((val,i)=> i?ctx.lineTo(X(i),Y(val)):ctx.moveTo(X(i),Y(val)));
      ctx.stroke();
      if(metric!=="deployed"&&metric!=="open_units"){
        ctx.fillStyle=c;
        s.forEach((val,i)=>{ ctx.beginPath(); ctx.arc(X(i),Y(val),2.6,0,7); ctx.fill(); });
      }
    }
  });
  geom={L,T,pw,ph,n,X,Y};
}

/* ---------- bar chart ---------- */
const bv = document.getElementById("bars"), bx = bv.getContext("2d");
const tip2 = document.getElementById("tip2");
let bgeom = null, syms = [];

function drawBars(){
  sizeCanvas(bv,330);
  const W=bv.clientWidth,H=330,L=76,R=16,T=14,B=52,pw=W-L-R,ph=H-T-B;
  bx.clearRect(0,0,W,H); bx.fillStyle="#141c2b"; bx.fillRect(0,0,W,H);
  const v0=VARS.filter(v=>shown.has(v));
  syms = Object.keys(DATA.variants.V3A.tickers)
    .sort((a,b)=>Math.abs(DATA.variants.V3A.tickers[b][tmetric])
                 -Math.abs(DATA.variants.V3A.tickers[a][tmetric]));
  let vals=[]; v0.forEach(v=>syms.forEach(s=>vals.push(DATA.variants[v].tickers[s]?.[tmetric]||0)));
  let lo=Math.min(0,...vals),hi=Math.max(0,...vals); const pad=(hi-lo)*0.08||1; lo-=pad; hi+=pad;
  const Y=v=>T+ph-(v-lo)/(hi-lo)*ph;
  const step=pw/syms.length, gw=step*0.82, bw=gw/v0.length;

  bx.strokeStyle="#243044"; bx.fillStyle="#93a4bd"; bx.font="11px ui-monospace,monospace";
  bx.textAlign="right";
  niceTicks(lo,hi,6).forEach(t=>{ const y=Y(t);
    bx.beginPath(); bx.moveTo(L,y); bx.lineTo(L+pw,y); bx.stroke();
    bx.fillText("$"+Math.round(t).toLocaleString(),L-8,y+4); });
  bx.strokeStyle="#3f4d66"; bx.beginPath(); bx.moveTo(L,Y(0)); bx.lineTo(L+pw,Y(0)); bx.stroke();

  v0.forEach((v,vi)=>{
    bx.fillStyle=DATA.variants[v].color; bx.globalAlpha=.9;
    syms.forEach((s,i)=>{
      const val=DATA.variants[v].tickers[s]?.[tmetric]||0;
      const y0=Y(0),y1=Y(val);
      bx.fillRect(L+i*step+(step-gw)/2+vi*bw, Math.min(y0,y1), bw-1, Math.max(Math.abs(y1-y0),1));
    });
    bx.globalAlpha=1;
  });
  bx.fillStyle="#93a4bd"; bx.textAlign="center"; bx.font="9.5px ui-monospace,monospace";
  syms.forEach((s,i)=>{ bx.save(); bx.translate(L+i*step+step/2,H-B+10);
    bx.rotate(-Math.PI/4); bx.fillText(s,0,0); bx.restore(); });
  bgeom={L,T,pw,ph,step,gw,bw,Y,v0};
}

/* ---------- hover ---------- */
cv.addEventListener("mousemove", e=>{
  if(!geom) return;
  const r=cv.getBoundingClientRect(), mx=e.clientX-r.left, my=e.clientY-r.top;
  const {L,T,pw,ph,n,X,Y}=geom;
  if(mx<L-10||mx>L+pw+10||my<T-10||my>T+ph+10){ tip.style.opacity=0; return; }
  const i=Math.max(0,Math.min(n-1,Math.round((mx-L)/(pw/(n-1)))));
  const v0=VARS.filter(v=>shown.has(v));
  tip.innerHTML = `<b>${DATA.sessions[i]}</b><br>` + v0.map(v=>
    `<span style="color:${DATA.variants[v].color}">■</span> ${v}: ${METRICS[metric].fmt(DATA.variants[v].series[metric][i])}`).join("<br>");
  tip.style.opacity=1;
  const tw=tip.offsetWidth;
  tip.style.left = Math.min(Math.max(X(i)+14,4), r.width-tw-4)+"px";
  tip.style.top = Math.max(my-10,4)+"px";
});
cv.addEventListener("mouseleave", ()=>tip.style.opacity=0);

bv.addEventListener("mousemove", e=>{
  if(!bgeom) return;
  const r=bv.getBoundingClientRect(), mx=e.clientX-r.left, my=e.clientY-r.top;
  const {L,T,pw,ph,step,gw,bw,Y,v0}=bgeom;
  if(mx<L||mx>L+pw||my<T||my>T+ph){ tip2.style.opacity=0; return; }
  const i=Math.max(0,Math.min(syms.length-1,Math.floor((mx-L)/step)));
  const s=syms[i];
  tip2.innerHTML = `<b>${s}</b><br>` + v0.map(v=>
    `<span style="color:${DATA.variants[v].color}">■</span> ${v}: ${usd(DATA.variants[v].tickers[s]?.[tmetric]||0)}`).join("<br>");
  tip2.style.opacity=1;
  const tw=tip2.offsetWidth;
  tip2.style.left = Math.min(Math.max(L+i*step+step/2+12,4), r.width-tw-4)+"px";
  tip2.style.top = Math.max(my-10,4)+"px";
});
bv.addEventListener("mouseleave", ()=>tip2.style.opacity=0);

/* ---------- table ---------- */
(function(){
  const n=DATA.sessions.length;
  document.getElementById("tbl").innerHTML =
    "<thead><tr><th>Session</th>"+VARS.map(v=>`<th>${v} total</th><th>${v} Δ</th>`).join("")+"</tr></thead><tbody>"+
    DATA.sessions.map((d,i)=>
      `<tr><td><code>${d}</code></td>`+VARS.map(v=>{
        const s=DATA.variants[v].series;
        const c1=s.total[i]>=0?"pos":"neg", c2=s.delta[i]>=0?"pos":"neg";
        return `<td class="${c1}">${usd(s.total[i])}</td><td class="${c2}">${s.delta[i]>=0?"+":"−"}$${Math.abs(s.delta[i]).toLocaleString(undefined,{minimumFractionDigits:2,maximumFractionDigits:2})}</td>`;
      }).join("")+"</tr>").join("")+"</tbody>";
})();

let rt; window.addEventListener("resize", ()=>{ clearTimeout(rt); rt=setTimeout(()=>{draw();drawBars();},120); });
draw(); drawBars();
</script>
</body>
</html>
"""


def write_html(series, contrib, summary_json):
    payload = json.loads(summary_json.read_text(encoding="utf-8"))
    slim = {
        "sessions": payload["sessions"],
        "variants": {
            v: {
                "label": d["label"],
                "color": d["color"],
                "series": d["series"],
                "stats": d["stats"],
                "tickers": d["tickers"],
            }
            for v, d in payload["variants"].items()
        },
    }
    html = (
        HTML_TEMPLATE
        .replace("__DATA__", json.dumps(slim, separators=(",", ":")))
        .replace("__NSESS__", str(len(SESSION_DATES)))
        .replace("__START__", SESSION_DATES[0])
        .replace("__END__", SESSION_DATES[-1])
        .replace("__GEN__", datetime.now(MST).strftime("%Y-%m-%d %H:%M MST"))
    )
    path = ROOT / "Model Performance Explorer.html"
    path.write_text(html, encoding="utf-8")
    return path


# --------------------------------------------------------------------------
def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    series, _events = all_series()
    enrich(series)
    contrib = ticker_contributions(series)

    charts = make_charts(series, contrib)
    daily_csv = write_csv(series)
    ticker_csv = write_ticker_csv(contrib)
    summary_json = write_json(series, contrib)
    md = write_markdown(series, contrib, charts, daily_csv, ticker_csv, summary_json)
    html = write_html(series, contrib, summary_json)

    print("Wrote:")
    for p in charts:
        print(f"  {p.relative_to(ROOT)}")
    for p in (daily_csv, ticker_csv, summary_json, md, html):
        print(f"  {p.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
