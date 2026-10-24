"""Legacy audit utility for the one-minute INTC entry-window comparison.

The active model uses the chart-posting price recorded in the trade log. This
module is not called by the current report builder; its minute series is retained
for audit context and must not be treated as a replacement fill or slippage proof.
"""

import csv
from datetime import datetime, timezone
from pathlib import Path

from minute_session_data import (
    BAR_SECONDS, CLOSES_1M, LOGGED_ENTRY_PRICE, SESSION_DATE, START_EPOCH,
    SYMBOL, WINDOW_START,
)
from intraday_core import bar_index, build_intraday
from model_perf_core import (
    CHARTS_DIR, DATA_DIR, MST, UNIT, VARIANT_COLOR, VARIANT_LABEL, VARIANTS,
    parse_trades,
)

ROOT = Path(__file__).resolve().parent.parent


def minute_series():
    """Return per-model INTC cumulative PnL over the 10:00–11:00 window."""
    if len(CLOSES_1M) != 60:
        raise ValueError(f"Expected 60 minute closes, got {len(CLOSES_1M)}")
    events = parse_trades()
    session_bar = bar_index(SESSION_DATE, WINDOW_START)  # logged 10:00 MST
    rows = []
    results = {v: [] for v in VARIANTS}
    timestamp = START_EPOCH
    active = {}
    for v in VARIANTS:
        lots, realized = build_intraday(v, events, [SYMBOL])
        realized_to_window = sum(
            r["pnl"] for r in realized
            if r["sym"] == SYMBOL and r["bar"] <= session_bar
        )
        active[v] = (
            realized_to_window,
            [lot for lot in lots
             if lot["sym"] == SYMBOL
             and lot["entry_bar"] <= session_bar
             and (lot["close_bar"] is None or lot["close_bar"] > session_bar)],
        )
    for price in CLOSES_1M:
        dt = datetime.fromtimestamp(timestamp + BAR_SECONDS, timezone.utc).astimezone(MST)
        row = {
            "minute_close_epoch": timestamp + BAR_SECONDS,
            "time_mst": dt.strftime("%H:%M"),
            "symbol": SYMBOL,
            "close_usd": price,
        }
        for v in VARIANTS:
            realized_to_window, open_at_minute = active[v]
            unrealized = sum(
                (1.0 if lot["side"] == "long" else -1.0)
                * lot["qty"] * UNIT * (price / lot["entry_px"] - 1.0)
                for lot in open_at_minute
            )
            results[v].append(realized_to_window + unrealized)
            row[v + "_intc_pnl_usd"] = results[v][-1]
        rows.append(row)
        timestamp += BAR_SECONDS
    return rows, results


def write_minute_closeup():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.ticker import FuncFormatter

    CHARTS_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    rows, results = minute_series()
    path = DATA_DIR / "model_performance_minute_intc.csv"
    fields = ["minute_close_epoch", "time_mst", "symbol", "close_usd"] + [
        v + "_intc_pnl_usd" for v in VARIANTS
    ]
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

    bg, panel, grid, fg, muted = "#0d131e", "#141c2b", "#243044", "#f1f5f9", "#93a4bd"
    fig, (price_ax, pnl_ax) = plt.subplots(
        2, 1, figsize=(13.2, 8.2), sharex=True,
        gridspec_kw={"height_ratios": [1, 1.65], "hspace": 0.13},
    )
    fig.patch.set_facecolor(bg)
    x = list(range(60))
    close = [r["close_usd"] for r in rows]

    price_ax.set_facecolor(panel)
    price_ax.plot(x, close, color="#fbbf24", lw=1.75, label="Yahoo 1m close")
    price_ax.scatter([0], [close[0]], s=26, color="#fbbf24", zorder=5)
    price_ax.annotate(
        f"first minute close ${close[0]:.2f}\n"
        f"logged entry ref ~${LOGGED_ENTRY_PRICE:.2f} (off-scale)",
        xy=(0, close[0]), xytext=(26, 12), textcoords="offset points",
        color=fg, fontsize=9,
        arrowprops={"arrowstyle": "->", "color": muted, "lw": 0.8},
    )
    price_ax.set_ylim(min(close) - 0.18, max(close) + 0.35)
    price_ax.set_ylabel("INTC price (USD)", color=muted)
    price_ax.set_title(
        "INTC — Sep 24, 2026 · hazard-flip window · 1-minute closes (MST)",
        color=fg, fontsize=14, fontweight="bold", loc="left", pad=12,
    )
    price_ax.grid(True, color=grid, linewidth=0.7, alpha=0.8)
    price_ax.tick_params(colors=muted, labelsize=8)
    for spine in price_ax.spines.values():
        spine.set_color(grid)

    pnl_ax.set_facecolor(panel)
    for v in VARIANTS:
        pnl_ax.plot(x, results[v], color=VARIANT_COLOR[v], lw=2.0,
                    label=VARIANT_LABEL[v])
    pnl_ax.axvline(0, color="#38bdf8", ls=":", lw=1.5, alpha=0.9)
    pnl_ax.axhline(0, color=muted, ls="--", lw=0.8, alpha=0.65)
    pnl_ax.text(0.012, 0.97, "SHORT logged at 10:00 · ~$115.11 · 1 unit",
                transform=pnl_ax.transAxes, va="top", color="#38bdf8",
                fontsize=9, fontweight="bold")
    pnl_ax.set_ylabel("INTC cumulative PnL (USD)", color=muted)
    pnl_ax.set_xlabel("Minute-bar close time · MST", color=muted)
    pnl_ax.grid(True, color=grid, linewidth=0.7, alpha=0.8)
    pnl_ax.tick_params(colors=muted, labelsize=8)
    for spine in pnl_ax.spines.values():
        spine.set_color(grid)
    pnl_ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: f"${y:,.0f}"))
    ticks = list(range(0, 60, 5))
    pnl_ax.set_xticks(ticks)
    pnl_ax.set_xticklabels([rows[i]["time_mst"] for i in ticks], rotation=0)
    pnl_ax.legend(loc="lower right", ncol=2, frameon=True,
                  facecolor=panel, edgecolor=grid, labelcolor=fg, fontsize=8)

    gap = close[0] - LOGGED_ENTRY_PRICE
    pct_gap = 100 * gap / LOGGED_ENTRY_PRICE
    fig.text(0.095, 0.015,
             f"First retained Yahoo minute close: ${close[0]:.2f} vs logged entry reference ~${LOGGED_ENTRY_PRICE:.2f} "
             f"(+${gap:.2f} / {pct_gap:.1f}%). Log date is approximate from chart axis; this is not verified slippage. "
             "Model PnL uses the recorded entry reference.",
             color=muted, fontsize=8.5)
    fig.subplots_adjust(left=0.09, right=0.98, top=0.92, bottom=0.11)
    image = CHARTS_DIR / "13-minute-intc-hazard-flip.png"
    fig.savefig(image, dpi=160, facecolor=bg, bbox_inches="tight")
    plt.close(fig)
    return image, path, rows, results


