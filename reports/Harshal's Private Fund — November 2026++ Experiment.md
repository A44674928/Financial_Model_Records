# Harshal's Private Fund

**Statement:** Profit-only balance and position schedule  ·  **Experiment:** November 2026++ Experiment

## Profit-only balance

This section carries forward the selected prior profit estimate, then adds only the two transaction-level realized-PnL amounts visible in the October 29 TradingView Paper Trading balance-history screenshots. It does **not** carry forward principal, account balances, margin, or other assets.

| Balance-sheet line | Amount (USD) | Treatment |
|---|---:|---|
| Prior profit-only carry-in | $2,396,569,687.95 | User-selected conservative endpoint of the prior model-based oil exit estimate |
| BRENT realized PnL added | +$933,875,016.74 | Screenshot shows 538,566,907-unit long closed at $115.777; average entry $114.043000 |
| USOIL realized PnL added | +$1,779,605,629.28 | Screenshot shows 601,218,118-unit long closed at $102.14; average entry $99.180000 |
| **Total new realized-PnL additions** | **+$2,713,480,646.02** | Sum of the two displayed transaction PnL amounts |
| Principal carried into this experiment | $0.00 | Excluded by instruction; not a claim that original principal was zero or lost |
| **Profit-only cash carry-forward subtotal** | **$5,110,050,333.97** | Prior carry-in plus the two realized-PnL additions; before the LCID funding-source reconciliation |

## Added open position: LCID

The user-provided position screenshot shows an open LONG LCID position. It is added to the fund's position schedule as an **open asset snapshot**, not as realized profit.

| Instrument | Side/status | Quantity | Average fill | Screenshot last price | Trade value / cost basis | Market value | Unrealized PnL | PnL % |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| LCID (NASDAQ:LCID) | LONG; open per screenshot | 299,401,198.6 | $3.34 | $3.33 | $1,000,000,003.32 | $997,005,991.34 | -$2,994,011.99 | -0.30% |

The screenshot also displays **1× leverage** and **$997,005,991.34 margin**; these are transcribed as platform fields only. No additional leverage, borrowing, or financing is modeled. The $3.33 last price is screenshot-time context, not a supplied EOD mark. Screenshot capture date/time is not shown. Source archive: [`Archive/Private_Fund_LCID_Position/README.md`](../Archive/Private_Fund_LCID_Position/README.md).

The LCID market value is **not added to the profit-only cash subtotal** because the source of its funding was not specified. For reference only, a simple addition of $5,110,050,333.97 and $997,005,991.34 is **$6,107,056,325.31**; this is not a reconciled fund total. If LCID was bought with cash already included in the fund balance, the cash balance must be reduced by the funded amount; if separately funded, that contribution needs to be identified. The unrealized loss is already reflected in the market value versus trade value and must not be deducted twice.

## Close records

| Instrument | Action | Quantity | Average entry | Close price | Displayed realized PnL | Screenshot timestamp |
|---|---|---:|---:|---:|---:|---|
| BRENT (`BLACKBULL:BRENT`) | Close long | 538,566,907 | $114.043000 | $115.777 | +$933,875,016.74 | 2026-10-29 10:41:44; timezone not shown |
| USOIL (`TVC:USOIL`) | Close long | 601,218,118 | $99.180000 | $102.14 | +$1,779,605,629.28 | 2026-10-29 10:41:38; timezone not shown |

Screenshots and provenance: [`Archive/November_2026_Experiment_Oil_Closes_2026-10-29/README.md`](../Archive/November_2026_Experiment_Oil_Closes_2026-10-29/README.md). The account-level before/after balances and cumulative account PnL displayed in those screenshots are not added here; only the two transaction-level realized-PnL figures are included.

## Provenance and limitations

The two oil-close PnL additions are transcribed from user-provided **TradingView Paper Trading** balance-history screenshots. They are screenshot-reported paper-trading close results, not independently audited brokerage executions. The visible records provide unit counts, average entry prices, close prices, timestamps, and per-close realized PnL; the timestamp timezone is not displayed. No account-level balance, principal, margin, or 50× display setting is used to scale these PnL amounts. Their mapping to the separate earlier locked-foundation estimate is unspecified; this sheet adds them to the carry-in per instruction and does not claim a cross-book deduplication.

The prior **$2,396,569,687.95** carry-in remains a user-selected conservative endpoint of a model-based price-envelope calculation. It is not an independently reconciled fill-level realized-PnL figure or audited cash balance. Therefore, the **$5,110,050,333.97** profit-only subtotal combines that selected prior estimate with the two screenshot-reported PnL additions; it should not be described as an audited account balance or fully reconciled realized profit.

The LCID holding is transcribed from a user-provided TradingView position screenshot and remains open per that snapshot. The snapshot does not establish its acquisition date, funding source, or account/ledger mapping. Its market value is displayed separately until funding is reconciled; neither it nor the screenshot unrealized PnL changes the realized-profit figures above.

The experiment label “November 2026++” is used as supplied. The two oil closes are dated October 29, 2026, and are carried into this experiment per the user's instruction. No exact November opening day, additional investment, subsequent trade, return, liability, or principal is inferred. Any later change should be recorded as a separate dated transaction, with realized PnL distinguished from transfers and unrealized marks.
