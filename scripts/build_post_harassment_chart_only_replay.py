#!/usr/bin/env python3
"""Build a source-screened V3A core + V3A 1U/EOD chart-only replay.

This is a scoped hypothetical portfolio reconstruction, not an account or
execution record. User direction in the 2026-10-30 request authorizes use of
existing post-cutoff TradingView marks and the deterministic V3A 1U/EOD force
schedule through the latest complete benchmark (2026-10-26) for this portfolio
only. User-sourced chart/trade events remain capped at 2026-10-19; post-cutoff,
manual, ATS, and override events are audited but not replayed. No historical
source logs are edited.
"""
from __future__ import annotations

import bisect
import csv
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import model_perf_core as core  # noqa: E402
from influencer_ai_policy import (  # noqa: E402
    BLOCKED_TICKERS,
    is_explicit_third_party_commentary,
)

EVENT_CUTOFF = "2026-10-19"
VALUATION_AS_OF = "2026-10-26"
SCOPED_EXCEPTION_ID = "USER_AUTHORIZED_POST_HARASSMENT_V3A_V3A_MARKS_AND_FORCE_V1"
UNIT = core.UNIT

OUT_DAILY = ROOT / "data" / "post_harassment_v3a_v3a_chart_only_daily_v1.csv"
OUT_POSITIONS = ROOT / "data" / "post_harassment_v3a_v3a_chart_only_positions_v1.csv"
OUT_AUDIT = ROOT / "data" / "post_harassment_v3a_v3a_chart_only_event_audit_v1.csv"
OUT_SUMMARY = ROOT / "data" / "post_harassment_v3a_v3a_chart_only_summary_v1.json"
OUT_MANIFEST = ROOT / "data" / "post_harassment_v3a_v3a_chart_only_manifest_v1.json"

MANUAL_OR_OVERRIDE = re.compile(
    r"\bmanual\b|\bATS\b|automated\s+trading\s+system|"
    r"user[- ](?:directed|reported|specified|requested|approved)|"
    r"explicit\s+close\s+of\s+reported\s+active|cash[- ]out|"
    r"live\s+test\s+positions",
    re.I,
)
AMBIGUOUS_DIRECTION = re.compile(r"no\s+explicit\s+direction|default\s+long|direction\s+unclear", re.I)
NON_CHART_RATIONALE = re.compile(r"\bnews\b|\bheadline\b|\bparts\s+news\b", re.I)
CHART_CONTEXT = re.compile(
    r"\b(?:\d+\s*(?:m|min|h|hr|d|w|mo)|TVC|NYSE|NASDAQ|AMEX|LSE|BlackBull|"
    r"support|resistance|trendline|trend\s+line|fib(?:onacci)?|VFI|WaveTrend|"
    r"envelope|overbought|oversold|breakout|channel|chart|triangle|marker)\b",
    re.I,
)

SOURCE_LINE_RE = re.compile(
    core.LINE_RE.pattern.replace(r"[\d,]+\.?\d*", r"[\d,]+\.?\d*%?")
)


def read_all_events():
    """Parse direct standardized trade logs, including screened-out rows for audit."""
    events = []
    paths = sorted((ROOT / "trades").glob("*.txt"))
    for path in paths:
        if path.name == "index.txt":
            continue
        sym = path.stem.upper()
        for lineno, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            match = SOURCE_LINE_RE.match(line)
            if not match:
                raise ValueError(f"Unparsed source event {path.relative_to(ROOT)}:{lineno}: {line}")
            parsed = float(match.group("units"))
            events.append({
                "sym": sym,
                "date": match.group("date"),
                "time": match.group("time"),
                "tag": match.group("tag").strip().upper(),
                "kind": match.group("kind").lower(),
                "px": float(match.group("px").replace(",", "").rstrip("%")),
                "units": int(parsed) if parsed.is_integer() else parsed,
                "note": match.group("note"),
                "order": lineno,
                "source_file": str(path.relative_to(ROOT)),
                "source_line": lineno,
            })
    return sorted(events, key=lambda e: (e["date"], e["time"], e["sym"], e["order"]))


