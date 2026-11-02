#!/usr/bin/env python3
"""Build the October 30 user-directed USOIL exit register, without touching scenarios."""
import csv
from decimal import Decimal as D, ROUND_HALF_UP
from pathlib import Path
from build_brent_119_exit import FIELDS, PRIMARY, COMPONENT

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'data/usoil_sold_10450_20261030_v1.csv'
PRICE = D('104.50')
POLICY = 'USER_DIRECTED_USOIL_EXIT_SCOPED_EXCEPTION_20261030'

def money(x):
    return str(x.quantize(D('.01'), rounding=ROUND_HALF_UP))

def lot(id, book, name, date, time, entry, qty, kind, source, overlap='', notes='', treatment=PRIMARY, supersedes='', evidence_price='', evidence_pnl=''):
    e, q = D(entry), D(str(qty))
    if kind == 'U':
        unit, convention = 'U ($10,000 model notional)', 'Fixed entry notional; 1U = $10,000'
        basis, pnl = q * D(10000), q * D(10000) * (PRICE / e - 1)
        formula = 'units x $10,000 x (sale_price / entry_price - 1)'
    else:
        unit = {'platform':'platform-reported units','modeled':'modeled quantity equivalent','conversion':'price-derived calculated units'}[kind]
        convention = {'platform':'Platform-reported units; contract multiplier and cash basis not inferred','modeled':'Allocation dollars / entry price; not verified contracts or barrels','conversion':'Clean-sheet notional / entry price; not a verified fill or contract quantity'}[kind]
        basis, pnl = q * e, q * (PRICE - e)
        formula = 'quantity x (sale_price - entry_price)'
    return dict(zip(FIELDS,[id,book, name,'USOIL (OIL)','LONG',name,date,time,str(e),str(q),unit,convention,
        '' if kind == 'platform' else money(basis), '2026-10-30',str(PRICE),
        '' if kind == 'platform' else money(basis+pnl),money(pnl),formula,
        'Prior source state retained; see source and notes',supersedes,evidence_price,evidence_pnl,
        'CLOSED — SOLD AT $104.50 on 2026-10-30', overlap or 'NONE',treatment,
        'Within-book primary rows only; do not sum books or alternative variants',
        'User-reported sale; not independently verified or audited',POLICY,source,notes]))

