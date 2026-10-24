# Oil Desk EOD Accumulation Hypothetical

A separate sidecar model layered on top of the existing chart-opened Brent and TVC:USOIL positions. It does not alter the four core strategy definitions or their DXY/yield account bases.

For the daily position and PnL methodology across all variants and sidecars, see [`Model Calculation Guide.md`](Model%20Calculation%20Guide.md).

## Assumptions

- Buy **10 units (10U; $100,000 notional)** in each instrument at every supplied EOD session.
- One new long lot is opened at each session's EOD close and remains open through Oct. 23; no exits, fees, financing, or scaling from PnL.
- The daily buy at a given close starts accruing PnL after that close; therefore it has zero mark-to-market PnL at its purchase EOD.
- Chart-opened positions are shown separately and then added to the daily-buy hypothetical for a combined energy subtotal.
- Both the core replay and this sidecar use the same exact daily energy marks from `data/energy_provider_eod_marks_v1.csv`; the sidecar buys each tranche at that instrument's supplied EOD close.
- Yahoo `BZ=F` / `CL=F` values are pre-entry context proxies only; they are not used to mark active energy positions or sidecar purchases.

## Exact EOD mark coverage

| Ticker | Instrument / source | Active-period coverage | Sessions | Oct. 23 EOD mark |
|---|---|---|---:|---:|
| `BRENT` | User-provided BlackBull Markets Brent Cash EOD (`BlackBull Brent Cash`) | 2026-09-23–2026-10-23 | 23 | $117.345 |
| `OIL` | User-provided TradingView TVC:USOIL EOD (`TVC:USOIL`) | 2026-09-10–2026-10-23 | 32 | $103.45 |

## Terminal summary — Oct. 23, 2026

| Instrument | EOD sessions | Daily-buy units | Daily-buy notional | Daily-buy PnL | Chart units | Chart-position PnL | Combined energy PnL |
|---|---:|---:|---:|---:|---:|---:|---:|
| BRENT | 23 | 230 | $2,300,000.00 | $+224,358.86 | 5 | $+5,026.57 | $+229,385.42 |
| OIL | 32 | 320 | $3,200,000.00 | $+275,347.06 | 6 | $+6,614.56 | $+281,961.62 |
| **All energy** | 55 | 550 | $5,500,000.00 | $+499,705.92 | 11 | $+11,641.13 | $+511,347.05 |

![Daily EOD accumulation and chart positions](Charts/performance/19-oil-desk-daily-accumulation.png)

Session-level lots and PnL: [`oil_desk_eod_accumulation_v1.csv`](data/oil_desk_eod_accumulation_v1.csv).

Energy source rows: [`energy_provider_eod_marks_v1.csv`](data/energy_provider_eod_marks_v1.csv). Active source map: [`active_price_source_registry_v2.csv`](data/active_price_source_registry_v2.csv).

This hypothetical is not combined into the main portfolio DXY/yield multiplier views because it has its own daily capital deployment schedule. Applying those factors to the sidecar requires a separate account-capital convention.
