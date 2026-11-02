import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class OilDeskClosureAluminumTests(unittest.TestCase):
    def test_oil_closure_note_keeps_aluminum_separate(self):
        briefing = (ROOT / 'reports/$200 Oil Foundation & U-Sized Opportunity Capitalization Strategy — Briefing.md').read_text(encoding='utf-8')
        self.assertIn('harassment while working the desk resulted in the closure', briefing)
        self.assertIn('October 29, 2026', briefing)
        self.assertIn('**remains open**', briefing)
        self.assertIn('exact desk-closure date was not supplied', briefing)
        self.assertIn('not independently verified', briefing)

    def test_sec_reports_are_user_reported_and_rewards_not_booked(self):
        briefing = (ROOT / 'reports/$200 Oil Foundation & U-Sized Opportunity Capitalization Strategy — Briefing.md').read_text(encoding='utf-8')
        self.assertIn('numerous reports were made to the SEC via AI last week', briefing)
        self.assertIn('October 26–November 1, 2026', briefing)
        self.assertIn('expects rewards if the tips are verified', briefing)
        self.assertIn('not independently verified', briefing)
        self.assertIn('No reward amount or receivable is recorded', briefing)

    def test_aluminum_status_does_not_claim_new_fill_or_mark(self):
        aluminum = (ROOT / 'reports/ALIUSD User-Directed LONG Position.md').read_text(encoding='utf-8')
        self.assertIn('Aluminum (ALIUSD) **remains open**', aluminum)
        self.assertIn('not an independently verified current brokerage position', aluminum)
        self.assertIn('No new mark, execution, or change to quantity or basis is implied', aluminum)
        self.assertIn('15,546,506', aluminum)
        self.assertIn('$2,999.99', aluminum)


if __name__ == '__main__':
    unittest.main()
