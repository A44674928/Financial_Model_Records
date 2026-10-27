"""Checks the clean-sheet specifications against the current model registry."""
import json
import unittest
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TWM_SPEC = ROOT / "TWM Chart-to-Model Series — Clean-Sheet Specification.md"
WINNER_SPEC = ROOT / "THE ONE MODEL — Winning Model and Contender Specification.md"
TOM_SPEC = ROOT / "THE ONE MODEL (TOM) — Clean-Sheet Specification.md"


class CleanSheetSpecTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.twm = TWM_SPEC.read_text(encoding="utf-8")
        cls.winner = WINNER_SPEC.read_text(encoding="utf-8")
        cls.tom = TOM_SPEC.read_text(encoding="utf-8")
        cls.summary = json.loads(
            (ROOT / "data" / "the_one_model_split_portfolios_v1_summary.json").read_text(encoding="utf-8")
        )
        cls.portfolios = cls.summary["individual_portfolios"]

    def test_twm_spec_covers_chart_intake_sizes_and_accumulator_limits(self):
        for phrase in (
            "TWM terminology",
            "**TWM** is the prefix for the **The Winning Model** chart-to-model series",
            "Chart submission and event-intake contract",
            "The user supplies intent",
            "human-in-the-loop specification",
            "TWM_1X",
            "1.000000×",
            "TWM_MICRO",
            "TWM_1K_FULL",
            "TWM_10K_MAX",
            "0.001×",
            "0.01×",
            "TWM_1M_FULL",
            "TWM_1M_LIGHT",
            "TWM_1M_MAX",
            "TWM_20B",
            "20,000× TWM_1M",
            "ACCUMULATOR=OFF|ON",
            "No new out-of-pocket cash",
            "does not alter the base TWM_1M_MAX PnL",
        ):
            self.assertIn(phrase, self.twm)

    def test_winner_spec_matches_all_16_core_force_pairs_and_current_champion(self):
        rows = [
            line for line in self.winner.splitlines()
            if line.startswith("|") and "Core |" not in line and "---" not in line
        ]
        comparison_rows = []
        for line in rows:
            columns = [column.strip().strip("*").strip() for column in line.strip("|").split("|")]
            if (
                len(columns) == 5
                and columns[0] in {"V1", "V2", "V3A", "V3B"}
                and columns[1] in {"V1", "V2", "V3A", "V3B"}
            ):
                comparison_rows.append((columns[0], columns[1], line))
        self.assertEqual(len(comparison_rows), 16)
        self.assertEqual({(core, force) for core, force, _ in comparison_rows}, {
            (core, force)
            for core in ("V1", "V2", "V3A", "V3B")
            for force in ("V1", "V2", "V3A", "V3B")
        })
        for portfolio in self.portfolios:
            core = portfolio["core_variant"]
            force = portfolio["variant_specific_1u_eod_variant"]
            energy = portfolio["oil_sidecar_included"]
            line = next(line for row_core, row_force, line in comparison_rows
                        if row_core == core and row_force == force)
            pnl = f"${float(portfolio['terminal_pnl_usd']):,.2f}"
            ratio = f"{float(portfolio['deployed_notional_ratio_pct']):.4f}%"
            self.assertIn(pnl, line)
            self.assertIn(ratio, line)
        self.assertIn("core_v3a__1u_v3a__with_oil", self.winner)
        self.assertIn("Current incumbent: THE WINNING MODEL", self.winner)
        self.assertIn("possible V4", self.winner)
        self.assertIn("winner is selected from the same 32 portfolios", self.winner)

    def test_tom_spec_covers_all_members_winner_and_both_micro_sizing_interpretations(self):
        for phrase in (
            "4 core variants × 4 force variants × 2 energy states = 32",
            "TOM_1K_TOTAL",
            "TOM_10K_TOTAL",
            "TOM_1K_EACH",
            "TOM_10K_EACH",
            "$32,000.00",
            "$320,000.00",
            "$34.37",
            "$1,221.72",
            "$343.73",
            "$12,217.21",
            "$1,050.87",
            "$39,424.47",
            "$10,508.70",
            "$394,244.73",
            "Accumulator is **OFF by default**",
            "Valuation marks are TradingView-only: never substitute a legacy price source",
            "Preserve user-provided categories (including ATS/manual)",
            "core_v3a__1u_v3a__with_oil",
        ):
            self.assertIn(phrase, self.tom)

        comparison_rows = []
        for line in self.tom.splitlines():
            if not line.startswith("|"):
                continue
            columns = [column.strip().strip("*").strip() for column in line.strip("|").split("|")]
            if len(columns) == 4 and columns[0] in {"V1", "V2", "V3A", "V3B"} and columns[1] in {"V1", "V2", "V3A", "V3B"}:
                comparison_rows.append((columns[0], columns[1], line))
        self.assertEqual(len(comparison_rows), 16)
        for portfolio in self.portfolios:
            line = next(
                line for core, force, line in comparison_rows
                if core == portfolio["core_variant"]
                and force == portfolio["variant_specific_1u_eod_variant"]
            )
            self.assertIn(f"${float(portfolio['terminal_pnl_usd']):,.2f}", line)

        aggregate_open = Decimal(self.summary["aggregate_gross_open_notional_usd"])
        aggregate_pnl = Decimal(self.summary["aggregate_terminal_pnl_usd"])
        aggregate_added = Decimal(self.summary["aggregate_cumulative_gross_notional_added_usd"])
        for target, pnl, additions in ((Decimal("1000"), "$34.37", "$1,221.72"),
                                        (Decimal("10000"), "$343.73", "$12,217.21")):
            factor = target / aggregate_open
            self.assertEqual(f"${(aggregate_pnl * factor):,.2f}", pnl)
            self.assertEqual(f"${(aggregate_added * factor):,.2f}", additions)
            self.assertIn(pnl, self.tom)
            self.assertIn(additions, self.tom)

        for target, expected_pnl, expected_additions in (
            (Decimal("1000"), "$1,050.87", "$39,424.47"),
            (Decimal("10000"), "$10,508.70", "$394,244.73"),
        ):
            each_pnl = sum(
                Decimal(row["terminal_pnl_usd"]) * target / Decimal(row["gross_open_notional_usd"])
                for row in self.portfolios
            )
            each_additions = sum(
                Decimal(row["cumulative_gross_notional_added_usd"]) * target / Decimal(row["gross_open_notional_usd"])
                for row in self.portfolios
            )
            self.assertEqual(f"${each_pnl:,.2f}", expected_pnl)
            self.assertEqual(f"${each_additions:,.2f}", expected_additions)
            self.assertIn(expected_pnl, self.tom)
            self.assertIn(expected_additions, self.tom)


if __name__ == "__main__":
    unittest.main()
