"""Daily US10Y spread carry relative to the user's 4.865% baseline.

Source observations are the user-provided September and October CSVs under data/.
The adjustment uses the model engine's cumulative deployed-notional denominator,
actual calendar days / 365, and the last available yield close for sessions where
the Treasury market supplied no observation (e.g. 2026-10-12).
"""

import csv
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_FILES = (
    ROOT / "data" / "us10y_close_september_2026.csv",
    ROOT / "data" / "us10y_close_october_2026.csv",
)
BASELINE_PCT = 4.865
START_DATE = "2026-09-10"
VARIANTS = ("V1", "V2", "V3A", "V3B")


def load_source_yields():
    """Load and validate user-supplied daily US10Y close observations in percent."""
    values = {}
    for path in SOURCE_FILES:
        with path.open(newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            if not reader.fieldnames or "Date" not in reader.fieldnames:
                raise ValueError(f"Missing Date column in {path.name}")
            value_column = next(
                (name for name in reader.fieldnames if name != "Date"), None
            )
            if not value_column:
                raise ValueError(f"Missing yield column in {path.name}")
            for row in reader:
                day = row["Date"].strip()
                value = float(row[value_column].strip())
                if day in values:
                    raise ValueError(f"Duplicate US10Y observation for {day}")
                if not 0.0 < value < 20.0:
                    raise ValueError(f"Implausible yield {value} for {day}")
                values[day] = value
    if not values:
        raise ValueError("No US10Y observations were loaded")
    return dict(sorted(values.items()))


def align_session_yields(session_dates):
    """Forward-fill the last available Treasury close onto comparison sessions."""
    observed = load_source_yields()
    observed_dates = sorted(observed)
    aligned = []
    last_day = None
    for day in session_dates:
        if day < START_DATE:
            aligned.append({
                "date": day, "yield_pct": None, "source_date": None,
                "carried_forward": False, "active": False,
            })
            continue
        for candidate in observed_dates:
            if candidate > day:
                break
            last_day = candidate
        if last_day is None:
            raise ValueError(f"No US10Y observation on/before session {day}")
        aligned.append({
            "date": day,
            "yield_pct": observed[last_day],
            "source_date": last_day,
            "carried_forward": last_day != day,
            "active": True,
        })
    if not any(row["date"] == START_DATE and row["yield_pct"] is not None for row in aligned):
        raise ValueError(f"Model session calendar does not contain baseline date {START_DATE}")
    return aligned


def apply_us10y_adjustment(series, session_dates):
    """Add daily carry adjustment arrays to each model series in-place.

    The annualized spread is (daily US10Y close - 4.865%) / 100. For each
    interval, use the deployed notional and latest US10Y close known at the
    interval's start, multiplying by actual elapsed calendar days / 365. The
    first active interval starts after the 2026-09-10 baseline date; the
    adjustment is zero before that date.
    """
    if len(session_dates) < 2:
        raise ValueError("At least two session dates are required")
    aligned = align_session_yields(session_dates)
    interval_days = [0] * len(session_dates)
    applied_yield = [None] * len(session_dates)
    daily_carry = {v: [0.0] * len(session_dates) for v in VARIANTS}
    cumulative_carry = {v: [0.0] * len(session_dates) for v in VARIANTS}

    for i in range(len(session_dates) - 1):
        start_day, end_day = session_dates[i], session_dates[i + 1]
        days = (date.fromisoformat(end_day) - date.fromisoformat(start_day)).days
        interval_days[i + 1] = days
        if start_day < START_DATE or not aligned[i]["active"]:
            continue
        rate_pct = aligned[i]["yield_pct"]
        applied_yield[i + 1] = rate_pct
        annual_spread = (rate_pct - BASELINE_PCT) / 100.0
        for variant in VARIANTS:
            deployed = series[variant]["deployed"][i]
            daily_carry[variant][i + 1] = deployed * annual_spread * days / 365.0

    for variant in VARIANTS:
        running = 0.0
        adj = []
        for i, amount in enumerate(daily_carry[variant]):
            running += amount
            adj.append(running)
        cumulative_carry[variant] = adj
        series[variant]["yield_adjustment_daily"] = daily_carry[variant]
        series[variant]["yield_adjustment"] = adj
        series[variant]["adjusted_total"] = [
            value + carry for value, carry in zip(series[variant]["total"], adj)
        ]
        series[variant]["adjusted_roi"] = [
            100.0 * total / deployed if deployed else 0.0
            for total, deployed in zip(series[variant]["adjusted_total"], series[variant]["deployed"])
        ]
        series[variant]["us10y_yield_pct"] = [row["yield_pct"] for row in aligned]
        series[variant]["us10y_source_date"] = [row["source_date"] for row in aligned]
        series[variant]["us10y_forward_filled"] = [row["carried_forward"] for row in aligned]
        series[variant]["us10y_spread_pct_points"] = [
            row["yield_pct"] - BASELINE_PCT if row["yield_pct"] is not None else None
            for row in aligned
        ]
        series[variant]["us10y_accrual_days"] = interval_days

    rows = []
    for i, row in enumerate(aligned):
        rows.append({
            **row,
            "baseline_pct": BASELINE_PCT,
            "spread_pct_points": (
                row["yield_pct"] - BASELINE_PCT if row["yield_pct"] is not None else None
            ),
            "interval_start_date": session_dates[i - 1] if i > 0 else None,
            "accrual_days": interval_days[i],
            "applied_yield_pct": applied_yield[i],
            "daily_adjustment_usd": {
                v: daily_carry[v][i] for v in VARIANTS
            },
            "cumulative_adjustment_usd": {
                v: cumulative_carry[v][i] for v in VARIANTS
            },
        })
    return rows


def write_adjustment_csv(rows, series, path):
    """Write auditable date/model rows for the daily adjustment."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "variant", "session_date", "yield_close_pct", "yield_source_date",
        "yield_forward_filled", "baseline_pct", "spread_pct_points",
        "interval_start_date", "accrual_days", "applied_yield_pct",
        "deployed_notional_usd", "daily_adjustment_usd",
        "cumulative_adjustment_usd", "base_trading_pnl_usd",
        "adjusted_total_pnl_usd", "adjusted_roi_pct",
    ]
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for i, row in enumerate(rows):
            for variant in VARIANTS:
                writer.writerow({
                    "variant": variant,
                    "session_date": row["date"],
                    "yield_close_pct": row["yield_pct"],
                    "yield_source_date": row["source_date"],
                    "yield_forward_filled": row["carried_forward"],
                    "baseline_pct": BASELINE_PCT,
                    "spread_pct_points": row["spread_pct_points"],
                    "interval_start_date": row["interval_start_date"],
                    "accrual_days": row["accrual_days"],
                    "applied_yield_pct": row["applied_yield_pct"],
                    "deployed_notional_usd": series[variant]["deployed"][i],
                    "daily_adjustment_usd": row["daily_adjustment_usd"][variant],
                    "cumulative_adjustment_usd": row["cumulative_adjustment_usd"][variant],
                    "base_trading_pnl_usd": series[variant]["total"][i],
                    "adjusted_total_pnl_usd": series[variant]["adjusted_total"][i],
                    "adjusted_roi_pct": series[variant]["adjusted_roi"][i],
                })
    return path
