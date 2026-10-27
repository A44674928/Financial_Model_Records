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
LIGHT_INPUT_CSV = ROOT / "data" / "strategy_sidecar_comparison_daily_v1.csv"
DXY_SIDE_INPUT = ROOT / "data" / "dxy_currency_desk_sidecar_daily_20261026.csv"
ENERGY_SIDE_INPUT = ROOT / "data" / "tradingview_energy_sidecar_daily_20261026.csv"
OUTPUT_CSV = ROOT / "data" / "the_one_model_vs_winning_model_v1.csv"
OUTPUT_JSON = ROOT / "data" / "the_one_model_vs_winning_model_v1_summary.json"
OUTPUT_CHART = ROOT / "Charts" / "superstructure" / "the-one-model-vs-winning-model.png"
OUTPUT_1M_CHART = ROOT / "Charts" / "superstructure" / "the-winning-model-1m-open-notional.png"
OUTPUT_LIGHT_CHART = ROOT / "Charts" / "superstructure" / "twm-1m-light.png"
OUTPUT_MAX_CHART = ROOT / "Charts" / "superstructure" / "twm-1m-max.png"
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
    with LIGHT_INPUT_CSV.open(newline="", encoding="utf-8") as handle:
        light_rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError(f"No daily rows in {INPUT_CSV}")
    if len(light_rows) != len(rows) or [row["date"] for row in light_rows] != [row["date"] for row in rows]:
        raise ValueError("Light-model input dates must align exactly with the winner comparison sessions")
    with DXY_SIDE_INPUT.open(newline="", encoding="utf-8") as handle:
        dxy_one_rows = [row for row in csv.DictReader(handle) if dec(row["unit_size_u"]) == Decimal("1")]
    dxy_one_by_date = {row["date"]: row for row in dxy_one_rows}
    if len(dxy_one_by_date) != len(dxy_one_rows):
        raise ValueError("Duplicate 1U DXY sidecar rows prevent clean no-DXY reconstruction")
    if set(dxy_one_by_date) != {row["date"] for row in rows[1:]}:
        raise ValueError("Expected the chart-directed 1U DXY sidecar on every session after the opening row")
    with ENERGY_SIDE_INPUT.open(newline="", encoding="utf-8") as handle:
        energy_ten_rows = [row for row in csv.DictReader(handle) if dec(row["unit_size_u"]) == Decimal("10")]
    energy_ten_by_date = {}
    seen_energy_ticker_dates = set()
    for row in energy_ten_rows:
        key = (row["ticker"], row["date"])
        if key in seen_energy_ticker_dates:
            raise ValueError(f"Duplicate 10U energy sidecar row: {key}")
        seen_energy_ticker_dates.add(key)
        totals = energy_ten_by_date.setdefault(row["date"], {
            "pnl": Decimal("0"), "added": Decimal("0"), "open": Decimal("0")
        })
        totals["pnl"] += dec(row["daily_buys_unrealized_pnl_usd"])
        totals["added"] += dec(row["cumulative_daily_buy_notional_usd"])
        totals["open"] += dec(row["cumulative_daily_buy_notional_usd"])
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
    winner_open_terminal = dec(rows[-1][winner_open_key])
    if winner_open_terminal <= 0:
        raise ValueError("Cannot size a $1M open-notional model from a zero terminal open position")
    million_open_scale = Decimal("1000000.00") / winner_open_terminal
    light_prefix = "V3A_core_plus_V3A_force_1u"
    light_pnl_key = f"{light_prefix}_pnl_usd"
    light_added_key = f"{light_prefix}_cumulative_notional_usd"
    light_open_key = f"{light_prefix}_open_notional_usd"
    light_terminal_open = dec(light_rows[-1][light_open_key])
    if light_terminal_open <= 0:
        raise ValueError("Cannot size TWM_1M_LIGHT from zero terminal gross open notional")
    light_scale = Decimal("1000000.00") / light_terminal_open

    current_rebuild_rows = []
    for light_source in light_rows:
        day = light_source["date"]
        dxy = dxy_one_by_date.get(day)
        energy = energy_ten_by_date.get(day, {"pnl": Decimal("0"), "added": Decimal("0"), "open": Decimal("0")})
        dxy_pnl = dec(dxy["daily_investment_unrealized_pnl_usd"]) if dxy else Decimal("0")
        dxy_added = dec(dxy["cumulative_notional_added_usd"]) if dxy else Decimal("0")
        dxy_open = dec(dxy["open_notional_usd"]) if dxy else Decimal("0")
        current_rebuild_rows.append({
            "date": day,
            "pnl": dec(light_source[light_pnl_key]) - dxy_pnl + energy["pnl"],
            "added": dec(light_source[light_added_key]) - dxy_added + energy["added"],
            "open": dec(light_source[light_open_key]) - dxy_open + energy["open"],
        })
    current_terminal_open = current_rebuild_rows[-1]["open"]
    if current_terminal_open <= 0:
        raise ValueError("Cannot size current-data V3A/10U-energy replay from zero gross open notional")
    current_scale = Decimal("1000000.00") / current_terminal_open

    output_rows = []
    dates = []
    one_pnl, scaled_pnl, million_open_pnl, light_pnl, current_pnl = [], [], [], [], []
    for source, light_source, current_source in zip(rows, light_rows, current_rebuild_rows):
        day = source["date"]
        dates.append(day)
        base_winner_pnl = dec(source[winner_pnl_key])
        base_winner_added = dec(source[winner_added_key])
        base_winner_open = dec(source[winner_open_key])
        equal_pnl = (base_winner_pnl * scale).quantize(CENT)
        equal_added = (base_winner_added * scale).quantize(CENT)
        equal_open = (base_winner_open * scale).quantize(CENT)
        million_pnl = (base_winner_pnl * million_open_scale).quantize(CENT)
        million_added = (base_winner_added * million_open_scale).quantize(CENT)
        million_open = (base_winner_open * million_open_scale).quantize(CENT)
        light_base_pnl = dec(light_source[light_pnl_key])
        light_base_added = dec(light_source[light_added_key])
        light_base_open = dec(light_source[light_open_key])
        light_scaled_pnl = (light_base_pnl * light_scale).quantize(CENT)
        light_scaled_added = (light_base_added * light_scale).quantize(CENT)
        light_scaled_open = (light_base_open * light_scale).quantize(CENT)
        current_scaled_pnl = (current_source["pnl"] * current_scale).quantize(CENT)
        current_scaled_added = (current_source["added"] * current_scale).quantize(CENT)
        current_scaled_open = (current_source["open"] * current_scale).quantize(CENT)
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
            "winning_model_1m_open_pnl_usd": f"{million_pnl:.2f}",
            "winning_model_1m_open_cumulative_gross_notional_added_usd": f"{million_added:.2f}",
            "winning_model_1m_open_gross_open_notional_usd": f"{million_open:.2f}",
            "winning_model_1m_open_pnl_to_gross_added_pct": f"{ratio_pct(million_pnl, million_added):.6f}",
            "twm_1m_light_pnl_usd": f"{light_scaled_pnl:.2f}",
            "twm_1m_light_cumulative_gross_notional_added_usd": f"{light_scaled_added:.2f}",
            "twm_1m_light_gross_open_notional_usd": f"{light_scaled_open:.2f}",
            "twm_1m_light_pnl_to_gross_added_pct": f"{ratio_pct(light_scaled_pnl, light_scaled_added):.6f}",
            "twm_1m_max_pnl_usd": f"{current_scaled_pnl:.2f}",
            "twm_1m_max_cumulative_gross_notional_added_usd": f"{current_scaled_added:.2f}",
            "twm_1m_max_gross_open_notional_usd": f"{current_scaled_open:.2f}",
            "twm_1m_max_pnl_to_gross_added_pct": f"{ratio_pct(current_scaled_pnl, current_scaled_added):.6f}",
        })
        one_pnl.append(one)
        scaled_pnl.append(equal_pnl)
        million_open_pnl.append(million_pnl)
        light_pnl.append(light_scaled_pnl)
        current_pnl.append(current_scaled_pnl)

    last = output_rows[-1]
    winner_original_dd = _max_drawdown(
        [dec(row[winner_pnl_key]) for row in rows], dates
    )
    winner_scaled_dd = _max_drawdown(scaled_pnl, dates)
    million_open_dd = _max_drawdown(million_open_pnl, dates)
    million_open_peak = max(output_rows, key=lambda row: dec(row["winning_model_1m_open_gross_open_notional_usd"]))
    light_dd = _max_drawdown(light_pnl, dates)
    light_peak = max(output_rows, key=lambda row: dec(row["twm_1m_light_gross_open_notional_usd"]))
    current_dd = _max_drawdown(current_pnl, dates)
    current_peak = max(output_rows, key=lambda row: dec(row["twm_1m_max_gross_open_notional_usd"]))
    one_dd = _max_drawdown(one_pnl, dates)
    equal_pnl = dec(last["winning_model_equal_gross_pnl_usd"])
    million_open_terminal_pnl = dec(last["winning_model_1m_open_pnl_usd"])
    light_terminal_pnl = dec(last["twm_1m_light_pnl_usd"])
    current_terminal_pnl = dec(last["twm_1m_max_pnl_usd"])
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
        "winning_model_1m_open_version_name": "TWM_1M_FULL",
        "winning_model_1m_open_notional_target_usd": "1000000.00",
        "winning_model_1m_open_scale_factor": f"{million_open_scale:.12f}",
        "winning_model_1m_open_scale_factor_exact": str(million_open_scale),
        "winning_model_1m_open_combined_dxy_units_per_active_eod": f"{Decimal('11') * million_open_scale:.6f}",
        "winning_model_1m_open_terminal_pnl_usd": f"{million_open_terminal_pnl:.2f}",
        "winning_model_1m_open_cumulative_gross_notional_added_usd": last["winning_model_1m_open_cumulative_gross_notional_added_usd"],
        "winning_model_1m_open_gross_open_notional_usd": last["winning_model_1m_open_gross_open_notional_usd"],
        "winning_model_1m_open_pnl_to_gross_added_pct": last["winning_model_1m_open_pnl_to_gross_added_pct"],
        "winning_model_1m_open_max_gross_open_notional_usd": million_open_peak["winning_model_1m_open_gross_open_notional_usd"],
        "winning_model_1m_open_max_gross_open_notional_date": million_open_peak["date"],
        "winning_model_1m_open_max_peak_to_trough_pnl_drawdown_usd": f"{million_open_dd['amount']:.2f}",
        "winning_model_1m_open_sizing_basis": "The original winning portfolio is scaled so its terminal 2026-10-26 gross open notional equals $1,000,000.00. The same scale is applied uniformly to daily PnL, additions, and open notional; this is not a $1M PnL target or evidence of account capital/future capacity.",
        "twm_1m_light_version_name": "TWM_1M_LIGHT",
        "twm_1m_light_construction": "V3A core plus the V3A-specific 1U/EOD force model from the strategy-sidecar comparison; keeps the chart-directed core DXY sleeve, excludes the 10U/DAY DXY add-on and energy daily-buy sidecar. Includes chart-post, ATS, manual, and user-reported core events present in the source replay, all uniformly scaled. Actual executions are unverified.",
        "twm_1m_light_source_portfolio": "V3A_core_plus_V3A_force_1u",
        "twm_1m_light_terminal_open_notional_target_usd": "1000000.00",
        "twm_1m_light_scale_factor": f"{light_scale:.12f}",
        "twm_1m_light_scale_factor_exact": str(light_scale),
        "twm_1m_light_source_terminal_pnl_usd": f"{dec(light_rows[-1][light_pnl_key]):.2f}",
        "twm_1m_light_source_cumulative_gross_notional_added_usd": f"{dec(light_rows[-1][light_added_key]):.2f}",
        "twm_1m_light_source_gross_open_notional_usd": f"{light_terminal_open:.2f}",
        "twm_1m_light_terminal_pnl_usd": f"{light_terminal_pnl:.2f}",
        "twm_1m_light_cumulative_gross_notional_added_usd": last["twm_1m_light_cumulative_gross_notional_added_usd"],
        "twm_1m_light_gross_open_notional_usd": last["twm_1m_light_gross_open_notional_usd"],
        "twm_1m_light_pnl_to_gross_added_pct": last["twm_1m_light_pnl_to_gross_added_pct"],
        "twm_1m_light_max_gross_open_notional_usd": light_peak["twm_1m_light_gross_open_notional_usd"],
        "twm_1m_light_max_gross_open_notional_date": light_peak["date"],
        "twm_1m_light_max_peak_to_trough_pnl_drawdown_usd": f"{light_dd['amount']:.2f}",
        "twm_1m_light_max_drawdown": {
            "peak_date": light_dd["peak_date"], "peak_pnl_usd": f"{light_dd['peak_pnl']:.2f}",
            "trough_date": light_dd["trough_date"], "trough_pnl_usd": f"{light_dd['trough_pnl']:.2f}",
        },
        "twm_1m_max_version_name": "TWM_1M_MAX",
        "twm_1m_max_construction": "Current 37-session V3A core plus V3A-specific 1U/EOD force model and the 10U/DAY-per-active-ticker energy sidecar; remove the integrated chart-directed 1U/DAY DXY sleeve and omit the 10U/DAY DXY add-on to match the archived Oct 23 comparison scope. Uses current core trade log and TradingView-only energy marks, including modeled ATS/manual/user-reported core events where present; events are proportionally scaled and not verified brokerage fills.",
        "twm_1m_max_source_terminal_pnl_usd": f"{current_rebuild_rows[-1]['pnl']:.2f}",
        "twm_1m_max_source_cumulative_gross_notional_added_usd": f"{current_rebuild_rows[-1]['added']:.2f}",
        "twm_1m_max_source_gross_open_notional_usd": f"{current_terminal_open:.2f}",
        "twm_1m_max_scale_factor": f"{current_scale:.12f}",
        "twm_1m_max_scale_factor_exact": str(current_scale),
        "twm_1m_max_terminal_pnl_usd": f"{current_terminal_pnl:.2f}",
        "twm_1m_max_cumulative_gross_notional_added_usd": last["twm_1m_max_cumulative_gross_notional_added_usd"],
        "twm_1m_max_gross_open_notional_usd": last["twm_1m_max_gross_open_notional_usd"],
        "twm_1m_max_pnl_to_gross_added_pct": last["twm_1m_max_pnl_to_gross_added_pct"],
        "twm_1m_max_max_gross_open_notional_usd": current_peak["twm_1m_max_gross_open_notional_usd"],
        "twm_1m_max_max_gross_open_notional_date": current_peak["date"],
        "twm_1m_max_max_peak_to_trough_pnl_drawdown_usd": f"{current_dd['amount']:.2f}",
        "twm_1m_cash_debit_assumption": "Per user instruction, all positions are fully paid in cash with no leverage, financing, or borrowed funds. Under this simplified model, the $1,000,000 gross-open target is treated as the fully funded capital base; cumulative gross additions are turnover/reused capital, not cumulative deposits.",
        "twm_1m_fully_funded_capital_base_usd": "1000000.00",
        "twm_1m_full_pnl_on_funded_capital_pct": f"{ratio_pct(million_open_terminal_pnl, Decimal('1000000')):.6f}",
        "twm_1m_light_pnl_on_funded_capital_pct": f"{ratio_pct(light_terminal_pnl, Decimal('1000000')):.6f}",
        "twm_1m_max_pnl_on_funded_capital_pct": f"{ratio_pct(current_terminal_pnl, Decimal('1000000')):.6f}",
        "twm_1m_max_peak_funded_notional_usd": current_peak["twm_1m_max_gross_open_notional_usd"],
        "winning_model_equal_gross_terminal_pnl_usd": f"{equal_pnl:.2f}",
        "winning_model_1m_open_max_drawdown": {
            "peak_date": million_open_dd["peak_date"], "peak_pnl_usd": f"{million_open_dd['peak_pnl']:.2f}",
            "trough_date": million_open_dd["trough_date"], "trough_pnl_usd": f"{million_open_dd['trough_pnl']:.2f}",
        },
        "winning_model_equal_gross_cumulative_gross_notional_added_usd": last["winning_model_equal_gross_cumulative_notional_added_usd"],
        "winning_model_equal_gross_gross_open_notional_usd": last["winning_model_equal_gross_open_notional_usd"],
        "winning_model_equal_gross_pnl_to_gross_added_pct": last["winning_model_equal_gross_pnl_to_gross_added_pct"],
        "winning_model_equal_gross_max_peak_to_trough_pnl_drawdown_usd": f"{winner_scaled_dd['amount']:.2f}",
        "equal_gross_terminal_pnl_difference_winner_minus_one_model_usd": f"{equal_pnl - one_pnl_terminal:.2f}",
        "equal_gross_deployed_notional_ratio_difference_percentage_points": f"{equal_ratio - one_ratio:.6f}",
        "equal_gross_winner_selection_caveat": "The winning constituent is selected from the same full historical period being evaluated. This ex-post selection introduces look-ahead/selection bias and is not out-of-sample validation.",
        "scaling_caveat": "The equal-gross winning-model curve multiplies every daily PnL, cumulative addition, and open-notional amount by one constant. It is a mathematical normalization, not evidence that scaled positions could be executed at the same prices or costs. Margin, capacity, impact, financing, and correlated concentration are not modeled.",
        "caveat": "Historical hypothetical paper-model outputs, not verified brokerage executions. Per user instruction, the 1M scenarios use a fully funded debit-account capital base equal to $1,000,000 of gross open notional, with no leverage or financing; PnL on that base is reported separately from PnL divided by cumulative gross additions. Costs and actual fills are not modeled or verified.",
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


