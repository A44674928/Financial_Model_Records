"""Regression coverage for chart-added trades outside the model price universe."""

import sys
import unittest
from pathlib import Path
from zipfile import ZipFile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from model_perf_core import DXY_PRICES, MODEL_PRICES, PRICES, SESSION_DATES, UNMODELED_SYMBOLS, VARIANTS, all_series, build_dxy_daily_lots, build_lots, parse_trades  # noqa: E402


class ModelTradeScopeTests(unittest.TestCase):
    def test_model_parser_excludes_unpriced_index_fx_and_yield_books(self):
        events = parse_trades()
        modeled = {event["sym"] for event in events}
        self.assertEqual(UNMODELED_SYMBOLS, {"BTC", "ETH", "DXY", "EURUSD", "JPYUSD", "US10Y", "US30Y"})
        self.assertTrue(modeled.isdisjoint(UNMODELED_SYMBOLS))
        self.assertTrue(modeled.issubset(PRICES))
        self.assertEqual(len(events), 89)
        self.assertEqual(sum(event["date"] <= "2026-10-22" for event in events), 85)
        self.assertEqual(sum(event["date"] <= "2026-10-23" for event in events), 89)
        self.assertTrue({"BTC", "ETH"}.isdisjoint(modeled))
        self.assertEqual(SESSION_DATES[-1], "2026-10-23")

    def test_chart_directed_dxy_daily_sleeve_is_integrated_in_each_core_variant(self):
        dxy_lots, dxy_realized = build_dxy_daily_lots()
        self.assertEqual(len(dxy_lots), 35)
        self.assertEqual(sum(lot["qty"] for lot in dxy_lots), 35.0)
        self.assertEqual(dxy_lots[0]["entry_date"], "2026-09-04")
        self.assertEqual(dxy_lots[-1]["entry_date"], "2026-10-23")
        self.assertTrue(all(lot["side"] == "long" for lot in dxy_lots))
        self.assertEqual(dxy_realized, [])
        expected_pnl = sum(10_000 * (DXY_PRICES[-1] / lot["entry_px"] - 1) for lot in dxy_lots)
        self.assertAlmostEqual(expected_pnl, 2492.3028113951395, places=8)
        series, events = all_series()
        for variant in VARIANTS:
            self.assertIn("DXY", {lot["sym"] for lot in series[variant]["lots"]})
            core_lots, core_realized = build_lots(variant, events)
            core_terminal = sum(row["pnl"] for row in core_realized) + sum(
                lot["qty"] * 10_000 * (MODEL_PRICES[lot["sym"]][-1] / lot["entry_px"] - 1)
                * (1 if lot["side"] == "long" else -1)
                for lot in core_lots if lot["open"]
            )
            self.assertAlmostEqual(series[variant]["total"][-1] - core_terminal, expected_pnl, places=2)
            self.assertAlmostEqual(series[variant]["deployed"][-1] - sum(
                lot["qty"] * 10_000 for lot in core_lots
            ), 350_000.0, places=2)

    def test_open_units_are_current_exposure_not_cumulative_units_added(self):
        series, _ = all_series()
        for variant in VARIANTS:
            lots = series[variant]["lots"]
            for idx, day in enumerate(SESSION_DATES):
                expected = sum(
                    lot["qty"] for lot in lots
                    if lot["entry_idx"] <= idx
                    and (lot["close_idx"] is None or idx < lot["close_idx"])
                )
                self.assertAlmostEqual(
                    series[variant]["open_units"][idx], expected, places=8,
                    msg=f"{variant} {day}",
                )

    def test_tradingview_session_file_covers_core_and_keeps_sidecars_separate(self):
        import csv

        root = Path(__file__).resolve().parents[1]
        with (root / "data/tradingview_benchmark_session_marks_20261024.csv").open(newline="", encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))
        by_key = {(row["Ticker"], row["Date"]): row for row in rows}
        self.assertEqual(set(PRICES), {ticker for ticker, _ in by_key} - {"DXY"})
        self.assertEqual(len(PRICES), 31)
        self.assertNotIn("BTC", {ticker for ticker, _ in by_key})
        self.assertNotIn("ETH", {ticker for ticker, _ in by_key})
        self.assertEqual(len([row for row in rows if row["Ticker"] == "DXY"]), 36)
        for ticker, series in PRICES.items():
            self.assertEqual(len(series), 36)
            self.assertEqual(series[-1], float(by_key[(ticker, "2026-10-23")]["Close"]))
            self.assertEqual(series[-1], float(by_key[(ticker, "2026-10-23")]["Close"]))
        xrh0_carries = [row for row in rows if row["Ticker"] == "XRH0" and row["Mark_Status"].startswith("carry_forward_")]
        self.assertEqual(len(xrh0_carries), 5)
        self.assertEqual({row["Date"] for row in xrh0_carries}, {
            "2026-09-15", "2026-10-07", "2026-10-08", "2026-10-19", "2026-10-22",
        })
        self.assertEqual(float(PRICES["ORCL"][-1]), 126.16)
        self.assertEqual(float(PRICES["BRENT"][-1]), 117.345)
        self.assertEqual(float(PRICES["OIL"][-1]), 103.45)
        self.assertEqual(float(PRICES["LULU"][-1]), 99.01)

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

    def test_manual_automatic_target_trims_are_lot_scoped_in_all_core_variants(self):
        events = parse_trades()
        expected = {
            "BRENT": (111.412, 111.025, 117.0, 5015.62),
            "OIL": (99.04, 98.74, 102.0, 2988.69),
        }
        for variant in VARIANTS:
            lots, realized = build_lots(variant, events)
            for ticker, (manual_entry, original_entry, target, trim_pnl) in expected.items():
                tagged = [lot for lot in lots if lot["sym"] == ticker and lot.get("manual_automatic_entry")]
                self.assertEqual(sum(lot["qty"] for lot in tagged), 50.0)
                self.assertEqual([(lot["qty"], lot["open"]) for lot in tagged], [(40, True), (10, False)])
                self.assertTrue(all(lot["entry_px"] == manual_entry for lot in tagged))
                original = [
                    lot for lot in lots if lot["sym"] == ticker
                    and lot["entry_px"] == original_entry and lot["entry_date"] == "2026-10-19"
                ]
                self.assertEqual(len(original), 1)
                self.assertEqual(original[0]["qty"], 1.0)
                self.assertTrue(original[0]["open"])
                self.assertIsNone(original[0]["close_idx"])
                trim = [
                    item for item in realized
                    if item["sym"] == ticker and item["date"] == "2026-10-23" and item["qty"] == 10
                ]
                self.assertEqual(len(trim), 1)
                self.assertAlmostEqual(trim[0]["pnl"], trim_pnl, places=2)
                self.assertEqual(tagged[1]["close_px"], target)
                self.assertEqual(tagged[1]["close_idx"], SESSION_DATES.index("2026-10-23"))

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
            for name in ("BRENT", "OIL"):
                log_content = (root / f"trades/{name}.txt").read_bytes()
                self.assertEqual(archive.read(f"trades/{name}.txt"), log_content)

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
        self.assertEqual(PRICES["ORCL"][oct23], 126.16)
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
        self.assertTrue(text.startswith(
            "# THE ONE MODEL\n\n![THE ONE MODEL vs THE WINNING MODEL — equal terminal gross additions]"
        ))
        self.assertIn("> **TradingView-only interim recalculation — 2026-10-24.**", text)
        self.assertIn("the-one-model-split-portfolio.png", text)
        comparison_chart = "Charts/superstructure/the-one-model-vs-winning-model.png"
        self.assertIn(comparison_chart, text)
        self.assertLess(text.index(comparison_chart), text.index("Charts/superstructure/the-one-model.png"))
        generator = (root / "scripts/build_model_performance.py").read_text(encoding="utf-8")
        self.assertIn('A("# THE ONE MODEL")', generator)
        self.assertIn("the-one-model-vs-winning-model.png", generator)
        self.assertIn("the-one-model.png", generator)
        self.assertIn("the-one-model-split-portfolio.png", generator)
        for relpath in (
            "Charts/superstructure/the-one-model.png",
            "Charts/superstructure/the-one-model-split-portfolio.png",
        ):
            graph = root / relpath
            self.assertTrue(graph.is_file())
            self.assertEqual(graph.read_bytes()[:8], b"\x89PNG\r\n\x1a\n")
        self.assertIn("`89` direct-price events plus `1` DXY direction signals out of `99` total 2026 log events", text)
        self.assertIn("`0` direct events after cutoff", text)
        self.assertIn("`31` direct-price core tickers plus the integrated 1U/DAY/DXY sleeve", text)
        self.assertIn("EURUSD, JPYUSD, US10Y, and US30Y", text)
        self.assertIn("Legacy Model-Level US10Y Additive Carry (Reference Only)", text)
        self.assertIn("remain sensitivities rather than additional core PnL", text)
        self.assertIn("tradingview_benchmark_session_marks_20261024.csv", text)
        self.assertIn("BTC and ETH remain excluded pending recalibration", text)
        self.assertIn("five missing source sessions", text)
        self.assertIn("No Yahoo or historical-series fill is used", text)
        self.assertIn("1U/DAY/DXY index-return sleeve is included in every core variant", text)
        self.assertIn("Crypto Sidecar — Pending TradingView Recalibration", text)
        self.assertIn("TradingView Energy and Currency Desk Sidecars.md", text)
        self.assertIn("shared/variant-specific 1U/EOD force models", text)
        self.assertIn("Model Calculation Guide.md", text)
        self.assertIn("89` direct-price events plus `1` DXY direction signals", text)
        self.assertIn("master ledger are not recalculated by this run", text)
        self.assertIn("TradingView Energy Sidecar", text)
        self.assertIn("tradingview_energy_sidecar_daily_20261024.csv", text)
        self.assertIn("0.05U, 1U, and 10U", text)
        self.assertIn("10U TradingView energy schedule", text)
        self.assertIn("14-energy-eod-mark-history.png", text)
        self.assertNotIn("14-energy-live-mark-overlay.png", text)
        self.assertNotIn("Separate Approximate Quotes", text)
        self.assertNotIn("$115.72", text)
        explorer = (root / "Model Performance Explorer.html").read_text(encoding="utf-8")
        self.assertIn("TradingView-only interim core", explorer)
        self.assertIn("tradingview_benchmark_coverage_20261024.csv", explorer)
        self.assertIn("14-energy-eod-mark-history.png", explorer)
        chart = root / "Charts/performance/14-energy-eod-mark-history.png"
        self.assertTrue(chart.is_file())
        self.assertEqual(chart.read_bytes()[:8], b"\x89PNG\r\n\x1a\n")
        self.assertFalse((root / "Charts/performance/14-energy-live-mark-overlay.png").exists())
        for chart in sorted((root / "Charts/performance").glob("*.png")):
            chart_path = chart.relative_to(root).as_posix()
            if chart.name == "19-oil-desk-daily-accumulation.png":
                continue  # retained legacy chart; current energy schedules use the TV sidecar CSV
            self.assertIn(chart_path, text, f"comparison report is missing {chart_path}")
        self.assertIn("Charts/CLN25/Weekend%20Oil/24-weekend-oil-50u-positions.png", text)
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
