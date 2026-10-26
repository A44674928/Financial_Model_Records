import csv
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_core_cost_basis_credits.py"
spec = importlib.util.spec_from_file_location("core_cost_basis_credits", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


class CoreCostBasisClosureCreditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        module.main()
        with module.CSV_PATH.open(newline="", encoding="utf-8") as handle:
            cls.rows = list(csv.DictReader(handle))
        cls.report = module.REPORT_PATH.read_text(encoding="utf-8")

    def row(self, ticker, variant):
        return next(row for row in self.rows if row["ticker"] == ticker and row["variant"] == variant)

    def test_open_position_basis_matches_latest_model_lots(self):
        expected = {
            "BRENT": ("150", "113.888773"),
            "OIL": ("150", "100.197067"),
            "META": ("3", "692.190000"),
            "INTC": ("9", "93.799444"),
        }
        for ticker, (units, avg) in expected.items():
            for variant in module.VARIANTS:
                row = self.row(ticker, variant)
                self.assertEqual(row["open_long_units"], units)
                self.assertEqual(row["unit_weighted_average_entry_price"], avg)

    def test_designated_closure_credits_are_variant_specific(self):
        for variant in module.VARIANTS:
            self.assertEqual(self.row("BRENT", variant)["closure_credit_usd"], "7043.82")
            self.assertEqual(self.row("OIL", variant)["closure_credit_usd"], "4223.99")
        self.assertEqual(
            [self.row("META", v)["closure_credit_usd"] for v in module.VARIANTS],
            ["1718.87", "0.00", "8594.34", "0.00"],
        )
        self.assertEqual(
            [self.row("INTC", v)["closure_credit_usd"] for v in module.VARIANTS],
            ["5506.50", "0.00", "17955.56", "0.00"],
        )
        self.assertEqual(self.row("META", "V3A")["adjusted_effective_basis_price"], "492.269519")
        self.assertEqual(self.row("INTC", "V3A")["adjusted_effective_basis_price"], "74.268960")

    def test_report_discloses_scope_and_separates_scenario_from_actual_basis(self):
        self.assertIn("economic cost-basis reclassification", self.report)
        self.assertIn("Earlier SAR-driven covers for META/INTC are excluded", self.report)
        self.assertIn("the basis of the existing 2U was not supplied", self.report)
        self.assertIn("uncertain-size maximum-ATS campaign scenario", self.report)
        self.assertIn("not one combined account", self.report)
        with module.CSV_PATH.open(newline="", encoding="utf-8") as handle:
            self.assertEqual(list(csv.DictReader(handle)), self.rows)


if __name__ == "__main__":
    unittest.main()
