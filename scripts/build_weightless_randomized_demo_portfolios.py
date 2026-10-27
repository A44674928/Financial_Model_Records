#!/usr/bin/env python3
"""Build reproducible, equal-dollar random mixes of existing model sleeves.

Composition choices are uniform and are not weighted by historical returns.
Each selected component is scaled to $1,000 maximum gross open notional. DXY is
removed from composite core/TOM paths and may appear once as a standalone
component, so a demo never double-counts its currency sleeve. All books remain
independent and gross exposures are summed, not netted.
"""
from __future__ import annotations

import csv
import html
import json
import random
import statistics
import sys
from collections import defaultdict
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
REPORTS = ROOT / "reports"
CHARTS = ROOT / "Charts" / "superstructure"
SEED = 20261026
DEMO_COUNT = 32
SLEEVE_MAX_OPEN_TARGET = Decimal("1000")
VARIANTS = ("V1", "V2", "V3A", "V3B")

CORE_DAILY = DATA / "model_performance_daily.csv"
STRATEGY_DAILY = DATA / "strategy_sidecar_comparison_daily_v1.csv"
TOM_DAILY = DATA / "the_one_model_split_portfolios_v1.csv"
TWM_DAILY = DATA / "the_one_model_vs_winning_model_v1.csv"
DXY_DAILY = DATA / "dxy_currency_desk_sidecar_daily_20261026.csv"
ENERGY_DAILY = DATA / "the_one_model_energy_11u_sidecar_daily_v1.csv"
TICKER_CONTRIBUTIONS = DATA / "model_performance_tickers.csv"

MEMBERS_OUT = DATA / "weightless_demo_portfolio_members_v1.csv"
DAILY_OUT = DATA / "weightless_demo_portfolio_daily_v1.csv"
SUMMARY_OUT = DATA / "weightless_demo_portfolio_summary_v1.csv"
SVG_OUT = CHARTS / "weightless-randomized-demo-portfolios-20261026.svg"
REPORT_OUT = REPORTS / "Weightless Randomized Demo Portfolios — 2026-10-26.md"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def dec(value: str | float | int) -> Decimal:
    return Decimal(str(value))


def load_core_ticker_series(dates: list[str]) -> dict[str, dict]:
    """Rebuild ticker-specific core paths from the established lot engine."""
    sys.path.insert(0, str(ROOT / "scripts"))
    from model_perf_core import MODEL_PRICES, UNIT, all_series  # local import: no plotting dependency

    core_series, _events = all_series()
    output = {}
    for variant in VARIANTS:
        source = core_series[variant]
        symbols = sorted({lot["sym"] for lot in source["lots"] if lot["sym"] != "DXY"})
        for ticker in symbols:
            lots = [lot for lot in source["lots"] if lot["sym"] == ticker]
            realized = [trade for trade in source["realized_trades"] if trade["sym"] == ticker]
            if not lots:
                continue
            p_series, add_series, open_series = [], [], []
            for index, _date in enumerate(dates):
                realized_pnl = sum(
                    trade["pnl"] for trade in realized if trade["idx"] <= index
                )
                unrealized_pnl = 0.0
                gross_open = 0.0
                gross_added = 0.0
                price = MODEL_PRICES[ticker][index]
                for lot in lots:
                    notional = float(lot["qty"]) * UNIT
                    if lot["entry_idx"] <= index:
                        gross_added += notional
                    if lot["entry_idx"] <= index and (
                        lot["close_idx"] is None or index < lot["close_idx"]
                    ):
                        sign = 1.0 if lot["side"] == "long" else -1.0
                        unrealized_pnl += sign * notional * (price / lot["entry_px"] - 1.0)
                        gross_open += notional
                p_series.append(dec(realized_pnl + unrealized_pnl))
                add_series.append(dec(gross_added))
                open_series.append(dec(gross_open))
            if max(open_series, default=Decimal("0")) <= 0:
                continue
            key = f"CORE_TICKER_{variant}_{ticker}"
            output[key] = make_component(
                key, "ticker", dates, p_series, add_series, open_series,
                description=f"{variant} core ticker {ticker}; DXY excluded",
                dxy_units=0.0,
            )
    return output


