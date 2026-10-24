"""Regression checks for the Oct 22 stock/ETF close reconciliation."""

import csv
import unittest
from pathlib import Path

from model_perf_core import PRICES, SESSION_DATES


ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "data" / "oct22_equity_eod_recheck.csv"


class Oct22EquityEodRecheckTests(unittest.TestCase):
    def test_audit_matches_terminal_marks_and_flags_only_net(self):
        with AUDIT.open(newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))

        self.assertEqual(len(rows), 27)  # 26 STOCK entries plus XLE ETF
        self.assertEqual({row["symbol"] for row in rows},
                         {symbol for symbol in PRICES if symbol not in {"BTC", "ETH", "BRENT", "OIL", "XRH0", "LCID"}})
        corrections = [row for row in rows if row["result"] == "CORRECTED"]
        self.assertEqual([(row["symbol"], row["prior_ledger_mark_usd"],
                           row["verified_oct22_yahoo_close_usd"], row["change_usd"])
                          for row in corrections], [("NET", "306.60", "303.61", "-2.99")])

        oct22_index = SESSION_DATES.index("2026-10-22")
        for row in rows:
            self.assertEqual(float(row["verified_oct22_yahoo_close_usd"]), PRICES[row["symbol"]][oct22_index])
            self.assertIn("period1=1792627200&period2=1792713600&interval=1d", row["source_url"])
            if row["symbol"] != "NET":
                self.assertEqual(row["result"], "MATCH")
                self.assertEqual(row["change_usd"], "0.00")


if __name__ == "__main__":
    unittest.main()
