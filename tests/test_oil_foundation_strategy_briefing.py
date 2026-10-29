import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BRIEFING = ROOT / "reports" / "$200 Oil Foundation & U-Sized Opportunity Capitalization Strategy — Briefing.md"


class OilFoundationStrategyBriefingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = BRIEFING.read_text(encoding="utf-8")

    def test_two_part_strategy_keeps_oil_foundation_and_u_sleeve_separate(self):
        self.assertIn("Fibonacci Volatility Cypher Shark Opportunity Capitalization Strategy", self.text)
        self.assertIn("$200 OIL LONG foundation", self.text)
        self.assertIn("U-sized opportunity sleeve", self.text)
        self.assertIn("do not borrow against, net with, or silently reduce the oil foundation", self.text.lower())

    def test_entry_basis_lock_and_source_limits_are_explicit(self):
        self.assertIn("Sep. 23", self.text)
        self.assertIn("$102.315", self.text)
        self.assertIn("Sep. 22", self.text)
        self.assertIn("$89.89", self.text)
        self.assertIn("The historical rule was to remain locked until **both** supplied BRENT and OIL EOD marks reached **$200.00**", self.text)
        self.assertIn("Latest user-reported outcome: ATS liquidation and dissolution", self.text)
        self.assertIn("organization dissolved at a profit", self.text)
        self.assertIn("The year was not included in the user's text", self.text)
        self.assertIn("not treated as an entry, exit, or verified fill", self.text)

    def test_income_is_objective_not_guaranteed_and_uses_realized_results(self):
        self.assertIn("realized income", self.text)
        self.assertIn("Realized PnL only", self.text)
        self.assertIn("Unrealized gains are not cash income", self.text)
        self.assertIn("neither income nor profitability is assured", self.text)
        self.assertIn("mechanics still to formalize", self.text.lower())

    def test_readme_links_briefing_and_local_references_exist(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("%24200%20Oil%20Foundation", readme)
        for relative in (
            Path("Units Experiment Pool Allocation.md"),
            Path("TWM Chart-to-Model Series — Clean-Sheet Specification.md"),
            Path("reports/Weightless Randomized Demo Portfolios — 2026-10-26.md"),
        ):
            self.assertTrue((ROOT / relative).exists(), relative)

    def test_original_screenshots_are_archived_and_linked_from_briefing(self):
        archive = ROOT / "Archive" / "200_OIL_LONG_foundation"
        for name in ("IMG_1165.png", "IMG_1167.png", "IMG_1168.png"):
            self.assertGreater((archive / name).stat().st_size, 0)
        index = (archive / "README.md").read_text(encoding="utf-8")
        self.assertIn("no separate fill, exit, or close event is inferred", index)
        self.assertIn("102.315", index)
        self.assertIn("89.89", index)
        self.assertIn("Archive/200_OIL_LONG_foundation/", self.text)


if __name__ == "__main__":
    unittest.main()
