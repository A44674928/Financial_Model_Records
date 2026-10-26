"""Checks for the focused one-minute INTC entry-window data and replay."""

import unittest

from minute_closeup import minute_series
from minute_session_data import CLOSES_1M, LOGGED_ENTRY_PRICE
from model_perf_core import VARIANTS, parse_trades
from intraday_core import INTRADAY_SESSION_DATES, N_BARS, build_intraday


class MinuteSessionTests(unittest.TestCase):
    def test_one_minute_window_has_sixty_regular_bars(self):
        rows, _ = minute_series()
        self.assertEqual(len(CLOSES_1M), 60)
        self.assertEqual(len(rows), 60)
        self.assertEqual(rows[0]["time_mst"], "10:01")
        self.assertEqual(rows[-1]["time_mst"], "11:00")
        self.assertTrue(all(
            rows[i + 1]["minute_close_epoch"] - rows[i]["minute_close_epoch"] == 60
            for i in range(59)
        ))

    def test_model_pairs_overlap_until_their_sar_paths_diverge(self):
        _, series = minute_series()
        self.assertEqual(series["V1"], series["V2"])
        self.assertEqual(series["V3A"], series["V3B"])
        self.assertGreater(series["V3A"][0], series["V1"][0])
        self.assertEqual(set(series), set(VARIANTS))

    def test_post_oct22_events_are_not_clamped_to_last_hourly_bar(self):
        self.assertEqual(INTRADAY_SESSION_DATES[-1], "2026-10-22")
        events = parse_trades()
        for variant in VARIANTS:
            lots, realized = build_intraday(variant, events, ["META"])
            self.assertFalse(any(lot["entry_bar"] >= N_BARS for lot in lots))
            self.assertFalse(any(row["bar"] >= N_BARS for row in realized))
            self.assertFalse(any(lot["entry_px"] == 637.2 for lot in lots))

    def test_logged_fill_discrepancy_is_preserved_not_repriced(self):
        rows, _ = minute_series()
        gap = rows[0]["close_usd"] - LOGGED_ENTRY_PRICE
        self.assertAlmostEqual(gap, 10.48, places=2)
        self.assertGreater(gap / LOGGED_ENTRY_PRICE, 0.09)
        self.assertEqual(rows[0]["close_usd"], CLOSES_1M[0])


if __name__ == "__main__":
    unittest.main()
