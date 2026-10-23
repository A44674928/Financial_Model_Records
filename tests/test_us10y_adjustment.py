"""Tests for the user-provided US10Y actual/365 baseline carry adjustment."""

import csv
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from model_perf_core import SESSION_DATES, all_series  # noqa: E402
from us10y_adjustment import (  # noqa: E402
    BASELINE_PCT,
    START_DATE,
    apply_us10y_adjustment,
)


class US10YAdjustmentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.series, _ = all_series()
        cls.rows = apply_us10y_adjustment(cls.series, SESSION_DATES)
        cls.rows_by_date = {row["date"]: row for row in cls.rows}

    def test_baseline_starts_on_sep10_and_carry_uses_actual_calendar_days(self):
        sep10 = SESSION_DATES.index(START_DATE)
        sep11 = SESSION_DATES.index("2026-09-11")
        self.assertEqual(self.series["V1"]["yield_adjustment"][sep10], 0.0)
        expected = (
            self.series["V1"]["deployed"][sep10]
            * ((4.95 - BASELINE_PCT) / 100)
            * 1
            / 365
        )
        self.assertAlmostEqual(
            self.series["V1"]["yield_adjustment_daily"][sep11], expected, places=10
        )

    def test_treasury_holiday_carries_friday_close_through_oct12(self):
        row = self.rows_by_date["2026-10-12"]
        self.assertEqual(row["yield_pct"], 5.24)
        self.assertEqual(row["source_date"], "2026-10-09")
        self.assertTrue(row["carried_forward"])
        self.assertEqual(row["accrual_days"], 3)
        self.assertEqual(row["applied_yield_pct"], 5.24)
        next_row = self.rows_by_date["2026-10-13"]
        self.assertEqual(next_row["accrual_days"], 1)
        self.assertEqual(next_row["applied_yield_pct"], 5.24)

    def test_adjusted_totals_equal_base_plus_cumulative_carry(self):
        for variant, series in self.series.items():
            self.assertGreater(series["yield_adjustment"][-1], 0)
            self.assertAlmostEqual(
                series["adjusted_total"][-1],
                series["total"][-1] + series["yield_adjustment"][-1],
                places=8,
            )
        self.assertAlmostEqual(self.series["V1"]["yield_adjustment"][-1], 158.44, places=2)
        self.assertGreater(
            self.series["V3A"]["yield_adjustment"][-1],
            self.series["V1"]["yield_adjustment"][-1],
        )

    def test_generated_exports_document_confirmed_holiday_carry(self):
        root = Path(__file__).resolve().parents[1]
        with (root / "data/model_performance_us10y_adjustment.csv").open(
            newline="", encoding="utf-8"
        ) as fh:
            output_rows = {
                (row["variant"], row["session_date"]): row
                for row in csv.DictReader(fh)
            }
        oct12 = output_rows[("V1", "2026-10-12")]
        self.assertEqual(oct12["yield_close_pct"], "5.24")
        self.assertEqual(oct12["yield_source_date"], "2026-10-09")
        self.assertEqual(oct12["yield_forward_filled"], "True")
        self.assertEqual(oct12["accrual_days"], "3")
        summary = json.loads(
            (root / "data/model_performance_summary.json").read_text(encoding="utf-8")
        )
        self.assertIn("user-confirmed", summary["us10y_adjustment"]["holiday_method"])
        report = (root / "Model Performance Comparison.md").read_text(encoding="utf-8")
        self.assertIn("Oct 9 close (5.24%) is carried across the Oct 12 Treasury holiday", report)
        self.assertIn("not a CPI inflation measure", report)


if __name__ == "__main__":
    unittest.main()
