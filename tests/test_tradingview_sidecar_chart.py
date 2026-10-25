"""Coverage for the DXY daily-sizing options graph in the sidecar report."""

import csv
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_tradingview_sidecars as sidecars  # noqa: E402


class TradingViewSidecarChartTests(unittest.TestCase):
    def test_dxy_sizing_options_are_graphed_and_labeled(self):
        sidecars.main()
        self.assertTrue(sidecars.DXY_GRAPH.is_file())
        self.assertEqual(sidecars.DXY_GRAPH.read_bytes()[:8], b"\x89PNG\r\n\x1a\n")

        with sidecars.DXY_CSV.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), 105)
        self.assertEqual({row["unit_size_label"] for row in rows}, {"0.05U", "1U", "10U"})

        report = sidecars.REPORT.read_text(encoding="utf-8")
        self.assertIn("23-dxy-daily-sizing-alternatives.png", report)
        self.assertIn("0.05U, 1U, and 10U", report)
        self.assertIn("1U/DAY schedule is included in every core model", report)
        self.assertIn("THE ONE MODEL adds the 10U/DAY schedule on top", report)
        self.assertIn("11U/DAY total", report)
        self.assertIn("0.05U remains an alternative", report)
        self.assertEqual(sidecars.DXY_SIZE_COLORS.keys(), {"0.05U", "1U", "10U"})
        generator = (ROOT / "scripts/build_tradingview_sidecars.py").read_text(encoding="utf-8")
        self.assertIn('"10U": "THE ONE MODEL ADD-ON"', generator)


if __name__ == "__main__":
    unittest.main()
