#!/usr/bin/env python3
"""Build the day-by-day model-performance comparison deliverables.

Reads `trades/` through `model_perf_core.py` and writes:

  data/model_performance_daily.csv      full per-session series, all variants
  data/model_performance_tickers.csv    per-ticker terminal contribution
  data/model_performance_summary.json   machine-readable summary + series
  Charts/performance/*.png              static model-performance charts
  Model Performance Comparison.md       written report
  Model Performance Explorer.html       standalone interactive explorer

Run from anywhere:  PYTHONPATH=scripts python3 scripts/build_model_performance.py
"""

import csv
import json
import re
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
from matplotlib.ticker import FuncFormatter

from model_perf_core import (  # noqa: E402
    CHARTS_DIR, DATA_DIR, MODEL_PRICES, MST, PRICES, ROOT, SESSION_DATES, UNIT, VARIANTS,
    VARIANT_COLOR, VARIANT_LABEL, all_series, parse_trades,
)
from intraday_core import (  # noqa: E402
    BAR_LABELS, BAR_SESSION, BARS_PER_SESSION, N_BARS, crossovers,
    intraday_series, spread,
)
from us10y_adjustment import (
    BASELINE_PCT as US10Y_BASELINE_PCT,
    START_DATE as US10Y_ADJUSTMENT_START,
    SOURCE_FILES as US10Y_SOURCE_FILES,
    apply_us10y_adjustment,
    write_adjustment_csv,
)

DIVERGENCE = ["CAT", "INTC", "META", "PLTR"]

BG = "#0d131e"
PANEL = "#141c2b"
GRID = "#243044"
FG = "#f1f5f9"
MUTED = "#93a4bd"

USDFMT = FuncFormatter(lambda v, _: f"${v:,.0f}")
PCTFMT = FuncFormatter(lambda v, _: f"{v:.1f}%")


def _top_split_portfolio_ratios():
    """Return the four highest terminal ratios from the 32 split portfolios."""
    from build_strategy_sidecar_comparison import comparison_rows

    rows = comparison_rows()[0]
    last = rows[-1]
    performers = []
    for core in VARIANTS:
        for force in VARIANTS:
            base = f"{core}_core_plus_{force}_force_1u"
            label = f"Core {core} + 1U {force}"
            for oil, suffix in ((False, ""), (True, "_and_oil")):
                field = f"{base}{suffix}_return_on_cumulative_notional_pct"
                performers.append((float(last[field]), label + (" with energy sidecar" if oil else " without energy sidecar")))
    return sorted(performers, reverse=True)[:4]


def _unitfmt(value):
    """Render fractional logged units without rounding them away."""
    return f"{value:.4f}".rstrip("0").rstrip(".")


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
                px = MODEL_PRICES[sym][-1]
                sign = 1.0 if entry["side"] == "long" else -1.0
                per[sym]["unrealized"] += sign * notional * (px / entry["entry_px"] - 1.0)
                per[sym]["units"] += entry["qty"]
            else:
                per[sym]["units"] += entry["qty"]
        for r in s["realized_trades"]:
            per.setdefault(r["sym"], {"realized": 0.0, "unrealized": 0.0, "units": 0.0})
            per[r["sym"]]["realized"] += r["pnl"]
        for sym, d in per.items():
            # Set terminal ticker total to the sum of the cent-rounded components
            # that appear in the report and CSV, so each displayed row adds up.
            realized_cents = float(f"{d['realized']:.2f}")
            unrealized_cents = float(f"{d['unrealized']:.2f}")
            d["exact_total"] = d["realized"] + d["unrealized"]
            d["total"] = realized_cents + unrealized_cents
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
    if dates and idx[-1] != len(dates) - 1:
        idx.append(len(dates) - 1)
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
    _style(ax, "Cumulative Base Trading PnL by Session — Fall (Arizona) [2026]", "PnL (USD)", USDFMT)
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
    pairs = [("V1", "V2", "V1 − V2 : stop-and-reverse effect (1U book)"),
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

    # 7. Realized vs unrealized composition at terminal EOD close
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
    _style(ax, f"Terminal PnL Composition — {SESSION_DATES[-1]} EOD Close", "PnL (USD)", USDFMT)
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


def make_us10y_adjustment_chart(series, yield_rows):
    """Plot observed US10Y closes against baseline and cumulative adjustment."""
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 8.2), sharex=True)
    dates = SESSION_DATES
    x = list(range(len(dates)))
    valid = [(i, row["yield_pct"]) for i, row in enumerate(yield_rows)
             if row["yield_pct"] is not None]
    vx = [i for i, _ in valid]
    vy = [value for _, value in valid]
    ax1.plot(vx, vy, color="#38bdf8", lw=2.1, marker="o", ms=3,
             label="User-provided US10Y close")
    ax1.axhline(US10Y_BASELINE_PCT, color="#fbbf24", lw=1.5, ls="--",
                label=f"Baseline {US10Y_BASELINE_PCT:.3f}%")
    ax1.fill_between(vx, US10Y_BASELINE_PCT, vy,
                     where=[value >= US10Y_BASELINE_PCT for value in vy],
                     color="#34d399", alpha=0.22, interpolate=True)
    ax1.axvline(dates.index(US10Y_ADJUSTMENT_START), color=MUTED, lw=1, ls=":")
    _style(ax1, "US10Y Daily Close vs Baseline", "Yield (%)", PCTFMT)
    ax1.set_xlabel("")
    ax1.legend(facecolor=PANEL, edgecolor=GRID, labelcolor=FG, fontsize=8)

    for variant in VARIANTS:
        ax2.plot(x, series[variant]["yield_adjustment"],
                 label=VARIANT_LABEL[variant], color=VARIANT_COLOR[variant], lw=2.1)
    ax2.axhline(0, color=MUTED, lw=1, ls="--", alpha=0.7)
    _style(ax2, "Cumulative US10Y Excess-Yield Adjustment", "Adjustment (USD)", USDFMT)
    _xticks(ax2, dates)
    ax2.legend(facecolor=PANEL, edgecolor=GRID, labelcolor=FG, fontsize=8, loc="upper left")
    fig.tight_layout()
    path = CHARTS_DIR / "15-us10y-baseline-adjustment.png"
    fig.savefig(path, dpi=150, facecolor=BG, bbox_inches="tight")
    plt.close(fig)
    return path


