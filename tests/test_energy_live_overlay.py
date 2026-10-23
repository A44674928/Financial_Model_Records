"""Checks the separately dated, user-provided energy mark overlay."""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from energy_live_overlay import inject_html_overlay, overlay_rows


class EnergyLiveOverlayTests(unittest.TestCase):
    def test_explorer_card_is_idempotent_and_keeps_historical_basis_clear(self):
        with TemporaryDirectory() as temp_dir:
            html_path = Path(temp_dir) / "explorer.html"
            html_path.write_text(
                '  <div class="card">\n    <h2>Full session table</h2>',
                encoding="utf-8",
            )
            inject_html_overlay(html_path)
            inject_html_overlay(html_path)
            html = html_path.read_text(encoding="utf-8")
            self.assertEqual(html.count('id="energy-live-overlay"'), 1)
            self.assertIn("$115.72", html)
            self.assertIn("+$4,264.55", html)
            self.assertIn("provider and timestamp were not specified", html)
            self.assertIn("not mixed into", html)
            self.assertIn("Charts/performance/14-energy-live-mark-overlay.png", html)

    def test_cash_cfd_marks_reconcile_to_trade_lots(self):
        rows = {r["symbol"]: r for r in overlay_rows()}
        self.assertEqual(set(rows), {"BRENT", "OIL"})
        self.assertEqual(rows["BRENT"]["historical_mark_usd"], "113.17")
        self.assertEqual(rows["BRENT"]["live_mark_usd"], "115.72")
        self.assertEqual(rows["BRENT"]["historical_unrealized_pnl_usd"], "3068.78")
        self.assertEqual(rows["BRENT"]["live_unrealized_pnl_usd"], "4264.55")
        self.assertEqual(rows["BRENT"]["change_from_historical_mark_usd"], "1195.77")
        self.assertEqual(rows["OIL"]["historical_mark_usd"], "99.47")
        self.assertEqual(rows["OIL"]["live_mark_usd"], "100.94")
        self.assertEqual(rows["OIL"]["historical_unrealized_pnl_usd"], "4051.72")
        self.assertEqual(rows["OIL"]["live_unrealized_pnl_usd"], "4998.30")
        self.assertEqual(rows["OIL"]["change_from_historical_mark_usd"], "946.58")
        expected_lots = {"BRENT": "5", "OIL": "6"}
        for symbol, row in rows.items():
            self.assertEqual(row["live_realized_pnl_usd"], "0.00")
            self.assertEqual(row["open_lots"], expected_lots[symbol])
            self.assertEqual(row["open_units"], expected_lots[symbol])
            self.assertIn("provider/time not specified", row["live_quote_basis"])


if __name__ == "__main__":
    unittest.main()
