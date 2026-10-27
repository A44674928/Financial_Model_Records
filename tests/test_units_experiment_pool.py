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
    assert [row["modeled_instrument_quantity_equivalent"] for row in rows] == [
        "82664148.28147826", "94122545.07297030"
    ]


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
    assert "$115.00" in report and "$101.00" in report
