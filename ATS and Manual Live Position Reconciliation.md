# ATS and Manual Live Position Reconciliation

> **Status and disclosure:** This is a user-directed hypothetical reconciliation, not a verified brokerage ledger, audited account statement, or investment recommendation. The user reports visual oversight/confirmation of ATS activity, but the exact ATS execution quantity is unknown. The requested category names are preserved while every ATS quantity remains explicitly scenario-based.

## Later user-reported ATS oil liquidation

The user reports that the ATS sold **all ATS-held oil positions** as part of an exit from the oil industry, with the intention of selling for profit. This is user-reported and not independently verified. Exact units, execution date/time/timezone, and per-lot fills were not supplied, so no realized PnL, exact closed quantity, or residual ATS balance is calculated.

| Ticker | Marked-price group / user-supplied sale prices | Quantity | Execution date/time |
|---|---|---:|---|
| BRENT | Marked above $115: $117.345 to $116.48 | Not supplied | Not supplied |
| BRENT | Marked below $115: $114.67 to $116.48 | Not supplied | Not supplied |
| OIL (USOIL) | $103.40 / $101.50 as stated; cohort mapping not specified | Not supplied | Not supplied |

Detailed machine-readable sale bands: [`ats_oil_liquidation_reported_v1.csv`](data/ats_oil_liquidation_reported_v1.csv). The interval endpoints are preserved as ranges, not exact fill prices. The OIL price pair is preserved in the order supplied without assigning it to lots or mark cohorts. No PnL or per-lot exit is inferred.

The open-lot and ATS size-sensitivity tables below are pre-liquidation records; they do not establish current residual ATS units after this report. This update records the ATS scope only, does not reconcile manual or separately hypothetical pool positions, and does not rewrite historical core-model results. The exact quantity and trade chronology are still needed before any lot-level close or realized-PnL calculation can be posted.

## AUTOMATED TRADING SYSTEM LIVE POSITIONS

For this reconciliation only, the user selected each tagged Oct. 19 Weekend Oil 50U lot as a sizing proxy for a whole-portfolio 80% ATS / 20% manual framework. That proxy yields a maximum ATS allocation of 40U and a separate 10U manual remainder per ticker. It is **not** evidence that either those exact unit sizes or the broader account allocation were actually held.

The user-reported Oct. 23 ATS action is modeled as an ATS long exit at **$118.00 BRENT** and **$103.50 OIL**, with an equal-size short opened at the same modeled price. Since the amount is unknown, the ledger shows illustrative ATS executions of 10U, 20U, 30U, and 40U per ticker (25%, 50%, 75%, and 100% of the 40U ATS ceiling). These are sensitivities, not probabilities or a claimed exhaustive bound; actual quantity could be below the shown scenarios, in which case the assumed initial 10U cover would need revision. The manual 10U reference sleeve remains long in each scenario; any unexecuted part of the 40U ATS allocation also remains long.

The earlier Oct. 23 modeled 10U trims and 10U shorts at $117 BRENT / $102 OIL are superseded—not stacked—in this reconciliation. They remain in the legacy historical core replay for audit continuity, but are not additional ATS or manual events here.


## MANUALLY APPROVED SHORT CLOSURE

The Oct. 25 20:35 MST action is now reconciled closure-first: first apply the modeled 10U cover at $114.627 BRENT / $100.74 OIL, then allocate the 35U BRENT / 34U OIL manually approved orders to any remaining ATS short. Under every shown scenario this closes all remaining ATS shorts. Because the orders are larger than the residual shorts, the excess remains as a separate LONG position; only that excess counts as new long buy supply in this reconciliation. At the maximum 40U ATS scenario, 30U short per ticker remains after the initial 10U cover, so the approved orders close 30U each and leave 5U BRENT / 4U OIL LONG. For smaller ATS scenarios, more of each manual order remains LONG.