def build_rows():
    rows=[]
    def add(*a,**kw): rows.append(lot(*a,**kw))
    pf='Private Fund / TradingView Paper Trading'; foundation='ATS locked $200 LONG foundation / $20B Units Experiment pool'; winner='THE WINNING MODEL — 50U transferred from the oil foundation'; core='Core paper-trade ledger replay'; v2='Oil portfolio v2 / November 2026 Oil Clean Sheet'; ats='ATS and Manual Live Position Reconciliation'
    add('USOIL10450-PF',pf,'PF-USOIL-CLOSE-20261029','earlier entry; date unknown','not supplied','99.18','601218118','platform','Archive/November_2026_Experiment_Oil_Closes_2026-10-29/IMG_1217.png',notes='Earlier void lifted and superseded; screenshot close and PnL are evidence only.',supersedes='PRIVATE_TV_USOIL_CLOSE_20261029',evidence_price='102.14',evidence_pnl='1779605629.28')
    src='Units Experiment Pool Allocation.md; data/units_experiment_oil_foundation_lots_20261027.csv'
    add('USOIL10450-FOUNDATION',foundation,'Combined foundation','not supplied','not supplied','95.26185814707322344409305211','204760619.11636445','modeled',src,overlap='Combination of the two component legs, not an additional position',notes='Supersedes earlier ATS price bands; component legs excluded from subtotal.')
    add('USOIL10450-POOL',foundation,'Original pool residual','2026-09-22 (model assumption)','not supplied','89.89','105755668.62131494','modeled',src,overlap='Component of combined foundation',treatment=COMPONENT)
    add('USOIL10450-SUPPLEMENTAL',foundation,'Supplemental order remainder','not supplied','not supplied','101.00','99004950.49504950','modeled',src,overlap='Component of combined foundation; 50U transferred to Winner excluded',treatment=COMPONENT)
    add('USOIL10450-WINNER',winner,'50U transfer','2026-10-26 (assumed)','not supplied','101.00','4950.49504950','modeled',src,overlap='Carved out of supplemental leg; corresponds to ATS/manual 50U source lot; do not sum books',notes='Capital reallocation, not a new performance reward or separate additional fill.')
    core_lots=[('20260910','2026-09-10','06:30','97.32',1),('20260922','2026-09-22','06:30','90.20',1),('20260924','2026-09-24','06:30','93.74',1),('20260929','2026-09-29','06:30','89.30',1),('20261008','2026-10-08','06:30','90.60',1),('20261019','2026-10-19','06:30','98.74',1),('50U-residual','2026-10-19','06:30','99.04',40),('manual-1722','2026-10-25','17:22','101.74',10),('manual-2000','2026-10-25','20:00','101.00',10),('approved-2035','2026-10-25','20:35','100.74',34)]
    for id,date,time,entry,qty in core_lots:
        overlap = 'Same source lot as Oil v2 50U, there untrimmed' if id=='50U-residual' else ('Same manual replenishment in ATS/manual; do not add books' if id.startswith('manual') else ('Core replay retains 34U; ATS/manual residual is scenario-dependent and excluded' if id=='approved-2035' else ''))
        add('USOIL10450-CORE-'+id,core,id,date,time,entry,qty,'U','trades/OIL.txt',overlap=overlap)
    add('USOIL10450-V2-50U',v2,'Oil v2 50U large lot','2026-10-19','06:30','99.04',50,'U','data/november_2026_oil_clean_sheet_v1.csv',overlap='Same source lot as core 40U residual; Oil v2 cutoff retains 50U',notes='Per variant, alternatives are not additive.')
    for n,price,qty in [('1','103','388.3495145631067961165048544'),('2','104','384.6153846153846153846153846')]:
        add('USOIL10450-V2-T'+n,v2,'Converted tranche '+n,'clean-sheet conversion; date unknown','not supplied',price,qty,'conversion','data/november_2026_oil_clean_sheet_v1.csv',notes='$40,000 conversion notional, per variant; conversion is not a verified execution.')
    for name,date,time,price,qty in [('fixed-50','2026-10-26','not supplied','101.00',50),('order-10','2026-10-26 assumed','not supplied','100.96',10),('reported-17','2026-10-26 assumed','not supplied','100.85',17),('manual-1722','2026-10-25','17:22','101.74',10),('manual-2000','2026-10-25','20:00','101.00',10)]:
        overlap='Same manual replenishment as core' if name.startswith('manual') else ('Source lot reallocated to Winner; do not add books' if name=='fixed-50' else '')
        add('USOIL10450-ATS-'+name,ats,name,date,time,price,qty,'U','data/ats_manual_live_positions_v1.csv',overlap=overlap,notes='Real non-scenario lot only; user-reported/model input, not verified.')
    return rows

def main():
    rows=build_rows(); assert len(rows)==23 and len({r['record_id'] for r in rows})==23
    assert sum(D(r['quantity']) for r in rows if r['book_or_model']=='Core paper-trade ledger replay')==100
    x={r['record_id']:r for r in rows}
    assert abs(D(x['USOIL10450-FOUNDATION']['price_only_realized_pnl_usd'])-sum(D(x[i]['price_only_realized_pnl_usd']) for i in ['USOIL10450-POOL','USOIL10450-SUPPLEMENTAL']))<=D('.02')
    with OUT.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=FIELDS); w.writeheader(); w.writerows(rows)
    for b in dict.fromkeys(r['book_or_model'] for r in rows):
        print(b, money(sum(D(r['price_only_realized_pnl_usd']) for r in rows if r['book_or_model']==b and r['book_subtotal_treatment']==PRIMARY)))
if __name__=='__main__': main()
