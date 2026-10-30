# Harshal's Private Fund

**Statement:** Profit-only balance and position schedule  ·  **Experiment:** November 2026++ Experiment

## Profit-only balance

This section carries forward the selected prior profit estimate. The October 29 TradingView Paper Trading screenshots display two oil close transactions, but the user directed that both close records be **nullified and voided**. The earlier BRENT and USOIL longs remain open at their reported entry prices ($114.043 and $99.18); no current mark is supplied. Screenshot PnL is preserved as source evidence but is **not recognized as realized PnL**. The status is user-directed and not independently confirmed by a platform void record. The schedule does **not** carry forward principal, account balances, margin, or other assets.

| Balance-sheet line | Amount (USD) | Treatment |
|---|---:|---|
| Prior profit-only carry-in | $2,396,569,687.95 | User-selected conservative endpoint of the prior model-based oil exit estimate |
| BRENT close record — nullified/voided per user instruction | $0.00 recognized | Earlier long remains open at $114.043; screenshot close/PnL retained only as voided-source evidence |
| USOIL close record — nullified/voided per user instruction | $0.00 recognized | Earlier long remains open at $99.18; screenshot close/PnL retained only as voided-source evidence |
| **Total new realized-PnL additions** | **$0.00** | Both close records nullified/voided; no close is booked |
| Principal carried into this experiment | $0.00 | Excluded by instruction; not a claim that original principal was zero or lost |
| **Profit-only cash carry-forward subtotal** | **$2,396,569,687.95** | Prior carry-in plus $0.00 recognized additions; before the LCID funding-source reconciliation |

## Oil longs retained open after voiding the October 29 close records

| Instrument | Side/status | Reported quantity | Earlier entry price | Entry date/time | Current mark / valuation |
|---|---|---:|---:|---|---|
| BRENT (`BLACKBULL:BRENT`) | LONG; open | 538,566,907 platform units | $114.043000 | Earlier entry; exact date/time not supplied | Not supplied; no market value or PnL calculated |
| USOIL (`TVC:USOIL`) | LONG; open | 601,218,118 platform units | $99.180000 | Earlier entry; exact date/time not supplied | Not supplied; no market value or PnL calculated |

These are separate Private Fund source-book lots. The October 29 close records are nullified/voided per user direction; their screenshot close prices are not marks and their displayed PnL is not realized. Quantities and entry prices are transcribed from the screenshots; no multiplier, cash basis, account mapping to the active Oil model, or funding source is inferred.

## Added open position: LCID

The user-provided position screenshot shows an open LONG LCID position. It is added to the fund's position schedule as an **open asset snapshot**, not as realized profit.

| Instrument | Side/status | Quantity | Average fill | Screenshot last price | Trade value / cost basis | Market value | Unrealized PnL | PnL % |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| LCID (NASDAQ:LCID) | LONG; open per screenshot | 299,401,198.6 | $3.34 | $3.33 | $1,000,000,003.32 | $997,005,991.34 | -$2,994,011.99 | -0.30% |

The screenshot also displays **1× leverage** and **$997,005,991.34 margin**; these are transcribed as platform fields only. No additional leverage, borrowing, or financing is modeled. The $3.33 last price is screenshot-time context, not a supplied EOD mark. Screenshot capture date/time is not shown. Source archive: [`Archive/Private_Fund_LCID_Position/README.md`](../Archive/Private_Fund_LCID_Position/README.md).

The LCID market value is **not added to the profit-only carry-forward** because the source of its funding was not specified. For reference only, a simple addition of $2,396,569,687.95 and $997,005,991.34 is **$3,393,575,679.29**; this is not a reconciled fund total. If LCID was bought with cash already included in the fund balance, the cash balance must be reduced by the funded amount; if separately funded, that contribution needs to be identified. The unrealized loss is already reflected in the market value versus trade value and must not be deducted twice.

### Additional LCID buy order added to the fund