def exclusion_reasons(event):
    reasons = []
    if event["date"] > EVENT_CUTOFF:
        reasons.append("trade-event cutoff: only chart events through 2026-10-19 are eligible")
    if event["sym"] in BLOCKED_TICKERS:
        reasons.append("standing screened-ticker exclusion")
    if event["sym"] in {"DXY", "BTC", "ETH", "ALIUSD", "EURUSD", "JPYUSD", "US10Y", "US30Y"}:
        reasons.append("not eligible in this direct-price V3A/V3A chart-only replay")
    if is_explicit_third_party_commentary(event["note"]):
        reasons.append("explicit third-party/community commentary or signal badge")
    if MANUAL_OR_OVERRIDE.search(event["note"]):
        reasons.append("manual, ATS, user-directed/reported, or override event excluded")
    if AMBIGUOUS_DIRECTION.search(event["note"]):
        reasons.append("direction is explicitly inferred/ambiguous")
    if NON_CHART_RATIONALE.search(event["note"]):
        reasons.append("news-based rationale is not a chart-only signal")
    if not CHART_CONTEXT.search(event["note"]):
        reasons.append("no explicit chart/timeframe/technical context in normalized source note")
    if event["sym"] not in core.PRICES:
        reasons.append("no configured direct-price mark series")
    return list(dict.fromkeys(reasons))


def force_v3a_daily(events):
    """Reproduce the repository's V3A-specific 1U/EOD force rules, without sidecars."""
    events_by_day = defaultdict(list)
    for event in events:
        target = bisect.bisect_left(core.SESSION_DATES, event["date"])
        if target < len(core.SESSION_DATES):
            events_by_day[core.SESSION_DATES[target]].append(event)
    for day in events_by_day:
        events_by_day[day].sort(key=lambda e: (e["date"], e["time"], e["sym"], e["order"]))

    symbols = sorted({e["sym"] for e in events})
    current_direction = {}
    lots = {symbol: [] for symbol in symbols}
    last_exit_units = {}
    realized_total = 0.0
    cumulative_added = 0.0
    daily = []
    daily_lots = []
    realized_events = []

    def close_longs(symbol, price, day):
        nonlocal realized_total
        for lot in lots[symbol]:
            if lot["open"] and lot["direction"] == "long":
                pnl = lot["notional_usd"] * (price / lot["entry_price"] - 1.0)
                realized_total += pnl
                realized_events.append({"ticker": symbol, "date": day, "pnl_usd": pnl})
                lot["open"] = False
                lot["close_date"] = day
                lot["close_price"] = price

    for index, day in enumerate(core.SESSION_DATES):
        event_day_units = {}
        for event in events_by_day.get(day, []):
            sym = event["sym"]
            if event["kind"] == "exit":
                last_exit_units[sym] = float(event["units"])
                close_longs(sym, float(event["px"]), day)
            elif event["tag"] in {"LONG", "REBUY"}:
                current_direction[sym] = "long"
                event_day_units[sym] = 1.0
            elif event["tag"] == "SHORT":
                units = 1.0
                if "Compounded short" in event["note"] and last_exit_units.get(sym, 0.0) > 1.0:
                    units = last_exit_units[sym]
                current_direction[sym] = "short"
                event_day_units[sym] = units

        daily_adds = 0.0
        for sym in symbols:
            direction = current_direction.get(sym)
            if not direction:
                continue
            tranche_units = event_day_units.get(sym, 1.0)
            price = core.PRICES[sym][index]
            notional = tranche_units * UNIT
            lot = {
                "ticker": sym,
                "direction": direction,
                "units": tranche_units,
                "notional_usd": notional,
                "entry_date": day,
                "entry_price": price,
                "open": True,
                "close_date": None,
                "close_price": None,
            }
            lots[sym].append(lot)
            daily_lots.append(lot)
            cumulative_added += notional
            daily_adds += notional

        unrealized = 0.0
        open_notional = 0.0
        open_units = 0.0
        for sym in symbols:
            mark = core.PRICES[sym][index]
            for lot in lots[sym]:
                if not lot["open"]:
                    continue
                sign = 1.0 if lot["direction"] == "long" else -1.0
                unrealized += lot["notional_usd"] * sign * (mark / lot["entry_price"] - 1.0)
                open_notional += lot["notional_usd"]
                open_units += lot["units"]
        daily.append({
            "date": day,
            "realized_pnl_usd": realized_total,
            "unrealized_pnl_usd": unrealized,
            "total_pnl_usd": realized_total + unrealized,
            "cumulative_gross_additions_usd": cumulative_added,
            "gross_open_notional_usd": open_notional,
            "open_units": open_units,
            "daily_additions_usd": daily_adds,
        })
    return daily, lots, realized_events


