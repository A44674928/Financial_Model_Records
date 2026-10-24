"""Regression tests for $500 and $10,000 direction-following models and sidecars."""

import csv
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from build_strategy_sidecar_comparison import (  # noqa: E402
    comparison_rows,
    exponential_daily_model,
    force_multiplier_daily_model,
)
from model_perf_core import SESSION_DATES, parse_trades  # noqa: E402


class StrategySidecarComparisonTests(unittest.TestCase):
    def test_force_multiplier_is_one_10000_unit_and_20x_notional(self):
        events = parse_trades()
        exp_daily, exp_positions = exponential_daily_model(events)
        force_daily, force_positions = force_multiplier_daily_model(events)
        self.assertEqual(len(exp_daily), len(SESSION_DATES))
        self.assertEqual(exp_daily[-1]["exponential_active_symbols"], 33)
        self.assertEqual(force_daily[-1]["force_multiplier_active_symbols"], 33)
        self.assertEqual(exp_daily[-1]["exponential_cumulative_notional_added_usd"], "364000.00")
        self.assertEqual(force_daily[-1]["force_multiplier_cumulative_notional_added_usd"], "7280000.00")
        self.assertEqual(exp_daily[-1]["exponential_open_notional_usd"], "315500.00")
        self.assertEqual(force_daily[-1]["force_multiplier_open_notional_usd"], "6310000.00")
        self.assertAlmostEqual(
            float(force_daily[-1]["force_multiplier_total_pnl_usd"]),
            20 * float(exp_daily[-1]["exponential_total_pnl_usd"]),
            delta=0.10,
        )

        def pos(rows, ticker, day):
            return next(row for row in rows if row["ticker"] == ticker and row["date"] == day)

        # Weekend direction applies on the next priced EOD for both sizing variants.
        for ledger in (exp_positions, force_positions):
            self.assertEqual(pos(ledger, "NFLX", "2026-10-02")["direction"], "")
            self.assertEqual(pos(ledger, "NFLX", "2026-10-05")["direction"], "long")
            self.assertEqual(pos(ledger, "NFLX", "2026-10-05")["open_lot_count"], 1)
        self.assertEqual(pos(exp_positions, "NFLX", "2026-10-05")["daily_add_notional_usd"], "500.00")
        self.assertEqual(pos(force_positions, "NFLX", "2026-10-05")["daily_add_notional_usd"], "10000.00")
        self.assertEqual(pos(force_positions, "NFLX", "2026-10-05")["tranche_notional_usd"], "10000.00")

        # CAT flips on Oct. 6: old long lots close and only one new short lot stays open.
        for ledger in (exp_positions, force_positions):
            self.assertEqual(pos(ledger, "CAT", "2026-10-05")["direction"], "long")
            self.assertGreater(pos(ledger, "CAT", "2026-10-05")["open_lot_count"], 1)
            self.assertEqual(pos(ledger, "CAT", "2026-10-06")["direction"], "short")
            self.assertEqual(pos(ledger, "CAT", "2026-10-06")["open_lot_count"], 1)
        self.assertEqual(pos(exp_positions, "CAT", "2026-10-06")["open_notional_usd"], "500.00")
        self.assertEqual(pos(force_positions, "CAT", "2026-10-06")["open_notional_usd"], "10000.00")

    def test_sidecar_and_core_composites_are_additive_without_chart_double_count(self):
        rows, _, _, core = comparison_rows()
        terminal = rows[-1]
        self.assertEqual(terminal["oil_desk_daily_buy_pnl_usd"], "499705.92")
        self.assertEqual(terminal["exponential_500_pnl_usd"], "21118.86")
        self.assertEqual(terminal["force_multiplier_1u_pnl_usd"], "422377.26")
        self.assertEqual(terminal["exponential_500_plus_oil_pnl_usd"], "520824.78")
        self.assertEqual(terminal["force_multiplier_plus_oil_pnl_usd"], "922083.18")
        self.assertEqual(terminal["V1_core_pnl_usd"], f"{core['V1']['total'][-1]:.2f}")
        self.assertEqual(
            terminal["V1_plus_force_multiplier_and_oil_pnl_usd"],
            f"{core['V1']['total'][-1] + float(terminal['force_multiplier_plus_oil_pnl_usd']):.2f}",
        )
        self.assertEqual(terminal["force_multiplier_plus_oil_cumulative_notional_usd"], "12780000.00")
        self.assertEqual(terminal["force_multiplier_plus_oil_open_notional_usd"], "11810000.00")
        report = Path(__file__).resolve().parents[1] / "Strategy and Sidecar Comparison.md"
        report_text = report.read_text(encoding="utf-8")
        self.assertIn("Force multiplier (1U/EOD)", report_text)
        self.assertIn("Model Calculation Guide.md", report_text)
        self.assertIn("force_multiplier_eod_positions_v1.csv", report_text)
        self.assertIn("Force multiplier — 1U per EOD", report_text)
        audit_path = Path(__file__).resolve().parents[1] / "data" / "force_multiplier_eod_positions_v1.csv"
        with audit_path.open(newline="", encoding="utf-8") as handle:
            force_audit = list(csv.DictReader(handle))
        self.assertEqual(len(force_audit), 36 * 33)
        self.assertTrue(all(row["model"] == "force_multiplier" for row in force_audit))


if __name__ == "__main__":
    unittest.main()
