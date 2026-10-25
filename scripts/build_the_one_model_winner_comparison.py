#!/usr/bin/env python3
"""Compare THE ONE MODEL with its top terminal-PnL constituent at equal gross additions.

The winning portfolio is selected ex post from the 32 THE ONE MODEL portfolios
by highest terminal modeled PnL. Its entire position path is then multiplied by
a constant so terminal cumulative gross notional additions match THE ONE MODEL
aggregate. This is a linear arithmetic comparison, not an execution simulation.
"""
import csv
import json
from datetime import datetime
from decimal import Decimal
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

ROOT = Path(__file__).resolve().parents[1]
INPUT_CSV = ROOT / "data" / "the_one_model_split_portfolios_v1.csv"
INPUT_SUMMARY = ROOT / "data" / "the_one_model_split_portfolios_v1_summary.json"
OUTPUT_CSV = ROOT / "data" / "the_one_model_vs_winning_model_v1.csv"
OUTPUT_JSON = ROOT / "data" / "the_one_model_vs_winning_model_v1_summary.json"
OUTPUT_CHART = ROOT / "Charts" / "superstructure" / "the-one-model-vs-winning-model.png"
REPORT = ROOT / "THE ONE MODEL vs THE WINNING MODEL.md"
CENT = Decimal("0.01")


def dec(value):
    return Decimal(str(value))


def dollars(value):
    return f"${dec(value):,.2f}"


def ratio_pct(pnl, added):
    return pnl / added * Decimal("100") if added else Decimal("0")


def _max_drawdown(values, dates):
    peak = Decimal("0")
    peak_date = "before period"
    max_dd = Decimal("0")
    record = {"amount": Decimal("0"), "peak_date": peak_date,
              "peak_pnl": peak, "trough_date": dates[0], "trough_pnl": Decimal("0")}
    for pnl, day in zip(values, dates):
        if pnl > peak:
            peak, peak_date = pnl, day
        drawdown = peak - pnl
        if drawdown > max_dd:
            max_dd = drawdown
            record = {"amount": drawdown, "peak_date": peak_date,
                      "peak_pnl": peak, "trough_date": day, "trough_pnl": pnl}
    return record


