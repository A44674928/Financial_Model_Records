import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOTE = (
    "The user reports that Harshal’s Oil Desk began to exit all positions on "
    "**October 29, 2026**, with the goal of exiting cleanly before the end of that week."
)


class OilExitTimelineTests(unittest.TestCase):
    def test_reports_distinguish_start_and_goal_from_verified_fills(self):
        for name in (
            "ATS and Manual Live Position Reconciliation.md",
            "reports/$200 Oil Foundation & U-Sized Opportunity Capitalization Strategy — Briefing.md",
        ):
            text = (ROOT / name).read_text(encoding="utf-8")
            self.assertIn(NOTE, text, name)
            self.assertIn("not a verified fill date or confirmation", text, name)

    def test_generated_reconciliation_retains_timeline(self):
        spec = importlib.util.spec_from_file_location(
            "ats_manual_reconciliation", ROOT / "scripts/build_ats_manual_reconciliation.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as temp:
            module.REPORT_PATH = Path(temp) / "report.md"
            module.build_report()
            report = module.REPORT_PATH.read_text(encoding="utf-8")
        self.assertIn(NOTE, report)
        self.assertIn("not a verified fill date or confirmation", report)


if __name__ == "__main__":
    unittest.main()
