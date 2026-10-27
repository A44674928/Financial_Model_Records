"""Regression tests for the requested one-time DXY withdrawal scenario."""

import sys
import unittest
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_tradingview_sidecars import (  # noqa: E402
    DXY_CASH_OIL_CSV,
    DXY_WITHDRAWAL_CSV,
    REPORT,
    build_dxy_cash_oil_bridge,
    build_dxy_rows,
    build_dxy_withdrawal_scenario,
)


class DxyWithdrawalScenarioTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        dxy_rows = build_dxy_rows()
        cls.rows = build_dxy_withdrawal_scenario(dxy_rows)
        cls.by_component = {row["component"]: row for row in cls.rows}
        cls.bridge = build_dxy_cash_oil_bridge(dxy_rows, cls.rows)[0]
        cls.report = REPORT.read_text(encoding="utf-8")

    def test_combined_11u_schedule_withdraws_40_percent_per_portfolio(self):
        row = self.by_component["Combined DXY allocation"]
        self.assertEqual(row["requested_date"], "2026-10-25")
        self.assertEqual(row["valuation_date"], "2026-10-26")
        self.assertEqual(row["sessions"], 35)
        self.assertEqual(Decimal(row["units_before"]), Decimal("385"))
        self.assertEqual(Decimal(row["units_planned_for_withdrawal"]), Decimal("154"))
        self.assertEqual(Decimal(row["notional_basis_planned_for_withdrawal_usd"]), Decimal("1540000.00"))
        self.assertEqual(Decimal(row["reference_withdrawal_mark_value_usd"]), Decimal("1555020.71"))
        self.assertEqual(Decimal(row["pnl_share_at_reference_mark_usd"]), Decimal("15020.71"))
        self.assertEqual(Decimal(row["units_remaining"]), Decimal("231"))
        self.assertEqual(Decimal(row["marked_value_remaining_usd"]), Decimal("2332531.06"))
        self.assertEqual(Decimal(row["pnl_remaining_at_reference_mark_usd"]), Decimal("22531.06"))

    def test_scenario_keeps_core_and_addon_distinct_and_future_size_unchanged(self):
        core = self.by_component["Integrated core sleeve"]
        addon = self.by_component["THE ONE add-on"]
        self.assertEqual(Decimal(core["units_planned_for_withdrawal"]), Decimal("14"))
        self.assertEqual(Decimal(addon["units_planned_for_withdrawal"]), Decimal("140"))
        self.assertIn("Future daily sizing stays at 11U/DAY", self.report)
        self.assertIn("baseline historical results through Oct. 23 remain unchanged", self.report)
        self.assertIn("not an actual DXY security trade", self.report)
        self.assertTrue(DXY_WITHDRAWAL_CSV.is_file())
        self.assertIn("dxy_withdrawal_scenario_v1.csv", self.report)

    def test_cash_to_oil_transfer_remains_pending_and_does_not_expand_size(self):
        self.assertIn("supplied 2026-10-26 DXY EOD close", self.bridge["status"])
        self.assertIn("reported executed", self.bridge["status"])
        self.assertEqual(self.bridge["dxy_units_to_withdraw"], "154.0000")
        self.assertEqual(self.bridge["dxy_withdrawal_proceeds_at_next_eod_usd"], "1555020.71")
        self.assertEqual(self.bridge["oil_cash_allocation_target_usd"], "690000.00")
        self.assertEqual(self.bridge["oil_cash_allocation_at_next_eod_usd"], "690000.00")
        self.assertEqual(self.bridge["excess_cash_support_for_existing_positions_at_next_eod_usd"], "865020.71")
        self.assertEqual(self.bridge["reference_excess_cash_support_at_current_mark_usd"], "865020.71")
        self.assertEqual(self.bridge["incremental_portfolio_size_from_internal_transfer_usd"], "0.00")
        self.assertEqual(self.bridge["future_combined_dxy_schedule_u_per_eod"], "11")
        self.assertIn("One-time 40% DXY withdrawal sizing reference", self.report)
        self.assertIn("not an actual withdrawal or cash balance", self.report)
        self.assertTrue(DXY_CASH_OIL_CSV.is_file())


if __name__ == "__main__":
    unittest.main()
