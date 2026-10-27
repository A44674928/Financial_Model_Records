import csv
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_weightless_randomized_demo_portfolios.py"


def load_builder():
    spec = importlib.util.spec_from_file_location("weightless_demo_builder", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class WeightlessDemoPortfolioTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.builder = load_builder()

    def test_generated_outputs_cover_32_aligned_mixes_and_guard_dxy(self):
        with (ROOT / "data" / "weightless_demo_portfolio_summary_v1.csv").open(newline="", encoding="utf-8") as handle:
            summaries = list(csv.DictReader(handle))
        with (ROOT / "data" / "weightless_demo_portfolio_members_v1.csv").open(newline="", encoding="utf-8") as handle:
            members = list(csv.DictReader(handle))
        with (ROOT / "data" / "weightless_demo_portfolio_daily_v1.csv").open(newline="", encoding="utf-8") as handle:
            daily = list(csv.DictReader(handle))

        self.assertEqual(len(summaries), 32)
        self.assertEqual(len(daily), 37)
        self.assertEqual(daily[0]["date"], "2026-09-03")
        self.assertEqual(daily[-1]["date"], "2026-10-26")
        self.assertEqual(len(members), sum(int(row["component_count"]) for row in summaries))
        self.assertEqual({row["demo_id"] for row in summaries}, {row["demo_id"] for row in members})

        for row in summaries:
            self.assertGreaterEqual(int(row["component_count"]), 3)
            self.assertLessEqual(int(row["component_count"]), 6)
            self.assertEqual(row["dxy_sleeve_count"], "0" if float(row["dxy_units_per_active_eod"]) == 0 else "1")
            self.assertIn("core", row["component_types"].split(";"))
            self.assertIn("model", row["component_types"].split(";"))
            last_pnl = daily[-1][f"{row['demo_id']}__pnl_usd"]
            self.assertEqual(last_pnl, row["terminal_pnl_usd"])

        self.assertTrue({"core", "model", "force", "ticker", "energy", "dxy"}.issubset(
            {row["component_type"] for row in members}
        ))
        self.assertTrue(all(row["equal_sleeve_target_usd"] == "1000.00" for row in members))
        for row in members:
            if row["component_type"] in {"core", "ticker", "force", "energy"}:
                self.assertEqual(row["dxy_units_per_active_eod"], "0.0000")

    def test_fixed_seed_reproduces_compositions_and_daily_paths(self):
        dates, catalog, _categories, model_components = self.builder.load_component_catalog()
        demos_a, members_a = self.builder.make_demos(dates, catalog, model_components)
        demos_b, members_b = self.builder.make_demos(dates, catalog, model_components)
        self.assertEqual(members_a, members_b)
        self.assertEqual(
            [(demo["id"], demo["pnl"], demo["added"], demo["open"]) for demo in demos_a],
            [(demo["id"], demo["pnl"], demo["added"], demo["open"]) for demo in demos_b],
        )

    def test_report_and_svg_disclose_interpretation_and_profitability_limit(self):
        report = (ROOT / "reports" / "Weightless Randomized Demo Portfolios — 2026-10-26.md").read_text(encoding="utf-8")
        svg = (ROOT / "Charts" / "superstructure" / "weightless-randomized-demo-portfolios-20261026.svg").read_text(encoding="utf-8")
        self.assertIn("Uniform composition draws", report)
        self.assertIn("$1,000 maximum gross open notional", report)
        self.assertIn("not a forecast", report)
        self.assertIn("not a share ticker", report)
        self.assertIn("10th–90th percentile", svg)
        self.assertIn("not forecast or universal profitability", svg)


if __name__ == "__main__":
    unittest.main()