| Ticker | ATS short opened | After initial 10U cover | Manual approved order | Applied to short closure | Short remaining | Excess order left LONG / counted as buy supply |
|---|---:|---:|---:|---:|---:|---:|
| BRENT | 10U | 0U | 35U | 0U | 0U | 35U |
| BRENT | 20U | 10U | 35U | 10U | 0U | 25U |
| BRENT | 30U | 20U | 35U | 20U | 0U | 15U |
| BRENT | 40U | 30U | 35U | 30U | 0U | 5U |
| OIL (USOIL) | 10U | 0U | 34U | 0U | 0U | 34U |
| OIL (USOIL) | 20U | 10U | 34U | 10U | 0U | 24U |
| OIL (USOIL) | 30U | 20U | 34U | 20U | 0U | 14U |
| OIL (USOIL) | 40U | 30U | 34U | 30U | 0U | 4U |

Thus, the framing matches the position sizes: after the earlier 10U modeled cover, the largest remaining ATS short is 30U per ticker, less than either approved order. The closure applies only up to the open short; the remaining 5U/4U in the maximum scenario are not short closures.

## Additional modeled ATS fixed-price entries

The ledger retains the earlier **50U LONG ATS lots per ticker** at the previously supplied model prices of **$115.00 BRENT** and **$101.00 OIL**, dated 2026-10-26 with time not supplied. The user has clarified that the synchronized mirror move is a **separate additional 50U ATS USOIL LONG @ $101.11 at 07:51 MST**, synchronized with the 50U manual BRENT buy at $115.51. The mirror description applies to this new $101.11 lot, not the older $101.00 lot. The attached TradingView 1-minute USOIL chart shows $101.110000, the date Mon 26 Oct 2026, and a handwritten “ATS WAIT” annotation. This new $101.11 lot is distinct from—and added on top of—the earlier $101.00 ATS USOIL lot; the screenshot supports quote/time context but not a verified brokerage fill. Additional user-reported post-cutoff LONG entries include 10U per ticker through a MANUALLY APPROVED ATS ORDER at $115.025 BRENT / $100.96 OIL (date assumed 2026-10-26 from context; time not supplied), plus 16U BRENT at $114.90 and 17U OIL at $100.85 (date assumed 2026-10-26; strategy category and time not specified). These are user-reported, not independently verified, and retained separately from the fixed-price ATS entries. A further 50U manual BRENT LONG at $115.51 is included from the TradingView Brent Cash 1-minute screenshot: it shows $115.510 at 07:51:14 UTC−7 on a date inferred as 2026-10-26 from conversation/chart context, with a handwritten “PICK UP OPPORTUNITY” note. LONG is inferred from that annotation and was not explicitly stated in text; this is not a verified brokerage fill. Before the latest reported cash-out, the maximum 40U-per-ticker scenario included **161U BRENT / 161U OIL** in the tagged campaign. The user now reports selling the specifically paired **50U manual BRENT lot @ $115.51** at **$117.409** and the synchronized **50U ATS OIL mirror @ $101.11** at **$102.71**; these sales leave **111U BRENT / 111U OIL** in that maximum-scenario campaign. The older 50U ATS OIL lot @ $101.00 is not closed. Modeled realized PnL is $8,220.07 BRENT + $7,912.17 OIL = **$16,132.24 before costs**. These exits are user-reported but not independently verified; date is inferred as 2026-10-26 and 13:00 MST is an ordering placeholder because execution time was not supplied. The supplied 2026-10-26 EOD marks are BRENT $115.38 and OIL/USOIL $101.30; this scenario remains an uncertain-size position reconciliation, not verified account PnL.

| Ticker | Existing lots in maximum ATS scenario | Additional open lots counted | Updated tagged-campaign total |
|---|---|---|---:|
| BRENT | 10U @ $111.412; 10U @ $115.792; 10U @ $114.800; 5U @ $114.627 | 50U @ $115.00 ATS + 10U @ $115.025 ATS order + 16U @ $114.90 (classification unspecified); 50U @ $115.51 manual lot sold at $117.409 | 111U remaining |
| OIL (USOIL) | 10U @ $99.04; 10U @ $101.74; 10U @ $101.00; 4U @ $100.74 | Existing 50U @ $101.00 ATS + 10U @ $100.96 ATS order + 17U @ $100.85 (classification unspecified); 50U @ $101.11 ATS mirror sold at $102.71 | 111U remaining |

