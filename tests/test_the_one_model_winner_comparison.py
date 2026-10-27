"""Regression tests for the equal-gross THE ONE MODEL winner comparison."""
import csv
import json
import sys
import unittest
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_the_one_model_winner_comparison as comparison


class TheOneModelWinnerComparisonTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.summary = json.loads(comparison.OUTPUT_JSON.read_text(encoding="utf-8"))
        cls.report = comparison.REPORT.read_text(encoding="utf-8")

    def test_selects_the_current_top_individual_terminal_pnl_portfolio(self):
        one_model = json.loads(comparison.INPUT_SUMMARY.read_text(encoding="utf-8"))
        winner = one_model["best_terminal_pnl_portfolio"]
        self.assertEqual(self.summary["winning_portfolio_id"], winner["portfolio_id"])
        self.assertEqual(self.summary["winning_portfolio_id"], "core_v3a__1u_v3a__with_oil")
        self.assertEqual(self.summary["winning_model_original_terminal_pnl_usd"], "753361.68")
        self.assertEqual(self.summary["winning_energy_sidecar_unit_size_u_per_active_ticker"], 11)
        self.assertEqual(self.summary["winning_dxy_exposure_per_active_eod_before_scaling"], "11U/DAY")
        self.assertIn("ex post", self.summary["winner_selection_method"])

    def test_equal_gross_terminal_additions_and_metrics_reconcile(self):
        one_model = json.loads(comparison.INPUT_SUMMARY.read_text(encoding="utf-8"))
        self.assertEqual(
            self.summary["winning_model_equal_gross_cumulative_gross_notional_added_usd"],
            one_model["aggregate_cumulative_gross_notional_added_usd"],
        )
        self.assertEqual(self.summary["the_one_model_cumulative_gross_notional_added_usd"], "584960000.00")
        self.assertEqual(self.summary["winning_model_equal_gross_terminal_pnl_usd"], "20492278.46")
        self.assertEqual(self.summary["equal_gross_winner_combined_dxy_units_per_active_eod"], "299.212276")
        self.assertEqual(self.summary["equal_gross_terminal_pnl_difference_winner_minus_one_model_usd"], "4034586.94")
        self.assertEqual(self.summary["winning_model_equal_gross_pnl_to_gross_added_pct"], "3.503193")
        self.assertEqual(self.summary["the_one_model_pnl_to_gross_added_pct"], "2.813473")
        self.assertIn("selection bias", self.summary["equal_gross_winner_selection_caveat"])
        self.assertIn("not an assertion", self.report)

    def test_daily_export_and_chart_are_present_and_reconciled(self):
        with comparison.OUTPUT_CSV.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), 37)
        last = rows[-1]
        self.assertEqual(last["the_one_model_cumulative_gross_notional_added_usd"], "584960000.00")
        self.assertEqual(last["winning_model_equal_gross_cumulative_notional_added_usd"], "584960000.00")
        self.assertEqual(last["the_one_model_aggregate_pnl_usd"], "16457691.52")
        self.assertEqual(last["winning_model_equal_gross_pnl_usd"], "20492278.46")
        self.assertTrue(comparison.OUTPUT_CHART.is_file())
        self.assertEqual(comparison.OUTPUT_CHART.read_bytes()[:8], b"\x89PNG\r\n\x1a\n")
        self.assertIn("the-one-model-vs-winning-model.png", self.report)
        self.assertIn("Equal-gross comparison", (ROOT / "Model Performance Comparison.md").read_text(encoding="utf-8"))
        self.assertIn("THE ONE MODEL vs THE WINNING MODEL", (ROOT / "README.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
