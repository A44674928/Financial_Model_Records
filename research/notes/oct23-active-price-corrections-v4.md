# Oct. 23 Active Price Corrections — v4

> Superseded as an active close set by [`consolidated_portfolio_closes_v7.csv`](../../data/consolidated_portfolio_closes_v7.csv); this note records the preceding v4 reconciliation. See [the v7 exact energy marks note](oct23-active-price-marks-v7.md).

## Decision and scope

The active close source is `data/consolidated_portfolio_closes_v4.csv`. It copies v3 and changes only the Oct. 23 marks for CVX, WMT, and TMO to their preserved v1 values, following the user's selection after the marks were found to conflict with the user's reported gains. All earlier dates and the other Oct. 23 marks remain unchanged. The v1, v2, and v3 source files remain intact.

| Ticker | v3 mark | Selected v1 mark (v4) | Entry price(s) | Result at selected mark |
|---|---:|---:|---:|---:|
| CVX | $151.30 | **$233.21** | $210.83, $210.68, $206.83 | +$3,406.36 modeled unrealized PnL |
| WMT | $81.15 | **$119.89** | $104.26 | +$1,499.14 modeled unrealized PnL |
| TMO | $524.30 | **$673.82** | $662.99 | +$163.35 modeled unrealized PnL |

These endpoint marks are selected from the preserved v1 data, whose source label is Yahoo Finance. This change does **not** establish the saved TradingView candidate as a complete or validated series, and does not change the graph source to TradingView. The user's TradingView-default preference remains pending a verified TradingView history because the saved candidate values conflict with the stated gains and the earlier coverage review did not validate it as a complete history.

AAPL remains at $347.73 and profitable against all four logged entries. NVDA remains at $210.96 against one $229.59 entry, or approximately $811.45 modeled unrealized loss; the saved TV and Yahoo marks agree at the Oct. 23 endpoint.

## Audit trail

- `data/consolidated_portfolio_closes_v3.csv` is preserved unchanged; v4 is now active.
- `data/eod_close_reconciliation_20261023_v3_to_v4.csv` compares the 35 endpoint rows and records the three changed prices.
- Existing v1→v2 and v2→v3 source files and audit tables are preserved.
- No Oct. 22 or earlier marks, trade entries, or trade logs were changed.

## Rebuilt outputs

The active daily-price loader now reads v4. Model-performance exports, charts, the comparison report, whole-portfolio DXY calculations and charts, and the yield multiplier explorer are rebuilt from the v4 endpoint. The master `Trades Zip PnL.md` remains outside this refresh.
