"""Build whole-portfolio USD-vs-DXY numeraire graph and terminal report.

DXY is applied to the account as a numeraire, never as a separate $10,000 lot.
Daily FX cost bases use the uploaded close on each user's original entry date, as
confirmed by the user. The USD account-capital bases are $830k/$920k as specified.
"""

import csv
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from model_perf_core import (  # noqa: E402
    UNIT,
    VARIANTS,
    VARIANT_LABEL,
    VARIANT_COLOR,
    SESSION_DATES,
    all_series,
)
from us10y_adjustment import (  # noqa: E402
    BASELINE_PCT,
    START_DATE as US10Y_START_DATE,
    align_session_yields,
)

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
CHARTS = ROOT / "Charts" / "performance"
DXY_FILE = DATA / "dxy_september_october_2026_daily_close.csv"
FX_FILE = DATA / "eur_jpy_usd_september_october_2026.csv"
TERMINAL_MARK_FILE = DATA / "dxy_fx_oct22_marks_2026.csv"
US30Y_FILES = (
    DATA / "us30y_close_september_2026.csv",
    DATA / "us30y_close_october_2026.csv",
)
REPORT = ROOT / "DXY-Equivalent Portfolio Snapshot.md"
GRAPH = CHARTS / "16-whole-portfolio-dxy-vs-usd-pnl.png"
TOTAL_PNL_GRAPH = CHARTS / "17-dxy-close-vs-whole-portfolio-pnl-usd.png"
DAILY_CSV = DATA / "whole_portfolio_dxy_vs_usd_daily.csv"
SUMMARY_CSV = DATA / "whole_portfolio_dxy_vs_usd_summary.csv"
TERMINAL_DATE = "2026-10-22"
CAPITAL_BASIS_USD = {"V1": 830_000.0, "V2": 830_000.0, "V3A": 920_000.0, "V3B": 920_000.0}
FX_ENTRIES = {
    "EURUSD": {"date": "2026-09-15", "original_chart_entry": 1.15388, "column": "EUR_USD_Close"},
    "JPYUSD": {"date": "2026-09-07", "original_chart_entry": 0.010160, "column": "JPY_USD_Close"},
}
US30Y_ENTRY_DATE = "2026-09-15"
US30Y_ENTRY_YIELD_PCT = 5.35
US30Y_NEW_LONG_DATE = "2026-10-23"
US30Y_NEW_LONG_ENTRY_PCT = 5.311

BG = "#0d131e"
PANEL = "#141c2b"
GRID = "#26344a"
FG = "#edf2f7"
MUTED = "#93a4bd"
DXY_COLOR = "#e6b94a"


def read_daily_column(path, date_col, value_col):
    values = {}
    with path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if not reader.fieldnames or date_col not in reader.fieldnames or value_col not in reader.fieldnames:
            raise ValueError(f"Expected {date_col!r} and {value_col!r} in {path.name}")
        for row in reader:
            day = row[date_col].strip()
            if day in values:
                raise ValueError(f"Duplicate {day} observation in {path.name}")
            value = float(row[value_col].strip())
            if value <= 0:
                raise ValueError(f"Nonpositive close for {day} in {path.name}")
            values[day] = value
    missing = [day for day in SESSION_DATES if day not in values]
    if missing:
        raise ValueError(f"{path.name} lacks model-session observations: {missing}")
    return values


def validate_terminal_marks(dxy, fx):
    expected = {"DXY": dxy[TERMINAL_DATE]}
    expected.update({symbol: fx[symbol][TERMINAL_DATE] for symbol in FX_ENTRIES})
    with TERMINAL_MARK_FILE.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    marks = {row["symbol"].strip().upper(): (row["mark_date"].strip(), float(row["close"])) for row in rows}
    for symbol, value in expected.items():
        if symbol not in marks:
            raise ValueError(f"Missing {symbol} in {TERMINAL_MARK_FILE.name}")
        mark_date, mark_value = marks[symbol]
        if mark_date != TERMINAL_DATE or abs(mark_value - value) > 1e-10:
            raise ValueError(
                f"{symbol} terminal CSV value {value} does not match the authoritative "
                f"terminal mark {mark_date}={mark_value}"
            )


