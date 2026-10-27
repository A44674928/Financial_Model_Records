#!/usr/bin/env python3
"""Build the separate realized-PnL share/unit accumulator companion to TWM_1M_MAX."""
import csv
import json
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_strategy_sidecar_comparison import variant_force_multiplier_daily_model  # noqa: E402
from model_perf_core import PRICES, SESSION_DATES, UNIT, all_series, parse_trades  # noqa: E402
from share_accumulator_core import ENERGY_TICKERS, run_share_accumulator  # noqa: E402

DATA = ROOT / "data"
SUMMARY_INPUT = DATA / "the_one_model_vs_winning_model_v1_summary.json"
BASE_DAILY_CSV = DATA / "the_one_model_vs_winning_model_v1.csv"
ENERGY_CSV = DATA / "tradingview_energy_sidecar_daily_20261026.csv"
DAILY_OUTPUT = DATA / "twm_1m_max_share_accumulator_daily_v1.csv"
TICKER_OUTPUT = DATA / "twm_1m_max_share_accumulator_ticker_summary_v1.csv"
SUMMARY_OUTPUT = DATA / "twm_1m_max_share_accumulator_v1_summary.json"
REPORT_OUTPUT = ROOT / "TWM_1M_MAX Realized-PnL Share Accumulator.md"
CHART_OUTPUT = ROOT / "Charts" / "superstructure" / "twm-1m-max-share-accumulator.png"
SHARE_COUNT_CHART_OUTPUT = ROOT / "Charts" / "superstructure" / "twm-1m-max-share-counts.png"


def _write_csv(path, rows):
    if not rows:
        raise ValueError(f"Refusing to write empty CSV: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _money(value):
    amount = float(value)
    if abs(amount) < 0.005:
        amount = 0.0
    return f"${amount:,.2f}"


def _write_chart(base_rows, tracker_rows):
    dates = [row["date"] for row in base_rows]
    baseline = [float(row["twm_1m_max_pnl_usd"]) for row in base_rows]
    tracker_by_date = defaultdict(float)
    for row in tracker_rows:
        tracker_by_date[row["date"]] += float(row["accumulator_net_pnl_usd"])
    overlay = [tracker_by_date[day] for day in dates]
    combined = [base + extra for base, extra in zip(baseline, overlay)]

    CHART_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(12, 6.5))
    ax.axhline(0, color="#64748b", linewidth=0.8)
    ax.plot(dates, baseline, color="#2563eb", linewidth=2.2, label="TWM_1M_MAX baseline PnL")
    ax.plot(dates, overlay, color="#16a34a", linewidth=2.0, label="Accumulator incremental PnL")
    ax.plot(dates, combined, color="#7c3aed", linewidth=1.8, linestyle="--",
            label="Baseline + accumulator incremental PnL")
    ax.set_title("TWM_1M_MAX — realized-PnL share accumulator companion")
    ax.set_ylabel("Modeled PnL (USD)")
    ax.set_xlabel("Session date")
    ax.grid(True, alpha=0.2)
    ax.legend(loc="best", frameon=False)
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(CHART_OUTPUT, dpi=160)
    plt.close(fig)