def inject_minute_section(md_path, html_path, image_path, csv_path, rows, results):
    """Add a compact, idempotent section/card after the generator writes its files."""
    first = rows[0]["close_usd"]
    gap = first - LOGGED_ENTRY_PRICE
    pct_gap = 100 * gap / LOGGED_ENTRY_PRICE
    out = (
        "## 1-Minute Close-Up — INTC Hazard-Flip Window\n\n"
        f"A focused **60-bar, one-minute** view around the logged Sep 24 `10:00 MST` INTC short "
        "(the trade-log note says the date is approximate from the chart axis). This is a zoom into one high-signal hour, not a replacement for the 35-session "
        "hourly sub-book. The lower panel carries INTC-only cumulative realized + open PnL "
        "for each model; V1/V2 and V3A/V3B overlap here because their SAR paths have not "
        "yet diverged on this date.\n\n"
        f"![INTC one-minute hazard-flip close-up]({image_path.relative_to(ROOT).as_posix()})\n\n"
        f"**Timing/source caveat:** the trade-log note says the event date is approximate from the chart axis; "
        "this is a diagnostic comparison at the logged `10:00 MST` reference, not a verified execution or slippage measurement. "
        f"The first retained Yahoo one-minute close is **${first:.2f}** at `10:01 MST`, versus the logged entry reference "
        f"**~${LOGGED_ENTRY_PRICE:.2f}** (a **${gap:.2f} / {pct_gap:.1f}%** difference). The replay's PnL still uses "
        "the recorded entry price; it does not silently reprice or correct the trade. "
        f"Minute series: [`{csv_path.name}`](data/{csv_path.name}) (60 rows).\n\n"
    )
    md = md_path.read_text(encoding="utf-8")
    marker = "## 1-Minute Close-Up — INTC Hazard-Flip Window"
    if marker in md:
        original = md_path.read_text(encoding="utf-8")
        method = "## Method & Caveats"
        tail = method + original.split(method, 1)[1]
        md = original.split(marker, 1)[0] + out + tail
    else:
        method = "## Method & Caveats"
        md = md.replace(method, out + method, 1)
    md_path.write_text(md, encoding="utf-8")

    html = html_path.read_text(encoding="utf-8")
    card_marker = "  <div class=\"card\">\n    <h2>Full session table</h2>"
    card_id = "  <div class=\"card\" id=\"minute-closeup\">"
    card = (
        card_id + "\n"
        "    <h2>1-minute close-up — INTC hazard-flip window</h2>\n"
        "    <p class=\"hint\">Sep 24, 2026 · 10:00–11:00 MST · 60 one-minute bars. "
        f"First retained Yahoo close ${first:.2f} at 10:01 vs logged entry reference ~${LOGGED_ENTRY_PRICE:.2f} "
        f"(+${gap:.2f}, {pct_gap:.1f}%). The trade-log note says the event date is approximate from the chart axis; "
        "treat this as a diagnostic discrepancy, not verified slippage. PnL uses the recorded entry reference.</p>\n"
        f"    <a href=\"{image_path.relative_to(ROOT).as_posix()}\"><img "
        f"src=\"{image_path.relative_to(ROOT).as_posix()}\" alt=\"INTC one-minute close-up\" "
        "style=\"width:100%;height:auto;border-radius:8px\"></a>\n"
        f"    <p class=\"hint\"><a href=\"{csv_path.relative_to(ROOT).as_posix()}\">Download minute data (CSV)</a></p>\n"
        "  </div>\n\n"
    )
    if card_id in html:
        start = html.index(card_id)
        end = html.index("  </div>", start) + len("  </div>\n\n")
        html = html[:start] + html[end:]
    html = html.replace(card_marker, card + card_marker, 1)
    html_path.write_text(html, encoding="utf-8")
