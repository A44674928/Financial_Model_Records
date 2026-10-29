import csv
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def rows(relative_path):
    with (ROOT / relative_path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def test_void_replay_restores_separate_oil_books_and_keeps_source_events():
    events = rows("data/under_duress_oil_void_events_v1.csv")
    positions = rows("data/under_duress_oil_restored_positions_v1.csv")
    by_id = {row["event_id"]: row for row in positions}
    assert len(events) == 24
    assert len(positions) == 16
    assert len({row["event_id"] for row in events}) == 24
    assert all(row["void_status"].startswith("VOIDED_IN_UNDER_DURESS_SCENARIO") for row in positions)
    nullified = [row for row in events if row["position_effect"] == "NULLIFY_SHORT_NO_POSITION"]
    assert len(nullified) == 8
    assert all(row["restored_quantity"] == "0" and row["restored_side"] == "NONE" for row in nullified)
    assert not [row for row in positions if row["restored_side"] == "SHORT"]

    brent_foundation = by_id["ATS-FOUNDATION-BRENT-LIQ"]
    oil_foundation = by_id["ATS-FOUNDATION-OIL-LIQ"]
    assert Decimal(brent_foundation["restored_quantity"]) == Decimal("179865012.22971259")
    assert Decimal(oil_foundation["restored_quantity"]) == Decimal("204760619.11636445")
    assert brent_foundation["mark_date"] == oil_foundation["mark_date"] == "2026-10-26"
    assert Decimal(brent_foundation["conditional_unrealized_pnl_usd"]) == Decimal("1246948058.69")
    assert Decimal(oil_foundation["conditional_unrealized_pnl_usd"]) == Decimal("1236373664.12")

    screenshot_brent = by_id["PF-BRENT-CLOSE-20261029"]
    screenshot_oil = by_id["PF-USOIL-CLOSE-20261029"]
    assert Decimal(screenshot_brent["conditional_unrealized_pnl_usd"]) == Decimal("933875016.74")
    assert Decimal(screenshot_oil["conditional_unrealized_pnl_usd"]) == Decimal("1779605629.28")
    assert screenshot_brent["reported_realized_pnl_if_sale_stands_usd"] == "933875016.74"
    assert screenshot_oil["reported_realized_pnl_if_sale_stands_usd"] == "1779605629.28"
    assert "not realized" in (ROOT / "reports/Under-Duress Oil Sale Void Replay.md").read_text(encoding="utf-8")


def test_ats_sensitivities_nullify_shorts_and_funding_is_hypothetical_unallocated():
    events = rows("data/under_duress_oil_void_events_v1.csv")
    short_events = [row for row in events if row["position_effect"] == "NULLIFY_SHORT_NO_POSITION"]
    assert len(short_events) == 8
    assert sorted({int(row["scenario"].split("U")[0]) for row in short_events}) == [10, 20, 30, 40]
    assert all("no open short" in row["action_voided"] for row in short_events)
    positions = rows("data/under_duress_oil_restored_positions_v1.csv")
    assert not [row for row in positions if row["restored_side"] == "SHORT"]

    funding = rows("data/under_duress_lcid_scenario_funding_v1.csv")
    assert len(funding) == 1
    row = funding[0]
    assert Decimal(row["cash_component_usd"]) == Decimal("2200000000.00")
    assert Decimal(row["equity_component_usd"]) == Decimal("2000000000.00")
    assert Decimal(row["total_consideration_usd"]) == Decimal("4200000000.00")
    assert row["funding_status"] == "Hypothetical offer only; not a completed transaction"
    assert row["allocation_status"] == "Unallocated scenario restoration pool"

    report = (ROOT / "reports/Under-Duress Oil Sale Void Replay.md").read_text(encoding="utf-8")
    assert "not a change to source history" in report
    assert "not included in a cash balance or reconciled NAV" in report
    assert "not additive positions" in report or "not additive" in report
    assert "buy a few more barrels every couple dollars" in report
    assert "private portfolio" in report
    audit_log = (ROOT / "reports/Under-Duress Audit Rollback Log.md").read_text(encoding="utf-8")
    assert "ATS flagged sell orders for manual review" in audit_log
    assert "was supplied in the repository" in audit_log
