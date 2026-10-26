"""Regression coverage for the separate daily-buy oil-desk scenario."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from build_oil_desk_hypothetical import build_rows, load_energy_marks  # noqa: E402


class OilDeskHypotheticalTests(unittest.TestCase):
    def test_daily_buy_lots_and_chart_positions_are_separate_and_combined(self):
        rows = build_rows()
        terminal = {ticker: next(row for row in reversed(rows) if row["ticker"] == ticker)
                    for ticker in ("BRENT", "OIL")}
        self.assertEqual(sum(row["ticker"] == "BRENT" for row in rows), 23)
        self.assertEqual(sum(row["ticker"] == "OIL" for row in rows), 32)
        self.assertEqual(terminal["BRENT"]["cumulative_daily_buy_units"], 230)
        self.assertEqual(terminal["BRENT"]["cumulative_daily_buy_notional_usd"], "2300000.00")
        self.assertEqual(terminal["BRENT"]["daily_buys_unrealized_pnl_usd"], "224358.86")
        self.assertEqual(terminal["BRENT"]["chart_open_units"], "55")
        self.assertEqual(terminal["BRENT"]["chart_positions_unrealized_pnl_usd"], "26032.81")
        self.assertEqual(terminal["BRENT"]["combined_energy_unrealized_pnl_usd"], "250391.67")
        self.assertEqual(terminal["BRENT"]["eod_close"], "117.345")
        self.assertEqual(terminal["BRENT"]["source"], "User-provided BlackBull Markets Brent Cash EOD")
        self.assertEqual(terminal["OIL"]["cumulative_daily_buy_units"], 320)
        self.assertEqual(terminal["OIL"]["cumulative_daily_buy_notional_usd"], "3200000.00")
        self.assertEqual(terminal["OIL"]["daily_buys_unrealized_pnl_usd"], "275347.06")
        self.assertEqual(terminal["OIL"]["chart_open_units"], "56")
        self.assertEqual(terminal["OIL"]["chart_positions_unrealized_pnl_usd"], "23003.98")
        self.assertEqual(terminal["OIL"]["combined_energy_unrealized_pnl_usd"], "298351.04")
        self.assertEqual(terminal["OIL"]["eod_close"], "103.45")
        self.assertEqual(terminal["OIL"]["source"], "User-provided TradingView TVC:USOIL EOD")
        first_brent = next(row for row in rows if row["ticker"] == "BRENT")
        first_oil = next(row for row in rows if row["ticker"] == "OIL")
        self.assertEqual(first_brent["date"], "2026-09-23")
        self.assertEqual(first_oil["date"], "2026-09-10")
        self.assertEqual(first_brent["daily_buys_unrealized_pnl_usd"], "0.00")
        self.assertEqual(first_oil["daily_buys_unrealized_pnl_usd"], "0.00")
        marks = load_energy_marks()
        self.assertEqual(len(marks["BRENT"]), 23)
        self.assertEqual(len(marks["OIL"]), 32)
        self.assertEqual(marks["BRENT"]["2026-10-23"]["close"], 117.345)
        self.assertEqual(marks["OIL"]["2026-10-23"]["close"], 103.45)
        report = Path(__file__).resolve().parents[1] / "Oil Desk EOD Accumulation Hypothetical.md"
        report_text = report.read_text(encoding="utf-8")
        self.assertIn("same exact daily energy marks", report_text)
        self.assertIn("energy_provider_eod_marks_v1.csv", report_text)
        self.assertIn("already included in each core variant", report_text)
        self.assertIn("open-lot unrealized PnL only", report_text)
        self.assertIn("already included in each core variant", report_text)
        self.assertIn("open-lot unrealized PnL only", report_text)
        self.assertIn("2026-09-23–2026-10-23 | 23 | $117.345", report_text)
        self.assertIn("2026-09-10–2026-10-23 | 32 | $103.45", report_text)
        self.assertNotIn("approximate quote", report_text.lower())


if __name__ == "__main__":
    unittest.main()
