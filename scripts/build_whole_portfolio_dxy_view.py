"""Build whole-portfolio USD-vs-DXY numeraire graph and terminal report.

DXY is applied to the account as a numeraire, never as a separate $10,000 lot.
Daily FX cost bases use the uploaded close on each user's original entry date, as
confirmed by the user. The USD account-capital bases are $830k/$920k as specified.
"""

import csv
import json
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
TERMINAL_MARK_FILE = DATA / "dxy_fx_oct23_marks_2026.csv"
US30Y_FILES = (
    DATA / "us30y_close_september_2026.csv",
    DATA / "us30y_close_october_2026.csv",
)
REPORT = ROOT / "DXY-Equivalent Portfolio Snapshot.md"
GRAPH = CHARTS / "16-whole-portfolio-dxy-vs-usd-pnl.png"
TOTAL_PNL_GRAPH = CHARTS / "17-dxy-close-vs-whole-portfolio-pnl-usd.png"
DAILY_CSV = DATA / "whole_portfolio_dxy_vs_usd_daily.csv"
SUMMARY_CSV = DATA / "whole_portfolio_dxy_vs_usd_summary.csv"
TERMINAL_DATE = "2026-10-23"
CAPITAL_BASIS_USD = {"V1": 830_000.0, "V2": 830_000.0, "V3A": 920_000.0, "V3B": 920_000.0}
FX_ENTRIES = {
    "EURUSD": {"date": "2026-09-15", "original_chart_entry": 1.15388, "column": "EUR_USD_Close"},
    "JPYUSD": {"date": "2026-09-07", "original_chart_entry": 0.010160, "column": "JPY_USD_Close"},
}
US30Y_ENTRY_DATE = "2026-09-15"
US30Y_ENTRY_YIELD_PCT = 5.35
US30Y_NEW_LONG_DATE = "2026-10-23"
US30Y_NEW_LONG_ENTRY_PCT = 5.311
US30Y_MULTIPLIER_START = "2026-09-15"
US30Y_MULTIPLIER_BASELINE_PCT = 5.35
YIELD_FACTOR_SCENARIOS = ("none", "us10y", "us10y_us30y")
YIELD_FACTOR_LABELS = {
    "none": "No yield multiplier",
    "us10y": "US10Y blanket multiplier",
    "us10y_us30y": "US10Y × US30Y blanket multipliers",
}
YIELD_EXPLORER = ROOT / "Whole Portfolio Yield Multiplier Explorer.html"
YIELD_SCENARIO_CSV = DATA / "whole_portfolio_yield_multiplier_scenarios.csv"
YIELD_SCENARIO_SUMMARY_CSV = DATA / "whole_portfolio_yield_multiplier_summary.csv"

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


def compound_yield_multiplier(session_dates, yields_by_date, baseline_pct, start_date):
    """Compound a yield-spread factor using actual calendar days / 365."""
    factors = [1.0] * len(session_dates)
    for i in range(len(session_dates) - 1):
        factors[i + 1] = factors[i]
        start = session_dates[i]
        if start < start_date or start not in yields_by_date:
            continue
        days = (date.fromisoformat(session_dates[i + 1]) - date.fromisoformat(start)).days
        annual_spread = (yields_by_date[start] - baseline_pct) / 100.0
        daily_factor = 1.0 + annual_spread * days / 365.0
        if daily_factor <= 0:
            raise ValueError(f"Nonpositive yield multiplier step on {start}: {daily_factor}")
        factors[i + 1] = factors[i] * daily_factor
    return factors


