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


def test_written_csv_and_report_keep_two_stage_and_hypothetical_scope_explicit():
    pool.write_outputs()
    with pool.OUTPUT_CSV.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 2
    assert all("no order or brokerage execution" in row["execution_status"] for row in rows)
    with pool.COSTS_CSV.open(newline="", encoding="utf-8") as handle:
        costs = list(csv.DictReader(handle))
    assert len(costs) == 7
    report = pool.OUTPUT_REPORT.read_text(encoding="utf-8")
    assert "User-estimated, hypothetical paper portfolio" in report
    assert "approximately the prior **45 days**" in report
    assert "manual transcription/normalization" in report
    assert "TradingView account resets do not erase records already archived here" in report
    assert "$478,800,000.00" in report
    assert "$497,100,395.26" in report
    assert "$987,245,895.26" in report
    assert "$19,012,754,104.74" in report
    assert "both** supplied BRENT and OIL EOD marks reach **$200.00**" in report
    assert "they are **not** contract, barrel, share, or broker-order quantities" in report
    assert "Sep. 23 / $102.315" in report
    assert "Sep. 22 / $89.89" in report
    assert "The year was not stated in your text" in report
    assert "not modeled as a fill or close event" in report
    assert "**LOCKED** as of supplied TradingView marks dated **2026-10-26**" in report
    assert "$1,213,906,232.61" in report and "$1,206,672,178.97" in report
    assert "not actual account PnL" in report
