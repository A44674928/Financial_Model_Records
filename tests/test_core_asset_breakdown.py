import csv
import sys
import unittest
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_core_asset_breakdown as breakdown


class CoreAssetBreakdownTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows, cls.summaries = breakdown.build_rows()
        breakdown.write_csv(cls.rows)
        breakdown.write_report(cls.rows, cls.summaries)
        cls.report = breakdown.REPORT.read_text(encoding="utf-8")

    def test_all_core_assets_and_variants_reconcile(self):
        self.assertEqual(len(self.rows), 128)
        self.assertEqual({row["ticker"] for row in self.rows if row["ticker"] != "DXY"}, set(breakdown.PRICES))
        self.assertEqual(sum(row["ticker"] == "DXY" for row in self.rows), 4)
        expected_gross = {variant: Decimal("2955000") for variant in breakdown.VARIANTS}
        expected_pnl = {
            "V1": Decimal("114524.25"),
            "V2": Decimal("111926.39"),
            "V3A": Decimal("135836.06"),
            "V3B": Decimal("123093.10"),
        }
        for variant, gross in expected_gross.items():
            rows = [row for row in self.rows if row["variant"] == variant]
            self.assertEqual(sum(Decimal(row["gross_open_notional_usd"]) for row in rows), gross)
            rounded_asset_sum = sum(Decimal(row["total_pnl_usd"]) for row in rows)
            self.assertLessEqual(abs(rounded_asset_sum - self.summaries[variant]["pnl"]), Decimal("0.05"))
            self.assertEqual(self.summaries[variant]["pnl"].quantize(Decimal("0.01")), expected_pnl[variant])

    def test_oil_positions_and_current_user_supplied_marks_are_disclosed(self):
        for variant in breakdown.VARIANTS:
            brent = next(row for row in self.rows if row["variant"] == variant and row["ticker"] == "BRENT")
            oil = next(row for row in self.rows if row["variant"] == variant and row["ticker"] == "OIL")
            self.assertEqual(brent["long_open_units"], "100")
            self.assertEqual(oil["long_open_units"], "100")
            self.assertEqual(brent["short_open_units"], "0")
            self.assertEqual(oil["short_open_units"], "0")
            self.assertEqual(brent["gross_open_notional_usd"], "1000000.00")
            self.assertEqual(oil["gross_open_notional_usd"], "1000000.00")
            self.assertEqual(brent["eod_mark"], "115.38")
            self.assertEqual(oil["eod_mark"], "101.3")
        self.assertIn("$2,000,000.00 gross open notional", self.report)
        self.assertIn("marked at the supplied 2026-10-26 closes", self.report)
        self.assertIn("BRENT and OIL current marks are user-supplied TradingView EOD values", self.report)
        self.assertIn("not independently verified brokerage executions", self.report)
        self.assertIn("No direct-price entries fall after the current mark cutoff", self.report)
        self.assertIn("short closures reduce short exposure", self.report)
        self.assertIn("only the unallocated excess of the approved orders remains long", self.report)
        with breakdown.OUTPUT_CSV.open(newline="", encoding="utf-8") as handle:
            self.assertEqual(list(csv.DictReader(handle)), self.rows)

if __name__ == "__main__":
    unittest.main()