def make_component(
    component_id: str,
    category: str,
    dates: list[str],
    pnl: list[Decimal],
    added: list[Decimal],
    opened: list[Decimal],
    *,
    description: str,
    dxy_units: float = 0.0,
) -> dict:
    if not (len(dates) == len(pnl) == len(added) == len(opened)):
        raise ValueError(f"Mismatched daily series for {component_id}")
    maximum_open = max(opened, default=Decimal("0"))
    if maximum_open <= 0:
        raise ValueError(f"No positive gross open notional for {component_id}")
    return {
        "id": component_id,
        "category": category,
        "description": description,
        "dates": dates,
        "pnl": pnl,
        "added": added,
        "open": opened,
        "native_max_open": maximum_open,
        "scale": SLEEVE_MAX_OPEN_TARGET / maximum_open,
        "dxy_units": dxy_units,
    }


def _aligned(rows: list[dict[str, str]], dates: list[str], date_key: str, field: str) -> list[Decimal]:
    by_date = {row[date_key]: dec(row[field]) for row in rows}
    return [by_date.get(day, Decimal("0")) for day in dates]


def load_component_catalog() -> tuple[list[str], dict[str, dict], dict[str, list[str]]]:
    core_rows = read_csv(CORE_DAILY)
    dates = [row["session_date"] for row in core_rows if row["variant"] == "V1"]
    if len(dates) != 37 or dates[0] != "2026-09-03" or dates[-1] != "2026-10-26":
        raise ValueError(f"Unexpected model window: {dates[0]} .. {dates[-1]} ({len(dates)} sessions)")

    dxy_rows = [row for row in read_csv(DXY_DAILY) if dec(row["unit_size_u"]) == Decimal("10")]
    dxy_by_date = {row["date"]: row for row in dxy_rows}
    dxy_pnl_10 = [dec(dxy_by_date[day]["daily_investment_unrealized_pnl_usd"]) if day in dxy_by_date else Decimal("0") for day in dates]
    dxy_added_10 = [dec(dxy_by_date[day]["cumulative_notional_added_usd"]) if day in dxy_by_date else Decimal("0") for day in dates]
    dxy_open_10 = [dec(dxy_by_date[day]["open_notional_usd"]) if day in dxy_by_date else Decimal("0") for day in dates]

    catalog: dict[str, dict] = {}
    categories: dict[str, list[str]] = defaultdict(list)

    # DXY-free direct-price core strategies: subtract only their integrated 1U/DAY DXY sleeve.
    for variant in VARIANTS:
        variant_rows = [row for row in core_rows if row["variant"] == variant]
        if [row["session_date"] for row in variant_rows] != dates:
            raise ValueError(f"Core session calendar mismatch for {variant}")
        pnl = [dec(row["total_pnl_usd"]) - dxy_pnl_10[i] / Decimal("10") for i, row in enumerate(variant_rows)]
        added = [dec(row["deployed_usd"]) - dxy_added_10[i] / Decimal("10") for i, row in enumerate(variant_rows)]
        opened = [dec(row["open_units"]) * Decimal("10000") - dxy_open_10[i] / Decimal("10") for i, row in enumerate(variant_rows)]
        component_id = f"CORE_{variant}_NO_DXY"
        catalog[component_id] = make_component(
            component_id, "core", dates, pnl, added, opened,
            description=f"{variant} direct-price core; integrated 1U/DAY DXY removed",
        )
        categories["core"].append(component_id)

    # Variant-specific 1U/EOD force strategies contain no DXY sleeve.
    strategy_rows = read_csv(STRATEGY_DAILY)
    if [row["date"] for row in strategy_rows] != dates:
        raise ValueError("Strategy comparison session calendar mismatch")
    for variant in VARIANTS:
        component_id = f"FORCE_{variant}_1U_EOD"
        catalog[component_id] = make_component(
            component_id, "force", dates,
            [dec(row[f"{variant}_force_1u_pnl_usd"]) for row in strategy_rows],
            [dec(row[f"{variant}_force_1u_cumulative_notional_added_usd"]) for row in strategy_rows],
            [dec(row[f"{variant}_force_1u_open_notional_usd"]) for row in strategy_rows],
            description=f"{variant} variant-specific 1U/EOD force model; no DXY",
        )
        categories["force"].append(component_id)

    for component_id, component in load_core_ticker_series(dates).items():
        catalog[component_id] = component
        categories["ticker"].append(component_id)

    # Each energy ticker is an independent TradingView-marked 11U/DAY U-equivalent sleeve.
    energy_rows = read_csv(ENERGY_DAILY)
    by_ticker: dict[str, dict[str, dict[str, str]]] = defaultdict(dict)
    for row in energy_rows:
        by_ticker[row["ticker"]][row["date"]] = row
    for ticker in ("BRENT", "OIL"):
        ticker_rows = by_ticker[ticker]
        active_dates = [day for day in dates if day in ticker_rows]
        if not active_dates:
            raise ValueError(f"No supplied TradingView energy marks for {ticker}")
        if active_dates != dates[dates.index(active_dates[0]):]:
            raise ValueError(f"Unexpected missing active-session marks for {ticker}")
        pnl, added, opened = [], [], []
        last_row = None
        for day in dates:
            if day in ticker_rows:
                last_row = ticker_rows[day]
            if last_row is None:
                pnl.append(Decimal("0")); added.append(Decimal("0")); opened.append(Decimal("0"))
            else:
                pnl.append(dec(last_row["daily_buys_unrealized_pnl_usd"]))
                added.append(dec(last_row["cumulative_daily_buy_notional_usd"]))
                opened.append(dec(last_row["cumulative_daily_buy_notional_usd"]))
        component_id = f"ENERGY_{ticker}_11U_DAY"
        catalog[component_id] = make_component(
            component_id, "energy", dates, pnl, added, opened,
            description=f"11U/DAY {ticker} daily-buy sidecar; U-equivalents, no share conversion",
        )
        categories["energy"].append(component_id)

    # DXY is a standalone 1U or 10U model sleeve, not a direct-price stock sleeve.
    for units, fraction in (("1U", Decimal("0.1")), ("10U", Decimal("1"))):
        component_id = f"DXY_{units}_STANDALONE"
        catalog[component_id] = make_component(
            component_id, "dxy", dates,
            [value * fraction for value in dxy_pnl_10],
            [value * fraction for value in dxy_added_10],
            [value * fraction for value in dxy_open_10],
            description=f"Standalone TradingView DXY index-return sleeve, {units}; not a share ticker",
            dxy_units=float(units[:-1]),
        )
        categories["dxy"].append(component_id)

    # Whole-model choices are all DXY-free; a DXY sleeve can therefore be selected once independently.
    tom_rows = read_csv(TOM_DAILY)
    if [row["date"] for row in tom_rows] != dates:
        raise ValueError("TOM session calendar mismatch")
    tom_summary = json.loads((DATA / "the_one_model_split_portfolios_v1_summary.json").read_text(encoding="utf-8"))
    portfolio_ids = [item["portfolio_id"] for item in tom_summary["individual_portfolios"]]
    for portfolio_id in portfolio_ids:
        pnl, added, opened = [], [], []
        for row in tom_rows:
            pnl.append(dec(row[f"{portfolio_id}__pnl_usd"]) - Decimal("1.1") * dec(row[f"{portfolio_id}__dxy_10u_sidecar_pnl_usd"]))
            added.append(dec(row[f"{portfolio_id}__cumulative_notional_added_usd"]) - Decimal("1.1") * dec(row[f"{portfolio_id}__dxy_10u_sidecar_notional_added_usd"]))
            opened.append(dec(row[f"{portfolio_id}__open_notional_usd"]) - Decimal("1.1") * dec(row[f"{portfolio_id}__dxy_10u_sidecar_open_notional_usd"]))
        component_id = f"TOM_MEMBER_NO_DXY_{portfolio_id}"
        catalog[component_id] = make_component(
            component_id, "model", dates, pnl, added, opened,
            description=f"One TOM constituent {portfolio_id}; both DXY sleeves removed",
        )

    # Equal probability over model *types*, then equal probability among TOM members within that type.
    model_types = ["TOM_MEMBER", "TOM_AGGREGATE", "TWM_1M_MAX"]
    tom_aggregate = []
    for row in tom_rows:
        tom_aggregate.append({
            "date": row["date"],
            "pnl": dec(row["aggregate_pnl_usd"]) - Decimal("1.1") * dec(row["aggregate_dxy_10u_sidecar_pnl_usd"]),
            "added": dec(row["aggregate_cumulative_notional_added_usd"]) - Decimal("1.1") * dec(row["aggregate_dxy_10u_sidecar_notional_added_usd"]),
            "open": dec(row["aggregate_open_notional_usd"]) - Decimal("1.1") * dec(row["aggregate_dxy_10u_sidecar_open_notional_usd"]),
        })
    component_id = "TOM_32_AGGREGATE_NO_DXY"
    catalog[component_id] = make_component(
        component_id, "model", dates,
        [row["pnl"] for row in tom_aggregate], [row["added"] for row in tom_aggregate], [row["open"] for row in tom_aggregate],
        description="TOM aggregate of 32 independent books; both DXY sleeves removed arithmetically",
    )

    twm_rows = read_csv(TWM_DAILY)
    if [row["date"] for row in twm_rows] != dates:
        raise ValueError("TWM session calendar mismatch")
    component_id = "TWM_1M_MAX_NO_DXY_10U_ENERGY"
    catalog[component_id] = make_component(
        component_id, "model", dates,
        [dec(row["twm_1m_max_pnl_usd"]) for row in twm_rows],
        [dec(row["twm_1m_max_cumulative_gross_notional_added_usd"]) for row in twm_rows],
        [dec(row["twm_1m_max_gross_open_notional_usd"]) for row in twm_rows],
        description="Existing TWM_1M_MAX: no DXY, 10U/DAY energy",
    )
    model_components = {
        "TOM_MEMBER": [key for key in catalog if key.startswith("TOM_MEMBER_NO_DXY_")],
        "TOM_AGGREGATE": ["TOM_32_AGGREGATE_NO_DXY"],
        "TWM_1M_MAX": ["TWM_1M_MAX_NO_DXY_10U_ENERGY"],
    }
    if set(model_components) != set(model_types):
        raise AssertionError("Model type catalog is inconsistent")
    categories["model"] = ["<selected by unweighted model-type draw>"]

    return dates, catalog, categories, model_components


def percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    position = (len(ordered) - 1) * fraction
    low = int(position)
    high = min(low + 1, len(ordered) - 1)
    mix = position - low
    return ordered[low] * (1 - mix) + ordered[high] * mix


def drawdown(values: list[Decimal]) -> Decimal:
    peak = Decimal("0")
    max_dd = Decimal("0")
    for value in values:
        if value > peak:
            peak = value
        max_dd = max(max_dd, peak - value)
    return max_dd


def make_demos(dates: list[str], catalog: dict[str, dict], model_components: dict[str, list[str]]) -> tuple[list[dict], list[dict]]:
    rng = random.Random(SEED)
    demos, membership = [], []
    extra_categories = ("force", "ticker", "energy", "dxy")
    for index in range(1, DEMO_COUNT + 1):
        selected = ["core", "model"] + rng.sample(list(extra_categories), rng.randint(1, len(extra_categories)))
        components = []
        for category in selected:
            if category == "model":
                model_type = rng.choice(("TOM_MEMBER", "TOM_AGGREGATE", "TWM_1M_MAX"))
                component_id = rng.choice(model_components[model_type])
            else:
                component_id = rng.choice([key for key, comp in catalog.items() if comp["category"] == category])
            components.append(catalog[component_id])
        demo_id = f"WLESS-{index:02d}"
        if sum(component["dxy_units"] > 0 for component in components) > 1:
            raise AssertionError("A demo may contain at most one standalone DXY sleeve")
        budget = SLEEVE_MAX_OPEN_TARGET * len(components)
        pnl, added, opened = [], [], []
        for day_index in range(len(dates)):
            pnl.append(sum((component["pnl"][day_index] * component["scale"] for component in components), Decimal("0")))
            added.append(sum((component["added"][day_index] * component["scale"] for component in components), Decimal("0")))
            opened.append(sum((component["open"][day_index] * component["scale"] for component in components), Decimal("0")))
        returns = [value / budget * Decimal("100") for value in pnl]
        max_open = max(opened)
        if max_open > budget + Decimal("0.01"):
            raise AssertionError(f"Gross open exceeds reserved capacity in {demo_id}")
        demos.append({
            "id": demo_id,
            "components": components,
            "pnl": pnl,
            "added": added,
            "open": opened,
            "returns": returns,
            "budget": budget,
            "max_open": max_open,
            "terminal_pnl": pnl[-1],
            "terminal_added": added[-1],
            "terminal_open": opened[-1],
            "pnl_to_add_pct": pnl[-1] / added[-1] * Decimal("100") if added[-1] else Decimal("0"),
            "pnl_to_budget_pct": pnl[-1] / budget * Decimal("100"),
            "pnl_to_max_open_pct": pnl[-1] / max_open * Decimal("100") if max_open else Decimal("0"),
            "max_drawdown": drawdown(pnl),
            "dxy_units": sum(component["dxy_units"] for component in components),
        })
        for component in components:
            membership.append({
                "demo_id": demo_id,
                "component_id": component["id"],
                "component_type": component["category"],
                "component_description": component["description"],
                "native_max_open_notional_usd": f"{component['native_max_open']:.2f}",
                "equal_sleeve_target_usd": f"{SLEEVE_MAX_OPEN_TARGET:.2f}",
                "scale_factor": f"{component['scale']:.12f}",
                "dxy_units_per_active_eod": f"{component['dxy_units']:.4f}",
            })
    return demos, membership


