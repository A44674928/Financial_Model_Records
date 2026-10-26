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
        expected_gross = {
            "V1": Decimal("2015000"),
            "V2": Decimal("1965000"),
            "V3A": Decimal("2105000"),
            "V3B": Decimal("1965000"),
        }
        expected_pnl = {
            "V1": Decimal("103591.26"),
            "V2": Decimal("100748.06"),
            "V3A": Decimal("124874.75"),
            "V3B": Decimal("111914.76"),
        }
        for variant, gross in expected_gross.items():
            rows = [row for row in self.rows if row["variant"] == variant]
            self.assertEqual(sum(Decimal(row["gross_open_notional_usd"]) for row in rows), gross)
            rounded_asset_sum = sum(Decimal(row["total_pnl_usd"]) for row in rows)
            self.assertLessEqual(abs(rounded_asset_sum - self.summaries[variant]["pnl"]), Decimal("0.05"))
            self.assertEqual(self.summaries[variant]["pnl"].quantize(Decimal("0.01")), expected_pnl[variant])

    def test_oil_concentration_and_post_cutoff_entries_are_disclosed(self):
        for variant in breakdown.VARIANTS:
            brent = next(row for row in self.rows if row["variant"] == variant and row["ticker"] == "BRENT")
            oil = next(row for row in self.rows if row["variant"] == variant and row["ticker"] == "OIL")
            self.assertEqual(brent["long_open_units"], "45")
            self.assertEqual(oil["long_open_units"], "46")
            self.assertEqual(brent["short_open_units"], "10")
            self.assertEqual(oil["short_open_units"], "10")
            self.assertEqual(brent["gross_open_notional_usd"], "550000.00")
            self.assertEqual(oil["gross_open_notional_usd"], "560000.00")
        self.assertIn("$1,110,000.00 gross open notional", self.report)
        self.assertIn("$114.627 BRENT and $100.74 OIL on Oct. 25 at 20:35 MST", self.report)
        self.assertIn("$115.792 BRENT/$101.74 OIL entries use the user-recalled 17:20–17:25 MST window", self.report)
        self.assertIn("$114.80 BRENT/$101.00 OIL entries use an approximate 20:00 MST timestamp", self.report)
        self.assertIn("$200,000 per ticker, $400,000 combined", self.report)
        self.assertIn("2026-10-25 | ~17:22 | BRENT | LONG | 10U | $115.792", self.report)
        self.assertIn("2026-10-25 | ~20:00 | BRENT | LONG | 10U | $114.800", self.report)
        self.assertIn("$115.792", self.report)
        self.assertIn("$101.740", self.report)
        with breakdown.OUTPUT_CSV.open(newline="", encoding="utf-8") as handle:
            self.assertEqual(list(csv.DictReader(handle)), self.rows)


if __name__ == "__main__":
    unittest.main()
