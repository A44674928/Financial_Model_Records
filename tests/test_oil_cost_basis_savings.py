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
        cls.ats_basis_rows = cost_basis.build_ats_basis_rows()
        cost_basis.write_csv(cls.rows)
        cost_basis.write_ats_basis_csv(cls.ats_basis_rows)
        cost_basis.write_report(cls.rows, cls.positions, cls.portfolios, cls.ats_basis_rows)
        cls.report = cost_basis.REPORT.read_text(encoding="utf-8")

    def test_trim_and_short_credits_lower_effective_basis_without_extra_pnl(self):
        brent = self.positions["BRENT"]
        oil = self.positions["OIL"]
        self.assertEqual(brent["remaining_original_units"], Decimal("40"))
        for position in (brent, oil):
            self.assertEqual(position["remaining_original_units"], Decimal("40"))
            self.assertEqual(position["replenishment_units"], Decimal("20"))
            self.assertEqual(position["combined_open_units"], Decimal("60"))
            self.assertEqual(position["gross_open_notional"], Decimal("600000"))
            self.assertEqual(len(position["replenishments"]), 2)
            self.assertEqual([event["date"] for event in position["replenishments"]], ["2026-10-25", "2026-10-25"])
            self.assertEqual([event["time"] for event in position["replenishments"]], ["17:22", "20:00"])
            self.assertIn("17:20–17:25 MST", position["replenishments"][0]["note"])
            self.assertIn("approximate time per user", position["replenishments"][1]["note"])

        self.assertEqual(brent["realized_trim_pnl"].quantize(Decimal("0.01")), Decimal("5015.62"))
        self.assertEqual(brent["realized_short_pnl"].quantize(Decimal("0.01")), Decimal("2028.21"))
        self.assertEqual(brent["total_realized_credit"].quantize(Decimal("0.01")), Decimal("7043.82"))
        self.assertEqual(brent["short_exit_date"], "2026-10-25")
        self.assertEqual(brent["short_exit_time"], "20:35")
        self.assertEqual(brent["short_exit_price"], Decimal("114.627"))
        self.assertEqual(brent["adjusted_net_basis"].quantize(Decimal("0.01")), Decimal("592956.18"))
        self.assertEqual(brent["unadjusted_effective_basis_price"].quantize(Decimal("0.000001")), Decimal("112.676581"))
        self.assertEqual(brent["adjusted_effective_basis_price"].quantize(Decimal("0.000001")), Decimal("111.353792"))
        self.assertEqual(brent["basis_reduction_per_exposure_unit"].quantize(Decimal("0.000001")), Decimal("1.322790"))
        self.assertEqual(brent["unit_weighted_average_price"].quantize(Decimal("0.001")), Decimal("112.707"))
        self.assertEqual(brent["target_to_rebuy_price_gaps"], [Decimal("1.208"), Decimal("2.200")])

        self.assertEqual(oil["realized_trim_pnl"].quantize(Decimal("0.01")), Decimal("2988.69"))
        self.assertEqual(oil["realized_short_pnl"].quantize(Decimal("0.01")), Decimal("1235.29"))
        self.assertEqual(oil["total_realized_credit"].quantize(Decimal("0.01")), Decimal("4223.99"))
        self.assertEqual(oil["short_exit_date"], "2026-10-25")
        self.assertEqual(oil["short_exit_time"], "20:35")
        self.assertEqual(oil["short_exit_price"], Decimal("100.74"))
        self.assertEqual(oil["adjusted_net_basis"].quantize(Decimal("0.01")), Decimal("595776.01"))
        self.assertEqual(oil["unadjusted_effective_basis_price"].quantize(Decimal("0.000001")), Decimal("99.804237"))
        self.assertEqual(oil["adjusted_effective_basis_price"].quantize(Decimal("0.000001")), Decimal("99.101618"))
        self.assertEqual(oil["basis_reduction_per_exposure_unit"].quantize(Decimal("0.000001")), Decimal("0.702619"))
        self.assertEqual(oil["unit_weighted_average_price"].quantize(Decimal("0.001")), Decimal("99.817"))
        self.assertEqual(oil["target_to_rebuy_price_gaps"], [Decimal("0.260"), Decimal("1.000")])
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
        for ticker, short_credit in (("BRENT", "2028.21"), ("OIL", "1235.29")):
            ticker_rows = [row for row in self.rows if row["ticker"] == ticker]
            self.assertEqual(len(ticker_rows), 32)
            self.assertTrue(all(row["realized_short_pnl_credited_usd"] == short_credit for row in ticker_rows))
        with cost_basis.OUTPUT_CSV.open(newline="", encoding="utf-8") as handle:
            self.assertEqual(list(csv.DictReader(handle)), self.rows)

    def test_ats_full_size_short_close_is_added_as_separate_basis_sensitivity(self):
        max_rows = [row for row in self.ats_basis_rows if row["ats_short_opened_units"] == "40"]
        self.assertEqual(len(max_rows), 2)
        brent = next(row for row in max_rows if row["ticker"] == "BRENT")
        oil = next(row for row in max_rows if row["ticker"] == "OIL")
        self.assertEqual(brent["short_close_pnl_credit_usd"], "11433.90")
        self.assertEqual(oil["short_close_pnl_credit_usd"], "10666.67")
        self.assertEqual(brent["residual_long_units_from_manual_order"], "5")
        self.assertEqual(oil["residual_long_units_from_manual_order"], "4")
        self.assertEqual(brent["open_long_units_in_basis_scope"], "85")
        self.assertEqual(oil["open_long_units_in_basis_scope"], "84")
        self.assertEqual(brent["new_ats_long_units"], "50")
        self.assertEqual(oil["new_ats_long_units"], "50")
        self.assertEqual(brent["short_close_credit_adjusted_effective_basis_price"], "113.070827")
        self.assertEqual(oil["short_close_credit_adjusted_effective_basis_price"], "99.556879")
        exact_total = sum(
            Decimal(row["ats_short_opened_units"]) * cost_basis.UNIT_NOTIONAL
            * (Decimal("1") - cost_basis.ATS_LOTS[row["ticker"]]["cover"] / cost_basis.ATS_LOTS[row["ticker"]]["short_entry"])
            for row in max_rows
        )
        self.assertEqual(cost_basis._money(exact_total), Decimal("22100.56"))
        self.assertIn("rather than stacks with, the legacy 10U-short credit", self.report)
        self.assertIn("No post-Oct. 23 TradingView EOD mark is supplied", self.report)
        with cost_basis.ATS_OUTPUT_CSV.open(newline="", encoding="utf-8") as handle:
            self.assertEqual(list(csv.DictReader(handle)), self.ats_basis_rows)

    def test_report_documents_reclassification_and_missing_post_entry_marks(self):
        self.assertIn("not additional gains", self.report)
        self.assertIn("separate realized 10U SHORT PnL", self.report)
        self.assertIn("$114.627 BRENT and $100.74 OIL on 2026-10-25 at 20:35 MST", self.report)
        self.assertIn("$115.792 BRENT/$101.74 OIL entries use the user-recalled 17:20–17:25 MST window, modeled at a 17:22 midpoint", self.report)
        self.assertIn("$114.80 BRENT/$101.00 OIL entries use approximately 20:00 MST", self.report)
        self.assertIn("17:20–17:25 MST (modeled at 17:22 midpoint)", self.report)
        self.assertIn("combined short PnL before costs) is $3,263.50", self.report)
        self.assertIn("These are blended, PnL-equivalent prices—not logged entry prices or fills", self.report)
        self.assertIn("simple unit-count average for the modeled open lots is $112.707", self.report)
        self.assertIn("60U", self.report)
        self.assertIn("does not fold the separate 35U/34U post-cutoff buys", self.report)
        self.assertIn("not additional portfolio PnL", self.report)
        self.assertIn("2026-10-25", self.report)
        self.assertIn("there are no post-entry marks", self.report)
        self.assertIn("32 independent core-based portfolios", self.report)
        self.assertIn("not both added together", self.report)


if __name__ == "__main__":
    unittest.main()
