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

    def test_open_assumptions_trim_levels_and_terminal_pnl_reconcile(self):
        self.assertEqual(len(self.rows), 10)
        terminal = {row["repository_ticker"]: row for row in self.rows if row["date"] == "2026-10-23"}
        self.assertEqual(terminal["BRENT"]["entry_price"], "111.412")
        self.assertEqual(terminal["OIL"]["entry_price"], "99.04")
        self.assertEqual(terminal["BRENT"]["opened_gross_notional_usd"], "500000.00")
        self.assertEqual(terminal["OIL"]["opened_gross_notional_usd"], "500000.00")
        self.assertEqual(terminal["BRENT"]["trim_target_price"], "117")
        self.assertEqual(terminal["OIL"]["trim_target_price"], "102")
        self.assertEqual(terminal["BRENT"]["units_sold_cumulative_u"], "10")
        self.assertEqual(terminal["OIL"]["units_sold_cumulative_u"], "10")
        self.assertEqual(terminal["BRENT"]["open_units_u"], "40")
        self.assertEqual(terminal["OIL"]["open_units_u"], "40")
        self.assertEqual(terminal["BRENT"]["realized_pnl_usd"], "5015.62")
        self.assertEqual(terminal["OIL"]["realized_pnl_usd"], "2988.69")
        self.assertEqual(terminal["BRENT"]["remaining_unrealized_pnl_usd"], "21301.12")
        self.assertEqual(terminal["OIL"]["remaining_unrealized_pnl_usd"], "17810.99")
        self.assertEqual(terminal["BRENT"]["total_realized_plus_unrealized_pnl_usd"], "26316.74")
        self.assertEqual(terminal["OIL"]["total_realized_plus_unrealized_pnl_usd"], "20799.68")
        total = sum(Decimal(row["total_realized_plus_unrealized_pnl_usd"]) for row in terminal.values())
        realized = sum(Decimal(row["realized_pnl_usd"]) for row in terminal.values())
        unrealized = sum(Decimal(row["remaining_unrealized_pnl_usd"]) for row in terminal.values())
        self.assertEqual(total, Decimal("47116.42"))
        self.assertEqual(realized, Decimal("8004.31"))
        self.assertEqual(unrealized, Decimal("39112.11"))
        self.assertTrue(all(row["side"] == "LONG" for row in self.rows))

    def test_daily_marks_cover_five_sessions_and_keep_sources_distinct(self):
        expected_dates = ["2026-10-19", "2026-10-20", "2026-10-21", "2026-10-22", "2026-10-23"]
        for ticker in ("BRENT", "OIL"):
            rows = [row for row in self.rows if row["repository_ticker"] == ticker]
            self.assertEqual([row["date"] for row in rows], expected_dates)
            self.assertEqual([row["sessions_marked"] for row in rows], ["1", "2", "3", "4", "5"])
            self.assertEqual([row["units_sold_cumulative_u"] for row in rows[:4]], ["0"] * 4)
            self.assertEqual(rows[-1]["assumed_trim_date"], "2026-10-23")
        self.assertIn("BlackBull Markets Brent Cash", self.report)
        self.assertIn("TradingView TVC:USOIL", self.report)
        self.assertIn("not a complete OHLC history", self.report)
        self.assertIn("does **not** verify the intraday touch", self.report)

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
        self.assertEqual(rows[-1]["total_realized_plus_unrealized_pnl_usd"], "20799.68")


if __name__ == "__main__":
    unittest.main()
