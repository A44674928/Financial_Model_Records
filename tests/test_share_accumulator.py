"""Regression tests for the realized-PnL-funded share/unit companion."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from share_accumulator_core import run_share_accumulator  # noqa: E402


class ShareAccumulatorTests(unittest.TestCase):
    def test_fractional_equity_shares_buy_only_at_next_mark(self):
        dates = ["2026-10-01", "2026-10-02", "2026-10-05"]
        daily, terminal = run_share_accumulator(
            dates,
            {"ACME": dict(zip(dates, [10, 20, 30]))},
            [{"ticker": "ACME", "date": dates[0], "pnl": 100}],
            1.0,
        )
        rows = [row for row in daily if row["ticker"] == "ACME"]
        self.assertEqual(float(rows[0]["shares_or_model_units_held"]), 0)
        self.assertEqual(float(rows[0]["realized_pnl_pending_next_mark_usd"]), 100)
        self.assertAlmostEqual(float(rows[1]["next_mark_purchase_cash_usd"]), 100)
        self.assertAlmostEqual(float(rows[1]["shares_or_model_units_held"]), 5)
        self.assertAlmostEqual(float(rows[2]["shares_or_model_units_held"]), 5)
        self.assertAlmostEqual(float(rows[2]["accumulator_market_value_usd"]), 150)
        self.assertAlmostEqual(float(terminal[0]["accumulator_unrealized_pnl_usd"]), 50)

    def test_loss_sells_holdings_then_carries_shortfall_against_future_profit(self):
        dates = [f"2026-10-0{i}" for i in range(1, 6)]
        daily, _ = run_share_accumulator(
            dates,
            {"ACME": dict(zip(dates, [10, 10, 5, 10, 20]))},
            [
                {"ticker": "ACME", "date": dates[0], "pnl": 100},
                {"ticker": "ACME", "date": dates[1], "pnl": -150},
                {"ticker": "ACME", "date": dates[2], "pnl": 80},
                {"ticker": "ACME", "date": dates[3], "pnl": 30},
            ],
            1.0,
        )
        rows = [row for row in daily if row["ticker"] == "ACME"]
        self.assertAlmostEqual(float(rows[1]["shares_or_model_units_held"]), 10)
        self.assertAlmostEqual(float(rows[2]["next_mark_sale_proceeds_usd"]), 50)
        self.assertAlmostEqual(float(rows[2]["shares_or_model_units_held"]), 0)
        self.assertAlmostEqual(float(rows[2]["unfunded_loss_carry_usd"]), 100)
        self.assertAlmostEqual(float(rows[3]["unfunded_loss_carry_usd"]), 20)
        self.assertAlmostEqual(float(rows[4]["next_mark_purchase_cash_usd"]), 10)
        self.assertAlmostEqual(float(rows[4]["shares_or_model_units_held"]), 0.5)
        self.assertAlmostEqual(float(rows[4]["unfunded_loss_carry_usd"]), 0)

    def test_energy_is_tracked_as_model_u_not_shares(self):
        dates = ["2026-10-01", "2026-10-02", "2026-10-05"]
        daily, terminal = run_share_accumulator(
            dates,
            {"BRENT": dict(zip(dates, [100, 110, 121]))},
            [{"ticker": "BRENT", "date": dates[0], "pnl": 500}],
            1.0,
            unit_value=10_000,
        )
        row = next(row for row in daily if row["ticker"] == "BRENT" and row["date"] == dates[2])
        self.assertEqual(row["asset_tracker_type"], "model_U_equivalent")
        self.assertAlmostEqual(float(row["shares_or_model_units_held"]), 0.05)
        self.assertAlmostEqual(float(row["accumulator_market_value_usd"]), 550)
        self.assertAlmostEqual(float(terminal[0]["accumulator_unrealized_pnl_usd"]), 50)

    def test_netting_same_ticker_close_events_and_waiting_for_next_supplied_mark(self):
        dates = ["2026-10-01", "2026-10-02", "2026-10-05", "2026-10-06"]
        daily, _ = run_share_accumulator(
            dates,
            {"ACME": {dates[0]: 10, dates[2]: 20, dates[3]: 25}},
            [
                {"ticker": "ACME", "date": dates[0], "pnl": 100},
                {"ticker": "ACME", "date": dates[0], "pnl": -30},
            ],
            1.0,
        )
        rows = [row for row in daily if row["ticker"] == "ACME"]
        self.assertAlmostEqual(float(rows[0]["scaled_realized_pnl_usd"]), 70)
        self.assertAlmostEqual(float(rows[1]["shares_or_model_units_held"]), 0)
        self.assertAlmostEqual(float(rows[2]["next_mark_purchase_cash_usd"]), 70)
        self.assertAlmostEqual(float(rows[2]["shares_or_model_units_held"]), 3.5)


if __name__ == "__main__":
    unittest.main()
