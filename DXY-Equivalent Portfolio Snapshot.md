# Whole-Portfolio DXY Numeraire — Daily Comparison

The whole-book base PnL includes realized and open unrealized PnL (including FX and the separate US30Y trade marks), but excludes yield multipliers. The US10Y and US30Y blanket factors are applied to full account value only in the explicit scenarios below; neither yield is treated as a new $10,000 lot. DXY remains a separate whole-book numeraire, not a position.

[Open the interactive yield-multiplier scenario explorer](Whole%20Portfolio%20Yield%20Multiplier%20Explorer.html) to toggle between no factor, US10Y only, and US10Y compounded with US30Y.

![DXY Close vs. Whole-Portfolio PnL in Dollars](Charts/performance/17-dxy-close-vs-whole-portfolio-pnl-usd.png)

![Whole-portfolio unrealized PnL and USD/DXY returns](Charts/performance/16-whole-portfolio-dxy-vs-usd-pnl.png)

## Oct. 23 Terminal Results

| Variant | Capital basis | Open unrealized PnL (USD) | Realized PnL (USD) | Base PnL (no yield factors) | Base USD return | DXY-equivalent account value | DXY-numeraire return |
|---|---:|---:|---:|---:|---:|---:|---:|
| **Variant 1 — 1u Open** | $830,000 | $+73,391.74 | $+25,561.44 | $+98,953.18 | +11.508% | 9,064.77 DXY-eq units | +8.067% |
| **Variant 2 — 1u SAR** | $830,000 | $+42,850.29 | $+31,385.57 | $+74,235.86 | +8.530% | 8,822.68 DXY-eq units | +5.181% |
| **Variant 3A — Nu Open** | $920,000 | $+117,595.09 | $+25,561.44 | $+143,156.52 | +15.187% | 10,379.20 DXY-eq units | +11.633% |
| **Variant 3B — Nu SAR** | $920,000 | $+42,850.29 | $+42,552.27 | $+85,402.56 | +8.909% | 9,813.54 DXY-eq units | +5.549% |

## Toggleable blanket yield-multiplier scenarios

The base case is the portfolio account value without either yield multiplier. The US10Y case scales the full account value by its compounded US10Y excess-yield factor. The combined case multiplies that factor by the independently compounded US30Y excess-yield factor (`M10Y × M30Y`). In each case, the portfolio's starting capital is scaled as requested; scenario PnL is adjusted account value minus the original capital basis.

- US10Y baseline: `4.865%` from `2026-09-10`. US30Y baseline: `5.350%` from `2026-09-15` (first logged US30Y event).
- Each elapsed interval uses the prior session's yield close and actual calendar days / 365; Treasury non-session dates carry the latest available close. These are yield-derived scenario factors, not CPI inflation or Treasury total-return estimates.
- The separate US30Y SHORT/LONG trade PnL remains in the portfolio base as a marked position. The US30Y blanket factor is an additional whole-account scenario and does not create another $10,000 position.

| Variant | No multiplier: account / USD return / DXY return | US10Y: account / USD return / DXY return | US10Y × US30Y: account / USD return / DXY return |
|---|---:|---:|---:|
| **Variant 1 — 1u Open** | $925,513.26 / +11.508% / +8.067% | $925,811.11 / +11.544% / +8.102% | $925,945.81 / +11.560% / +8.118% |
| **Variant 2 — 1u SAR** | $900,795.94 / +8.530% / +5.181% | $901,085.84 / +8.565% / +5.215% | $901,216.94 / +8.580% / +5.230% |
| **Variant 3A — Nu Open** | $1,059,716.60 / +15.187% / +11.633% | $1,060,057.65 / +15.224% / +11.669% | $1,060,211.88 / +15.240% / +11.685% |
| **Variant 3B — Nu SAR** | $1,001,962.64 / +8.909% / +5.549% | $1,002,285.10 / +8.944% / +5.583% | $1,002,430.92 / +8.960% / +5.598% |

