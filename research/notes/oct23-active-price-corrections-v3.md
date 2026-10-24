# Oct. 23 Active Price Corrections — v3

> Superseded as the active close set by [`consolidated_portfolio_closes_v5.csv`](../../data/consolidated_portfolio_closes_v5.csv); this note records the preceding v3 reconciliation. See [the v5 note](oct23-active-price-corrections-v5.md) for the current endpoint decisions.

## Decision and scope

The active close source is `data/consolidated_portfolio_closes_v3.csv`. It is based on v2, changes only six Oct. 23 endpoint marks, and preserves v2 and the original v1 source unchanged. The historical daily price series and all Oct. 22 marks remain as before; no price was interpolated into earlier dates.

| Ticker | v2 close | v3 active close | Basis |
|---|---:|---:|---|
| NFLX | $762.10 | **$65.85** | User confirmed the v1 close is correct |
| BTC | $68,250.00 | **$81,227.04** | User confirmed the v1 close is correct |
| ETH | $2,640.00 | **$2,408.47** | User confirmed the v1 close is correct |
| RIVN | $11.25 | **$11.83** | User confirmed the v1 close is correct |
| LCID | $3.55 | **$3.52** | New user-provided Oct. 23 correction; Oct. 20–22 user marks remain $3.27, $3.21, and $3.46 |
| XRH0 | $790.00 | **$785.00** | New user-provided Oct. 23 correction; retain $790 through Oct. 22 and do not invent interim marks |

For the four Yahoo-labeled instruments, the explicit user confirmation selects the prior v1 values over the conflicting v2 endpoint values. The new LCID and XRH0 figures supersede the earlier Oct. 23 marks only; they do not revise other dates or trade-entry quotes.

## Audit trail

- `data/consolidated_portfolio_closes_v2.csv` remains preserved.
- `data/eod_closes_20261023_v1.csv` remains preserved.
- `data/eod_close_reconciliation_20261023.csv` remains the original v1-to-v2 audit.
- `data/eod_close_reconciliation_20261023_v2_to_v3.csv` compares all 35 terminal symbols and records the six changed values and their basis.
- `data/lcid_small_caps_pilot_daily_marks_v1.csv` preserves the previous $3.55 Oct. 23 pilot mark; `data/lcid_small_caps_pilot_daily_marks.csv` is the active corrected series.

## Rebuilt outputs

The active daily-price loader now reads v3. The model performance daily and ticker exports, static performance charts, `Model Performance Comparison.md`, the whole-portfolio DXY calculations and graphs, the yield-multiplier explorer, and the LCID pilot report/export/chart are rebuilt from the corrected endpoints.

The master `Trades Zip PnL.md` remains unrecalculated and unreconciled; intraday source data and trade-entry quotes are unchanged. The comprehensive-history v4–v6 candidates remain audit-only and are not adopted as a historical price series.
