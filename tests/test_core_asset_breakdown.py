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
        self.assertIn("BRENT | LONG* | 50U | $115.510", self.report)
        self.assertIn("LONG is inferred from that annotation, not explicitly stated", self.report)
        self.assertIn("$117.409 at 08:58:03 UTC−7", self.report)
        self.assertIn("2026-10-26 | 06:30 | GEV | LONG* | 1U | $823.810", self.report)
        self.assertIn("2026-10-26 | 06:30 | RIVN | LONG* | 1U | $11.770", self.report)
        self.assertIn("2026-10-26 | 06:30 | META | TAKE PROFIT* | 1U | $637.200", self.report)
        self.assertIn("2026-10-26 | 06:30 | META | LONG* | 1U | $637.200", self.report)
        self.assertIn("2026-10-26 | 07:51 | USOIL (OIL) | LONG* | 50U | $101.110", self.report)
        self.assertIn("2026-10-26 | 13:00 | INTC | TAKE PROFIT* | 6U | $87.550", self.report)
        self.assertIn("2026-10-26 | 13:00 | META | TAKE PROFIT* | 4U | $637.200", self.report)
        self.assertIn("2026-10-26 | 13:00 | INTC | LONG* | 6U | $87.550", self.report)
        self.assertIn("2026-10-26 | 13:00 | CAT | TAKE PROFIT* | 2U | $692.860", self.report)
        self.assertIn("2026-10-26 | 13:00 | DIS | SHORT* | 1U | $110.270", self.report)
        self.assertIn("2026-10-26 | 13:00 | PLTR | TAKE PROFIT* | 3U | $199.530", self.report)
        self.assertIn("2026-10-26 | 13:00 | TSLA | TAKE PROFIT* | 1U | $394.570", self.report)
        self.assertIn("2026-10-26 | 13:00 | UPS | SHORT* | 1U | $100.080", self.report)
        self.assertIn("2026-10-26 | 13:00 | SPCX | SHORT* | 1U | $148.460", self.report)
        self.assertIn("2026-10-26 | 13:00 | BRENT | TAKE PROFIT* | 50U | $117.409", self.report)
        self.assertIn("2026-10-26 | 13:00 | USOIL (OIL) | TAKE PROFIT* | 50U | $102.710", self.report)
        self.assertIn("$16,132.24 before costs", self.report)
        self.assertIn("the separate earlier OIL 50U @ $101.00 lot is untouched", self.report)
        self.assertIn("6U INTC LONG @ $87.55 is applied independently to each of the four core variants", self.report)
        self.assertIn("SPCX SHORT @ $148.46", self.report)
        self.assertIn("DIS SHORT @ $110.27", self.report)
        self.assertIn("UPS SHORT @ $100.08", self.report)
        self.assertIn("default 1U", self.report)
        self.assertIn("existing 2U LONG plus the new 1U LONG leaves 3U LONG", self.report)
        self.assertIn("compounded V3A began with a modeled 5U SHORT", self.report)
        self.assertIn("distinct from the earlier 50U ATS OIL lot @ $101.00", self.report)
        with breakdown.OUTPUT_CSV.open(newline="", encoding="utf-8") as handle:
            self.assertEqual(list(csv.DictReader(handle)), self.rows)


if __name__ == "__main__":
    unittest.main()