def _write_share_count_chart(daily_rows, ticker_rows, pending_realized_pnl, accounting_cost_basis):
    """Show actual held quantities over time, with independent ticker scales."""
    by_ticker = defaultdict(list)
    for row in daily_rows:
        by_ticker[row["ticker"]].append(row)
    equities = sorted(ticker for ticker in by_ticker if ticker not in ENERGY_TICKERS)
    energy = sorted(ticker for ticker in by_ticker if ticker in ENERGY_TICKERS)
    terminal_by_ticker = {row["ticker"]: row for row in ticker_rows}
    colors = plt.get_cmap("tab10").colors
    calendar_rows = sorted(daily_rows, key=lambda item: item["date"])
    calendar_dates = list(dict.fromkeys(row["date"] for row in calendar_rows))
    date_ticks = [datetime.strptime(calendar_dates[index], "%Y-%m-%d")
                  for index in sorted(set([0, 7, 14, 21, 28, len(calendar_dates) - 1]))]

    fig = plt.figure(figsize=(15, 13), facecolor="white")
    grid = fig.add_gridspec(
        4, 2, height_ratios=[1, 1, 1, 0.9],
        left=0.08, right=0.98, top=0.82, bottom=0.10, hspace=0.38, wspace=0.16,
    )
    first_ax = fig.add_subplot(grid[0, 0])
    axes = [first_ax]
    axes.extend(
        fig.add_subplot(grid[row, col], sharex=first_ax)
        for row in range(3) for col in range(2)
        if not (row == 0 and col == 0)
    )
    energy_ax = fig.add_subplot(grid[3, :], sharex=first_ax)
    fig.suptitle("TWM_1M_MAX accumulator — shares held, not PnL", y=0.975,
                 fontsize=18, fontweight="bold")
    fig.text(
        0.5, 0.935,
        "Fractional share counts by equity. Each ticker uses its own count scale; BRENT/OIL are separate model-U equivalents.",
        ha="center", va="top", fontsize=10, color="#475569",
    )
    fig.text(
        0.29, 0.885,
        f"PENDING REALIZED PNL — NEXT SUPPLIED MARK\n${pending_realized_pnl:,.2f} net  |  Oct. 27 if a mark is supplied\nTicker-level gains buy; losses sell or carry",
        ha="center", va="center", fontsize=10, color="#1e3a8a",
        bbox={"boxstyle": "round,pad=0.65", "facecolor": "#eff6ff", "edgecolor": "#bfdbfe"},
    )
    fig.text(
        0.73, 0.885,
        f"ADDITIONAL OUT-OF-POCKET CASH\n$0.00  |  accounting basis: ${accounting_cost_basis:,.2f}\nPurchases funded from realized PnL, not new cash",
        ha="center", va="center", fontsize=10, color="#166534",
        bbox={"boxstyle": "round,pad=0.65", "facecolor": "#f0fdf4", "edgecolor": "#bbf7d0"},
    )

    for index, ticker in enumerate(equities):
        ax = axes[index]
        rows = sorted(by_ticker[ticker], key=lambda item: item["date"])
        dates = [datetime.strptime(row["date"], "%Y-%m-%d") for row in rows]
        counts = [float(row["shares_or_model_units_held"]) for row in rows]
        held = float(terminal_by_ticker[ticker]["shares_or_model_units_held"])
        peak = max(counts, default=0.0)
        color = colors[index % len(colors)]
        ax.step(dates, counts, where="post", color=color, linewidth=2.4)
        ax.fill_between(dates, counts, step="post", color=color, alpha=0.12)
        ax.scatter([dates[-1]], [counts[-1]], s=24, color=color, zorder=3)
        ax.set_title(f"{ticker}  |  {held:,.4f} shares held", loc="left", fontsize=12, fontweight="bold")
        ax.set_ylabel("Shares")
        ax.grid(True, axis="y", alpha=0.22)
        ax.set_xlim(dates[0], dates[-1])
        ax.set_ylim(0, max(1.0, peak * 1.18) if peak == 0 else peak * 1.18)
        ax.set_xticks(date_ticks)
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
        ax.tick_params(axis="x", labelbottom=False)
        if peak == 0:
            ax.text(0.98, 0.78, "No shares currently held", transform=ax.transAxes,
                    ha="right", va="top", fontsize=9, color="#64748b")

    # Keep energy units out of the stock-share panels and use a distinct axis.
    for index, ticker in enumerate(energy):
        rows = sorted(by_ticker[ticker], key=lambda item: item["date"])
        dates = [datetime.strptime(row["date"], "%Y-%m-%d") for row in rows]
        counts = [float(row["shares_or_model_units_held"]) for row in rows]
        held = float(terminal_by_ticker[ticker]["shares_or_model_units_held"])
        energy_ax.step(dates, counts, where="post", linewidth=2.4,
                       color=colors[(len(equities) + index) % len(colors)],
                       label=f"{ticker}: {held:.6f} U held")
    energy_ax.set_title("BRENT / OIL  |  separate model-unit-equivalent holdings", loc="left",
                        fontsize=12, fontweight="bold")
    energy_ax.set_ylabel("Model-U equivalents")
    energy_ax.set_xlabel("Session date")
    energy_ax.grid(True, axis="y", alpha=0.22)
    energy_ax.legend(loc="upper left", frameon=False, ncol=max(1, len(energy)))
    energy_ax.set_xticks(date_ticks)
    energy_ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    energy_ax.tick_params(axis="x", labelbottom=True, labelrotation=25)
    energy_ax.margins(x=0.01, y=0.2)

    SHARE_COUNT_CHART_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(SHARE_COUNT_CHART_OUTPUT, dpi=180, bbox_inches="tight")
    plt.close(fig)


