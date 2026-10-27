"""Independent all-ticker replay and benchmark/composite reconciliation tests."""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from audit_actionable_tickers import audit_all, write_audit  # noqa: E402


class ActionableTickerAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = audit_all()
        cls.audit_path = write_audit(cls.result)
        cls.rows = {row["Ticker"]: row for row in cls.result["ticker_rows"]}

    def test_tradingview_core_scope_and_sidecars_reconcile(self):
        self.assertEqual(self.result["symbols"], 31)
        self.assertEqual(self.result["core_assets"], 32)
        self.assertEqual(self.result["dxy_core_units"], 36.0)
        self.assertAlmostEqual(self.result["dxy_core_terminal_pnl"], 3413.80, places=2)
        self.assertEqual(self.result["sessions"], 37)
        self.assertEqual(self.result["events"], 116)
        self.assertEqual(self.result["core_daily_rows"], 148)
        self.assertEqual(self.result["force_daily_rows"], 37)
        self.assertEqual(self.result["energy_rows"], 171)
        self.assertEqual(self.result["dxy_sidecar_rows"], 108)
        self.assertEqual(self.result["composite_daily_rows"], 37)
        self.assertEqual(len(self.rows), 32)
        self.assertIn("DXY", self.rows)
        self.assertNotIn("BTC", self.rows)
        self.assertNotIn("ETH", self.rows)
        self.assertTrue(all("tradingview" in row["EOD_Source"].lower() for row in self.result["ticker_rows"]))
        self.assertEqual(float(self.rows["DXY"]["V1_Core_Units_Added"]), 36.0)
        self.assertAlmostEqual(float(self.rows["DXY"]["V1_Core_Total_USD"]), 3413.80, places=2)
        self.assertEqual(self.audit_path.name, "actionable_ticker_reconciliation_20261026_v1.csv")

    def test_terminal_marks_and_ticker_attribution_are_reconcilable(self):
        row = self.rows["LULU"]
        self.assertEqual(float(row["EOD_Close"]), 102.91)
        self.assertIn("tradingview_eod_marks_20261026.csv", row["EOD_Source"])
        for variant in ("V1", "V2", "V3A", "V3B"):
            self.assertAlmostEqual(
                float(row[f"{variant}_Core_Total_USD"]),
                float(row[f"{variant}_Core_Realized_USD"]) + float(row[f"{variant}_Core_Unrealized_USD"]),
                places=2,
            )

    def test_32_portfolio_aggregate_and_energy_sleeves_reconcile(self):
        self.assertEqual(self.result["terminal_aggregate"], "16457691.52")
        self.assertEqual(self.result["terminal_notional"], "584960000.00")
        # Each core and force book occurs in eight of the 32 independent
        # portfolios. The integrated 1U DXY sleeve is part of core; an added
        # 10U DXY sidecar is included in all 32; 11U energy is included in 16.
        core_pnl = 8 * sum(
            float(row[f"{variant}_Core_Total_USD"])
            for row in self.result["ticker_rows"] for variant in ("V1", "V2", "V3A", "V3B")
        )
        force_pnl = 8 * sum(
            float(row[f"{variant}_Variant_1U_EOD_Total_USD"])
            for row in self.result["ticker_rows"] if row["Ticker"] != "DXY"
            for variant in ("V1", "V2", "V3A", "V3B")
        )
        energy_rows = [row for row in __import__("csv").DictReader(
            (ROOT / "data/the_one_model_energy_11u_sidecar_daily_v1.csv").open(encoding="utf-8")
        ) if row["date"] == "2026-10-26"]
        energy_pnl = sum(float(row["daily_buys_unrealized_pnl_usd"]) for row in energy_rows)
        dxy_rows = [row for row in __import__("csv").DictReader(
            (ROOT / "data/dxy_currency_desk_sidecar_daily_20261026.csv").open(encoding="utf-8")
        ) if row["date"] == "2026-10-26" and float(row["unit_size_u"]) == 10.0]
        dxy_10u_pnl = float(dxy_rows[0]["daily_investment_unrealized_pnl_usd"])
        self.assertAlmostEqual(
            core_pnl + force_pnl + 16 * energy_pnl + 32 * dxy_10u_pnl,
            float(self.result["terminal_aggregate"]),
            delta=1.5,
        )


if __name__ == "__main__":
    unittest.main()
