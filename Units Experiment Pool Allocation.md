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
| BRENT allocation — 50% | $9,506,377,052.37 |
| OIL allocation — 50% | $9,506,377,052.37 |
| Residual cash below the $10,000 denomination | $14,104.74 |

## $200 LONG PORTFOLIO — balanced OIL/BRENT allocation

The remaining pool is split equally by dollar notional and modeled as long at the specified user-provided prices: BRENT **$115.00** and OIL/USOIL **$101.00**. Each ticker allocation is converted into $1,000,000,000 Large Units first, then $10,000 Small Units; sub-$10,000 balances remain cash.

| Ticker | Entry-price assumption | Dollar allocation | Large Units | Small Units | Residual cash | Quantity equivalent (not contracts/barrels) |
|---|---:|---:|---:|---:|---:|---:|
| BRENT | $115.00 | $9,506,377,052.37 | 9 | 50,637 | $7,052.37 | 82,664,148.28147826 |
| OIL (USOIL) | $101.00 | $9,506,377,052.37 | 9 | 50,637 | $7,052.37 | 94,122,545.07297030 |
| **Total** | — | **$19,012,754,104.74** | **18** | **101,274** | **$14,104.74** | — |

**Lock rule:** keep the $200 LONG PORTFOLIO locked until **both** supplied BRENT and OIL EOD marks reach **$200.00**. This is a scenario rule, not an automated order or an independently verified market trigger. The quantity equivalents are dollar allocations divided by the stated prices; they are **not** contract, barrel, share, or broker-order quantities because contract multipliers, execution quality, fees, financing, and market impact are unspecified.

CSV audits: [model-book deductions](data/units_experiment_model_costs_20261026.csv) and [balanced allocation](data/units_experiment_pool_allocation_20261026.csv). The winner scale factor is 27.201116019530× on cumulative gross additions; the pool deduction uses its scaled current open notional of $497,100,395.26.