def make_energy_eod_history_chart():
    """Plot only exact user-provided EOD marks over each active energy period."""
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)
    source_path = DATA_DIR / "energy_provider_eod_marks_v1.csv"
    marks = {"BRENT": [], "OIL": []}
    with source_path.open(newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            ticker = row["Ticker"]
            if ticker in marks:
                marks[ticker].append((
                    datetime.strptime(row["Date"], "%Y-%m-%d"),
                    float(row["EOD_Close"]),
                ))

    fig, ax = plt.subplots(figsize=(12, 5.6))
    colors = {"BRENT": "#38bdf8", "OIL": "#f59e0b"}
    sources = {
        "BRENT": "BlackBull Markets Brent Cash",
        "OIL": "TradingView TVC:USOIL",
    }
    for ticker in ("BRENT", "OIL"):
        points = sorted(marks[ticker])
        if not points:
            raise ValueError(f"No exact EOD marks found for {ticker} in {source_path}")
        dates = [point[0] for point in points]
        prices = [point[1] for point in points]
        ax.plot(dates, prices, color=colors[ticker], lw=2.2, marker="o", ms=4,
                label=f"{ticker} — {sources[ticker]} ({len(points)} sessions)")
        offset = (0, 10) if ticker == "BRENT" else (0, -16)
        ax.annotate(f"${prices[-1]:,.3f}".rstrip("0").rstrip("."),
                    (dates[-1], prices[-1]), xytext=offset,
                    textcoords="offset points", color=FG, fontsize=9,
                    ha="right", va="center")

    _style(ax, "Exact Energy EOD Mark History — Active Periods", "EOD mark (USD)", USDFMT)
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    fig.autofmt_xdate(rotation=0, ha="center")
    ax.legend(facecolor=PANEL, edgecolor=GRID, labelcolor=FG, fontsize=8, loc="best")
    fig.text(0.5, 0.015,
             "Exact user-provided daily marks from data/energy_provider_eod_marks_v1.csv; "
             "each line starts on its first active-position date. No proxy or approximate quotes shown.",
             ha="center", color=MUTED, fontsize=8)
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    path = CHARTS_DIR / "14-energy-eod-mark-history.png"
    fig.savefig(path, dpi=150, facecolor=BG, bbox_inches="tight")
    plt.close(fig)
    return path


# --------------------------------------------------------------------------
# Intraday charts
# --------------------------------------------------------------------------
def make_intraday_charts(iser, co):
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)
    x = list(range(N_BARS))
    files = []

    def save(fig, name):
        path = CHARTS_DIR / name
        fig.savefig(path, dpi=150, facecolor=BG, bbox_inches="tight")
        plt.close(fig)
        files.append(path)

    def xticks_hourly(ax, step=14):
        idx = list(range(6, N_BARS, step))
        ax.set_xticks(idx)
        ax.set_xticklabels([BAR_LABELS[i].replace(" ", "\n") for i in idx],
                           rotation=0, fontsize=7.5)

    # 09. Divergence sub-book, hourly
    fig, ax = plt.subplots(figsize=(13, 5.8))
    for v in VARIANTS:
        ax.plot(x, iser[v]["total"], label=VARIANT_LABEL[v],
                color=VARIANT_COLOR[v], lw=1.8)
    ax.axhline(0, color=MUTED, lw=1, ls="--", alpha=0.6)
    _style(ax, "Intraday PnL — Divergence Sub-Book (CAT · INTC · META · PLTR)",
           "PnL (USD)", USDFMT)
    xticks_hourly(ax)
    ax.legend(facecolor=PANEL, edgecolor=GRID, labelcolor=FG, fontsize=9, loc="upper left")
    save(fig, "09-intraday-sub-book-pnl.png")

    # 10. Intraday spreads with crossover markers
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(13, 8.6), sharex=True)
    for ax, key, title in [
        (ax1, "V1-V2", "V1 − V2 : stop-and-reverse effect (1U book)"),
        (ax2, "V3A-V3B", "V3A − V3B : stop-and-reverse effect (natural-unit book)"),
    ]:
        d = co[key]
        sp = d["spread"]
        ax.plot(x, sp, color="#a78bfa", lw=1.7)
        ax.fill_between(x, 0, sp, where=[s >= 0 for s in sp],
                        color="#34d399", alpha=0.25, interpolate=True)
        ax.fill_between(x, 0, sp, where=[s < 0 for s in sp],
                        color="#ef4444", alpha=0.25, interpolate=True)
        ax.axhline(0, color=MUTED, lw=1, ls="--", alpha=0.7)
        for bar, colour, mark in ((d["first_positive"], "#38bdf8", "first > 0"),
                                  (d["persists_from"], "#34d399", "stays > 0"),
                                  (d["peak_bar"], "#fbbf24", "peak")):
            if bar is None:
                continue
            ax.axvline(bar, color=colour, lw=1, ls=":", alpha=0.85)
            ax.annotate(f"{mark}\n{BAR_LABELS[bar]}\n${sp[bar]:,.0f}",
                        xy=(bar, sp[bar]), xytext=(8, 10),
                        textcoords="offset points", color=colour, fontsize=7.5)
        _style(ax, title, "Spread (USD)", USDFMT)
    xticks_hourly(ax2)
    fig.suptitle("Intraday Regime Flips — When One Model Overtakes Another",
                 color=FG, fontsize=14, fontweight="bold", y=0.985)
    save(fig, "10-intraday-spreads.png")

    # 11. Crossover zoom (V3A − V3B around Oct 13–17)
    d = co["V3A-V3B"]
    lo = max(0, (d["first_positive"] or 0) // BARS_PER_SESSION * BARS_PER_SESSION
             - 2 * BARS_PER_SESSION)
    hi = min(N_BARS, lo + 6 * BARS_PER_SESSION)
    fig, ax = plt.subplots(figsize=(12, 5.6))
    zx = list(range(lo, hi))
    zv = d["spread"][lo:hi]
    ax.plot(zx, zv, color="#a78bfa", lw=2.2, marker="o", ms=3)
    ax.fill_between(zx, 0, zv, where=[s >= 0 for s in zv],
                    color="#34d399", alpha=0.28, interpolate=True)
    ax.fill_between(zx, 0, zv, where=[s < 0 for s in zv],
                    color="#ef4444", alpha=0.28, interpolate=True)
    ax.axhline(0, color=MUTED, lw=1, ls="--", alpha=0.8)
    if d["first_positive"] is not None and lo <= d["first_positive"] < hi:
        ax.axvline(d["first_positive"], color="#38bdf8", lw=1.4, ls=":")
        ax.annotate(f"CROSSOVER\n{BAR_LABELS[d['first_positive']]} MST\n"
                    f"${d['spread'][d['first_positive']]:,.2f}",
                    xy=(d["first_positive"], d["spread"][d["first_positive"]]),
                    xytext=(12, 14), textcoords="offset points",
                    color="#38bdf8", fontsize=9, fontweight="bold")
    _style(ax, "Zoom — V3A Overtakes V3B (hourly bars, MST)", "Spread (USD)", USDFMT)
    ax.set_xticks(zx)
    ax.set_xticklabels([BAR_LABELS[i].replace(" ", "\n") for i in zx],
                       rotation=90, fontsize=7)
    save(fig, "11-crossover-zoom.png")

    # 12. Per-ticker intraday paths (2x2)
    fig, axes = plt.subplots(2, 2, figsize=(13, 8), sharex=True)
    for ax, sym in zip(axes.ravel(), DIVERGENCE):
        for v in VARIANTS:
            ax.plot(x, iser[v]["per_ticker"][sym], label=VARIANT_LABEL[v],
                    color=VARIANT_COLOR[v], lw=1.5)
        ax.axhline(0, color=MUTED, lw=1, ls="--", alpha=0.6)
        _style(ax, f"{sym} — intraday PnL by model", "PnL (USD)", USDFMT)
        ax.set_xlabel("")
    for ax in axes[1]:
        ax.set_xticks(list(range(6, N_BARS, 14)))
        ax.set_xticklabels([BAR_LABELS[i].replace(" ", "\n")
                            for i in range(6, N_BARS, 14)], fontsize=7.5)
    axes[0, 0].legend(facecolor=PANEL, edgecolor=GRID, labelcolor=FG,
                      fontsize=8, loc="upper left")
    fig.suptitle("Where Each Model's Edge Comes From", color=FG,
                 fontsize=14, fontweight="bold", y=0.98)
    save(fig, "12-intraday-per-ticker.png")
    return files


# --------------------------------------------------------------------------
# Data exports
# --------------------------------------------------------------------------
def write_intraday_csv(iser, co):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    path = DATA_DIR / "model_performance_intraday.csv"
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["bar_index", "bar_close_mst", "session_date", "bar_in_session"]
                   + [f"{v}_subtotal_usd" for v in VARIANTS]
                   + [f"{v}_{s}_usd" for v in VARIANTS for s in DIVERGENCE]
                   + ["spread_V1_V2_usd", "spread_V3A_V3B_usd"])
        for i in range(N_BARS):
            w.writerow([i, BAR_LABELS[i], SESSION_DATES[BAR_SESSION[i]],
                        i % BARS_PER_SESSION]
                       + [f"{iser[v]['total'][i]:.2f}" for v in VARIANTS]
                       + [f"{iser[v]['per_ticker'][s][i]:.2f}"
                          for v in VARIANTS for s in DIVERGENCE]
                       + [f"{co['V1-V2']['spread'][i]:.2f}",
                          f"{co['V3A-V3B']['spread'][i]:.2f}"])
    return path


def write_csv(series):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    path = DATA_DIR / "model_performance_daily.csv"
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["variant", "session_date", "session_index",
                    "realized_cum_usd", "unrealized_usd", "total_pnl_usd",
                    "daily_delta_usd", "roi_pct", "deployed_usd",
                    "open_units", "drawdown_usd", "us10y_yield_close_pct",
                    "us10y_spread_pct_points", "yield_adjustment_daily_usd",
                    "yield_adjustment_cumulative_usd", "adjusted_total_pnl_usd",
                    "adjusted_roi_pct"])
        for v in VARIANTS:
            s = series[v]
            for i, d in enumerate(s["dates"]):
                yield_close = s["us10y_yield_pct"][i]
                spread_points = s["us10y_spread_pct_points"][i]
                realized_display, unrealized_display = _display_components(
                    s["realized"][i], s["total"][i]
                )
                total_display = _cents(s["total"][i])
                adjusted_display = total_display + _cents(s["yield_adjustment"][i])
                w.writerow([v, d, i,
                            f"{realized_display:.2f}", f"{unrealized_display:.2f}",
                            f"{total_display:.2f}", f"{s['delta'][i]:.2f}",
                            f"{s['roi'][i]:.4f}", f"{s['deployed'][i]:.2f}",
                            f"{_unitfmt(s['open_units'][i])}", f"{s['drawdown'][i]:.2f}",
                            "" if yield_close is None else f"{yield_close:.3f}",
                            "" if spread_points is None else f"{spread_points:.3f}",
                            f"{s['yield_adjustment_daily'][i]:.4f}",
                            f"{s['yield_adjustment'][i]:.4f}",
                            f"{adjusted_display:.2f}",
                            f"{s['adjusted_roi'][i]:.4f}"])
    return path


def write_ticker_csv(contrib):
    path = DATA_DIR / "model_performance_tickers.csv"
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["variant", "ticker", "units_deployed",
                    "realized_usd", "unrealized_usd", "total_usd"])
        for v in VARIANTS:
            for sym in sorted(contrib[v], key=lambda s: -contrib[v][s]["total"]):
                d = contrib[v][sym]
                w.writerow([v, sym, _unitfmt(d['units']),
                            f"{d['realized']:.2f}", f"{d['unrealized']:.2f}",
                            f"{d['total']:.2f}"])
    return path


