"""Regression tests for the terminal DXY-equivalent portfolio view."""

import csv
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_csv(path):
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


class DXYPortfolioSnapshotTests(unittest.TestCase):
    def test_oct22_fx_marks_are_in_usd_then_dxy_point_equivalents(self):
        rows = {
            row["symbol"]: row
            for row in read_csv(ROOT / "data/dxy_portfolio_open_positions_oct22.csv")
            if row["variant"] == "V1" and row["symbol"] in {"DXY", "EURUSD", "JPYUSD"}
        }
        self.assertAlmostEqual(float(rows["DXY"]["unrealized_pnl_usd"]), 255.2302522, places=5)
        self.assertAlmostEqual(float(rows["EURUSD"]["unrealized_pnl_usd"]), -278.9718168, places=5)
        self.assertAlmostEqual(float(rows["JPYUSD"]["unrealized_pnl_usd"]), -3724.4094488, places=5)
        for row in rows.values():
            self.assertAlmostEqual(
                float(row["dxy_point_equivalent"]),
                float(row["unrealized_pnl_usd"]) / 1000.0,
                places=9,
            )

    def test_summary_unrealized_matches_all_open_position_rows(self):
        positions = read_csv(ROOT / "data/dxy_portfolio_open_positions_oct22.csv")
        summary = {row["variant"]: row for row in read_csv(ROOT / "data/dxy_portfolio_summary_oct22.csv")}
        for variant, row in summary.items():
            pnl = sum(
                float(p["unrealized_pnl_usd"])
                for p in positions
                if p["variant"] == variant and p["unrealized_pnl_usd"]
            )
            self.assertAlmostEqual(pnl, float(row["total_unrealized_pnl_usd"]), places=6)
        self.assertEqual(float(summary["V1"]["cumulative_deployed_units"]), 83.0)
        self.assertEqual(float(summary["V1"]["open_units_including_yield_refs"]), 68.0)
        self.assertAlmostEqual(float(summary["V1"]["us10y_carry_adjustment_usd"]), 176.7657534, places=5)

    def test_us30y_daily_mark_flags_the_treasury_holiday_carry(self):
        rows = {
            row["date"]: row
            for row in read_csv(ROOT / "data/us30y_short_mark_to_market_daily_2026.csv")
        }
        holiday = rows["2026-10-12"]
        self.assertEqual(holiday["close_yield_pct"], "5.6")
        self.assertEqual(holiday["source_date"], "2026-10-09")
        self.assertEqual(holiday["carried_forward"], "True")
        terminal = rows["2026-10-22"]
        self.assertEqual(terminal["close_yield_pct"], "5.29")
        self.assertAlmostEqual(float(terminal["unrealized_pnl_usd"]), 112.1495327, places=5)

    def test_report_discloses_snapshot_scope_and_yield_proxy(self):
        text = (ROOT / "DXY-Equivalent Portfolio Snapshot.md").read_text(encoding="utf-8")
        self.assertIn("terminal snapshot", text)
        self.assertIn("not a bond-duration", text)
        self.assertIn("$1,000 per DXY index point", text)
        self.assertIn("No daily DXY/EURUSD/JPYUSD closes were supplied", text)


if __name__ == "__main__":
    unittest.main()
