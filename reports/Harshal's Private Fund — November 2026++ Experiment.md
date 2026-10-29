# Harshal's Private Fund

**Statement:** Profit-only balance sheet  ·  **Experiment:** November 2026++ Experiment

## Balance sheet

This sheet carries forward the selected prior profit estimate, then adds only the two transaction-level realized-PnL amounts visible in the October 29 TradingView Paper Trading balance-history screenshots. It does **not** carry forward principal, account balances, margin, or other assets.

| Balance-sheet line | Amount (USD) | Treatment |
|---|---:|---|
| Prior profit-only carry-in | $2,396,569,687.95 | User-selected conservative endpoint of the prior model-based oil exit estimate |
| BRENT realized PnL added | +$933,875,016.74 | Screenshot shows 538,566,907-unit long closed at $115.777; average entry $114.043000 |
| USOIL realized PnL added | +$1,779,605,629.28 | Screenshot shows 601,218,118-unit long closed at $102.14; average entry $99.180000 |
| **Total new realized-PnL additions** | **+$2,713,480,646.02** | Sum of the two displayed transaction PnL amounts |
| Principal carried into this experiment | $0.00 | Excluded by instruction; not a claim that original principal was zero or lost |
| Other assets carried in | $0.00 | None included |
| Liabilities carried in | $0.00 | None supplied or modeled |
| **Ending profit-only experiment balance** | **$5,110,050,333.97** | Prior carry-in plus the two PnL additions; principal remains excluded |

## Close records

| Instrument | Action | Quantity | Average entry | Close price | Displayed realized PnL | Screenshot timestamp |
|---|---|---:|---:|---:|---:|---|
| BRENT (`BLACKBULL:BRENT`) | Close long | 538,566,907 | $114.043000 | $115.777 | +$933,875,016.74 | 2026-10-29 10:41:44; timezone not shown |
| USOIL (`TVC:USOIL`) | Close long | 601,218,118 | $99.180000 | $102.14 | +$1,779,605,629.28 | 2026-10-29 10:41:38; timezone not shown |

Screenshots and provenance: [`Archive/November_2026_Experiment_Oil_Closes_2026-10-29/README.md`](../Archive/November_2026_Experiment_Oil_Closes_2026-10-29/README.md). The account-level before/after balances and cumulative account PnL displayed in those screenshots are not added here; only the two transaction-level realized-PnL figures are included.

## Provenance and limitations

The two new PnL additions are transcribed from user-provided **TradingView Paper Trading** balance-history screenshots. They are screenshot-reported paper-trading close results, not independently audited brokerage executions. The visible records provide unit counts, average entry prices, close prices, timestamps, and per-close realized PnL; the timestamp timezone is not displayed. No account-level balance, principal, margin, or 50× display setting is used to scale these PnL amounts. Their mapping to the separate earlier locked-foundation estimate is unspecified; this sheet adds them to the carry-in per instruction and does not claim a cross-book deduplication.

The prior **$2,396,569,687.95** carry-in remains a user-selected conservative endpoint of a model-based price-envelope calculation. It is not an independently reconciled fill-level realized-PnL figure or audited cash balance. Therefore, the **$5,110,050,333.97** ending figure combines that selected prior estimate with the two screenshot-reported PnL additions; it should not be described as an audited account balance or fully reconciled realized profit.

The experiment label “November 2026++” is used as supplied. The two added closes are dated October 29, 2026, and are carried into this experiment per the user's instruction. No exact November opening day, additional investment, subsequent trade, return, liability, or principal is inferred. Any later change should be recorded as a separate dated transaction, with realized PnL distinguished from transfers and unrealized marks.
