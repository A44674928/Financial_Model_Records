#!/usr/bin/env python3
"""Build an auditable, versioned replay under the influencer/AI source block.

Outputs are new v1 artifacts; historical model reports and raw trade logs are
left untouched. The replay is also capped at the last TradingView-permitted
date under the standing October 20, 2026 source cutoff.
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from influencer_ai_policy import (  # noqa: E402
    BLOCKED_TICKERS,
    MAX_TRADINGVIEW_INPUT_DATE,
    POLICY_EFFECTIVE_DATE,
    is_explicit_third_party_commentary,
)

# Configure model_perf_core before importing it so it filters post-cutoff marks
# and screened tickers before creating its active in-memory price inputs.
os.environ["PAPER_TRADES_INFLUENCER_AI_SCREEN"] = "1"

import model_perf_core as core  # noqa: E402

DATA = ROOT / "data"
REPORT = ROOT / "reports" / "Influencer and AI Screened Replay — 2026-10-29.md"
DAILY_OUT = DATA / "model_performance_influencer_ai_screened_daily_v1.csv"
SUMMARY_OUT = DATA / "model_performance_influencer_ai_screened_summary_v1.json"
AUDIT_OUT = DATA / "influencer_ai_blocked_inputs_v1.csv"
MANIFEST_OUT = DATA / "influencer_ai_screened_replay_manifest_v1.json"

LINE_RE = re.compile(
    r"^(?P<date>\d{4}-\d{2}-\d{2})\s+(?P<time>\d{2}:\d{2})\s+MST\s*\|\s*"
    r"SIMULATED PAPER\s+\[(?P<tag>[A-Za-z ]+?)\]\s*\|\s*"
    r"(?P<kind>entry|exit):\s*\[Market @ ~\$?(?P<px>[\d,]+\.?\d*%?)\]\s*\|\s*"
    r"size:\s*\[(?P<units>\d+(?:\.\d+)?)\s*units?[^\]]*\]\s*\|\s*"
    r"note:\s*\[(?P<note>.*)\]\s*$"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def event_audit_rows():
    """List every trade-log record removed by at least one active screen."""
    rows = []
    for path in sorted((ROOT / "trades").glob("*.txt")):
        if path.name == "index.txt":
            continue
        ticker = path.stem.upper()
        for lineno, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            match = LINE_RE.match(line)
            if not match:
                raise ValueError(f"Unparsed line in audit scan: {path.name}:{lineno}: {line}")
            note = match.group("note")
            day = match.group("date")
            reasons = []
            if ticker in BLOCKED_TICKERS:
                reasons.append("user-approved AI-exposure ticker screen")
            if is_explicit_third_party_commentary(note):
                reasons.append("explicit third-party/community commentary provenance")
            if ticker == "DXY":
                reasons.append("directional sleeve is based on chart commentary; raw DXY marks alone are retained")
            if day > MAX_TRADINGVIEW_INPUT_DATE.isoformat():
                if re.search(r"TradingView|TVC:", note, re.I):
                    reasons.append("post-2026-10-19 TradingView input blocked under standing policy")
                else:
                    reasons.append("outside screened replay window ending 2026-10-19")
            if reasons:
                record_id = hashlib.sha256(f"{path.name}\0{lineno}\0{line}".encode("utf-8")).hexdigest()[:16]
                rows.append({
                    "Record_ID": record_id,
                    "Source_File": f"trades/{path.name}",
                    "Line": lineno,
                    "Date": day,
                    "Ticker": ticker,
                    "Event": match.group("kind").upper(),
                    "Tag": match.group("tag").strip().upper(),
                    "Units": match.group("units"),
                    "Exclusion_Reasons": "; ".join(dict.fromkeys(reasons)),
                    "Original_Record_Preserved": "YES",
                    "Used_In_Screened_Replay": "NO",
                    "Original_Note": note,
                })
    return rows


def main():
    events = core.parse_trades()
    series = {variant: core.daily_series(variant, events) for variant in core.VARIANTS}

    with DAILY_OUT.open("w", newline="", encoding="utf-8") as handle:
        fields = ["Date", "Variant", "Realized_PnL_USD", "Unrealized_PnL_USD", "Total_PnL_USD",
                  "ROI_Pct", "Deployed_Notional_USD", "Open_Units"]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for variant in core.VARIANTS:
            model = series[variant]
            for idx, day in enumerate(model["dates"]):
                writer.writerow({
                    "Date": day,
                    "Variant": variant,
                    "Realized_PnL_USD": f"{model['realized'][idx]:.2f}",
                    "Unrealized_PnL_USD": f"{model['unrealized'][idx]:.2f}",
                    "Total_PnL_USD": f"{model['total'][idx]:.2f}",
                    "ROI_Pct": f"{model['roi'][idx]:.6f}",
                    "Deployed_Notional_USD": f"{model['deployed'][idx]:.2f}",
                    "Open_Units": f"{model['open_units'][idx]:.6f}",
                })

    audit = event_audit_rows()
    with AUDIT_OUT.open("w", newline="", encoding="utf-8") as handle:
        fields = ["Record_ID", "Source_File", "Line", "Date", "Ticker", "Event", "Tag", "Units",
                  "Exclusion_Reasons", "Original_Record_Preserved", "Used_In_Screened_Replay", "Original_Note"]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(audit)

    summary = {
        "policy_name": "Influencer and AI source / ticker block",
        "policy_effective_date": POLICY_EFFECTIVE_DATE.isoformat(),
        "replay_start_date": core.SESSION_DATES[0],
        "replay_end_date": core.SESSION_DATES[-1],
        "standing_tradingview_last_allowed_date": MAX_TRADINGVIEW_INPUT_DATE.isoformat(),
        "blocked_tickers": sorted(BLOCKED_TICKERS),
        "direct_price_tickers_remaining": sorted(core.PRICES),
        "third_party_commentary_events_excluded": sum(
            "explicit third-party/community commentary provenance" in row["Exclusion_Reasons"]
            for row in audit
        ),
        "blocked_ticker_event_records": sum(
            "user-approved AI-exposure ticker screen" in row["Exclusion_Reasons"]
            for row in audit
        ),
        "dxy_directional_events_excluded": sum(row["Ticker"] == "DXY" for row in audit),
        "all_excluded_record_count_with_overlap": len(audit),
        "excluded_record_count_note": "Record counts overlap where multiple rules apply.",
        "source_scope": {
            "allowed": ["official issuer filings", "raw market data", "user trade ledger records"],
            "blocked": ["all third-party commentary, regardless of influencer labeling", "AI-generated or AI-company commentary"],
        },
        "tradingview_post_cutoff_rows_used": 0,
        "dxy_directional_sleeve_included": False,
        "variants": {},
    }
    for variant in core.VARIANTS:
        model = series[variant]
        summary["variants"][variant] = {
            "label": core.VARIANT_LABEL[variant],
            "realized_pnl_usd": round(model["realized"][-1], 2),
            "unrealized_pnl_usd": round(model["unrealized"][-1], 2),
            "total_pnl_usd": round(model["total"][-1], 2),
            "roi_pct": round(model["roi"][-1], 6),
            "deployed_notional_usd": round(model["deployed"][-1], 2),
            "open_units": round(model["open_units"][-1], 6),
            "retained_lot_count": len(model["lots"]),
        }
    SUMMARY_OUT.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    input_paths = [
        core.BENCHMARK_SESSION_FILE,
        *[path for path in sorted((ROOT / "trades").glob("*.txt")) if path.name != "index.txt"],
    ]
    manifest = {
        "version": 1,
        "built_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "builder": "scripts/build_influencer_ai_screened_replay.py",
        "cutoff": MAX_TRADINGVIEW_INPUT_DATE.isoformat(),
        "source_hashes_sha256": {str(path.relative_to(ROOT)): sha256(path) for path in input_paths},
        "outputs": [str(p.relative_to(ROOT)) for p in (DAILY_OUT, SUMMARY_OUT, AUDIT_OUT, REPORT, MANIFEST_OUT)],
        "original_model_report_preserved": "Model Performance Comparison.md",
    }
    MANIFEST_OUT.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Influencer and AI-Screened Replay — 2026-10-29",
        "",
        "> Versioned retroactive replay. Existing reports, ledgers, screenshots, and source records were not overwritten or deleted.",
        "",
        "## Policy applied",
        "",
        "- Excluded the approved broad AI-exposure ticker screen: " + ", ".join(f"`{t}`" for t in sorted(BLOCKED_TICKERS)) + ".",
        "- Excluded trade events whose stored provenance explicitly identifies third-party/community commentary or recommendation badges.",
        "- Excluded the DXY directional sleeve because its logged directions are chart-commentary signals; raw DXY marks alone are not a position signal.",
        f"- Enforced the standing TradingView cutoff by ending the replay on **{MAX_TRADINGVIEW_INPUT_DATE.isoformat()}**. No October 20-or-later TradingView marks or events enter the replay.",
        "- Official issuer filings, raw market observations, and user trade-ledger records are eligible. The block is on commentary and the selected securities, not on the listed source types.",
        "",
        "## Recomputed terminal results",
        "",
        "| Variant | Realized PnL | Unrealized PnL | Total PnL | ROI | Deployed notional | Open units |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for variant in core.VARIANTS:
        item = summary["variants"][variant]
        lines.append(
            f"| {variant} — {item['label']} | ${item['realized_pnl_usd']:,.2f} | "
            f"${item['unrealized_pnl_usd']:,.2f} | ${item['total_pnl_usd']:,.2f} | "
            f"{item['roi_pct']:.4f}% | ${item['deployed_notional_usd']:,.2f} | {item['open_units']:,.4f} |"
        )
    lines += [
        "",
        "These are simulated paper-model results under the screened inputs, not brokerage results or a cash-balance reconciliation. The existing accounting convention remains all-cash/debit; no leverage or financing is inferred.",
        "",
        "## Audit and output files",
        "",
        f"- Removed records in the audit index: **{len(audit)} rows** (counts overlap when multiple policies apply).",
        f"- Explicit third-party commentary event rows: **{summary['third_party_commentary_events_excluded']}**.",
        f"- Event rows in the seven blocked tickers: **{summary['blocked_ticker_event_records']}**.",
        f"- DXY directional events screened out: **{summary['dxy_directional_events_excluded']}**.",
        "- [Blocked-input audit CSV](../data/influencer_ai_blocked_inputs_v1.csv) records each source line, reason, and preservation status.",
        "- [Daily replay CSV](../data/model_performance_influencer_ai_screened_daily_v1.csv) and [summary JSON](../data/model_performance_influencer_ai_screened_summary_v1.json) are separate versioned outputs.",
        "- [Replay manifest](../data/influencer_ai_screened_replay_manifest_v1.json) includes SHA-256 hashes for the consumed benchmark and trade logs.",
        "- The previous [Model Performance Comparison](../Model%20Performance%20Comparison.md) remains unchanged as a historical record.",
        "",
        "## Provenance limits",
        "",
        "Historical trade notes do not consistently identify the author or origin of each idea. This replay excludes records with explicit commentary provenance and the user-selected securities; it does not label an un-attributed note as influencer content without evidence. The rule is fail-closed for new source inputs: unclassified commentary is not eligible until it is documented as an allowed source class. The audit CSV is a source screen, not a claim that every historic recommendation has been exhaustively attributed.",
        "",
        "The replay uses the repository's existing standardized paper-trade logs and the pre-cutoff benchmark marks. It preserves the prior report and original ledgers; it does not rewrite their historical conclusions.",
        "",
    ]
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Built {len(core.SESSION_DATES)} sessions through {core.SESSION_DATES[-1]}.")
    print(f"Retained direct-price tickers: {len(core.PRICES)}; audit exclusions: {len(audit)} records.")
    for variant in core.VARIANTS:
        item = summary["variants"][variant]
        print(f"{variant}: total PnL ${item['total_pnl_usd']:,.2f}; ROI {item['roi_pct']:.4f}%")


if __name__ == "__main__":
    main()
