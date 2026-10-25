"""Audit every Markdown table in the generated model-performance report."""

import csv
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "Model Performance Comparison.md"


def read_csv(path):
    with (ROOT / path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def table_after(text, marker):
    lines = text.splitlines()
    marker_idx = next(i for i, line in enumerate(lines) if marker in line)
    start = next(i for i in range(marker_idx + 1, len(lines)) if lines[i].strip().startswith("|"))
    result = []
    for line in lines[start:]:
        if not line.strip().startswith("|"):
            break
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if not all(set(cell) <= set("-:") for cell in cells):
            result.append(cells)
    return result


def num(value):
    value = value.replace("**", "").replace("`", "").replace("U", "")
    match = re.search(r"[-+]?\$?[\d,]+(?:\.\d+)?", value)
    if not match:
        return 0.0
    return float(match.group(0).replace("$", "").replace(",", "").replace("+", ""))


def ticker_rows(rows, variant):
    return {row["ticker"]: row for row in rows if row["variant"] == variant}


class ModelPerformanceReportAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = REPORT.read_text(encoding="utf-8")
        cls.summary = json.loads((ROOT / "data/model_performance_summary.json").read_text(encoding="utf-8"))
        cls.daily = read_csv("data/model_performance_daily.csv")
        cls.tickers = read_csv("data/model_performance_tickers.csv")

    def test_every_report_table_is_in_the_audit_inventory(self):
        lines = self.report.splitlines()
        table_headers = sum(
            line.strip().startswith("|")
            and index + 1 < len(lines)
            and lines[index + 1].strip().startswith("|")
            and all(set(cell.strip()) <= set("-:") for cell in lines[index + 1].strip().strip("|").split("|"))
            for index, line in enumerate(lines)
        )
        self.assertEqual(table_headers, 10)
        self.assertIn("TradingView-only interim recalculation", self.report)
        self.assertNotIn("Oct. 23 Endpoint Price Corrections Applied", self.report)

    def test_current_lulu_mark_is_tradingview_sourced_and_reconciles(self):
        marks = read_csv("data/tradingview_benchmark_session_marks_20261024.csv")
        lulu = next(row for row in marks if row["Ticker"] == "LULU" and row["Date"] == "2026-10-23")
        self.assertEqual(float(lulu["Close"]), 99.01)
        self.assertEqual(lulu["Mark_Status"], "provided_tradingview_close")
        v3a_lulu = next(row for row in self.tickers if row["variant"] == "V3A" and row["ticker"] == "LULU")
        self.assertEqual(float(v3a_lulu["unrealized_usd"]), 317.84)
        self.assertEqual(float(v3a_lulu["total_usd"]), 317.84)
        self.assertIn("LULU PRICE LIST (TRADINGVIEW).rtf", lulu["Source_File"])
        self.assertIn("BTC and ETH remain excluded pending recalibration", self.report)
        self.assertIn("No legacy or substitute prices are used", self.report)

    def test_four_model_table_components_and_legacy_adjustment_reconcile(self):
        table = table_after(self.report, "## The Four Models")
        self.assertEqual(len(table), 5)
        for row in table[1:]:
            realized, unrealized, total, carry, adjusted = map(num, row[3:8])
            self.assertEqual(round(realized + unrealized, 2), round(total, 2))
            self.assertEqual(round(total + carry, 2), round(adjusted, 2))
        v3a = next(row for row in table[1:] if "Variant 3A" in row[0])
        self.assertEqual(num(v3a[3]) + num(v3a[4]), num(v3a[5]))

    def test_tradingview_marks_and_xrh0_gap_flags_are_explicit(self):
        marks = read_csv("data/tradingview_benchmark_session_marks_20261024.csv")
        core = {row["Ticker"] for row in marks if row["Ticker"] != "DXY"}
        self.assertEqual(len(core), 31)
        self.assertNotIn("BTC", core)
        self.assertNotIn("ETH", core)
        xrh0 = [row for row in marks if row["Ticker"] == "XRH0" and row["Mark_Status"].startswith("carry_forward_")]
        self.assertEqual(len(xrh0), 5)
        self.assertIn("five missing source sessions", self.report)
        self.assertIn("Treat its interim path as provisional", self.report)

    def test_daily_moves_table_matches_all_36_exported_sessions(self):
        table = table_after(self.report, "## Day-by-Day Moves")
        self.assertEqual(len(table) - 1, 36)
        data = {(row["variant"], row["session_date"]): row for row in self.daily}
        for row in table[1:]:
            date = row[0].strip("`")
            for column, variant in zip(range(1, 5), ("V1", "V2", "V3A", "V3B")):
                self.assertAlmostEqual(num(row[column]), float(data[(variant, date)]["daily_delta_usd"]), places=2)

    def test_drawdown_composition_and_divergence_tables_match_generated_data(self):
        risk = table_after(self.report, "## Risk — Drawdown from Running Peak")
        self.assertEqual(len(risk) - 1, 4)
        for row in risk[1:]:
            variant = re.search(r"Variant (1|2|3A|3B)", row[0]).group(1)
            variant = {"1": "V1", "2": "V2"}.get(variant, "V" + variant)
            stats = self.summary["variants"][variant]["stats"]
            self.assertAlmostEqual(num(row[1]), stats["peak"], places=2)
            self.assertEqual(row[2].strip("`"), stats["peak_day"])
            self.assertAlmostEqual(num(row[3]), stats["trough"][1], places=2)
            self.assertEqual(row[4].strip("`"), stats["trough"][0])
            self.assertAlmostEqual(num(row[5]), stats["max_drawdown"], places=2)
            self.assertEqual(row[6].strip("`"), stats["max_drawdown_day"])
            self.assertAlmostEqual(num(row[7]), stats["best_day"][1], places=2)
            self.assertEqual(re.search(r"`(2026-\d{2}-\d{2})`", row[7]).group(1), stats["best_day"][0])
            self.assertAlmostEqual(num(row[8]), stats["worst_day"][1], places=2)
            self.assertEqual(re.search(r"`(2026-\d{2}-\d{2})`", row[8]).group(1), stats["worst_day"][0])

        composition = table_after(self.report, "## Terminal Composition")
        terminal = {(row["variant"], row["session_date"]): row for row in self.daily if row["session_date"] == "2026-10-23"}
        for row in composition[1:]:
            variant = re.search(r"Variant (1|2|3A|3B)", row[0]).group(1)
            variant = {"1": "V1", "2": "V2"}.get(variant, "V" + variant)
            data = terminal[(variant, "2026-10-23")]
            self.assertAlmostEqual(num(row[1]), float(data["realized_cum_usd"]), places=2)
            self.assertAlmostEqual(num(row[2]), float(data["unrealized_usd"]), places=2)
            self.assertAlmostEqual(num(row[1]) + num(row[2]), float(data["total_pnl_usd"]), places=2)

        divergence = table_after(self.report, "### The four divergence tickers")
        for row in divergence[1:]:
            symbol = row[0].strip("`")
            for cell, variant in zip(row[1:], ("V1", "V2", "V3A", "V3B")):
                value = ticker_rows(self.tickers, variant)[symbol]["total_usd"]
                self.assertAlmostEqual(num(cell), float(value), places=2)

    def test_top_and_bottom_contributor_tables_preserve_fractional_units_and_sum(self):
        for marker, reverse in (("### Top contributors (V3A)", True), ("### Bottom contributors (V3A)", False)):
            table = table_after(self.report, marker)
            expected = sorted(ticker_rows(self.tickers, "V3A").items(), key=lambda item: float(item[1]["total_usd"]), reverse=reverse)[:10]
            self.assertEqual(len(table) - 1, 10)
            for row, (symbol, data) in zip(table[1:], expected):
                self.assertEqual(row[0].strip("`"), symbol)
                self.assertAlmostEqual(num(row[1]), float(data["units_deployed"]), places=4)
                self.assertAlmostEqual(num(row[2]), float(data["realized_usd"]), places=2)
                self.assertAlmostEqual(num(row[3]), float(data["unrealized_usd"]), places=2)
                self.assertAlmostEqual(num(row[2]) + num(row[3]), num(row[4]), places=2)
        orcl = next(row for row in self.tickers if row["variant"] == "V3A" and row["ticker"] == "ORCL")
        self.assertEqual(float(orcl["units_deployed"]), 3.5)
        intc = next(row for row in table_after(self.report, "### Top contributors (V3A)")[1:] if row[0].strip("`") == "INTC")
        self.assertEqual(num(intc[2]) + num(intc[3]), num(intc[4]))

    def test_intraday_summary_tables_match_intraday_exports(self):
        intraday = self.summary["intraday"]
        table = table_after(self.report, "### Terminal, divergence sub-book only")
        for row in table[1:]:
            variant = re.search(r"Variant (1|2|3A|3B)", row[0]).group(1)
            variant = {"1": "V1", "2": "V2"}.get(variant, "V" + variant)
            total = intraday["series"][variant]["total"][-1]
            self.assertAlmostEqual(num(row[1]) + num(row[2]), num(row[3]), places=2)
            self.assertAlmostEqual(num(row[3]), total, places=2)

        crossover = table_after(self.report, "### The regime flips")
        for row in crossover[1:]:
            key = row[0].strip("*")
            milestone = intraday["milestones"][key]
            labels = intraday["labels"]
            self.assertEqual(row[1].strip("`").replace(" MST", ""), labels[milestone["first_positive"]])
            self.assertEqual(row[2].strip("`").replace(" MST", ""), labels[milestone["persists_from"]])
            self.assertAlmostEqual(num(row[3]), milestone["peak"], places=2)
            self.assertAlmostEqual(num(row[4]), milestone["trough"], places=2)
            self.assertAlmostEqual(num(row[5]), milestone["terminal"], places=2)

        ticker_table = table_after(self.report, "Intraday per-ticker contribution at the Oct 22 close")
        last_bar = read_csv("data/model_performance_intraday.csv")[-1]
        for row in ticker_table[1:]:
            symbol = row[0].strip("`")
            for cell, variant in zip(row[1:5], ("V1", "V2", "V3A", "V3B")):
                self.assertAlmostEqual(num(cell), float(last_bar[f"{variant}_{symbol}_usd"]), places=2)
            peak_idx = max(range(len(intraday["series"]["V3A"]["per_ticker"][symbol])), key=lambda i: intraday["series"]["V3A"]["per_ticker"][symbol][i])
            self.assertEqual(row[5].strip("`"), intraday["labels"][peak_idx] + " MST")


if __name__ == "__main__":
    unittest.main()