def write_million_open_chart(result, rows):
    OUTPUT_1M_CHART.parent.mkdir(parents=True, exist_ok=True)
    dates = [datetime.strptime(row["date"], "%Y-%m-%d") for row in rows]
    pnl = [float(row["winning_model_1m_open_pnl_usd"]) for row in rows]
    added = [float(row["winning_model_1m_open_cumulative_gross_notional_added_usd"]) for row in rows]
    opened = [float(row["winning_model_1m_open_gross_open_notional_usd"]) for row in rows]

    bg, panel, grid = "#0b1220", "#111c2e", "#273449"
    fg, muted, teal, violet, amber = "#f8fafc", "#a8b6ca", "#2dd4bf", "#c084fc", "#fbbf24"
    fig, axes = plt.subplots(2, 1, figsize=(13.5, 7.8), sharex=True,
                             gridspec_kw={"height_ratios": [1, 1.1]})
    fig.patch.set_facecolor(bg)
    for ax in axes:
        ax.set_facecolor(panel)
        ax.grid(True, color=grid, linewidth=0.75, alpha=0.85)
        ax.set_axisbelow(True)
        ax.tick_params(colors=muted, labelsize=9)
        for spine in ax.spines.values():
            spine.set_color(grid)

    ax = axes[0]
    ax.plot(dates, pnl, color=teal, linewidth=2.2, label="Cumulative modeled PnL")
    ax.axhline(0, color=muted, linewidth=0.9, linestyle="--")
    ax.set_ylabel("Modeled PnL (USD)", color=muted)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda value, _: f"${value / 1000:.0f}K"))
    ax.legend(facecolor=panel, edgecolor=grid, labelcolor=fg, fontsize=8.5, loc="upper left")
    ax.set_title("TWM_1M_FULL — $1M current-open-notional sizing",
                 color=fg, fontsize=14, fontweight="bold", loc="left", pad=12)
    ax.annotate(f"Terminal PnL  {dollars(result['winning_model_1m_open_terminal_pnl_usd'])}",
                (dates[-1], pnl[-1]), xytext=(-8, 9), textcoords="offset points",
                color=teal, fontsize=8.5, ha="right", fontweight="bold")

    ax = axes[1]
    ax.plot(dates, added, color=violet, linewidth=2.0,
            label="Cumulative gross notional added")
    ax.plot(dates, opened, color=amber, linewidth=2.0,
            label="Gross open notional")
    ax.axhline(1_000_000, color=muted, linewidth=1.0, linestyle=":",
               label="$1M gross-open target")
    ax.set_ylabel("Gross notional (USD)", color=muted)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda value, _: f"${value / 1e6:.1f}M"))
    ax.set_xlabel("Session (MST)", color=muted)
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    ax.legend(facecolor=panel, edgecolor=grid, labelcolor=fg, fontsize=8.3, loc="upper left", ncol=2)
    fig.autofmt_xdate(rotation=0, ha="center")
    fig.text(
        0.5, 0.012,
        f"{result['period_start']}–{result['period_end']} · original winner uniformly scaled to $1M terminal gross open notional · "
        "hypothetical historical replay · not account equity or verified execution",
        color=muted, fontsize=7.7, ha="center",
    )
    fig.tight_layout(rect=(0.015, 0.045, 0.99, 0.985))
    fig.savefig(OUTPUT_1M_CHART, dpi=170, facecolor=bg, bbox_inches="tight")
    plt.close(fig)


