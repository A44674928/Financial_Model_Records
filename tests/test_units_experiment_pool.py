import csv
import sys
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_units_experiment_pool as pool


def test_pool_subtracts_selected_open_books_and_splits_the_remainder_evenly():
    totals, winner, costs, rows = pool.build_rows()
    assert totals["mark_date"] == "2026-10-26"
    assert Decimal(totals["the_one_open_notional_usd"]) == Decimal("478800000.00")
    assert Decimal(totals["winner_open_notional_usd"]) == Decimal("497100395.26")
    assert winner["equal_gross_scale_factor"] == "27.201116019530"
    assert len(costs) == 7
    assert Decimal(totals["total_deductions_usd"]) == Decimal("987245895.26")
    assert Decimal(totals["remaining_pool_usd"]) == Decimal("19012754104.74")
    assert [row["ticker"] for row in rows] == ["BRENT", "OIL"]
    assert {row["allocation_usd"] for row in rows} == {"9506377052.37"}
    assert sum(Decimal(row["allocation_usd"]) for row in rows) == Decimal("19012754104.74")
    assert [row["large_unit_count"] for row in rows] == ["9", "9"]
    assert [row["small_unit_count"] for row in rows] == ["50637", "50637"]
    assert [row["residual_cash_under_small_unit_usd"] for row in rows] == ["7052.37", "7052.37"]
    assert [row["user_reported_entry_date_text"] for row in rows] == ["Sep 23", "Sep 22"]
    assert [row["modeled_entry_date"] for row in rows] == ["2026-09-23", "2026-09-22"]
    assert all("month/day but not a year" in row["entry_year_assumption"] for row in rows)
    assert [row["user_reported_entry_price_usd"] for row in rows] == ["102.315", "89.89"]
    assert [row["modeled_instrument_quantity_equivalent"] for row in rows] == [
        "92912838.31666911", "105755668.62131494"
    ]
    assert [row["current_tradingview_mark_date"] for row in rows] == ["2026-10-26", "2026-10-26"]
    assert [row["current_tradingview_mark_usd"] for row in rows] == ["115.38", "101.30"]
    assert [row["modeled_unrealized_mark_change_usd"] for row in rows] == [
        "1213906232.61", "1206672178.97"
    ]
    assert [row["lock_status_as_of_current_marks"] for row in rows] == ["LOCKED", "LOCKED"]


def test_50u_each_is_reallocated_from_foundation_to_winning_model():
    _totals, _winner, _costs, allocation_rows = pool.build_rows()
    lots = pool.build_foundation_lots(allocation_rows)
    assert len(lots) == 8
    retained = [row for row in lots if row["lot_id"] == "SUPPLEMENTAL_ORDER_FOUNDATION_REMAINDER"]
    transferred = [row for row in lots if row["lot_id"] == "TRANSFERRED_50U_TO_WINNING_MODEL"]
    combined = [row for row in lots if row["lot_id"] == "COMBINED_LOCKED_FOUNDATION"]
    assert [row["allocation_destination"] for row in transferred] == ["THE_WINNING_MODEL", "THE_WINNING_MODEL"]
    assert all(row["source_provenance"].startswith("ATS source") for row in transferred)
    assert [row["funded_notional_usd"] for row in transferred] == ["500000.00", "500000.00"]
    assert [row["quantity_equivalent_not_shares_or_contracts"] for row in transferred] == [
        "4347.82608696", "4950.49504950"
    ]
    assert [row["funded_notional_usd"] for row in retained] == ["9999500000.00", "9999500000.00"]
    assert [row["quantity_equivalent_not_shares_or_contracts"] for row in retained] == [
        "86952173.91304348", "99004950.49504950"
    ]
    assert sum(Decimal(row["funded_notional_usd"]) for row in retained + transferred) == Decimal("20000000000.00")
    assert sum(Decimal(row["funded_notional_usd"]) for row in combined) == Decimal("39011754104.74")
    assert [row["entry_or_blended_basis_usd"] for row in combined] == [
        "108.44731174", "95.26185815"
    ]
    assert [row["modeled_unrealized_mark_change_usd"] for row in combined] == [
        "1246948058.69", "1236373664.12"
    ]
    assert all("not a new fill or duplicate position" in row["execution_status"] for row in transferred)
    envelope = pool.modeled_exit_price_envelope(lots)
    assert envelope["COMBINED"]["low_pnl"].quantize(Decimal("0.01")) == Decimal("2396569687.95")
    assert envelope["COMBINED"]["high_pnl"].quantize(Decimal("0.01")) == Decimal("3266753771.99")


def test_written_csv_and_report_keep_two_stage_and_hypothetical_scope_explicit():

    pool.write_outputs()
    with pool.OUTPUT_CSV.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 2
    assert all("no order or brokerage execution" in row["execution_status"] for row in rows)
    with pool.COSTS_CSV.open(newline="", encoding="utf-8") as handle:
        costs = list(csv.DictReader(handle))
    assert len(costs) == 7
    with pool.FOUNDATION_LOTS_CSV.open(newline="", encoding="utf-8") as handle:
        foundation_lots = list(csv.DictReader(handle))
    assert len(foundation_lots) == 8
    assert sum(Decimal(row["funded_notional_usd"]) for row in foundation_lots if row["lot_id"] == "TRANSFERRED_50U_TO_WINNING_MODEL") == Decimal("1000000.00")
    report = pool.OUTPUT_REPORT.read_text(encoding="utf-8")
    assert "Historical allocation model and later user-reported exit" in report
    assert "underlying money was verified in an account" in report
    assert "Latest user-reported ATS liquidation and organization dissolution" in report
    assert "organization dissolved at a profit" in report
    assert "$2,396,569,687.95" in report and "$3,266,753,771.99" in report
    assert "$870,184,084.04" in report
    assert "approximately the prior **45 days**" in report
    assert "manual transcription/normalization" in report
    assert "TradingView account resets do not erase records already archived here" in report
    assert "$478,800,000.00" in report
    assert "$497,100,395.26" in report
    assert "$987,245,895.26" in report
    assert "$19,012,754,104.74" in report
    assert "$20,000,000,000 order scenario" in report
    assert "$39,011,754,104.74" in report
    assert "$108.44731174" in report and "$95.26185815" in report
    assert "$498,100,395.26" in report
    assert "THE WINNING MODEL" in report and "burden/capital reallocation" in report
    assert "conditional on" in report
    assert "both BRENT and OIL EOD marks to reach **$200.00**" in report
    assert "they are **not** contract, barrel, share, or broker-order quantities" in report
    assert "Sep. 23 / $102.315" in report
    assert "Sep. 22 / $89.89" in report
    assert "The year was not stated in your text" in report
    assert "not modeled as a fill or close event" in report
    assert "**Historical lock status at the last supplied TradingView close:** **LOCKED** as of **2026-10-26**" in report
    assert "$1,213,906,232.61" in report and "$1,206,672,178.97" in report
    assert "actual account PnL" in report
