# ATS and Manual Live Position Reconciliation

> **Status and disclosure:** This is a user-directed hypothetical reconciliation, not a verified brokerage ledger, audited account statement, or investment recommendation. The user reports visual oversight/confirmation of ATS activity, but the exact ATS execution quantity is unknown. The requested category names are preserved while every ATS quantity remains explicitly scenario-based.

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

Per the user's latest instruction, add a separate **50U LONG ATS entry per ticker** at fixed prices of **$115.00 BRENT** and **$101.00 OIL**, modeled on 2026-10-26. The time was not supplied; these are hypothetical modeled open entries, not verified live fills, and no post-entry EOD mark is available. In the maximum 40U-per-ticker short scenario, these additions raise the tagged-campaign long holdings from 35U BRENT / 34U OIL to **85U BRENT / 84U OIL**.

| Ticker | Existing lots in maximum ATS scenario | New modeled ATS lot | Updated tagged-campaign total |
|---|---|---|---:|
| BRENT | 10U @ $111.412; 10U @ $115.792; 10U @ $114.800; 5U @ $114.627 | 50U @ $115.00 (2026-10-26; time not supplied) | 85U |
| OIL (USOIL) | 10U @ $99.04; 10U @ $101.74; 10U @ $101.00; 4U @ $100.74 | 50U @ $101.00 (2026-10-26; time not supplied) | 84U |

These totals are for the tagged campaign and ATS/manual reconciliation only; they exclude other core lots and the daily energy schedule. If the ATS short execution was smaller than the 40U-per-ticker ceiling, additional unsold ATS long units remain, so the total holdings would be larger than 85U/84U.

## MANUAL LIVE TEST POSITIONS

The four later 10U replenishment entries remain separate manual long lots and are labeled accordingly in the trade logs. Their sizes are not rescaled or netted against the ATS sensitivity. The 17:22 times are modeled midpoints of the user-recalled 17:20–17:25 window; the 20:00 times are approximate. The user-supplied prices remain model inputs, not verified transaction reports.

| Date | Time (MST) | Ticker | Manual event | Units | Modeled price |
|---|---|---|---|---:|---:|
| 2026-10-25 | ~17:22 | BRENT | Replenishment | 10U | $115.792 |
| 2026-10-25 | ~20:00 | BRENT | Replenishment | 10U | $114.800 |
| 2026-10-25 | ~17:22 | OIL (USOIL) | Replenishment | 10U | $101.740 |
| 2026-10-25 | ~20:00 | OIL (USOIL) | Replenishment | 10U | $101.000 |

## Scope boundaries and audit trail

- This is a separate reconciliation layer. It does not rewrite the Oct. 23 historical core PnL, DXY bridge, or the 32 independent THE ONE model alternatives; those are not a single live account.
- The 50U per-ticker lot is only the sizing proxy selected for this oil reconciliation. Other portfolio holdings are not multiplied by 80%, and the 32-book aggregate must not be used as an actual account denominator.
- The 40U ATS ceiling is not a claim that 40U executed. The exact sale/short quantity, order timing, fills, fees, financing, spread, slippage, and broker position remain unverified.
- The manually approved order sizes are retained as given; modeled closure amounts are capped at the open short. Residual long units are separated from closed-short units.
- The Oct. 25 replenishments are post-Oct. 23 and have no subsequent EOD mark in this ledger. No post-entry PnL is reported.
- Fixed model convention: 1U = $10,000 original notional. Oil unit sizing is not a count of barrels or an account equity percentage.

Machine-readable reconciliation: [`ats_manual_live_positions_v1.csv`](data/ats_manual_live_positions_v1.csv).
