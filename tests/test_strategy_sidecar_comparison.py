"""Regression tests for fixed-$500 EOD direction-following and sidecar composites."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from build_strategy_sidecar_comparison import comparison_rows, exponential_daily_model  # noqa: E402
from model_perf_core import SESSION_DATES, parse_trades  # noqa: E402


class StrategySidecarComparisonTests(unittest.TestCase):
    def test_exponential_daily_adds_follow_carried_direction_and_close_on_flip(self):
        daily, positions = exponential_daily_model(parse_trades())
        self.assertEqual(len(daily), len(SESSION_DATES))
        self.assertEqual(daily[-1]["exponential_active_symbols"], 33)
        self.assertEqual(daily[-1]["exponential_cumulative_notional_added_usd"], "364000.00")
        self.assertEqual(daily[-1]["exponential_open_notional_usd"], "315500.00")

        def pos(ticker, day):
            return next(row for row in positions if row["ticker"] == ticker and row["date"] == day)

        # The Oct. 3 Saturday authorization applies at the next priced EOD.
        self.assertEqual(pos("NFLX", "2026-10-02")["direction"], "")
        self.assertEqual(pos("NFLX", "2026-10-05")["direction"], "long")
        self.assertEqual(pos("NFLX", "2026-10-05")["open_lot_count"], 1)
        self.assertEqual(pos("NFLX", "2026-10-05")["daily_add_notional_usd"], "500.00")

        # CAT reverses on Oct. 6; all old long tranches close and only the new
        # short EOD tranche remains open on that date.
        self.assertEqual(pos("CAT", "2026-10-05")["direction"], "long")
        self.assertGreater(pos("CAT", "2026-10-05")["open_lot_count"], 1)
        self.assertEqual(pos("CAT", "2026-10-06")["direction"], "short")
        self.assertEqual(pos("CAT", "2026-10-06")["open_lot_count"], 1)
        self.assertEqual(pos("CAT", "2026-10-06")["open_notional_usd"], "500.00")
        self.assertEqual(pos("CAT", "2026-10-23")["direction"], "long")
        self.assertEqual(pos("CAT", "2026-10-23")["open_lot_count"], 5)

    def test_all_sidecar_and_core_composites_are_additive_without_chart_double_count(self):
        rows, _, core = comparison_rows()
        terminal = rows[-1]
        self.assertEqual(terminal["oil_desk_daily_buy_pnl_usd"], "499705.92")
        self.assertEqual(terminal["exponential_pnl_usd"], "21118.86")
        self.assertEqual(terminal["both_sidecars_pnl_usd"], "520824.78")
        self.assertEqual(terminal["V1_core_pnl_usd"], f"{core['V1']['total'][-1]:.2f}")
        self.assertEqual(
            terminal["V1_plus_both_sidecars_pnl_usd"],
            f"{core['V1']['total'][-1] + float(terminal['both_sidecars_pnl_usd']):.2f}",
        )
        self.assertEqual(terminal["both_sidecars_cumulative_notional_usd"], "5864000.00")
        self.assertEqual(terminal["both_sidecars_open_notional_usd"], "5815500.00")


if __name__ == "__main__":
    unittest.main()
