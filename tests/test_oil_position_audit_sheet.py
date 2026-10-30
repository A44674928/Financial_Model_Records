import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_oil_position_sheet_contains_base_and_reinstated_scenario_rows():
    path = ROOT / "data" / "oil_position_audit_sheet_v1.csv"
    rows = list(csv.DictReader(path.open(newline="", encoding="utf-8-sig")))
    counts = Counter(row["row_type"] for row in rows)
    assert counts["ACTIVE_OIL_MODEL_POSITION"] == 18
    assert counts["UNDER_DURESS_RESTORED_LONG"] == 14
    assert counts["ATS_FOUNDATION_RESTORATION"] == 2
    assert counts["REINSTATED_NULLIFIED_SHORT_LIFECYCLE"] == 8
    assert counts["ATS_SCENARIO_RESIDUAL_LONG"] == 8
    assert counts["LEGACY_BASELINE_SHORT_EVENT"] == 2
    assert {row["size_group"] for row in rows} == {"SMALL_UNITS", "LARGE_UNITS", "UNKNOWN_UNIT_CONVENTION"}
    assert all("<=1U" in row["size_rule"] or "unknown" in row["size_rule"].lower() or "unavailable" in row["size_rule"].lower() or "no contract/unit multiplier" in row["size_rule"].lower() for row in rows)


def test_un_nullified_short_sensitivities_remain_hypothetical_and_non_additive():
    rows = list(csv.DictReader((ROOT / "data" / "oil_position_audit_sheet_v1.csv").open(newline="", encoding="utf-8-sig")))
    shorts = [row for row in rows if row["row_type"] == "REINSTATED_NULLIFIED_SHORT_LIFECYCLE"]
    assert len(shorts) == 8
    assert {(row["ticker"], row["quantity"]) for row in shorts} == {
        (ticker, size) for ticker in ("BRENT", "OIL") for size in ("10", "20", "30", "40")
    }
    assert all(row["test_override_state"] == "UN-NULLIFIED / REINSTATED FOR AUDIT TEST ONLY" for row in shorts)
    assert all("CLOSED IN REINSTATED HYPOTHETICAL LIFECYCLE" in row["position_state"] for row in shorts)
    assert all("ALTERNATIVE SENSITIVITY" in row["additivity_rule"] for row in shorts)
    assert all(row["count_in_core_v2"].startswith("NO") for row in shorts)
    assert all("not evidence an actual short was executed" in row["audit_notes"] for row in shorts)


def test_private_fund_oil_longs_remain_open_after_close_nullification_without_using_close_as_mark():
    rows = list(csv.DictReader((ROOT / "data" / "oil_position_audit_sheet_v1.csv").open(newline="", encoding="utf-8-sig")))
    pf = [row for row in rows if row["position_id"] in {"PF-BRENT-CLOSE-20261029", "PF-USOIL-CLOSE-20261029"}]
    assert len(pf) == 2
    assert {(row["ticker"], row["quantity"], row["entry_price_usd"]) for row in pf} == {
        ("BRENT", "538566907", "114.043"), ("USOIL", "601218118", "99.18")
    }
    assert all(row["position_state"].startswith("OPEN;") for row in pf)
    assert all(not row["valuation_mark_usd"] and not row["conditional_unrealized_pnl_usd"] for row in pf)
    assert all(not row["gross_basis_usd"] and not row["u_equivalent"] for row in pf)
    assert all(row["size_group"] == "UNKNOWN_UNIT_CONVENTION" for row in pf)
    assert all("NULLIFIED AND VOIDED" in row["source_nullification_state"] for row in pf)
    assert all("source_reported_close_price" in row["audit_notes"] for row in pf)


def test_base_oil_sheet_total_matches_version_two_without_summing_scenarios():
    rows = list(csv.DictReader((ROOT / "data" / "oil_position_audit_sheet_v1.csv").open(newline="", encoding="utf-8-sig")))
    base = [row for row in rows if row["row_type"] == "ACTIVE_OIL_MODEL_POSITION"]
    assert all(row["valuation_date"] == "2026-10-26" for row in base)
    assert all(row["count_in_core_v2"] == "YES" for row in base)
    row_sum = sum(float(row["scenario_total_pnl_usd"]) for row in base)
    assert abs(row_sum - 42935.36) < 0.02  # Row-level cent rounding can differ by one cent from aggregate PnL.
    assert all(row["valuation_date"] != "2026-10-29" for row in base)