Per the user's instruction, the following filled LCID order is included as a separate purchase lot. The order-history screenshot shows the account selector truncated as `SWITCH_TO_LCI...`; it does not establish that this is the same account as the prior LCID position snapshot. No aggregate quantity or combined market value is inferred.

| Instrument | Order | Quantity | Fill price | Fill value / cost basis | Status | Displayed fill time | Order ID |
|---|---|---:|---:|---:|---|---|---|
| LCID (NASDAQ:LCID) | Buy market | 301,204,819.27 | $3.32 | $999,999,999.98 | Filled | 2026-10-29 11:05:57; timezone not shown | 3736492349 |

The order is recorded as a separate LCID lot at fill value. The screenshot does not supply a later mark for this lot, its funded-cash source, or a matching close; it is not added as realized PnL or to the profit-only cash subtotal. See [`Archive/Private_Fund_LCID_Position/README.md`](../Archive/Private_Fund_LCID_Position/README.md) for screenshot provenance.

## Close records

| Instrument | User-directed status | Quantity | Earlier entry | Voided screenshot close (not a mark) | Screenshot PnL (not recognized) | Screenshot timestamp |
|---|---|---:|---:|---:|---:|---|
| BRENT (`BLACKBULL:BRENT`) | Close nullified/voided; long remains open | 538,566,907 | $114.043000 | $115.777 | +$933,875,016.74 | 2026-10-29 10:41:44; timezone not shown |
| USOIL (`TVC:USOIL`) | Close nullified/voided; long remains open | 601,218,118 | $99.180000 | $102.14 | +$1,779,605,629.28 | 2026-10-29 10:41:38; timezone not shown |

The original screenshots are retained unchanged. The user directed that both close records be nullified and voided; the longs remain open at the earlier entries shown above. Entry dates/times are unknown. The screenshot close prices are preserved as voided-source details, not used as current marks, and **$0.00 is booked as realized PnL**. Platform void status is not independently confirmed, and the account mapping to the active Oil model or locked foundation is unresolved. See [`Archive/November_2026_Experiment_Oil_Closes_2026-10-29/README.md`](../Archive/November_2026_Experiment_Oil_Closes_2026-10-29/README.md) and [`Under-Duress Oil Sale Void Replay.md`](Under-Duress%20Oil%20Sale%20Void%20Replay.md).

## Provenance and limitations

The two displayed oil-close PnL figures are transcribed from user-provided **TradingView Paper Trading** balance-history screenshots. The screenshots are preserved as evidence; they are **not independently audited brokerage executions** or proof that a platform processed a void. Per the user's instruction, the close records are nullified and voided here; their earlier long lots remain open, and the displayed PnL is not recognized as realized. No account-level balance, principal, margin, or 50× display setting is used to scale the amounts. Entry dates/times and mapping to the separate earlier locked-foundation estimate remain unspecified.

The prior **$2,396,569,687.95** carry-in remains a user-selected conservative endpoint of a model-based price-envelope calculation. It is not an independently reconciled fill-level realized-PnL figure or audited cash balance. The current **$2,396,569,687.95** profit-only carry-forward reflects that prior estimate plus **$0.00 recognized** from the nullified/voided oil closes; it should not be described as an audited account balance or fully reconciled realized profit.

The LCID holding is transcribed from a user-provided TradingView position screenshot and remains open per that snapshot. The snapshot does not establish its acquisition date, funding source, or account/ledger mapping. Its market value is displayed separately until funding is reconciled; neither it nor the screenshot unrealized PnL changes the realized-profit figures above.

The experiment label “November 2026++” is used as supplied. The October 29 oil close screenshots are retained, but the user directed that the close records be nullified and voided; the earlier longs remain open at the stated entry prices and their displayed PnL is not carried into the balance. No exact entry date/time, current mark, November opening day, additional investment, liability, or principal is inferred. Any later change should be recorded separately, with realized PnL distinguished from transfers and unrealized marks.
