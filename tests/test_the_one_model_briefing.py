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
        self.assertIn("Debit Investors Only", text)
        self.assertIn("Accredited Investors may NOT participate", text)

    def test_20b_paper_portfolio_and_two_stage_archival_process_are_disclosed(self):
        self.assertIn("$20B Paper Portfolio — historical two-stage record", self.briefing)
        self.assertIn("TradingView Paper Trading", self.briefing)
        self.assertIn("manually porting activity", self.briefing)
        self.assertIn("$987,245,895.26", self.briefing)
        self.assertIn("$19,012,754,104.74", self.briefing)
        self.assertIn("both** supplied BRENT and OIL EOD marks reach $200.00", self.briefing)
        self.assertIn("Units Experiment Pool Allocation.md", self.briefing)

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
        portfolios, rows, energy_11u_rows = split_model.build_rows()
        summary = split_model.build_summary(portfolios, rows)
        self.assertEqual(len(rows), 37)
        self.assertEqual(summary["period_start"], "2026-09-03")
        self.assertEqual(summary["period_end"], "2026-10-26")
        self.assertEqual(summary["portfolio_count"], 32)
        self.assertEqual(summary["aggregate_terminal_pnl_usd"], "16457691.52")
        self.assertEqual(summary["aggregate_cumulative_gross_notional_added_usd"], "584960000.00")
        self.assertEqual(summary["aggregate_gross_open_notional_usd"], "478800000.00")
        self.assertEqual(summary["aggregate_deployed_notional_ratio_pct"], "2.813473")
        self.assertEqual(summary["aggregate_max_peak_to_trough_pnl_drawdown_usd"], "1786528.08")
        self.assertEqual(summary["aggregate_max_drawdown_peak_date"], "2026-09-28")
        self.assertEqual(summary["aggregate_max_drawdown_trough_date"], "2026-09-29")
        self.assertEqual(summary["dxy_10u_sidecar_terminal_pnl_per_portfolio_usd"], "34137.97")
        self.assertEqual(summary["dxy_10u_sidecar_notional_added_per_portfolio_usd"], "3600000.00")
        self.assertEqual(summary["aggregate_dxy_10u_sidecar_terminal_pnl_usd"], "1092415.04")
        self.assertEqual(summary["aggregate_dxy_10u_sidecar_notional_added_usd"], "115200000.00")
        self.assertEqual(summary["combined_dxy_units_per_active_eod_per_portfolio"], 11)
        self.assertEqual(summary["integrated_core_dxy_1u_terminal_pnl_per_portfolio_usd"], "3413.80")
        self.assertEqual(summary["integrated_core_dxy_1u_notional_added_per_portfolio_usd"], "360000.00")
        self.assertEqual(summary["combined_dxy_terminal_pnl_per_portfolio_usd"], "37551.77")
        self.assertEqual(summary["combined_dxy_cumulative_notional_per_portfolio_usd"], "3960000.00")
        self.assertEqual(summary["aggregate_combined_dxy_terminal_pnl_usd"], "1201656.64")
        self.assertEqual(summary["aggregate_combined_dxy_cumulative_notional_usd"], "126720000.00")
        self.assertEqual(summary["energy_sidecar_minimum_units_per_active_ticker_eod"], 11)
        self.assertEqual(summary["energy_sidecar_included_portfolios"], 16)
        self.assertEqual(summary["energy_sidecar_excluded_portfolios"], 16)
        self.assertEqual(summary["energy_11u_sidecar_terminal_pnl_per_energy_inclusive_portfolio_usd"], "424919.09")
        self.assertEqual(summary["energy_11u_sidecar_notional_added_per_energy_inclusive_portfolio_usd"], "6270000.00")
        self.assertEqual(summary["aggregate_energy_11u_sidecar_terminal_pnl_usd"], "6798705.44")
        self.assertEqual(summary["aggregate_energy_11u_sidecar_notional_added_usd"], "100320000.00")
        self.assertEqual(len(energy_11u_rows), 57)
        self.assertEqual({row["unit_size_label"] for row in energy_11u_rows}, {"11U"})
        self.assertEqual(sum(row["ticker"] == "BRENT" for row in energy_11u_rows), 24)
        self.assertEqual(sum(row["ticker"] == "OIL" for row in energy_11u_rows), 33)
        self.assertEqual(summary["profitable_portfolios_at_terminal"], 32)
        self.assertEqual(
            sum(Decimal(p["terminal_pnl_usd"]) for p in summary["individual_portfolios"]),
            Decimal(summary["aggregate_terminal_pnl_usd"]),
        )
        self.assertEqual(
            sum(Decimal(p["cumulative_gross_notional_added_usd"]) for p in summary["individual_portfolios"]),
            Decimal(summary["aggregate_cumulative_gross_notional_added_usd"]),
        )
        self.assertEqual(
            sum(Decimal(p["dxy_10u_sidecar_terminal_pnl_usd"]) for p in summary["individual_portfolios"]),
            Decimal(summary["aggregate_dxy_10u_sidecar_terminal_pnl_usd"]),
        )
        for portfolio in portfolios:
            self.assertTrue(portfolio["dxy_10u_sidecar_included"])
            self.assertEqual(rows[-1][f"{portfolio['portfolio_id']}__dxy_10u_sidecar_notional_added_usd"], "3600000.00")
            self.assertEqual(rows[-1][f"{portfolio['portfolio_id']}__dxy_10u_sidecar_pnl_usd"], "34137.97")
            expected_energy_u = 11 if portfolio["oil_sidecar_included"] else 0
            self.assertEqual(portfolio["energy_sidecar_unit_size_u"], expected_energy_u)
            self.assertEqual(
                rows[-1][f"{portfolio['portfolio_id']}__energy_11u_sidecar_notional_added_usd"],
                "6270000.00" if expected_energy_u else "0.00",
            )

    def test_aggregate_results_and_full_table_are_disclosed(self):
        self.assertIn("Current-model snapshot — user-provided TradingView benchmark through 2026-10-26", self.briefing)
        self.assertIn("116 price-covered direct-trade events", self.briefing)
        self.assertIn("four Oct. 25 10U replenishments", self.briefing)
        self.assertIn("user-directed modeled INTC/META closes", self.briefing)
        self.assertIn("The separate whole-portfolio DXY/yield views remain historical through Oct. 23; hourly charts remain through Oct. 22", self.briefing)
        self.assertIn("Oil Cost Basis Savings Model", self.briefing)
        self.assertIn("32 independently tracked portfolios", self.briefing)
        self.assertIn("$16,457,691.52", self.briefing)
        self.assertIn("$584,960,000.00", self.briefing)
        self.assertIn("$478,800,000.00", self.briefing)
        self.assertIn("2.813473%", self.briefing)
        self.assertIn("$1,786,528.08", self.briefing)
        self.assertIn("11U/DAY total", self.briefing)
        self.assertIn("$37,551.77", self.briefing)
        self.assertIn("$3,960,000.00", self.briefing)
        self.assertIn("11U/DAY per active BRENT and OIL ticker", self.briefing)
        self.assertIn("$424,919.09", self.briefing)
        self.assertIn("$100,320,000.00", self.briefing)
        self.assertIn("Terminal statistics for all 32 portfolios", self.briefing)
        self.assertIn("the_one_model_split_portfolios_v1.csv", self.briefing)
        self.assertIn("the_one_model_split_portfolios_v1_summary.json", self.briefing)
        self.assertIn("All **16 Core × 1U/EOD pairings**", self.briefing)
        self.assertIn("36 daily lots; $360,000 gross notional added; +$3,413.80 terminal proxy PnL", self.briefing)
        self.assertIn("LLY's Oct. 20 close to $1,283.66", self.briefing)
        self.assertIn("Core V1 — 1U Open | $+114,524.25 | $4,585,000.00", self.briefing)
        self.assertIn("Core V3A — Nu Open | $+135,836.06 | $4,675,000.00", self.briefing)
        self.assertIn("36 daily lots; $360,000 gross notional added; +$3,413.80 terminal proxy PnL", self.briefing)
        self.assertIn("0.05U DXY schedule remains an alternative", self.briefing)
        self.assertIn("$34,137.97 terminal proxy PnL on $3,600,000.00 additions", self.briefing)
        self.assertNotIn("$12,393,481.92", self.briefing)
        table_start = self.briefing.index("| Core variant | 1U/EOD variant | Energy sidecar | DXY 10U sidecar | Combined DXY |")
        table_end = self.briefing.index("\n\nFull daily audit series:", table_start)
        table_rows = [line for line in self.briefing[table_start:table_end].splitlines() if line.startswith("| V")]
        self.assertEqual(len(table_rows), 32)
        self.assertEqual({"| V1 | V1 | No |" in self.briefing, "| V3B | V3B | 11U/DAY |" in self.briefing}, {True})
        for portfolio in self.summary["individual_portfolios"]:
            energy = "11U/DAY" if portfolio["oil_sidecar_included"] else "No"
            expected = (
                f"| {portfolio['core_variant']} | {portfolio['variant_specific_1u_eod_variant']} | {energy} | Yes | 11U/DAY | "
                f"${float(portfolio['terminal_pnl_usd']):,.2f} | "
                f"${float(portfolio['cumulative_gross_notional_added_usd']):,.2f} | "
                f"${float(portfolio['gross_open_notional_usd']):,.2f} | "
                f"{float(portfolio['deployed_notional_ratio_pct']):.6f}% |"
            )
            self.assertIn(expected, table_rows)
        self.assertIn("V3A Core + V3A 1U/EOD with the 11U energy sidecar", self.briefing)
        self.assertNotIn("10U DXY schedules are also separate alternatives and are excluded", self.briefing)
        self.assertIn("11U/DAY", self.briefing)
        self.assertIn("36 daily 1U core lots plus 36 daily 10U sidecar lots", self.briefing)

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
        self.assertIn("aggregate_dxy_10u_sidecar_pnl_usd", headers)
        self.assertIn("core_v1__1u_v1__no_oil__dxy_10u_sidecar_pnl_usd", headers)


if __name__ == "__main__":
    unittest.main()
