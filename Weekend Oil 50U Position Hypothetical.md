# Weekend Oil 50U Position Hypothetical — Core-Integrated Attribution

> **Hypothetical educational mark-to-market only.** These tagged entries and assumed partial exits are modeled paper trades, not broker executions, verified account returns, or recommendations. Costs, financing, slippage, and liquidation are not modeled.

> **Core scope:** The two new 50U entries and their 10U target trims are integrated in all four core variants and flow through their downstream model outputs. This report isolates the new lots for attribution; it is **not an additional overlay** and must not be added again to core or aggregate results. The pre-existing Oct. 19 1U BRENT and 1U OIL core lots remain separate and untouched by these trims.

## Position and trim assumptions

The user specified a **50U LONG** position each in BRENT and USOIL at the **2026-10-19 market open**, with entry marks of $111.412 and $99.04 respectively. The thesis instruction is modeled as selling **10U of BRENT at $117** and **10U of USOIL at $102**, leaving **40U open in each new lot** after the assumed trims. Each ticker also retains its separate original 1U core lot. At $10,000 notional per unit, the new entries open $1,000,000 total gross notional; $200,000 of unit-basis gross notional is trimmed and $800,000 remains open in the new lots.
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

![50U long BRENT and USOIL positions with assumed 10U trims](Charts/CLN25/Weekend%20Oil/24-weekend-oil-50u-positions.png)

Session-level export: [`weekend_oil_50u_positions_v1.csv`](data/weekend_oil_50u_positions_v1.csv).

## Separate force-multiplier short lots (outside this long-lot attribution)

At the user's direction, separate hypothetical 10U SHORT lots were added on 2026-10-23 at the respective $117 BRENT and $102 USOIL target levels, in addition to the partial long trims and remaining longs. These target-level EOD trigger prices are model assumptions, not verified intraday touches or fills. The shorts are not included in this report's long-only attribution CSV or chart. Their explicit hypothetical modeled exits are $114.627 BRENT and $100.74 USOIL on 2026-10-25 at 20:35 MST, after the four earlier Oct. 25 LONG replenishments and simultaneously with separate 35U BRENT and 34U OIL Weekend Oil LONG buys. The buys are distinct from the tagged 10U SHORT closures; only the buy lots count toward weekly buy supply. These lot-specific closes override SAR auto-close only for these two tagged shorts; prices/time are modeled, not verified brokerage executions. The exits are after the Oct. 23 cutoff and do not affect this report's long-only attribution.

## Subsequent manual replenishment entries (outside this attribution window)

The user added four manual LONG replenishment entries after the earlier 10U target trims, all on Oct. 25: 10U USOIL at $101.74 and 10U BRENT at $115.792 use the user-recalled 17:20–17:25 MST window, modeled at a 17:22 midpoint; the additional 10U USOIL at $101.00 and 10U BRENT at $114.80 use an approximate 20:00 MST time per the user's recollection. Both times are modeled ordering assumptions, not verified transaction times. These are separate new lots; all fall after this report's final 2026-10-23 EOD mark and are not included in this attribution CSV or chart. The supplied prices remain the modeled entry prices; no later EOD marks or new exit targets were supplied, so no PnL is modeled for these entries here. Separately, the user specified additional Weekend Oil LONG buys simultaneous with the modeled short closes at 20:35 MST: 35U BRENT at $114.627 and 34U USOIL (internal ticker OIL) at $100.74. These distinct buy lots add 69U ($690,000 fixed-notional) to the post-cutoff long campaign and count toward weekly buy supply; the separate 10U short closures do not count toward that supply. The Weekend Oil tagged long campaign is then 95U BRENT (40U residual + 20U earlier replenishments + 35U buy) and 94U OIL (40U residual + 20U earlier replenishments + 34U buy). Including other logged core oil longs, and assuming the tagged shorts are closed, all-core long exposure reaches 100U per ticker (200U combined, $2,000,000 fixed-unit notional). They are not part of this report’s original 50U-only attribution CSV/chart or the existing residual-plus-replenishment basis-credit scope; they are hypothetical model inputs, not verified fills, and remain unmarked after the Oct. 23 cutoff.

## Source and scope notes

- Weekend source archive: [`Weekend Oil (10-17 & 10-18).zip`](Weekend%20Oil%20%2810-17%20%26%2010-18%29.zip); [upstream GitHub file](https://github.com/A44674928/Financial_Model_Records/blob/main/Weekend%20Oil%20(10-17%20%26%2010-18).zip) at commit `b5d6a9a0d9abb84d108c82f312b5298ecf9f437a`; SHA-256 `7419893a19fa1416a5dd238d48cacf17e22187da9b392b54ae50f5093b377c6f`.
- The archive contains two annotated IG **Weekend Oil – US Crude (CLN25)** screenshots dated Oct. 17 and Oct. 18, not a complete OHLC history and not separate BRENT/USOIL Monday-open price files. The screenshots are retained as source context, not transcribed as daily marks.
- The two Oct. 19 open prices, BRENT $111.412 and USOIL $99.04, and the trim levels/size were provided by the user. BRENT is stored internally as `BRENT`; USOIL maps to repository ticker `OIL`.
- Subsequent EOD values come from [`energy_provider_eod_marks_v1.csv`](data/energy_provider_eod_marks_v1.csv): BlackBull Markets Brent Cash for BRENT and TradingView TVC:USOIL for OIL. No new or external daily prices are inserted.
- The tagged entries/trim are recorded in [`trades/BRENT.txt`](trades/BRENT.txt) and [`trades/OIL.txt`](trades/OIL.txt), integrated in all four core variants, and therefore flow once through downstream core-based outputs, including THE ONE MODEL's 32-book aggregate. This document and CSV are a lot-level attribution only, not a second position allocation.
- The first recorded EOD marks at/above the target are dated 2026-10-23. The daily-close source cannot establish an intraday touch or actual fill; the target execution is an explicit model assumption.
- PnL excludes commissions, spread, slippage, financing, CFD contract multipliers/tracking differences, taxes, margin, and execution constraints. The percentage shown is measured against opening gross notional, not account equity.
