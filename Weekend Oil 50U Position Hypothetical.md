# Weekend Oil 50U Position Hypothetical

> **Hypothetical educational mark-to-market only.** The partial exits below are assumed paper trades, not broker executions, a verified account return, or a recommendation. Costs, financing, slippage, and liquidation are not modeled.

## Position and trim assumptions

The user specified a **50U LONG** position each in BRENT and USOIL at the **2026-10-19 market open**, with entry marks of $111.412 and $99.04 respectively. The thesis instruction is modeled as selling **10U of BRENT at $117** and **10U of USOIL at $102**, leaving **40U open in each** after the assumed trims. At $10,000 notional per unit, opening gross notional is $1,000,000 total; $200,000 of unit-basis gross notional is trimmed and $800,000 remains open.

| Instrument | Entry price | Trim instruction | Modeled trigger session | Realized PnL on 10U sale | Oct. 23 EOD mark | Remaining 40U unrealized PnL | Total realized + unrealized PnL | Remaining gross open notional |
|---|---:|---|---|---:|---:|---:|---:|---:|
| BRENT | $111.412 | Sell 10U at $117 | 2026-10-23 | $+5,015.62 | $117.345 | $+21,301.12 | $+26,316.74 | $400,000.00 |
| USOIL (repository ticker OIL) | $99.04 | Sell 10U at $102 | 2026-10-23 | $+2,988.69 | $103.45 | $+17,810.99 | $+20,799.68 | $400,000.00 |
| **Combined** | — | **Sell 20U total** | **2026-10-23 assumed** | **$+8,004.31** | — | **$+39,112.11** | **$+47,116.42** | **$800,000.00** |

The combined realized PnL is **$8,004.31**; the remaining open positions carry **$39,112.11** unrealized PnL at the Oct. 23 marks. Total modeled PnL is **$47,116.42**, or 4.7116% of the original $1,000,000 gross notional—not an account return.

## Session marks and PnL

For the open portion, PnL is `open gross notional × (EOD close ÷ entry price − 1)`. When an EOD mark first equals or exceeds its trim target, the model assumes the specified 10U sale occurred at the target price, realizes that tranche's PnL, and marks the remaining 40U at the session close. Available daily data are closes only: Oct. 23 is the first recorded EOD at/above either target, so the report assigns that modeled trigger session. It does **not** verify the intraday touch, fill time, or actual execution at the target.

| EOD date | Instrument | EOD close | Units sold cumulative | Units open | Realized PnL | Remaining unrealized PnL | Total PnL | Mark source |
|---|---|---:|---:|---:|---:|---:|---:|---|
| 2026-10-19 | BRENT | $110.840 | 0U | 50U | $+0.00 | $-2,567.05 | $-2,567.05 | User-provided BlackBull Markets Brent Cash EOD |
| 2026-10-20 | BRENT | $110.575 | 0U | 50U | $+0.00 | $-3,756.33 | $-3,756.33 | User-provided BlackBull Markets Brent Cash EOD |
| 2026-10-21 | BRENT | $111.075 | 0U | 50U | $+0.00 | $-1,512.40 | $-1,512.40 | User-provided BlackBull Markets Brent Cash EOD |
| 2026-10-22 | BRENT | $114.136 | 0U | 50U | $+0.00 | $+12,224.89 | $+12,224.89 | User-provided BlackBull Markets Brent Cash EOD |
| 2026-10-23 | BRENT | $117.345 | 10U | 40U | $+5,015.62 | $+21,301.12 | $+26,316.74 | User-provided BlackBull Markets Brent Cash EOD |
| 2026-10-19 | USOIL (repository ticker OIL) | $98.230 | 0U | 50U | $+0.00 | $-4,089.26 | $-4,089.26 | User-provided TradingView TVC:USOIL EOD |
| 2026-10-20 | USOIL (repository ticker OIL) | $98.170 | 0U | 50U | $+0.00 | $-4,392.16 | $-4,392.16 | User-provided TradingView TVC:USOIL EOD |
| 2026-10-21 | USOIL (repository ticker OIL) | $97.700 | 0U | 50U | $+0.00 | $-6,764.94 | $-6,764.94 | User-provided TradingView TVC:USOIL EOD |
| 2026-10-22 | USOIL (repository ticker OIL) | $99.090 | 0U | 50U | $+0.00 | $+252.42 | $+252.42 | User-provided TradingView TVC:USOIL EOD |
| 2026-10-23 | USOIL (repository ticker OIL) | $103.450 | 10U | 40U | $+2,988.69 | $+17,810.99 | $+20,799.68 | User-provided TradingView TVC:USOIL EOD |

![50U long BRENT and USOIL positions with assumed 10U trims](Charts/performance/24-weekend-oil-50u-positions.png)

Session-level export: [`weekend_oil_50u_positions_v1.csv`](data/weekend_oil_50u_positions_v1.csv).

## Source and scope notes

- Weekend source archive: [`Weekend Oil (10-17 & 10-18).zip`](Weekend%20Oil%20%2810-17%20%26%2010-18%29.zip); [upstream GitHub file](https://github.com/A44674928/Financial_Model_Records/blob/main/Weekend%20Oil%20(10-17%20%26%2010-18).zip) at commit `b5d6a9a0d9abb84d108c82f312b5298ecf9f437a`; SHA-256 `7419893a19fa1416a5dd238d48cacf17e22187da9b392b54ae50f5093b377c6f`.
- The archive contains two annotated IG **Weekend Oil – US Crude (CLN25)** screenshots dated Oct. 17 and Oct. 18, not a complete OHLC history and not separate BRENT/USOIL Monday-open price files. The screenshots are retained as source context, not transcribed as daily marks.
- The two Oct. 19 open prices, BRENT $111.412 and USOIL $99.04, and the trim levels/size were provided by the user. BRENT is stored internally as `BRENT`; USOIL maps to repository ticker `OIL`.
- Subsequent EOD values come from [`energy_provider_eod_marks_v1.csv`](data/energy_provider_eod_marks_v1.csv): BlackBull Markets Brent Cash for BRENT and TradingView TVC:USOIL for OIL. No new or external daily prices are inserted.
- The assumed target sale is not included in the core replay, THE ONE MODEL's 32-portfolio aggregate, or standard 10U energy strategy-comparison composites. This is a separate hypothetical position overlay, not a change to those model results.
- PnL excludes commissions, spread, slippage, financing, CFD contract multipliers/tracking differences, taxes, margin, and execution constraints. The percentage shown is measured against opening gross notional, not account equity.
