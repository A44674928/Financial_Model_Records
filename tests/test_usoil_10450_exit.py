import csv
import hashlib
import io
import sys
import unittest
import zipfile
from decimal import Decimal as D, ROUND_HALF_UP
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import build_usoil_10450_exit as builder


def read(path):
    with (ROOT / path).open(encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f))


class USOILExitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = read('data/usoil_sold_10450_20261030_v1.csv')
        cls.by_id = {r['record_id']: r for r in cls.rows}

    def test_register_is_reproducible_and_has_one_exit(self):
        self.assertEqual(len(self.rows), 23)
        self.assertEqual(len(self.by_id), 23)
        out = io.StringIO(newline='')
        w = csv.DictWriter(out, fieldnames=builder.FIELDS)
        w.writeheader(); w.writerows(builder.build_rows())
        self.assertEqual(out.getvalue().encode(), (ROOT / 'data/usoil_sold_10450_20261030_v1.csv').read_bytes())
        for r in self.rows:
            self.assertEqual(r['sale_date'], '2026-10-30')
            self.assertEqual(D(r['sale_price_usd']), D('104.50'))
            self.assertEqual(r['ticker'], 'USOIL (OIL)')
            self.assertIn('not independently verified', r['execution_verification_status'])

    def test_all_lot_math_and_per_book_totals(self):
        totals = {}
        for r in self.rows:
            q, entry, sale = map(D, (r['quantity'], r['entry_price_usd'], r['sale_price_usd']))
            expected = (q * D(10000) * (sale / entry - 1) if r['quantity_unit'].startswith('U (') else q * (sale - entry))
            self.assertEqual(D(r['price_only_realized_pnl_usd']), expected.quantize(D('.01'), rounding=ROUND_HALF_UP), r['record_id'])
            if r['book_subtotal_treatment'] == builder.PRIMARY:
                totals[r['book_or_model']] = totals.get(r['book_or_model'], D(0)) + D(r['price_only_realized_pnl_usd'])
        self.assertEqual(list(totals.values()), list(map(D, ['3198480387.76','1891607645.29','17326.73','48210.64','28339.45','33163.92'])))
        combined = D(self.by_id['USOIL10450-FOUNDATION']['price_only_realized_pnl_usd'])
        components = sum(D(self.by_id[i]['price_only_realized_pnl_usd']) for i in ('USOIL10450-POOL', 'USOIL10450-SUPPLEMENTAL'))
        self.assertLessEqual(abs(combined-components), D('.02'))

    def test_private_fund_evidence_and_unknown_basis(self):
        r = self.by_id['USOIL10450-PF']
        self.assertEqual(r['supersedes_record_id'], 'PRIVATE_TV_USOIL_CLOSE_20261029')
        self.assertEqual((r['superseded_close_price_evidence_usd'], r['superseded_close_pnl_evidence_usd']), ('102.14', '1779605629.28'))
        self.assertEqual((r['gross_basis_usd'], r['model_implied_gross_proceeds_usd']), ('', ''))
        self.assertEqual(r['price_only_realized_pnl_usd'], '3198480387.76')

    def test_ledger_closes_exactly_100u_and_does_not_close_previously_closed_lots(self):
        core = [r for r in self.rows if r['book_or_model'] == 'Core paper-trade ledger replay']
        self.assertEqual(len(core), 10)
        self.assertEqual(sum(D(r['quantity']) for r in core), 100)
        self.assertNotIn('101.11', {r['entry_price_usd'] for r in core})
        events = [line for line in (ROOT / 'trades/OIL.txt').read_text().splitlines() if line.startswith('2026-10-30')]
        self.assertEqual(len(events), 10)
        self.assertTrue(all('~$104.50' in line and 'chronology placeholder' in line for line in events))
        with zipfile.ZipFile(ROOT / 'trades.zip') as z:
            for name in z.namelist():
                if not name.endswith('/'):
                    self.assertEqual(z.read(name), (ROOT / name).read_bytes(), name)

    def test_audit_closes_real_lots_only(self):
        audit = read('data/oil_position_audit_sheet_v1.csv')
        closed = [r for r in audit if r['ticker'] in ('OIL','USOIL') and r['exit_price_usd'] == '104.50']
        self.assertEqual(len(closed), 14)
        scenario_types = {'ATS_SCENARIO_RESIDUAL_LONG','REINSTATED_NULLIFIED_SHORT_LIFECYCLE','LEGACY_BASELINE_SHORT_EVENT','REPORTED_LIQUIDATION_REFERENCE'}
        for r in audit:
            if r['ticker'] in ('OIL','USOIL') and (r['row_type'] in scenario_types or (r['row_type'] == 'UNDER_DURESS_RESTORED_LONG' and r['position_id'] != 'PF-USOIL-CLOSE-20261029')):
                self.assertNotEqual(r['exit_price_usd'], '104.50')
        for file, sha in [('data/under_duress_oil_restored_positions_v1.csv','a539c01ca3171857c5d899a06265f8d16a416419be632ad0ecaefb1d3e6f52d8'),('data/under_duress_oil_void_events_v1.csv','4a4175102c4fe73ac2d8326a92b0de1b109a800c366cc7a9731fe77b2327ad96')]:
            self.assertEqual(hashlib.sha256((ROOT / file).read_bytes()).hexdigest(), sha)

    def test_sheets_and_rollup(self):
        sheet = read('data/november_2026_oil_clean_sheet_v1.csv')
        usoil = next(r for r in sheet if r['ticker'].startswith('USOIL'))
        brent = next(r for r in sheet if r['ticker'].startswith('BRENT'))
        self.assertEqual(usoil['user_directed_exit_price_usd'], '104.50')
        self.assertEqual(usoil['oil_v2_exit_price_only_realized_pnl_usd_per_variant'], '28339.45')
        self.assertEqual(brent['user_directed_exit_price_usd'], '119.00')
        balance = read('data/november_2026_plus_plus_experiment_balance_sheet_v1.csv')
        def find(prefix): return next(r for r in balance if r['balance_sheet_line'].startswith(prefix))
        self.assertEqual(find('USOIL close order')['amount_usd'], '3198480387.76')
        self.assertEqual(find('USOIL close order')['source_reported_pnl_usd'], '1779605629.28')
        self.assertEqual(find('Total new realized-PnL additions')['amount_usd'], '5868156545.76')
        self.assertEqual(find('Profit-only cash carry-forward subtotal')['amount_usd'], '8264726233.71')
        self.assertEqual(find('Unreconciled simple sum')['amount_usd'], '9261732225.05')
        log = [r for r in read('data/account_change_log_2026-10-30_v1.csv') if r['ticker'] == 'USOIL']
        self.assertEqual(len(log), 7)
        self.assertTrue(all(r['close_or_offer_value'] == '104.50' for r in log))

    def test_cross_book_overlap_and_variant_boundaries(self):
        for id in ('USOIL10450-WINNER','USOIL10450-CORE-50U-residual','USOIL10450-CORE-manual-1722','USOIL10450-CORE-manual-2000','USOIL10450-ATS-fixed-50'):
            self.assertNotEqual(self.by_id[id]['overlap_flag'], 'NONE')
        text = (ROOT / 'reports/USOIL Full Exit at $104.50 — 2026-10-30.md').read_text()
        self.assertIn('do not sum across books', text)
        self.assertIn('not a verified fill', text)
        self.assertIn('sensitivities', text.lower())

if __name__ == '__main__':
    unittest.main()
