"""Checks the clean-sheet specifications against the current model registry."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TWM_SPEC = ROOT / "TWM Chart-to-Model Series — Clean-Sheet Specification.md"
WINNER_SPEC = ROOT / "THE ONE MODEL — Winning Model and Contender Specification.md"


class CleanSheetSpecTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.twm = TWM_SPEC.read_text(encoding="utf-8")
        cls.winner = WINNER_SPEC.read_text(encoding="utf-8")
        cls.portfolios = json.loads(
            (ROOT / "data" / "the_one_model_split_portfolios_v1_summary.json").read_text(encoding="utf-8")
        )["individual_portfolios"]

    def test_twm_spec_covers_chart_intake_sizes_and_accumulator_limits(self):
        for phrase in (
            "TWM terminology",
            "**TWM** is the prefix for the **The Winning Model** chart-to-model series",
            "Chart submission and event-intake contract",
            "The user supplies intent",
            "human-in-the-loop specification",
            "TWM_1X",
            "1.000000×",
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


if __name__ == "__main__":
    unittest.main()
