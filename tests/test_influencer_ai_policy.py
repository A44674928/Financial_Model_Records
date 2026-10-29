import csv
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from influencer_ai_policy import (  # noqa: E402
    BLOCKED_TICKERS,
    MAX_TRADINGVIEW_INPUT_DATE,
    InfluencerAIPolicyError,
    is_explicit_third_party_commentary,
    require_active_input_allowed,
    source_class_allowed,
    ticker_allowed,
)


def test_user_approved_ticker_block_is_case_insensitive_and_exact():
    assert BLOCKED_TICKERS == {"NVDA", "PLTR", "META", "AMZN", "TSLA", "AAPL", "INTC"}
    assert not ticker_allowed("nvda")
    assert not ticker_allowed("INTC")
    assert ticker_allowed("BRENT")


def test_source_allowlist_is_fail_closed_and_keeps_user_selected_sources():
    assert source_class_allowed("official_issuer_filing")
    assert source_class_allowed("raw_market_data")
    assert source_class_allowed("user_trade_ledger")
    assert not source_class_allowed("third_party_commentary")
    assert not source_class_allowed("unknown")
    assert not source_class_allowed("")


def test_active_input_guard_rejects_blocked_sources_and_tickers():
    require_active_input_allowed("raw_market_data", "BRENT")
    require_active_input_allowed("official_issuer_filing")
    import pytest
    with pytest.raises(InfluencerAIPolicyError, match="not allowed"):
        require_active_input_allowed("third_party_commentary")
    with pytest.raises(InfluencerAIPolicyError, match="Ticker"):
        require_active_input_allowed("raw_market_data", "NVDA")


def test_commentary_classifier_blocks_explicit_sources_but_not_user_confirmed_positions():
    assert is_explicit_third_party_commentary("Sep 8 TradingView post, LONG badge")
    assert is_explicit_third_party_commentary("Support > Buy > CAT")
    assert is_explicit_third_party_commentary("Sources say no smart glasses this year")
    assert not is_explicit_third_party_commentary(
        "Oct 4 chart/post; user confirmed LONG position, chart quote 106.446"
    )
    assert not is_explicit_third_party_commentary("user-specified raw market mark")
    assert not is_explicit_third_party_commentary("raw issuer close 100.50")


def test_screened_core_loads_only_allowed_dates_and_tickers():
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT / "scripts")
    env["PAPER_TRADES_INFLUENCER_AI_SCREEN"] = "1"
    code = (
        "import json, model_perf_core as c; "
        "print(json.dumps({'end':c.SESSION_DATES[-1], 'tickers':sorted(c.PRICES), "
        "'events':[(e['sym'], e['note']) for e in c.parse_trades()]}))"
    )
    result = subprocess.run(
        [sys.executable, "-c", code], cwd=ROOT, env=env, text=True,
        capture_output=True, check=True,
    )
    import json
    data = json.loads(result.stdout)
    assert data["end"] == MAX_TRADINGVIEW_INPUT_DATE.isoformat()
    assert not BLOCKED_TICKERS.intersection(data["tickers"])
    assert all(not is_explicit_third_party_commentary(note) for _, note in data["events"])
    assert all(symbol != "DXY" for symbol, _ in data["events"])


def test_policy_register_preserves_allowances_and_blocks():
    with (ROOT / "data" / "influencer_ai_policy_blocklist_v1.csv").open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    decisions = {(row["Policy_Type"], row["Identifier"]): row["Decision"] for row in rows}
    assert decisions[("security_ticker", "NVDA")] == "block"
    assert decisions[("source_class", "third_party_commentary")] == "block"
    assert decisions[("source_class", "official_issuer_filing")] == "allow"
    assert decisions[("source_class", "raw_market_data")] == "allow"
