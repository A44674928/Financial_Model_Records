from datetime import date
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from tradingview_policy import (  # noqa: E402
    POLICY_EFFECTIVE_DATE,
    STATUS_BLOCKED,
    STATUS_LEGACY_EXCEPTION,
    STATUS_NON_TRADINGVIEW,
    STATUS_PRE_CUTOFF,
    TradingViewPolicyError,
    classify_existing_record,
    classify_source_date,
    require_active_input_allowed,
)


def test_date_boundary_is_after_october_19():
    assert POLICY_EFFECTIVE_DATE == date(2026, 10, 20)
    assert classify_source_date("TradingView Paper Trading", "2026-10-19") == STATUS_PRE_CUTOFF
    assert classify_source_date("TradingView", "2026-10-20") == STATUS_BLOCKED
    assert classify_source_date("Yahoo Finance", "2026-10-20") == STATUS_NON_TRADINGVIEW


def test_existing_post_cutoff_record_is_flagged_but_not_allowed_for_active_use():
    assert classify_existing_record("TradingView chart", "2026-10-26") == STATUS_LEGACY_EXCEPTION
    with pytest.raises(TradingViewPolicyError, match="post-2026-10-19 policy"):
        require_active_input_allowed("TradingView EOD marks", "2026-10-26")


def test_pre_cutoff_and_non_tradingview_inputs_pass_guard():
    require_active_input_allowed("TradingView price list", "2026-10-19")
    require_active_input_allowed("BlackBull Markets", "2026-10-26")


def test_tvc_symbol_is_classified_as_tradingview_source():
    with pytest.raises(TradingViewPolicyError):
        require_active_input_allowed("TVC:USOIL chart", "2026-10-20")