def build_daily_series():
    dxy = read_daily_column(DXY_FILE, "Date", "Close")
    fx = read_fx_daily()
    validate_terminal_marks(dxy, fx)
    us30y, us30y_source_dates = read_us30y_daily()
    us10y_rows = align_session_yields(SESSION_DATES)
    core, _ = all_series()
    _daily_carry, legacy_cumulative_carry = established_us10y_carry(core, us10y_rows)
    us10y_values = {
        row["date"]: row["yield_pct"]
        for row in us10y_rows
        if row["yield_pct"] is not None
    }
    us10y_factor = compound_yield_multiplier(
        SESSION_DATES, us10y_values, BASELINE_PCT, US10Y_START_DATE
    )
    us30y_factor = compound_yield_multiplier(
        SESSION_DATES, us30y, US30Y_MULTIPLIER_BASELINE_PCT, US30Y_MULTIPLIER_START
    )
    combined_factor = [a * b for a, b in zip(us10y_factor, us30y_factor)]

    fx_pnl = {symbol: [0.0] * len(SESSION_DATES) for symbol in FX_ENTRIES}
    for symbol, spec in FX_ENTRIES.items():
        base = fx[symbol][spec["date"]]
        for i, day in enumerate(SESSION_DATES):
            if day >= spec["date"]:
                fx_pnl[symbol][i] = UNIT * (fx[symbol][day] / base - 1.0)

    us30y_short_pnl = [0.0] * len(SESSION_DATES)
    us30y_long_pnl = [0.0] * len(SESSION_DATES)
    for i, day in enumerate(SESSION_DATES):
        if day >= US30Y_ENTRY_DATE:
            us30y_short_pnl[i] = -UNIT * (us30y[day] / US30Y_ENTRY_YIELD_PCT - 1.0)
        if day >= US30Y_NEW_LONG_DATE:
            us30y_long_pnl[i] = UNIT * (us30y[day] / US30Y_NEW_LONG_ENTRY_PCT - 1.0)

    result = {}
    for variant in VARIANTS:
        unrealized = [
            core[variant]["unrealized"][i]
            + fx_pnl["EURUSD"][i]
            + fx_pnl["JPYUSD"][i]
            + us30y_short_pnl[i]
            + us30y_long_pnl[i]
            for i in range(len(SESSION_DATES))
        ]
        realized = list(core[variant]["realized"])
        total_pnl = [realized[i] + unrealized[i] for i in range(len(SESSION_DATES))]
        capital = CAPITAL_BASIS_USD[variant]
        baseline_pnl = total_pnl[0]
        base_account_value = [capital + value - baseline_pnl for value in total_pnl]
        dxy_start_value = capital / dxy[SESSION_DATES[0]]
        scenario_factors = {
            "none": [1.0] * len(SESSION_DATES),
            "us10y": us10y_factor,
            "us10y_us30y": combined_factor,
        }
        scenarios = {}
        for scenario, factors in scenario_factors.items():
            account_value = [value * factor for value, factor in zip(base_account_value, factors)]
            scenario_pnl = [value - capital for value in account_value]
            dxy_value = [value / dxy[day] for value, day in zip(account_value, SESSION_DATES)]
            scenarios[scenario] = {
                "account_value_usd": account_value,
                "pnl_usd": scenario_pnl,
                "usd_return_pct": [(value / capital - 1.0) * 100.0 for value in account_value],
                "dxy_equivalent_value": dxy_value,
                "dxy_return_pct": [(value / dxy_start_value - 1.0) * 100.0 for value in dxy_value],
            }
        result[variant] = {
            "realized_usd": realized,
            "unrealized_usd": unrealized,
            "fx_eur_usd": fx_pnl["EURUSD"],
            "fx_jpy_usd": fx_pnl["JPYUSD"],
            "us30y_short_unrealized_usd": us30y_short_pnl,
            "us30y_long_unrealized_usd": us30y_long_pnl,
            "legacy_us10y_carry_reference_usd": legacy_cumulative_carry[variant],
            "total_pnl_usd": total_pnl,
            "usd_account_value": base_account_value,
            "usd_return_pct": scenarios["none"]["usd_return_pct"],
            "dxy_equivalent_value": scenarios["none"]["dxy_equivalent_value"],
            "dxy_equivalent_pnl": [value - dxy_start_value for value in scenarios["none"]["dxy_equivalent_value"]],
            "dxy_return_pct": scenarios["none"]["dxy_return_pct"],
            "yield_factor_us10y": us10y_factor,
            "yield_factor_us30y": us30y_factor,
            "yield_factor_combined": combined_factor,
            "yield_scenarios": scenarios,
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
        "us30y_short_unrealized_pnl_usd", "us30y_long_unrealized_pnl_usd",
        "total_unrealized_pnl_usd", "legacy_us10y_carry_reference_usd", "total_pnl_usd",
        "usd_account_value", "usd_return_pct", "dxy_equivalent_account_value",
        "dxy_equivalent_pnl", "dxy_numeraire_return_pct",
        "us10y_blanket_factor", "us30y_blanket_factor", "combined_us10y_us30y_factor",
        "none_account_value_usd", "none_pnl_usd", "none_dxy_equivalent_value",
        "none_usd_return_pct", "none_dxy_return_pct",
        "us10y_account_value_usd", "us10y_pnl_usd", "us10y_dxy_equivalent_value",
        "us10y_usd_return_pct", "us10y_dxy_return_pct",
        "us10y_us30y_account_value_usd", "us10y_us30y_pnl_usd",
        "us10y_us30y_dxy_equivalent_value", "us10y_us30y_usd_return_pct",
        "us10y_us30y_dxy_return_pct",
    ]
    with DAILY_CSV.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
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
                    "us30y_short_unrealized_pnl_usd": result[variant]["us30y_short_unrealized_usd"][i],
                    "us30y_long_unrealized_pnl_usd": result[variant]["us30y_long_unrealized_usd"][i],
                    "total_unrealized_pnl_usd": result[variant]["unrealized_usd"][i],
                    "legacy_us10y_carry_reference_usd": result[variant]["legacy_us10y_carry_reference_usd"][i],
                    "total_pnl_usd": result[variant]["total_pnl_usd"][i],
                    "usd_account_value": result[variant]["usd_account_value"][i],
                    "usd_return_pct": result[variant]["usd_return_pct"][i],
                    "dxy_equivalent_account_value": result[variant]["dxy_equivalent_value"][i],
                    "dxy_equivalent_pnl": result[variant]["dxy_equivalent_pnl"][i],
                    "dxy_numeraire_return_pct": result[variant]["dxy_return_pct"][i],
                    "us10y_blanket_factor": result[variant]["yield_factor_us10y"][i],
                    "us30y_blanket_factor": result[variant]["yield_factor_us30y"][i],
                    "combined_us10y_us30y_factor": result[variant]["yield_factor_combined"][i],
                    **{
                        f"{scenario}_{field}": values[i]
                        for scenario, scenario_values in result[variant]["yield_scenarios"].items()
                        for field, values in scenario_values.items()
                    },
                })


