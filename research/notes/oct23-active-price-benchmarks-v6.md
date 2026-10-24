# Active Price Benchmarks — v6

> Historical decision, superseded as the active energy source by [v7 exact user-provided marks](oct23-active-price-marks-v7.md). v6 remains preserved for audit.

## Decision and scope

The active consolidated endpoint is `data/consolidated_portfolio_closes_v6.csv`. It copies v5, preserves all earlier versions, and changes only the Oct. 23 BRENT and OIL endpoints to the Yahoo futures benchmark closes already used by the historical series.

| Internal ticker | v5 mark/source | v6 mark/source | Proxy basis |
|---|---:|---:|---|
| BRENT | $117.345, BlackBull override | **$113.81, Yahoo BZ=F** | Brent futures benchmark; not the logged BlackBull Brent Cash instrument |
| OIL | $103.45, TVC:USOIL override | **$97.53, Yahoo CL=F** | WTI futures benchmark; not the logged TVC:USOIL CFD instrument |

The change makes each energy series internally consistent from the cached historical Yahoo BZ=F/CL=F values through the Oct. 23 endpoint. It does **not** claim to reproduce the BlackBull or TradingView CFD candle. Exact chart-feed marks would require the matching provider history. The v5 file and all earlier close versions remain preserved. Row-level changes are in `data/eod_close_reconciliation_20261023_v5_to_v6.csv`.

The saved TradingView/Yahoo comparison candidate remains audit-only. Its repeated near-constant daily increments and large differences from the other source series are not reliable evidence of actual TradingView candles, so it was not adopted.

## FX, DXY, and yields

The current local daily inputs were retained, not newly fetched or independently validated:

- DXY and EUR/USD / JPY/USD: [`data/dxy_september_october_2026_daily_close.csv`](../../data/dxy_september_october_2026_daily_close.csv), [`data/eur_jpy_usd_september_october_2026.csv`](../../data/eur_jpy_usd_september_october_2026.csv), and terminal marks in [`data/dxy_fx_oct23_marks_2026.csv`](../../data/dxy_fx_oct23_marks_2026.csv). These are labeled user-provided; provider, session close, and timezone are not recorded in the input.
- US10Y and US30Y: the supplied daily yield files under `data/`. They are percentage yields, not instrument prices; source/provider and close convention are not independently verified here.
- The portfolio DXY comparison and yield-multiplier scenarios are rebuilt from these retained local inputs. The yield multiplier is **not CPI inflation** or a Treasury total-return measure. A true inflation-adjusted return would require a specified CPI series and calculation convention.

The row-level source map, proxy warnings, and verification status for the full active price set are in `data/active_price_source_registry_v1.csv`.

## Outputs rebuilt

The active daily loader now reads v6. Model performance and ticker exports, the performance charts, energy overlay, whole-portfolio DXY comparison, yield-multiplier explorer, and associated reports were rebuilt from v6 and the retained local FX/DXY/yield inputs. The master `Trades Zip PnL.md` remains outside this refresh.

## Limits

No external market-data endpoint was available in this run. The new version uses cached source series only; it does not invent or interpolate daily TradingView values. Future exact chart matching requires the proper provider-specific history (or an enabled market-data feed), especially for BlackBull Brent Cash, TVC:USOIL, FX close conventions, and ICE DXY.
