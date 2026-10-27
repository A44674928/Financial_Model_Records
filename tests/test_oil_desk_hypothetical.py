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
        self.assertEqual(sum(row["ticker"] == "BRENT" for row in rows), 24)
        self.assertEqual(sum(row["ticker"] == "OIL" for row in rows), 33)
        self.assertEqual(terminal["BRENT"]["cumulative_daily_buy_units"], 240)
        self.assertEqual(terminal["BRENT"]["cumulative_daily_buy_notional_usd"], "2400000.00")
        self.assertEqual(terminal["BRENT"]["daily_buys_unrealized_pnl_usd"], "183171.11")
        self.assertEqual(terminal["BRENT"]["chart_open_units"], "100")
        self.assertEqual(terminal["BRENT"]["chart_positions_unrealized_pnl_usd"], "20799.95")
        self.assertEqual(terminal["BRENT"]["combined_energy_unrealized_pnl_usd"], "203971.06")
        self.assertEqual(terminal["BRENT"]["eod_close"], "115.38")
        self.assertEqual(terminal["BRENT"]["source"], "tradingview_eod_marks_20261026.csv")
        self.assertEqual(terminal["OIL"]["cumulative_daily_buy_units"], 330)
        self.assertEqual(terminal["OIL"]["cumulative_daily_buy_notional_usd"], "3300000.00")
        self.assertEqual(terminal["OIL"]["daily_buys_unrealized_pnl_usd"], "203118.97")
        self.assertEqual(terminal["OIL"]["chart_open_units"], "100")
        self.assertEqual(terminal["OIL"]["chart_positions_unrealized_pnl_usd"], "16112.31")
        self.assertEqual(terminal["OIL"]["combined_energy_unrealized_pnl_usd"], "219231.27")
        self.assertEqual(terminal["OIL"]["eod_close"], "101.30")
        self.assertEqual(terminal["OIL"]["source"], "tradingview_eod_marks_20261026.csv")
        first_brent = next(row for row in rows if row["ticker"] == "BRENT")
        first_oil = next(row for row in rows if row["ticker"] == "OIL")
        self.assertEqual(first_brent["date"], "2026-09-23")
        self.assertEqual(first_oil["date"], "2026-09-10")
        self.assertEqual(first_brent["daily_buys_unrealized_pnl_usd"], "0.00")
        self.assertEqual(first_oil["daily_buys_unrealized_pnl_usd"], "0.00")
        marks = load_energy_marks()
        self.assertEqual(len(marks["BRENT"]), 24)
        self.assertEqual(len(marks["OIL"]), 33)
        self.assertEqual(marks["BRENT"]["2026-10-26"]["close"], 115.38)
        self.assertEqual(marks["OIL"]["2026-10-26"]["close"], 101.30)
        report = Path(__file__).resolve().parents[1] / "Oil Desk EOD Accumulation Hypothetical.md"
        report_text = report.read_text(encoding="utf-8")
        self.assertIn("same aligned marks", report_text)
        self.assertIn("tradingview_benchmark_session_marks_20261026.csv", report_text)
        self.assertIn("already included in each core variant", report_text)
        self.assertIn("open-lot unrealized PnL only", report_text)
        self.assertIn("already included in each core variant", report_text)
        self.assertIn("open-lot unrealized PnL only", report_text)
        self.assertIn("2026-09-23–2026-10-26 | 24 | $115.38", report_text)
        self.assertIn("2026-09-10–2026-10-26 | 33 | $101.30", report_text)
        self.assertNotIn("approximate quote", report_text.lower())


if __name__ == "__main__":
    unittest.main()
