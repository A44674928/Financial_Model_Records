import csv
import sys
import unittest
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_oil_cost_basis_savings as cost_basis
from model_perf_core import VARIANTS, build_lots, parse_trades


class OilCostBasisSavingsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows, cls.positions, cls.portfolios = cost_basis.build_rows()
        cost_basis.write_csv(cls.rows)
        cost_basis.write_report(cls.rows, cls.positions, cls.portfolios)
        cls.report = cost_basis.REPORT.read_text(encoding="utf-8")

    def test_trim_credits_lower_effective_basis_without_extra_pnl(self):
        brent = self.positions["BRENT"]
        oil = self.positions["OIL"]
        self.assertEqual(brent["remaining_original_units"], Decimal("40"))
        self.assertEqual(brent["replenishment_units"], Decimal("10"))
        self.assertEqual(brent["gross_open_notional"], Decimal("500000"))
        self.assertEqual(brent["realized_trim_pnl"].quantize(Decimal("0.01")), Decimal("5015.62"))
        self.assertEqual(brent["adjusted_net_basis"].quantize(Decimal("0.01")), Decimal("494984.38"))
        self.assertEqual(brent["unadjusted_effective_basis_price"].quantize(Decimal("0.000001")), Decimal("112.261289"))
        self.assertEqual(brent["adjusted_effective_basis_price"].quantize(Decimal("0.000001")), Decimal("111.135170"))
        self.assertEqual(brent["basis_reduction_per_exposure_unit"].quantize(Decimal("0.000001")), Decimal("1.126119"))
        self.assertEqual(brent["unit_weighted_average_price"], Decimal("112.288"))
        self.assertEqual(brent["target_to_rebuy_price_gap"], Decimal("1.208"))

        self.assertEqual(oil["realized_trim_pnl"].quantize(Decimal("0.01")), Decimal("2988.69"))
        self.assertEqual(oil["adjusted_net_basis"].quantize(Decimal("0.01")), Decimal("497011.31"))
        self.assertEqual(oil["unadjusted_effective_basis_price"].quantize(Decimal("0.000001")), Decimal("99.568474"))
        self.assertEqual(oil["adjusted_effective_basis_price"].quantize(Decimal("0.000001")), Decimal("98.973315"))
        self.assertEqual(oil["basis_reduction_per_exposure_unit"].quantize(Decimal("0.000001")), Decimal("0.595159"))
        self.assertEqual(oil["target_to_rebuy_price_gap"], Decimal("0.26"))
        self.assertTrue(all(position["replenishment_after_cutoff"] for position in self.positions.values()))
        events = parse_trades()
        for variant in VARIANTS:
            _, realized = build_lots(variant, events)
            for ticker, position in self.positions.items():
                trim_realized = sum(
                    row["pnl"] for row in realized
                    if row["sym"] == ticker and row["date"] == position["trim_date"]
                    and row["qty"] == float(position["trim_units"])
                )
                self.assertAlmostEqual(
                    trim_realized, float(position["realized_trim_pnl"]), places=8
                )

    def test_adjustment_maps_to_every_core_based_one_model_portfolio(self):
        self.assertEqual(len(self.portfolios), 32)
        self.assertEqual(len(self.rows), 64)
        portfolio_ids = {row["portfolio_id"] for row in self.rows}
        self.assertEqual(len(portfolio_ids), 32)
        self.assertEqual({row["core_variant"] for row in self.rows}, {"V1", "V2", "V3A", "V3B"})
        self.assertEqual(sum(row["energy_sidecar_included"] == "yes" for row in self.rows), 32)
        self.assertTrue(all(row["basis_credit_is_additional_pnl"] == "no" for row in self.rows))
        self.assertTrue(all(row["core_pnl_change_from_reclassification_usd"] == "0.00" for row in self.rows))
        with cost_basis.OUTPUT_CSV.open(newline="", encoding="utf-8") as handle:
            self.assertEqual(list(csv.DictReader(handle)), self.rows)

    def test_report_documents_reclassification_and_missing_post_entry_marks(self):
        self.assertIn("not an additional gain", self.report)
        self.assertIn("These are blended, PnL-equivalent prices—not logged entry prices or fills", self.report)
        self.assertIn("simple unit-count average would be $112.288", self.report)
        self.assertIn("not additional portfolio PnL", self.report)
        self.assertIn("2026-10-25", self.report)
        self.assertIn("there are no post-entry marks", self.report)
        self.assertIn("32 independent core-based portfolios", self.report)
        self.assertIn("not both added together", self.report)


if __name__ == "__main__":
    unittest.main()
