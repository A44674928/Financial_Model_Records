# Harshal's Private Fund

**Statement:** Profit-only balance and position schedule  ·  **Experiment:** November 2026++ Experiment

## Profit-only balance

This section carries forward the selected prior profit estimate. The October 29 TradingView Paper Trading screenshots display two oil close transactions. The user directed that both close records be **nullified and voided**; on **2026-10-30** the user then directed that **all BRENT was sold at $119**, which **lifts and supersedes** the BRENT void. The BRENT long is therefore closed at $119.00 with price-only realized PnL recognized. The **USOIL** close remains nullified and voided, and the earlier USOIL long remains open at its reported entry price of $99.18 with no current mark supplied. The superseded BRENT screenshot PnL is preserved as source evidence but is **not recognized as realized PnL**. Neither status is independently confirmed by a platform void record. The schedule does **not** carry forward principal, account balances, margin, or other assets.

| Balance-sheet line | Amount (USD) | Treatment |
|---|---:|---|
| Prior profit-only carry-in | $2,396,569,687.95 | User-selected conservative endpoint of the prior model-based oil exit estimate |
| BRENT close record — 2026-10-29 void **lifted**; sold at $119 on 2026-10-30 | $2,669,676,158.00 recognized | Price-only realized PnL: 538,566,907 platform units × ($119.00 − $114.043), before costs. Superseded screenshot close $115.777 / PnL $933,875,016.74 retained as source evidence only |
| USOIL close record — nullified/voided per user instruction | $0.00 recognized | Earlier long remains open at $99.18; screenshot close/PnL retained only as voided-source evidence |
| **Total new realized-PnL additions** | **$2,669,676,158.00** | BRENT recognized from the $119 exit; USOIL close remains nullified/voided |
| Principal carried into this experiment | $0.00 | Excluded by instruction; not a claim that original principal was zero or lost |
| **Profit-only cash carry-forward subtotal** | **$5,066,245,845.95** | Prior carry-in plus $2,669,676,158.00 recognized BRENT additions; before the LCID funding-source reconciliation |

## BRENT closed at $119; USOIL long retained open

| Instrument | Side/status | Reported quantity | Earlier entry price | Entry date/time | Exit price | Current mark / valuation |
|---|---|---:|---:|---|---:|---|
| BRENT (`BLACKBULL:BRENT`) | **CLOSED — SOLD AT $119 on 2026-10-30** | 538,566,907 platform units | $114.043000 | Earlier entry; exact date/time not supplied | $119.00 | Closed; price-only realized PnL $2,669,676,158.00 before costs |
| USOIL (`TVC:USOIL`) | LONG; open | 601,218,118 platform units | $99.180000 | Earlier entry; exact date/time not supplied | — | Not supplied; no market value or PnL calculated |

These are separate Private Fund source-book lots. The user's 2026-10-30 direction that **all BRENT was sold at $119** supersedes the earlier nullification/void of the BRENT close, so that lot is now closed and its price-only realized PnL is recognized once. The USOIL close record remains nullified/voided per the earlier direction; its screenshot close price is not a mark and its displayed PnL is not realized. Quantities and entry prices are transcribed from the screenshots; no multiplier, cash basis, account mapping to the active Oil model, or funding source is inferred. See [`BRENT Full Exit at $119 — 2026-10-30.md`](BRENT%20Full%20Exit%20at%20%24119%20%E2%80%94%202026-10-30.md) and [`data/brent_sold_119_20261030_v1.csv`](../data/brent_sold_119_20261030_v1.csv).

## Added open position: LCID

The user-provided position screenshot shows an open LONG LCID position. It is added to the fund's position schedule as an **open asset snapshot**, not as realized profit.

| Instrument | Side/status | Quantity | Average fill | Screenshot last price | Trade value / cost basis | Market value | Unrealized PnL | PnL % |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| LCID (NASDAQ:LCID) | LONG; open per screenshot | 299,401,198.6 | $3.34 | $3.33 | $1,000,000,003.32 | $997,005,991.34 | -$2,994,011.99 | -0.30% |

The screenshot also displays **1× leverage** and **$997,005,991.34 margin**; these are transcribed as platform fields only. No additional leverage, borrowing, or financing is modeled. The $3.33 last price is screenshot-time context, not a supplied EOD mark. Screenshot capture date/time is not shown. Source archive: [`Archive/Private_Fund_LCID_Position/README.md`](../Archive/Private_Fund_LCID_Position/README.md).

The LCID market value is **not added to the profit-only carry-forward** because the source of its funding was not specified. For reference only, a simple addition of $5,066,245,845.95 and $997,005,991.34 is **$6,063,251,837.29**; this is not a reconciled fund total. If LCID was bought with cash already included in the fund balance, the cash balance must be reduced by the funded amount; if separately funded, that contribution needs to be identified. The unrealized loss is already reflected in the market value versus trade value and must not be deducted twice.

### Additional LCID buy order added to the fund

Per the user's instruction, the following filled LCID order is included as a separate purchase lot. The order-history screenshot shows the account selector truncated as `SWITCH_TO_LCI...`; it does not establish that this is the same account as the prior LCID position snapshot. No aggregate quantity or combined market value is inferred.

