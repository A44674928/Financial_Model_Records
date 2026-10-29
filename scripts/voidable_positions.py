"""Lot-level replay helpers for scenario-voided position events.

Source events are never deleted. A replay can suppress an OPEN event (and its
linked close lifecycle) or suppress a CLOSE event so the linked position stays
open. Book and lot IDs isolate positions against accidental cross-book netting.
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Iterable


@dataclass(frozen=True)
class PositionEvent:
    event_id: str
    book: str
    ticker: str
    event_type: str  # OPEN or CLOSE
    side: str  # LONG or SHORT; a CLOSE applies to that side's identified lot
    quantity: Decimal
    lot_id: str
    voided: bool = False
    void_reason: str = ""


def rebuild_open_lots(events: Iterable[PositionEvent]) -> dict[tuple[str, str, str], Decimal]:
    """Replay events, skipping only events explicitly voided in this scenario."""
    event_list = list(events)
    lots: dict[tuple[str, str, str], Decimal] = {}
    lot_sides: dict[tuple[str, str, str], str] = {}
    event_ids: set[str] = set()
    voided_open_lots: set[tuple[str, str, str]] = set()

    for event in event_list:
        if event.event_id in event_ids:
            raise ValueError(f"duplicate event_id: {event.event_id}")
        event_ids.add(event.event_id)
        if event.quantity <= 0:
            raise ValueError(f"event quantity must be positive: {event.event_id}")
        if event.side not in {"LONG", "SHORT"}:
            raise ValueError(f"unsupported side for {event.event_id}: {event.side}")
        if event.event_type not in {"OPEN", "CLOSE"}:
            raise ValueError(f"unsupported event_type for {event.event_id}: {event.event_type}")
        if event.voided and not event.void_reason.strip():
            raise ValueError(f"voided event requires an audit reason: {event.event_id}")
        if event.voided and event.event_type == "OPEN":
            voided_open_lots.add((event.book, event.ticker, event.lot_id))

    for event in event_list:
        key = (event.book, event.ticker, event.lot_id)
        if key in voided_open_lots:
            # A nullified opening suppresses its linked close lifecycle too.
            continue
        if event.event_type == "OPEN":
            if event.voided:
                continue
            existing_side = lot_sides.get(key)
            if existing_side is not None and existing_side != event.side:
                raise ValueError(f"lot side mismatch for {event.event_id}")
            lot_sides[key] = event.side
            lots[key] = lots.get(key, Decimal("0")) + event.quantity
        else:  # CLOSE
            available = lots.get(key, Decimal("0"))
            if lot_sides.get(key) != event.side:
                raise ValueError(f"close {event.event_id} side does not match its linked lot")
            if event.quantity > available:
                raise ValueError(
                    f"close {event.event_id} exceeds lot {event.lot_id}: "
                    f"{event.quantity} > {available}"
                )
            if not event.voided:
                lots[key] = available - event.quantity
    return {key: quantity for key, quantity in lots.items() if quantity}