def build_comparison():
    summary = json.loads(INPUT_SUMMARY.read_text(encoding="utf-8"))
    with INPUT_CSV.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError(f"No daily rows in {INPUT_CSV}")
    winner = summary["best_terminal_pnl_portfolio"]
    portfolio_id = winner["portfolio_id"]
    if len(rows) != summary["sessions"]:
        raise ValueError("Daily input row count does not match THE ONE MODEL summary")

    winner_pnl_key = f"{portfolio_id}__pnl_usd"
    winner_added_key = f"{portfolio_id}__cumulative_notional_added_usd"
    winner_open_key = f"{portfolio_id}__open_notional_usd"
    aggregate_added = dec(rows[-1]["aggregate_cumulative_notional_added_usd"])
    winner_added = dec(rows[-1][winner_added_key])
    if winner_added <= 0 or aggregate_added <= 0:
        raise ValueError("Cannot equalize gross notional when a terminal addition total is zero")
    scale = aggregate_added / winner_added

    output_rows = []
    dates = []
    one_pnl, scaled_pnl = [], []
    for source in rows:
        day = source["date"]
        dates.append(day)
        base_winner_pnl = dec(source[winner_pnl_key])
        base_winner_added = dec(source[winner_added_key])
        base_winner_open = dec(source[winner_open_key])
        equal_pnl = (base_winner_pnl * scale).quantize(CENT)
        equal_added = (base_winner_added * scale).quantize(CENT)
        equal_open = (base_winner_open * scale).quantize(CENT)
        one = dec(source["aggregate_pnl_usd"])
        one_added = dec(source["aggregate_cumulative_notional_added_usd"])
        one_open = dec(source["aggregate_open_notional_usd"])
        output_rows.append({
            "date": day,
            "the_one_model_aggregate_pnl_usd": f"{one:.2f}",
            "the_one_model_cumulative_gross_notional_added_usd": f"{one_added:.2f}",
            "the_one_model_gross_open_notional_usd": f"{one_open:.2f}",
            "the_one_model_pnl_to_gross_added_pct": f"{ratio_pct(one, one_added):.6f}",
            "winning_model_original_pnl_usd": f"{base_winner_pnl:.2f}",
            "winning_model_original_cumulative_gross_notional_added_usd": f"{base_winner_added:.2f}",
            "winning_model_original_gross_open_notional_usd": f"{base_winner_open:.2f}",
            "winning_model_original_pnl_to_gross_added_pct": f"{ratio_pct(base_winner_pnl, base_winner_added):.6f}",
            "winning_model_equal_gross_pnl_usd": f"{equal_pnl:.2f}",
            "winning_model_equal_gross_cumulative_notional_added_usd": f"{equal_added:.2f}",
            "winning_model_equal_gross_open_notional_usd": f"{equal_open:.2f}",
            "winning_model_equal_gross_pnl_to_gross_added_pct": f"{ratio_pct(equal_pnl, equal_added):.6f}",
        })
        one_pnl.append(one)
        scaled_pnl.append(equal_pnl)

    last = output_rows[-1]
    winner_original_dd = _max_drawdown(
        [dec(row[winner_pnl_key]) for row in rows], dates
    )
    winner_scaled_dd = _max_drawdown(scaled_pnl, dates)
    one_dd = _max_drawdown(one_pnl, dates)
    equal_pnl = dec(last["winning_model_equal_gross_pnl_usd"])
    one_pnl_terminal = dec(last["the_one_model_aggregate_pnl_usd"])
    one_ratio = dec(last["the_one_model_pnl_to_gross_added_pct"])
    equal_ratio = dec(last["winning_model_equal_gross_pnl_to_gross_added_pct"])
    details = next(item for item in summary["individual_portfolios"]
                   if item["portfolio_id"] == portfolio_id)
    result = {
        "label": "THE ONE MODEL vs THE WINNING MODEL — equal terminal gross additions",
        "period_start": dates[0],
        "period_end": dates[-1],
        "sessions": len(rows),
        "winner_selection_method": "Highest terminal modeled PnL among the 32 THE ONE MODEL constituent portfolios, selected using the full comparison period (ex post).",
        "winning_portfolio_id": portfolio_id,
        "winning_core_variant": details["core_variant"],
        "winning_variant_specific_1u_eod_variant": details["variant_specific_1u_eod_variant"],
        "winning_energy_sidecar_included": details["oil_sidecar_included"],
        "winning_energy_sidecar_unit_size_u_per_active_ticker": details["energy_sidecar_unit_size_u_per_active_ticker"],
        "winning_dxy_exposure_per_active_eod_before_scaling": "11U/DAY",
        "the_one_model_terminal_pnl_usd": last["the_one_model_aggregate_pnl_usd"],
        "the_one_model_cumulative_gross_notional_added_usd": last["the_one_model_cumulative_gross_notional_added_usd"],
        "the_one_model_gross_open_notional_usd": last["the_one_model_gross_open_notional_usd"],
        "the_one_model_pnl_to_gross_added_pct": last["the_one_model_pnl_to_gross_added_pct"],
        "the_one_model_max_peak_to_trough_pnl_drawdown_usd": f"{one_dd['amount']:.2f}",
        "winning_model_original_terminal_pnl_usd": last["winning_model_original_pnl_usd"],
        "winning_model_original_cumulative_gross_notional_added_usd": last["winning_model_original_cumulative_gross_notional_added_usd"],
        "winning_model_original_gross_open_notional_usd": last["winning_model_original_gross_open_notional_usd"],
        "winning_model_original_pnl_to_gross_added_pct": last["winning_model_original_pnl_to_gross_added_pct"],
        "winning_model_original_max_peak_to_trough_pnl_drawdown_usd": f"{winner_original_dd['amount']:.2f}",
        "equal_gross_scale_factor": f"{scale:.12f}",
        "equal_gross_scale_factor_exact": str(scale),
        "equal_gross_winner_combined_dxy_units_per_active_eod": f"{Decimal('11') * scale:.6f}",
        "winning_model_equal_gross_terminal_pnl_usd": f"{equal_pnl:.2f}",
        "winning_model_equal_gross_cumulative_gross_notional_added_usd": last["winning_model_equal_gross_cumulative_notional_added_usd"],
        "winning_model_equal_gross_gross_open_notional_usd": last["winning_model_equal_gross_open_notional_usd"],
        "winning_model_equal_gross_pnl_to_gross_added_pct": last["winning_model_equal_gross_pnl_to_gross_added_pct"],
        "winning_model_equal_gross_max_peak_to_trough_pnl_drawdown_usd": f"{winner_scaled_dd['amount']:.2f}",
        "equal_gross_terminal_pnl_difference_winner_minus_one_model_usd": f"{equal_pnl - one_pnl_terminal:.2f}",
        "equal_gross_deployed_notional_ratio_difference_percentage_points": f"{equal_ratio - one_ratio:.6f}",
        "equal_gross_winner_selection_caveat": "The winning constituent is selected from the same full historical period being evaluated. This ex-post selection introduces look-ahead/selection bias and is not out-of-sample validation.",
        "scaling_caveat": "The equal-gross winning-model curve multiplies every daily PnL, cumulative addition, and open-notional amount by one constant. It is a mathematical normalization, not evidence that scaled positions could be executed at the same prices or costs. Margin, capacity, impact, financing, and correlated concentration are not modeled.",
        "caveat": "Historical hypothetical paper-model outputs, not actual brokerage execution or a verified account return. Deployed-notional ratios are not account returns; costs and execution are not fully modeled.",
        "one_model_max_drawdown": {
            "peak_date": one_dd["peak_date"], "peak_pnl_usd": f"{one_dd['peak_pnl']:.2f}",
            "trough_date": one_dd["trough_date"], "trough_pnl_usd": f"{one_dd['trough_pnl']:.2f}",
        },
        "winning_model_equal_gross_max_drawdown": {
            "peak_date": winner_scaled_dd["peak_date"], "peak_pnl_usd": f"{winner_scaled_dd['peak_pnl']:.2f}",
            "trough_date": winner_scaled_dd["trough_date"], "trough_pnl_usd": f"{winner_scaled_dd['trough_pnl']:.2f}",
        },
        "winning_model_original_max_drawdown": {
            "peak_date": winner_original_dd["peak_date"], "peak_pnl_usd": f"{winner_original_dd['peak_pnl']:.2f}",
            "trough_date": winner_original_dd["trough_date"], "trough_pnl_usd": f"{winner_original_dd['trough_pnl']:.2f}",
        },
    }
    return result, output_rows


