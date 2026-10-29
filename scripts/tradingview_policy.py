"""Strict TradingView source-date policy for this repository.

TradingView-derived inputs dated October 20, 2026 or later are blocked from
new analytical use. Existing rows may be classified as legacy exceptions for
preservation/audit only; the exception classification is not permission to
recompute active outputs.
"""

from datetime import date

POLICY_EFFECTIVE_DATE = date(2026, 10, 20)  # Oct. 19 remains permitted.
STATUS_PRE_CUTOFF = "ALLOWED_PRE_CUTOFF"
STATUS_NON_TRADINGVIEW = "NOT_TRADINGVIEW"
STATUS_BLOCKED = "BLOCKED_POST_CUTOFF"
STATUS_LEGACY_EXCEPTION = "FLAGGED_LEGACY_EXCEPTION_NOT_FOR_ACTIVE_USE"


class TradingViewPolicyError(ValueError):
    """Raised when a prohibited TradingView input is submitted for active use."""


def is_tradingview_source(source: str) -> bool:
    normalized = (source or "").strip().casefold()
    return any(marker in normalized for marker in ("tradingview", "trading view", "tvc:"))


def classify_source_date(source: str, source_date: str | date, *, existing_exception: bool = False) -> str:
    """Classify a source/date pair without treating legacy exceptions as allowed."""
    if not is_tradingview_source(source):
        return STATUS_NON_TRADINGVIEW
    day = source_date if isinstance(source_date, date) else date.fromisoformat(source_date[:10])
    if day < POLICY_EFFECTIVE_DATE:
        return STATUS_PRE_CUTOFF
    return STATUS_LEGACY_EXCEPTION if existing_exception else STATUS_BLOCKED


def require_active_input_allowed(source: str, source_date: str | date) -> None:
    """Reject a prohibited source before it enters an active model or trade log."""
    status = classify_source_date(source, source_date)
    if status in {STATUS_BLOCKED, STATUS_LEGACY_EXCEPTION}:
        raise TradingViewPolicyError(
            f"TradingView input dated {source_date} is blocked by the "
            f"post-2026-10-19 policy ({POLICY_EFFECTIVE_DATE.isoformat()} onward)."
        )


def classify_existing_record(source: str, source_date: str | date) -> str:
    """Label a preserved historical record; never approves it for active use."""
    return classify_source_date(source, source_date, existing_exception=True)