def read_fx_daily():
    fx = {symbol: {} for symbol in FX_ENTRIES}
    with FX_FILE.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            day = row["Date"].strip()
            for symbol, spec in FX_ENTRIES.items():
                value = float(row[spec["column"]].strip())
                if value <= 0:
                    raise ValueError(f"Nonpositive {symbol} close on {day}")
                fx[symbol][day] = value
    for symbol, values in fx.items():
        missing = [day for day in SESSION_DATES if day not in values]
        if missing:
            raise ValueError(f"{FX_FILE.name} lacks {symbol} model-session observations: {missing}")
        entry_date = FX_ENTRIES[symbol]["date"]
        if entry_date not in values:
            raise ValueError(f"No {symbol} daily close on its entry date {entry_date}")
    return fx


def read_us30y_daily():
    observed = {}
    for path in US30Y_FILES:
        with path.open(newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            if not reader.fieldnames or "Date" not in reader.fieldnames:
                raise ValueError(f"Missing Date column in {path.name}")
            value_col = next((name for name in reader.fieldnames if name != "Date"), None)
            if not value_col:
                raise ValueError(f"Missing close column in {path.name}")
            for row in reader:
                day = row["Date"].strip()
                if day in observed:
                    raise ValueError(f"Duplicate US30Y observation on {day}")
                observed[day] = float(row[value_col].strip())
    ordered_dates = sorted(observed)
    values, source_dates = {}, {}
    for day in SESSION_DATES:
        if day < US30Y_ENTRY_DATE:
            continue
        available = [source for source in ordered_dates if source <= day]
        if not available:
            raise ValueError(f"No US30Y close on or before {day}")
        source = available[-1]
        values[day] = observed[source]
        source_dates[day] = source
    return values, source_dates


def established_us10y_carry(core_series, yield_rows):
    """Reuse the existing US10Y carry basis; do not extend old assumptions."""
    daily = {variant: [0.0] * len(SESSION_DATES) for variant in VARIANTS}
    cumulative = {variant: [0.0] * len(SESSION_DATES) for variant in VARIANTS}
    for i in range(len(SESSION_DATES) - 1):
        start = SESSION_DATES[i]
        end = SESSION_DATES[i + 1]
        if start < US10Y_START_DATE or not yield_rows[i]["active"]:
            continue
        days = (date.fromisoformat(end) - date.fromisoformat(start)).days
        spread = (yield_rows[i]["yield_pct"] - BASELINE_PCT) / 100.0
        for variant in VARIANTS:
            notional = core_series[variant]["deployed"][i]
            daily[variant][i + 1] = notional * spread * days / 365.0
    for variant in VARIANTS:
        running = 0.0
        for i, amount in enumerate(daily[variant]):
            running += amount
            cumulative[variant][i] = running
    return daily, cumulative


def build_daily_series():
    dxy = read_daily_column(DXY_FILE, "Date", "Close")
    fx = read_fx_daily()
    validate_terminal_marks(dxy, fx)
    us30y, us30y_source_dates = read_us30y_daily()
    us10y_rows = align_session_yields(SESSION_DATES)
    core, _ = all_series()
    _daily_carry, cumulative_carry = established_us10y_carry(core, us10y_rows)

    fx_pnl = {symbol: [0.0] * len(SESSION_DATES) for symbol in FX_ENTRIES}
    for symbol, spec in FX_ENTRIES.items():
        base = fx[symbol][spec["date"]]
        for i, day in enumerate(SESSION_DATES):
            if day >= spec["date"]:
                fx_pnl[symbol][i] = UNIT * (fx[symbol][day] / base - 1.0)

    us30y_pnl = [0.0] * len(SESSION_DATES)
    for i, day in enumerate(SESSION_DATES):
        if day >= US30Y_ENTRY_DATE:
            us30y_pnl[i] = -UNIT * (us30y[day] / US30Y_ENTRY_YIELD_PCT - 1.0)

    result = {}
    for variant in VARIANTS:
        unrealized = [
            core[variant]["unrealized"][i]
            + fx_pnl["EURUSD"][i]
            + fx_pnl["JPYUSD"][i]
            + us30y_pnl[i]
            for i in range(len(SESSION_DATES))
        ]
        realized = list(core[variant]["realized"])
        total_pnl = [
            realized[i] + unrealized[i] + cumulative_carry[variant][i]
            for i in range(len(SESSION_DATES))
        ]
        capital = CAPITAL_BASIS_USD[variant]
        baseline_pnl = total_pnl[0]
        usd_account_value = [capital + value - baseline_pnl for value in total_pnl]
        usd_return_pct = [(value / capital - 1.0) * 100.0 for value in usd_account_value]
        dxy_equivalent_value = [usd / dxy[day] for usd, day in zip(usd_account_value, SESSION_DATES)]
        dxy_start_value = capital / dxy[SESSION_DATES[0]]
        dxy_return_pct = [(value / dxy_start_value - 1.0) * 100.0 for value in dxy_equivalent_value]
        result[variant] = {
            "realized_usd": realized,
            "unrealized_usd": unrealized,
            "fx_eur_usd": fx_pnl["EURUSD"],
            "fx_jpy_usd": fx_pnl["JPYUSD"],
            "us30y_unrealized_usd": us30y_pnl,
            "us10y_carry_usd": cumulative_carry[variant],
            "total_pnl_usd": total_pnl,
            "usd_account_value": usd_account_value,
            "usd_return_pct": usd_return_pct,
            "dxy_equivalent_value": dxy_equivalent_value,
            "dxy_equivalent_pnl": [value - dxy_start_value for value in dxy_equivalent_value],
            "dxy_return_pct": dxy_return_pct,
            "core_model_deployed_usd": list(core[variant]["deployed"]),
        }
    return dxy, fx, us30y, us30y_source_dates, core, result


def write_daily_csv(dxy, fx, us30y, us30y_source_dates, core, result):
    fields = [
        "variant", "session_date", "dxy_close", "capital_basis_usd",
        "core_model_deployed_notional_usd", "core_realized_pnl_usd",
        "core_unrealized_pnl_usd", "eurusd_daily_close", "eurusd_entry_close_basis",
        "eurusd_unrealized_pnl_usd", "jpyusd_daily_close", "jpyusd_entry_close_basis",
        "jpyusd_unrealized_pnl_usd", "us30y_daily_close_pct", "us30y_source_date",
        "us30y_short_unrealized_pnl_usd", "total_unrealized_pnl_usd", "us10y_carry_cumulative_usd", "total_pnl_usd",
        "usd_account_value", "usd_return_pct", "dxy_equivalent_account_value",
        "dxy_equivalent_pnl", "dxy_numeraire_return_pct",
    ]
    with DAILY_CSV.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        for variant in VARIANTS:
            for i, day in enumerate(SESSION_DATES):
                writer.writerow({
                    "variant": variant,
                    "session_date": day,
                    "dxy_close": dxy[day],
                    "capital_basis_usd": CAPITAL_BASIS_USD[variant],
                    "core_model_deployed_notional_usd": result[variant]["core_model_deployed_usd"][i],
                    "core_realized_pnl_usd": core[variant]["realized"][i],
                    "core_unrealized_pnl_usd": core[variant]["unrealized"][i],
                    "eurusd_daily_close": fx["EURUSD"][day],
                    "eurusd_entry_close_basis": fx["EURUSD"][FX_ENTRIES["EURUSD"]["date"]],
                    "eurusd_unrealized_pnl_usd": result[variant]["fx_eur_usd"][i],
                    "jpyusd_daily_close": fx["JPYUSD"][day],
                    "jpyusd_entry_close_basis": fx["JPYUSD"][FX_ENTRIES["JPYUSD"]["date"]],
                    "jpyusd_unrealized_pnl_usd": result[variant]["fx_jpy_usd"][i],
                    "us30y_daily_close_pct": us30y.get(day, ""),
                    "us30y_source_date": us30y_source_dates.get(day, ""),
                    "us30y_short_unrealized_pnl_usd": result[variant]["us30y_unrealized_usd"][i],
                    "total_unrealized_pnl_usd": result[variant]["unrealized_usd"][i],
                    "us10y_carry_cumulative_usd": result[variant]["us10y_carry_usd"][i],
                    "total_pnl_usd": result[variant]["total_pnl_usd"][i],
                    "usd_account_value": result[variant]["usd_account_value"][i],
                    "usd_return_pct": result[variant]["usd_return_pct"][i],
                    "dxy_equivalent_account_value": result[variant]["dxy_equivalent_value"][i],
                    "dxy_equivalent_pnl": result[variant]["dxy_equivalent_pnl"][i],
                    "dxy_numeraire_return_pct": result[variant]["dxy_return_pct"][i],
                })


def make_total_pnl_graph(dxy, result):
    """Plot cumulative total USD PnL against the daily DXY index close."""
    import matplotlib.dates as mdates
    import matplotlib.pyplot as plt
    from matplotlib.ticker import FuncFormatter

    CHARTS.mkdir(parents=True, exist_ok=True)
    dates = [date.fromisoformat(day) for day in SESSION_DATES]
    fig, ax = plt.subplots(figsize=(14, 7.5))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(PANEL)
    ax.grid(True, color=GRID, alpha=0.7, linewidth=0.7)
    ax.tick_params(colors=MUTED, labelsize=9)
    for side in ("bottom", "left", "top", "right"):
        ax.spines[side].set_color(GRID)

    for variant in VARIANTS:
        ax.plot(
            dates,
            result[variant]["total_pnl_usd"],
            color=VARIANT_COLOR[variant],
            lw=2.2,
            label=f"{VARIANT_LABEL[variant]} — total PnL (USD)",
        )
    ax.axhline(0, color=MUTED, lw=0.9, ls="--", alpha=0.85)
    ax.set_ylabel("Whole-portfolio cumulative PnL (USD)", color=FG)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda value, _: f"${value/1000:,.0f}k"))
    ax.set_title("DXY Close vs. Whole-Portfolio PnL in Dollars", color=FG, fontsize=16, pad=13)

    ax_dxy = ax.twinx()
    ax_dxy.plot(
        dates,
        [dxy[day] for day in SESSION_DATES],
        color=DXY_COLOR,
        lw=2.4,
        ls=(0, (5, 3)),
        label="DXY daily close (right axis)",
    )
    ax_dxy.set_ylabel("DXY index close", color=DXY_COLOR)
    ax_dxy.tick_params(axis="y", colors=DXY_COLOR, labelsize=9)
    ax_dxy.spines["right"].set_color(DXY_COLOR)

    handles1, labels1 = ax.get_legend_handles_labels()
    handles2, labels2 = ax_dxy.get_legend_handles_labels()
    legend = ax.legend(handles1 + handles2, labels1 + labels2, loc="upper left",
                       ncol=2, fontsize=8.5, frameon=True)
    legend.get_frame().set_facecolor(BG)
    legend.get_frame().set_edgecolor(GRID)
    for text in legend.get_texts():
        text.set_color(FG)

    tick_dates = dates[::4]
    if tick_dates[-1] != dates[-1]:
        tick_dates.append(dates[-1])
    ax.set_xticks(tick_dates)
    ax.set_xlim(dates[0], dates[-1])
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%-m/%-d"))
    ax.tick_params(axis="x", rotation=35)
    ax.set_xlabel("Session close (Arizona / MST)", color=FG)
    fig.text(
        0.5, 0.012,
        "Total USD PnL = realized + open unrealized (including FX/US30Y marks) + established US10Y carry; DXY is the whole-book numeraire, not a trade.",
        color=MUTED, ha="center", fontsize=8.5,
    )
    fig.tight_layout(rect=(0.02, 0.04, 0.98, 0.99))
    fig.savefig(TOTAL_PNL_GRAPH, dpi=160, facecolor=BG, bbox_inches="tight")
    plt.close(fig)


