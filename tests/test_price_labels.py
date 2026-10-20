"""Snapshot-data, non-destructive image, and report consistency checks."""

import csv
import importlib.util
import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageChops, ImageColor, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("labels", ROOT / "scripts/label_current_prices.py")
labels = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(labels)

# Manually cross-checked against the numeric labels and badges in all nine JPEGs.
EXPECTED = {
    "BRENT": ("111.025", "LONG", "x"),
    "CAT": ("729.58", "LONG", "x"),
    "INTC": ("94.865", "LONG", "x"),
    "LMT": ("548.23", "LONG", "x"),
    "OIL": ("98.74", "LONG", "x"),
    "ORCL": ("128.23", "LONG", "x"),
    "PLTR": ("194.15", "SHORT", "y"),
    "SPCX": ("147.96", "SHORT", "y"),
    "TSLA": ("368.06", "SHORT", "y"),
}


class PriceLabelsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.points = labels.load_points()

    def test_exact_displayed_prices_and_source_badges(self):
        actual = {
            p["ticker"]: (p["price_usd"], p["chart_bias"], p["marker"])
            for p in self.points
        }
        self.assertEqual(actual, EXPECTED)
        self.assertEqual(len(self.points), 9)
        for point in self.points:
            self.assertTrue(point["captured_local"].startswith("2026-10-19 "))

    def test_one_point_for_each_original_chart(self):
        sources = {ROOT / p["source_image"] for p in self.points}
        self.assertEqual(sources, set((ROOT / "Charts").glob("*/*.jpeg")))
        self.assertEqual(len({labels.output_path(p) for p in self.points}), 9)

    def test_symbol_key_including_hazard(self):
        self.assertEqual(
            {symbol: signal["label"] for symbol, signal in labels.SIGNALS.items()},
            {"x": "Long", "y": "Short", "z": "Hazard"},
        )
        for symbol, signal in labels.SIGNALS.items():
            with self.subTest(symbol=symbol):
                image = Image.new("RGB", (400, 400), labels.BACKGROUND)
                labels.draw_marker(ImageDraw.Draw(image), (180, 220), symbol)
                colors = {color for _, color in image.getcolors(image.width * image.height)}
                self.assertIn(ImageColor.getrgb(signal["color"]), colors)

    def test_annotated_images_preserve_source_outside_marker(self):
        for point in self.points:
            with self.subTest(ticker=point["ticker"]):
                with Image.open(ROOT / point["source_image"]) as image:
                    source = image.convert("RGB")
                with Image.open(labels.output_path(point)) as image:
                    self.assertEqual(image.format, "PNG")
                    self.assertEqual(image.size, (source.width, source.height + labels.FOOTER_HEIGHT))
                    top = image.crop((0, 0, source.width, source.height)).convert("RGB")
                difference = ImageChops.difference(top, source).getbbox()
                self.assertIsNotNone(difference)
                x, y = int(point["point_x_px"]), int(point["point_y_px"])
                allowed = (
                    x - labels.POINT_RADIUS - 1,
                    y + labels.BADGE_OFFSET[1] - labels.BADGE_RADIUS - 1,
                    x + labels.BADGE_OFFSET[0] + labels.BADGE_RADIUS + 1,
                    y + labels.POINT_RADIUS + 1,
                )
                self.assertGreaterEqual(difference[0], allowed[0])
                self.assertGreaterEqual(difference[1], allowed[1])
                self.assertLessEqual(difference[2], allowed[2])
                self.assertLessEqual(difference[3], allowed[3])
                color = ImageColor.getrgb(labels.SIGNALS[point["marker"]]["color"])
                patch = top.crop(allowed)
                colors = {pixel for _, pixel in patch.getcolors(patch.width * patch.height)}
                self.assertIn(color, colors)

    def test_report_table_matches_csv_and_links(self):
        report = labels.REPORT_PATH.read_text(encoding="utf-8")
        table = report.split(labels.BEGIN_TABLE, 1)[1].split(labels.END_TABLE, 1)[0].strip()
        self.assertEqual(table, labels.markdown_table(self.points))
        for point in self.points:
            self.assertTrue(labels.output_path(point).is_file())
        self.assertIn("not a live market quote", report)
        self.assertIn("**z — Hazard**", report)
        self.assertNotIn("z — Warning", report)

    def test_wrong_current_signal_is_not_silently_accepted(self):
        rows = [dict(p) for p in self.points]
        rows[0]["marker"] = "z"  # An old warning is not evidence of a current one.
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "points.csv"
            with path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
                writer.writeheader()
                writer.writerows(rows)
            with self.assertRaisesRegex(ValueError, "must match the source badge"):
                labels.load_points(path)


if __name__ == "__main__":
    unittest.main()
