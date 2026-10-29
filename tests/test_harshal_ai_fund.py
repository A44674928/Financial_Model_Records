import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_ai_fund_replay_is_separate_cutoff_safe_and_routes_only_selected_events():
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT / "scripts")
    env["PAPER_TRADES_AI_FUND_REPLAY"] = "1"
    code = (
        "import json, model_perf_core as c; "
        "ev=c.parse_trades(); lots, realized=c.build_dxy_daily_lots(); "
        "print(json.dumps({'end':c.SESSION_DATES[-1], 'tickers':sorted(c.PRICES), "
        "'events':[(e['sym'],e['note']) for e in ev], 'dxy_lots':len(lots), "
        "'dxy_terminal':lots[-1]['entry_date'] if lots else None}))"
    )
    result = subprocess.run(
        [sys.executable, "-c", code], cwd=ROOT, env=env, text=True,
        capture_output=True, check=True,
    )
    data = json.loads(result.stdout)
    assert data["end"] == "2026-10-19"
    assert set(data["tickers"]) == {
        "AAPL", "AMZN", "CAT", "CVX", "DIS", "INTC", "META", "NVDA", "OIL", "PLTR", "TSLA"
    }
    assert data["dxy_lots"] > 0
    assert data["dxy_terminal"] == "2026-10-19"
    assert all(
        ticker in {"AAPL", "AMZN", "CAT", "CVX", "DIS", "INTC", "META", "NVDA", "OIL", "PLTR", "TSLA"}
        for ticker, _ in data["events"]
    )
    assert all(
        ticker in {"AAPL", "AMZN", "INTC", "META", "NVDA", "PLTR", "TSLA"}
        or "TradingView" in note
        or "badge" in note.lower()
        or "Support > Buy" in note
        or note.startswith("Buy ")
        or note.startswith("BUY ")
        for ticker, note in data["events"]
    )


def test_ai_fund_artifacts_keep_yield_signals_unpriced_and_preserve_source_links():
    summary = json.loads((ROOT / "data" / "harshal_priyavadan_patel_ai_fund_summary_v1.json").read_text())
    assert summary["portfolio_name"] == "HARSHAL_PRIYAVADAN_PATEL_AI_FUND"
    assert summary["post_cutoff_tradingview_inputs_used"] == 0
    assert summary["dxy_directional_sleeve_modeled"] is True
    assert summary["yield_events_retained_but_not_pnl_modeled"] == 3
    report = (ROOT / "reports" / "HARSHAL_PRIYAVADAN_PATEL_AI_FUND.md").read_text()
    assert "all-cash/debit" in report
    assert "October 20-or-later" in report