def write_light_chart(result, rows):
    OUTPUT_LIGHT_CHART.parent.mkdir(parents=True, exist_ok=True)
    dates = [datetime.strptime(row["date"], "%Y-%m-%d") for row in rows]
    pnl = [float(row["twm_1m_light_pnl_usd"]) for row in rows]
    added = [float(row["twm_1m_light_cumulative_gross_notional_added_usd"]) for row in rows]
    opened = [float(row["twm_1m_light_gross_open_notional_usd"]) for row in rows]

    bg, panel, grid = "#0b1220", "#111c2e", "#273449"
    fg, muted, teal, violet, amber = "#f8fafc", "#a8b6ca", "#2dd4bf", "#c084fc", "#fbbf24"
    fig, axes = plt.subplots(2, 1, figsize=(13.5, 7.8), sharex=True,
                             gridspec_kw={"height_ratios": [1, 1.1]})
    fig.patch.set_facecolor(bg)
    for ax in axes:
        ax.set_facecolor(panel)
        ax.grid(True, color=grid, linewidth=0.75, alpha=0.85)
        ax.set_axisbelow(True)
        ax.tick_params(colors=muted, labelsize=9)
        for spine in ax.spines.values():
            spine.set_color(grid)

    ax = axes[0]
    ax.plot(dates, pnl, color=teal, linewidth=2.2, label="Cumulative modeled PnL")
    ax.axhline(0, color=muted, linewidth=0.9, linestyle="--")
    ax.set_ylabel("Modeled PnL (USD)", color=muted)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda value, _: f"${value / 1000:.0f}K"))
    ax.legend(facecolor=panel, edgecolor=grid, labelcolor=fg, fontsize=8.5, loc="upper left")
    ax.set_title("TWM_1M_LIGHT — $1M current-open-notional sizing",
                 color=fg, fontsize=14, fontweight="bold", loc="left", pad=12)
    ax.annotate(f"Terminal PnL  {dollars(result['twm_1m_light_terminal_pnl_usd'])}",
                (dates[-1], pnl[-1]), xytext=(-8, 9), textcoords="offset points",
                color=teal, fontsize=8.5, ha="right", fontweight="bold")

    ax = axes[1]
    ax.plot(dates, added, color=violet, linewidth=2.0,
            label="Cumulative gross notional added")
    ax.plot(dates, opened, color=amber, linewidth=2.0,
            label="Gross open notional")
    ax.axhline(1_000_000, color=muted, linewidth=1.0, linestyle=":",
               label="$1M gross-open target")
    ax.set_ylabel("Gross notional (USD)", color=muted)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda value, _: f"${value / 1e6:.1f}M"))
    ax.set_xlabel("Session (MST)", color=muted)
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    ax.legend(facecolor=panel, edgecolor=grid, labelcolor=fg, fontsize=8.3, loc="upper left", ncol=2)
    fig.autofmt_xdate(rotation=0, ha="center")
    fig.text(
        0.5, 0.012,
        f"{result['period_start']}–{result['period_end']} · V3A core + V3A 1U/EOD · core DXY only · no energy sidecar · "
        "supplemental core events proportionally scaled · hypothetical replay",
        color=muted, fontsize=7.7, ha="center",
    )
    fig.tight_layout(rect=(0.015, 0.045, 0.99, 0.985))
    fig.savefig(OUTPUT_LIGHT_CHART, dpi=170, facecolor=bg, bbox_inches="tight")
    plt.close(fig)


