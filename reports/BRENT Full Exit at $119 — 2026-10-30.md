# BRENT Full Exit at $119 — 2026-10-30

> **Later USOIL update:** The USOIL void referred to in this historical BRENT report was subsequently lifted and superseded by the separate [USOIL $104.50 exit](USOIL%20Full%20Exit%20at%20%24104.50%20%E2%80%94%202026-10-30.md). The BRENT-only statements below describe the state at the time of that instruction.

> **User-directed exit record.** The user directs that **all BRENT was sold at $119**. This report books that exit across the repository's real BRENT positions, per book, at a single sale price of **$119.00** on **2026-10-30** (time not supplied). It **supersedes** the previously voided 2026-10-29 Private Fund BRENT close at $115.777. Price-only realized PnL is computed from each lot's own basis, before costs. The sale price is user-reported; it is **not** an independently verified brokerage fill, execution, or audited account record. Source books and historical records are preserved, not rewritten.

**ATS decision note:** The user reports that the ATS asked for a price check at $119 and then made the decision to sell on its own. This describes the reported decision process, not independently verified evidence of a price check, order, or execution; no additional timing or price source is inferred. The user-directed bookkeeping and per-book treatment remain unchanged.

**Machine-readable register:** [`data/brent_sold_119_20261030_v1.csv`](../data/brent_sold_119_20261030_v1.csv) — 22 rows, one per lot or documented component leg.
**Builder:** [`scripts/build_brent_119_exit.py`](../scripts/build_brent_119_exit.py) · **Test:** [`tests/test_brent_119_exit.py`](../tests/test_brent_119_exit.py)

## Scope

Per the user's direction, this exit applies to **real positions only**:

| Included | Excluded (left untouched) |
|---|---|
| Private Fund / TradingView Paper Trading lot | Under-Duress Oil Sale Void Replay overlay |
| ATS locked $200 LONG foundation / $20B Units Experiment pool | 10U / 20U / 30U / 40U ATS exit sensitivities |
| THE WINNING MODEL 50U transfer carved out of the foundation | Legacy baseline superseded events (Oct. 23 10U trim and 10U short) |
| Core paper-trade ledger replay (`trades/BRENT.txt`) | Lots already closed before this exit |
| Oil portfolio v2 mark-forward / November 2026 Oil Clean Sheet | USOIL and all non-BRENT tickers |
| ATS and Manual Live Position Reconciliation real lots | The 111U maximum-ATS-scenario campaign total (scenario-dependent) |

The ATS sensitivity rows remain **alternative scenarios** and are not additive; they are deliberately not converted into sold positions. The Under-Duress overlay remains preserved as its own earlier baseline.

## Supersession of the voided October 29 close

The 2026-10-29 Private Fund BRENT close was previously **nullified and voided** per user instruction, leaving 538,566,907 units open at $114.043 with no mark and **$0.00** booked. The user now directs that the real exit price is **$119**.

| Item | Prior treatment (2026-10-29) | This record (2026-10-30) |
|---|---|---|
| Close status | Nullified and voided; long retained open | **Lifted** — the exit stands |
| Exit price | Screenshot $115.777, not used as a mark | **$119.00**, user-directed |
| Realized PnL booked | $0.00 | **$2,669,676,158.00** (price-only) |
| Screenshot evidence | Preserved as voided-source detail | Preserved as **superseded** source detail |

The screenshot close price $115.777 and displayed PnL $933,875,016.74 are **preserved unchanged** in `superseded_close_price_evidence_usd` and `superseded_close_pnl_evidence_usd`. They remain source evidence only and are **not** used as marks or booked as PnL. The original screenshot at [`Archive/November_2026_Experiment_Oil_Closes_2026-10-29/IMG_1218.png`](../Archive/November_2026_Experiment_Oil_Closes_2026-10-29/IMG_1218.png) is untouched. The USOIL close from the same screenshot pair remains **voided** — this instruction covered BRENT only.

## Per-book results

Books are kept separate. Their quantity conventions are **not verified as interchangeable**, so no cross-book grand total is asserted.

| Book | Quantity | Unit convention | Basis | Gross basis | Model-implied proceeds | Price-only realized PnL |
|---|---:|---|---|---:|---:|---:|
| Private Fund / TradingView Paper Trading | 538,566,907 | platform-reported units | $114.043 | not inferred | not inferred | **$2,669,676,158.00** |
| ATS locked $200 LONG foundation | 179,865,012.22971259 | modeled quantity equivalent | $108.44731174 blended | $19,505,877,052.37 | $21,403,936,455.34 | **$1,898,059,402.97** |
| THE WINNING MODEL 50U transfer | 4,347.82608696 | modeled quantity equivalent | $115.00 | $500,000.00 | $517,391.30 | **$17,391.30** |
| Core paper-trade ledger replay | 100 U | U ($10,000 notional) | per lot | $1,000,000.00 | $1,052,827.16 | **$52,827.16** |
| Oil v2 / November Clean Sheet (per variant) | 50 U + 680.863392727800 | U and price-derived units | per lot | $580,000.00 | $615,076.52 | **$35,076.52** |
| ATS and Manual Live Position Reconciliation | 96 U | U ($10,000 notional) | per lot | $960,000.00 | $992,985.41 | **$32,985.41** |