def write_outputs(result, rows):
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0])
    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    OUTPUT_JSON.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")


def write_chart(result, rows):
    OUTPUT_CHART.parent.mkdir(parents=True, exist_ok=True)
    dates = [datetime.strptime(row["date"], "%Y-%m-%d") for row in rows]
    one_pnl = [float(row["the_one_model_aggregate_pnl_usd"]) for row in rows]
    scaled_pnl = [float(row["winning_model_equal_gross_pnl_usd"]) for row in rows]
    one_added = [float(row["the_one_model_cumulative_gross_notional_added_usd"]) for row in rows]
    scaled_added = [float(row["winning_model_equal_gross_cumulative_notional_added_usd"]) for row in rows]
    one_open = [float(row["the_one_model_gross_open_notional_usd"]) for row in rows]
    scaled_open = [float(row["winning_model_equal_gross_open_notional_usd"]) for row in rows]
    one_ratio = [float(row["the_one_model_pnl_to_gross_added_pct"]) for row in rows]
    scaled_ratio = [float(row["winning_model_equal_gross_pnl_to_gross_added_pct"]) for row in rows]

    bg, panel, grid = "#0b1220", "#111c2e", "#273449"
    fg, muted, teal, violet, amber = "#f8fafc", "#a8b6ca", "#2dd4bf", "#c084fc", "#fbbf24"
    fig, axes = plt.subplots(3, 1, figsize=(13.5, 10), sharex=True,
                             gridspec_kw={"height_ratios": [1.25, 1, 0.8]})
    fig.patch.set_facecolor(bg)
    for ax in axes:
        ax.set_facecolor(panel)
        ax.grid(True, color=grid, linewidth=0.75, alpha=0.85)
        ax.set_axisbelow(True)
        ax.tick_params(colors=muted, labelsize=9)
        for spine in ax.spines.values():
            spine.set_color(grid)

    ax = axes[0]
    ax.plot(dates, one_pnl, color=teal, linewidth=2.2, label="THE ONE MODEL — 32-portfolio aggregate")
    ax.plot(dates, scaled_pnl, color=violet, linewidth=2.2, label="THE WINNING MODEL — equal-gross scaled")
    ax.axhline(0, color=muted, linewidth=0.9, linestyle="--")
    ax.set_ylabel("Modeled cumulative PnL (USD)", color=muted)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda value, _: f"${value / 1e6:.0f}M"))
    ax.legend(facecolor=panel, edgecolor=grid, labelcolor=fg, fontsize=8.2, loc="upper left")
    ax.set_title("THE ONE MODEL vs THE WINNING MODEL — equal terminal gross additions",
                 color=fg, fontsize=14, fontweight="bold", loc="left", pad=12)
    ax.annotate(f"One Model  {dollars(result['the_one_model_terminal_pnl_usd'])}",
                (dates[-1], one_pnl[-1]), xytext=(-8, -18), textcoords="offset points",
                color=teal, fontsize=8.5, ha="right", fontweight="bold")
    ax.annotate(f"Winner scaled  {dollars(result['winning_model_equal_gross_terminal_pnl_usd'])}",
                (dates[-1], scaled_pnl[-1]), xytext=(-8, 9), textcoords="offset points",
                color=violet, fontsize=8.5, ha="right", fontweight="bold")

    ax = axes[1]
    ax.plot(dates, one_added, color=teal, linewidth=2, label="THE ONE MODEL cumulative gross additions")
    ax.plot(dates, scaled_added, color=violet, linewidth=2, linestyle="--",
            label="Winning model scaled additions")
    ax.plot(dates, one_open, color=amber, linewidth=1.6, label="THE ONE MODEL gross open notional")
    ax.plot(dates, scaled_open, color=fg, linewidth=1.6, linestyle=":",
            label="Winning model scaled open notional")
    ax.set_ylabel("Gross notional (USD)", color=muted)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda value, _: f"${value / 1e6:.0f}M"))
    ax.legend(facecolor=panel, edgecolor=grid, labelcolor=fg, fontsize=7.5, loc="upper left", ncol=2)

    ax = axes[2]
    ax.plot(dates, one_ratio, color=teal, linewidth=2, label="THE ONE MODEL")
    ax.plot(dates, scaled_ratio, color=violet, linewidth=2, linestyle="--", label="Winning model scaled")
    ax.set_ylabel("PnL / gross additions (%)", color=muted)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{value:.1f}%"))
    ax.set_xlabel("Session (MST)", color=muted)
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    ax.legend(facecolor=panel, edgecolor=grid, labelcolor=fg, fontsize=8, loc="upper left")
    fig.autofmt_xdate(rotation=0, ha="center")
    fig.text(
        0.5, 0.012,
        f"{result['period_start']}–{result['period_end']} · equal terminal gross additions · winning portfolio selected ex post · "
        "single-winner path scaled linearly · hypothetical model only · costs/capacity/execution not fully modeled",
        color=muted, fontsize=7.7, ha="center",
    )
    fig.tight_layout(rect=(0.015, 0.045, 0.99, 0.985))
    fig.savefig(OUTPUT_CHART, dpi=170, facecolor=bg, bbox_inches="tight")
    plt.close(fig)