def write_csv(path: Path, headers: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_outputs(dates: list[str], demos: list[dict], membership: list[dict]) -> None:
    write_csv(MEMBERS_OUT, list(membership[0].keys()), membership)

    daily_rows = []
    for i, day in enumerate(dates):
        row = {"date": day}
        for demo in demos:
            prefix = demo["id"]
            row[f"{prefix}__pnl_usd"] = f"{demo['pnl'][i]:.2f}"
            row[f"{prefix}__cumulative_gross_additions_usd"] = f"{demo['added'][i]:.2f}"
            row[f"{prefix}__gross_open_notional_usd"] = f"{demo['open'][i]:.2f}"
            row[f"{prefix}__return_on_allocated_capacity_pct"] = f"{demo['returns'][i]:.6f}"
        daily_rows.append(row)
    write_csv(DAILY_OUT, list(daily_rows[0].keys()), daily_rows)

    summary_rows = []
    for demo in demos:
        ids = [component["id"] for component in demo["components"]]
        summary_rows.append({
            "demo_id": demo["id"],
            "component_count": len(ids),
            "component_types": ";".join(sorted({component["category"] for component in demo["components"]})),
            "component_ids": ";".join(ids),
            "dxy_sleeve_count": sum(component["dxy_units"] > 0 for component in demo["components"]),
            "dxy_units_per_active_eod": f"{demo['dxy_units']:.4f}",
            "allocated_sleeve_capacity_usd": f"{demo['budget']:.2f}",
            "terminal_pnl_usd": f"{demo['terminal_pnl']:.2f}",
            "terminal_cumulative_gross_additions_usd": f"{demo['terminal_added']:.2f}",
            "terminal_gross_open_notional_usd": f"{demo['terminal_open']:.2f}",
            "maximum_gross_open_notional_usd": f"{demo['max_open']:.2f}",
            "maximum_pnl_drawdown_usd": f"{demo['max_drawdown']:.2f}",
            "pnl_to_gross_additions_pct": f"{demo['pnl_to_add_pct']:.6f}",
            "pnl_to_allocated_capacity_pct": f"{demo['pnl_to_budget_pct']:.6f}",
            "pnl_to_maximum_open_notional_pct": f"{demo['pnl_to_max_open_pct']:.6f}",
        })
    write_csv(SUMMARY_OUT, list(summary_rows[0].keys()), summary_rows)
    write_svg(CHARTS, SVG_OUT, dates, demos)
    write_report(REPORT_OUT, dates, demos)


def _path(values: list[float], x_map, y_map) -> str:
    return " ".join(("M" if i == 0 else "L") + f"{x_map(i):.1f},{y_map(value):.1f}" for i, value in enumerate(values))


def write_svg(charts_dir: Path, path: Path, dates: list[str], demos: list[dict]) -> None:
    charts_dir.mkdir(parents=True, exist_ok=True)
    width, height = 1240, 760
    left, right, top, bottom = 95, 75, 125, 105
    plot_w, plot_h = width - left - right, height - top - bottom
    values = [float(value) for demo in demos for value in demo["returns"]]
    y_min = min(-1.0, min(values) - 0.35)
    y_max = max(1.0, max(values) + 0.35)
    pad = (y_max - y_min) * 0.06
    y_min -= pad; y_max += pad
    x_map = lambda index: left + plot_w * index / (len(dates) - 1)
    y_map = lambda value: top + plot_h * (y_max - value) / (y_max - y_min)
    bands = []
    for index in range(len(dates)):
        point_values = [float(demo["returns"][index]) for demo in demos]
        bands.append((percentile(point_values, 0.10), percentile(point_values, 0.50), percentile(point_values, 0.90)))
    upper = [item[2] for item in bands]
    lower = [item[0] for item in bands]
    median = [item[1] for item in bands]
    polygon = [f"{x_map(i):.1f},{y_map(upper[i]):.1f}" for i in range(len(dates))]
    polygon += [f"{x_map(i):.1f},{y_map(lower[i]):.1f}" for i in reversed(range(len(dates)))]

    palette = ["#0f766e", "#2563eb", "#9333ea", "#ea580c", "#0891b2", "#65a30d", "#c026d3", "#475569"]
    elements = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#fbfdff"/>',
        '<style>text{font-family:Inter,Segoe UI,Arial,sans-serif;fill:#334155}.title{font-size:25px;font-weight:700;fill:#0f172a}.sub{font-size:13px;fill:#475569}.axis{font-size:12px;fill:#64748b}.note{font-size:11px;fill:#475569}.legend{font-size:11px;fill:#334155}</style>',
        '<text x="95" y="43" class="title">Weightless randomization: 32 mixed demo portfolios</text>',
        '<text x="95" y="69" class="sub">Equal-probability component selection · $1,000 max-open sleeve scale · no performance weighting · 2026-09-03–2026-10-26</text>',
        '<text x="95" y="91" class="sub">Cumulative PnL as % of reserved sleeve-capacity budget; shaded band = 10th–90th percentile, bold line = median</text>',
    ]
    tick_count = 6
    for step in range(tick_count + 1):
        value = y_min + (y_max - y_min) * step / tick_count
        y = y_map(value)
        elements.append(f'<line x1="{left}" y1="{y:.1f}" x2="{left+plot_w}" y2="{y:.1f}" stroke="#e2e8f0" stroke-width="1"/>')
        elements.append(f'<text x="{left-13}" y="{y+4:.1f}" text-anchor="end" class="axis">{value:.1f}%</text>')
    zero_y = y_map(0)
    elements.append(f'<line x1="{left}" y1="{zero_y:.1f}" x2="{left+plot_w}" y2="{zero_y:.1f}" stroke="#94a3b8" stroke-width="1.5"/>')
    for index in sorted(set(round(x) for x in [0, 6, 12, 18, 24, 30, 36])):
        x = x_map(index)
        label = dates[index][5:]
        elements.append(f'<line x1="{x:.1f}" y1="{top+plot_h}" x2="{x:.1f}" y2="{top+plot_h+6}" stroke="#94a3b8"/>')
        elements.append(f'<text x="{x:.1f}" y="{top+plot_h+26}" text-anchor="middle" class="axis">{label}</text>')
    elements.append(f'<polygon points="{" ".join(polygon)}" fill="#60a5fa" fill-opacity="0.18" stroke="none"/>')
    for i, demo in enumerate(demos):
        curve = [float(x) for x in demo["returns"]]
        color = palette[i % len(palette)]
        elements.append(f'<path d="{_path(curve, x_map, y_map)}" fill="none" stroke="{color}" stroke-opacity="0.24" stroke-width="1.1"/>')
    elements.append(f'<path d="{_path(median, x_map, y_map)}" fill="none" stroke="#0f172a" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"/>')
    lastx, lasty = x_map(len(dates)-1), y_map(median[-1])
    elements.append(f'<circle cx="{lastx:.1f}" cy="{lasty:.1f}" r="5" fill="#0f172a"/>')
    elements.append(f'<text x="{lastx+12:.1f}" y="{lasty-10:.1f}" class="sub" font-weight="700">Median {median[-1]:.2f}%</text>')
    elements.append(f'<text x="{left+plot_w/2:.1f}" y="{height-56}" text-anchor="middle" class="axis">Supplied TradingView session date</text>')
    elements.append(f'<text x="25" y="{top+plot_h/2:.1f}" transform="rotate(-90 25 {top+plot_h/2:.1f})" text-anchor="middle" class="axis">Cumulative modeled PnL / allocated sleeve capacity</text>')
    elements.append(f'<rect x="{left}" y="{height-32}" width="15" height="9" fill="#60a5fa" fill-opacity="0.25"/><text x="{left+22}" y="{height-24}" class="note">10th–90th percentile range</text>')
    elements.append(f'<line x1="{left+200}" y1="{height-28}" x2="{left+225}" y2="{height-28}" stroke="#0f172a" stroke-width="3"/><text x="{left+233}" y="{height-24}" class="note">median</text>')
    elements.append(f'<text x="{width-right}" y="{height-24}" text-anchor="end" class="note">Equal sleeve dollars; historical composition demo only—not forecast or universal profitability</text>')
    elements.append('</svg>')
    path.write_text("\n".join(elements) + "\n", encoding="utf-8")