def make_graph(dxy, result):
    import matplotlib.dates as mdates
    import matplotlib.pyplot as plt
    from matplotlib.ticker import FuncFormatter

    CHARTS.mkdir(parents=True, exist_ok=True)
    dates = [date.fromisoformat(day) for day in SESSION_DATES]
    fig, (ax_top, ax_bottom) = plt.subplots(
        2, 1, figsize=(14, 10), sharex=True,
        gridspec_kw={"height_ratios": [1.15, 1.0]},
    )
    fig.patch.set_facecolor(BG)
    for ax in (ax_top, ax_bottom):
        ax.set_facecolor(PANEL)
        ax.grid(True, color=GRID, alpha=0.7, linewidth=0.7)
        ax.tick_params(colors=MUTED, labelsize=9)
        ax.spines["bottom"].set_color(GRID)
        ax.spines["left"].set_color(GRID)
        ax.spines["top"].set_color(GRID)
        ax.spines["right"].set_color(GRID)
        ax.yaxis.label.set_color(FG)

    # Upper plot: DXY level versus the whole portfolio's daily USD unrealized PnL.
    for variant in VARIANTS:
        ax_top.plot(
            dates,
            result[variant]["unrealized_usd"],
            color=VARIANT_COLOR[variant],
            lw=2.0,
            label=f"{VARIANT_LABEL[variant]} — unrealized USD",
        )
    ax_top.axhline(0, color=MUTED, lw=0.8, ls="--", alpha=0.8)
    ax_top.set_ylabel("Whole-portfolio unrealized PnL (USD)")
    ax_top.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f"${x/1000:,.0f}k"))
    ax_top.set_title("DXY Close vs. Whole-Portfolio Unrealized PnL in Dollars", color=FG, fontsize=15, pad=11)
    ax_dxy = ax_top.twinx()
    ax_dxy.plot(dates, [dxy[day] for day in SESSION_DATES], color=DXY_COLOR, lw=2.3,
                ls=(0, (5, 3)), label="DXY daily close (right axis)")
    ax_dxy.set_ylabel("DXY index close", color=DXY_COLOR)
    ax_dxy.tick_params(axis="y", colors=DXY_COLOR, labelsize=9)
    ax_dxy.spines["right"].set_color(DXY_COLOR)
    handles1, labels1 = ax_top.get_legend_handles_labels()
    handles2, labels2 = ax_dxy.get_legend_handles_labels()
    legend1 = ax_top.legend(handles1 + handles2, labels1 + labels2, loc="upper left",
                            ncol=3, fontsize=8, frameon=True)
    legend1.get_frame().set_facecolor(BG)
    legend1.get_frame().set_edgecolor(GRID)
    for text in legend1.get_texts():
        text.set_color(FG)

    # Lower plot: compare returns in USD with the same account value denominated in DXY.
    for variant in VARIANTS:
        ax_bottom.plot(dates, result[variant]["usd_return_pct"], color=VARIANT_COLOR[variant],
                       lw=1.9, label=f"{variant} USD")
        ax_bottom.plot(dates, result[variant]["dxy_return_pct"], color=VARIANT_COLOR[variant],
                       lw=1.9, ls="--", label=f"{variant} DXY-numeraire")
    ax_bottom.axhline(0, color=MUTED, lw=0.8, ls=":")
    ax_bottom.set_ylabel("Cumulative return from starting capital (%)")
    ax_bottom.set_xlabel("Session close (Arizona / MST)", color=FG)
    ax_bottom.set_title("Same Portfolio Return Measured in USD vs. DXY", color=FG, fontsize=13, pad=9)
    tick_dates = dates[::4]
    if tick_dates[-1] != dates[-1]:
        tick_dates.append(dates[-1])
    ax_bottom.set_xticks(tick_dates)
    ax_bottom.set_xlim(dates[0], dates[-1])
    ax_bottom.xaxis.set_major_formatter(mdates.DateFormatter("%-m/%-d"))
    ax_bottom.tick_params(axis="x", rotation=35)
    legend2 = ax_bottom.legend(loc="upper left", ncol=4, fontsize=8, frameon=True)
    legend2.get_frame().set_facecolor(BG)
    legend2.get_frame().set_edgecolor(GRID)
    for text in legend2.get_texts():
        text.set_color(FG)

    fig.text(
        0.5, 0.012,
        "DXY is the whole-book numeraire, not a separate $10,000 trade. DXY-equivalent account value = USD account value ÷ daily DXY close.",
        color=MUTED, ha="center", fontsize=9,
    )
    fig.tight_layout(rect=(0.02, 0.04, 0.98, 0.99))
    fig.savefig(GRAPH, dpi=160, facecolor=BG, bbox_inches="tight")
    plt.close(fig)