def write_json(series, contrib, iser=None, co=None, yield_rows=None):
    path = DATA_DIR / "model_performance_summary.json"
    payload = {
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "cohort": "Fall (Arizona) [2026]",
        "timezone": "America/Phoenix — MST / UTC-07:00 (no DST)",
        "unit_notional_usd": UNIT,
        "sessions": SESSION_DATES,
        "divergence_tickers": DIVERGENCE,
        "us10y_adjustment": {
            "status": "legacy additive reference; not used by whole-portfolio multiplier scenarios",
            "baseline_yield_pct": US10Y_BASELINE_PCT,
            "start_date": US10Y_ADJUSTMENT_START,
            "day_count": "actual/365",
            "formula": "cumulative deployed notional × ((US10Y close pct − baseline pct) / 100) × elapsed calendar days / 365",
            "source_files": [p.name for p in US10Y_SOURCE_FILES],
            "holiday_method": "user-confirmed: forward-fill last available Treasury close to equity sessions without a Treasury observation; Oct 12 uses Oct 9 close",
            "rows": [{k: row[k] for k in (
                "date", "yield_pct", "source_date", "carried_forward",
                "baseline_pct", "spread_pct_points", "interval_start_date",
                "accrual_days", "applied_yield_pct")}
                for row in (yield_rows or [])],
        },
        "variants": {
            v: {
                "label": VARIANT_LABEL[v],
                "color": VARIANT_COLOR[v],
                "series": {k: series[v][k] for k in
                           ("total", "realized", "unrealized", "roi",
                            "delta", "deployed", "open_units", "drawdown",
                            "us10y_yield_pct", "us10y_spread_pct_points",
                            "yield_adjustment_daily", "yield_adjustment",
                            "adjusted_total", "adjusted_roi")},
                "stats": series[v]["stats"],
                "tickers": contrib[v],
            }
            for v in VARIANTS
        },
    }
    if iser is not None and co is not None:
        payload["intraday"] = {
            "bars": N_BARS,
            "bars_per_session": BARS_PER_SESSION,
            "labels": BAR_LABELS,
            "session_index": BAR_SESSION,
            "series": {
                v: {"total": iser[v]["total"], "per_ticker": iser[v]["per_ticker"]}
                for v in VARIANTS
            },
            "spreads": {k: d["spread"] for k, d in co.items()},
            "milestones": {
                k: {kk: vv for kk, vv in d.items() if kk != "spread"}
                for k, d in co.items()
            },
        }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


# --------------------------------------------------------------------------
# Markdown report
# --------------------------------------------------------------------------
def _money(x):
    return (f"-${abs(x):,.2f}" if x < 0 else f"${x:,.2f}")


def _cents(value):
    return float(f"{value:.2f}")


def _display_components(realized, total):
    """Round realized and total, then make unrealized the cent-level residual."""
    realized_display = _cents(realized)
    total_display = _cents(total)
    return realized_display, round(total_display - realized_display, 2)


def _bl(i):
    return f"`{BAR_LABELS[i]} MST`" if i is not None else "—"


