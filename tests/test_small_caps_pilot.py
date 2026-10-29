import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_small_caps_pilot as pilot


def test_pilot_daily_marks_and_open_lot_pnl():
    entries, rows = pilot.pilot_daily_series()
    assert len(entries) == 5
    assert [row["date"] for row in rows] == [
        "2026-10-20", "2026-10-21", "2026-10-22", "2026-10-23"
    ]
    assert [row["lcid_mark_usd"] for row in rows] == [3.27, 3.21, 3.46, 3.52]
    assert [row["entries_active"] for row in rows] == [2, 3, 4, 5]
    assert [row["deployed_notional_usd"] for row in rows] == [20_000, 30_000, 40_000, 50_000]
    assert pilot.load_marks()["2026-10-23"] == 3.52
    root = Path(__file__).resolve().parents[1]
    with (root / "data/lcid_small_caps_pilot_daily_marks_v1.csv").open() as fh:
        assert "2026-10-23,3.55," in fh.read()

    oct22 = rows[2]
    expected_oct22 = sum(10_000 * (3.46 / entry["px"] - 1) for entry in entries[:4])
    assert abs(oct22["unrealized_pnl_usd"] - expected_oct22) < 1e-8
    oct23 = rows[3]
    expected_oct23 = sum(10_000 * (3.52 / entry["px"] - 1) for entry in entries)
    assert abs(oct23["unrealized_pnl_usd"] - expected_oct23) < 1e-8


def test_current_date_hypothetical_offer_uses_market_cap_terms_not_per_share():
    root = Path(__file__).resolve().parents[1]
    offer = (root / "Small Caps [Buyout & Reorganization Offering Test Pilot].md").read_text(encoding="utf-8")
    assert "Current-date hypothetical buyout offer — 2026-10-29" in offer
    assert "$1,310,000,000" in offer
    assert "$2,000,000,000" in offer
    assert "$2,200,000,000" in offer
    assert "$4,200,000,000" in offer
    assert "52.67%" in offer
    assert "220.61% above" in offer
    assert "No share count" in offer
    assert "not a per-share premium calculation" in offer
