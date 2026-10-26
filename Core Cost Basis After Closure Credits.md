# Core Cost Basis After Closure Credits

> **Scope and disclosure:** This is an economic cost-basis reclassification of modeled open LONG lots, not a tax-basis statement, brokerage record, verified fill report, or current market valuation. It uses the repository convention of $10,000 fixed notional per unit and the same notional-minus-realized-credit divided by exposure-quantity method used in the oil cost-basis report. No commissions, borrow costs, financing, or slippage are included.

The core model positions are replayed through the latest logged date, 2026-10-26. Post-Oct. 23 entries and exits have no later supplied EOD mark, so they do not change the historical Oct. 23 performance totals. The $87.55 INTC LONG is included in each model variant; the separate variants are not one combined account.

## Open-long basis by core variant

Prices below show both the unit-weighted entry average and the effective basis used for credit allocation. Closure credits are applied only to that ticker's current modeled open LONG basket.

| Ticker | Open LONG units (each variant) | Unit-weighted entry avg. | Unadjusted effective basis | Closure credit V1 / V2 / V3A / V3B | Adjusted effective basis V1 / V2 / V3A / V3B |
|---|---:|---:|---:|---:|---:|
| BRENT | 150U | $113.888773 | $113.844074 | $7,043.82 / $7,043.82 / $7,043.82 / $7,043.82 | $113.309476 / $113.309476 / $113.309476 / $113.309476 |
| USOIL | 150U | $100.197067 | $100.161374 | $4,223.99 / $4,223.99 / $4,223.99 / $4,223.99 | $99.879320 / $99.879320 / $99.879320 / $99.879320 |
| META | 3U | $692.190000 | $689.914948 | $1,718.87 / $0.00 / $8,594.34 / $0.00 | $650.385862 / $689.914948 / $492.269519 / $689.914948 |
| INTC | 9U | $93.799444 | $92.778930 | $5,506.50 / $0.00 / $17,955.56 / $0.00 | $87.102409 / $92.778930 / $74.268960 / $92.778930 |

### What is credited

- **BRENT and USOIL:** the 10U Manual-Automatic target-trim realized PnL and the explicit tagged 10U short-cover PnL are credited to each variant's open long basket, matching the existing [`Oil Cost Basis Savings Model.md`](Oil%20Cost%20Basis%20Savings%20Model.md) method. This is separate from the uncertain-size maximum-ATS campaign scenario; do not stack that campaign's 161U basis with these core rows.
- **INTC:** credits use the user-directed covers at $87.55 applied to the open short lots in each variant (V1's 2U and V3A's 6U). V2 and V3B had no INTC short exposure remaining at the time of those covers, so no new cover credit is assigned there.
- **META:** credits use the explicit $637.20 covers applied in each variant (V1's 1U; V3A's 5U total across the earlier 1U cover and the later 4U close). V2 and V3B had no META short exposure remaining at that time, so no new cover credit is assigned there. This model calculation does not establish the full basis of the user's reported 3U META LONG because the basis of the existing 2U was not supplied.
- Earlier SAR-driven covers for META/INTC are excluded from the new short-cover credit; they are not part of the user-directed close instructions reconciled here. Other realized trades are not added again. The credits reclassify modeled realized PnL and do not create additional portfolio PnL.
- The new credits from user-directed INTC/META covers are post-cutoff model results. They are not included in Oct. 23 terminal PnL and are not evidence of executed fills. The 13:00 MST log times for the new INTC/META actions are chronology placeholders because no times were supplied.

Machine-readable per-variant rows: [`core_cost_basis_closure_credits_v1.csv`](data/core_cost_basis_closure_credits_v1.csv).
