"""Regression coverage for chart-added trades outside the model price universe."""

import sys
import unittest
from pathlib import Path
from zipfile import ZipFile
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import model_perf_core
from model_perf_core import DXY_PRICES, MODEL_PRICES, PRICES, SESSION_DATES, UNMODELED_SYMBOLS, VARIANTS, all_series, build_dxy_daily_lots, build_lots, parse_trades  # noqa: E402


class ModelTradeScopeTests(unittest.TestCase):
    def test_model_parser_excludes_unpriced_index_fx_and_yield_books(self):
        events = parse_trades()
        modeled = {event["sym"] for event in events}
        self.assertEqual(UNMODELED_SYMBOLS, {"BTC", "ETH", "ALIUSD", "DXY", "EURUSD", "JPYUSD", "US10Y", "US30Y"})
        self.assertTrue(modeled.isdisjoint(UNMODELED_SYMBOLS))
        self.assertTrue(modeled.issubset(PRICES))
        self.assertEqual(len(events), 116)
        self.assertEqual(sum(event["date"] <= "2026-10-22" for event in events), 85)
        self.assertEqual(sum(event["date"] <= "2026-10-23" for event in events), 91)
        self.assertTrue({"BTC", "ETH"}.isdisjoint(modeled))
        self.assertEqual(SESSION_DATES[-1], "2026-10-26")
        self.assertEqual(sum(event["date"] <= "2026-10-26" for event in events), 116)

    def test_reported_ats_core_entries_and_meta_short_close_are_separate_lots(self):
        # Isolate the earlier Oct. 26 ATS action before the later user-directed
        # 13:00 V3A/INTC closure events.
        events = [event for event in parse_trades() if "USER-DIRECTED MODEL CLOSURE" not in event["note"]]
        date = "2026-10-26"
        additions = [event for event in events if event["date"] == date and event["time"] == "06:30"]
        self.assertEqual(len(additions), 4)
        self.assertEqual({event["sym"] for event in additions}, {"GEV", "RIVN", "META"})
        self.assertTrue(all("AUTOMATED TRADING SYSTEM LIVE POSITIONS" in event["note"] for event in additions))
        root = Path(__file__).resolve().parents[1]
        with ZipFile(root / "trades.zip") as archive:
            for filename in ("GEV.txt", "RIVN.txt", "INTC.txt", "META.txt", "index.txt"):
                self.assertEqual(archive.read(f"trades/{filename}"), (root / "trades" / filename).read_bytes())
        self.assertIn("126 standardized log events currently recorded", (root / "trades/index.txt").read_text())
        extended_dates = list(SESSION_DATES)
        with patch.object(model_perf_core, "SESSION_DATES", extended_dates), patch.object(
            model_perf_core, "N_SESS", len(extended_dates)
        ):
            for variant in VARIANTS:
                lots, realized = build_lots(variant, events)
                for ticker, price in (("GEV", 823.81), ("RIVN", 11.77), ("META", 637.2)):
                    new_longs = [lot for lot in lots if lot["sym"] == ticker and lot["side"] == "long"
                                 and lot["entry_date"] == date and lot["entry_px"] == price]
                    self.assertEqual(len(new_longs), 1, (variant, ticker))
                    self.assertEqual(new_longs[0]["qty"], 1)
                date_closes = [row for row in realized if row["sym"] == "META" and row["date"] == date]
                if variant in ("V1", "V3A"):
                    self.assertEqual(len(date_closes), 1)
                    self.assertEqual(date_closes[0]["qty"], 1)
                else:
                    # SAR paths already covered the active short before this
                    # date, so the user-reported close does not double-close it.
                    self.assertEqual(date_closes, [])
                open_meta_shorts = [lot for lot in lots if lot["sym"] == "META" and lot["side"] == "short" and lot["open"]]
                if variant == "V1":
                    self.assertEqual(open_meta_shorts, [])
                elif variant == "V3A":
                    self.assertEqual(sum(lot["qty"] for lot in open_meta_shorts), 4)
                else:
                    self.assertEqual(open_meta_shorts, [])

    def test_user_directed_short_closures_cover_remaining_exposure_at_supplied_prices(self):
        events = parse_trades()
        date = "2026-10-26"
        extended_dates = list(SESSION_DATES)
        with patch.object(model_perf_core, "SESSION_DATES", extended_dates), patch.object(
            model_perf_core, "N_SESS", len(extended_dates)
        ):
            for variant, expected_intc_closed, expected_meta_closed in (
                ("V1", 2, 1), ("V2", 0, 0), ("V3A", 6, 5), ("V3B", 0, 0)
            ):
                lots, realized = build_lots(variant, events)
                self.assertEqual(
                    [lot for lot in lots if lot["side"] == "short" and lot["open"]
                     and lot["sym"] in {"INTC", "META"}],
                    [],
                    variant,
                )
                new_intc_longs = [
                    lot for lot in lots
                    if lot["sym"] == "INTC" and lot["side"] == "long"
                    and lot["entry_date"] == date and lot["entry_px"] == 87.55 and lot["open"]
                ]
                self.assertEqual(sum(lot["qty"] for lot in new_intc_longs), 6, variant)
                intc_closes = [
                    lot for lot in lots
                    if lot["sym"] == "INTC" and lot["side"] == "short" and lot.get("close_date") == date
                ]
                self.assertEqual(sum(lot["qty"] for lot in intc_closes), expected_intc_closed)
                self.assertTrue(all(lot["close_px"] == 87.55 for lot in intc_closes))
                meta_closes = [
                    lot for lot in lots
                    if lot["sym"] == "META" and lot["side"] == "short" and lot.get("close_date") == date
                ]
                self.assertEqual(sum(lot["qty"] for lot in meta_closes), expected_meta_closed)
                self.assertTrue(all(lot["close_px"] == 637.20 for lot in meta_closes))
                close_events = [
                    event for event in events
                    if event["date"] == date and event["time"] == "13:00"
                    and event["kind"] == "exit" and event["sym"] in {"INTC", "META"}
                ]
                self.assertEqual({(event["sym"], event["units"], event["px"]) for event in close_events},
                                 {("INTC", 6, 87.55), ("META", 4, 637.2)})

    def test_manually_approved_short_closes_and_new_short_opens_reconcile(self):
        events = parse_trades()
        date = "2026-10-26"
        extended_dates = list(SESSION_DATES)
        with patch.object(model_perf_core, "SESSION_DATES", extended_dates), patch.object(
            model_perf_core, "N_SESS", len(extended_dates)
        ):
            expected_closed = {
                "V1": {"CAT": 1, "PLTR": 3, "TSLA": 1},
                "V2": {"CAT": 0, "PLTR": 2, "TSLA": 1},
                "V3A": {"CAT": 2, "PLTR": 3, "TSLA": 1},
                "V3B": {"CAT": 0, "PLTR": 2, "TSLA": 1},
            }
            for variant in VARIANTS:
                lots, _ = build_lots(variant, events)
                for ticker in ("CAT", "PLTR", "TSLA"):
                    self.assertFalse(
                        any(lot["sym"] == ticker and lot["side"] == "short" and lot["open"] for lot in lots),
                        (variant, ticker),
                    )
                    closed = [
                        lot for lot in lots if lot["sym"] == ticker and lot["side"] == "short"
                        and lot.get("close_date") == date
                    ]
                    self.assertEqual(sum(lot["qty"] for lot in closed), expected_closed[variant][ticker])
                for ticker, price, total in (("DIS", 110.27, 2), ("UPS", 100.08, 3), ("SPCX", 148.46, 4)):
                    open_shorts = [
                        lot for lot in lots if lot["sym"] == ticker and lot["side"] == "short" and lot["open"]
                    ]
                    self.assertEqual(sum(lot["qty"] for lot in open_shorts), total, (variant, ticker))
                    new_lots = [lot for lot in open_shorts if lot["entry_date"] == date and lot["entry_px"] == price]
                    self.assertEqual(sum(lot["qty"] for lot in new_lots), 1, (variant, ticker))
        root = Path(__file__).resolve().parents[1]
        with ZipFile(root / "trades.zip") as archive:
            for filename in ("CAT.txt", "DIS.txt", "PLTR.txt", "SPCX.txt", "TSLA.txt", "UPS.txt", "index.txt"):
                self.assertEqual(archive.read(f"trades/{filename}"), (root / "trades" / filename).read_bytes())
        self.assertIn("126 standardized log events currently recorded", (root / "trades/index.txt").read_text())

    def test_reported_oil_cashout_closes_only_the_named_paired_lots(self):
        events = parse_trades()
        date = "2026-10-26"
        closures = [
            event for event in events
            if "Explicit close of the specified paired 50U LONG lot" in event["note"]
        ]
        self.assertEqual({(e["sym"], e["units"], e["px"]) for e in closures},
                         {("BRENT", 50, 117.409), ("OIL", 50, 102.71)})
        extended_dates = list(SESSION_DATES)
        expected_pnl = {"BRENT": 8220.067526621078, "OIL": 7912.174859064369}
        with patch.object(model_perf_core, "SESSION_DATES", extended_dates), patch.object(
            model_perf_core, "N_SESS", len(extended_dates)
        ):
            for variant in VARIANTS:
                lots, realized = build_lots(variant, events)
                for ticker, tag, price in (
                    ("BRENT", "paired_manual_brent_50u", 117.409),
                    ("OIL", "paired_ats_oil_mirror_50u", 102.71),
                ):
                    closed = [lot for lot in lots if lot["sym"] == ticker
                              and lot.get("cashout_lot_tag") == tag and not lot["open"]]
                    self.assertEqual(sum(lot["qty"] for lot in closed), 50, (variant, ticker))
                    self.assertTrue(all(lot["close_px"] == price for lot in closed))
                    self.assertEqual(sum(lot["qty"] for lot in lots if lot["sym"] == ticker
                                         and lot["side"] == "long" and lot["open"]), 100)
                older_oil_lot = [lot for lot in lots if lot["sym"] == "OIL" and lot["side"] == "long"
                                 and lot["entry_px"] == 101.0 and lot["open"]]
                self.assertEqual(sum(lot["qty"] for lot in older_oil_lot), 10)
                # Only the $101.11 tagged mirror lot is closed; the $101.00
                # replenishment and separate ATS lot remain distinct.
                paired_pnl = {ticker: sum(row["pnl"] for row in realized
                                          if row["sym"] == ticker and row["date"] == date
                                          and row["qty"] == 50)
                              for ticker in ("BRENT", "OIL")}
                for ticker in expected_pnl:
                    self.assertAlmostEqual(paired_pnl[ticker], expected_pnl[ticker], places=6)
        with ZipFile(Path(__file__).resolve().parents[1] / "trades.zip") as archive:
            for filename in ("BRENT.txt", "OIL.txt", "index.txt"):
                self.assertEqual(archive.read(f"trades/{filename}"),
                                 (Path(__file__).resolve().parents[1] / "trades" / filename).read_bytes())

    def test_manual_short_exits_override_sar_only_for_tagged_oil_target_shorts(self):
        events = parse_trades()
        extended_dates = list(SESSION_DATES)
        expected = {"BRENT": (114.627, 2028.2051282051275), "OIL": (100.74, 1235.294117647059)}
        with patch.object(model_perf_core, "SESSION_DATES", extended_dates), patch.object(
            model_perf_core, "N_SESS", len(extended_dates)
        ):
            for variant in VARIANTS:
                lots, realized = build_lots(variant, events)
                for ticker, (exit_px, pnl) in expected.items():
                    target_shorts = [
                        lot for lot in lots
                        if lot["sym"] == ticker and lot.get("oil_target_short")
                    ]
                    self.assertEqual(len(target_shorts), 1)
                    self.assertFalse(target_shorts[0]["open"])
                    self.assertEqual(target_shorts[0]["close_date"], "2026-10-25")
                    self.assertEqual(target_shorts[0]["close_px"], exit_px)
                    close_event = [
                        row for row in realized
                        if row["sym"] == ticker and row["date"] == "2026-10-25"
                        and row["qty"] == 10
                    ]
                    self.assertEqual(len(close_event), 1)
                    self.assertAlmostEqual(close_event[0]["pnl"], pnl, places=6)

    def test_additional_weekend_oil_buys_are_separate_from_tagged_short_closes(self):
        events = parse_trades()
        buys = {
            event["sym"]: event
            for event in events
            if event["date"] == "2026-10-25" and event["time"] == "20:35"
            and event["tag"] == "LONG" and event["px"] in (114.627, 100.74)
        }
        self.assertEqual(buys["BRENT"]["units"], 35)
        self.assertEqual(buys["OIL"]["units"], 34)
        self.assertTrue(all("counts toward weekly buy supply" in event["note"] for event in buys.values()))
        for ticker, price in (("BRENT", 114.627), ("OIL", 100.74)):
            closes = [
                event for event in events
                if event["sym"] == ticker and event["date"] == "2026-10-25"
                and event["time"] == "20:35" and event["kind"] == "exit"
                and event["px"] == price
            ]
            self.assertEqual(len(closes), 1)
            self.assertEqual(closes[0]["units"], 10)
            self.assertIn("tagged", closes[0]["note"])

    def test_chart_directed_dxy_daily_sleeve_is_integrated_in_each_core_variant(self):
        dxy_lots, dxy_realized = build_dxy_daily_lots()
        self.assertEqual(len(dxy_lots), 36)
        self.assertEqual(sum(lot["qty"] for lot in dxy_lots), 36.0)
        self.assertEqual(dxy_lots[0]["entry_date"], "2026-09-04")
        self.assertEqual(dxy_lots[-1]["entry_date"], "2026-10-26")
        self.assertTrue(all(lot["side"] == "long" for lot in dxy_lots))
        self.assertEqual(dxy_realized, [])
        expected_pnl = sum(10_000 * (DXY_PRICES[-1] / lot["entry_px"] - 1) for lot in dxy_lots)
        self.assertAlmostEqual(expected_pnl, 3413.80, places=2)
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
            ), 360_000.0, places=2)

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
        with (root / "data/tradingview_benchmark_session_marks_20261026.csv").open(newline="", encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))
        by_key = {(row["Ticker"], row["Date"]): row for row in rows}
        self.assertEqual(set(PRICES), {ticker for ticker, _ in by_key} - {"DXY"})
        self.assertEqual(len(PRICES), 31)
        self.assertNotIn("BTC", {ticker for ticker, _ in by_key})
        self.assertNotIn("ETH", {ticker for ticker, _ in by_key})
        self.assertEqual(len([row for row in rows if row["Ticker"] == "DXY"]), 37)
        for ticker, series in PRICES.items():
            self.assertEqual(len(series), 37)
            self.assertEqual(series[-1], float(by_key[(ticker, "2026-10-26")]["Close"]))
        xrh0_carries = [row for row in rows if row["Ticker"] == "XRH0" and row["Mark_Status"].startswith("carry_forward_")]
        self.assertEqual(len(xrh0_carries), 5)
        self.assertEqual({row["Date"] for row in xrh0_carries}, {
            "2026-09-15", "2026-10-07", "2026-10-08", "2026-10-19", "2026-10-22",
        })
        self.assertEqual(float(PRICES["ORCL"][-1]), 126.06)
        self.assertEqual(float(PRICES["BRENT"][-1]), 115.38)
        self.assertEqual(float(PRICES["OIL"][-1]), 101.30)
        self.assertEqual(float(PRICES["LULU"][-1]), 102.91)

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

    def test_oct25_manual_replenishments_are_in_current_oct26_marked_replay(self):
        events = parse_trades()
        expected = [
            ("BRENT", "2026-10-25", 115.792, 10, "17:22", "17:20–17:25"),
            ("OIL", "2026-10-25", 101.74, 10, "17:22", "17:20–17:25"),
            ("BRENT", "2026-10-25", 114.8, 10, "20:00", "approximate time per user"),
            ("OIL", "2026-10-25", 101.0, 10, "20:00", "approximate time per user"),
        ]
        self.assertEqual(SESSION_DATES[-1], "2026-10-26")
        for ticker, date, price, units, time, note_fragment in expected:
            event = next(
                event for event in events
                if event["sym"] == ticker and event["date"] == date and event["px"] == price
            )
            self.assertEqual(event["kind"], "entry")
            self.assertEqual(event["tag"], "LONG")
            self.assertEqual(event["units"], units)
            self.assertEqual(event["time"], time)
            self.assertIn("Manual replenishment entry", event["note"])
            self.assertIn(note_fragment, event["note"])
            self.assertLessEqual(event["date"], SESSION_DATES[-1])
            for variant in VARIANTS:
                lots, _ = build_lots(variant, events)
                matches = [lot for lot in lots if lot["sym"] == ticker and lot["entry_date"] == date
                           and lot["entry_px"] == price]
                self.assertEqual(sum(lot["qty"] for lot in matches), units)
                self.assertTrue(all(lot["open"] for lot in matches))

        report = Path(__file__).resolve().parents[1] / "TradingView Energy and Currency Desk Sidecars.md"
        text = report.read_text(encoding="utf-8")
        self.assertIn("included in the current Oct. 26 replay at supplied marks", text)
        self.assertIn("$115.38/$101.30", text)

        root = Path(__file__).resolve().parents[1]
        with ZipFile(root / "trades.zip") as archive:
            for ticker in {item[0] for item in expected}:
                log_name = "OIL.txt" if ticker == "OIL" else f"{ticker}.txt"
                self.assertEqual(archive.read(f"trades/{log_name}"),
                                 (root / "trades" / log_name).read_bytes())

    def test_oil_trim_shorts_use_explicit_exit_prices_after_replenishment_override_sar(self):
        events = parse_trades()
        expected = {
            "BRENT": (117.0, 114.627, 2028.2051282051275),
            "OIL": (102.0, 100.74, 1235.294117647059),
        }
        for ticker, (entry_price, exit_price, _) in expected.items():
            short_event = next(
                event for event in events
                if event["sym"] == ticker and event["date"] == "2026-10-23"
                and event["tag"] == "SHORT" and event["px"] == entry_price
            )
            self.assertEqual(short_event["units"], 10)
            self.assertIn("Compounded short", short_event["note"])
            self.assertIn("not a verified intraday touch or execution", short_event["note"])
            exit_event = next(
                event for event in events
                if event["sym"] == ticker and event["date"] == "2026-10-25"
                and event["kind"] == "exit" and event["px"] == exit_price
            )
            self.assertEqual(exit_event["time"], "20:35")
            self.assertEqual(exit_event["units"], 10)
            self.assertIn("override SAR auto-close only for this tagged short", exit_event["note"])
            replenishment = next(
                event for event in events
                if event["sym"] == ticker and event["date"] == "2026-10-25"
                and event["kind"] == "entry" and event["px"] in {115.792, 101.74}
            )
            self.assertLess(replenishment["time"], exit_event["time"])

        # At the Oct. 23 cutoff, both short lots remain open. On an extended
        # replay, their 20:35 Oct. 25 explicit closes supersede SAR only for
        # these tagged lots; all four variants use the user-specified prices.
        extended_dates = list(SESSION_DATES)
        with patch.object(model_perf_core, "SESSION_DATES", extended_dates), patch.object(
            model_perf_core, "N_SESS", len(extended_dates)
        ):
            for variant in VARIANTS:
                lots, realized = build_lots(variant, events)
                for ticker, (entry_price, exit_price, pnl) in expected.items():
                    short = next(
                        lot for lot in lots
                        if lot["sym"] == ticker and lot["side"] == "short" and lot["entry_px"] == entry_price
                    )
                    self.assertFalse(short["open"])
                    self.assertEqual(short["close_px"], exit_price)
                    self.assertEqual(short["close_date"], "2026-10-25")
                    closed = [row for row in realized if row["sym"] == ticker and row["date"] == "2026-10-25"]
                    self.assertEqual(len(closed), 1)
                    self.assertAlmostEqual(closed[0]["pnl"], pnl, places=6)

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

    def test_current_report_and_graphs_cover_the_oct26_refresh(self):
        root = Path(__file__).resolve().parents[1]
        report = (root / "Model Performance Comparison.md").read_text(encoding="utf-8")
        self.assertTrue(report.startswith("# THE ONE MODEL\n"))
        self.assertIn("TradingView-only model update — 2026-10-26", report)
        self.assertIn("37 common sessions", report)
        self.assertIn("116` direct-price events", report)
        self.assertIn("marked against the **Monday, October 26, 2026** EOD close", report)
        self.assertIn("102.017", report)
        self.assertIn("No legacy or substitute prices are used", report)
        self.assertIn("preserved Oct. 23 baseline", report)
        self.assertIn("TradingView Energy and Currency Desk Sidecars.md", report)
        self.assertIn("Oil Cost Basis Savings Model.md", report)
        self.assertIn("ATS and Manual Live Position Reconciliation.md", report)
        self.assertIn("actionable_ticker_reconciliation_20261026_v1.csv", report)
        for relpath in (
            "Charts/performance/01-cumulative-pnl-by-session.png",
            "Charts/performance/14-energy-eod-mark-history.png",
            "Charts/performance/19-oil-desk-daily-accumulation.png",
            "Charts/performance/20-strategy-sidecar-comparison.png",
            "Charts/performance/23-dxy-daily-sizing-alternatives.png",
            "Charts/superstructure/the-one-model-split-portfolio.png",
            "Charts/CLN25/Weekend Oil/24-weekend-oil-50u-positions.png",
        ):
            graph = root / relpath
            self.assertTrue(graph.is_file(), relpath)
            self.assertEqual(graph.read_bytes()[:8], b"\x89PNG\r\n\x1a\n")
        explorer = (root / "Model Performance Explorer.html").read_text(encoding="utf-8")
        self.assertIn("TradingView-only core — 2026-10-26", explorer)
        self.assertIn("Oct 26, 2026 close", explorer)
        self.assertIn("$115.38", explorer)
        self.assertIn("$101.30", explorer)
        self.assertIn("hourly intraday charts through Oct 22", explorer)


if __name__ == "__main__":
    unittest.main()
