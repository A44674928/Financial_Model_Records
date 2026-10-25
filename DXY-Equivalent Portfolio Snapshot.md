# Whole-Portfolio DXY Numeraire — Daily Comparison

> **Historical view—not recalculated on the interim TradingView core (2026-10-24).** Values below retain the prior portfolio benchmark and local DXY/FX/yield inputs; do not present them as current TradingView-only model results. The current core includes the chart-directed 1U/DAY/DXY index-return sleeve; sizing alternatives and its audit are in [`TradingView Energy and Currency Desk Sidecars.md`](TradingView%20Energy%20and%20Currency%20Desk%20Sidecars.md). See the refreshed [`Model Performance Comparison.md`](Model%20Performance%20Comparison.md) and [`data/tradingview_benchmark_coverage_20261024.csv`](data/tradingview_benchmark_coverage_20261024.csv).

The whole-book base PnL includes realized and open unrealized PnL (including FX and the separate US30Y trade marks), but excludes yield multipliers. The US10Y and US30Y blanket factors are applied to full account value only in the explicit scenarios below; neither yield is treated as a new $10,000 lot. DXY remains a separate whole-book numeraire, not a position.

[Open the interactive yield-multiplier scenario explorer](Whole%20Portfolio%20Yield%20Multiplier%20Explorer.html) to toggle between no factor, US10Y only, and US10Y compounded with US30Y.

![DXY Close vs. Whole-Portfolio PnL in Dollars](Charts/performance/17-dxy-close-vs-whole-portfolio-pnl-usd.png)

![Whole-portfolio unrealized PnL and USD/DXY returns](Charts/performance/16-whole-portfolio-dxy-vs-usd-pnl.png)

## Oct. 23 Terminal Results

| Variant | Capital basis | Open unrealized PnL (USD) | Realized PnL (USD) | Base PnL (no yield factors) | Base USD return | DXY-equivalent account value | DXY-numeraire return |
|---|---:|---:|---:|---:|---:|---:|---:|
| **Variant 1 — 1U Open** | $830,000 | $+71,095.46 | $+33,565.74 | $+104,661.20 | +12.603% | 9,153.79 DXY-eq units | +9.129% |
| **Variant 2 — 1U SAR** | $830,000 | $+62,428.12 | $+39,389.88 | $+101,818.00 | +12.260% | 9,125.94 DXY-eq units | +8.797% |
| **Variant 3A — Nu Open** | $920,000 | $+92,378.95 | $+33,565.74 | $+125,944.69 | +13.683% | 10,243.74 DXY-eq units | +10.176% |
| **Variant 3B — Nu SAR** | $920,000 | $+62,428.12 | $+50,556.58 | $+112,984.71 | +12.275% | 10,116.80 DXY-eq units | +8.811% |

## Toggleable blanket yield-multiplier scenarios

The base case is the portfolio account value without either yield multiplier. The US10Y case scales the full account value by its compounded US10Y excess-yield factor. The combined case multiplies that factor by the independently compounded US30Y excess-yield factor (`M10Y × M30Y`). In each case, the portfolio's starting capital is scaled as requested; scenario PnL is adjusted account value minus the original capital basis.

- US10Y baseline: `4.865%` from `2026-09-10`. US30Y baseline: `5.350%` from `2026-09-15` (first logged US30Y event).
- Each elapsed interval uses the prior session's yield close and actual calendar days / 365; Treasury non-session dates carry the latest available close. These are yield-derived scenario factors, not CPI inflation or Treasury total-return estimates.
- The separate US30Y SHORT/LONG trade PnL remains in the portfolio base as a marked position. The US30Y blanket factor is an additional whole-account scenario and does not create another $10,000 position.

| Variant | No multiplier: account / USD return / DXY return | US10Y: account / USD return / DXY return | US10Y × US30Y: account / USD return / DXY return |
|---|---:|---:|---:|
| **Variant 1 — 1U Open** | $934,601.94 / +12.603% / +9.129% | $934,902.72 / +12.639% / +9.164% | $935,038.74 / +12.655% / +9.180% |
| **Variant 2 — 1U SAR** | $931,758.74 / +12.260% / +8.797% | $932,058.61 / +12.296% / +8.832% | $932,194.21 / +12.313% / +8.847% |
| **Variant 3A — Nu Open** | $1,045,885.42 / +13.683% / +10.176% | $1,046,222.02 / +13.720% / +10.211% | $1,046,374.24 / +13.736% / +10.227% |
| **Variant 3B — Nu SAR** | $1,032,925.44 / +12.275% / +8.811% | $1,033,257.87 / +12.311% / +8.846% | $1,033,408.19 / +12.327% / +8.861% |

Interactive toggle and session-level scenario data: [`Whole Portfolio Yield Multiplier Explorer.html`](Whole Portfolio Yield Multiplier Explorer.html), [`whole_portfolio_yield_multiplier_scenarios.csv`](data/whole_portfolio_yield_multiplier_scenarios.csv), and [`whole_portfolio_yield_multiplier_summary.csv`](data/whole_portfolio_yield_multiplier_summary.csv).

## DXY and FX Basis

- DXY daily closes run from `2026-09-03` (`98.95`) through `2026-10-23` (`102.10`). The Oct. 23 close of 102.10 is used for the new endpoint; the prior Oct. 22 close of 102.22 remains preserved in the daily series and Oct. 22 audit file.
- **Input provenance:** DXY, EUR/USD, JPY/USD, US10Y, and US30Y use the existing local daily input files; their provider and candle/close convention are not independently verified. The source map and proxy limitations are in [`data/active_price_source_registry_v3.csv`](data/active_price_source_registry_v3.csv). These local inputs were retained, not externally refreshed.
- **Energy marks:** this historical view's core logged Brent/USOIL positions and separate daily accumulation retain their prior benchmark and are not current TradingView results. The current standalone 0.05U/1U/10U TradingView energy schedule is in [`TradingView Energy and Currency Desk Sidecars.md`](TradingView%20Energy%20and%20Currency%20Desk%20Sidecars.md); it is not included in these historical account bases or yield-factor scenarios.
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