def build_report(dxy, fx, us30y, result):
    lines = [
        "# Whole-Portfolio DXY Numeraire — Daily Comparison",
        "",
        "The new first chart compares each variant's cumulative total PnL in dollars with the daily DXY close. Total USD PnL includes realized PnL, open unrealized PnL (including FX and US30Y marks), and the established US10Y carry adjustment. DXY is the numeraire for the whole portfolio, not a standalone $10,000 position. The second graph retains the open-unrealized-PnL and USD-versus-DXY-return views.",
        "",
        "![DXY Close vs. Whole-Portfolio PnL in Dollars](Charts/performance/17-dxy-close-vs-whole-portfolio-pnl-usd.png)",
        "",
        "![Whole-portfolio unrealized PnL and USD/DXY returns](Charts/performance/16-whole-portfolio-dxy-vs-usd-pnl.png)",
        "",
        "## Oct. 22 Terminal Results",
        "",
        "| Variant | Capital basis | Open unrealized PnL (USD) | Realized PnL (USD) | US10Y carry | Total PnL (USD) | USD return | DXY-equivalent account value (index units) | DXY-numeraire return |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    last = len(SESSION_DATES) - 1
    for variant in VARIANTS:
        row = result[variant]
        lines.append(
            f"| **{VARIANT_LABEL[variant]}** | ${CAPITAL_BASIS_USD[variant]:,.0f} | "
            f"${row['unrealized_usd'][last]:+,.2f} | ${row['realized_usd'][last]:+,.2f} | "
            f"${row['us10y_carry_usd'][last]:+,.2f} | ${row['total_pnl_usd'][last]:+,.2f} | "
            f"{row['usd_return_pct'][last]:+.3f}% | {row['dxy_equivalent_value'][last]:,.2f} DXY-eq units | "
            f"{row['dxy_return_pct'][last]:+.3f}% |"
        )
    eur_base = fx["EURUSD"][FX_ENTRIES["EURUSD"]["date"]]
    jpy_base = fx["JPYUSD"][FX_ENTRIES["JPYUSD"]["date"]]
    lines.extend([
        "",
        "## DXY and FX Basis",
        "",
        f"- DXY daily closes run from `{SESSION_DATES[0]}` (`{dxy[SESSION_DATES[0]]}`) through `{TERMINAL_DATE}` (`{dxy[TERMINAL_DATE]}`). This series' Oct. 22 close of 102.22 supersedes the earlier 101.616 terminal mark, as directed.",
        f"- EUR/USD PnL uses the uploaded daily close on its entry date as its cost basis: `{FX_ENTRIES['EURUSD']['date']}` close `{eur_base}`. The original chart quote `1.15388` remains in the trade log as source evidence; the graph does not use it as the PnL basis, per your instruction.",
        f"- JPY/USD PnL uses the uploaded daily close on its entry date as its cost basis: `{FX_ENTRIES['JPYUSD']['date']}` close `{jpy_base}`. The original chart quote `0.010160` remains in the trade log as source evidence; the graph does not use it as the PnL basis, per your instruction.",
        "- DXY-equivalent account value is computed as `USD account value ÷ daily DXY close`; returns are normalized to the Sep. 3 DXY-equivalent starting value. The USD capital bases are the $830,000 / $920,000 portfolio amounts you specified.",
        "- The DXY LONG log entry is retained as historical reference evidence, but this comparison does not treat it as an additional $10,000 position or add separate DXY-trade PnL.",
        "",
        "## PnL, Carry, and Position Treatment",
        "",
        "- Daily EUR/USD and JPY/USD unrealized PnL is calculated from the entry-date daily close, then marked to each uploaded daily close at $10,000 standard notional per position.",
        "- The Sep. 15 US30Y SHORT is marked daily with a proportional quote-return proxy on $10,000 notional. This is not a bond-duration/futures valuation. The Oct. 23 US30Y LONG, ORCL LONG at $125.83 for $25,000, and fifth LCID LONG at $3.47 are after the Oct. 22 cutoff and excluded from this graph. The four LCID entries dated Oct. 20–22 are included.",
        "- The US10Y spread carry preserves the established 4.865% baseline, actual/365 accrual, and cumulative deployed-notional basis from the core model comparison. Supplementary FX and US30Y PnL are included in the USD account value, but are not used to retroactively change the carry denominator. DXY itself is excluded because it is the numeraire.",
        "- US10Y positions are carry references, not independent yield-quote PnL rows. For the Oct. 12 market holiday, the user-approved US10Y 5.24% close from Oct. 9 is carried; the US30Y mark likewise carries its Oct. 9 5.60% close. The daily export records the US30Y source date explicitly.",
        "",
        f"Daily values and conversion factors: [`{DAILY_CSV.name}`](data/{DAILY_CSV.name}).",
        "",
        f"Terminal variant summary: [`{SUMMARY_CSV.name}`](data/{SUMMARY_CSV.name}).",
        "",
    ])
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def write_summary_csv(result, fx, dxy):
    fields = [
        "variant", "capital_basis_usd", "terminal_dxy_close", "dxy_start_close",
        "terminal_total_unrealized_pnl_usd", "terminal_realized_pnl_usd",
        "terminal_us10y_carry_usd", "terminal_total_pnl_usd", "usd_return_pct",
        "terminal_dxy_equivalent_account_value", "terminal_dxy_equivalent_pnl",
        "dxy_numeraire_return_pct", "eurusd_entry_close_basis", "eurusd_terminal_close",
        "eurusd_terminal_unrealized_pnl_usd", "jpyusd_entry_close_basis",
        "jpyusd_terminal_close", "jpyusd_terminal_unrealized_pnl_usd",
    ]
    with SUMMARY_CSV.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        for variant in VARIANTS:
            last = len(SESSION_DATES) - 1
            writer.writerow({
                "variant": variant,
                "capital_basis_usd": CAPITAL_BASIS_USD[variant],
                "terminal_dxy_close": dxy[TERMINAL_DATE],
                "dxy_start_close": dxy[SESSION_DATES[0]],
                "terminal_total_unrealized_pnl_usd": result[variant]["unrealized_usd"][last],
                "terminal_realized_pnl_usd": result[variant]["realized_usd"][last],
                "terminal_us10y_carry_usd": result[variant]["us10y_carry_usd"][last],
                "terminal_total_pnl_usd": result[variant]["total_pnl_usd"][last],
                "usd_return_pct": result[variant]["usd_return_pct"][last],
                "terminal_dxy_equivalent_account_value": result[variant]["dxy_equivalent_value"][last],
                "terminal_dxy_equivalent_pnl": result[variant]["dxy_equivalent_pnl"][last],
                "dxy_numeraire_return_pct": result[variant]["dxy_return_pct"][last],
                "eurusd_entry_close_basis": fx["EURUSD"][FX_ENTRIES["EURUSD"]["date"]],
                "eurusd_terminal_close": fx["EURUSD"][TERMINAL_DATE],
                "eurusd_terminal_unrealized_pnl_usd": result[variant]["fx_eur_usd"][last],
                "jpyusd_entry_close_basis": fx["JPYUSD"][FX_ENTRIES["JPYUSD"]["date"]],
                "jpyusd_terminal_close": fx["JPYUSD"][TERMINAL_DATE],
                "jpyusd_terminal_unrealized_pnl_usd": result[variant]["fx_jpy_usd"][last],
            })


def main():
    dxy, fx, us30y, us30y_source_dates, core, result = build_daily_series()
    write_daily_csv(dxy, fx, us30y, us30y_source_dates, core, result)
    write_summary_csv(result, fx, dxy)
    make_total_pnl_graph(dxy, result)
    make_graph(dxy, result)
    build_report(dxy, fx, us30y, result)
    last = len(SESSION_DATES) - 1
    for variant in VARIANTS:
        print(
            f"{variant}: unrealized ${result[variant]['unrealized_usd'][last]:,.2f}; "
            f"USD return {result[variant]['usd_return_pct'][last]:+.3f}%; "
            f"DXY return {result[variant]['dxy_return_pct'][last]:+.3f}%"
        )
    print(f"Wrote {TOTAL_PNL_GRAPH.relative_to(ROOT)}")
    print(f"Wrote {GRAPH.relative_to(ROOT)}")
    print(f"Wrote {REPORT.relative_to(ROOT)}")
    print(f"Wrote {DAILY_CSV.relative_to(ROOT)}")
    print(f"Wrote {SUMMARY_CSV.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
