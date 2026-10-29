from decimal import Decimal

import pytest

from scripts.voidable_positions import PositionEvent, rebuild_open_lots


def event(event_id, event_type, quantity, *, book="ATS", ticker="BRENT", side="LONG", voided=False, void_reason=""):
    return PositionEvent(
        event_id=event_id,
        book=book,
        ticker=ticker,
        event_type=event_type,
        side=side,
        quantity=Decimal(quantity),
        lot_id="lot-1",
        voided=voided,
        void_reason=void_reason,
    )


def test_voided_close_preserves_original_lot_and_audit_event():
    events = [
        event("open", "OPEN", "50"),
        event("sale", "CLOSE", "20", voided=True, void_reason="under duress"),
    ]
    assert rebuild_open_lots(events) == {("ATS", "BRENT", "lot-1"): Decimal("50")}


def test_nullifying_short_open_suppresses_its_linked_close_lifecycle():
    events = [
        event("short-open", "OPEN", "20", side="SHORT", voided=True, void_reason="under duress"),
        event("short-cover", "CLOSE", "20", side="SHORT", voided=True, void_reason="under duress"),
    ]
    assert rebuild_open_lots(events) == {}


def test_nonvoided_close_reduces_only_its_book_and_lot():
    events = [
        event("open", "OPEN", "50"),
        event("other-book-open", "OPEN", "30", book="Manual"),
        event("sale", "CLOSE", "20"),
    ]
    assert rebuild_open_lots(events) == {
        ("ATS", "BRENT", "lot-1"): Decimal("30"),
        ("Manual", "BRENT", "lot-1"): Decimal("30"),
    }


def test_close_cannot_exceed_linked_lot_even_when_not_voided():
    with pytest.raises(ValueError, match="exceeds lot"):
        rebuild_open_lots([event("open", "OPEN", "10"), event("sale", "CLOSE", "11")])


def test_duplicate_event_ids_are_rejected():
    with pytest.raises(ValueError, match="duplicate event_id"):
        rebuild_open_lots([event("same", "OPEN", "10"), event("same", "OPEN", "10")])


def test_voided_close_requires_a_reason_and_matching_lot_side():
    with pytest.raises(ValueError, match="audit reason"):
        rebuild_open_lots([event("open", "OPEN", "10"), event("close", "CLOSE", "1", voided=True)])
    with pytest.raises(ValueError, match="side does not match"):
        rebuild_open_lots([
            event("open", "OPEN", "10"),
            event("close", "CLOSE", "1", side="SHORT", voided=True, void_reason="under duress"),
        ])
