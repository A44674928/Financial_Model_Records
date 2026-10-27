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

    def test_dedicated_million_open_sizing_is_separate_from_equal_gross(self):
        self.assertEqual(self.summary["winning_model_1m_open_version_name"], "TWM_1M_FULL")
        self.assertEqual(self.summary["winning_model_1m_open_scale_factor"], "0.054719562244")
        self.assertEqual(self.summary["winning_model_1m_open_gross_open_notional_usd"], "1000000.00")
        self.assertEqual(self.summary["winning_model_1m_open_max_gross_open_notional_usd"], "1000000.00")
        self.assertEqual(self.summary["winning_model_1m_open_max_gross_open_notional_date"], "2026-10-26")
        self.assertEqual(self.summary["winning_model_1m_open_cumulative_gross_notional_added_usd"], "1176744.19")
        self.assertEqual(self.summary["winning_model_1m_open_terminal_pnl_usd"], "41223.62")
        self.assertEqual(self.summary["winning_model_1m_open_combined_dxy_units_per_active_eod"], "0.601915")
        self.assertEqual(self.summary["winning_model_1m_open_gross_open_notional_usd"], "1000000.00")
        self.assertIn("not a $1M PnL target", self.summary["winning_model_1m_open_sizing_basis"])
        self.assertIn("DXY terminology", self.report)
        self.assertIn("TWM_1M_FULL", self.report)
        self.assertIn("$1,176,744.19", self.report)
        self.assertIn("the-winning-model-1m-open-notional.png", self.report)

    def test_twm_1m_light_uses_confirmed_core_force_and_sidecar_scope(self):
        self.assertEqual(self.summary["twm_1m_light_version_name"], "TWM_1M_LIGHT")
        self.assertEqual(self.summary["twm_1m_light_source_portfolio"], "V3A_core_plus_V3A_force_1u")
        self.assertEqual(self.summary["twm_1m_light_scale_factor"], "0.118976799524")
        self.assertEqual(self.summary["twm_1m_light_terminal_open_notional_target_usd"], "1000000.00")
        self.assertEqual(self.summary["twm_1m_light_gross_open_notional_usd"], "1000000.00")
        self.assertEqual(self.summary["twm_1m_light_max_gross_open_notional_usd"], "1000000.00")
        self.assertEqual(self.summary["twm_1m_light_max_gross_open_notional_date"], "2026-10-26")
        self.assertEqual(self.summary["twm_1m_light_terminal_pnl_usd"], "35015.42")
        self.assertEqual(self.summary["twm_1m_light_cumulative_gross_notional_added_usd"], "1384295.06")
        scope = self.summary["twm_1m_light_construction"]
        self.assertIn("chart-directed core DXY", scope)
        self.assertIn("excludes the 10U/DAY DXY add-on", scope)
        self.assertIn("energy daily-buy sidecar", scope)
        self.assertIn("user-reported core events", scope)
        self.assertIn("TWM_1M_LIGHT", self.report)
        self.assertIn("properly scaled", self.report)

    def test_current_data_rebuild_uses_archived_scope_without_claiming_old_ratio(self):
        prefix = "twm_1m_max"
        self.assertEqual(self.summary[f"{prefix}_version_name"], "TWM_1M_MAX")
        self.assertEqual(self.summary[f"{prefix}_scale_factor"], "0.072753728629")
        self.assertEqual(self.summary[f"{prefix}_source_terminal_pnl_usd"], "677180.90")
        self.assertEqual(self.summary[f"{prefix}_source_cumulative_gross_notional_added_usd"], "16975000.00")
        self.assertEqual(self.summary[f"{prefix}_source_gross_open_notional_usd"], "13745000.00")
        self.assertEqual(self.summary[f"{prefix}_terminal_pnl_usd"], "49267.44")
        self.assertEqual(self.summary[f"{prefix}_cumulative_gross_notional_added_usd"], "1234994.54")
        self.assertEqual(self.summary[f"{prefix}_gross_open_notional_usd"], "1000000.00")
        self.assertEqual(self.summary[f"{prefix}_pnl_to_gross_added_pct"], "3.989284")
        self.assertEqual(self.summary["twm_1m_fully_funded_capital_base_usd"], "1000000.00")
        self.assertEqual(self.summary["twm_1m_max_pnl_on_funded_capital_pct"], "4.926744")
        self.assertIn("no leverage, financing, or borrowed funds", self.summary["twm_1m_cash_debit_assumption"])
        construction = self.summary[f"{prefix}_construction"]
        self.assertIn("remove the integrated chart-directed", construction)
        self.assertIn("TradingView-only energy marks", construction)
        self.assertIn("ATS/manual/user-reported", construction)
        self.assertIn("does **not** reproduce 8.88%", self.report)
        self.assertIn("8.879297%", self.report)
        self.assertIn("TWM_1M_MAX", self.report)
        self.assertIn("4.9267% of that $1M cash base", self.report)
        self.assertIn("$1,234,994.54** of additions is turnover over time", self.report)
        self.assertIn("PnL ÷ $1M fully funded cash base", self.report)

    def test_daily_export_and_chart_are_present_and_reconciled(self):
        with comparison.OUTPUT_CSV.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), 37)
        last = rows[-1]
        self.assertEqual(last["the_one_model_cumulative_gross_notional_added_usd"], "584960000.00")
        self.assertEqual(last["winning_model_equal_gross_cumulative_notional_added_usd"], "584960000.00")
        self.assertEqual(last["the_one_model_aggregate_pnl_usd"], "16457691.52")
        self.assertEqual(last["winning_model_equal_gross_pnl_usd"], "20492278.46")
        self.assertEqual(last["winning_model_1m_open_gross_open_notional_usd"], "1000000.00")
        self.assertEqual(last["winning_model_1m_open_pnl_usd"], "41223.62")
        self.assertEqual(last["winning_model_1m_open_cumulative_gross_notional_added_usd"], "1176744.19")
        self.assertEqual(last["twm_1m_light_pnl_usd"], "35015.42")
        self.assertEqual(last["twm_1m_light_cumulative_gross_notional_added_usd"], "1384295.06")
        self.assertEqual(last["twm_1m_light_gross_open_notional_usd"], "1000000.00")
        self.assertEqual(last["twm_1m_max_pnl_usd"], "49267.44")
        self.assertEqual(last["twm_1m_max_cumulative_gross_notional_added_usd"], "1234994.54")
        self.assertEqual(last["twm_1m_max_gross_open_notional_usd"], "1000000.00")
        self.assertTrue(comparison.OUTPUT_CHART.is_file())
        self.assertEqual(comparison.OUTPUT_CHART.read_bytes()[:8], b"\x89PNG\r\n\x1a\n")
        self.assertTrue(comparison.OUTPUT_1M_CHART.is_file())
        self.assertEqual(comparison.OUTPUT_1M_CHART.read_bytes()[:8], b"\x89PNG\r\n\x1a\n")
        self.assertTrue(comparison.OUTPUT_LIGHT_CHART.is_file())
        self.assertEqual(comparison.OUTPUT_LIGHT_CHART.read_bytes()[:8], b"\x89PNG\r\n\x1a\n")
        self.assertTrue(comparison.OUTPUT_MAX_CHART.is_file())
        self.assertEqual(comparison.OUTPUT_MAX_CHART.read_bytes()[:8], b"\x89PNG\r\n\x1a\n")
        self.assertIn("the-one-model-vs-winning-model.png", self.report)
        self.assertIn("Equal-gross comparison", (ROOT / "Model Performance Comparison.md").read_text(encoding="utf-8"))
        self.assertIn("THE ONE MODEL vs THE WINNING MODEL", (ROOT / "README.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
