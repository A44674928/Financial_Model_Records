"""Regression coverage for the separate daily-buy oil-desk scenario."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from build_oil_desk_hypothetical import build_rows  # noqa: E402


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
        self.assertEqual(terminal["BRENT"]["chart_open_units"], "5")
        self.assertEqual(terminal["BRENT"]["chart_positions_unrealized_pnl_usd"], "5026.57")
        self.assertEqual(terminal["BRENT"]["combined_energy_unrealized_pnl_usd"], "229385.42")
        self.assertEqual(terminal["OIL"]["cumulative_daily_buy_units"], 320)
        self.assertEqual(terminal["OIL"]["cumulative_daily_buy_notional_usd"], "3200000.00")
        self.assertEqual(terminal["OIL"]["daily_buys_unrealized_pnl_usd"], "275347.06")
        self.assertEqual(terminal["OIL"]["chart_open_units"], "6")
        self.assertEqual(terminal["OIL"]["chart_positions_unrealized_pnl_usd"], "6614.56")
        self.assertEqual(terminal["OIL"]["combined_energy_unrealized_pnl_usd"], "281961.62")
        first = next(row for row in rows if row["ticker"] == "OIL")
        self.assertEqual(first["daily_buys_unrealized_pnl_usd"], "0.00")


if __name__ == "__main__":
    unittest.main()
