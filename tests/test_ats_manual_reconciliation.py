import csv
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_ats_manual_reconciliation.py"
spec = importlib.util.spec_from_file_location("ats_manual_reconciliation", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


class AtsManualReconciliationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        module.main()
        cls.report = module.REPORT_PATH.read_text(encoding="utf-8")
        with module.CSV_PATH.open(newline="", encoding="utf-8") as f:
            cls.rows = list(csv.DictReader(f))

    def test_ats_scenarios_and_closure_first_allocations_reconcile(self):
        ats = [row for row in self.rows if row["record_type"].startswith("AUTOMATED TRADING SYSTEM")]
        self.assertEqual(len(ats), 8)
        self.assertEqual({row["ats_allocation_ceiling_units"] for row in ats}, {"40"})
        self.assertEqual({row["manual_reference_allocation_units"] for row in ats}, {"10"})
        for ticker, order_units, residuals in (("BRENT", 35, [35, 25, 15, 5]), ("OIL", 34, [34, 24, 14, 4])):
            ticker_rows = [row for row in ats if row["ticker"] == ticker]
            self.assertEqual([int(row["units"]) for row in ticker_rows], [10, 20, 30, 40])
            self.assertEqual([int(row["ats_short_units_after_initial_cover"]) for row in ticker_rows], [0, 10, 20, 30])
            self.assertEqual([int(row["manual_approved_buy_order_units"]) for row in ticker_rows], [order_units] * 4)
            self.assertEqual([int(row["manual_approved_short_close_units"]) for row in ticker_rows], [0, 10, 20, 30])
            self.assertEqual([int(row["ats_short_units_remaining_after_manual_close"]) for row in ticker_rows], [0, 0, 0, 0])
            self.assertEqual([int(row["residual_long_units_from_approved_buy"]) for row in ticker_rows], residuals)
            self.assertTrue(all("quantity unverified" in row["status"] for row in ticker_rows))

    def test_manual_test_replenishments_are_separate_from_approved_short_closures(self):
        manual = [row for row in self.rows if row["record_type"] == "MANUAL LIVE TEST POSITION"]
        self.assertEqual(len(manual), 4)
        self.assertEqual(sum(int(row["units"]) for row in manual if row["ticker"] == "BRENT"), 20)
        self.assertEqual(sum(int(row["units"]) for row in manual if row["ticker"] == "OIL"), 20)
        self.assertIn("MANUAL LIVE TEST POSITIONS", self.report)
        self.assertIn("MANUALLY APPROVED SHORT CLOSURE", self.report)
        self.assertIn("only that excess counts as new long buy supply", self.report)

    def test_legacy_events_are_not_stacked_in_new_reconciliation(self):
        self.assertIn("superseded—not stacked—in this reconciliation", self.report)
        self.assertTrue(all("not a confirmed fill" in row["status"] for row in self.rows if row["record_type"].startswith("AUTOMATED TRADING SYSTEM")))
        self.assertIn("data/ats_manual_live_positions_v1.csv", self.report)
        self.assertIn("LEGACY BASELINE ONLY", (ROOT / "trades/BRENT.txt").read_text())
        self.assertIn("MANUALLY APPROVED SHORT CLOSURE", (ROOT / "trades/OIL.txt").read_text())


if __name__ == "__main__":
    unittest.main()