def write_max_chart(result, rows):
    OUTPUT_MAX_CHART.parent.mkdir(parents=True, exist_ok=True)
    dates = [datetime.strptime(row["date"], "%Y-%m-%d") for row in rows]
    pnl = [float(row["twm_1m_max_pnl_usd"]) for row in rows]
    added = [float(row["twm_1m_max_cumulative_gross_notional_added_usd"]) for row in rows]
    opened = [float(row["twm_1m_max_gross_open_notional_usd"]) for row in rows]

    bg, panel, grid = "#0b1220", "#111c2e", "#273449"
    fg, muted, teal, violet, amber = "#f8fafc", "#a8b6ca", "#2dd4bf", "#c084fc", "#fbbf24"
    fig, axes = plt.subplots(2, 1, figsize=(13.5, 7.8), sharex=True,
                             gridspec_kw={"height_ratios": [1, 1.1]})
    fig.patch.set_facecolor(bg)
    for ax in axes:
        ax.set_facecolor(panel)
        ax.grid(True, color=grid, linewidth=0.75, alpha=0.85)
        ax.set_axisbelow(True)
        ax.tick_params(colors=muted, labelsize=9)
        for spine in ax.spines.values():
            spine.set_color(grid)

    ax = axes[0]
    ax.plot(dates, pnl, color=teal, linewidth=2.2, label="Cumulative modeled PnL")
    ax.axhline(0, color=muted, linewidth=0.9, linestyle="--")
    ax.set_ylabel("Modeled PnL (USD)", color=muted)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda value, _: f"${value / 1000:.0f}K"))
    ax.legend(facecolor=panel, edgecolor=grid, labelcolor=fg, fontsize=8.5, loc="upper left")
    ax.set_title("TWM_1M_MAX — refreshed old-scope replay",
                 color=fg, fontsize=14, fontweight="bold", loc="left", pad=12)
    ax.annotate(f"Terminal PnL  {dollars(result['twm_1m_max_terminal_pnl_usd'])}",
                (dates[-1], pnl[-1]), xytext=(-8, 9), textcoords="offset points",
                color=teal, fontsize=8.5, ha="right", fontweight="bold")

    ax = axes[1]
    ax.plot(dates, added, color=violet, linewidth=2.0,
            label="Cumulative gross notional added")
    ax.plot(dates, opened, color=amber, linewidth=2.0,
            label="Gross open notional")
    ax.axhline(1_000_000, color=muted, linewidth=1.0, linestyle=":",
               label="$1M gross-open target")
    ax.set_ylabel("Gross notional (USD)", color=muted)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda value, _: f"${value / 1e6:.1f}M"))
    ax.set_xlabel("Session (MST)", color=muted)
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    ax.legend(facecolor=panel, edgecolor=grid, labelcolor=fg, fontsize=8.3, loc="upper left", ncol=2)
    fig.autofmt_xdate(rotation=0, ha="center")
    fig.text(
        0.5, 0.012,
        f"{result['period_start']}–{result['period_end']} · V3A core + V3A 1U/EOD + 10U energy · no DXY · "
        "current TradingView marks · hypothetical replay",
        color=muted, fontsize=7.7, ha="center",
    )
    fig.tight_layout(rect=(0.015, 0.045, 0.99, 0.985))
    fig.savefig(OUTPUT_MAX_CHART, dpi=170, facecolor=bg, bbox_inches="tight")
    plt.close(fig)