| Instrument | Order | Quantity | Fill price | Fill value / cost basis | Status | Displayed fill time | Order ID |
|---|---|---:|---:|---:|---|---|---|
| LCID (NASDAQ:LCID) | Buy market | 301,204,819.27 | $3.32 | $999,999,999.98 | Filled | 2026-10-29 11:05:57; timezone not shown | 3736492349 |

The order is recorded as a separate LCID lot at fill value. The screenshot does not supply a later mark for this lot, its funded-cash source, or a matching close; it is not added as realized PnL or to the profit-only cash subtotal. See [`Archive/Private_Fund_LCID_Position/README.md`](../Archive/Private_Fund_LCID_Position/README.md) for screenshot provenance.

## Close records

| Instrument | User-directed status | Quantity | Earlier entry | Exit price booked | Price-only realized PnL booked | Superseded screenshot close (not a mark) | Superseded screenshot PnL (not recognized) | Screenshot timestamp |
|---|---|---:|---:|---:|---:|---:|---:|---|
| BRENT (`BLACKBULL:BRENT`) | **2026-10-29 void LIFTED; sold at $119 on 2026-10-30** | 538,566,907 | $114.043000 | **$119.00** | **+$2,669,676,158.00** | $115.777 | +$933,875,016.74 | 2026-10-29 10:41:44; timezone not shown |
| USOIL (`TVC:USOIL`) | Close nullified/voided; long remains open | 601,218,118 | $99.180000 | — | $0.00 | $102.14 | +$1,779,605,629.28 | 2026-10-29 10:41:38; timezone not shown |

The original screenshots are retained unchanged. The user first directed that both close records be nullified and voided, then directed on **2026-10-30** that **all BRENT was sold at $119**. That later instruction **lifts and supersedes** the BRENT void only: BRENT is closed at $119.00 and its price-only realized PnL is recognized once. The BRENT screenshot close price of $115.777 and its displayed PnL are preserved as **superseded source evidence**; they are not a mark and are not booked. The **USOIL** close record remains nullified and voided, and its long remains open at $99.18 with **$0.00** booked. Entry dates/times are unknown. Platform void status is not independently confirmed, and the account mapping to the active Oil model or locked foundation is unresolved. See [`BRENT Full Exit at $119 — 2026-10-30.md`](BRENT%20Full%20Exit%20at%20%24119%20%E2%80%94%202026-10-30.md), [`Archive/November_2026_Experiment_Oil_Closes_2026-10-29/README.md`](../Archive/November_2026_Experiment_Oil_Closes_2026-10-29/README.md) and [`Under-Duress Oil Sale Void Replay.md`](Under-Duress%20Oil%20Sale%20Void%20Replay.md).

## Provenance and limitations

The two displayed oil-close PnL figures are transcribed from user-provided **TradingView Paper Trading** balance-history screenshots. The screenshots are preserved as evidence; they are **not independently audited brokerage executions** or proof that a platform processed a void. Per the user's earlier instruction both close records were nullified and voided; per the user's later **2026-10-30** instruction the BRENT void is **lifted and superseded** by a sale at **$119**, so the BRENT long is now closed while the USOIL long remains open. Neither displayed screenshot PnL is recognized as realized: the BRENT figure is superseded by the $119 exit and the USOIL figure remains voided-source evidence. No account-level balance, principal, margin, or 50× display setting is used to scale the amounts. Entry dates/times and mapping to the separate earlier locked-foundation estimate remain unspecified.

The BRENT realized PnL of **$2,669,676,158.00** is **price-only and before costs**: `538,566,907 platform units × ($119.00 − $114.043)`. Fees, commissions, financing, margin, taxes, contract multipliers, slippage, and market impact are not modeled. The quantity is a **platform-reported unit count** transcribed from the screenshot; no cash basis or market value is inferred from it, and it is not verified as a contract, barrel, or broker-order quantity. The $119 sale price and the 2026-10-30 date are **user-reported**; no brokerage statement or platform order record independently confirms them. Execution time was not supplied. This exit is recorded under the versioned scoped exception `USER_DIRECTED_POST_CUTOFF_EXIT_SCOPED_EXCEPTION_20261030` because its date falls after the October 19 TradingView cutoff.

The prior **$2,396,569,687.95** carry-in remains a user-selected conservative endpoint of a model-based price-envelope calculation. It is not an independently reconciled fill-level realized-PnL figure or audited cash balance. The current **$5,066,245,845.95** profit-only carry-forward reflects that prior estimate plus **$2,669,676,158.00 recognized** from the user-directed BRENT $119 exit, with **$0.00** from the USOIL close that remains nullified/voided; it should not be described as an audited account balance or fully reconciled realized profit.

The LCID holding is transcribed from a user-provided TradingView position screenshot and remains open per that snapshot. The snapshot does not establish its acquisition date, funding source, or account/ledger mapping. Its market value is displayed separately until funding is reconciled; neither it nor the screenshot unrealized PnL changes the realized-profit figures above.

The experiment label “November 2026++” is used as supplied. The October 29 oil close screenshots are retained. The user first directed that both close records be nullified and voided, then directed on 2026-10-30 that all BRENT was sold at $119; the BRENT void is therefore lifted and superseded and that long is closed, while the **USOIL** long remains open at its stated entry price with its displayed PnL not carried into the balance. No exact entry date/time, current USOIL mark, November opening day, additional investment, liability, or principal is inferred. Any later change should be recorded separately, with realized PnL distinguished from transfers and unrealized marks.
