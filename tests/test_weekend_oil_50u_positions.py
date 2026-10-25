import csv
import sys
import unittest
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_weekend_oil_50u_positions as weekend_oil


class WeekendOil50UPositionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = weekend_oil.build_rows()
        cls.report = weekend_oil.REPORT.read_text(encoding="utf-8")

    def test_open_assumptions_and_terminal_pnl_reconcile(self):
        self.assertEqual(len(self.rows), 10)
        terminal = {row["repository_ticker"]: row for row in self.rows if row["date"] == "2026-10-23"}
        self.assertEqual(terminal["BRENT"]["entry_price"], "111.412")
        self.assertEqual(terminal["OIL"]["entry_price"], "99.04")
        self.assertEqual(terminal["BRENT"]["gross_notional_usd"], "500000.00")
        self.assertEqual(terminal["OIL"]["gross_notional_usd"], "500000.00")
        self.assertEqual(terminal["BRENT"]["unrealized_pnl_usd"], "26626.40")
        self.assertEqual(terminal["OIL"]["unrealized_pnl_usd"], "22263.73")
        self.assertEqual(
            Decimal(terminal["BRENT"]["unrealized_pnl_usd"]) + Decimal(terminal["OIL"]["unrealized_pnl_usd"]),
            Decimal("48890.13"),
        )
        self.assertTrue(all(row["side"] == "LONG" for row in self.rows))

    def test_daily_marks_cover_five_sessions_and_keep_sources_distinct(self):
        expected_dates = ["2026-10-19", "2026-10-20", "2026-10-21", "2026-10-22", "2026-10-23"]
        for ticker in ("BRENT", "OIL"):
            rows = [row for row in self.rows if row["repository_ticker"] == ticker]
            self.assertEqual([row["date"] for row in rows], expected_dates)
            self.assertEqual([row["sessions_marked"] for row in rows], ["1", "2", "3", "4", "5"])
        self.assertIn("BlackBull Markets Brent Cash", self.report)
        self.assertIn("TradingView TVC:USOIL", self.report)
        self.assertIn("not a complete OHLC history", self.report)

    def test_overlay_is_linked_and_explicitly_excluded_from_main_models(self):
        self.assertIn("not included", self.report)
        self.assertIn("THE ONE MODEL's 32-portfolio aggregate", self.report)
        self.assertIn("Weekend Oil 50U Position Hypothetical.md", (ROOT / "TradingView Energy and Currency Desk Sidecars.md").read_text())
        self.assertIn("Weekend Oil 50U Position Hypothetical.md", (ROOT / "Model Performance Comparison.md").read_text())
        self.assertIn("Weekend Oil 50U Position Hypothetical", (ROOT / "Hypothetical Securities Offering Briefing.md").read_text())
        self.assertTrue(weekend_oil.CHART.is_file())
        self.assertEqual(weekend_oil.CHART.read_bytes()[:8], b"\x89PNG\r\n\x1a\n")

    def test_csv_output_matches_replay(self):
        with weekend_oil.OUTPUT_CSV.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(rows, self.rows)
        self.assertEqual(len(rows), 10)
        self.assertEqual(rows[-1]["unrealized_pnl_usd"], "22263.73")


if __name__ == "__main__":
    unittest.main()