def write_yield_scenario_csv(result, dxy):
    fields = [
        "variant", "scenario", "scenario_label", "session_date", "capital_basis_usd",
        "base_total_pnl_usd", "base_account_value_usd", "us10y_factor", "us30y_factor",
        "combined_factor", "scenario_factor", "scenario_account_value_usd",
        "scenario_pnl_usd", "scenario_usd_return_pct", "dxy_close",
        "scenario_dxy_equivalent_account_value", "scenario_dxy_return_pct",
    ]
    with YIELD_SCENARIO_CSV.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for variant in VARIANTS:
            row = result[variant]
            for scenario in YIELD_FACTOR_SCENARIOS:
                scenario_values = row["yield_scenarios"][scenario]
                for i, day in enumerate(SESSION_DATES):
                    factor = 1.0 if scenario == "none" else (
                        row["yield_factor_us10y"][i] if scenario == "us10y"
                        else row["yield_factor_combined"][i]
                    )
                    writer.writerow({
                        "variant": variant,
                        "scenario": scenario,
                        "scenario_label": YIELD_FACTOR_LABELS[scenario],
                        "session_date": day,
                        "capital_basis_usd": CAPITAL_BASIS_USD[variant],
                        "base_total_pnl_usd": row["total_pnl_usd"][i],
                        "base_account_value_usd": row["usd_account_value"][i],
                        "us10y_factor": row["yield_factor_us10y"][i],
                        "us30y_factor": row["yield_factor_us30y"][i],
                        "combined_factor": row["yield_factor_combined"][i],
                        "scenario_factor": factor,
                        "scenario_account_value_usd": scenario_values["account_value_usd"][i],
                        "scenario_pnl_usd": scenario_values["pnl_usd"][i],
                        "scenario_usd_return_pct": scenario_values["usd_return_pct"][i],
                        "dxy_close": dxy[day],
                        "scenario_dxy_equivalent_account_value": scenario_values["dxy_equivalent_value"][i],
                        "scenario_dxy_return_pct": scenario_values["dxy_return_pct"][i],
                    })


