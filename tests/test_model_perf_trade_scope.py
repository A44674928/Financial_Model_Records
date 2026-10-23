"""Regression coverage for chart-added trades outside the model price universe."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from model_perf_core import PRICES, UNMODELED_SYMBOLS, parse_trades  # noqa: E402


class ModelTradeScopeTests(unittest.TestCase):
    def test_model_parser_excludes_unpriced_index_fx_and_yield_books(self):
        events = parse_trades()
        modeled = {event["sym"] for event in events}
        self.assertEqual(UNMODELED_SYMBOLS, {"DXY", "EURUSD", "JPYUSD", "US10Y", "US30Y"})
        self.assertTrue(modeled.isdisjoint(UNMODELED_SYMBOLS))
        self.assertTrue(modeled.issubset(PRICES))
        self.assertEqual(len(events), 82)

    def test_chart_reconciled_positions_are_in_model_replay(self):
        events = parse_trades()
        positions = {
            (event["sym"], event["date"], event["px"])
            for event in events
            if event["kind"] == "entry"
        }
        expected = {
            ("META", "2026-09-08", 616.67),
            ("OIL", "2026-09-10", 97.32),
            ("OIL", "2026-09-24", 93.74),
            ("BRENT", "2026-10-04", 106.446),
            ("CVX", "2026-10-05", 206.83),
        }
        self.assertTrue(expected.issubset(positions))

    def test_comparison_report_states_model_coverage_and_unreconciled_master(self):
        report = Path(__file__).resolve().parents[1] / "Model Performance Comparison.md"
        text = report.read_text(encoding="utf-8")
        self.assertIn("`82` modeled log events out of `88` total 2026 log events", text)
        self.assertIn("`DXY`, `EURUSD`, `JPYUSD`, `US10Y` and `US30Y`", text)
        self.assertIn("master PnL report has not been recalculated", text)


if __name__ == "__main__":
    unittest.main()