The Private Fund row carries **no gross basis or proceeds** because that source book deliberately infers no cash basis, market value, or contract multiplier from platform-reported units. Its price-only PnL is still well defined as `quantity × (sale − entry)` and needs no basis.

### Formulas

- **U-denominated model lots:** `units × $10,000 × (119 ÷ entry − 1)` — the repository's standard long PnL formula, where 1U is a fixed $10,000 entry notional, not a fixed barrel count.
- **Quantity-denominated lots:** `quantity × (119 − entry)`.

Both are verified against existing repository values before use.

**Rounding convention.** Each lot's realized PnL is booked at whole cents, and every book subtotal is the sum of those rounded per-lot figures — the normal ledger treatment. Summing unrounded values instead differs by a few cents ($52,827.13 rather than $52,827.16 for the nine core-ledger lots; $35,076.53 rather than $35,076.52 for the Oil v2 per-variant line). This matches the convention already documented in [`Core Portfolio Asset Breakdown.md`](../Core%20Portfolio%20Asset%20Breakdown.md): per-lot values are rounded to cents, so their displayed sum may differ from an unrounded total by a few cents. Neither figure is an error; the rounded per-lot sum is authoritative here.

### ATS locked foundation — component legs

The combined foundation row is the book's representative total. Its two component legs are recorded for audit continuity and are **excluded from the subtotal** to avoid double counting; they tie to the combined row within $0.01.

| Component leg | Quantity | Basis | Price-only PnL |
|---|---:|---:|---:|
| $20B pool residual allocation | 92,912,838.31666911 | $102.315 | $1,550,250,707.31 |
| Restored supplemental order remainder | 86,952,173.91304348 | $115.00 | $347,808,695.65 |
| **Combined foundation** | **179,865,012.22971259** | **$108.44731174** | **$1,898,059,402.97** |

This single $119 price **supersedes** the earlier user-reported ATS sale-price bands of $114.670–$117.345 for this book. The prior $2.4B conservative endpoint and the $2,396,569,687.95–$3,266,845,310.16 price-envelope estimates remain preserved as earlier references and are not restated.

### Core paper-trade ledger — 100U across nine lots

| Lot | Entry date | Units | Entry price | Price-only PnL |
|---|---|---:|---:|---:|
| 1U core entry | 2026-09-23 | 1 | $102.50 | $1,609.76 |
| 1U core entry | 2026-10-02 | 1 | $107.00 | $1,121.50 |
| 1U core entry | 2026-10-04 | 1 | $106.446 | $1,179.38 |
| 1U core entry | 2026-10-09 | 1 | $106.50 | $1,173.71 |
| 1U core entry | 2026-10-19 | 1 | $111.025 | $718.31 |
| Residual of the tagged 50U lot after the 10U trim | 2026-10-19 | 40 | $111.412 | $27,243.03 |
| MANUAL LIVE TEST replenishment | 2026-10-25 17:22 MST | 10 | $115.792 | $2,770.49 |
| MANUAL LIVE TEST replenishment | 2026-10-25 20:00 MST | 10 | $114.80 | $3,658.54 |
| MANUALLY APPROVED SHORT CLOSURE excess left LONG | 2026-10-25 20:35 MST | 35 | $114.627 | $13,352.44 |
| **Total** | — | **100** | — | **$52,827.16** |

This 100U ties to the open-long exposure documented in [`Core Cost Basis After Closure Credits.md`](../Core%20Cost%20Basis%20After%20Closure%20Credits.md). Lots already closed before this exit are **not** sold again: the Oct. 23 10U trim at $117.00, the Oct. 23 10U short covered at $114.627, and the paired 50U manual lot sold at $117.409 on Oct. 26.

### Oil v2 / November 2026 Oil Clean Sheet — per variant

| Line | Quantity | Basis | Price-only PnL |
|---|---:|---:|---:|
| Remaining large U | 50 U | $111.412 | $34,053.78 |
| Converted tranche 1 ($40,000 notional) | 341.8803418803418803418803419 | $117 | $683.76 |
| Converted tranche 2 ($40,000 notional) | 338.9830508474576271186440678 | $118 | $338.98 |
| **Per-variant total** | — | — | **$35,076.52** |

The four Oil v2 variants (V1/V2/V3A/V3B) are **alternatives**, not additive holdings; this total applies **per variant**. Oil v2 retains the full untrimmed 50U because its trade-event cutoff is 2026-10-19, where the core ledger retains 40U after the post-cutoff trim. The Small Unit conversion was a clean-sheet calculation, not an execution; the $119 exit is now applied to it.

### ATS and Manual Live Position Reconciliation — 96U of real lots

