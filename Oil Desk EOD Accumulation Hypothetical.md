# Oil Desk EOD Accumulation Hypothetical

> **Current hypothetical sidecar through 2026-10-26.** Daily energy marks use the same aligned user-provided TradingView EOD benchmark session file as the core replay, including the supplied Oct. 26 update. The 1U/DAY/DXY sleeve is already integrated into core variants; 0.05U remains an alternative, while THE ONE MODEL separately adds 10U/DAY DXY to each of its 32 portfolios. This 10U energy schedule is a separate scenario, not an additional allocation to the core or downstream core-based portfolios.

This daily-buy sidecar is separate from the core. Its chart-position series is an attribution of logged chart/core lots, including the 50U Manual-Automatic Weekend Oil entries; those same tagged lots are already included in each core variant and must not be added to core-based composites a second time. The chart-position column shows open-lot unrealized PnL only; the realized trim PnL is recorded in the core replay.

For the daily position and PnL methodology across all variants and sidecars, see [`Model Calculation Guide.md`](Model%20Calculation%20Guide.md).

## Assumptions

- Buy **10 units (10U; $100,000 notional)** in each instrument at every supplied EOD session.
- One new long lot is opened at each active session's EOD close and remains open through 2026-10-26; no exits, fees, financing, or scaling from PnL.
- The daily buy at a given close starts accruing PnL after that close; therefore it has zero mark-to-market PnL at its purchase EOD.
- Chart-opened positions are shown separately and then added to the daily-buy hypothetical for a combined energy subtotal.
- Both the core replay and this sidecar use the same aligned marks in `data/tradingview_benchmark_session_marks_20261026.csv`; the sidecar buys each tranche at that instrument's supplied EOD close.
- Yahoo `BZ=F` / `CL=F` values are pre-entry context proxies only; they are not used to mark active energy positions or sidecar purchases.

## Exact EOD mark coverage

| Ticker | Instrument / source | Active-period coverage | Sessions | 2026-10-26 EOD mark |
|---|---|---|---:|---:|
| `BRENT` | tradingview_eod_marks_20261026.csv (`BRENT`) | 2026-09-23–2026-10-26 | 24 | $115.38 |
| `OIL` | tradingview_eod_marks_20261026.csv (`TVC:USOIL`) | 2026-09-10–2026-10-26 | 33 | $101.30 |

## Terminal summary — 2026-10-26

| Instrument | EOD sessions | Daily-buy units | Daily-buy notional | Daily-buy PnL | Chart-open units | Chart-open unrealized PnL | Combined energy PnL |
|---|---:|---:|---:|---:|---:|---:|---:|
| BRENT | 24 | 240 | $2,400,000.00 | $+183,171.11 | 100 | $+20,799.95 | $+203,971.06 |
| OIL | 33 | 330 | $3,300,000.00 | $+203,118.97 | 100 | $+16,112.31 | $+219,231.27 |
| **All energy** | 57 | 570 | $5,700,000.00 | $+386,290.07 | 200 | $+36,912.26 | $+423,202.33 |

![Daily EOD accumulation and chart positions](Charts/performance/19-oil-desk-daily-accumulation.png)

Session-level lots and PnL: [`oil_desk_eod_accumulation_v1.csv`](data/oil_desk_eod_accumulation_v1.csv).

Energy source rows: [`energy_provider_eod_marks_v1.csv`](data/energy_provider_eod_marks_v1.csv). Active source map: [`active_price_source_registry_v3.csv`](data/active_price_source_registry_v3.csv).

This historical 10U/day-buy schedule is not part of current core-based composites or whole-portfolio DXY/yield multipliers. Its combined energy column includes the chart-lot attribution described above, which is already in core; do not add that contribution again. Applying whole-account factors to the separate daily-buy schedule would require a distinct capital convention.
