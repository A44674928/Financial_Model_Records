import csv
import importlib.util
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_monero_eom_conversion_overlay.py"


def load_builder():
    spec = importlib.util.spec_from_file_location("monero_eom_overlay", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class MoneroEomConversionOverlayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.builder = load_builder()

    def test_current_window_converts_supplied_september_mark_and_carries_october_usd_reserve(self):
        book_rows, months = self.builder.build_outputs()
        self.assertEqual(len(months), 2)
        self.assertEqual(months[0]["month"], "2026-09")
        self.assertEqual(months[1]["month"], "2026-10")
        self.assertEqual(months[0]["aggregate_net_realized_pnl_usd"], "4118396.62")
        self.assertEqual(months[0]["usd_reserve_generated_this_month"], "41183.97")
        self.assertEqual(months[1]["aggregate_net_realized_pnl_usd"], "6183132.26")
        self.assertEqual(months[1]["usd_reserve_generated_this_month"], "61831.32")
        self.assertEqual(months[0]["eom_mark_date"], "2026-09-30")
        self.assertEqual(months[0]["xmr_usd_eom_close"], "544.86000000")
        self.assertEqual(months[0]["usd_converted_this_eom"], "41183.97")
        self.assertEqual(months[0]["modeled_xmr_equivalent"], "75.58633410")
        self.assertEqual(months[0]["pending_usd_reserve_after_eom"], "0.00")
        self.assertIn("modeled conversion", months[0]["conversion_status"])
        self.assertEqual(months[1]["pending_usd_reserve_after_eom"], "61831.32")
        self.assertEqual(months[1]["modeled_xmr_equivalent"], "0.00000000")
        self.assertIn("no supplied TradingView Kraken EOM close", months[1]["conversion_status"])
        self.assertEqual(months[0]["source_window_start_date"], "2026-09-03")
        self.assertEqual(months[0]["source_window_end_date"], "2026-09-30")
        self.assertEqual(months[1]["source_window_start_date"], "2026-10-01")
        self.assertEqual(months[1]["source_window_end_date"], "2026-10-26")

        ids = {row["book_id"] for row in book_rows}
        tom_ids = {book_id for book_id in ids if book_id.startswith("TOM::")}
        self.assertEqual(len(tom_ids), 32)
        self.assertIn("WINNER_EQUAL_GROSS::core_v3a__1u_v3a__with_oil", ids)
        self.assertNotIn("CORE_V3A_STANDALONE", ids)
        zero_books = [row for row in book_rows if row["book_type"] in {"energy_sidecar", "dxy_sidecar", "dxy_position"}]
        self.assertTrue(zero_books)
        self.assertTrue(all(Decimal(row["realized_pnl_usd"]) == 0 for row in zero_books))

    def test_realized_losses_offset_monthly_gains_before_reserve_calculation(self):
        rows = [
            {
                "month": "2026-01", "book_id": "book_gain", "book_type": "test",
                "realized_pnl_usd": "500.00", "source_window_start_date": "2026-01-30",
                "source_window_end_date": "2026-01-30", "source_scope": "test",
            },
            {
                "month": "2026-01", "book_id": "book_loss", "book_type": "test",
                "realized_pnl_usd": "-650.00", "source_window_start_date": "2026-01-30",
                "source_window_end_date": "2026-01-30", "source_scope": "test",
            },
        ]
        with patch.object(self.builder, "build_monthly_book_rows", return_value=(["2026-01-30"], rows)):
            with patch.object(self.builder, "load_eom_marks", return_value={}):
                _books, months = self.builder.build_outputs()

        self.assertEqual(months[0]["aggregate_net_realized_pnl_usd"], "-150.00")
        self.assertEqual(months[0]["positive_net_realized_profit_base_usd"], "0.00")
        self.assertEqual(months[0]["usd_reserve_generated_this_month"], "0.00")
        self.assertEqual(months[0]["net_realized_pnl_after_reserve_usd"], "-150.00")

    def test_supplied_month_end_mark_converts_pending_usd_only_at_that_mark(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            marks_path = Path(temp_dir) / "marks.csv"
            with marks_path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=[
                    "mark_date", "symbol", "exchange", "close_usd", "mark_status", "source_file", "source_file_url"
                ], lineterminator="\n")
                writer.writeheader()
                writer.writerow({
                    "mark_date": "2026-09-30", "symbol": "XMRUSD", "exchange": "KRAKEN",
                    "close_usd": "565.00", "mark_status": "provided_tradingview_eom_close",
                    "source_file": "synthetic_test_mark.csv", "source_file_url": "",
                })
            with patch.object(self.builder, "XMR_EOM_MARKS", marks_path):
                _books, months = self.builder.build_outputs()

        self.assertEqual(months[0]["usd_converted_this_eom"], "41183.97")
        self.assertEqual(months[0]["modeled_xmr_equivalent"], "72.89198230")
        self.assertEqual(months[0]["pending_usd_reserve_after_eom"], "0.00")
        self.assertEqual(months[1]["usd_converted_this_eom"], "0.00")
        self.assertEqual(months[1]["pending_usd_reserve_after_eom"], "61831.32")

    def test_only_kraken_tradingview_eom_marks_are_accepted(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            marks_path = Path(temp_dir) / "marks.csv"
            with marks_path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=[
                    "mark_date", "symbol", "exchange", "close_usd", "mark_status", "source_file", "source_file_url"
                ], lineterminator="\n")
                writer.writeheader()
                writer.writerow({
                    "mark_date": "2026-09-30", "symbol": "XMRUSD", "exchange": "OTHER",
                    "close_usd": "565.00", "mark_status": "provided_tradingview_eom_close",
                    "source_file": "wrong_exchange.csv", "source_file_url": "",
                })
            with patch.object(self.builder, "XMR_EOM_MARKS", marks_path):
                with self.assertRaisesRegex(ValueError, "Kraken"):
                    self.builder.load_eom_marks()

    def test_stale_model_window_cannot_trigger_month_end_conversion(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            marks_path = Path(temp_dir) / "marks.csv"
            with marks_path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=[
                    "mark_date", "symbol", "exchange", "close_usd", "mark_status", "source_file", "source_file_url"
                ], lineterminator="\n")
                writer.writeheader()
                writer.writerow({
                    "mark_date": "2026-10-31", "symbol": "XMRUSD", "exchange": "KRAKEN",
                    "close_usd": "565.00", "mark_status": "provided_tradingview_eom_close",
                    "source_file": "synthetic_test_mark.csv", "source_file_url": "",
                })
            with patch.object(self.builder, "XMR_EOM_MARKS", marks_path):
                with self.assertRaisesRegex(ValueError, "too far from the supplied EOM mark"):
                    self.builder.build_outputs()

    def test_attached_xmr_screenshots_are_archived_as_context_not_eom_marks(self):
        archive = ROOT / "Archive" / "Monero_EOM_conversion"
        names = [
            "Screenshot 2026-10-27 at 9.28.40 AM.jpeg",
            "Screenshot 2026-10-27 at 9.28.59 AM.jpeg",
            "Screenshot 2026-10-27 at 9.29.09 AM.jpeg",
        ]
        for name in names:
            self.assertGreater((archive / name).stat().st_size, 0)
        index = (archive / "README.md").read_text(encoding="utf-8")
        self.assertIn("not an EOM close", index)
        self.assertIn("None is used in the conversion calculation", index)


if __name__ == "__main__":
    unittest.main()
