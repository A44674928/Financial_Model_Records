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
    percent_gain_scenarios,
    variant_force_multiplier_daily_model,
)
from model_perf_core import SESSION_DATES, UNIT, parse_trades  # noqa: E402


class StrategySidecarComparisonTests(unittest.TestCase):
    def test_force_multiplier_is_one_10000_unit_and_20x_notional(self):
        events = parse_trades()
        exp_daily, exp_positions = exponential_daily_model(events)
        force_daily, force_positions = force_multiplier_daily_model(events)
        self.assertEqual(len(exp_daily), len(SESSION_DATES))
        self.assertEqual(exp_daily[-1]["exponential_active_symbols"], 31)
        self.assertEqual(force_daily[-1]["force_multiplier_active_symbols"], 31)
        self.assertEqual(exp_daily[-1]["exponential_cumulative_notional_added_usd"], "328000.00")
        self.assertEqual(force_daily[-1]["force_multiplier_cumulative_notional_added_usd"], "6560000.00")
        self.assertEqual(exp_daily[-1]["exponential_open_notional_usd"], "279500.00")
        self.assertEqual(force_daily[-1]["force_multiplier_open_notional_usd"], "5590000.00")
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

    def test_variant_specific_1u_models_apply_open_sar_and_compounding_rules(self):
        events = parse_trades()
        daily = {}
        audits = {}
        for variant in ("V1", "V2", "V3A", "V3B"):
            daily[variant], audits[variant] = variant_force_multiplier_daily_model(variant, events)

        def audit(variant, ticker, day):
            return next(row for row in audits[variant] if row["ticker"] == ticker and row["date"] == day)

        # CAT's Oct. 6 full exit records 2 units. Only Nu variants size the
        # compounded-short event-day tranche at 2U; carried days return to 1U.
        self.assertEqual(audit("V1", "CAT", "2026-10-06")["daily_tranche_units"], "1.00")
        self.assertEqual(audit("V3A", "CAT", "2026-10-06")["daily_tranche_units"], "2.00")
        self.assertEqual(audit("V3B", "CAT", "2026-10-06")["daily_tranche_units"], "2.00")
        self.assertEqual(audit("V3A", "CAT", "2026-10-07")["daily_tranche_units"], "1.00")

        # On the Oct. 19 CAT LONG, open models retain old shorts; SAR models
        # cover them and finish the session with only the fresh long tranche.
        for variant in ("V1", "V3A"):
            self.assertEqual(audit(variant, "CAT", "2026-10-19")["direction"], "long")
            self.assertGreater(int(audit(variant, "CAT", "2026-10-19")["open_lot_count"]), 1)
        for variant in ("V2", "V3B"):
            self.assertEqual(audit(variant, "CAT", "2026-10-19")["direction"], "long")
            self.assertEqual(audit(variant, "CAT", "2026-10-19")["open_lot_count"], 1)

        terminal = {variant: rows[-1] for variant, rows in daily.items()}
        self.assertEqual(terminal["V1"]["V1_force_1u_cumulative_notional_added_usd"], "6560000.00")
        self.assertEqual(terminal["V2"]["V2_force_1u_pnl_usd"], "116972.32")
        self.assertEqual(terminal["V3A"]["V3A_force_1u_pnl_usd"], "139155.83")
        self.assertEqual(terminal["V3B"]["V3B_force_1u_cumulative_notional_added_usd"], "6650000.00")

    def test_sidecar_and_core_composites_are_additive_without_chart_double_count(self):
        rows, _, _, _, core = comparison_rows()
        terminal = rows[-1]
        self.assertEqual(terminal["oil_desk_daily_buy_pnl_usd"], "500808.26")
        self.assertEqual(terminal["exponential_500_pnl_usd"], "5471.50")
        self.assertEqual(terminal["force_multiplier_1u_pnl_usd"], "109429.96")
        self.assertEqual(terminal["exponential_500_plus_oil_pnl_usd"], "506279.76")
        self.assertEqual(terminal["force_multiplier_plus_oil_pnl_usd"], "610238.22")
        self.assertEqual(terminal["V1_core_pnl_usd"], f"{core['V1']['total'][-1]:.2f}")
        self.assertEqual(
            terminal["V1_plus_force_multiplier_and_oil_pnl_usd"],
            f"{core['V1']['total'][-1] + float(terminal['force_multiplier_plus_oil_pnl_usd']):.2f}",
        )
        self.assertEqual(terminal["force_multiplier_plus_oil_cumulative_notional_usd"], "12060000.00")
        self.assertEqual(terminal["force_multiplier_plus_oil_open_notional_usd"], "11090000.00")
        self.assertEqual(terminal["V1_force_1u_pnl_usd"], "118252.71")
        self.assertEqual(terminal["V2_force_1u_pnl_usd"], "116972.32")
        self.assertEqual(terminal["V3A_force_1u_pnl_usd"], "139155.83")
        self.assertEqual(terminal["V3B_force_1u_pnl_usd"], "127653.72")
        self.assertEqual(terminal["V1_force_1u_plus_oil_pnl_usd"], "619060.97")
        self.assertEqual(terminal["V3A_force_1u_plus_oil_pnl_usd"], "639964.09")
        combo_count = 0
        for core_variant in ("V1", "V2", "V3A", "V3B"):
            core_added = float(core[core_variant]["deployed"][-1])
            core_open = sum(
                lot["qty"] * UNIT
                for lot in core[core_variant]["lots"]
                if lot["entry_idx"] <= len(rows) - 1
                and (lot["close_idx"] is None or len(rows) - 1 < lot["close_idx"])
            )
            for force_variant in ("V1", "V2", "V3A", "V3B"):
                prefix = f"{core_variant}_core_plus_{force_variant}_force_1u_and_oil"
                expected_pnl = (
                    float(terminal[f"{core_variant}_core_pnl_usd"])
                    + float(terminal[f"{force_variant}_force_1u_pnl_usd"])
                    + float(terminal["oil_desk_daily_buy_pnl_usd"])
                )
                expected_added = (
                    core_added
                    + float(terminal[f"{force_variant}_force_1u_cumulative_notional_added_usd"])
                    + float(terminal["oil_desk_cumulative_notional_usd"])
                )
                expected_open = (
                    core_open
                    + float(terminal[f"{force_variant}_force_1u_open_notional_usd"])
                    + float(terminal["oil_desk_open_notional_usd"])
                )
                self.assertEqual(terminal[f"{prefix}_pnl_usd"], f"{expected_pnl:.2f}")
                self.assertEqual(terminal[f"{prefix}_cumulative_notional_usd"], f"{expected_added:.2f}")
                self.assertEqual(terminal[f"{prefix}_open_notional_usd"], f"{expected_open:.2f}")
                combo_count += 1
        self.assertEqual(combo_count, 16)
        scenarios = percent_gain_scenarios(rows)
        self.assertEqual(len(scenarios), 32)
        self.assertEqual(scenarios, sorted(scenarios, key=lambda item: item["terminal_pct"], reverse=True))
        for scenario in scenarios:
            prefix = f"{scenario['core_variant']}_core_plus_{scenario['force_variant']}_force_1u"
            if scenario["with_oil"]:
                prefix += "_and_oil"
            pnl = float(terminal[f"{prefix}_pnl_usd"])
            notional = float(terminal[f"{prefix}_cumulative_notional_usd"])
            self.assertEqual(
                terminal[f"{prefix}_return_on_cumulative_notional_pct"],
                f"{pnl / notional * 100:.6f}",
            )
        self.assertEqual(terminal["V1_core_plus_V1_force_1u_and_oil_pnl_usd"], "677252.26")
        self.assertEqual(terminal["V3A_core_plus_V3A_force_1u_and_oil_pnl_usd"], "719438.87")
        self.assertEqual(terminal["oil_desk_cumulative_notional_usd"], "5500000.00")
        before_oil = next(row for row in rows if row["date"] == "2026-09-09")
        first_oil = next(row for row in rows if row["date"] == "2026-09-10")
        self.assertEqual(before_oil["oil_desk_cumulative_notional_usd"], "0.00")
        self.assertEqual(first_oil["oil_desk_cumulative_notional_usd"], "100000.00")
        report = Path(__file__).resolve().parents[1] / "Strategy and Sidecar Comparison.md"
        report_text = report.read_text(encoding="utf-8")
        self.assertIn("Shared-direction force multiplier (1U/EOD)", report_text)
        self.assertIn("Model Calculation Guide.md", report_text)
        self.assertIn("force_multiplier_eod_positions_v1.csv", report_text)
        self.assertIn("Shared-direction force — 1U per EOD", report_text)
        self.assertIn("Variant-specific 1U/EOD force models and energy combinations", report_text)
        self.assertIn("force_multiplier_variant_eod_positions_v1.csv", report_text)
        self.assertIn("21-force-variant-oil-comparison.png", report_text)
        self.assertIn("All core + 1U force variant pairings + 10U energy schedule", report_text)
        self.assertIn("Cross-variant", report_text)
        self.assertEqual(report_text.count("| Matching |"), 4)
        self.assertEqual(report_text.count("| Cross-variant |"), 12)
        self.assertIn("Percent gain across all 32 combinations", report_text)
        self.assertIn("22-force-variant-oil-percent-gain.png", report_text)
        self.assertIn("not an account return", report_text)
        audit_path = Path(__file__).resolve().parents[1] / "data" / "force_multiplier_eod_positions_v1.csv"
        with audit_path.open(newline="", encoding="utf-8") as handle:
            force_audit = list(csv.DictReader(handle))
        self.assertEqual(len(force_audit), 36 * 31)
        self.assertTrue(all(row["model"] == "force_multiplier" for row in force_audit))
        variant_audit_path = Path(__file__).resolve().parents[1] / "data" / "force_multiplier_variant_eod_positions_v1.csv"
        with variant_audit_path.open(newline="", encoding="utf-8") as handle:
            variant_audit = list(csv.DictReader(handle))
        self.assertEqual(len(variant_audit), 4 * 36 * 31)
        self.assertEqual({row["variant"] for row in variant_audit}, {"V1", "V2", "V3A", "V3B"})
        charts_dir = Path(__file__).resolve().parents[1] / "Charts" / "performance"
        self.assertTrue((charts_dir / "21-force-variant-oil-comparison.png").exists())
        self.assertTrue((charts_dir / "22-force-variant-oil-percent-gain.png").exists())


if __name__ == "__main__":
    unittest.main()