def write_report(result):
    factor = dec(result["equal_gross_scale_factor"])
    text = f'''# THE ONE MODEL vs THE WINNING MODEL

> **Historical hypothetical comparison · TradingView-only benchmark through {result['period_end']} · {result['sessions']} sessions.** This compares the 32-portfolio THE ONE MODEL aggregate with one constituent selected as THE WINNING MODEL: the portfolio with the highest terminal modeled PnL over this same period. Selection is ex post and subject to look-ahead/selection bias.

## Comparison basis

“THE WINNING MODEL” here means **{result['winning_core_variant']} Core + {result['winning_variant_specific_1u_eod_variant']} variant-specific 1U/EOD, with the {result['winning_energy_sidecar_unit_size_u_per_active_ticker']}U/DAY energy sidecar per active ticker**—portfolio `{result['winning_portfolio_id']}`. It includes core’s integrated 1U/DAY DXY sleeve plus the 10U/DAY DXY add-on (11U/DAY total), just as each of the 32 THE ONE MODEL portfolios does.

The equal-gross comparison scales every daily PnL, notional addition, and open-notional value of this one winning portfolio by **{factor:.6f}×**, so its period-end cumulative gross additions match THE ONE MODEL at **{dollars(result['the_one_model_cumulative_gross_notional_added_usd'])}**. This scales the winner’s unit sizes too: its combined DXY schedule becomes **{dec(result['equal_gross_winner_combined_dxy_units_per_active_eod']):.4f}U/DAY**, versus the original 11U/DAY. It is a proportional arithmetic scaling of all components, not an assertion that the larger orders could be executed at unchanged prices, spreads, capacity, financing, or risk. The original, unscaled 1× winner is shown alongside it for context; that original portfolio does not have the same total gross additions as the 32-portfolio aggregate.

## Terminal comparison

| Historical result through {result['period_end']} | THE ONE MODEL: 32 independent portfolios | Winning constituent: original 1× | Winning constituent: equal-gross scaled |
|---|---:|---:|---:|
| Terminal modeled PnL | {dollars(result['the_one_model_terminal_pnl_usd'])} | {dollars(result['winning_model_original_terminal_pnl_usd'])} | **{dollars(result['winning_model_equal_gross_terminal_pnl_usd'])}** |
| Cumulative gross notional added | {dollars(result['the_one_model_cumulative_gross_notional_added_usd'])} | {dollars(result['winning_model_original_cumulative_gross_notional_added_usd'])} | **{dollars(result['winning_model_equal_gross_cumulative_gross_notional_added_usd'])}** |
| Gross open notional at period end | {dollars(result['the_one_model_gross_open_notional_usd'])} | {dollars(result['winning_model_original_gross_open_notional_usd'])} | {dollars(result['winning_model_equal_gross_gross_open_notional_usd'])} |
| PnL ÷ cumulative gross additions | {dec(result['the_one_model_pnl_to_gross_added_pct']):.4f}% | {dec(result['winning_model_original_pnl_to_gross_added_pct']):.4f}% | **{dec(result['winning_model_equal_gross_pnl_to_gross_added_pct']):.4f}%** |
| Peak-to-trough modeled PnL drawdown | {dollars(result['the_one_model_max_peak_to_trough_pnl_drawdown_usd'])} | {dollars(result['winning_model_original_max_peak_to_trough_pnl_drawdown_usd'])} | {dollars(result['winning_model_equal_gross_max_peak_to_trough_pnl_drawdown_usd'])} |

At the equal-gross terminal additions, the scaled winning curve exceeds THE ONE MODEL's terminal modeled PnL by **{dollars(result['equal_gross_terminal_pnl_difference_winner_minus_one_model_usd'])}** and its deployed-notional ratio by **{dec(result['equal_gross_deployed_notional_ratio_difference_percentage_points']):.4f} percentage points** in this historical sample. The comparison does not establish future outperformance. The winning portfolio was chosen using the same period being compared; this creates survivorship/selection bias, and its advantage is not an independent or out-of-sample result.

![THE ONE MODEL and the equal-gross scaled winning constituent](Charts/superstructure/the-one-model-vs-winning-model.png)

## Files and interpretation

- Daily comparison series: [`the_one_model_vs_winning_model_v1.csv`](data/the_one_model_vs_winning_model_v1.csv).
- Machine-readable comparison metrics: [`the_one_model_vs_winning_model_v1_summary.json`](data/the_one_model_vs_winning_model_v1_summary.json).
- The equal-gross line is generated by multiplying the winning constituent's daily modeled series by the same constant. Ratios are mathematically invariant to this scaling (aside from cent rounding); dollar drawdowns and notionals scale up.
- The 32-way aggregate assumes independent funding/exposure for every constituent. The one-winner comparison is a single concentrated portfolio. No positions, capital, correlated risk, or margin are netted between the two approaches.
- These are hypothetical paper-model outputs, not brokerage executions or verified account returns. Trading costs, slippage, capacity, financing, margin, taxes, market impact, and operational constraints are not fully modeled. A deployed-notional ratio is **not an account return**.
'''
    REPORT.write_text(text, encoding="utf-8")


def main():
    result, rows = build_comparison()
    write_outputs(result, rows)
    write_chart(result, rows)
    write_report(result)
    print(f"Wrote {OUTPUT_CSV.relative_to(ROOT)}")
    print(f"Wrote {OUTPUT_JSON.relative_to(ROOT)}")
    print(f"Wrote {OUTPUT_CHART.relative_to(ROOT)}")
    print(f"Wrote {REPORT.relative_to(ROOT)}")
    print(f"Equal-gross scale: {result['equal_gross_scale_factor']}x")
    print(f"THE ONE MODEL PnL: {dollars(result['the_one_model_terminal_pnl_usd'])}")
    print(f"Equal-gross winner PnL: {dollars(result['winning_model_equal_gross_terminal_pnl_usd'])}")


if __name__ == "__main__":
    main()
