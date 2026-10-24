# Exact User-Provided Energy EOD Marks — v7

The active consolidated Oct. 23 close set is `data/consolidated_portfolio_closes_v7.csv`. It preserves v6 and prior versions and restores the exact user-provided source-specific energy marks. v6 remains preserved as the prior Yahoo-futures-proxy endpoint decision.

## Active-position price history

- **BRENT — BlackBull Brent Cash:** 23 daily EOD marks, mapped in the order supplied to market sessions **Sep. 23–Oct. 23, 2026**. This begins on the first active Brent position date.
- **OIL — TradingView TVC:USOIL:** 32 daily EOD marks, mapped in the order supplied to market sessions **Sep. 10–Oct. 23, 2026**. The eight additional Sep. 10–21 marks fill the earlier active-position coverage gap.
- The complete input is `data/energy_provider_eod_marks_v1.csv`. The confirmed date mapping uses market sessions, with no interpolation or invented marks. Exact user marks override the cached Yahoo BZ=F/CL=F proxy series from the first active-position date onward. Earlier pre-entry context only retains those clearly labeled proxies.
- Oct. 23 exact marks are **BRENT $117.345** and **OIL $103.45**. Relative to v6, the endpoint changes are +$3.535 and +$5.92. Row-level changes are in `data/eod_close_reconciliation_20261023_v6_to_v7.csv`.

## Separate oil-desk hypothetical

A separate sidecar buys 10 new long units per ticker at every supplied EOD close, with $10,000 notional per unit. It reports the daily-buy lots alone, chart-opened maintenance positions alone, and the combined energy subtotal. It does not replace or blend into the four core strategy variants, and its daily capital deployment is not included in the core whole-account DXY/yield scenarios.

## Provenance limitations

These active energy values are direct user-provided EOD marks for the named instruments. The local DXY, FX, US10Y, and US30Y series were not refreshed and remain unverified for provider, timezone, and session convention. The yield factor remains a yield-spread scenario, not CPI inflation or Treasury total return. The historical master `Trades Zip PnL.md` remains unrecalculated.
