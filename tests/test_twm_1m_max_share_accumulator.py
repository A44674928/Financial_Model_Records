"""Integration checks for the TWM_1M_MAX share-accumulator companion."""
import csv
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from build_twm_1m_max_share_accumulator import build  # noqa: E402


class TWM1MMaxShareAccumulatorIntegrationTests(unittest.TestCase):
    def test_generated_companion_preserves_baseline_and_energy_unit_separation(self):
        result = build()
        with (ROOT / "data" / "the_one_model_vs_winning_model_v1.csv").open(
            newline="", encoding="utf-8"
        ) as handle:
            base_rows = list(csv.DictReader(handle))
        with (ROOT / "data" / "twm_1m_max_share_accumulator_ticker_summary_v1.csv").open(
            newline="", encoding="utf-8"
        ) as handle:
            ticker_rows = list(csv.DictReader(handle))

        self.assertEqual(base_rows[-1]["twm_1m_max_pnl_usd"], "49267.44")
        self.assertEqual(result["baseline_twm_1m_max_pnl_usd"], "49267.44")
        self.assertTrue(result["baseline_twm_1m_max_pnl_unchanged"])
        self.assertEqual(result["unrealized_gains_reinvested"], False)
        self.assertEqual(result["purchase_timing"], "first supplied TradingView EOD mark strictly after realization date")
        self.assertEqual(result["energy_unit_value_usd"], "10000.00")
        self.assertEqual(result["pending_realized_pnl_for_next_supplied_mark_usd"], "4406.61")
        self.assertEqual(result["additional_out_of_pocket_cash_usd"], "0.00")
        self.assertEqual(result["share_count_chart"], "Charts/superstructure/twm-1m-max-share-counts.png")
        self.assertTrue((ROOT / result["share_count_chart"]).exists())
        report = (ROOT / "TWM_1M_MAX Realized-PnL Share Accumulator.md").read_text(encoding="utf-8")
        self.assertIn("Share counts through time", report)
        self.assertIn("independent share-count axes", report)

        by_ticker = {row["ticker"]: row for row in ticker_rows}
        for ticker in ("BRENT", "OIL"):
            self.assertEqual(by_ticker[ticker]["asset_tracker_type"], "model_U_equivalent")
        for row in ticker_rows:
            if row["ticker"] not in {"BRENT", "OIL"}:
                self.assertEqual(row["asset_tracker_type"], "fractional_share")

        self.assertAlmostEqual(
            sum(float(row["accumulator_net_pnl_usd"]) for row in ticker_rows),
            float(result["accumulator_incremental_net_pnl_usd"]),
            places=2,
        )
        with (ROOT / "data" / "twm_1m_max_share_accumulator_v1_summary.json").open(
            encoding="utf-8"
        ) as handle:
            saved = json.load(handle)
        self.assertEqual(saved, result)


if __name__ == "__main__":
    unittest.main()
