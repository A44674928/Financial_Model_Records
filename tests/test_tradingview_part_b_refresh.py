"""Regression coverage for the revised user-provided Part B TradingView archive."""

import csv
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from import_tradingview_price_lists_part_b import import_part_b  # noqa: E402
from model_perf_core import SESSION_DATES, all_series  # noqa: E402


class TradingViewPartBRefreshTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = import_part_b()
        with (ROOT / "data/tradingview_benchmark_price_lists_part_b_20261024.csv").open(
            newline="", encoding="utf-8"
        ) as handle:
            cls.raw_rows = list(csv.DictReader(handle))
        with (ROOT / "data/tradingview_benchmark_session_marks_20261024.csv").open(
            newline="", encoding="utf-8"
        ) as handle:
            cls.session_rows = list(csv.DictReader(handle))

    def test_updated_archive_provenance_and_lly_row(self):
        self.assertEqual(self.manifest["source_repository_commit"], "d5228326d034c8d515f1a8ca1c484c70c738904f")
        self.assertEqual(
            self.manifest["source_archive_sha256"],
            "12e781167a8c62801e254f00cf62c56ae548b576f01066bc15a962159e742776",
        )
        row = next(
            row for row in self.raw_rows
            if row["Ticker"] == "LLY" and row["Date"] == "2026-10-20"
        )
        self.assertEqual(row["Close"], "1283.66000000")
        self.assertIn("/blob/d5228326d034c8d515f1a8ca1c484c70c738904f/", row["Source_File_URL"])
        self.assertEqual(row["Archive_SHA256"], self.manifest["source_archive_sha256"])

    def test_corrected_mark_flows_to_core_and_removes_false_pnl_spike(self):
        aligned = next(
            row for row in self.session_rows
            if row["Ticker"] == "LLY" and row["Date"] == "2026-10-20"
        )
        self.assertEqual(aligned["Close"], "1283.66000000")
        series, _ = all_series()
        i = SESSION_DATES.index("2026-10-20")
        expected = {"V1": -575.22, "V2": -868.55, "V3A": 125.56, "V3B": -868.55}
        for variant, model in series.items():
            delta = model["total"][i] - model["total"][i - 1]
            self.assertAlmostEqual(delta, expected[variant], places=2)
            self.assertLess(abs(delta), 2_000)


if __name__ == "__main__":
    unittest.main()