def group_open_positions(component, open_lots):
    grouped = defaultdict(lambda: {"lots": [], "units": 0.0, "basis": 0.0, "pnl": 0.0})
    for lot in open_lots:
        ticker = lot["sym"] if component == "V3A_CORE" else lot["ticker"]
        side = lot["side"] if component == "V3A_CORE" else lot["direction"]
        units = float(lot["qty"] if component == "V3A_CORE" else lot["units"])
        entry = float(lot["entry_px"] if component == "V3A_CORE" else lot["entry_price"])
        entry_date = lot["entry_date"]
        mark = float(core.PRICES[ticker][-1])
        sign = 1.0 if side == "long" else -1.0
        notional = units * UNIT
        pnl = notional * sign * (mark / entry - 1.0)
        key = (component, ticker, side)
        group = grouped[key]
        group["lots"].append((units, entry, entry_date))
        group["units"] += units
        group["basis"] += notional
        group["pnl"] += pnl
    output = []
    for (component, ticker, side), group in sorted(grouped.items()):
        units = group["units"]
        output.append({
            "component": component,
            "ticker": ticker,
            "side": side.upper(),
            "open_lot_count": len(group["lots"]),
            "model_units": f"{units:.4f}",
            "gross_open_model_notional_usd": f"{group['basis']:.2f}",
            "valuation_mark_date": VALUATION_AS_OF,
            "valuation_mark": f"{core.PRICES[ticker][-1]:.8f}",
            "unrealized_pnl_usd": f"{group['pnl']:.2f}",
            "lot_entry_dates_and_units": "; ".join(
                f"{day}:{q:g}U@{price:.8f}" for q, price, day in group["lots"]
            ),
        })
    return output


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(path, rows, fields=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    if fields is None:
        fields = list(rows[0]) if rows else []
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main():
    if core.SESSION_DATES[-1] != VALUATION_AS_OF:
        raise ValueError(f"Expected latest common mark {VALUATION_AS_OF}; found {core.SESSION_DATES[-1]}")
    # Source/screened replay: suppress the chart-commentary DXY direction sleeve.
    # The post-cutoff mark extension is scoped to this one user-authorized portfolio.
    core.SCREENED_REPLAY = True

    source_events = read_all_events()
    audit_rows = []
    included = []
    exclusion_counts = Counter()
    for event in source_events:
        reasons = exclusion_reasons(event)
        use = not reasons
        if use:
            included.append(event)
        else:
            exclusion_counts.update(reasons)
        audit_rows.append({
            "source_file": event["source_file"],
            "source_line": event["source_line"],
            "event_date": event["date"],
            "event_time_mst": event["time"],
            "ticker": event["sym"],
            "action_tag": event["tag"],
            "event_kind": event["kind"],
            "event_price_usd_or_quote": f"{event['px']:.8f}",
            "event_units": event["units"],
            "included_in_replay": "YES" if use else "NO",
            "exclusion_reasons": "; ".join(reasons),
            "original_note": event["note"],
        })

    if not included:
        raise ValueError("No chart-only V3A events survived the source/security filters")

    core_model = core.daily_series("V3A", included)
    force_daily, force_lots_by_ticker, force_realized_events = force_v3a_daily(included)
    core_open_lots = [lot for lot in core_model["lots"] if lot["open"]]
    force_open_lots = [lot for lots in force_lots_by_ticker.values() for lot in lots if lot["open"]]

    positions = group_open_positions("V3A_CORE", core_open_lots)
    positions.extend(group_open_positions("V3A_FORCE_1U_EOD", force_open_lots))

    daily_rows = []
    for i, day in enumerate(core_model["dates"]):
        force = force_daily[i]
        core_open = sum(
            float(lot["qty"]) * UNIT for lot in core_model["lots"]
            if lot["entry_idx"] <= i and (lot["close_idx"] is None or i < lot["close_idx"])
        )
        combined_pnl = core_model["total"][i] + force["total_pnl_usd"]
        daily_rows.append({
            "date": day,
            "V3A_core_realized_pnl_usd": f"{core_model['realized'][i]:.2f}",
            "V3A_core_unrealized_pnl_usd": f"{core_model['unrealized'][i]:.2f}",
            "V3A_core_total_pnl_usd": f"{core_model['total'][i]:.2f}",
            "V3A_core_cumulative_gross_additions_usd": f"{core_model['deployed'][i]:.2f}",
            "V3A_core_gross_open_notional_usd": f"{core_open:.2f}",
            "V3A_force_realized_pnl_usd": f"{force['realized_pnl_usd']:.2f}",
            "V3A_force_unrealized_pnl_usd": f"{force['unrealized_pnl_usd']:.2f}",
            "V3A_force_total_pnl_usd": f"{force['total_pnl_usd']:.2f}",
            "V3A_force_cumulative_gross_additions_usd": f"{force['cumulative_gross_additions_usd']:.2f}",
            "V3A_force_gross_open_notional_usd": f"{force['gross_open_notional_usd']:.2f}",
            "combined_V3A_V3A_total_pnl_usd": f"{combined_pnl:.2f}",
            "combined_cumulative_gross_additions_usd": f"{core_model['deployed'][i] + force['cumulative_gross_additions_usd']:.2f}",
            "combined_gross_open_notional_usd": f"{core_open + force['gross_open_notional_usd']:.2f}",
            "combined_open_units": f"{core_model['open_units'][i] + force['open_units']:.4f}",
            "valuation_basis": "TradingView-only marks; scoped user authorization through 2026-10-26",
        })

    final_core = core_model["total"][-1]
    final_force = force_daily[-1]["total_pnl_usd"]
    combined_final = final_core + final_force
    final_pnl_series = [float(row["combined_V3A_V3A_total_pnl_usd"]) for row in daily_rows]
    peak = 0.0
    max_dd = 0.0
    dd_peak_date = "before period"
    dd_trough_date = daily_rows[0]["date"]
    current_peak_date = dd_peak_date
    for row, pnl in zip(daily_rows, final_pnl_series):
        if pnl > peak:
            peak = pnl
            current_peak_date = row["date"]
        if peak - pnl > max_dd:
            max_dd = peak - pnl
            dd_peak_date = current_peak_date
            dd_trough_date = row["date"]

    summary = {
        "portfolio_name": "Post-Harassment V3A + V3A Audit Portfolio",
        "version": 1,
        "replay_method": "V3A core + V3A-specific 1U/EOD force model; chart-only event filter; no energy daily-buy sidecar; DXY direction excluded under source screen",
        "status": "Chart-only model reconstruction through latest complete marks; not a verified account restoration",
        "user_authorized_scoped_exception_id": SCOPED_EXCEPTION_ID,
        "scoped_force_model_additions_through_valuation_date": True,
        "post_cutoff_user_sourced_events_ingested": False,
        "event_cutoff": EVENT_CUTOFF,
        "valuation_as_of": VALUATION_AS_OF,
        "latest_common_mark_date_in_repository": core.SESSION_DATES[-1],
        "user_requested_to_date_limit": "No complete synchronized TradingView benchmark marks for 2026-10-27 through 2026-10-30 were present; output is not valued through 2026-10-30.",
        "direct_price_ticker_screen_excluded": sorted(BLOCKED_TICKERS),
        "dxy_directional_sleeve_included": False,
        "energy_daily_buy_sidecar_included": False,
        "manual_ats_user_directed_or_reported_events_included": 0,
        "included_chart_context_event_count": len(included),
        "source_event_count_audited": len(source_events),
        "excluded_event_count": len(source_events) - len(included),
        "exclusion_counts_with_overlap": dict(sorted(exclusion_counts.items())),
        "core_V3A": {
            "realized_pnl_usd": round(core_model["realized"][-1], 2),
            "unrealized_pnl_usd": round(core_model["unrealized"][-1], 2),
            "total_pnl_usd": round(final_core, 2),
            "cumulative_gross_additions_usd": round(core_model["deployed"][-1], 2),
            "gross_open_notional_usd": round(float(daily_rows[-1]["V3A_core_gross_open_notional_usd"]), 2),
            "open_units": round(core_model["open_units"][-1], 4),
            "open_lot_count": len(core_open_lots),
        },
        "force_V3A_1U_EOD": {
            "realized_pnl_usd": round(force_daily[-1]["realized_pnl_usd"], 2),
            "unrealized_pnl_usd": round(force_daily[-1]["unrealized_pnl_usd"], 2),
            "total_pnl_usd": round(final_force, 2),
            "cumulative_gross_additions_usd": round(force_daily[-1]["cumulative_gross_additions_usd"], 2),
            "gross_open_notional_usd": round(force_daily[-1]["gross_open_notional_usd"], 2),
            "open_units": round(force_daily[-1]["open_units"], 4),
            "open_lot_count": len(force_open_lots),
        },
        "combined_V3A_V3A": {
            "realized_pnl_usd": round(core_model["realized"][-1] + force_daily[-1]["realized_pnl_usd"], 2),
            "unrealized_pnl_usd": round(core_model["unrealized"][-1] + force_daily[-1]["unrealized_pnl_usd"], 2),
            "total_pnl_usd": round(combined_final, 2),
            "cumulative_gross_additions_usd": round(float(daily_rows[-1]["combined_cumulative_gross_additions_usd"]), 2),
            "gross_open_notional_usd": round(float(daily_rows[-1]["combined_gross_open_notional_usd"]), 2),
            "open_units": round(core_model["open_units"][-1] + force_daily[-1]["open_units"], 4),
            "open_lot_count": len(core_open_lots) + len(force_open_lots),
            "max_peak_to_trough_pnl_drawdown_usd": round(max_dd, 2),
            "max_drawdown_peak_date": dd_peak_date,
            "max_drawdown_trough_date": dd_trough_date,
        },
        "accounting_caveat": "Model U is $10,000 entry notional, not shares or account funding. No opening cash, actual shares, brokerage/ATS fills, account mapping, leverage, financing, or realized account cash balance is inferred. The all-cash/debit convention remains; modeled notional is not a borrowing claim.",
        "chart_processing_caveat": "The replay consumes normalized chart-context events in trades/*.txt. It does not OCR/reinterpret every image in Archives/ or Charts/; ambiguous/no-direction and non-chart/news/third-party/manual/ATS/user-directed records are excluded and audited.",
    }

    write_csv(OUT_DAILY, daily_rows)
    write_csv(OUT_POSITIONS, positions, fields=[
        "component", "ticker", "side", "open_lot_count", "model_units",
        "gross_open_model_notional_usd", "valuation_mark_date",
        "valuation_mark", "unrealized_pnl_usd",
        "lot_entry_dates_and_units",
    ])
    write_csv(OUT_AUDIT, audit_rows)
    OUT_SUMMARY.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    source_paths = [
        core.BENCHMARK_SESSION_FILE,
        ROOT / "data" / "tradingview_benchmark_source_manifest_20261026.json",
        ROOT / "scripts" / "model_perf_core.py",
        ROOT / "scripts" / "influencer_ai_policy.py",
        ROOT / "scripts" / "tradingview_policy.py",
        ROOT / "reports" / "TradingView Scoped Exception — Post-Harassment V3A + V3A Replay.md",
        Path(__file__),
        *sorted(path for path in (ROOT / "trades").glob("*.txt") if path.name != "index.txt"),
    ]
    manifest = {
        "version": 1,
        "builder": str(Path(__file__).relative_to(ROOT)),
        "built_at_local": datetime.now().astimezone().isoformat(timespec="seconds"),
        "scoped_exception_id": SCOPED_EXCEPTION_ID,
        "user_authorization_context": "2026-10-30 request to run V3A/V3A to date on all charts; scoped use of latest complete marks and deterministic V3A force schedule through 2026-10-26, with user-sourced events capped at 2026-10-19",
        "event_cutoff": EVENT_CUTOFF,
        "valuation_as_of": VALUATION_AS_OF,
        "source_hashes_sha256": {str(path.relative_to(ROOT)): sha256(path) for path in source_paths},
        "outputs": [str(p.relative_to(ROOT)) for p in (OUT_DAILY, OUT_POSITIONS, OUT_AUDIT, OUT_SUMMARY, OUT_MANIFEST)],
    }
    OUT_MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print(f"Built chart-only V3A/V3A through {VALUATION_AS_OF}; {len(included)} of {len(source_events)} normalized events included.")
    print(f"Core PnL ${final_core:,.2f}; force PnL ${final_force:,.2f}; combined ${combined_final:,.2f}.")
    print(f"Open notional ${float(daily_rows[-1]['combined_gross_open_notional_usd']):,.2f}; rows {len(positions)}.")
    print(f"Outputs: {OUT_DAILY.relative_to(ROOT)}, {OUT_POSITIONS.relative_to(ROOT)}, {OUT_AUDIT.relative_to(ROOT)}, {OUT_SUMMARY.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
