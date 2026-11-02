# Harshal's Private Fund

**Statement:** Profit-only balance and position schedule  ·  **Experiment:** November 2026++ Experiment

## Profit-only balance

Both earlier October 29 screenshot closes were voided and subsequently superseded by user-directed October 30 exits: BRENT at $119 and USOIL at $104.50. The screenshots remain unchanged as source evidence, not booked PnL. Execution is not independently verified; PnL is price-only before costs.

| Balance-sheet line | Amount (USD) | Treatment |
|---|---:|---|
| Prior profit-only carry-in | $2,396,569,687.95 | User-selected prior modeled estimate |
| BRENT $119 exit | $2,669,676,158.00 | Price-only, 538,566,907 × ($119 − $114.043) |
| USOIL $104.50 exit | $3,198,480,387.76 | Price-only, 601,218,118 × ($104.50 − $99.18) |
| **Total new realized-PnL additions** | **$5,868,156,545.76** | Both exits, once each |
| Principal carried into experiment | $0.00 | Excluded, not a claim original principal was zero |
| **Profit-only cash carry-forward subtotal** | **$8,264,726,233.71** | Prior estimate plus both exits; not an audited balance |

## Oil positions — closed

| Instrument | Quantity | Entry | Exit | Price-only PnL |
|---|---:|---:|---:|---:|
| BRENT | 538,566,907 platform units | $114.043 | $119 | $2,669,676,158.00 |
| USOIL | 601,218,118 platform units | $99.18 | $104.50 | $3,198,480,387.76 |

Both earlier voids are lifted and superseded. No cash basis, contract multiplier, funding source or cross-book mapping is inferred. Entry date/time and execution time were not supplied. See [BRENT report](BRENT%20Full%20Exit%20at%20%24119%20%E2%80%94%202026-10-30.md) and [USOIL report](USOIL%20Full%20Exit%20at%20%24104.50%20%E2%80%94%202026-10-30.md).

## Added open position: LCID

The user-provided position screenshot shows an open LONG LCID position. It is added to the fund's position schedule as an **open asset snapshot**, not as realized profit.

| Instrument | Side/status | Quantity | Average fill | Screenshot last price | Trade value / cost basis | Market value | Unrealized PnL | PnL % |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| LCID (NASDAQ:LCID) | LONG; open per screenshot | 299,401,198.6 | $3.34 | $3.33 | $1,000,000,003.32 | $997,005,991.34 | -$2,994,011.99 | -0.30% |

The screenshot also displays **1× leverage** and **$997,005,991.34 margin**; these are transcribed as platform fields only. No additional leverage, borrowing, or financing is modeled. The $3.33 last price is screenshot-time context, not a supplied EOD mark. Screenshot capture date/time is not shown. Source archive: [`Archive/Private_Fund_LCID_Position/README.md`](../Archive/Private_Fund_LCID_Position/README.md).

The LCID market value is **not added to the profit-only carry-forward** because the source of its funding was not specified. For reference only, a simple addition of $8,264,726,233.71 and $997,005,991.34 is **$9,261,732,225.05**; this is not a reconciled fund total. If LCID was bought with cash already included in the fund balance, the cash balance must be reduced by the funded amount; if separately funded, that contribution needs to be identified. The unrealized loss is already reflected in the market value versus trade value and must not be deducted twice.

### Additional LCID buy order added to the fund

Per the user's instruction, the following filled LCID order is included as a separate purchase lot. The order-history screenshot shows the account selector truncated as `SWITCH_TO_LCI...`; it does not establish that this is the same account as the prior LCID position snapshot. No aggregate quantity or combined market value is inferred.

| Instrument | Order | Quantity | Fill price | Fill value / cost basis | Status | Displayed fill time | Order ID |
|---|---|---:|---:|---:|---|---|---|
| LCID (NASDAQ:LCID) | Buy market | 301,204,819.27 | $3.32 | $999,999,999.98 | Filled | 2026-10-29 11:05:57; timezone not shown | 3736492349 |

The order is recorded as a separate LCID lot at fill value. The screenshot does not supply a later mark for this lot, its funded-cash source, or a matching close; it is not added as realized PnL or to the profit-only cash subtotal. See [`Archive/Private_Fund_LCID_Position/README.md`](../Archive/Private_Fund_LCID_Position/README.md) for screenshot provenance.

## Close records and provenance

| Instrument | Current user-directed exit | Price-only PnL | Superseded screenshot close | Superseded screenshot PnL | Screenshot timestamp |
|---|---:|---:|---:|---:|---|
| BRENT | $119.00 | $2,669,676,158.00 | $115.777 | $933,875,016.74 | 2026-10-29 10:41:44; timezone not shown |
| USOIL | $104.50 | $3,198,480,387.76 | $102.14 | $1,779,605,629.28 | 2026-10-29 10:41:38; timezone not shown |

The October 29 screenshots are preserved unchanged. Both prior voids are lifted and superseded by the user-directed October 30 prices. Neither screenshot PnL is booked. Platform quantities are transcribed; no contract multiplier or cash basis is inferred. No brokerage fill or account balance is independently verified. The carry-in is a prior model-based oil exit estimate and may overlap the reported exit profits; the overlap and the LCID funding source remain unreconciled; the subtotal is not an audited cash balance or fully reconciled profit. Fees, taxes, financing, margin, slippage and market impact are excluded. The two exits have separate post-cutoff scoped exceptions; no other marks or general model recalculation are authorized.