def write_yield_scenario_summary_csv(result):
    fields = [
        "variant", "scenario", "scenario_label", "capital_basis_usd",
        "terminal_us10y_factor", "terminal_us30y_factor", "terminal_combined_factor",
        "terminal_scenario_factor", "terminal_account_value_usd", "terminal_pnl_usd",
        "terminal_usd_return_pct", "terminal_dxy_equivalent_account_value",
        "terminal_dxy_return_pct",
    ]
    with YIELD_SCENARIO_SUMMARY_CSV.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        last = len(SESSION_DATES) - 1
        for variant in VARIANTS:
            row = result[variant]
            for scenario in YIELD_FACTOR_SCENARIOS:
                values = row["yield_scenarios"][scenario]
                factor = 1.0 if scenario == "none" else (
                    row["yield_factor_us10y"][last] if scenario == "us10y"
                    else row["yield_factor_combined"][last]
                )
                writer.writerow({
                    "variant": variant,
                    "scenario": scenario,
                    "scenario_label": YIELD_FACTOR_LABELS[scenario],
                    "capital_basis_usd": CAPITAL_BASIS_USD[variant],
                    "terminal_us10y_factor": row["yield_factor_us10y"][last],
                    "terminal_us30y_factor": row["yield_factor_us30y"][last],
                    "terminal_combined_factor": row["yield_factor_combined"][last],
                    "terminal_scenario_factor": factor,
                    "terminal_account_value_usd": values["account_value_usd"][last],
                    "terminal_pnl_usd": values["pnl_usd"][last],
                    "terminal_usd_return_pct": values["usd_return_pct"][last],
                    "terminal_dxy_equivalent_account_value": values["dxy_equivalent_value"][last],
                    "terminal_dxy_return_pct": values["dxy_return_pct"][last],
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
        "Base USD PnL = realized + open unrealized (including FX/US30Y position marks), excluding yield multipliers; see the separate full-account multiplier scenarios.",
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


def write_yield_multiplier_explorer(result):
    """Write a self-contained toggleable chart for the full-account scenarios."""
    payload = {
        "dates": SESSION_DATES,
        "scenarios": YIELD_FACTOR_LABELS,
        "variants": {
            variant: {
                "label": VARIANT_LABEL[variant],
                "color": VARIANT_COLOR[variant],
                "scenarios": row["yield_scenarios"],
                "factors": {
                    "us10y": row["yield_factor_us10y"],
                    "us30y": row["yield_factor_us30y"],
                    "combined": row["yield_factor_combined"],
                },
            }
            for variant, row in result.items()
        },
    }
    data = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
    html = '''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Whole Portfolio Yield Multiplier Explorer</title>
<style>
:root{color-scheme:dark;--bg:#0b1220;--panel:#141e2e;--line:#26364d;--fg:#edf2f7;--muted:#9aabc1;--blue:#38bdf8;--gold:#fbbf24}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:14px/1.5 system-ui,-apple-system,Segoe UI,sans-serif}.wrap{max-width:1240px;margin:auto;padding:26px 20px 40px}h1{font-size:28px;margin:0 0 5px}.sub,.hint{color:var(--muted)}.card{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:18px;margin-top:16px}.controls{display:flex;gap:8px;flex-wrap:wrap;margin:12px 0}.controls button{background:#101827;color:var(--fg);border:1px solid var(--line);border-radius:8px;padding:9px 12px;cursor:pointer}.controls button.on{border-color:var(--blue);background:#123146;box-shadow:0 0 0 1px var(--blue) inset}.variants label{display:inline-flex;gap:7px;align-items:center;padding:6px 10px;border:1px solid var(--line);border-radius:999px;margin:0 7px 7px 0;cursor:pointer;color:var(--muted)}.variants label.on{color:var(--fg);border-color:#50627a}.dot{width:9px;height:9px;border-radius:50%}canvas{display:block;width:100%;height:430px}.chartbox{position:relative}.tip{display:none;position:absolute;pointer-events:none;background:#070c14;border:1px solid #40516a;border-radius:8px;padding:8px 10px;font-size:12px;white-space:nowrap;z-index:2;box-shadow:0 8px 26px #0008}table{border-collapse:collapse;width:100%;font-variant-numeric:tabular-nums}th,td{padding:9px 8px;border-bottom:1px solid var(--line);text-align:right}th:first-child,td:first-child{text-align:left}th{color:#bdcce0;font-weight:600}.scroll{overflow:auto}.pill{display:inline-block;padding:3px 8px;border:1px solid var(--line);border-radius:99px;color:var(--gold)}code{color:#bfdbfe}footer{color:var(--muted);font-size:12px;margin-top:18px}
</style></head><body><main class="wrap">
<h1>Whole-Portfolio Yield Multiplier Explorer</h1>
<p class="sub">Interactive account-value comparison · Sep. 3–Oct. 23, 2026 · capital bases $830k / $920k · rates are blanket factors, not extra $10,000 positions</p>
<section class="card"><h2>Choose the blanket adjustment</h2><p class="hint">The selected factor scales the full account value. The US30Y scenario compounds on top of US10Y.</p><div class="controls" id="scenarios"></div><div class="controls" id="metrics"></div><div class="variants" id="variants"></div><div class="chartbox"><canvas id="chart"></canvas><div id="tip" class="tip"></div></div></section>
<section class="card"><h2>Oct. 23 comparison</h2><p class="hint">Each cell shows account value, USD return, and DXY-numeraire return. The no-multiplier case is the baseline.</p><div class="scroll"><table id="summary"></table></div></section>
<footer>US10Y baseline 4.865% from Sep. 10; US30Y baseline 5.350% from Sep. 15 (first logged US30Y event). Each interval compounds 1 + ((yield close − baseline) / 100) × actual calendar days / 365 using the start-of-interval close and last available close on Treasury holidays. US30Y position PnL remains separate. These yield-spread factors are not CPI inflation or Treasury total-return calculations. DXY/FX/yield inputs are local daily files whose provider and close convention are not independently verified; source map: data/active_price_source_registry_v2.csv.</footer>
</main><script>
const DATA=__DATA__;
const VARS=Object.keys(DATA.variants);let scenario="none",metric="account_value_usd",shown=new Set(VARS);
const usd=v=>"$"+Number(v).toLocaleString(undefined,{minimumFractionDigits:0,maximumFractionDigits:0});
const pct=v=>(v>=0?"+":"")+Number(v).toFixed(2)+"%";
const scenarios=document.getElementById("scenarios");
scenarios.innerHTML=Object.entries(DATA.scenarios).map(([k,label])=>`<button data-s="${k}" class="${k===scenario?"on":""}">${label}</button>`).join("");
scenarios.onclick=e=>{const b=e.target.closest("button");if(!b)return;scenario=b.dataset.s;scenarios.querySelectorAll("button").forEach(x=>x.classList.toggle("on",x===b));draw();summary();};
const metrics=document.getElementById("metrics");
metrics.innerHTML=[["account_value_usd","USD account value"],["dxy_equivalent_value","DXY-equivalent account value"]].map(([k,l])=>`<button data-m="${k}" class="${k===metric?"on":""}">${l}</button>`).join("");
metrics.onclick=e=>{const b=e.target.closest("button");if(!b)return;metric=b.dataset.m;metrics.querySelectorAll("button").forEach(x=>x.classList.toggle("on",x===b));draw();};
const ve=document.getElementById("variants");ve.innerHTML=VARS.map(v=>`<label class="on" data-v="${v}"><span class="dot" style="background:${DATA.variants[v].color}"></span>${DATA.variants[v].label}</label>`).join("");
ve.onclick=e=>{const l=e.target.closest("label");if(!l)return;const v=l.dataset.v;if(shown.has(v)&&shown.size>1){shown.delete(v);l.classList.remove("on")}else{shown.add(v);l.classList.add("on")}draw();};
const canvas=document.getElementById("chart"),ctx=canvas.getContext("2d"),tip=document.getElementById("tip");let geom;
function fmtAxis(v){return metric==="account_value_usd"?"$"+(v/1000000).toFixed(2)+"m":v.toFixed(0)}
function draw(){const ratio=devicePixelRatio||1,w=canvas.clientWidth,h=430;canvas.width=w*ratio;canvas.height=h*ratio;ctx.setTransform(ratio,0,0,ratio,0,0);ctx.clearRect(0,0,w,h);const L=78,R=20,T=18,B=48,pw=w-L-R,ph=h-T-B;let vals=[];for(const v of shown)vals.push(...DATA.variants[v].scenarios[scenario][metric]);let lo=Math.min(...vals),hi=Math.max(...vals);if(hi===lo){hi+=1;lo-=1}const pad=(hi-lo)*.08;lo-=pad;hi+=pad;ctx.font="11px system-ui";ctx.strokeStyle="#26364d";ctx.fillStyle="#9aabc1";ctx.lineWidth=1;for(let j=0;j<=5;j++){const y=T+ph*j/5,val=hi-(hi-lo)*j/5;ctx.beginPath();ctx.moveTo(L,y);ctx.lineTo(w-R,y);ctx.stroke();ctx.textAlign="right";ctx.fillText(fmtAxis(val),L-9,y+4)}for(let j=0;j<6;j++){const i=Math.round((DATA.dates.length-1)*j/5),x=L+pw*j/5;ctx.textAlign="center";ctx.fillText(DATA.dates[i].slice(5),x,h-18)}for(const v of shown){const a=DATA.variants[v],series=a.scenarios[scenario][metric];ctx.strokeStyle=a.color;ctx.lineWidth=2.4;ctx.beginPath();series.forEach((val,i)=>{const x=L+pw*i/(series.length-1),y=T+ph*(hi-val)/(hi-lo);i?ctx.lineTo(x,y):ctx.moveTo(x,y)});ctx.stroke()}geom={L,R,T,B,pw,ph,lo,hi,w,h};}
function summary(){const head=`<thead><tr><th>Model</th>${Object.entries(DATA.scenarios).map(([,l])=>`<th>${l}</th>`).join("")}</tr></thead>`;const rows=VARS.map(v=>{const x=DATA.variants[v];return `<tr><td><span class="dot" style="display:inline-block;background:${x.color};margin-right:7px"></span>${x.label}</td>${Object.keys(DATA.scenarios).map(s=>{const d=x.scenarios[s],i=d.account_value_usd.length-1;return `<td>${usd(d.account_value_usd[i])}<br><small>${pct(d.usd_return_pct[i])} USD · ${pct(d.dxy_return_pct[i])} DXY</small></td>`}).join("")}</tr>`}).join("");document.getElementById("summary").innerHTML=head+`<tbody>${rows}</tbody>`;}
canvas.addEventListener("mousemove",e=>{if(!geom)return;const r=canvas.getBoundingClientRect(),x=e.clientX-r.left,idx=Math.max(0,Math.min(DATA.dates.length-1,Math.round((x-geom.L)/geom.pw*(DATA.dates.length-1))));const lines=[`<b>${DATA.dates[idx]}</b>`];for(const v of shown){const a=DATA.variants[v],d=a.scenarios[scenario],f=metric==="account_value_usd"?d.account_value_usd[idx]:d.dxy_equivalent_value[idx],m= scenario==="none"?1:(scenario==="us10y"?a.factors.us10y[idx]:a.factors.combined[idx]);lines.push(`<span style="color:${a.color}">●</span> ${a.label}: ${usd(f)} · factor ${m.toFixed(6)}`)}tip.innerHTML=lines.join("<br>");tip.style.display="block";tip.style.left=Math.min(x+12,geom.w-310)+"px";tip.style.top="18px";});
canvas.addEventListener("mouseleave",()=>tip.style.display="none");window.addEventListener("resize",draw);draw();summary();
</script></body></html>'''
    YIELD_EXPLORER.write_text(html.replace("__DATA__", data), encoding="utf-8")
    return YIELD_EXPLORER


def build_report(dxy, fx, us30y, result):
    lines = [
        "# Whole-Portfolio DXY Numeraire — Daily Comparison",
        "",
        "The whole-book base PnL includes realized and open unrealized PnL (including FX and the separate US30Y trade marks), but excludes yield multipliers. The US10Y and US30Y blanket factors are applied to full account value only in the explicit scenarios below; neither yield is treated as a new $10,000 lot. DXY remains a separate whole-book numeraire, not a position.",
        "",
        "[Open the interactive yield-multiplier scenario explorer](Whole%20Portfolio%20Yield%20Multiplier%20Explorer.html) to toggle between no factor, US10Y only, and US10Y compounded with US30Y.",
        "",
        "![DXY Close vs. Whole-Portfolio PnL in Dollars](Charts/performance/17-dxy-close-vs-whole-portfolio-pnl-usd.png)",
        "",
        "![Whole-portfolio unrealized PnL and USD/DXY returns](Charts/performance/16-whole-portfolio-dxy-vs-usd-pnl.png)",
        "",
        "## Oct. 23 Terminal Results",
        "",
        "| Variant | Capital basis | Open unrealized PnL (USD) | Realized PnL (USD) | Base PnL (no yield factors) | Base USD return | DXY-equivalent account value | DXY-numeraire return |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    last = len(SESSION_DATES) - 1
    for variant in VARIANTS:
        row = result[variant]
        lines.append(
            f"| **{VARIANT_LABEL[variant]}** | ${CAPITAL_BASIS_USD[variant]:,.0f} | "
            f"${row['unrealized_usd'][last]:+,.2f} | ${row['realized_usd'][last]:+,.2f} | "
            f"${row['total_pnl_usd'][last]:+,.2f} | "
            f"{row['usd_return_pct'][last]:+.3f}% | {row['dxy_equivalent_value'][last]:,.2f} DXY-eq units | "
            f"{row['dxy_return_pct'][last]:+.3f}% |"
        )
    lines.extend([
        "",
        "## Toggleable blanket yield-multiplier scenarios",
        "",
        "The base case is the portfolio account value without either yield multiplier. The US10Y case scales the full account value by its compounded US10Y excess-yield factor. The combined case multiplies that factor by the independently compounded US30Y excess-yield factor (`M10Y × M30Y`). In each case, the portfolio's starting capital is scaled as requested; scenario PnL is adjusted account value minus the original capital basis.",
        "",
        f"- US10Y baseline: `{BASELINE_PCT:.3f}%` from `{US10Y_START_DATE}`. US30Y baseline: `{US30Y_MULTIPLIER_BASELINE_PCT:.3f}%` from `{US30Y_MULTIPLIER_START}` (first logged US30Y event).",
        "- Each elapsed interval uses the prior session's yield close and actual calendar days / 365; Treasury non-session dates carry the latest available close. These are yield-derived scenario factors, not CPI inflation or Treasury total-return estimates.",
        "- The separate US30Y SHORT/LONG trade PnL remains in the portfolio base as a marked position. The US30Y blanket factor is an additional whole-account scenario and does not create another $10,000 position.",
        "",
        "| Variant | No multiplier: account / USD return / DXY return | US10Y: account / USD return / DXY return | US10Y × US30Y: account / USD return / DXY return |",
        "|---|---:|---:|---:|",
    ])
    for variant in VARIANTS:
        row = result[variant]
        cells = []
        for scenario in YIELD_FACTOR_SCENARIOS:
            values = row["yield_scenarios"][scenario]
            cells.append(
                f"${values['account_value_usd'][last]:,.2f} / "
                f"{values['usd_return_pct'][last]:+.3f}% / "
                f"{values['dxy_return_pct'][last]:+.3f}%"
            )
        lines.append(f"| **{VARIANT_LABEL[variant]}** | " + " | ".join(cells) + " |")
    lines.extend([
        "",
        f"Interactive toggle and session-level scenario data: [`{YIELD_EXPLORER.name}`]({YIELD_EXPLORER.name}), [`{YIELD_SCENARIO_CSV.name}`](data/{YIELD_SCENARIO_CSV.name}), and [`{YIELD_SCENARIO_SUMMARY_CSV.name}`](data/{YIELD_SCENARIO_SUMMARY_CSV.name}).",
    ])
    eur_base = fx["EURUSD"][FX_ENTRIES["EURUSD"]["date"]]
    jpy_base = fx["JPYUSD"][FX_ENTRIES["JPYUSD"]["date"]]
    lines.extend([
        "",
        "## DXY and FX Basis",
        "",
        f"- DXY daily closes run from `{SESSION_DATES[0]}` (`{dxy[SESSION_DATES[0]]:.2f}`) through `{TERMINAL_DATE}` (`{dxy[TERMINAL_DATE]:.2f}`). The Oct. 23 close of 102.10 is used for the new endpoint; the prior Oct. 22 close of 102.22 remains preserved in the daily series and Oct. 22 audit file.",
        "- **Input provenance:** DXY, EUR/USD, JPY/USD, US10Y, and US30Y use the existing local daily input files; their provider and candle/close convention are not independently verified. The source map and proxy limitations are in [`data/active_price_source_registry_v2.csv`](data/active_price_source_registry_v2.csv). These local inputs were retained, not externally refreshed.",
        "- **Energy marks:** the core logged Brent/USOIL positions use exact user-provided BlackBull Brent Cash and TVC:USOIL EOD values from their first active-position dates; only pre-entry context remains on the Yahoo futures proxies. The separate daily 10-unit oil-desk accumulation is in [`Oil Desk EOD Accumulation Hypothetical.md`](Oil%20Desk%20EOD%20Accumulation%20Hypothetical.md) and is not included in the four account bases or yield-factor scenarios.",
        "- FX, DXY, and yield series remain local and unverified; the user-provided energy marks are not treated as DXY/FX or yield data.",
        "- The yield multiplier is a yield-spread scenario, not CPI inflation or a Treasury total-return estimate. A literal inflation-adjusted PnL series would require a specified CPI index and convention.",
        f"- EUR/USD PnL uses the uploaded daily close on its entry date as its cost basis: `{FX_ENTRIES['EURUSD']['date']}` close `{eur_base}`. The original chart quote `1.15388` remains in the trade log as source evidence; the graph does not use it as the PnL basis, per your instruction.",
        f"- JPY/USD PnL uses the uploaded daily close on its entry date as its cost basis: `{FX_ENTRIES['JPYUSD']['date']}` close `{jpy_base}`. The original chart quote `0.010160` remains in the trade log as source evidence; the graph does not use it as the PnL basis, per your instruction.",
        "- DXY-equivalent account value is computed as `USD account value ÷ daily DXY close`; returns are normalized to the Sep. 3 DXY-equivalent starting value. The USD capital bases are the $830,000 / $920,000 portfolio amounts you specified.",
        "- The DXY LONG log entry is retained as historical reference evidence, but this comparison does not treat it as an additional $10,000 position or add separate DXY-trade PnL.",
        "",
        "## PnL, Multiplier, and Position Treatment",
        "",
        "- Daily EUR/USD and JPY/USD unrealized PnL is calculated from the entry-date daily close, then marked to each uploaded daily close at $10,000 standard notional per position.",
        "- The Sep. 15 US30Y SHORT and Oct. 23 US30Y LONG remain separate marked $10,000 positions; the Oct. 23 LONG uses its 5.311% log entry and Oct. 23 5.43% close, so it contributes only from Oct. 23. The US30Y blanket factor is separate from these position marks. The Oct. 23 ORCL LONG and fifth LCID LONG remain included.",
        "- The old additive US10Y carry is retained in the daily CSV as a legacy reference only; it is not included in base PnL or any new scenario. The active whole-account adjustment is the compounded multiplier shown above. This prevents treating US10Y as a $10,000 position or layering the old carry on top of the new factor.",
        "- US10Y positions are rate references, not independent yield-quote PnL rows. For Treasury holidays, the last supplied daily close is carried forward; the source date is retained in the daily export. DXY itself remains the whole-book numeraire.",
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
        "terminal_us30y_long_unrealized_pnl_usd", "terminal_legacy_us10y_carry_reference_usd",
        "terminal_total_pnl_usd", "usd_return_pct",
        "terminal_dxy_equivalent_account_value", "terminal_dxy_equivalent_pnl",
        "dxy_numeraire_return_pct", "terminal_us10y_factor", "terminal_us30y_factor",
        "terminal_combined_factor", "eurusd_entry_close_basis", "eurusd_terminal_close",
        "eurusd_terminal_unrealized_pnl_usd", "jpyusd_entry_close_basis",
        "jpyusd_terminal_close", "jpyusd_terminal_unrealized_pnl_usd",
        "none_terminal_account_value_usd", "none_terminal_pnl_usd", "none_terminal_usd_return_pct",
        "none_terminal_dxy_equivalent_value", "none_terminal_dxy_return_pct",
        "us10y_terminal_account_value_usd", "us10y_terminal_pnl_usd", "us10y_terminal_usd_return_pct",
        "us10y_terminal_dxy_equivalent_value", "us10y_terminal_dxy_return_pct",
        "us10y_us30y_terminal_account_value_usd", "us10y_us30y_terminal_pnl_usd",
        "us10y_us30y_terminal_usd_return_pct", "us10y_us30y_terminal_dxy_equivalent_value",
        "us10y_us30y_terminal_dxy_return_pct",
    ]
    with SUMMARY_CSV.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
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
                "terminal_us30y_long_unrealized_pnl_usd": result[variant]["us30y_long_unrealized_usd"][last],
                "terminal_legacy_us10y_carry_reference_usd": result[variant]["legacy_us10y_carry_reference_usd"][last],
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
                "terminal_us10y_factor": result[variant]["yield_factor_us10y"][last],
                "terminal_us30y_factor": result[variant]["yield_factor_us30y"][last],
                "terminal_combined_factor": result[variant]["yield_factor_combined"][last],
                **{
                    f"{scenario}_terminal_{field}": values[last]
                    for scenario, scenario_values in result[variant]["yield_scenarios"].items()
                    for field, values in scenario_values.items()
                },
            })


def main():
    dxy, fx, us30y, us30y_source_dates, core, result = build_daily_series()
    write_daily_csv(dxy, fx, us30y, us30y_source_dates, core, result)
    write_summary_csv(result, fx, dxy)
    write_yield_scenario_csv(result, dxy)
    write_yield_scenario_summary_csv(result)
    write_yield_multiplier_explorer(result)
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
