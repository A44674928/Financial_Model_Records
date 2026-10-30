import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_rows(path):
    with (ROOT / path).open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def test_october_28_register_keeps_books_and_statuses_separate():
    rows = read_rows("data/multi_asset_account_statement_2026-10-28_v1.csv")
    assert len(rows) == 236
    assert all(row["statement_as_of_date"] == "2026-10-28" for row in rows)
    assert not any(row["record_as_of_date"].startswith("2026-10-29") for row in rows)
    counts = Counter(row["row_category"] for row in rows)
    assert counts["SCREENED_MAIN_MODEL_OPEN_LOT"] == 98
    assert counts["OIL_V2_BASE_POSITION"] == 18
    assert counts["OIL_AUDIT_SCENARIO_OR_REFERENCE"] == 46
    assert counts["AI_FUND_HISTORICAL_EVENT_AUDIT_ONLY"] == 41
    assert counts["USER_DIRECTED_POSITION_SNAPSHOT"] == 1
    assert counts["PRIVATE_FUND_POSITION_SNAPSHOT"] == 1
    assert counts["PRIVATE_FUND_OPEN_POSITION_RESTORED"] == 2

    main = [row for row in rows if row["row_category"] == "SCREENED_MAIN_MODEL_OPEN_LOT"]
    assert {row["variant"] for row in main} == {"V1", "V2", "V3A", "V3B"}
    assert not ({"AAPL", "AMZN", "INTC", "META", "NVDA", "PLTR", "TSLA", "BRENT", "OIL", "CVX", "VLO", "XLE"} & {row["ticker"] for row in main})
    assert all(row["record_as_of_date"] == "2026-10-19" for row in main)
    oil = [row for row in rows if row["row_category"] == "OIL_V2_BASE_POSITION"]
    assert all(row["mark_date_or_time"] == "2026-10-26" for row in oil)
    assert all(row["policy_status"].startswith("USER_AUTHORIZED_SCOPED_OIL_V2") for row in oil)


def test_october_28_register_includes_source_audit_but_no_october_29_lcid_trade():
    rows = read_rows("data/multi_asset_account_statement_2026-10-28_v1.csv")
    scenarios = [row for row in rows if row.get("test_override_state") == "UN-NULLIFIED / REINSTATED FOR AUDIT TEST ONLY"]
    shorts = [row for row in scenarios if row["source_row_type"] == "REINSTATED_NULLIFIED_SHORT_LIFECYCLE"]
    assert len(shorts) == 8
    assert all("ALTERNATIVE SENSITIVITY" in row["additivity_rule"] for row in shorts)
    assert any(row["ticker"] == "ALIUSD" and row["record_as_of_date"].startswith("2026-10-28") for row in rows)
    assert any(row["ticker"] == "LCID" and row["row_category"] == "PRIVATE_FUND_POSITION_SNAPSHOT" for row in rows)
    open_longs = [row for row in rows if row["row_category"] == "PRIVATE_FUND_OPEN_POSITION_RESTORED"]
    assert {(row["ticker"], row["quantity"], row["entry_price_usd_or_quote"]) for row in open_longs} == {
        ("BRENT", "538566907", "114.043000"), ("USOIL", "601218118", "99.180000")
    }
    assert all(row["side_or_action"] == "LONG OPEN" and not row["mark_price_usd_or_quote"] for row in open_longs)
    assert all("nullified and voided" in row["position_or_record_status"].lower() for row in open_longs)
    assert sum(row["row_category"] == "POST_CUTOFF_LCID_PILOT_LOT" for row in rows) == 5
    assert not any(row["source_record_id"] == "3736492349" for row in rows)
    assert all(row["policy_status"].startswith("EXCLUDED FROM ACTIVE MODEL") for row in rows if row["row_category"] == "AI_FUND_HISTORICAL_EVENT_AUDIT_ONLY")


def test_october_29_change_log_distinguishes_transactions_from_scenarios_and_controls():
    rows = read_rows("data/account_change_log_2026-10-29_v1.csv")
    assert len(rows) == 9
    oil = [row for row in rows if row["change_type"] == "OIL CLOSE NULLIFIED AND VOIDED PER USER INSTRUCTION"]
    assert len(oil) == 2
    assert round(sum(float(row["source_reported_pnl_usd"]) for row in oil), 2) == 2713480646.02
    assert all(row["reported_transaction_pnl_usd"] == "0.00" for row in oil)
    assert all("KEEP LONG OPEN" in row["side_or_action"] for row in oil)
    retained = [row for row in rows if row["change_type"] == "EARLIER OIL LONG RETAINED OPEN"]
    assert len(retained) == 2
    lcid = next(row for row in rows if row["change_type"] == "FILLED BUY ORDER")
    assert lcid["side_or_action"] == "BUY MARKET"
    assert lcid["reported_transaction_pnl_usd"] == "0.00"
    offer = next(row for row in rows if row["change_type"] == "HYPOTHETICAL LCID OFFER REFERENCE")
    assert "1310000000.00" in offer["close_or_offer_value"]
    assert "per-share" in offer["position_effect"]
    assert all(row["change_date"] == "2026-10-29" for row in rows)