def write_report(result):
    factor = dec(result["equal_gross_scale_factor"])
    million_open_factor = dec(result["winning_model_1m_open_scale_factor"])
    text = f'''# THE ONE MODEL vs THE WINNING MODEL

> **Historical hypothetical comparison · TradingView-only benchmark through {result['period_end']} · {result['sessions']} sessions.** This compares the 32-portfolio THE ONE MODEL aggregate with one constituent selected as THE WINNING MODEL: the portfolio with the highest terminal modeled PnL over this same period. Selection is ex post and subject to look-ahead/selection bias.

## Comparison basis

“THE WINNING MODEL” here means **{result['winning_core_variant']} Core + {result['winning_variant_specific_1u_eod_variant']} variant-specific 1U/EOD, with the {result['winning_energy_sidecar_unit_size_u_per_active_ticker']}U/DAY energy sidecar per active ticker**—portfolio `{result['winning_portfolio_id']}`. It includes core’s integrated 1U/DAY DXY sleeve plus the 10U/DAY DXY add-on (11U/DAY total), just as each of the 32 THE ONE MODEL portfolios does.

The equal-gross comparison scales every daily PnL, notional addition, and open-notional value of this one winning portfolio by **{factor:.6f}×**, so its period-end cumulative gross additions match THE ONE MODEL at **{dollars(result['the_one_model_cumulative_gross_notional_added_usd'])}**. This scales the winner’s unit sizes too: its combined DXY schedule becomes **{dec(result['equal_gross_winner_combined_dxy_units_per_active_eod']):.4f}U/DAY**, versus the original 11U/DAY. It is a proportional arithmetic scaling of all components, not an assertion that the larger orders could be executed at unchanged prices, spreads, capacity, financing, or risk. The original, unscaled 1× winner is shown alongside it for context; that original portfolio does not have the same total gross additions as the 32-portfolio aggregate.

## TWM_1M_FULL — $1M current-open-notional sizing

**TWM_1M_FULL** is the full TWM winner configuration—V3A core, the V3A-specific 1U/EOD force variant, the included 11U/DAY-per-active-ticker energy sidecar, and the combined 11U/DAY DXY schedule—uniformly scaled to **$1,000,000 of gross open notional**. It scales the original 1× winner by **{million_open_factor:.12f}×** (about {million_open_factor * 100:.4f}% of its original size). By construction, terminal gross open notional on {result['period_end']} is **{dollars(result['winning_model_1m_open_gross_open_notional_usd'])}**. The largest open notional in this historical replay also occurs on {result['winning_model_1m_open_max_gross_open_notional_date']} and is **{dollars(result['winning_model_1m_open_max_gross_open_notional_usd'])}**.

At that scale, the same historical replay produces **{dollars(result['winning_model_1m_open_terminal_pnl_usd'])}** of terminal modeled PnL on **{dollars(result['winning_model_1m_open_cumulative_gross_notional_added_usd'])}** of cumulative gross additions; the scaled combined DXY schedule is **{dec(result['winning_model_1m_open_combined_dxy_units_per_active_eod']):.6f}U/DAY**. Under your all-cash/debit convention, each $1M gross-open version is treated as a fully paid $1M position base, not $1M of PnL. Cumulative additions can exceed that base because cash from closed positions can be reused. DXY terminology and the TradingView-based DXY sleeve are retained; this sizing view does not relabel DXY as cash or a cash equivalent. This remains a hypothetical historical replay, not verified brokerage execution or proof of future performance.

![TWM_1M_FULL historical PnL and gross-notional path](Charts/superstructure/the-winning-model-1m-open-notional.png)

## TWM_1M_LIGHT — $1M current-open-notional sizing

**TWM_1M_LIGHT** uses the V3A core plus the V3A-specific 1U/EOD force schedule. It retains the chart-directed core DXY sleeve, but excludes the separate 10U/DAY DXY add-on and the energy daily-buy sidecar. Original chart-post events and the ATS/manual/user-reported core additions present in the source replay are included and properly scaled together by **{dec(result['twm_1m_light_scale_factor']):.12f}×** to target **$1,000,000 of terminal gross open notional**. The scaling also prorates those supplemental model events; it does not represent actual brokerage quantities or fills.

On {result['period_end']}, TWM_1M_LIGHT has **{dollars(result['twm_1m_light_gross_open_notional_usd'])}** gross open notional and **{dollars(result['twm_1m_light_terminal_pnl_usd'])}** terminal modeled PnL, on **{dollars(result['twm_1m_light_cumulative_gross_notional_added_usd'])}** cumulative gross additions. Its maximum open notional in the replay is **{dollars(result['twm_1m_light_max_gross_open_notional_usd'])}** on {result['twm_1m_light_max_gross_open_notional_date']}. Under the all-cash/debit convention, the $1M maximum gross-open notional is treated as $1M of fully funded positions; cumulative additions are total activity over time, not an additional cash deposit.

![TWM_1M_LIGHT historical PnL and gross-notional path](Charts/superstructure/twm-1m-light.png)

## Current-data rerun of the earlier V3A + 1U + 10U energy construction

**TWM_1M_MAX** reruns the earlier scope with the refreshed 37-session data through {result['period_end']}: V3A core + V3A-specific 1U/EOD + a 10U/DAY TradingView energy sidecar, with DXY excluded to match the earlier comparison universe. The 1U/DAY chart-directed DXY core sleeve is removed from the input composite, and the separate 10U/DAY DXY add-on is not included. Current logged ATS/manual/user-reported core events remain in the replay and are scaled with the rest of the model.

This current-data replay totals **{dollars(result['twm_1m_max_source_terminal_pnl_usd'])}** modeled PnL on **{dollars(result['twm_1m_max_source_cumulative_gross_notional_added_usd'])}** of additions, or **{dec(result['twm_1m_max_pnl_to_gross_added_pct']):.4f}%**. Scaled to **$1,000,000 terminal gross open notional** by **{dec(result['twm_1m_max_scale_factor']):.12f}×**, it yields **{dollars(result['twm_1m_max_terminal_pnl_usd'])}** modeled PnL on **{dollars(result['twm_1m_max_cumulative_gross_notional_added_usd'])}** of cumulative position additions. Under your all-cash/debit convention, treat the **$1,000,000** maximum open notional as the fully funded capital base; the cumulative **$1,234,994.54** of additions is turnover over time, not an extra $1.235M deposited. The modeled PnL is **{dec(result['twm_1m_max_pnl_on_funded_capital_pct']):.4f}% of that $1M cash base** over this replay. The 3.9893% figure above is instead PnL divided by cumulative additions. The current-data replay therefore does **not** reproduce 8.88%.

For comparison, the archived Oct. 23 snapshot (36 sessions; commit `abdd1d8`) had **$1,225,786.98** PnL on **$13,805,000.00** gross additions (**8.879297%**) and **$12,885,000.00** open notional. That is a historical result from the then-current marks and inputs, not a current-data forecast or account return.

![TWM_1M_MAX historical PnL and gross-notional path](Charts/superstructure/twm-1m-max.png)

## Terminal comparison

| Historical result through {result['period_end']} | THE ONE MODEL: 32 independent portfolios | Winner: original 1× | Winner: equal-gross scaled | TWM_1M_FULL | TWM_1M_LIGHT | TWM_1M_MAX |
|---|---:|---:|---:|---:|---:|---:|
| Terminal modeled PnL | {dollars(result['the_one_model_terminal_pnl_usd'])} | {dollars(result['winning_model_original_terminal_pnl_usd'])} | **{dollars(result['winning_model_equal_gross_terminal_pnl_usd'])}** | {dollars(result['winning_model_1m_open_terminal_pnl_usd'])} | {dollars(result['twm_1m_light_terminal_pnl_usd'])} | {dollars(result['twm_1m_max_terminal_pnl_usd'])} |
| Cumulative gross notional added | {dollars(result['the_one_model_cumulative_gross_notional_added_usd'])} | {dollars(result['winning_model_original_cumulative_gross_notional_added_usd'])} | **{dollars(result['winning_model_equal_gross_cumulative_gross_notional_added_usd'])}** | {dollars(result['winning_model_1m_open_cumulative_gross_notional_added_usd'])} | {dollars(result['twm_1m_light_cumulative_gross_notional_added_usd'])} | {dollars(result['twm_1m_max_cumulative_gross_notional_added_usd'])} |
| Gross open notional at period end | {dollars(result['the_one_model_gross_open_notional_usd'])} | {dollars(result['winning_model_original_gross_open_notional_usd'])} | {dollars(result['winning_model_equal_gross_gross_open_notional_usd'])} | **{dollars(result['winning_model_1m_open_gross_open_notional_usd'])}** | **{dollars(result['twm_1m_light_gross_open_notional_usd'])}** | **{dollars(result['twm_1m_max_gross_open_notional_usd'])}** |
| PnL ÷ cumulative gross additions | {dec(result['the_one_model_pnl_to_gross_added_pct']):.4f}% | {dec(result['winning_model_original_pnl_to_gross_added_pct']):.4f}% | **{dec(result['winning_model_equal_gross_pnl_to_gross_added_pct']):.4f}%** | {dec(result['winning_model_1m_open_pnl_to_gross_added_pct']):.4f}% | {dec(result['twm_1m_light_pnl_to_gross_added_pct']):.4f}% | {dec(result['twm_1m_max_pnl_to_gross_added_pct']):.4f}% |
| Modeled PnL ÷ $1M fully funded cash base | — | — | — | {dec(result['twm_1m_full_pnl_on_funded_capital_pct']):.4f}% | {dec(result['twm_1m_light_pnl_on_funded_capital_pct']):.4f}% | {dec(result['twm_1m_max_pnl_on_funded_capital_pct']):.4f}% |
| Peak-to-trough modeled PnL drawdown | {dollars(result['the_one_model_max_peak_to_trough_pnl_drawdown_usd'])} | {dollars(result['winning_model_original_max_peak_to_trough_pnl_drawdown_usd'])} | {dollars(result['winning_model_equal_gross_max_peak_to_trough_pnl_drawdown_usd'])} | {dollars(result['winning_model_1m_open_max_peak_to_trough_pnl_drawdown_usd'])} | {dollars(result['twm_1m_light_max_peak_to_trough_pnl_drawdown_usd'])} | {dollars(result['twm_1m_max_max_peak_to_trough_pnl_drawdown_usd'])} |

At the equal-gross terminal additions, the scaled winning curve exceeds THE ONE MODEL's terminal modeled PnL by **{dollars(result['equal_gross_terminal_pnl_difference_winner_minus_one_model_usd'])}** and its deployed-notional ratio by **{dec(result['equal_gross_deployed_notional_ratio_difference_percentage_points']):.4f} percentage points** in this historical sample. The comparison does not establish future outperformance. The winning portfolio was chosen using the same period being compared; this creates survivorship/selection bias, and its advantage is not an independent or out-of-sample result.

![THE ONE MODEL and the equal-gross scaled winning constituent](Charts/superstructure/the-one-model-vs-winning-model.png)

## Files and interpretation

- Daily comparison series, including the original, equal-gross, TWM_1M_FULL, TWM_1M_LIGHT, and TWM_1M_MAX paths: [`the_one_model_vs_winning_model_v1.csv`](data/the_one_model_vs_winning_model_v1.csv).
- Machine-readable metrics and construction notes for all $1M versions: [`the_one_model_vs_winning_model_v1_summary.json`](data/the_one_model_vs_winning_model_v1_summary.json).
- Each $1M version uniformly scales its selected source path to $1M terminal gross open notional. PnL-to-additions ratios are invariant to uniform scaling (aside from cent rounding). TWM_1M_LIGHT excludes the extra 10U/DAY DXY add-on and energy sidecar but retains core chart DXY. TWM_1M_MAX reruns the old no-DXY, 10U-energy construction using refreshed current data; it does not reproduce the archived 8.88% ratio.
- The 32-way aggregate assumes independent funding/exposure for every constituent. The one-winner comparison is a single concentrated portfolio. No positions, capital, correlated risk, or margin are netted between the two approaches.
- These are hypothetical paper-model outputs, not verified brokerage executions. Under the user-specified all-cash/debit convention, each $1M open-notional scenario is treated as a fully funded $1M capital base, and the table shows modeled PnL relative to that base. PnL divided by cumulative gross additions remains a turnover/deployed-notional ratio, not an account return. Trading costs, slippage, taxes, and operational constraints are not fully modeled.
'''
    REPORT.write_text(text, encoding="utf-8")


def main():
    result, rows = build_comparison()
    write_outputs(result, rows)
    write_chart(result, rows)
    write_million_open_chart(result, rows)
    write_light_chart(result, rows)
    write_max_chart(result, rows)
    write_report(result)
    print(f"Wrote {OUTPUT_CSV.relative_to(ROOT)}")
    print(f"Wrote {OUTPUT_JSON.relative_to(ROOT)}")
    print(f"Wrote {OUTPUT_CHART.relative_to(ROOT)}")
    print(f"Wrote {OUTPUT_1M_CHART.relative_to(ROOT)}")
    print(f"Wrote {OUTPUT_LIGHT_CHART.relative_to(ROOT)}")
    print(f"Wrote {OUTPUT_MAX_CHART.relative_to(ROOT)}")
    print(f"Wrote {REPORT.relative_to(ROOT)}")
    print(f"Equal-gross scale: {result['equal_gross_scale_factor']}x")
    print(f"THE ONE MODEL PnL: {dollars(result['the_one_model_terminal_pnl_usd'])}")
    print(f"Equal-gross winner PnL: {dollars(result['winning_model_equal_gross_terminal_pnl_usd'])}")


if __name__ == "__main__":
    main()
