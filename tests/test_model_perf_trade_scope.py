"""Regression coverage for chart-added trades outside the model price universe."""

import sys
import unittest
from pathlib import Path
from zipfile import ZipFile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from model_perf_core import PRICES, SESSION_DATES, UNMODELED_SYMBOLS, VARIANTS, all_series, build_lots, parse_trades  # noqa: E402


class ModelTradeScopeTests(unittest.TestCase):
    def test_model_parser_excludes_unpriced_index_fx_and_yield_books(self):
        events = parse_trades()
        modeled = {event["sym"] for event in events}
        self.assertEqual(UNMODELED_SYMBOLS, {"DXY", "EURUSD", "JPYUSD", "US10Y", "US30Y"})
        self.assertTrue(modeled.isdisjoint(UNMODELED_SYMBOLS))
        self.assertTrue(modeled.issubset(PRICES))
        self.assertEqual(len(events), 88)
        self.assertEqual(sum(event["date"] <= "2026-10-22" for event in events), 86)
        self.assertEqual(sum(event["date"] <= "2026-10-23" for event in events), 88)
        self.assertEqual(SESSION_DATES[-1], "2026-10-23")


    def test_oct23_eod_source_covers_all_direct_price_symbols(self):
        import csv

        root = Path(__file__).resolve().parents[1]
        with (root / "data/consolidated_portfolio_closes_v7.csv").open(newline="", encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))
        marks = {row["Ticker"]: float(row["EOD_Close"]) for row in rows if row["Date"] == "2026-10-23"}
        sources = {row["Ticker"]: row["Source"] for row in rows if row["Date"] == "2026-10-23"}
        self.assertEqual(set(PRICES), set(marks) - {"US10Y", "US30Y"})
        self.assertEqual(PRICES["AAPL"][-1], marks["AAPL"])
        self.assertEqual(marks["CVX"], 233.21)
        self.assertEqual(marks["WMT"], 119.89)
        self.assertEqual(marks["TMO"], 673.82)
        self.assertEqual(PRICES["CVX"][-1], 233.21)
        self.assertEqual(PRICES["WMT"][-1], 119.89)
        self.assertEqual(PRICES["TMO"][-1], 673.82)
        self.assertEqual(marks["UPS"], 101.06)
        self.assertEqual(PRICES["UPS"][-1], 101.06)
        self.assertEqual(PRICES["BTC"][-1], 81227.04)
        self.assertEqual(PRICES["ETH"][-1], 2408.47)
        self.assertEqual(PRICES["NFLX"][-1], 65.85)
        self.assertEqual(PRICES["RIVN"][-1], 11.83)
        self.assertEqual(PRICES["LCID"][-1], 3.52)
        self.assertEqual(PRICES["XRH0"][-1], 785.0)
        self.assertEqual(PRICES["XRH0"][SESSION_DATES.index("2026-10-22")], 790.0)
        self.assertEqual(PRICES["ORCL"][-1], 175.4)
        self.assertEqual(PRICES["BRENT"][-1], 117.345)
        self.assertEqual(PRICES["OIL"][-1], 103.45)
        self.assertEqual(marks["US10Y"], 4.986)
        self.assertEqual(marks["US30Y"], 5.43)
        self.assertEqual(sources["BRENT"], "User-provided BlackBull Markets Brent Cash EOD")
        self.assertEqual(sources["OIL"], "User-provided TradingView TVC:USOIL EOD")
        self.assertEqual(sources["LCID"], "User-provided mark correction")
        self.assertEqual(sources["XRH0"], "User-provided EOD correction")
        with (root / "data/consolidated_portfolio_closes_v2.csv").open(newline="", encoding="utf-8") as fh:
            old_rows = list(csv.DictReader(fh))
        old_marks = {row["Ticker"]: float(row["EOD_Close"]) for row in old_rows if row["Date"] == "2026-10-23"}
        self.assertEqual(old_marks["NFLX"], 762.1)
        self.assertEqual(old_marks["BTC"], 68250.0)
        with (root / "data/eod_close_reconciliation_20261023_v2_to_v3.csv").open(newline="", encoding="utf-8") as fh:
            v3_audit = list(csv.DictReader(fh))
        self.assertEqual(len(v3_audit), 35)
        self.assertEqual(sum(row["Price_Status"] == "price_changed" for row in v3_audit), 6)
        self.assertEqual(sum(row["Source_Status"] == "source_changed" for row in v3_audit), 2)
        with (root / "data/eod_close_reconciliation_20261023_v3_to_v4.csv").open(newline="", encoding="utf-8") as fh:
            v4_audit = list(csv.DictReader(fh))
        self.assertEqual(len(v4_audit), 35)
        self.assertEqual(sum(row["Price_Status"] == "price_changed" for row in v4_audit), 3)
        self.assertEqual({row["Ticker"] for row in v4_audit if row["Price_Status"] == "price_changed"}, {"CVX", "WMT", "TMO"})
        with (root / "data/eod_close_reconciliation_20261023_v4_to_v5.csv").open(newline="", encoding="utf-8") as fh:
            v5_audit = list(csv.DictReader(fh))
        self.assertEqual(len(v5_audit), 35)
        self.assertEqual(sum(row["Price_Status"] == "price_changed" for row in v5_audit), 1)
        self.assertEqual({row["Ticker"] for row in v5_audit if row["Price_Status"] == "price_changed"}, {"UPS"})
        with (root / "data/eod_close_reconciliation_20261023_v5_to_v6.csv").open(newline="", encoding="utf-8") as fh:
            v6_audit = list(csv.DictReader(fh))
        self.assertEqual(len(v6_audit), 35)
        self.assertEqual({row["Ticker"] for row in v6_audit if row["Price_Status"] == "price_changed"}, {"BRENT", "OIL"})
        self.assertEqual(sum(row["Source_Status"] == "source_changed" for row in v6_audit), 2)
        with (root / "data/active_price_source_registry_v2.csv").open(newline="", encoding="utf-8") as fh:
            registry = list(csv.DictReader(fh))
        registry_by_ticker = {row["Internal_Ticker"]: row for row in registry}
        self.assertIn("BlackBull Brent Cash EOD (user-provided)", registry_by_ticker["BRENT"]["Historical_Instrument"])
        self.assertIn("TradingView TVC:USOIL EOD (user-provided)", registry_by_ticker["OIL"]["Historical_Instrument"])
        self.assertIn("pre-entry context", registry_by_ticker["BRENT"]["Verification_Status"])
        self.assertEqual(PRICES["BRENT"][SESSION_DATES.index("2026-09-23")], 103.158)
        self.assertEqual(PRICES["OIL"][SESSION_DATES.index("2026-09-10")], 103.94)
        with (root / "data/energy_provider_eod_marks_v1.csv").open(newline="", encoding="utf-8") as fh:
            energy_rows = list(csv.DictReader(fh))
        self.assertEqual(sum(row["Ticker"] == "BRENT" for row in energy_rows), 23)
        self.assertEqual(sum(row["Ticker"] == "OIL" for row in energy_rows), 32)
        session_index = {day: i for i, day in enumerate(SESSION_DATES)}
        for row in energy_rows:
            self.assertAlmostEqual(
                PRICES[row["Ticker"]][session_index[row["Date"]]],
                float(row["EOD_Close"]), places=10,
            )
        with (root / "data/eod_close_reconciliation_20261023_v6_to_v7.csv").open(newline="", encoding="utf-8") as fh:
            v7_audit = list(csv.DictReader(fh))
        self.assertEqual({row["Ticker"] for row in v7_audit if row["Price_Status"] == "price_changed"}, {"BRENT", "OIL"})
        with (root / "data/model_performance_tickers.csv").open(newline="", encoding="utf-8") as fh:
            ticker_pnl = list(csv.DictReader(fh))
        v1_pnl = {row["ticker"]: float(row["total_usd"]) for row in ticker_pnl if row["variant"] == "V1"}
        self.assertAlmostEqual(v1_pnl["CVX"], 3406.36, places=2)
        self.assertAlmostEqual(v1_pnl["WMT"], 1499.14, places=2)
        self.assertAlmostEqual(v1_pnl["TMO"], 163.35, places=2)
        self.assertAlmostEqual(v1_pnl["AAPL"], 2037.22, places=2)
        self.assertAlmostEqual(v1_pnl["NVDA"], -811.45, places=2)
        self.assertAlmostEqual(v1_pnl["UPS"], -1422.48, places=2)
        self.assertAlmostEqual(v1_pnl["BRENT"], 5026.57, places=2)
        self.assertAlmostEqual(v1_pnl["OIL"], 6614.56, places=2)
        with (root / "data/eod_close_reconciliation_20261023.csv").open(newline="", encoding="utf-8") as fh:
            audit = list(csv.DictReader(fh))
        self.assertEqual(len(audit), 35)
        self.assertEqual(sum(row["Status"] == "price_changed" for row in audit), 26)
        self.assertEqual(sum(row["Status"] == "source_only" for row in audit), 2)

    def test_chart_reconciled_positions_are_in_model_replay(self):
        events = parse_trades()
        positions = {
            (event["sym"], event["date"], event["px"])
            for event in events
            if event["kind"] == "entry"
        }
        expected = {
            ("META", "2026-09-08", 616.67),
            ("OIL", "2026-09-10", 97.32),
            ("OIL", "2026-09-24", 93.74),
            ("BRENT", "2026-10-04", 106.446),
            ("CVX", "2026-10-05", 206.83),
        }
        self.assertTrue(expected.issubset(positions))

    def test_oct23_us30y_long_is_separate_and_synced_to_zip(self):
        root = Path(__file__).resolve().parents[1]
        log = root / "trades/US30Y.txt"
        content = log.read_bytes()
        self.assertIn(
            b"2026-10-23 06:30 MST | SIMULATED PAPER [LONG] | entry: [Market @ ~5.311%]",
            content,
        )
        with ZipFile(root / "trades.zip") as archive:
            self.assertEqual(archive.read("trades/US30Y.txt"), content)
            self.assertEqual(archive.read("trades/index.txt"), (root / "trades/index.txt").read_bytes())

    def test_oct23_orcl_long_is_in_new_terminal_replay_but_not_oct22_endpoint(self):
        events = parse_trades()
        orcl = next(
            event for event in events
            if event["sym"] == "ORCL" and event["date"] == "2026-10-23"
        )
        self.assertEqual(orcl["tag"], "LONG")
        self.assertEqual(orcl["kind"], "entry")
        self.assertEqual(orcl["px"], 125.83)
        self.assertEqual(orcl["units"], 2.5)
        oct22 = SESSION_DATES.index("2026-10-22")
        oct23 = SESSION_DATES.index("2026-10-23")
        self.assertEqual(PRICES["ORCL"][oct22], 125.54)
        self.assertEqual(PRICES["ORCL"][oct23], 175.4)
        for variant in VARIANTS:
            lots, _ = build_lots(variant, events)
            orcl_lot = next(
                lot for lot in lots
                if lot["sym"] == "ORCL" and lot["entry_px"] == 125.83
            )
            self.assertEqual(orcl_lot["entry_idx"], oct23)
            self.assertEqual(orcl_lot["qty"], 2.5)

        root = Path(__file__).resolve().parents[1]
        log = (root / "trades/ORCL.txt").read_bytes()
        self.assertIn(b"2026-10-23 06:30 MST | SIMULATED PAPER [LONG]", log)
        self.assertIn(b"size: [2.5 units ($25,000)]", log)
        with ZipFile(root / "trades.zip") as archive:
            self.assertEqual(archive.read("trades/ORCL.txt"), log)
            self.assertEqual(archive.read("trades/index.txt"), (root / "trades/index.txt").read_bytes())

    def test_lcid_small_caps_pilot_has_four_entries_at_oct22_and_five_at_oct23(self):
        root = Path(__file__).resolve().parents[1]
        events = parse_trades()
        lcid_events = [event for event in events if event["sym"] == "LCID"]
        expected_entries = [
            ("2026-10-20", 2.92),
            ("2026-10-20", 3.01),
            ("2026-10-21", 3.30),
            ("2026-10-22", 3.43),
            ("2026-10-23", 3.47),
        ]
        self.assertEqual([(event["date"], event["px"]) for event in lcid_events], expected_entries)
        self.assertTrue(all(event["tag"] == "LONG" and event["units"] == 1 for event in lcid_events))
        oct22_index = SESSION_DATES.index("2026-10-22")
        self.assertEqual(PRICES["LCID"][oct22_index], 3.46)
        self.assertEqual(PRICES["LCID"][SESSION_DATES.index("2026-10-21")], 3.21)
        expected_oct22_pnl = sum(10_000 * (3.46 / px - 1) for _, px in expected_entries[:4])
        for variant in VARIANTS:
            lots, _ = build_lots(variant, events)
            lcid_lots = [lot for lot in lots if lot["sym"] == "LCID"]
            self.assertEqual(len(lcid_lots), 5)
            self.assertAlmostEqual(sum(lot["qty"] for lot in lcid_lots), 5.0)
            oct22_lots = [lot for lot in lcid_lots if lot["entry_idx"] <= oct22_index]
            self.assertEqual(len(oct22_lots), 4)
            oct22_pnl = sum(
                lot["qty"] * 10_000 * (PRICES["LCID"][oct22_index] / lot["entry_px"] - 1)
                for lot in oct22_lots
            )
            self.assertAlmostEqual(oct22_pnl, expected_oct22_pnl, places=8)
        self.assertEqual(PRICES["LCID"][SESSION_DATES.index("2026-10-23")], 3.52)

        with ZipFile(root / "trades.zip") as archive:
            self.assertEqual(archive.read("trades/LCID.txt"), (root / "trades/LCID.txt").read_bytes())
            self.assertEqual(archive.read("trades/index.txt"), (root / "trades/index.txt").read_bytes())

    def test_comparison_report_states_model_coverage_and_unreconciled_master(self):
        root = Path(__file__).resolve().parents[1]
        report = root / "Model Performance Comparison.md"
        text = report.read_text(encoding="utf-8")
        self.assertTrue(text.startswith("# THE ONE MODEL\n\n## Model Performance Comparison"))
        generator = (root / "scripts/build_model_performance.py").read_text(encoding="utf-8")
        self.assertIn('A("# THE ONE MODEL")', generator)
        self.assertIn("`88` in-window price-covered events out of `95` total 2026 log events", text)
        self.assertIn("`0` after cutoff", text)
        self.assertIn("`33` price-covered symbols", text)
        self.assertIn("DXY, EURUSD, JPYUSD, US10Y and US30Y", text)
        self.assertIn("Legacy Model-Level US10Y Additive Carry (Reference Only)", text)
        self.assertIn("Whole Portfolio Yield Multiplier Explorer.html", text)
        self.assertIn("consolidated_portfolio_closes_v7.csv", text)
        self.assertIn("Selected preserved v1 Yahoo mark (v3→v4)", text)
        self.assertIn("CVX `$233.21`, WMT `$119.89`, TMO `$673.82`, and UPS `$101.06`", text)
        self.assertIn("saved TradingView/Yahoo comparison candidate remains audit-only", text)
        self.assertIn("User-provided exact BlackBull Brent Cash EOD", text)
        self.assertIn("active_price_source_registry_v2.csv", text)
        self.assertIn("Oil Desk EOD Accumulation Hypothetical.md", text)
        self.assertIn("shared/variant-specific 1U/EOD force models", text)
        self.assertIn("Model Calculation Guide.md", text)
        self.assertIn("84.5U ($845,000)", text)
        self.assertIn("master PnL report remains", text)
        self.assertIn("unrecalculated and unreconciled", text)
        self.assertIn("Energy EOD Marks Used for the Core Replay and Oil Sidecar", text)
        self.assertIn("energy_provider_eod_marks_v1.csv", text)
        self.assertIn("Sep. 23–Oct. 23, 2026 | 23 | $117.345", text)
        self.assertIn("Sep. 10–Oct. 23, 2026 | 32 | $103.45", text)
        self.assertIn("14-energy-eod-mark-history.png", text)
        self.assertNotIn("14-energy-live-mark-overlay.png", text)
        self.assertNotIn("Separate Approximate Quotes", text)
        self.assertNotIn("$115.72", text)
        explorer = (root / "Model Performance Explorer.html").read_text(encoding="utf-8")
        self.assertIn("same exact user-provided daily marks", explorer)
        self.assertIn("data/energy_provider_eod_marks_v1.csv", explorer)
        self.assertIn("14-energy-eod-mark-history.png", explorer)
        chart = root / "Charts/performance/14-energy-eod-mark-history.png"
        self.assertTrue(chart.is_file())
        self.assertEqual(chart.read_bytes()[:8], b"\x89PNG\r\n\x1a\n")
        self.assertFalse((root / "Charts/performance/14-energy-live-mark-overlay.png").exists())
        for chart in sorted((root / "Charts/performance").glob("*.png")):
            chart_path = chart.relative_to(root).as_posix()
            self.assertIn(chart_path, text, f"comparison report is missing {chart_path}")
        self.assertIn("all **16 Core × variant-specific 1U/EOD pairings**", text)
        self.assertIn("all **32 series**", text)
        self.assertIn("deployed-notional ratio, **not an account return**", text)
        self.assertIn("fixed-$500/EOD model and 1U/EOD alternatives are separate", text)
        self.assertIn("chart-posting prices recorded in the trade log", text)
        self.assertIn("`$115.11`", text)
        self.assertNotIn("1-Minute Close-Up", text)
        self.assertNotIn("13-minute-intc-hazard-flip.png", text)
        self.assertFalse((root / "Charts/performance/13-minute-intc-hazard-flip.png").exists())
        self.assertTrue((root / "data/model_performance_minute_intc.csv").is_file())
        self.assertNotIn("minute-closeup", explorer)
        self.assertNotIn("13-minute-intc-hazard-flip.png", explorer)
        self.assertNotIn("$125.59", explorer)
        self.assertNotIn("$115.72", explorer)
        self.assertNotIn("100.94", explorer)


if __name__ == "__main__":
    unittest.main()
