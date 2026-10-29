import csv
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_ats_manual_reconciliation.py"
spec = importlib.util.spec_from_file_location("ats_manual_reconciliation", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


class AtsManualReconciliationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        module.main()
        cls.report = module.REPORT_PATH.read_text(encoding="utf-8")
        with module.CSV_PATH.open(newline="", encoding="utf-8") as f:
            cls.rows = list(csv.DictReader(f))
        with module.LIQUIDATION_CSV_PATH.open(newline="", encoding="utf-8") as f:
            cls.liquidation_rows = list(csv.DictReader(f))

    def test_ats_scenarios_and_closure_first_allocations_reconcile(self):
        ats = [row for row in self.rows if row["record_type"] == "AUTOMATED TRADING SYSTEM LIVE POSITIONS — scenario"]
        self.assertEqual(len(ats), 8)
        self.assertEqual({row["ats_allocation_ceiling_units"] for row in ats}, {"40"})
        self.assertEqual({row["manual_reference_allocation_units"] for row in ats}, {"10"})
        for ticker, order_units, residuals in (("BRENT", 35, [35, 25, 15, 5]), ("OIL", 34, [34, 24, 14, 4])):
            ticker_rows = [row for row in ats if row["ticker"] == ticker]
            self.assertEqual([int(row["units"]) for row in ticker_rows], [10, 20, 30, 40])
            self.assertEqual([int(row["ats_short_units_after_initial_cover"]) for row in ticker_rows], [0, 10, 20, 30])
            self.assertEqual([int(row["manual_approved_buy_order_units"]) for row in ticker_rows], [order_units] * 4)
            self.assertEqual([int(row["manual_approved_short_close_units"]) for row in ticker_rows], [0, 10, 20, 30])
            self.assertEqual([int(row["ats_short_units_remaining_after_manual_close"]) for row in ticker_rows], [0, 0, 0, 0])
            self.assertEqual([int(row["residual_long_units_from_approved_buy"]) for row in ticker_rows], residuals)
            self.assertTrue(all("quantity unverified" in row["status"] for row in ticker_rows))

    def test_paired_long_cashouts_are_reported_separately_and_leave_111u_per_ticker(self):
        cashouts = [row for row in self.rows if row["record_type"] == "User-reported post-cutoff LONG liquidation"]
        self.assertEqual(len(cashouts), 2)
        by_ticker = {row["ticker"]: row for row in cashouts}
        self.assertEqual((by_ticker["BRENT"]["units"], by_ticker["BRENT"]["price"]), ("50", "117.409"))
        self.assertEqual((by_ticker["OIL"]["units"], by_ticker["OIL"]["price"]), ("50", "102.71"))
        self.assertIn("@ $101.11", by_ticker["OIL"]["notes"])
        self.assertNotIn("@ $101.00", by_ticker["OIL"]["scenario"])
        self.assertTrue(all("not independently verified" in row["status"] for row in cashouts))
        self.assertIn("111U BRENT / 111U OIL", self.report)
        self.assertIn("$16,132.24 before costs", self.report)

    def test_fixed_price_ats_additions_are_modeled_open_not_verified(self):
        added = [row for row in self.rows if row["record_type"] == "ATS modeled open position"]
        self.assertEqual(len(added), 2)
        by_ticker = {row["ticker"]: row for row in added}
        self.assertEqual(by_ticker["BRENT"]["units"], "50")
        self.assertEqual(by_ticker["BRENT"]["price"], "115.000")
        self.assertEqual(by_ticker["OIL"]["units"], "50")
        self.assertEqual(by_ticker["OIL"]["price"], "101.00")
        self.assertEqual(by_ticker["BRENT"]["date"], "2026-10-26")
        self.assertEqual(by_ticker["BRENT"]["time_mst"], "not supplied")
        self.assertIn("111U BRENT / 111U OIL", self.report)
        self.assertTrue(all("execution not verified" in row["status"] for row in added))
        oil_legacy_lot = by_ticker["OIL"]
        self.assertIn("separate from the later $101.11 mirror entry", oil_legacy_lot["scenario"])
        self.assertIn("Earlier separate 50U ATS OIL LONG @ $101.00", oil_legacy_lot["notes"])
        self.assertNotIn("OIL lot is the mirror", oil_legacy_lot["notes"])
        mirror = next(row for row in self.rows if row["record_type"].endswith("user-reported mirror"))
        self.assertEqual((mirror["ticker"], mirror["units"], mirror["price"], mirror["time_mst"]), ("OIL", "50", "101.11", "07:51 MST (synchronized with BRENT; seconds not supplied)"))
        self.assertIn("earlier 50U OIL @ $101.00", mirror["scenario"])
        self.assertIn("TradingView 1-minute USOIL screenshot", mirror["notes"])
        self.assertIn("ATS WAIT", mirror["notes"])
        self.assertIn("not a confirmed fill", mirror["status"])
        self.assertIn("mirror description applies to this new $101.11 lot, not the older $101.00 lot", self.report)
        self.assertNotIn("original OIL @ $101.00 lot as the synchronized mirror", self.report)

    def test_user_reported_additions_and_screenshot_supported_manual_brent_lot(self):
        additions = [row for row in self.rows if row["record_type"] == "User-reported additional LONG position"]
        self.assertEqual(len(additions), 4)
        lookup = {(row["ticker"], row["units"], row["price"]): row for row in additions}
        self.assertIn(("BRENT", "10", "115.025"), lookup)
        self.assertIn(("OIL", "10", "100.96"), lookup)
        self.assertIn(("BRENT", "16", "114.900"), lookup)
        self.assertIn(("OIL", "17", "100.85"), lookup)
        manual = [row for row in self.rows if row["record_type"] == "MANUAL LIVE TEST POSITION"]
        screenshot_lot = next(row for row in manual if row["units"] == "50")
        self.assertEqual(screenshot_lot["ticker"], "BRENT")
        self.assertEqual(screenshot_lot["price"], "115.510")
        self.assertIn("07:51:14 MST", screenshot_lot["time_mst"])
        self.assertIn("LONG is inferred", screenshot_lot["notes"])
        self.assertIn("PICK UP OPPORTUNITY", screenshot_lot["notes"])
        self.assertIn("$117.409 at 08:58:03 UTC−7", screenshot_lot["notes"])
        self.assertIn("strategy classification unspecified", self.report)
        self.assertIn("classification and execution not independently verified", lookup[("BRENT", "16", "114.900")]["notes"])
        self.assertIn("date-level assumption only", lookup[("OIL", "17", "100.85")]["time_mst"])
        self.assertIn("111U BRENT / 111U OIL", self.report)
        self.assertIn("separate additional 50U ATS USOIL LONG @ $101.11", self.report)
        self.assertIn("distinct from—and added on top of—the earlier $101.00 ATS USOIL lot", self.report)
        self.assertIn("LONG is inferred", self.report)

    def test_screenshot_supported_manual_and_ats_mirror_entries_are_synced_to_trade_archive(self):
        import zipfile
        brent_log = (ROOT / "trades/BRENT.txt").read_text(encoding="utf-8")
        self.assertIn("2026-10-26 07:51 MST | SIMULATED PAPER [LONG]", brent_log)
        self.assertIn("LONG inferred from handwritten PICK UP OPPORTUNITY", brent_log)
        oil_log = (ROOT / "trades/OIL.txt").read_text(encoding="utf-8")
        self.assertIn("2026-10-26 07:51 MST | SIMULATED PAPER [LONG]", oil_log)
        self.assertIn("$101.11", oil_log)
        self.assertIn("separate from the previously recorded 50U ATS OIL LONG @ $101.00 model lot", oil_log)
        with zipfile.ZipFile(ROOT / "trades.zip") as archive:
            self.assertEqual(archive.read("trades/BRENT.txt").decode("utf-8"), brent_log)
            self.assertEqual(archive.read("trades/OIL.txt").decode("utf-8"), oil_log)
            archived_index = archive.read("trades/index.txt").decode("utf-8")
        index = (ROOT / "trades/index.txt").read_text(encoding="utf-8")
        self.assertEqual(archived_index, index)
        self.assertIn("126 standardized log events currently recorded", index)

    def test_manual_test_replenishments_are_separate_from_approved_short_closures(self):
        manual = [row for row in self.rows if row["record_type"] == "MANUAL LIVE TEST POSITION"]
        self.assertEqual(len(manual), 5)
        self.assertEqual(sum(int(row["units"]) for row in manual if row["ticker"] == "BRENT"), 70)
        self.assertEqual(sum(int(row["units"]) for row in manual if row["ticker"] == "OIL"), 20)
        self.assertIn("MANUAL LIVE TEST POSITIONS", self.report)
        self.assertIn("MANUALLY APPROVED SHORT CLOSURE", self.report)
        self.assertIn("only that excess counts as new long buy supply", self.report)

    def test_legacy_events_are_not_stacked_in_new_reconciliation(self):
        self.assertIn("superseded—not stacked—in this reconciliation", self.report)
        self.assertTrue(all("not a confirmed fill" in row["status"] for row in self.rows if row["record_type"].startswith("AUTOMATED TRADING SYSTEM")))
        self.assertIn("data/ats_manual_live_positions_v1.csv", self.report)
        self.assertIn("LEGACY BASELINE ONLY", (ROOT / "trades/BRENT.txt").read_text())
        self.assertIn("MANUALLY APPROVED SHORT CLOSURE", (ROOT / "trades/OIL.txt").read_text())

    def test_reported_ats_liquidation_bands_keep_unknowns_and_do_not_claim_pnl(self):
        self.assertEqual(len(self.liquidation_rows), 3)
        brent_high = self.liquidation_rows[0]
        brent_low = self.liquidation_rows[1]
        oil = self.liquidation_rows[2]
        self.assertEqual((brent_high["ticker"], brent_high["marked_price_group"], brent_high["sale_price_min_usd"], brent_high["sale_price_max_usd"]), ("BRENT", "marked above $115", "116.480", "117.345"))
        self.assertEqual((brent_low["ticker"], brent_low["marked_price_group"], brent_low["sale_price_min_usd"], brent_low["sale_price_max_usd"]), ("BRENT", "marked below $115", "114.670", "116.480"))
        self.assertEqual((oil["ticker"], oil["sale_price_points_as_stated"]), ("OIL (USOIL)", "103.4 / 101.5"))
        for row in self.liquidation_rows:
            self.assertEqual(row["quantity_sold"], "not supplied")
            self.assertEqual(row["execution_date"], "not supplied")
            self.assertEqual(row["execution_time_timezone"], "not supplied")
            self.assertIn("not independently verified", row["status"])
            self.assertIn("No realized PnL computed", row["notes"])
        self.assertIn("all ATS-held oil positions", self.report)
        self.assertIn("pre-liquidation records", self.report)
        self.assertIn("does not rewrite historical core-model results", self.report)
        self.assertIn("ats_oil_liquidation_reported_v1.csv", self.report)


if __name__ == "__main__":
    unittest.main()
