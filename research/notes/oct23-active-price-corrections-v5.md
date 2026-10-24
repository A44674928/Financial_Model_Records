# Oct. 23 Active Price Corrections — v5

> Superseded as the active endpoint set by [`consolidated_portfolio_closes_v7.csv`](../../data/consolidated_portfolio_closes_v7.csv); this note records the preceding v5 reconciliation. See [the v7 exact energy marks note](oct23-active-price-marks-v7.md).

## Decision and scope

The active close source is `data/consolidated_portfolio_closes_v5.csv`. It copies v4 and changes only the Oct. 23 UPS mark to the preserved v1 close of $101.06. This is consistent with the user's reported approximate $101 quote and the prior Oct. 22 close of $101.52; v1–v4 and their audits remain preserved.

| Ticker | Position | Entry price(s) | v4 mark | v5 mark | Modeled unrealized PnL at v5 |
|---|---|---:|---:|---:|---:|
| UPS | Two SHORT units | $94.13, $94.57 | $134.60 | **$101.06** | **−$1,422.48** |

Because UPS is short, a move from roughly $94.50 to $101.06 is adverse and still produces a loss. The correction reduces the modeled loss from roughly $8,532.22 under the v4 mark to $1,422.48; it does not turn the position profitable.

The saved multi-source candidate lists TradingView at $132.60 and Yahoo at $101.06 for Oct. 23, a 31.21% discrepancy. The user's reported ~$101 value agrees with the preserved v1 endpoint, not the saved TradingView candidate. Accordingly, v5 adopts the preserved v1 Yahoo-labeled endpoint for UPS; the TradingView candidate remains audit-only and the broader TradingView default remains pending a verified history.

## Audit trail

- `data/consolidated_portfolio_closes_v4.csv` remains preserved; v5 is now active.
- `data/eod_close_reconciliation_20261023_v4_to_v5.csv` compares all 35 endpoint rows and records only the UPS change.
- No trade entries, other endpoint values, or historical dates were changed.

## Rebuilt outputs

The active daily-price loader now reads v5. Model-performance exports, charts, comparison report, whole-portfolio DXY calculations and charts, and the yield-multiplier explorer were rebuilt. The master `Trades Zip PnL.md` remains outside this refresh.
