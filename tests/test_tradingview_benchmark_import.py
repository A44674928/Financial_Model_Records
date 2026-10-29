"""Coverage and provenance tests for the exclusive TradingView benchmark import."""

import csv
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from import_tradingview_price_lists import COVERAGE_CSV, PRICE_CSV, import_archive  # noqa: E402


class TradingViewBenchmarkImportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = import_archive(allow_flagged_legacy=True)
        with PRICE_CSV.open(newline="", encoding="utf-8") as handle:
            cls.prices = list(csv.DictReader(handle))
        with COVERAGE_CSV.open(newline="", encoding="utf-8") as handle:
            cls.coverage = {row["Ticker"]: row for row in csv.DictReader(handle)}

    def test_default_import_rejects_post_cutoff_tradingview_data(self):
        with self.assertRaisesRegex(ValueError, "blocked by the post-2026-10-19 policy"):
            import_archive()

    def test_legacy_rows_are_flagged_only_under_explicit_preservation_override(self):
        post_cutoff = [row for row in self.prices if row["Date"] >= "2026-10-20"]
        self.assertTrue(post_cutoff)
        self.assertTrue(all(row["Policy_Status"] == "FLAGGED_LEGACY_EXCEPTION_NOT_FOR_ACTIVE_USE" for row in post_cutoff))
        self.assertTrue(self.manifest["legacy_exception_preservation_override"])
        self.assertEqual(self.manifest["tradingview_policy_cutoff_date"], "2026-10-20")

    def test_only_ticker_specific_files_are_imported(self):
        expected = {
            "BRENT", "CAT", "GEV", "HD", "INTC", "LCID", "LMT", "LULU",
            "META", "OIL", "ORCL", "PLTR", "SPCX", "TSLA", "VLO",
        }
        self.assertEqual(set(self.manifest["provided_symbols"]), expected)
        self.assertEqual(self.manifest["provided_symbol_count"], 15)
        self.assertEqual(self.manifest["missing_symbol_count"], 16)
        self.assertEqual(len(self.prices), 571)
        self.assertNotIn("TICKER", {row["Ticker"] for row in self.prices})
        self.assertNotIn("USOIL", {row["Ticker"] for row in self.prices})
        self.assertEqual(self.manifest["source_repository_commit"], "22540a55b08214460bb6cd7e64d8174c1ee1e1c2")

    def test_all_supplied_symbols_cover_every_comparison_session(self):
        for ticker in self.manifest["provided_symbols"]:
            row = self.coverage[ticker]
            self.assertEqual(row["Coverage_Status"], "complete_for_comparison_sessions", ticker)
            self.assertEqual(int(row["Comparison_Session_Rows"]), 36, ticker)
            self.assertEqual(row["Last_Provided_Date"], "2026-10-23", ticker)

    def test_missing_symbols_are_explicit_and_not_filled_from_legacy_sources(self):
        expected_missing = {
            "AAPL", "AMZN", "CVX", "DIS", "LLY", "NET", "NFLX",
            "NVDA", "PEP", "RIVN", "TMO", "UPS", "V", "WMT", "XLE", "XRH0",
        }
        self.assertEqual(set(self.manifest["missing_symbols"]), expected_missing)
        for ticker in expected_missing:
            row = self.coverage[ticker]
            self.assertEqual(row["Coverage_Status"], "missing_user_price_list")
            self.assertEqual(row["2026-10-23_Close"], "")
            self.assertIn("not to be substituted", row["Source"])
        self.assertNotIn("BTC", self.manifest["missing_symbols"])
        self.assertNotIn("ETH", self.manifest["missing_symbols"])

    def test_user_supplied_lulu_energy_and_gev_values_are_preserved(self):
        endpoint = {row["Ticker"]: float(row["Close"]) for row in self.prices if row["Date"] == "2026-10-23"}
        self.assertEqual(endpoint["LULU"], 99.01)
        self.assertEqual(endpoint["BRENT"], 117.345)
        self.assertEqual(endpoint["OIL"], 103.45)
        self.assertEqual(endpoint["GEV"], 815.0)
        brent_sep7 = next(row for row in self.prices if row["Ticker"] == "BRENT" and row["Date"] == "2026-09-07")
        self.assertEqual(float(brent_sep7["Close"]), 99.153)
        brent_sep28 = next(row for row in self.prices if row["Ticker"] == "BRENT" and row["Date"] == "2026-09-28")
        self.assertEqual(float(brent_sep28["Close"]), 102.676)
        with (ROOT / "data/energy_provider_eod_marks_v1.csv").open(newline="", encoding="utf-8") as handle:
            prior_energy = list(csv.DictReader(handle))
        old_sep28 = next(row for row in prior_energy if row["Ticker"] == "BRENT" and row["Date"] == "2026-09-28")
        self.assertEqual(float(old_sep28["EOD_Close"]), 103.676)

    def test_legacy_comparisons_are_prominently_marked_as_not_refreshed(self):
        report = (ROOT / "Model Performance Comparison.md").read_text(encoding="utf-8")
        strategy = (ROOT / "Strategy and Sidecar Comparison.md").read_text(encoding="utf-8")
        explorer = (ROOT / "Model Performance Explorer.html").read_text(encoding="utf-8")
        dxy = (ROOT / "DXY-Equivalent Portfolio Snapshot.md").read_text(encoding="utf-8")
        self.assertIn("TradingView-only model update — 2026-10-26", report)
        self.assertIn("No legacy or substitute prices are used", report)
        self.assertIn("TradingView sidecar schedules through 2026-10-26", strategy)
        self.assertIn("TradingView-only core — 2026-10-26", explorer)
        self.assertIn("integrated chart-directed 1U/DAY/DXY", explorer)
        self.assertIn("Historical view—not recalculated", dxy)


if __name__ == "__main__": 

    unittest.main()
