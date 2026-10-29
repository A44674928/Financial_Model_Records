"""Influencer / AI-source and issuer-screen policy for active paper-model replays.

The policy is intentionally source-based: raw market observations and official
issuer filings remain eligible, while third-party commentary and AI-generated
recommendations are not. The ticker screen is separately user-approved.
"""

from __future__ import annotations

import re
from datetime import date, timedelta

POLICY_EFFECTIVE_DATE = date(2026, 10, 29)

# User-approved broad AI-exposure screen (not an independently researched
# taxonomy of every AI-related security).
BLOCKED_TICKERS = frozenset({"NVDA", "PLTR", "META", "AMZN", "TSLA", "AAPL", "INTC"})

# Source classes explicitly retained by the user.
ALLOWED_SOURCE_CLASSES = frozenset({
    "official_issuer_filing",
    "raw_market_data",
    "user_trade_ledger",
})
BLOCKED_SOURCE_CLASSES = frozenset({
    "influencer_commentary",
    "third_party_commentary",
    "ai_generated_commentary",
    "ai_company_commentary",
})

# The shared TradingView cutoff remains in force. This derives its last allowed
# date rather than duplicating the date independently.
from tradingview_policy import POLICY_EFFECTIVE_DATE as TRADINGVIEW_POLICY_EFFECTIVE_DATE

MAX_TRADINGVIEW_INPUT_DATE = TRADINGVIEW_POLICY_EFFECTIVE_DATE - timedelta(days=1)

# Evidence-based retrospective event filter. It blocks events whose own
# provenance notes explicitly identify an external/community post, a signal
# badge, or an external recommendation. It deliberately does not infer a
# third-party author from a bare price/mark or user-directed entry.
_COMMENTARY_PATTERNS = (
    re.compile(r"\bTradingView\s+(?:community\s+)?post\b", re.I),
    re.compile(r"\b(?:LONG|SHORT)\s+badge\b", re.I),
    re.compile(r"\bSupport\s*>\s*Buy\b", re.I),
    re.compile(r"\bBuy\s+(?:CAT|Disney|PLTR)\b", re.I),
    re.compile(r"\bSources say\b", re.I),
)

_USER_DIRECTED_ACTION = re.compile(
    r"\buser[- ](?:confirmed|directed|requested|specified|reported)\b", re.I
)


def is_explicit_third_party_commentary(note: str) -> bool:
    """Return True only where a note identifies third-party commentary.

    An explicit user-confirmed/directed/requested/specified/reported action is
    treated as the user's ledger event, not as third-party commentary. A raw
    chart or market quote alone is not commentary.
    """
    note = note or ""
    if _USER_DIRECTED_ACTION.search(note):
        return False
    return any(pattern.search(note) for pattern in _COMMENTARY_PATTERNS)


class InfluencerAIPolicyError(ValueError):
    """Raised when an input fails the active source/security screen."""


def source_class_allowed(source_class: str) -> bool:
    """Check a normalized source class against the allowlist; default deny."""
    return (source_class or "").strip().lower() in ALLOWED_SOURCE_CLASSES


def ticker_allowed(ticker: str) -> bool:
    """Return False for the approved issuer screen (case-insensitive)."""
    return (ticker or "").strip().upper() not in BLOCKED_TICKERS


def require_active_input_allowed(source_class: str, ticker: str | None = None) -> None:
    """Fail closed unless both source class and optional ticker are allowed."""
    if not source_class_allowed(source_class):
        raise InfluencerAIPolicyError(
            f"Source class {source_class!r} is not allowed by the influencer/AI block"
        )
    if ticker is not None and not ticker_allowed(ticker):
        raise InfluencerAIPolicyError(
            f"Ticker {ticker!r} is blocked by the approved AI-exposure screen"
        )