def write_markdown(series, contrib, charts, daily_csv, ticker_csv, summary_json,
                   iser=None, co=None, icharts=None, intraday_csv=None,
                   yield_chart=None, yield_csv=None):
    n = len(SESSION_DATES)
    last = n - 1
    symbol_count = len(PRICES)
    invariant_symbol_count = symbol_count - len(DIVERGENCE)
    direct_price_events = parse_trades()
    direct_modeled_event_count = sum(event["date"] <= SESSION_DATES[-1] for event in direct_price_events)
    post_terminal_event_count = len(direct_price_events) - direct_modeled_event_count
    dxy_log = (ROOT / "trades" / "DXY.txt").read_text(encoding="utf-8").splitlines()
    dxy_signal_count = sum(
        bool(re.search(r"\[(?:LONG|REBUY|SHORT)\]", line))
        and line[:10] <= SESSION_DATES[-1]
        for line in dxy_log if line.strip() and not line.lstrip().startswith("#")
    )
    trade_files = [p for p in (ROOT / "trades").glob("*.txt") if p.name != "index.txt"]
    book_event_count = sum(
        1 for p in trade_files for line in p.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    )
    modeled_event_count = direct_modeled_event_count + dxy_signal_count
    price_unmodeled_event_count = book_event_count - len(direct_price_events) - dxy_signal_count
    post_cutoff_manual_replenishments = [
        event for event in direct_price_events
        if event["date"] > SESSION_DATES[-1]
        and "Manual replenishment entry" in event["note"]
    ]
    term = {v: series[v]["total"][last] for v in VARIANTS}
    spread_ab = term["V1"] - term["V2"]
    spread_cd = term["V3A"] - term["V3B"]
    spread_size = term["V3A"] - term["V1"]
    flat_units = series["V1"]["stats"]["units"]
    natural_units = series["V3A"]["stats"]["units"]
    flat_deployed = series["V1"]["stats"]["deployed"]
    natural_deployed = series["V3A"]["stats"]["deployed"]

    lines = []
    A = lines.append
    A("# THE ONE MODEL")
    A("")
    A("![THE ONE MODEL vs THE WINNING MODEL — equal terminal gross additions](Charts/superstructure/the-one-model-vs-winning-model.png)")
    A("")
    A("*Equal-gross comparison with the top terminal-PnL constituent selected ex post from this same period; its daily path is scaled to match THE ONE MODEL's terminal gross additions. This is a hypothetical, selection-biased comparison—not out-of-sample evidence.*")
    A("")
    A("> **TradingView-only interim recalculation — 2026-10-24.** Core results below combine the 31 supplied direct-price TradingView symbols with a 1U/DAY/DXY currency-index sleeve across 36 common sessions. The DXY sleeve adds one 1U tranche each active EOD in the latest charted LONG/REBUY/SHORT direction; its current single LONG badge controls despite the conflicting caption. BTC and ETH remain excluded pending recalibration. No legacy or substitute prices are used. XRH0 has five transparently flagged carry-forward marks from prior supplied TradingView closes. See [`data/tradingview_benchmark_coverage_20261024.csv`](data/tradingview_benchmark_coverage_20261024.csv), [`data/tradingview_benchmark_session_marks_20261024.csv`](data/tradingview_benchmark_session_marks_20261024.csv), and the [crypto pending page](Crypto%20Sidecar%20%E2%80%94%20Pending%20TradingView%20Recalibration.md).")
    A("> **Updated source archive:** the revised Part B ZIP changes LLY's Oct. 20 TradingView mark from `$12,833.66` to `$1,283.66`; all model results below use the revised source and have been regenerated. See [`research/notes/tradingview-benchmark-import-20261024.md`](research/notes/tradingview-benchmark-import-20261024.md) and the Part B manifest.")
    A("")
    A("![THE ONE MODEL 32-portfolio split-strategy superstructure](Charts/superstructure/the-one-model.png)")
    A("")
    A("*Four-by-four Core × variant-specific 1U/EOD pairings, each tracked with and without its own energy sidecar; all 32 portfolios are summed without netting.*")
    A("")
    A("![THE ONE MODEL 32-portfolio split-strategy aggregate PnL, gross notional, and deployed-notional ratio](Charts/superstructure/the-one-model-split-portfolio.png)")
    A("")
    A("*Aggregate of 32 independent portfolios; percentage is PnL ÷ gross notional added, not an account return.*")
    A("")
    A("## Model Performance Comparison — *Fall (Arizona) [2026]*")
    A("")
    A("Day-by-day (and, where market data supports it, intraday) comparison of the four "
      "portfolio models carried on the same standardized book: "
      "**[`trades/`](trades/)** / **[`trades.zip`](trades.zip)** — "
      f"`{symbol_count}` direct-price core tickers plus the integrated 1U/DAY/DXY sleeve, "
      f"`{direct_modeled_event_count}` direct-price events plus `{dxy_signal_count}` DXY direction signals out of "
      f"`{book_event_count}` total 2026 log events (`{price_unmodeled_event_count}` other events outside scope; "
      f"`{post_terminal_event_count}` direct events after cutoff), "
      "`1U = $10,000.00` standard notional, all timestamps in Arizona year-round "
      "**`MST` / `UTC-07:00`**, marked against the **Friday, October 23, 2026** close. Intraday plots remain on their supplied Oct. 22 hourly scope.")
    A("")
    if post_cutoff_manual_replenishments:
        replenishment_details = []
        for event in post_cutoff_manual_replenishments:
            symbol = "USOIL (internal ticker OIL)" if event["sym"] == "OIL" else event["sym"]
            price = f"{event['px']:,.3f}".rstrip("0").rstrip(".")
            if "approximate time per user" in event["note"] and "17:20–17:25" in event["note"]:
                time_label = "approx. 17:20–17:25 MST (modeled at 17:22)"
            elif "approximate time per user" in event["note"]:
                time_label = f"approx. {event['time']} MST"
            else:
                time_label = f"{event['time']} MST"
            replenishment_details.append(
                f"{event['date']} {symbol} LONG {event['units']:g}U at ${price} ({time_label})"
            )
        A(
            "> **Post-cutoff manual replenishments:** "
            + "; ".join(replenishment_details)
            + " are recorded in the trade logs but fall after the Oct. 23 terminal mark. "
            "No post-entry EOD marks are included, so these entries are excluded from current core PnL and composites pending a later benchmark refresh."
        )
        A("")
    A("> **Oil target-trim force-multiplier shorts:** separate hypothetical 10U SHORT lots in BRENT at $117 and OIL at $102 are modeled from the Oct. 23 target-trim session, in addition to the partial sales and remaining longs. The target-level EOD trigger is the model entry assumption, not a verified intraday touch or fill. Both shorts remain open at the Oct. 23 cutoff; at that session's EOD marks, they contribute -$294.87 BRENT and -$1,421.57 OIL unrealized PnL (-$1,716.44 per core path). Their user-directed modeled exits are $114.627 BRENT and $100.74 OIL at 2026-10-25 20:35 MST, after the four earlier Oct. 25 10U replenishments and simultaneous with separate 35U BRENT and 34U OIL LONG Weekend Oil buys. Those new LONG lots are distinct from the 10U SHORT closures and count toward buy-side weekly supply; closing the shorts does not count toward that supply. Added to the existing post-close 65U BRENT plus 66U OIL core longs, they bring all-core long exposure to 100U per ticker, 200U total ($2,000,000 fixed-unit notional). The exits override SAR auto-close only for the two tagged target-level shorts; all prices/timing and trades are hypothetical model inputs, not verified brokerage executions. At the fixed $100,000 notional per lot, the exits imply +$2,028.21 BRENT and +$1,235.29 OIL (+$3,263.50 combined short PnL before costs) when replayed, but this post-cutoff result is excluded from current terminal core totals.")
    A("> **Oil cost-basis savings:** the realized target-trim PnL and the separately modeled post-cutoff SHORT-exit PnL are credited against tagged residual-plus-replenishment long lots as basis reclassifications, not additional profit. The short-exit credit is excluded from current Oct. 23 core PnL. The additional 35U BRENT and 34U OIL LONG buys are separate post-cutoff lots, not part of the existing residual-plus-10U-replenishment basis-credit calculation. See [`Oil Cost Basis Savings Model.md`](Oil%20Cost%20Basis%20Savings%20Model.md) and [`oil_cost_basis_savings_v1.csv`](data/oil_cost_basis_savings_v1.csv).")
    A("")
    A("> **Interactive version:** open **[`Model Performance Explorer.html`](Model%20Performance%20Explorer.html)** "
      "for a self-contained explorer with toggleable series, a hover crosshair, and per-ticker "
      "breakdowns. Machine-readable exports live in [`data/`](data/): "
      f"[`{daily_csv.name}`](data/{daily_csv.name}), "
      f"[`{ticker_csv.name}`](data/{ticker_csv.name}), "
      f"[`{summary_json.name}`](data/{summary_json.name}).")
    A("> **DXY and historical account views:** the 1U/DAY/DXY index-return sleeve is included in every core variant. THE ONE MODEL's 32-portfolio split aggregate additionally adds the 10U/DAY DXY schedule to each portfolio, for 11U/DAY total; its regenerated totals are shown in the aggregate chart and portfolio audit export. Do not add the 1U sleeve twice. The 0.05U schedule remains an alternative. The separate DXY-numeraire and yield-multiplier views have been rebuilt using the current core paths; they remain sensitivities rather than additional core PnL.")
    A("> **Small Caps pilot:** **[`Small Caps [Buyout & Reorganization Offering Test Pilot].md`](Small%20Caps%20%5BBuyout%20%26%20Reorganization%20Offering%20Test%20Pilot%5D.md)** tracks the five LCID entries; all five are included in the Oct. 23 four-model comparison.")
    A("> **Energy and DXY sizing:** **[`TradingView Energy and Currency Desk Sidecars.md`](TradingView%20Energy%20and%20Currency%20Desk%20Sidecars.md)** provides the standard energy sizes and DXY schedule audit. The DXY 1U/DAY series is included in core variants. THE ONE MODEL adds the 10U/DAY DXY schedule to every split portfolio (11U/DAY combined) and uses 11U/DAY energy tranches per active ticker in its 16 energy-inclusive portfolios. The strategy-comparison composites below retain their existing 10U energy schedule; 0.05U DXY remains an alternative. The user-specified 50U-long BRENT plus 50U-long USOIL Manual-Automatic entries and their targeted 10U trims are now included in all four core variants and flow into downstream core-based results. [`Weekend Oil 50U Position Hypothetical.md`](Weekend%20Oil%2050U%20Position%20Hypothetical.md) is a lot-level attribution of those same core lots, not an additional overlay.")
    A("> **Strategy and sidecar comparison:** **[`Strategy and Sidecar Comparison.md`](Strategy%20and%20Sidecar%20Comparison.md)** compares the existing variants, the fixed-$500/EOD and shared/variant-specific 1U/EOD force models, and additive composites using the 10U TradingView energy schedule.")
    A("> **How the models work:** **[`Model Calculation Guide.md`](Model%20Calculation%20Guide.md)** explains unit sizing, day-by-day lot handling, close/reversal behavior, and PnL formulas.")
    A("")
    A("## The Four Models")
    A("")
    A("| Model | Rule | Units deployed | Realized | Unrealized | Base PnL | Legacy additive US10Y carry (reference) | **Legacy adjusted PnL** | **Legacy adjusted ROI** |")
    A("|---|---|---:|---:|---:|---:|---:|---:|---:|")
    for v in VARIANTS:
        s = series[v]
        realized_display, unrealized_display = _display_components(s["realized"][last], term[v])
        carry_display = _cents(s["yield_adjustment"][last])
        adjusted_display = _cents(term[v]) + carry_display
        A(f"| **{VARIANT_LABEL[v]}** | "
          f"{'logged entry sizes; explicit exits close longs' if v == 'V1' else ''}"
          f"{'V1 sizing plus LONG/REBUY closes open shorts' if v == 'V2' else ''}"
          f"{'V1 behavior; qualifying compounded shorts use preceding full-exit units' if v == 'V3A' else ''}"
          f"{'V2 behavior plus qualifying compounded shorts' if v == 'V3B' else ''} | "
          f"{s['stats']['units']:.1f}U (${s['stats']['deployed']:,.0f}) | "
          f"{_money(realized_display)} | {_money(unrealized_display)} | "
          f"{_money(term[v])} | {_money(carry_display)} | "
          f"**{_money(adjusted_display)}** | "
          f"**{s['adjusted_roi'][last]:.2f}%** |")
    A("")
    A("Displayed dollar components are rounded to cents and reconciled so realized plus unrealized equals Base PnL; legacy adjusted PnL equals displayed Base PnL plus the displayed carry. Unrounded replay values drive model calculations and charts.")
    A("")
    A("## TradingView Benchmark and Alignment")
    A("")
    A("The 31 directly priced core tickers use the normalized user-provided Part A and Part B TradingView lists only, aligned to the 36-session common calendar. A 1U/DAY/DXY index-return sleeve, activated by charted direction, is integrated into each model total and deployed-notional denominator; DXY is not represented as a directly traded security. The session marks and provenance are in [`tradingview_benchmark_session_marks_20261024.csv`](data/tradingview_benchmark_session_marks_20261024.csv); raw imported rows, coverage, and archive hashes are preserved alongside them. BTC and ETH have no marks in this core and remain pending recalibration.")
    A("")
    A("**Provisional XRH0 convention:** five missing source sessions (`2026-09-15`, `2026-10-07`, `2026-10-08`, `2026-10-19`, and `2026-10-22`) carry forward the previous supplied TradingView close. Each row is explicitly flagged. No external or legacy price is inserted; revisit this convention if a different gap treatment is preferred.")
    A("")
    A("Crypto status: [**Crypto Sidecar — Pending TradingView Recalibration**](Crypto%20Sidecar%20%E2%80%94%20Pending%20TradingView%20Recalibration.md). Energy schedules, DXY index-return assumptions, and standalone DXY sizing alternatives: [**TradingView Energy and Currency Desk Sidecars**](TradingView%20Energy%20and%20Currency%20Desk%20Sidecars.md). The 1U/DAY/DXY schedule from that page is already included in core PnL.")
    A("")
    if yield_chart is not None and yield_csv is not None:
        A("## Legacy Model-Level US10Y Additive Carry (Reference Only)")
        A("")
        A("This inherited per-model additive overlay is retained for audit comparison, but it is "
          "not the active whole-portfolio blanket factor and is not included in the new DXY-view "
          "scenarios. Use the linked Whole Portfolio Yield Multiplier Explorer to compare the "
          "full account value with no yield factor, US10Y alone, and US10Y compounded with US30Y. "
          "This yield-based overlay is not a CPI inflation measure or Treasury total-return calculation. It treats the user-provided "
          f"daily US10Y closes as annualized carry relative to the `{US10Y_BASELINE_PCT:.3f}%` "
          f"baseline from `{US10Y_ADJUSTMENT_START}`. For each interval, the adjustment is the "
          "model's cumulative deployed notional (the same denominator used for ROI; it does not "
          "fall after a position closes) × ((yield close − 4.865) / 100) × actual calendar days / 365. "
          "Values above baseline add positive adjustment; below baseline subtract. Per your "
          "confirmation, the Oct 9 close (5.24%) is carried across the Oct 12 Treasury holiday; "
          "the export records the original source date. The Oct 23 close (4.986%) is marked at the latest session; "
          "the Oct 22-to-Oct 23 carry interval uses the Oct 22 close (4.96%) under the existing start-of-interval convention.")
        A("")
        A(f"![US10Y yield baseline and cumulative adjustment]({yield_chart.relative_to(ROOT).as_posix()})")
        A("")
        A(f"Session-level rates, forward-fill dates, actual/365 accruals, and adjusted totals: "
          f"[`{yield_csv.name}`](data/{yield_csv.name}).")
        A("")
    A("## TradingView Energy Sidecar")
    A("")
    A("Brent and WTI core positions use the supplied aligned TradingView marks. Energy and DXY sizing alternatives are documented with per-session source flags in [`TradingView Energy and Currency Desk Sidecars.md`](TradingView%20Energy%20and%20Currency%20Desk%20Sidecars.md). The 1U/DAY/DXY index-return sleeve is already included in each core variant; do not add the 1U DXY schedule twice. Standard strategy composites add the 10U energy schedule. THE ONE MODEL separately uses 11U/DAY per active energy ticker in its 16 energy-inclusive portfolios; its derived machine-readable schedule is [`the_one_model_energy_11u_sidecar_daily_v1.csv`](data/the_one_model_energy_11u_sidecar_daily_v1.csv). Chart-opened core energy positions are shown separately and are not double-counted. Machine-readable standard schedules: [`tradingview_energy_sidecar_daily_20261024.csv`](data/tradingview_energy_sidecar_daily_20261024.csv) and [`dxy_currency_desk_sidecar_daily_20261024.csv`](data/dxy_currency_desk_sidecar_daily_20261024.csv).")
    dxy_core = contrib["V1"].get("DXY", {"units": 0.0, "total": 0.0})
    A(f"**Integrated 1U/DAY/DXY sleeve (same across all four core variants):** {dxy_core['units']:.0f} daily units, **${dxy_core['units'] * UNIT:,.2f}** gross notional added, terminal proxy PnL **${dxy_core['total']:+,.2f}**. This is already included in the four-model results above.")
    A("")
    A("![TradingView-sourced energy EOD mark history](Charts/performance/14-energy-eod-mark-history.png)")
    A("")
    A(f"All four models agree on `{invariant_symbol_count}` of the `{symbol_count}` tickers. They diverge only on "
      "**`CAT`, `INTC`, `META` and `PLTR`** — the four symbols where a short is followed by a "
      "long (or a full exit is compounded into a short). Everything below is driven by those four.")
    A("")
    A("## Headline Chart")
    A("")
    A(f"![Cumulative base trading PnL by session]({charts[0].relative_to(ROOT).as_posix()})")
    A("")
    A("**Reading it:** the models begin close together, then spread as the reversal-sensitive "
      "positions develop. At the Oct. 23 close the base and legacy additive US10Y-adjusted rankings are "
      f"**{' > '.join(sorted(VARIANTS, key=lambda v: term[v], reverse=True))}** and "
      f"**{' > '.join(sorted(VARIANTS, key=lambda v: series[v]['adjusted_total'][last], reverse=True))}**, respectively.")
    A("")
    A("## Base Return on Capital")
    A("")
    A(f"![Cumulative base ROI by session]({charts[1].relative_to(ROOT).as_posix()})")
    A("")
    A("This chart shows base trading PnL before the legacy additive US10Y carry; the legacy adjusted ROI "
      "is shown for reference in the model table above and selectable in the interactive explorer. "
      "For whole-account factor scenarios, use the linked Yield Multiplier Explorer.")
    A("")
    A(f"Raw dollars flatter V3A/V3B because they deploy more capital — `{_unitfmt(natural_units)}` units "
      f"(`{_money(natural_deployed)}`) against V1/V2's `{_unitfmt(flat_units)}` units "
      f"(`{_money(flat_deployed)}`). ROI normalises for that, and the terminal ranking is "
      "unchanged: compounding shorts into full exits beats flat sizing on both capital bases, "
      "and *not* stop-and-reversing beats stop-and-reversing on both.")
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
        realized_display, unrealized_display = _display_components(s["realized"][last], term[v])
        A(f"| **{VARIANT_LABEL[v]}** | {_money(realized_display)} | "
          f"{_money(unrealized_display)} | {s['stats']['n_realized']} | "
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
        A(f"| `{sym}` | {_unitfmt(d['units'])}U | {_money(d['realized'])} | "
          f"{_money(d['unrealized'])} | **{_money(d['total'])}** |")
    A("")
    A("Ticker units preserve fractional logged sizes. Each ticker total equals its cent-rounded realized plus unrealized components; summing independently rounded ticker rows can differ from the unrounded model total by a few cents.")
    A("")
    A("### Bottom contributors (V3A)")
    A("")
    A("| Ticker | Units | Realized | Unrealized | **Total** |")
    A("|---|---:|---:|---:|---:|")
    bot = sorted(contrib["V3A"].items(), key=lambda kv: kv[1]["total"])[:10]
    for sym, d in bot:
        A(f"| `{sym}` | {_unitfmt(d['units'])}U | {_money(d['realized'])} | "
          f"{_money(d['unrealized'])} | **{_money(d['total'])}** |")
    A("")
    if iser is not None and co is not None:
        A("## Intraday — Hour by Hour")
        A("")
        A("Daily closes hide *when* inside a session the models pull apart. Zooming to "
          "**hourly bars** (7 per session: `06:30`→`13:00 MST`) resolves that.")
        A("")
        A(f"> **Scope:** the intraday view covers **`CAT`, `INTC`, `META` and `PLTR`** — the "
          f"divergence sub-book. The other `{invariant_symbol_count}` tickers produce byte-identical PnL under all "
          "four models, so they cancel exactly out of every comparison below. Every number "
          "here is therefore *exact*, not interpolated.")
        A("")
        A(f"![Intraday divergence sub-book]({icharts[0].relative_to(ROOT).as_posix()})")
        A("")
        A("### Terminal, divergence sub-book only")
        A("")
        A("| Model | Realized | Unrealized | **Sub-book total** |")
        A("|---|---:|---:|---:|")
        for v in VARIANTS:
            s = iser[v]
            realized_display, unrealized_display = _display_components(
                s["realized"][-1], s["total"][-1]
            )
            A(f"| **{VARIANT_LABEL[v]}** | {_money(realized_display)} | "
              f"{_money(unrealized_display)} | **{_money(_cents(s['total'][-1]))}** |")
        A("")
        A(f"The sub-book totals differ from the full-portfolio totals above by exactly the "
          f"{invariant_symbol_count} invariant tickers, which contribute the same amount to every model.")
        A("")
        A("### The regime flips")
        A("")
        A(f"![Intraday spreads]({icharts[1].relative_to(ROOT).as_posix()})")
        A("")
        A(f"![Crossover zoom]({icharts[2].relative_to(ROOT).as_posix()})")
        A("")
        A("| Spread | First > 0 | Stays > 0 from | Peak | Trough | Terminal |")
        A("|---|---|---|---:|---:|---:|")
        for key in ("V1-V2", "V3A-V3B", "V3A-V1", "V3B-V2"):
            d = co[key]
            A(f"| **{key}** | {_bl(d['first_positive'])} | {_bl(d['persists_from'])} | "
              f"{_money(d['peak'])} @ {_bl(d['peak_bar'])} | "
              f"{_money(d['trough'])} @ {_bl(d['trough_bar'])} | "
              f"**{_money(d['terminal'])}** |")
        A("")
        A("**What this says — stop-and-reverse is a help early and a drag late.** Both "
          "spreads open the season deeply *negative*, meaning the **SAR books lead** out of "
          "the gate: at " + _bl(co["V1-V2"]["trough_bar"]) + " `V2` is ahead of `V1` by "
          f"{_money(-co['V1-V2']['trough'])} and `V3B` is ahead of `V3A` by "
          f"{_money(-co['V3A-V3B']['trough'])} — the widest SAR lead of the whole season, "
          "on the same bar. Flipping a position instead of stacking a new one protects "
          "capital while prices run *against* the earlier direction.")
        A("")
        A("That lead then erodes as the trend matures, and the **open books take over for "
          "good in the `Oct 14`–`Oct 16` window**: `V3A − V3B` first prints positive at "
          f"{_bl(co['V3A-V3B']['first_positive'])} and never looks back from "
          f"{_bl(co['V3A-V3B']['persists_from'])}; `V1 − V2` flips a day later and holds "
          f"from {_bl(co['V1-V2']['persists_from'])}. Once the moves are directional, "
          "reversing out of the original entry throws away the winner — which is why the "
          "two spreads end the season on opposite sides of zero, and `"
          f"{abs(co['V3A-V3B']['terminal'] / co['V1-V2']['terminal']):.1f}×` apart in "
          "magnitude.")
        A("")
        A("Compounding shorts into full exits, by contrast, is unambiguous: `V3A − V1` "
          f"turns positive on {_bl(co['V3A-V1']['first_positive'])} — the moment the "
          "`INTC` `5-unit` full exit at `$127.11` is compounded — and never crosses back.")
        A("")
        A("### Which ticker drives each edge")
        A("")
        A(f"![Intraday per ticker]({icharts[3].relative_to(ROOT).as_posix()})")
        A("")
        A("Intraday per-ticker contribution at the Oct 22 close (the hourly archive has no Oct 23 bars):")
        A("")
        A("| Ticker | " + " | ".join(VARIANTS) + " | Intraday peak bar (V3A) |")
        A("|---|" + "---:|---:|---:|---:|" + "---|")
        for sym in DIVERGENCE:
            col = iser["V3A"]["per_ticker"][sym]
            pk = max(range(N_BARS), key=lambda i: col[i])
            A(f"| `{sym}` | " + " | ".join(
                _money(iser[v]["per_ticker"][sym][-1]) for v in VARIANTS) +
              f" | {_bl(pk)} |")
        A("")
        A(f"Full per-bar series: [`{intraday_csv.name}`](data/{intraday_csv.name}) "
          f"({N_BARS} rows).")
        A("")

    A("## Supplemental Portfolio, Pilot, and Sidecar Graphs")
    A("")
    A("The following views extend beyond the four core direct-price variants. They use distinct account bases or sidecar schedules where noted; they are not all on a common capital base, and their positions/capital must not be netted or stacked implicitly.")
    A("")
    A("### Whole-Portfolio DXY Numeraire and Yield Scenarios")
    A("")
    A("> **Historical only—not recalculated on the current TradingView core.** The DXY-numeraire and yield-multiplier graphs below retain their previous portfolio benchmark and must not be read as current results. The current 1U/DAY/DXY index-return sleeve is integrated into the core; its sizing alternatives are in [`TradingView Energy and Currency Desk Sidecars.md`](TradingView%20Energy%20and%20Currency%20Desk%20Sidecars.md).")
    A("")
    A("![DXY close vs whole-portfolio PnL in dollars](Charts/performance/17-dxy-close-vs-whole-portfolio-pnl-usd.png)")
    A("")
    A("![Whole-portfolio unrealized PnL and USD/DXY returns](Charts/performance/16-whole-portfolio-dxy-vs-usd-pnl.png)")
    A("")
    A("### LCID Small-Caps Pilot")
    A("")
    A("The five-entry LCID pilot is already included in the four-model replay through the corrected Oct. 23 mark; this graph is a focused component view, not another add-on to the core totals. See [`Small Caps [Buyout & Reorganization Offering Test Pilot].md`](Small%20Caps%20%5BBuyout%20%26%20Reorganization%20Offering%20Test%20Pilot%5D.md) for entry and mark details.")
    A("")
    A("![LCID small-caps pilot daily PnL and marks](Charts/performance/18-lcid-small-caps-pilot-pnl.png)")
    A("")
    A("### TradingView Energy and Currency Desk Sidecars")
    A("")
    A("The sidecar report presents 0.05U, 1U, and 10U sizing schedules. The chart-directed 1U/DAY/DXY index-return sleeve is integrated in every core variant; THE ONE MODEL adds the 10U schedule to each split portfolio, while 0.05U remains an alternative. Strategy-comparison composites retain their original scope and add the 10U energy schedule, not the DXY 10U schedule. See [`TradingView Energy and Currency Desk Sidecars.md`](TradingView%20Energy%20and%20Currency%20Desk%20Sidecars.md).")
    A("")
    A("![DXY daily-investment sizing options](Charts/performance/23-dxy-daily-sizing-alternatives.png)")
    A("")
    A("*The three panels show 0.05U, 1U, and 10U daily-lot PnL paths on separate scales. The 1U schedule is already included in core PnL; THE ONE MODEL adds the 10U schedule to every split portfolio (11U/DAY combined), while 0.05U remains an alternative.*")
    A("")
    A("The user-specified 50U-long BRENT and 50U-long USOIL Manual-Automatic lots were added to each core variant at the supplied Oct. 19 TradingView marks, with 10U target trims at $117 and $102 respectively. Their first recorded EOD marks at/above target are on Oct. 23; the daily closes do not verify an intraday touch or fill. The lots are included in the core replay and downstream aggregates; [`Weekend Oil 50U Position Hypothetical.md`](Weekend%20Oil%2050U%20Position%20Hypothetical.md) isolates their PnL for attribution only. Existing separate 1U core lots are not trimmed.")
    A("")
    A("![50U long BRENT and 50U long USOIL hypothetical PnL](Charts/CLN25/Weekend%20Oil/24-weekend-oil-50u-positions.png)")
    A("")
    A("### EOD Add-On and Variant-Specific 1U/EOD Comparisons")
    A("")
    A("The fixed-$500/EOD model and 1U/EOD alternatives are separate model families, not stacked on top of one another. The broad comparison distinguishes standalone results from additive composites; composites sum PnL and gross notionals without netting positions or capital. See [`Strategy and Sidecar Comparison.md`](Strategy%20and%20Sidecar%20Comparison.md) and [`Model Calculation Guide.md`](Model%20Calculation%20Guide.md) for full rules and tables.")
    A("")
    A("![Core models, separate $500 and 1U direction-following models, and sidecar combinations](Charts/performance/20-strategy-sidecar-comparison.png)")
    A("")
    A("The next chart contains all **16 Core × variant-specific 1U/EOD pairings**, including matching and cross-variant pairs, each with the 10U TradingView energy daily-buy sidecar. These are additive USD totals; positions and capital are not netted, and the core's chart-opened energy lots are not duplicated in the sidecar.")
    A("")
    A("![All 16 Core × 1U variant pairings with energy sidecar](Charts/performance/21-force-variant-oil-comparison.png)")
    A("")
    leaders = "; ".join(f"{label}, **{ratio:.2f}%**" for ratio, label in _top_split_portfolio_ratios())
    A("The percentage-gain view plots all **32 series**: the same 16 Core × 1U pairings, each with and without the energy sidecar. Gain is cumulative PnL divided by cumulative gross notional added—a deployed-notional ratio, **not an account return**. Only the top four terminal performers are named in the legend; all 32 are plotted. The earlier **8.88% static single-composite proxy is not a result for this 32-portfolio split**. The leading terminal ratios are " + leaders + ".")
    A("")
    A("![All 32 Core × 1U variant pairings with and without the energy sidecar, shown as deployed-notional percentage gain](Charts/performance/22-force-variant-oil-percent-gain.png)")
    A("")

    A("## Method & Caveats")
    A("")
    A(f"- **Model coverage:** the four variants directly price `{symbol_count}` TradingView tickers and include the chart-directed 1U/DAY/DXY index-return sleeve. `{direct_modeled_event_count}` direct-price trade events plus `{dxy_signal_count}` DXY direction signal are in scope through Oct. 23; `{post_terminal_event_count}` direct-price events after the mark are excluded. `{price_unmodeled_event_count}` other BTC, ETH, EURUSD, JPYUSD, US10Y, and US30Y log events are not replayed as direct-price positions. The two US10Y events establish yield-adjustment context; this report's additive carry is retained only as a legacy reference. Whole-account US10Y and compounded US30Y multiplier scenarios remain historical. DXY uses an index-return proxy, not an exchange-traded contract model.")
    A("- **Price source:** every direct-price core mark comes from the normalized user-provided TradingView Part A/Part B lists, aligned in [`data/tradingview_benchmark_session_marks_20261024.csv`](data/tradingview_benchmark_session_marks_20261024.csv). DXY's 1U/day proxy uses its separate supplied TradingView index marks and the charted direction signal; it is integrated into the core totals but is not a directly traded security. BTC/ETH remain pending and outside the core. Five missing XRH0 sessions use the last prior supplied TradingView close, with each carry-forward row explicitly flagged; this is a provisional mark convention. No Yahoo or historical-series fill is used.")
    A("- **Benchmark provenance and alignment:** Part A and Part B raw observations, per-ticker coverage, and archive hashes are preserved in the paired CSV/JSON artifacts under `data/`. DXY is marked separately from the 31 direct-price tickers but its chart-directed 1U/day proxy is integrated into this core portfolio. EURUSD, JPYUSD, US10Y, and US30Y remain outside. Do not interpret the historical whole-portfolio DXY/yield pages as recalculated from this benchmark.")
    A("- **Session calendar:** the `36` U.S. equity regular sessions from "
      f"`{SESSION_DATES[0]}` to `{SESSION_DATES[-1]}`. DXY index marks align to the same sessions; BTC/ETH remain excluded pending recalibration.")
    A("- **XRH0 interim marks:** the source list omits five common sessions (`2026-09-15`, `2026-10-07`, `2026-10-08`, `2026-10-19`, and `2026-10-22`). Those are carried forward from the prior supplied TradingView close and flagged in the session-mark CSV; no external price is inserted. Treat its interim path as provisional.")
    A("- **Performance scope:** logged core trade entries/exits retain their chart-posting prices; the additional DXY sleeve adds 1U at each active EOD in the latest charted direction, marked to the supplied TradingView index close. The integrated core totals therefore include DXY daily-investment PnL and notional. Historical whole-account/yield outputs and the master ledger are not recalculated by this run.")
    A("- **ROI** is cumulative PnL divided by notional deployed *to date* "
      "(units opened on or before that session × 1U standard notional), so early sessions show larger "
      "percentages on less capital.")
    A("- **Open units** are units still held at each session close; they decline when a position closes. "
      "This differs from cumulative units deployed, which continues to include previously closed units.")
    A("- **All-actionable-ticker audit:** an independent replay reconciles all 31 TradingView-priced core tickers, "
      "the integrated 1U/DAY/DXY sleeve, energy/DXY sizing schedules, position exports, and all 32 portfolio aggregates. "
      "See the current [`data/actionable_ticker_reconciliation_20261023_v1.csv`](data/actionable_ticker_reconciliation_20261023_v1.csv) audit output.")
    A("- Entry fills use the chart-posting prices recorded in the trade log, not later minute or session closes; "
      "the Sep. 24 INTC short uses the chart-posting price `$115.11`. Exits are realised on their log date.")
    A("- Excludes commissions, borrow fees, and overnight financing.")
    A("")
    A("---")
    A("")
    A("Master ledger: **[`Trades Zip PnL.md`](Trades%20Zip%20PnL.md)** · "
      "Chart-signal report: **[`Triangle Signals.md`](Triangle%20Signals.md)** · "
      "Visual book: **[`Unrealized PnL.md`](Unrealized%20PnL.md)** · "
      "Pre-2026: **[`2024 Trades PnL.md`](reports/2024/2024%20Trades%20PnL.md)**")
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
  .benchmark-notice{border:1px solid #eab308;background:#422006;color:#fef3c7;
    border-radius:9px;padding:14px 16px;margin:0 0 22px;font-size:13px}
  .benchmark-notice strong{color:#fde68a}
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
     (__START__ &rarr; __END__, MST) &middot; __NSYMS__ direct-price symbols + integrated 1U/DAY/DXY &middot; 1U = $10,000.00
     &middot; daily marks through the Oct 23, 2026 close; hourly intraday charts through Oct 22</p>
  <div class="benchmark-notice"><strong>TradingView-only interim core — 2026-10-24.</strong>
    This explorer reflects the 31 direct-price symbols plus integrated chart-directed 1U/DAY/DXY sleeve using the updated Part B archive. LLY's Oct. 20 close is $1,283.66 (superseding the prior $12,833.66 source row). BTC/ETH remain excluded pending recalibration. XRH0 has five flagged carry-forward marks. Historical whole-book/yield views are not part of these core results. <a href="data/tradingview_benchmark_coverage_20261024.csv">View coverage</a> · <a href="Crypto%20Sidecar%20%E2%80%94%20Pending%20TradingView%20Recalibration.md">Crypto status</a>.</div>

  <div class="card">
    <h2>Energy EOD marks used in the core replay and energy sidecar</h2>
    <p class="hint">Both use the same exact user-provided daily marks from <code>data/energy_provider_eod_marks_v1.csv</code>. BRENT: BlackBull Markets Brent Cash, Sep 23–Oct 23 (23 sessions), terminal $117.345. OIL: TradingView <code>TVC:USOIL</code>, Sep 10–Oct 23 (32 sessions), terminal $103.45. Yahoo <code>BZ=F</code>/<code>CL=F</code> are pre-entry context only; no separate approximate quote series is used in current totals.</p>
    <p><img src="Charts/performance/14-energy-eod-mark-history.png" alt="Exact user-provided energy EOD mark history by active period" style="max-width:100%;height:auto"></p>
  </div>

  <div class="card">
    <h2>Terminal results</h2>
    <p class="hint">Oct 23, 2026 close. The table includes a separately labeled legacy US10Y carry reference; the DXY-numeraire and whole-account yield views are historical and are not recalculated on this TradingView core. The DXY 1U/DAY index-return sleeve is included in core totals; its sizing alternatives are detailed in the currency-desk sidecar. The hourly intraday archive stops at Oct 22.</p>
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
    Generated __GEN__. Core marks: user-provided TradingView EOD lists. The four variants model
    the __NSYMS__ direct-price symbols; the integrated 1U/DAY/DXY sleeve uses supplied DXY index marks.
    EURUSD, JPYUSD and US30Y are outside this portfolio valuation. LCID pilot marks are user-provided. The per-model US10Y additive overlay is retained as a legacy reference only; whole-account US10Y and US30Y multiplier scenarios live in the linked explorer. The Oct 23 ORCL LONG and fifth LCID LONG are included in this EOD model replay.
    Intraday source charts remain through Oct 22. The master <b>Trades Zip PnL.md</b> is a legacy snapshot and has not been recalculated for
    the newly reconciled Oct 23 positions, including the Manual-Automatic 50U oil lots and modeled target trims, so its totals do not match this comparison. Excludes commissions,
    borrow fees and financing.
  </footer>
</div>
<script>
const DATA = __DATA__;
const VARS = ["V1","V2","V3A","V3B"];
const METRICS = {
  total:      {label:"Base cumulative trading PnL", fmt:v=>(v>=0?"+":"−")+"$"+Math.abs(v).toLocaleString(undefined,{minimumFractionDigits:2,maximumFractionDigits:2}), axis:v=>"$"+Math.round(v).toLocaleString()},
  adjusted_total: {label:"Legacy additive US10Y-adjusted cumulative PnL", fmt:v=>(v>=0?"+":"−")+"$"+Math.abs(v).toLocaleString(undefined,{minimumFractionDigits:2,maximumFractionDigits:2}), axis:v=>"$"+Math.round(v).toLocaleString()},
  yield_adjustment: {label:"Legacy cumulative US10Y carry reference", fmt:v=>(v>=0?"+":"−")+"$"+Math.abs(v).toLocaleString(undefined,{minimumFractionDigits:2,maximumFractionDigits:2}), axis:v=>"$"+Math.round(v).toLocaleString()},
  roi:        {label:"Base return on deployed capital", fmt:v=>(v>=0?"+":"")+v.toFixed(3)+"%", axis:v=>v.toFixed(1)+"%"},
  adjusted_roi: {label:"Legacy additive US10Y-adjusted return on deployed capital", fmt:v=>(v>=0?"+":"")+v.toFixed(3)+"%", axis:v=>v.toFixed(1)+"%"},
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
      <div class="k" style="margin-top:8px">Legacy additive US10Y carry / PnL (reference only)</div>
      <div style="font-size:13px;font-variant-numeric:tabular-nums">${usd(s.yield_adjustment[s.yield_adjustment.length-1])} / ${usd(s.adjusted_total[s.adjusted_total.length-1])}</div>
      <div class="k" style="margin-top:8px">adjusted ROI</div>
      <div style="font-size:13px">${pct(s.adjusted_roi[s.adjusted_roi.length-1])}</div>
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

/* ---------- intraday ---------- */
const IN = DATA.intraday;
const IMETRICS = {
  sub:   {label:"Divergence sub-book PnL", get:v=>IN.series[v].total},
  rz:    {label:"Realized (cumulative)",   get:v=>IN.series[v].realized},
  un:    {label:"Unrealized (open)",       get:v=>IN.series[v].unrealized},
  sp12:  {label:"Spread V1 − V2",          get:()=>IN.spreads["V1-V2"]},
  sp34:  {label:"Spread V3A − V3B",        get:()=>IN.spreads["V3A-V3B"]},
  sp31:  {label:"Spread V3A − V1",         get:()=>IN.spreads["V3A-V1"]},
  tick:  {label:"Per-ticker (V3A)",        get:()=>null}
};
let imetric="sub", depth="hour", ishown=new Set(VARS), isym="CAT";

const iEl=document.getElementById("imetrics");
iEl.innerHTML = Object.entries(IMETRICS).map(([k,m])=>
  `<button class="${k===imetric?"on":""}" data-i="${k}">${m.label}</button>`).join("");
iEl.onclick = e=>{ const b=e.target.closest("button"); if(!b) return;
  imetric=b.dataset.i; [...iEl.children].forEach(c=>c.classList.toggle("on",c===b));
  syncILegend(); drawI(); };

const dEl=document.getElementById("depth");
dEl.innerHTML = [["hour","Hourly bars (245)"],["session","Session closes (35)"]]
  .map(([k,l])=>`<button class="${k===depth?"on":""}" data-d="${k}">${l}</button>`).join("");
dEl.onclick = e=>{ const b=e.target.closest("button"); if(!b) return;
  depth=b.dataset.d; [...dEl.children].forEach(c=>c.classList.toggle("on",c===b)); drawI(); };

const ilEl=document.getElementById("ilegend");
function ilegendHTML(){
  if(imetric==="tick"){
    return IN.tickers.map(s=>
      `<label class="${s===isym?"on":""}" data-s="${s}"><span class="swatch" style="background:#a78bfa"></span>${s}</label>`).join("");
  }
  if(imetric.startsWith("sp"))
    return `<label class="on"><span class="swatch" style="background:#a78bfa"></span>Spread</label>`;
  return VARS.map(v=>
    `<label class="${ishown.has(v)?"on":""}" data-v="${v}"><span class="swatch" style="background:${DATA.variants[v].color}"></span>${DATA.variants[v].label}</label>`).join("");
}
function syncILegend(){ ilEl.innerHTML=ilegendHTML(); }
ilEl.onclick = e=>{ const l=e.target.closest("label"); if(!l) return;
  if(imetric==="tick"){ isym=l.dataset.s; }
  else if(!imetric.startsWith("sp")){ const v=l.dataset.v;
    if(ishown.has(v)&&ishown.size>1){ishown.delete(v);} else {ishown.add(v);} }
  syncILegend(); drawI(); };
syncILegend();

const ic=document.getElementById("ichart"), ix=ic.getContext("2d");
const tip3=document.getElementById("tip3");
let ig=null;

function drawI(){
  sizeCanvas(ic,420);
  const W=ic.clientWidth,H=420,L=80,R=16,T=16,B=56,pw=W-L-R,ph=H-T-B;
  ix.clearRect(0,0,W,H); ix.fillStyle="#141c2b"; ix.fillRect(0,0,W,H);
  const step = depth==="hour" ? 1 : IN.bars_per_session;
  const xs=[]; for(let i=(depth==="hour"?0:IN.bars_per_session-1); i<IN.bars; i+=step) xs.push(i);
  const n=xs.length;

  let seriesList=[];
  if(imetric==="tick"){
    seriesList=[{name:`${isym} (V3A)`,color:"#a78bfa",vals:xs.map(i=>IN.series.V3A.per_ticker[isym][i])}];
  } else if(imetric.startsWith("sp")){
    const vals=IMETRICS[imetric].get();
    seriesList=[{name:IMETRICS[imetric].label,color:"#a78bfa",vals:xs.map(i=>vals[i])}];
  } else {
    seriesList=VARS.filter(v=>ishown.has(v)).map(v=>({
      name:DATA.variants[v].label,color:DATA.variants[v].color,
      vals:xs.map(i=>IMETRICS[imetric].get(v)[i])}));
  }
  let vals=[]; seriesList.forEach(s=>s.vals.forEach(v=>vals.push(v)));
  if(!vals.length) return;
  let lo=Math.min(0,...vals), hi=Math.max(0,...vals); const pad=(hi-lo)*0.08||1;
  lo-=pad; hi+=pad;
  const X=j=>L+(n===1?pw/2:j*pw/(n-1));
  const Y=v=>T+ph-(v-lo)/(hi-lo)*ph;

  ix.strokeStyle="#243044"; ix.fillStyle="#93a4bd"; ix.font="11px ui-monospace,monospace";
  ix.textAlign="right";
  niceTicks(lo,hi,6).forEach(t=>{ const y=Y(t);
    ix.beginPath(); ix.moveTo(L,y); ix.lineTo(L+pw,y); ix.stroke();
    ix.fillText("$"+Math.round(t).toLocaleString(),L-8,y+4); });
  ix.strokeStyle="#3f4d66"; ix.beginPath(); ix.moveTo(L,Y(0)); ix.lineTo(L+pw,Y(0)); ix.stroke();
  ix.textAlign="center"; ix.font="9.5px ui-monospace,monospace";
  const every = depth==="hour" ? 14 : 3;
  xs.forEach((b,j)=>{ if(j%every===0||j===n-1){
    const lb=IN.labels[b];
    ix.save(); ix.translate(X(j),H-B+12); ix.rotate(-Math.PI/4);
    ix.fillText(lb,0,0); ix.restore(); }});

  seriesList.forEach(s=>{
    if(s.vals.some(v=>v<0) && !imetric.startsWith("sp") && imetric!=="tick"){
      ix.fillStyle=s.color; ix.globalAlpha=.16;
      ix.beginPath(); ix.moveTo(X(0),Y(0));
      s.vals.forEach((v,j)=>ix.lineTo(X(j),Y(v)));
      ix.lineTo(X(n-1),Y(0)); ix.closePath(); ix.fill(); ix.globalAlpha=1;
    }
    ix.strokeStyle=s.color; ix.lineWidth=2; ix.beginPath();
    s.vals.forEach((v,j)=> j?ix.lineTo(X(j),Y(v)):ix.moveTo(X(j),Y(v)));
    ix.stroke();
  });

  if(imetric.startsWith("sp")){
    const m=IN.milestones[imetric==="sp12"?"V1-V2":imetric==="sp34"?"V3A-V3B":"V3A-V1"];
    [[m.first_positive,"#38bdf8","first >0"],[m.persists_from,"#34d399","persists"],
     [m.peak_bar,"#fbbf24","peak"],[m.trough_bar,"#ef4444","trough"]].forEach(([b,c,lab])=>{
      if(b==null) return;
      const j=xs.indexOf(b); if(j<0) return;
      ix.setLineDash([3,3]); ix.strokeStyle=c; ix.lineWidth=1.2;
      ix.beginPath(); ix.moveTo(X(j),T); ix.lineTo(X(j),T+ph); ix.stroke(); ix.setLineDash([]);
      ix.fillStyle=c; ix.font="9.5px sans-serif"; ix.textAlign="left";
      ix.fillText(lab, X(j)+4, T+12);
    });
  }
  ig={L,T,pw,ph,n,X,Y,xs,seriesList};
}

ic.addEventListener("mousemove",e=>{
  if(!ig) return;
  const r=ic.getBoundingClientRect(), mx=e.clientX-r.left, my=e.clientY-r.top;
  const {L,T,pw,ph,n,X,Y,xs,seriesList}=ig;
  if(mx<L-10||mx>L+pw+10||my<T-10||my>T+ph+10){ tip3.style.opacity=0; return; }
  const j=Math.max(0,Math.min(n-1,Math.round((mx-L)/(pw/(n-1)))));
  tip3.innerHTML = `<b>${IN.labels[xs[j]]} MST</b><br>` + seriesList.map(s=>
    `<span style="color:${s.color}">■</span> ${s.name}: ${usd(s.vals[j])}`).join("<br>");
  tip3.style.opacity=1;
  const tw=tip3.offsetWidth;
  tip3.style.left=Math.min(Math.max(X(j)+14,4),r.width-tw-4)+"px";
  tip3.style.top=Math.max(my-10,4)+"px";
});
ic.addEventListener("mouseleave",()=>tip3.style.opacity=0);

(function(){
  const el=document.getElementById("milestones");
  const rows=[["V1 − V2","V1-V2"],["V3A − V3B","V3A-V3B"],["V3A − V1","V3A-V1"],["V3B − V2","V3B-V2"]];
  el.innerHTML = rows.map(([lab,key])=>{
    const m=IN.milestones[key];
    const f=m.first_positive!=null?IN.labels[m.first_positive]:"—";
    const p=m.persists_from!=null?IN.labels[m.persists_from]:"—";
    const pk=m.peak_bar!=null?IN.labels[m.peak_bar]:"—";
    return `<div class="stat">
      <div class="k">${lab}</div>
      <div class="v ${m.terminal>=0?'pos':'neg'}">${usd(m.terminal)}</div>
      <div class="k" style="margin-top:8px">first &gt; 0</div><div style="font-size:13px">${f} MST</div>
      <div class="k" style="margin-top:6px">persists from</div><div style="font-size:13px">${p} MST</div>
      <div class="k" style="margin-top:6px">peak</div><div style="font-size:13px">${usd(m.peak)} @ ${pk}</div>
    </div>`;
  }).join("");
})();

let rt; window.addEventListener("resize", ()=>{ clearTimeout(rt); rt=setTimeout(()=>{draw();drawBars();drawI();},120); });
draw(); drawBars(); drawI();
</script>
</body>
</html>
"""


def write_html(series, contrib, summary_json, iser=None):
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
        "intraday": {
            "bars": payload["intraday"]["bars"],
            "bars_per_session": payload["intraday"]["bars_per_session"],
            "labels": payload["intraday"]["labels"],
            "tickers": payload["divergence_tickers"],
            "series": {
                v: {
                    "total": [round(x, 2) for x in iser[v]["total"]],
                    "realized": [round(x, 2) for x in iser[v]["realized"]],
                    "unrealized": [round(x, 2) for x in iser[v]["unrealized"]],
                    "per_ticker": {s: [round(y, 2) for y in arr]
                                   for s, arr in d["per_ticker"].items()},
                }
                for v, d in payload["intraday"]["series"].items()
            },
            "spreads": {k: [round(x, 2) for x in arr]
                        for k, arr in payload["intraday"]["spreads"].items()},
            "milestones": payload["intraday"]["milestones"],
        },
    }
    html = (
        HTML_TEMPLATE
        .replace("__DATA__", json.dumps(slim, separators=(",", ":")))
        .replace("__NSESS__", str(len(SESSION_DATES)))
        .replace("__NSYMS__", str(len(PRICES)))
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
    yield_rows = apply_us10y_adjustment(series, SESSION_DATES)
    enrich(series)
    contrib = ticker_contributions(series)

    charts = make_charts(series, contrib)
    energy_chart = make_energy_eod_history_chart()
    yield_chart = make_us10y_adjustment_chart(series, yield_rows)

    events = parse_trades()
    iser = intraday_series(VARIANTS, events, DIVERGENCE)
    co = crossovers(iser)
    icharts = make_intraday_charts(iser, co)

    daily_csv = write_csv(series)
    intraday_csv = write_intraday_csv(iser, co)
    ticker_csv = write_ticker_csv(contrib)
    yield_csv = write_adjustment_csv(
        yield_rows, series, DATA_DIR / "model_performance_us10y_adjustment.csv"
    )
    summary_json = write_json(series, contrib, iser, co, yield_rows)
    md = write_markdown(series, contrib, charts, daily_csv, ticker_csv, summary_json,
                        iser, co, icharts, intraday_csv, yield_chart, yield_csv)
    html = write_html(series, contrib, summary_json, iser)
    # Keep the one-minute INTC source series as audit data only. The active replay
    # uses the chart-posting price recorded in trades/INTC.txt, not a later Yahoo
    # minute close, so do not generate or inject that comparison chart/card here.

    print("Wrote:")
    for p in charts + [energy_chart, yield_chart] + icharts:
        print(f"  {p.relative_to(ROOT)}")
    for p in (daily_csv, intraday_csv, yield_csv,
              ticker_csv, summary_json, md, html):
        print(f"  {p.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