def write_report(path: Path, dates: list[str], demos: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    returns = [float(demo["pnl_to_budget_pct"]) for demo in demos]
    pnl_per_demo = [float(demo["terminal_pnl"]) for demo in demos]
    max_open = [float(demo["max_open"]) for demo in demos]
    members = []
    for demo in demos:
        components = "<br>".join(html.escape(component["id"]) for component in demo["components"])
        members.append(
            f"| {demo['id']} | {len(demo['components'])} | {components} | "
            f"${demo['budget']:,.0f} | ${demo['terminal_pnl']:,.2f} | "
            f"{demo['pnl_to_budget_pct']:.3f}% | {demo['pnl_to_add_pct']:.3f}% | "
            f"{demo['pnl_to_max_open_pct']:.3f}% | ${demo['max_open']:,.2f} | ${demo['max_drawdown']:,.2f} |"
        )
    compositions = "\n".join(members)
    text = f'''# Weightless Randomized Demo Portfolios — 2026-10-26

**Snapshot:** supplied TradingView replay, **{dates[0]}–{dates[-1]}** ({len(dates)} sessions). This is a reproducible composition/aggregation demonstration—not a forecast, portfolio recommendation, or claim of future profitability.

![32 equal-dollar random portfolio mixes and their distribution](../Charts/superstructure/weightless-randomized-demo-portfolios-20261026.svg)

## What “weightless randomization” means here

- **Uniform composition draws:** seed `{SEED}` selects component types and available variants/tickers without ranking or weighting them by ROI, Sharpe, drawdown, or other historical performance. Each demo always has one DXY-free core book and one DXY-free whole-model component, plus a uniform random selection of one to four additional categories from force, ticker, energy, and standalone DXY. There are **32 reproducible demo compositions**.
- **Equal dollars per chosen component:** each selected component is scaled to **$1,000 maximum gross open notional**, so every selected sleeve has equal size. The reserved all-cash capacity is the sum of those sleeve targets (3–6 components = $3K–$6K). No return-based portfolio weights are applied.
- **DXY control:** core and whole-model source paths are stripped of DXY before they enter the catalog. A demo can have at most one explicitly selected standalone 1U or 10U/DAY DXY sleeve. DXY is an index-return proxy, not a share ticker.
- **Independent books, not netting:** each component retains its own historical event/mark path. Same-ticker components, if selected, are separate funded sleeves; their gross PnL/additions/exposure are summed and never position-netted. Energy sidecars remain separate BRENT/OIL U-equivalents.
- **No invented history:** components that begin after Sep. 3 remain at zero before their first supplied active session. TradingView-only marks are used; no legacy-price substitutions, image-inferred trades, or verified-fill claims are introduced.

## The superstructure demonstration

The superstructure performs the same steps for every exact mix: identify independent components; record their source variant, ticker, sidecar scope, and scale factor; align each path to the shared session calendar; sum daily PnL, additions, and gross open notional; then report drawdown and clearly named return denominators. The graph shows every demo's cumulative PnL relative to its reserved sleeve-capacity budget, with a 10th–90th percentile band and median.

Across this seeded sample, the ending return on allocated sleeve capacity ranges from **{min(returns):.3f}% to {max(returns):.3f}%**, with a median of **{statistics.median(returns):.3f}%**. Ending modeled PnL ranges from **${min(pnl_per_demo):,.2f} to ${max(pnl_per_demo):,.2f}**. Maximum concurrent gross-open exposure ranges from **${min(max_open):,.2f} to ${max(max_open):,.2f}**. The range is intentional: the system keeps the different mixes and their inputs separate while using the same aggregation contract.

This demonstrates composition-agnostic **accounting and reporting**, not that every mix is profitable or that exact composition does not affect results. In-sample selection, correlation, concentration, market capacity, trading costs, and future performance remain unresolved.

## Demo portfolio series

`PnL / capacity` is terminal modeled PnL divided by the reserved sum of the $1,000 per-sleeve limits. `PnL / additions` is a separate deployed-notional ratio. `PnL / max open` divides terminal PnL by the actual maximum concurrent gross-open notional and is the funded-peak-exposure view; it is not interchangeable with either additions or reserved-capacity return. `Maximum open` is the actual concurrent gross exposure after aligning the selected sleeves' daily paths; it can be below reserved capacity when sleeve peaks occur on different dates.

| Demo | Sleeves | Randomly selected composition | Reserved capacity | Terminal PnL | PnL / capacity | PnL / additions | PnL / max open | Maximum open | Max drawdown |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
{compositions}

## Reproducibility and files

- Builder: [`scripts/build_weightless_randomized_demo_portfolios.py`](../scripts/build_weightless_randomized_demo_portfolios.py). Rebuild from the repository root with `python scripts/build_weightless_randomized_demo_portfolios.py`.
- Component manifest, scaling factors, and DXY check: [`data/weightless_demo_portfolio_members_v1.csv`](../data/weightless_demo_portfolio_members_v1.csv).
- Full aligned daily PnL/additions/open paths for all 32 demos: [`data/weightless_demo_portfolio_daily_v1.csv`](../data/weightless_demo_portfolio_daily_v1.csv).
- One-row-per-demo summary: [`data/weightless_demo_portfolio_summary_v1.csv`](../data/weightless_demo_portfolio_summary_v1.csv).
- Graph: [`Charts/superstructure/weightless-randomized-demo-portfolios-20261026.svg`](../Charts/superstructure/weightless-randomized-demo-portfolios-20261026.svg).
- Source families: V1–V3B core, variant-specific 1U/EOD force, direct-price ticker sleeves, supplied 11U energy sidecars, standalone TradingView DXY, DXY-free TOM constituents/aggregate, and TWM_1M_MAX.
'''
    path.write_text(text, encoding="utf-8")


def main() -> None:
    dates, catalog, categories, model_components = load_component_catalog()
    demos, membership = make_demos(dates, catalog, model_components)
    write_outputs(dates, demos, membership)
    print(f"Wrote {len(demos)} demos, {len(membership)} component rows, {len(dates)} sessions")
    print(f"Report: {REPORT_OUT.relative_to(ROOT)}")
    print(f"Graph:  {SVG_OUT.relative_to(ROOT)}")
    print(f"Mean terminal return on capacity: {statistics.mean(float(d['pnl_to_budget_pct']) for d in demos):.3f}%")


if __name__ == "__main__":
    main()
