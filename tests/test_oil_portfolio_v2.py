import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_oil_v2_marks_existing_positions_through_latest_complete_eod_only():
    summary = json.loads((ROOT / "data" / "oil_portfolio_summary_v2.json").read_text())
    assert summary["output_version"] == "2"
    assert summary["active_trade_event_cutoff"] == "2026-10-19"
    assert summary["active_replay_end_date"] == "2026-10-26"
    assert summary["post_cutoff_tradingview_inputs_used"] == 25
    assert summary["post_cutoff_trade_rows_used"] == 0
    assert summary["variants"]["V1"]["total_pnl_usd"] == 42935.36
    assert summary["variants"]["V1"]["realized_pnl_usd"] == 0.0

    v1 = json.loads((ROOT / "data" / "oil_portfolio_summary_v1.json").read_text())
    assert v1["active_replay_end_date"] == "2026-10-19"
    daily = list(csv.DictReader((ROOT / "data" / "oil_portfolio_daily_v2.csv").open(newline="", encoding="utf-8-sig")))
    assert daily[-1]["date"] == "2026-10-26"
    report = (ROOT / "reports" / "Oil Portfolio — 2026-10-26 Update.md").read_text()
    assert "not a fully current October 29 valuation" in report
    assert "October 27–29 data still needed" in report
    assert "does not ingest later trade-log events" in report
