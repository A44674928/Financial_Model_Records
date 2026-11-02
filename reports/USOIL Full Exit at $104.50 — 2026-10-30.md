# USOIL Full Exit at $104.50 — 2026-10-30

> **User-directed exit.** All in-scope USOIL (internal ticker OIL) is recorded sold at **$104.50 on 2026-10-30**, execution time not supplied. The prior Private Fund USOIL close void is lifted and superseded. The price is user-reported, not an independently verified brokerage fill. PnL is price-only before costs, not audited.

The original screenshot close of **$102.14** and displayed PnL **$1,779,605,629.28** remain superseded source evidence, not booked amounts. See [original screenshot](../Archive/November_2026_Experiment_Oil_Closes_2026-10-29/IMG_1217.png). The [register](../data/usoil_sold_10450_20261030_v1.csv) and [builder](../scripts/build_usoil_10450_exit.py) give exact lot inputs.

## Per-book results

These are separate books with overlapping lots and non-interchangeable quantity conventions: **do not sum across books**. Oil v2 variants are alternatives, not additive.

| Book | Price-only PnL |
|---|---:|
| Private Fund / TradingView Paper Trading | $3,198,480,387.76 |
| ATS locked $200 LONG foundation / $20B Units Experiment pool | $1,891,607,645.29 |
| THE WINNING MODEL — 50U transferred from the oil foundation | $17,326.73 |
| Core paper-trade ledger replay | $48,210.64 |
| Oil portfolio v2 / November 2026 Oil Clean Sheet (per variant) | $28,339.45 |
| ATS and Manual Live Position Reconciliation | $33,163.92 |

## Lot detail

Each primary row counts once in its own book. The foundation component rows are detail of its combined row and are not added to it. Round each lot to cents before subtotalling. 1U = $10,000 entry notional; U PnL = units × $10,000 × (104.50 / entry − 1). Quantity-based PnL = quantity × (104.50 − entry).

### Private Fund / TradingView Paper Trading

| Lot | Quantity | Entry | PnL | Treatment |
|---|---:|---:|---:|---|
| PF-USOIL-CLOSE-20261029 | 601218118 platform-reported units | $99.18 | $3,198,480,387.76 | Primary |

### ATS locked $200 LONG foundation / $20B Units Experiment pool

| Lot | Quantity | Entry | PnL | Treatment |
|---|---:|---:|---:|---|
| Combined foundation | 204760619.11636445 modeled quantity equivalent | $95.26185814707322344409305211 | $1,891,607,645.29 | Primary |
| Original pool residual | 105755668.62131494 modeled quantity equivalent | $89.89 | $1,545,090,318.56 | Component only |
| Supplemental order remainder | 99004950.49504950 modeled quantity equivalent | $101.00 | $346,517,326.73 | Component only |

### THE WINNING MODEL — 50U transferred from the oil foundation

| Lot | Quantity | Entry | PnL | Treatment |
|---|---:|---:|---:|---|
| 50U transfer | 4950.49504950 modeled quantity equivalent | $101.00 | $17,326.73 | Primary |

### Core paper-trade ledger replay

| Lot | Quantity | Entry | PnL | Treatment |
|---|---:|---:|---:|---|
| 20260910 | 1 U ($10,000 model notional) | $97.32 | $737.77 | Primary |
| 20260922 | 1 U ($10,000 model notional) | $90.20 | $1,585.37 | Primary |
| 20260924 | 1 U ($10,000 model notional) | $93.74 | $1,147.86 | Primary |
| 20260929 | 1 U ($10,000 model notional) | $89.30 | $1,702.13 | Primary |
| 20261008 | 1 U ($10,000 model notional) | $90.60 | $1,534.22 | Primary |
| 20261019 | 1 U ($10,000 model notional) | $98.74 | $583.35 | Primary |
| 50U-residual | 40 U ($10,000 model notional) | $99.04 | $22,051.70 | Primary |
| manual-1722 | 10 U ($10,000 model notional) | $101.74 | $2,712.80 | Primary |
| manual-2000 | 10 U ($10,000 model notional) | $101.00 | $3,465.35 | Primary |
| approved-2035 | 34 U ($10,000 model notional) | $100.74 | $12,690.09 | Primary |

### Oil portfolio v2 / November 2026 Oil Clean Sheet

| Lot | Quantity | Entry | PnL | Treatment |
|---|---:|---:|---:|---|
| Oil v2 50U large lot | 50 U ($10,000 model notional) | $99.04 | $27,564.62 | Primary |
| Converted tranche 1 | 388.3495145631067961165048544 price-derived calculated units | $103 | $582.52 | Primary |
| Converted tranche 2 | 384.6153846153846153846153846 price-derived calculated units | $104 | $192.31 | Primary |

### ATS and Manual Live Position Reconciliation

| Lot | Quantity | Entry | PnL | Treatment |
|---|---:|---:|---:|---|
| fixed-50 | 50 U ($10,000 model notional) | $101.00 | $17,326.73 | Primary |
| order-10 | 10 U ($10,000 model notional) | $100.96 | $3,506.34 | Primary |
| reported-17 | 17 U ($10,000 model notional) | $100.85 | $6,152.70 | Primary |
| manual-1722 | 10 U ($10,000 model notional) | $101.74 | $2,712.80 | Primary |
| manual-2000 | 10 U ($10,000 model notional) | $101.00 | $3,465.35 | Primary |

## Scope and overlap

The 100U core exit includes six 1U lots, a 40U remainder of the tagged 50U, two manual 10U lots, and the 34U approved-order long retained in the core replay. The October 23 10U trim, the covered short and the 50U mirror already sold at $102.71 are **not sold again**.

The ATS/manual 97U comprises 50U @ $101, 10U @ $100.96, 17U @ $100.85 and two manual 10U lots. Its 50U source lot was transferred to THE WINNING MODEL and is not another independent holding; its manual replenishments overlap the core. The core 40U and Oil v2 50U come from the same source, with Oil v2 retaining the full lot due to its earlier cutoff. The Winner allocation is carved out of the supplemental foundation leg. The foundation combined row comprises its two component legs; the $104.50 exit supersedes the earlier $101.50–$103.40 sale-price bands, which remain historical evidence.

Oil v2 includes a 50U lot and two $40,000 converted clean-sheet tranches. The conversion is modeled, not a verified fill. The six original small OIL lots are represented in the core book, while the clean sheet treats the small-unit pool as converted; these views are not additive.

The Under-Duress overlay and 10U/20U/30U/40U sensitivities remain unchanged. The 34U core long is a legacy core-replay attribution; scenario-dependent residuals are excluded, as in the BRENT treatment. Earlier valuation marks are historical references, not post-exit valuations. No new EOD marks or general model recomputation is authorized.

This user-reported post-cutoff exit is recorded under `USER_DIRECTED_USOIL_EXIT_SCOPED_EXCEPTION_20261030`. Execution time is unknown; 13:00 MST in the trade log is only an ordering placeholder. Fees, financing, taxes, multipliers and slippage are excluded. No reconciled cash balance or audited NAV is asserted. The Private Fund carry-in is an earlier oil-exit estimate that may overlap these reported exits; any double counting is unresolved.