These totals are for the tagged campaign and ATS/manual reconciliation only; they exclude other core lots and the daily energy schedule. If the ATS short execution was smaller than the 40U-per-ticker ceiling, additional unsold ATS long units remain, so even after the paired 50U sales the total holdings would be larger than 111U per ticker. The OIL @ $101.11 mirror entry is additional to the existing 50U @ $101.00 ATS lot. The 10U/10U manually approved ATS order and 16U/17U user-reported additions are dated 2026-10-26 by conversation context because the user did not supply dates or times; their classification is preserved as stated or left unspecified. The screenshot-supported 50U BRENT entry is distinguished as a manual live test position with LONG inferred from the handwritten annotation.

## MANUAL LIVE TEST POSITIONS

The four later 10U replenishment entries remain separate manual long lots and are labeled accordingly in the trade logs. The additional 50U BRENT manual position is recorded as a separate MANUAL LIVE TEST POSITION from the screenshot; its LONG direction is inferred from the handwritten annotation. Its date is inferred from conversation/chart context. A second screenshot later shows $117.409 at 08:58:03 UTC−7; that is a later intraday chart observation only, not a verified fill or EOD valuation. The other 16U BRENT / 17U OIL additions remain outside the manual classification because the user did not specify their strategy category. The 17:22 times are modeled midpoints of the user-recalled 17:20–17:25 window; the 20:00 times are approximate. User-supplied prices remain model inputs, not verified transaction reports.

| Date | Time (MST) | Ticker | Manual event | Units | Modeled price |
|---|---|---|---|---:|---:|
| 2026-10-25 | ~17:22 | BRENT | Replenishment | 10U | $115.792 |
| 2026-10-25 | ~20:00 | BRENT | Replenishment | 10U | $114.800 |
| 2026-10-25 | ~17:22 | OIL (USOIL) | Replenishment | 10U | $101.740 |
| 2026-10-25 | ~20:00 | OIL (USOIL) | Replenishment | 10U | $101.000 |
| 2026-10-26* | 07:51:14 | BRENT | Manual LONG inferred from TradingView annotation; screenshot-supported | 50U | $115.510 |

* Date inferred from conversation context. Screenshot times are UTC−7 (MST). The 08:58:03 screenshot observation at $117.409 is not used as an EOD mark. The separate 10U BRENT / 10U OIL entries are MANUALLY APPROVED ATS ORDER entries shown in the supplemental records above, not part of this manual-only table.

## Additional user-reported entries — strategy classification unspecified

The user reported opening these LONG additions but did not specify whether they were ATS or manual. They are counted in the campaign totals but deliberately left outside both strategy labels. Date is inferred as 2026-10-26 from conversation context; timestamps were not supplied.

| Date (inferred) | Time | Ticker | User-reported position | Units | Price |
|---|---|---|---|---:|---:|
| 2026-10-26 | not supplied | BRENT | LONG; strategy classification unspecified | 16U | $114.900 |
| 2026-10-26 | not supplied | OIL (USOIL) | LONG; strategy classification unspecified | 17U | $100.850 |

## Scope boundaries and audit trail

- This is a separate reconciliation layer. It does not rewrite the Oct. 23 historical core PnL, DXY bridge, or the 32 independent THE ONE model alternatives; those are not a single live account.
- The 50U per-ticker lot is only the sizing proxy selected for this oil reconciliation. Other portfolio holdings are not multiplied by 80%, and the 32-book aggregate must not be used as an actual account denominator.
- The 40U ATS ceiling is not a claim that 40U executed. The exact sale/short quantity, order timing, fills, fees, financing, spread, slippage, and broker position remain unverified.
- The manually approved order sizes are retained as given; modeled closure amounts are capped at the open short. Residual long units are separated from closed-short units.
- The Oct. 25 replenishments and Oct. 26 user-reported additions now have supplied 2026-10-26 TradingView EOD marks (BRENT $115.38; OIL/USOIL $101.30). This reconciliation does not promote those scenario holdings to verified brokerage positions or actual account PnL. Dates/times or categories not supplied by the user remain explicitly marked as assumed or unspecified.
- Fixed model convention: 1U = $10,000 original notional. Oil unit sizing is not a count of barrels or an account equity percentage.

Machine-readable reconciliation: [`ats_manual_live_positions_v1.csv`](data/ats_manual_live_positions_v1.csv); user-reported ATS oil-sale bands: [`ats_oil_liquidation_reported_v1.csv`](data/ats_oil_liquidation_reported_v1.csv).
