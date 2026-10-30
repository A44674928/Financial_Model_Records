import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run_core(mode, version=None):
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT / "scripts")
    env["PAPER_TRADES_OIL_PORTFOLIO_REPLAY"] = "0"
    env["PAPER_TRADES_AI_FUND_REPLAY"] = "0"
    env["PAPER_TRADES_INFLUENCER_AI_SCREEN"] = "0"
    env["PAPER_TRADES_OIL_PORTFOLIO_REPLAY"] = "1" if mode == "oil" else "0"
    env["PAPER_TRADES_AI_FUND_REPLAY"] = "1" if mode == "ai_fund" else "0"
    if version is not None:
        env["PAPER_TRADES_AI_FUND_REPLAY_VERSION"] = str(version)
    code = (
        "import json, model_perf_core as c; ev=c.parse_trades(); "
        "s=c.daily_series('V1',ev); print(json.dumps({'end':c.SESSION_DATES[-1], "
        "'tickers':sorted(c.PRICES), 'events':[(e['sym'],e['date']) for e in ev], "
        "'lot_tickers':sorted({lot['sym'] for lot in s['lots']}), 'dxy_lots':sum(l['sym']=='DXY' for l in s['lots'])}))"
    )
    result = subprocess.run(
        [sys.executable, "-c", code], cwd=ROOT, env=env, text=True,
        capture_output=True, check=True,
    )
    return json.loads(result.stdout)


def test_oil_portfolio_isolated_and_uses_only_pre_cutoff_marks():
    data = run_core("oil")
    assert data["end"] == "2026-10-19"
    assert set(data["tickers"]) == {"BRENT", "OIL", "CVX", "VLO", "XLE"}
    assert set(data["lot_tickers"]) == {"BRENT", "OIL", "CVX", "VLO", "XLE"}
    assert data["dxy_lots"] == 0
    assert {ticker for ticker, _ in data["events"]} <= set(data["tickers"])


def test_oil_portfolio_ledger_contains_weekend_oil_and_flags_later_records():
    summary = json.loads((ROOT / "data" / "oil_portfolio_summary_v1.json").read_text())
    ledger = list(__import__("csv").DictReader((ROOT / "data" / "oil_portfolio_trade_ledger_v1.csv").open()))
    assert summary["portfolio_name"] == "Oil"
    assert summary["active_replay_end_date"] == "2026-10-19"
    assert summary["post_cutoff_tradingview_inputs_used"] == 0
    assert summary["all_trade_log_rows_indexed"] == len(ledger) == 34
    assert summary["pre_cutoff_trade_log_rows_used"] == 18
    assert summary["post_cutoff_trade_log_rows_preserved_not_used"] == 16
    for variant in ("V1", "V2", "V3A", "V3B"):
        lots = summary["weekend_oil_tagged_lots_by_variant"][variant]
        assert {(row["ticker"], row["units"]) for row in lots} == {("BRENT", 50.0), ("OIL", 50.0)}
        assert all(row["entry_date"] == "2026-10-19" for row in lots)
    assert any(row["record_status"] == "PRESERVED_FLAGGED_TV_POST_CUTOFF_NOT_USED" for row in ledger)


def test_current_ai_fund_v2_has_no_oil_and_v1_is_preserved_as_history():
    v2 = json.loads((ROOT / "data" / "harshal_priyavadan_patel_ai_fund_summary_v2.json").read_text())
    v1 = json.loads((ROOT / "data" / "harshal_priyavadan_patel_ai_fund_summary_v1.json").read_text())
    assert v2["version"] == 2
    assert not ({"BRENT", "OIL", "CVX", "VLO", "XLE"} & set(v2["direct_price_tickers_modeled"]))
    assert {"OIL", "CVX"} <= set(v1["direct_price_tickers_modeled"])
    assert (ROOT / "reports" / "HARSHAL_PRIYAVADAN_PATEL_AI_FUND_v1.md").is_file()
    assert "transfers all oil and oil-linked trade records" in (ROOT / "reports" / "HARSHAL_PRIYAVADAN_PATEL_AI_FUND.md").read_text()


def test_oil_portfolio_keeps_separate_book_sources_out_of_model_total():
    related = list(__import__("csv").DictReader((ROOT / "data" / "oil_portfolio_related_book_records_v1.csv").open()))
    assert len(related) == 5
    assert sum(row["reported_transaction_pnl_usd"] != "" for row in related) == 2
    assert all("not used in active Oil replay" in row["status"] for row in related if row["reported_transaction_pnl_usd"])
    report = (ROOT / "reports" / "Oil Portfolio.md").read_text()
    assert "Weekend Oil" in report
    assert "not used in the active replay" in report


def test_oil_pnl_reconciliation_attributes_gap_without_shorting():
    summary = json.loads((ROOT / "data" / "oil_portfolio_summary_v1.json").read_text())
    reconciliation = summary["pnl_reconciliation"]
    assert reconciliation["ai_fund_v1_to_v2_removed_pnl_usd_by_variant"] == {
        "V1": 1214.71, "V2": 1214.71, "V3A": 1214.72, "V3B": 1214.71,
    }
    assert reconciliation["transferred_ai_fund_v1_oil_cvx_trade_pnl_usd"] == 1214.71
    assert reconciliation["oil_portfolio_total_pnl_usd"] == 1723.09
    assert reconciliation["other_oil_records_net_pnl_usd"] == 508.38
    assert reconciliation["private_fund_screenshot_reported_close_pnl_usd_separate"] == 2713480646.02
    assert reconciliation["active_oil_short_entries_used"] == 0
    assert reconciliation["later_short_entries_not_used"] == 2
    rows = list(__import__("csv").DictReader((ROOT / "data" / "oil_pnl_reconciliation_v1.csv").open()))
    moved = [row for row in rows if row["reconciliation_type"] == "TRANSFERRED_AI_FUND_V1_TRADE"]
    assert len(moved) == 3
    assert sum(float(row["amount_usd"]) for row in moved) == 1214.71
    report = (ROOT / "reports" / "Oil Portfolio.md").read_text()
    assert "not oil shorts" in report
    assert "$2,713,480,646.02" in report