Interactive toggle and session-level scenario data: [`Whole Portfolio Yield Multiplier Explorer.html`](Whole Portfolio Yield Multiplier Explorer.html), [`whole_portfolio_yield_multiplier_scenarios.csv`](data/whole_portfolio_yield_multiplier_scenarios.csv), and [`whole_portfolio_yield_multiplier_summary.csv`](data/whole_portfolio_yield_multiplier_summary.csv).

## DXY and FX Basis

- DXY daily closes run from `2026-09-03` (`98.95`) through `2026-10-23` (`102.10`). The Oct. 23 close of 102.10 is used for the new endpoint; the prior Oct. 22 close of 102.22 remains preserved in the daily series and Oct. 22 audit file.
- **Input provenance:** DXY, EUR/USD, JPY/USD, US10Y, and US30Y use the existing local daily input files; their provider and candle/close convention are not independently verified. The source map and proxy limitations are in [`data/active_price_source_registry_v2.csv`](data/active_price_source_registry_v2.csv). These local inputs were retained, not externally refreshed.
- **Energy marks:** the core logged Brent/USOIL positions use exact user-provided BlackBull Brent Cash and TVC:USOIL EOD values from their first active-position dates; only pre-entry context remains on the Yahoo futures proxies. The separate daily 10-unit oil-desk accumulation is in [`Oil Desk EOD Accumulation Hypothetical.md`](Oil%20Desk%20EOD%20Accumulation%20Hypothetical.md) and is not included in the four account bases or yield-factor scenarios.
- FX, DXY, and yield series remain local and unverified; the user-provided energy marks are not treated as DXY/FX or yield data.
- The yield multiplier is a yield-spread scenario, not CPI inflation or a Treasury total-return estimate. A literal inflation-adjusted PnL series would require a specified CPI index and convention.
- EUR/USD PnL uses the uploaded daily close on its entry date as its cost basis: `2026-09-15` close `1.1024`. The original chart quote `1.15388` remains in the trade log as source evidence; the graph does not use it as the PnL basis, per your instruction.
- JPY/USD PnL uses the uploaded daily close on its entry date as its cost basis: `2026-09-07` close `0.007068`. The original chart quote `0.010160` remains in the trade log as source evidence; the graph does not use it as the PnL basis, per your instruction.
- DXY-equivalent account value is computed as `USD account value ÷ daily DXY close`; returns are normalized to the Sep. 3 DXY-equivalent starting value. The USD capital bases are the $830,000 / $920,000 portfolio amounts you specified.
- The DXY LONG log entry is retained as historical reference evidence, but this comparison does not treat it as an additional $10,000 position or add separate DXY-trade PnL.

## PnL, Multiplier, and Position Treatment

- Daily EUR/USD and JPY/USD unrealized PnL is calculated from the entry-date daily close, then marked to each uploaded daily close at $10,000 standard notional per position.
- The Sep. 15 US30Y SHORT and Oct. 23 US30Y LONG remain separate marked $10,000 positions; the Oct. 23 LONG uses its 5.311% log entry and Oct. 23 5.43% close, so it contributes only from Oct. 23. The US30Y blanket factor is separate from these position marks. The Oct. 23 ORCL LONG and fifth LCID LONG remain included.
- The old additive US10Y carry is retained in the daily CSV as a legacy reference only; it is not included in base PnL or any new scenario. The active whole-account adjustment is the compounded multiplier shown above. This prevents treating US10Y as a $10,000 position or layering the old carry on top of the new factor.
- US10Y positions are rate references, not independent yield-quote PnL rows. For Treasury holidays, the last supplied daily close is carried forward; the source date is retained in the daily export. DXY itself remains the whole-book numeraire.

Daily values and conversion factors: [`whole_portfolio_dxy_vs_usd_daily.csv`](data/whole_portfolio_dxy_vs_usd_daily.csv).

Terminal variant summary: [`whole_portfolio_dxy_vs_usd_summary.csv`](data/whole_portfolio_dxy_vs_usd_summary.csv).
