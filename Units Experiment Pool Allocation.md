# $20B Paper Portfolio — Units Experiment

> **User-estimated, hypothetical paper portfolio.** The $20,000,000,000 starting pool is not independently verified profit, cash, or account equity. No live orders or brokerage executions are represented.

## Historical record and two-stage process

The user describes this as a paper portfolio built over approximately the prior **45 days** through TradingView Paper Trading. The current GitHub core replay covers **37 regular-session marks from 2026-09-03 through 2026-10-26**; the user-reported 45-day TradingView history is maintained by manually porting records into this repository. The workflow has two stages: (1) manual paper trading and observation in TradingView; then (2) manual transcription/normalization of the activity into the GitHub trade ledger, price records, and model reports. The GitHub copy is the durable historical record after it is updated; it does not sync automatically and does not establish independently verified fills. TradingView account resets do not erase records already archived here.

## Model-capital deductions

For pool budgeting, “price” means **current open gross notional** as of the latest model snapshot, not cumulative historical turnover. Cumulative additions are displayed for context but are not deducted, because closed lots can recycle modeled capital. THE ONE MODEL and the 27.201116× WINNING MODEL are funded as separate books per the requested construction; the winner is selected from THE ONE MODEL’s 32-portfolio universe, so it repeats that model lineage by design.

| Model book | Current open gross notional | Historical cumulative additions (reference only) | Deducted from pool |
|---|---:|---:|---:|
| THE ONE MODEL — aggregate of 32 independent portfolios | $478,800,000.00 | $584,960,000.00 | $478,800,000.00 |
| THE WINNING MODEL — selected portfolio scaled 27.201116x | $497,100,395.26 | $584,960,000.00 | $497,100,395.26 |
| Fixed-$500/EOD direction-following alternative | $267,500.00 | $343,500.00 | $267,500.00 |
| Shared-direction 1U/EOD force alternative | $5,350,000.00 | $6,870,000.00 | $5,350,000.00 |
| Generic 10U/DAY TradingView energy sidecar | $5,700,000.00 | $5,700,000.00 | $5,700,000.00 |
| 0.05U/DAY DXY alternative | $18,000.00 | $18,000.00 | $18,000.00 |
| One-time chart-opened DXY position | $10,000.00 | $10,000.00 | $10,000.00 |
| **All selected model books** | — | — | **$987,245,895.26** |

Minor books are included only when separately maintained outside THE ONE/WINNING allocations: the fixed-$500/EOD alternative, shared-direction 1U/EOD force alternative, generic 10U energy schedule, 0.05U/DAY DXY alternative, and the separate one-time chart-opened DXY position. The integrated 1U/DAY DXY sleeve, THE ONE 10U/DAY DXY add-on, its variant-specific 1U/EOD components, and its 11U/DAY energy sleeves are already represented in THE ONE and are not charged again. Whole-portfolio DXY/yield views are historical comparison views, and the ATS/manual maximum-size reconciliation is an uncertain separate scenario with potential overlap; neither is charged as an additional active book.

| Pool bridge | Amount |
|---|---:|
| User-estimated starting pool | $20,000,000,000.00 |
| Less: selected model-book active gross notional | ($987,245,895.26) |
| **Remaining pool for the $200 LONG PORTFOLIO** | **$19,012,754,104.74** |
| BRENT allocation — 50%, using its reported entry basis | $9,506,377,052.37 |
| OIL allocation — 50%, using its reported entry basis | $9,506,377,052.37 |
| Residual cash below the $10,000 denomination | $14,104.74 |

## $200 LONG PORTFOLIO — balanced OIL/BRENT allocation

The $20B pool experiment's residual is split equally by dollar notional. Per your supplied entry data, the modeled BRENT leg uses **Sep. 23 at $102.315** and the OIL/USOIL leg uses **Sep. 22 at $89.89**. The year was not stated in your text; this run maps both dates to **2026** to align with the accompanying September 2026 TradingView/model context. These are user-reported historical entry-basis inputs, not independently verified fills. The Sep. 22 USOIL screenshot supports ticker context; its “Trade active / Target hit” note is not modeled as a fill or close event. The $200 label is the **price lock threshold**, not the funding amount; the experiment continues to use the $20B pool bridge and its hypothetical allocations. Each ticker allocation is converted into $1,000,000,000 Large Units first, then $10,000 Small Units; sub-$10,000 balances remain cash.

| Ticker | User-stated date / entry basis (2026 model alignment*) | Dollar allocation | Large Units | Small Units | Residual cash | Quantity equivalent (not contracts/barrels) | 2026-10-26 TradingView mark | Modeled unrealized mark change* |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| BRENT | Sep. 23 / $102.315 | $9,506,377,052.37 | 9 | 50,637 | $7,052.37 | 92,912,838.31666911 | $115.38 | $1,213,906,232.61 |
| OIL (USOIL) | Sep. 22 / $89.89 | $9,506,377,052.37 | 9 | 50,637 | $7,052.37 | 105,755,668.62131494 | $101.30 | $1,206,672,178.97 |
| **Total** | — | **$19,012,754,104.74** | **18** | **101,274** | **$14,104.74** | — | — | **$2,420,578,411.58** |

**Current lock status:** **LOCKED** as of supplied TradingView marks dated **2026-10-26**. Keep the portfolio locked until **both** supplied BRENT and OIL EOD marks reach **$200.00**; the current marks are BRENT $115.38 and OIL $101.30. The *modeled unrealized mark change* is a simple, linear price-equivalent calculation on the hypothetical residual-pool allocations; it is not actual account PnL, a verified fill, liquid/withdrawable cash, or an addition to pool deductions. The quantity equivalents are allocation dollars divided by the reported entry basis; they are **not** contract, barrel, share, or broker-order quantities because contract multipliers, execution quality, fees, financing, and market impact are unspecified.

CSV audits: [model-book deductions](data/units_experiment_model_costs_20261026.csv) and [balanced allocation](data/units_experiment_pool_allocation_20261026.csv). The winner scale factor is 27.201116019530× on cumulative gross additions; the pool deduction uses its scaled current open notional of $497,100,395.26.
