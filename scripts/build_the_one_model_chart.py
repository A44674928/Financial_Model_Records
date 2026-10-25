#!/usr/bin/env python3
"""Draw THE ONE MODEL split-portfolio architecture and aggregate KPI chart."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / "data" / "the_one_model_split_portfolios_v1_summary.json"
OUT = ROOT / "Charts" / "superstructure" / "the-one-model.png"

BG = "#0b1220"
PANEL = "#111c2e"
PANEL_BLUE = "#10273a"
PANEL_TEAL = "#102b31"
PANEL_AMBER = "#2b2117"
BLUE = "#38bdf8"
TEAL = "#2dd4bf"
AMBER = "#fbbf24"
FG = "#f8fafc"
MUTED = "#a8b6ca"


def add_box(ax, x, y, w, h, title, body, edge, face,
            title_size=10, body_size=8.4, body_y_offset=0.53):
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.025,rounding_size=0.12",
        linewidth=1.5, edgecolor=edge, facecolor=face,
    ))
    ax.text(x + w / 2, y + h - 0.17, title, ha="center", va="top",
            fontsize=title_size, color=edge, fontweight="bold", linespacing=1.05)
    ax.text(x + w / 2, y + h - body_y_offset, body, ha="center", va="top",
            fontsize=body_size, color=FG, linespacing=1.25, wrap=True)


def arrow(ax, start, end, color=MUTED, lw=1.8):
    ax.add_patch(FancyArrowPatch(
        start, end, arrowstyle="-|>", mutation_scale=13, linewidth=lw,
        color=color, connectionstyle="arc3,rad=0",
    ))


def money(value):
    return f"${float(value):,.2f}"


def main():
    with SUMMARY.open(encoding="utf-8") as handle:
        summary = json.load(handle)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig = plt.figure(figsize=(16, 10), facecolor=BG)
    ax = fig.add_axes([0.025, 0.025, 0.95, 0.95])
    ax.set_facecolor(BG)
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 10)
    ax.axis("off")

    ax.text(8, 9.62, "THE ONE MODEL", ha="center", va="center",
            color=FG, fontsize=27, fontweight="bold")
    ax.text(8, 9.20,
            "SPLIT-PORTFOLIO STRATEGY · 32 INDEPENDENT MODEL PORTFOLIOS · HISTORICAL MODELED RESULTS",
            ha="center", va="center", color=MUTED, fontsize=10, fontweight="bold")
    ax.text(8, 8.80,
            "SEP 3–OCT 23, 2026 · 36 SESSIONS · HYPOTHETICAL PAPER-TRADE OUTPUT",
            ha="center", va="center", color=AMBER, fontsize=9.4, fontweight="bold",
            bbox={"boxstyle": "round,pad=0.40", "facecolor": PANEL_AMBER,
                  "edgecolor": AMBER, "linewidth": 1.1})

    kpis = [
        ("AGGREGATE TERMINAL PnL", money(summary["aggregate_terminal_pnl_usd"]), TEAL),
        ("DEPLOYED-NOTIONAL RATIO", f"{float(summary['aggregate_deployed_notional_ratio_pct']):.4f}%", BLUE),
        ("GROSS NOTIONAL ADDED", f"${float(summary['aggregate_cumulative_gross_notional_added_usd']) / 1e6:.2f}M", AMBER),
        ("GROSS OPEN NOTIONAL", f"${float(summary['aggregate_gross_open_notional_usd']) / 1e6:.2f}M", BLUE),
    ]
    kpi_x = [0.55, 4.35, 8.15, 11.95]
    for x, (label, value, color) in zip(kpi_x, kpis):
        ax.add_patch(FancyBboxPatch(
            (x, 7.62), 3.5, 0.86,
            boxstyle="round,pad=0.025,rounding_size=0.11",
            linewidth=1.2, edgecolor=color, facecolor=PANEL,
        ))
        ax.text(x + 1.75, 8.27, label, ha="center", va="center",
                fontsize=8.1, color=MUTED, fontweight="bold")
        ax.text(x + 1.75, 7.91, value, ha="center", va="center",
                fontsize=14 if len(value) < 15 else 12, color=color, fontweight="bold")

    ax.text(0.45, 7.16, "PORTFOLIO CONSTRUCTION — CROSS EVERY CORE VARIANT WITH EVERY 1U/EOD VARIANT",
            color=BLUE, fontsize=9.6, fontweight="bold", va="center")
    top_y, top_h, top_w = 4.95, 1.75, 2.72
    top_x = [0.45, 3.57, 6.69, 9.81, 12.93]
    boxes = [
        ("4 CORE VARIANTS",
         "V1 · V2 · V3A · V3B\n\nFour distinct Core model rule sets"),
        ("× 4 VARIANT-SPECIFIC 1U/EOD",
         "V1 · V2 · V3A · V3B\n\nFour separate 1U/EOD model paths"),
        ("16 CROSS-VARIANT PAIRS",
         "Every Core × 1U/EOD pairing\n\nIncludes matching and cross-variant pairs"),
        ("2 ENERGY SIDECAR STATES PER PAIR",
         "One portfolio without the sidecar\nOne separate portfolio with the\n11U/DAY energy schedule per active ticker"),
        ("32 SEPARATE PORTFOLIOS",
         "16 pairings × 2 energy-sidecar states\n\nEach also adds 10U/DAY DXY to core's\nintegrated 1U/DAY schedule (11U total)"),
    ]
    for i, (x, (title, body)) in enumerate(zip(top_x, boxes)):
        add_box(ax, x, top_y, top_w, top_h, title, body,
                AMBER if i == 3 else (TEAL if i == 4 else BLUE),
                PANEL_AMBER if i == 3 else (PANEL_TEAL if i == 4 else PANEL_BLUE),
                title_size=8.7 if i in (1, 2) else 9.6, body_size=8.25)
        if i < len(boxes) - 1:
            arrow(ax, (x + top_w + 0.06, top_y + top_h / 2),
                  (top_x[i + 1] - 0.06, top_y + top_h / 2),
                  color=AMBER if i == 3 else BLUE)

    ax.text(0.45, 4.42, "SPLIT ACCOUNTING → AGGREGATE REPORTING",
            color=TEAL, fontsize=9.8, fontweight="bold", va="center")
    add_box(
        ax, 0.62, 2.35, 6.95, 1.68,
        "32 INDEPENDENT LEDGERS",
        "Track each portfolio’s PnL, gross notional added, open notional, and drawdown separately.\n"
        "No positions, capital, or risk are netted. The energy sidecar is included once in each\n"
        "of the 16 separately funded energy-inclusive portfolios.",
        BLUE, PANEL_BLUE, title_size=10, body_size=8.5, body_y_offset=0.53,
    )
    add_box(
        ax, 8.43, 2.35, 6.95, 1.68,
        "SUM THE 32 PORTFOLIOS",
        "Display total modeled PnL, total gross additions and open exposure,\n"
        "aggregate PnL ÷ gross notional added, and peak-to-trough PnL drawdown.\n"
        "Full terminal statistics for all 32 portfolios are in the linked table and audit export.",
        TEAL, PANEL_TEAL, title_size=10, body_size=8.5, body_y_offset=0.53,
    )
    arrow(ax, (8, 4.78), (4.1, 4.10), color=MUTED, lw=1.3)
    arrow(ax, (8, 4.78), (11.9, 4.10), color=MUTED, lw=1.3)

    drawdown = summary["aggregate_max_peak_to_trough_pnl_drawdown_usd"]
    peak_date = summary["aggregate_max_drawdown_peak_date"]
    trough_date = summary["aggregate_max_drawdown_trough_date"]
    ax.text(8, 1.76,
            f"MAX AGGREGATE PnL DRAWDOWN: {money(drawdown)} · {peak_date} → {trough_date}   |   "
            f"{summary['profitable_portfolios_at_terminal']}/32 portfolios positive at period end",
            ha="center", va="center", color=AMBER, fontsize=9.6, fontweight="bold")
    ax.text(8, 1.30,
            "The percentage is a deployed-notional ratio, not an account return. Aggregate totals assume distinct funding for all 32 portfolios.",
            ha="center", va="center", color=FG, fontsize=8.8)
    ax.text(8, 0.91,
            "Every portfolio includes core 1U/DAY plus 10U/DAY DXY (11U total); 0.05U, numeraire, yield/CPI, and options are excluded.",
            ha="center", va="center", color=MUTED, fontsize=8.4)
    ax.text(8, 0.53,
            "Hypothetical model output—not brokerage executions or a verified account track record. Trading costs and execution are not fully modeled.",
            ha="center", va="center", color=MUTED, fontsize=8.0)

    fig.savefig(OUT, dpi=180, facecolor=BG, bbox_inches="tight")
    plt.close(fig)
    print(OUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