def build():
    base_summary = json.loads(SUMMARY_INPUT.read_text(encoding="utf-8"))
    scale = float(base_summary["twm_1m_max_scale_factor_exact"])
    with BASE_DAILY_CSV.open(newline="", encoding="utf-8") as handle:
        base_rows = list(csv.DictReader(handle))
    if [row["date"] for row in base_rows] != SESSION_DATES:
        raise ValueError("TWM_1M_MAX daily input dates do not match core replay sessions")

    price_marks = {ticker: dict(zip(SESSION_DATES, marks)) for ticker, marks in PRICES.items()}
    energy_marks = defaultdict(dict)
    with ENERGY_CSV.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if float(row["unit_size_u"]) == 10.0:
                energy_marks[row["ticker"].upper()][row["date"]] = float(row["eod_close"])
    for ticker in ENERGY_TICKERS:
        if energy_marks[ticker]:
            price_marks[ticker] = dict(energy_marks[ticker])

    core, _events = all_series()
    realized_events = []
    accepted_tickers = set(PRICES) | set(ENERGY_TICKERS)
    for event in core["V3A"]["realized_trades"]:
        if event["sym"] in accepted_tickers:
            realized_events.append({
                "ticker": event["sym"], "date": SESSION_DATES[event["idx"]], "pnl": event["pnl"],
                "source": "V3A_core",
            })
    _force_daily, _force_positions, force_realized = variant_force_multiplier_daily_model(
        "V3A", parse_trades(), return_realized=True
    )
    for event in force_realized:
        if event["sym"] in accepted_tickers:
            realized_events.append({
                "ticker": event["sym"], "date": event["date"], "pnl": event["pnl"],
                "source": "V3A_force_1u",
            })

    # Keep the actual source attribution for auditability while the accumulator
    # nets all same-ticker/same-session core and force realized PnL together.
    event_source_totals = defaultdict(float)
    for event in realized_events:
        event_source_totals[event["source"]] += float(event["pnl"]) * scale

    daily_rows, ticker_rows = run_share_accumulator(
        SESSION_DATES, price_marks, realized_events, scale, unit_value=UNIT
    )
    _write_csv(DAILY_OUTPUT, daily_rows)
    _write_csv(TICKER_OUTPUT, ticker_rows)

    terminal_pnl = sum(float(row["accumulator_net_pnl_usd"]) for row in ticker_rows)
    terminal_market_value = sum(float(row["accumulator_market_value_usd"]) for row in ticker_rows)
    terminal_basis = sum(float(row["accumulator_cost_basis_usd"]) for row in ticker_rows)
    terminal_realized_overlay_pnl = sum(float(row["accumulator_realized_pnl_usd"]) for row in ticker_rows)
    terminal_unrealized = sum(float(row["accumulator_unrealized_pnl_usd"]) for row in ticker_rows)
    terminal_loss_carry = sum(float(row["unfunded_loss_carry_usd"]) for row in ticker_rows)
    terminal_pending = sum(float(row["realized_pnl_without_future_mark_usd"]) for row in ticker_rows)
    base_pnl = float(base_summary["twm_1m_max_terminal_pnl_usd"])
    summary = {
        "portfolio": "TWM_1M_MAX share accumulator companion",
        "period_start": SESSION_DATES[0],
        "period_end": SESSION_DATES[-1],
        "sessions": len(SESSION_DATES),
        "scale_factor": f"{scale:.15f}",
        "funded_cash_base_usd": "1000000.00",
        "baseline_twm_1m_max_pnl_usd": f"{base_pnl:.2f}",
        "baseline_twm_1m_max_pnl_unchanged": True,
        "source_realized_trade_count": len(realized_events),
        "source_realized_pnl_scaled_usd": f"{sum(float(event['pnl']) for event in realized_events) * scale:.2f}",
        "core_realized_pnl_scaled_usd": f"{event_source_totals['V3A_core']:.2f}",
        "force_realized_pnl_scaled_usd": f"{event_source_totals['V3A_force_1u']:.2f}",
        "accumulator_market_value_usd": f"{terminal_market_value:.2f}",
        "accumulator_cost_basis_usd": f"{terminal_basis:.2f}",
        "accumulator_unrealized_pnl_usd": f"{terminal_unrealized:.2f}",
        "accumulator_realized_pnl_usd": f"{terminal_realized_overlay_pnl:.2f}",
        "accumulator_incremental_net_pnl_usd": f"{terminal_pnl:.2f}",
        "baseline_plus_incremental_accumulator_pnl_usd": f"{base_pnl + terminal_pnl:.2f}",
        "unfunded_loss_carry_usd": f"{terminal_loss_carry:.2f}",
        "realized_pnl_without_future_mark_usd": f"{terminal_pending:.2f}",
        "pending_realized_pnl_for_next_supplied_mark_usd": f"{terminal_pending:.2f}",
        "additional_out_of_pocket_cash_usd": "0.00",
        "energy_unit_value_usd": f"{UNIT:.2f}",
        "energy_trackers": "BRENT and OIL are separate model-U equivalents, never shares",
        "unrealized_gains_reinvested": False,
        "purchase_timing": "first supplied TradingView EOD mark strictly after realization date",
        "loss_handling": "sell same-ticker accumulator holdings at next supplied mark; carry uncovered loss against future realized profit",
        "share_count_chart": str(SHARE_COUNT_CHART_OUTPUT.relative_to(ROOT)),
        "event_sources": {
            "V3A_core_scaled_realized_pnl_usd": f"{event_source_totals['V3A_core']:.2f}",
            "V3A_force_1u_scaled_realized_pnl_usd": f"{event_source_totals['V3A_force_1u']:.2f}",
        },
    }
    SUMMARY_OUTPUT.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    _write_chart(base_rows, daily_rows)
    _write_share_count_chart(daily_rows, ticker_rows, terminal_pending, terminal_basis)

    lines = [
        "# TWM_1M_MAX Realized-PnL Share Accumulator",
        "",
        "This is a separate companion overlay. It does not replace or modify TWM_1M_MAX's dollar PnL, trade sizing, or basis-credit treatment.",
        "",
        "## Rules",
        "",
        "- Only realized PnL from the V3A core and its V3A 1U/EOD force schedule enters the accumulator. Unrealized gains are never reinvested.",
        "- Same-ticker realized PnL for a session is netted. Positive net PnL buys fractional shares at the first supplied TradingView EOD mark strictly after that session.",
        "- BRENT and OIL are tracked as separate model-U equivalents (1U = $10,000 of initial notional); they are not represented as shares.",
        "- A later realized loss sells only that ticker's accumulated lots at its next supplied EOD mark. Sale proceeds cover the loss first; any shortfall remains a loss debit and offsets future same-ticker realized profits before purchases resume.",
        "- DXY is not turned into a separate share/unit tracker or added as another sleeve; only eligible direct-ticker and energy realized events are used, avoiding DXY double-counting.",
        "- Marks are sourced from the existing TradingView benchmark session file and 10U energy sidecar input. No legacy-price substitution is used.",
        "- This accumulator is a cash-flow overlay: its share/unit cost basis is funded from realized PnL already included in the baseline. Therefore only the accumulator's own realized/unrealized investment PnL is incremental; its market value or cost basis must not be added to baseline PnL.",
        "",
        "## Terminal results",
        "",
        f"- Period: **{SESSION_DATES[0]}–{SESSION_DATES[-1]}** ({len(SESSION_DATES)} sessions).",
        f"- Baseline TWM_1M_MAX PnL remains **{_money(base_pnl)}** on the existing $1,000,000 funded-cash base.",
        f"- Scaled realized PnL events eligible for this overlay: **{_money(summary['source_realized_pnl_scaled_usd'])}** across {len(realized_events)} close events.",
        f"- Accumulator holdings at the last supplied marks: market value **{_money(terminal_market_value)}**, cost basis **{_money(terminal_basis)}**.",
        f"- Accumulator incremental PnL: **{_money(terminal_pnl)}** (realized **{_money(terminal_realized_overlay_pnl)}**, unrealized **{_money(terminal_unrealized)}**).",
        f"- Baseline plus incremental accumulator PnL for perspective: **{_money(base_pnl + terminal_pnl)}**. This does not add the accumulator's cost basis or market value a second time.",
        f"- Unfunded realized-loss carry: **{_money(terminal_loss_carry)}**; **{_money(terminal_pending)}** of net realized PnL from the final session is pending processing at the next supplied EOD mark (Oct. 27 if a TradingView mark is supplied).",
        f"- Additional out-of-pocket cash for the accumulated shares: **$0.00**. The **{_money(terminal_basis)}** accounting cost basis is funded from realized PnL already earned; it is not new cash or zero accounting basis.",
        "",
        "### Ticker-level holdings",
        "",
        "| Ticker | Tracker | Held shares / model-U equivalents | Cost basis | Market value | Incremental PnL | Loss carry |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in ticker_rows:
        amount_label = "model-U" if row["asset_tracker_type"] == "model_U_equivalent" else "shares"
        lines.append(
            f"| {row['ticker']} | {amount_label} | {float(row['shares_or_model_units_held']):,.8f} | "
            f"{_money(row['accumulator_cost_basis_usd'])} | {_money(row['accumulator_market_value_usd'])} | "
            f"{_money(row['accumulator_net_pnl_usd'])} | {_money(row['unfunded_loss_carry_usd'])} |"
        )
    lines.extend([
        "",
        "## Share counts through time",
        "",
        f"![Ticker-level share counts and separate energy model-U equivalents]({SHARE_COUNT_CHART_OUTPUT.relative_to(ROOT)})",
        "",
        "The panels show units held—not dollars or PnL. Equity panels use independent share-count axes because share quantities are not directly comparable across tickers; BRENT/OIL are in a separate model-U panel.",
        "",
        "## Audit files",
        "",
        f"- Share-count chart: `{SHARE_COUNT_CHART_OUTPUT.relative_to(ROOT)}`",
        f"- Daily ticker ledger: `{DAILY_OUTPUT.relative_to(ROOT)}`",
        f"- Terminal ticker summary: `{TICKER_OUTPUT.relative_to(ROOT)}`",
        f"- Machine-readable summary: `{SUMMARY_OUTPUT.relative_to(ROOT)}`",
        f"- PnL comparison chart: `{CHART_OUTPUT.relative_to(ROOT)}`",
        "",
        "The daily ledger distinguishes realized PnL, next-mark purchases/sales, held shares or U-equivalents, market value, cost basis, loss carry, and incremental overlay PnL.",
        "",
    ])
    REPORT_OUTPUT.write_text("\n".join(lines), encoding="utf-8")
    return summary


if __name__ == "__main__":
    result = build()
    print(f"Built share accumulator: {REPORT_OUTPUT}")
    print(f"Incremental overlay PnL: ${float(result['accumulator_incremental_net_pnl_usd']):,.2f}")