| Lot | Entry date | Units | Entry price | Price-only PnL |
|---|---|---:|---:|---:|
| ATS modeled fixed-price long | 2026-10-26 | 50 | $115.00 | $17,391.30 |
| MANUALLY APPROVED ATS ORDER | 2026-10-26 | 10 | $115.025 | $3,455.77 |
| User-reported long; category unspecified | 2026-10-26 | 16 | $114.900 | $5,709.31 |
| MANUAL LIVE TEST replenishment | 2026-10-25 | 10 | $115.792 | $2,770.49 |
| MANUAL LIVE TEST replenishment | 2026-10-25 | 10 | $114.800 | $3,658.54 |
| **Total** | — | **96** | — | **$32,985.41** |

The 50U manual lot at $115.51 is **excluded** — it was already sold at $117.409 on 2026-10-26.

## Cross-book overlaps — do not sum

Three lots appear in more than one book. Each counts in its own book's subtotal, but the books must never be added together.

| Lot | Books | Note |
|---|---|---|
| 10U @ $115.792 (2026-10-25) | Core ledger + ATS/manual | Same manual replenishment lot |
| 10U @ $114.800 (2026-10-25) | Core ledger + ATS/manual | Same manual replenishment lot |
| 50U @ $111.412 (2026-10-19) | Core ledger (40U) + Oil v2 (50U) | Same source lot; Oil v2 is untrimmed due to its Oct. 19 cutoff |
| 4,347.82608696 units @ $115.00 | Winner transfer, carved out of the supplemental leg | Already excluded from that leg — not a double count |

## Books updated by this record

| Book | Change |
|---|---|
| [`trades/BRENT.txt`](../trades/BRENT.txt) | Nine lot-specific exit entries appended at $119 |
| [`data/brent_sold_119_20261030_v1.csv`](../data/brent_sold_119_20261030_v1.csv) | New 22-row authoritative register |
| [`data/account_change_log_2026-10-30_v1.csv`](../data/account_change_log_2026-10-30_v1.csv) | New dated change log |
| [`Harshal's Private Fund — November 2026++ Experiment.md`](Harshal's%20Private%20Fund%20%E2%80%94%20November%202026%2B%2B%20Experiment.md) | BRENT void lifted; PnL booked; carry-forward updated |
| [`data/november_2026_plus_plus_experiment_balance_sheet_v1.csv`](../data/november_2026_plus_plus_experiment_balance_sheet_v1.csv) | BRENT rows updated; USOIL void untouched |
| [`November 2026 Oil Clean Sheet.md`](November%202026%20Oil%20Clean%20Sheet.md) | BRENT marked SOLD at $119 |
| [`data/november_2026_oil_clean_sheet_v1.csv`](../data/november_2026_oil_clean_sheet_v1.csv) | BRENT exit columns populated |
| [`data/oil_position_audit_sheet_v1.csv`](../data/oil_position_audit_sheet_v1.csv) | Real BRENT rows closed; scenario rows untouched |
| [`ATS and Manual Live Position Reconciliation.md`](../ATS%20and%20Manual%20Live%20Position%20Reconciliation.md) | $119 exit recorded for real lots |
| [`Units Experiment Pool Allocation.md`](../Units%20Experiment%20Pool%20Allocation.md) | Foundation exit re-recorded at a single $119 price |
| [`Under-Duress Oil Sale Void Replay.md`](Under-Duress%20Oil%20Sale%20Void%20Replay.md) | Cross-reference note only; overlay not rewritten |
| [`TradingView Post-October 19 Block Policy.md`](TradingView%20Post-October%2019%20Block%20Policy.md) | Versioned scoped exception recorded |

## Policy treatment

The $119 price is dated **2026-10-30**, after the October 19 TradingView cutoff. It is recorded under the versioned scoped exception **`USER_DIRECTED_POST_CUTOFF_EXIT_SCOPED_EXCEPTION_20261030`**, authorized by this explicit user instruction. It is a **user-reported sale price**, not a newly imported TradingView mark or EOD series, and it authorizes no other post-cutoff data or model activity. No TradingView import, benchmark, sidecar, or general PnL rebuild is performed. Consistent with the standing block, this record does not create October 27–30 EOD marks and is not a current-date valuation of any other ticker.

## Limitations

- The $119 price, the 2026-10-30 date, and the "all BRENT" scope are **user-reported**. No brokerage statement, platform order record, or fill report independently confirms them.
- Time of execution was not supplied; **13:00 MST** is used only as a chronology ordering placeholder where a timestamp is structurally required.
- PnL is **price-only, before costs**. Fees, commissions, financing, margin, taxes, contract multipliers, slippage, and market impact are not modeled.
- Quantity conventions differ by book (platform-reported units, modeled quantity equivalents, fixed-notional U, and price-derived conversion units). They are **not** verified as dimensionally interchangeable.
- No cross-book grand total, reconciled cash balance, or NAV is asserted. Per-book subtotals are the outer limit of aggregation this record supports.
- Entry prices and quantities for the Private Fund and foundation lots are transcribed or modeled values carried forward from their source books; their exact entry dates/times remain unknown.
- This is a paper-trading record. It is not audited brokerage accounting, tax reporting, or investment advice.
