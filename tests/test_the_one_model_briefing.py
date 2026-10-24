from pathlib import Path
import json
import sys
import unittest
from decimal import Decimal

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_the_one_model_split_portfolios as split_model


class TheOneModelBriefingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.summary = json.loads(
            (ROOT / "data/the_one_model_split_portfolios_v1_summary.json").read_text(encoding="utf-8")
        )
        cls.briefing = (ROOT / "Hypothetical Securities Offering Briefing.md").read_text(encoding="utf-8")

    def test_briefing_discloses_manual_operation_and_hypothetical_status(self):
        text = (ROOT / "Hypothetical Securities Offering Briefing.md").read_text(encoding="utf-8")
        self.assertIn("not an offering document", text.lower())
        self.assertIn("not a prospectus", text.lower())
        self.assertIn("built to be operated manually by **Harshal Priyavadan Patel**", text)
        self.assertIn("not operational", text.lower())
        self.assertIn("THE ONE MODEL", text)
        self.assertIn("not an account return", text)

    def test_32_portfolio_construction_has_all_cross_pairs_and_oil_states(self):
        portfolios = split_model.portfolio_definitions()
        self.assertEqual(len(portfolios), 32)
        self.assertEqual(len({p["portfolio_id"] for p in portfolios}), 32)
        self.assertEqual(sum(p["oil_sidecar_included"] for p in portfolios), 16)
        self.assertEqual({p["core_variant"] for p in portfolios}, {"V1", "V2", "V3A", "V3B"})
        self.assertEqual({p["one_unit_eod_variant"] for p in portfolios}, {"V1", "V2", "V3A", "V3B"})
        for core in {p["core_variant"] for p in portfolios}:
            self.assertEqual(sum(p["core_variant"] == core and not p["oil_sidecar_included"] for p in portfolios), 4)
            self.assertEqual(sum(p["core_variant"] == core and p["oil_sidecar_included"] for p in portfolios), 4)

    def test_aggregate_totals_reconcile_to_all_32_independent_portfolios(self):
        portfolios, rows = split_model.build_rows()
        summary = split_model.build_summary(portfolios, rows)
        self.assertEqual(len(rows), 36)
        self.assertEqual(summary["period_start"], "2026-09-03")
        self.assertEqual(summary["period_end"], "2026-10-23")
        self.assertEqual(summary["portfolio_count"], 32)
        self.assertEqual(summary["aggregate_terminal_pnl_usd"], "27155856.32")
        self.assertEqual(summary["aggregate_cumulative_gross_notional_added_usd"], "350880000.00")
        self.assertEqual(summary["aggregate_gross_open_notional_usd"], "316000000.00")
        self.assertEqual(summary["aggregate_deployed_notional_ratio_pct"], "7.739357")
        self.assertEqual(summary["aggregate_max_peak_to_trough_pnl_drawdown_usd"], "1844483.12")
        self.assertEqual(summary["aggregate_max_drawdown_peak_date"], "2026-09-28")
        self.assertEqual(summary["aggregate_max_drawdown_trough_date"], "2026-09-29")
        self.assertEqual(summary["profitable_portfolios_at_terminal"], 32)
        self.assertEqual(
            sum(Decimal(p["terminal_pnl_usd"]) for p in summary["individual_portfolios"]),
            Decimal(summary["aggregate_terminal_pnl_usd"]),
        )
        self.assertEqual(
            sum(Decimal(p["cumulative_gross_notional_added_usd"]) for p in summary["individual_portfolios"]),
            Decimal(summary["aggregate_cumulative_gross_notional_added_usd"]),
        )

    def test_aggregate_results_and_full_table_are_disclosed(self):
        self.assertIn("32 independently tracked portfolios", self.briefing)
        self.assertIn("$27,155,856.32", self.briefing)
        self.assertIn("$350,880,000.00", self.briefing)
        self.assertIn("$316,000,000.00", self.briefing)
        self.assertIn("7.7394%", self.briefing)
        self.assertIn("$1,844,483.12", self.briefing)
        self.assertIn("Terminal statistics for all 32 portfolios", self.briefing)
        self.assertIn("the_one_model_split_portfolios_v1.csv", self.briefing)
        self.assertIn("the_one_model_split_portfolios_v1_summary.json", self.briefing)
        self.assertIn("all 16 Core × 1U/EOD pairings", self.briefing)

    def test_architecture_and_aggregate_chart_are_generated_and_embedded(self):
        for relpath in (
            "Charts/superstructure/the-one-model.png",
            "Charts/superstructure/the-one-model-split-portfolio.png",
        ):
            chart = ROOT / relpath
            self.assertTrue(chart.is_file())
            self.assertEqual(chart.read_bytes()[:8], b"\x89PNG\r\n\x1a\n")
            self.assertIn(relpath, self.briefing)

    def test_hypothetical_instrument_price_is_at_briefing_end_and_distinguished_from_1u(self):
        self.assertTrue(self.briefing.rstrip().endswith("**$10,000/Unit**"))
        self.assertIn("not an actual offering price", self.briefing)
        self.assertIn("separate from the model’s **1U / 1 Unit = $10,000 entry-notional** convention", self.briefing)

    def test_generated_csv_has_32_portfolio_series_plus_aggregate(self):
        path = ROOT / "data/the_one_model_split_portfolios_v1.csv"
        with path.open(newline="", encoding="utf-8") as handle:
            headers = next(__import__("csv").reader(handle))
        self.assertEqual(len([h for h in headers if h.endswith("__pnl_usd")]), 32)
        self.assertIn("aggregate_pnl_usd", headers)
        self.assertIn("aggregate_deployed_notional_ratio_pct", headers)


if __name__ == "__main__":
    unittest.main()
