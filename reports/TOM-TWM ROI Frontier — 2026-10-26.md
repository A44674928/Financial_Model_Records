# TOM / TWM ROI Frontier — 2026-10-26

**Purpose:** measure whether the current DXY sleeve and other TOM/TWM components dilute the historical percentage return, then show the highest-return carve-out supported by the available supplied-mark data.

**Data window:** 2026-09-03 through 2026-10-26 (37 model sessions), except where a later-starting sleeve has fewer active sessions. Valuation marks are TradingView-only. These are hypothetical, mark-to-market model results—not verified executions, forecasts, or investment advice.

## Bottom line

The **highest auditable ticker-level PnL / gross additions ratio found across the current core ticker, variant-force, and sidecar records** is **23.5066%** for an **LMT-only core book**, with DXY, all other tickers, energy, and the 1U/EOD force book carved out. It contributes **$9,402.64** modeled PnL on **$40,000** gross additions and a **$40,000** maximum open-notional base. All four core variants have the same LMT lots and score in this sample. LMT first becomes active on supplied session marks on **2026-10-05**; all four 1U lots remain open at the Oct. 26 cutoff, so this is a roughly 16-session active holding window inside the 37-session comparison period.

Scaled arithmetically to a $1,000,000 gross-open base (25× the observed LMT book), this is **$235,066.03** terminal modeled PnL over the same historical window, with a scaled maximum peak-to-trough drawdown of **$11,698.51** (1.1699% of the assumed funded base). This is the literal maximum historical carve-out we found among the comparable per-ticker core and sidecar records—not a full TOM/TWM model, not a diversified book, and not evidence that LMT will keep leading. It is also an ex-post ticker selection from the same mark window, excludes costs and capacity effects, and materially concentrates the portfolio in one stock.

The highest **isolated energy-sidecar** ratio is **7.6321%** for the 11U/DAY BRENT-only buy sleeve, from **2026-09-23 through 2026-10-26 (24 active marks)**. It produced **$201,488.22** predominantly unrealized PnL on **$2,640,000** gross additions/open notional; scaled to $1M, that is **$76,321.30** PnL and **$17,620.87** historical maximum drawdown. It is still a concentrated, retrospectively selected overlay, not a full model.

If the requirement is to retain a full 37-session core-plus-force model, the best tested carve-out is **V3A Core + V3A-specific 1U/EOD + 11U/DAY energy, with the entire combined 11U/DAY DXY sleeve removed**. It returns **4.0799% PnL/additions** and **5.0004% PnL / maximum fully funded gross open notional**. That is the cleaner full-model comparison; the LMT-only and BRENT-only results are aggressive single-sleeve ceilings, not like-for-like replacements.

## Keep the percentage denominators separate

- **PnL / cumulative gross additions** is the model's deployed-notional ratio. Additions can represent repeated/reused capital; it is not an account return.
- **PnL / maximum gross open notional** is the fully funded cash/debit comparison used here for all-cash versions. Gross open notional is used as the simplified funded-capital base; no leverage or borrowing is assumed.
- All displayed results are over the stated historical interval, are not annualized, and are before trading frictions. Sidecar PnL is marked to the supplied TradingView closes; it is not assumed realized.

## Maximum historical single-ticker carve-out: LMT core only

The current core ticker ledger permits a consistent per-ticker deployed-notional ratio: `terminal ticker PnL / (units deployed × $10,000 per 1U)`. I screened all tracked direct-price core tickers in each of V1, V2, V3A, and V3B. **LMT is the highest in every variant at 23.5066%**, with the same four long 1U lots and no model-variant close/reversal difference in this window. The corresponding additions and maximum open notional are both $40,000; the $9,402.64 PnL is the model's realized-plus-unrealized terminal contribution.

| LMT-only core view | Historical result | $1M arithmetic scale |
|---|---:|---:|
| Active supplied-mark window | 2026-10-05–2026-10-26 (16 sessions) | same window |
| Gross additions | $40,000.00 | $1,000,000.00 |
| Maximum gross open / assumed funded base | $40,000.00 | $1,000,000.00 |
| Terminal modeled PnL | $9,402.64 | **$235,066.03** |
| PnL / additions | **23.5066%** | **23.5066%** |
| PnL / fully funded max-open base | **23.5066%** | **23.5066%** |
| Historical max peak-to-trough drawdown | $467.94 | $11,698.51 |
| Drawdown / funded base | 1.1699% | 1.1699% |

The PnL curve's peak-to-trough mark-to-market drawdown was $467.94 (Oct. 12 peak to Oct. 13 trough) before scaling. The one-ticker result is an *ex-post* screen, and its active holding window is much shorter than the full comparison interval. A 25× size increase is mathematical scaling only; execution capacity, concentration, and real-world fills are not established by this replay. `model_performance_tickers.csv` records terminal ticker PnL and deployed units; the core lot replay supplies the daily LMT path used for maximum exposure and drawdown.

For context, among the separate daily-buy sidecars, LMT core-only leads BRENT-only (7.6321%), OIL-only (6.1551%), and the force-only single-ticker paths (highest observed 18.2827% on LMT). Combining additional positive-notional sleeves with lower ratios cannot increase the ratio above the best sleeve: the combined PnL/additions ratio is an additions-weighted average.

## What happens when DXY is carved out

DXY is **positive in dollars** in this sample, but the combined sleeve has lower modeled return per dollar of additions than the non-DXY TOM book. Thus it raises absolute PnL while diluting the percentage ratio; this is not evidence that DXY is intrinsically a bad hedge or that its exposure should be removed in other windows.

| Construction | Sessions | Modeled PnL | Gross additions | Max/terminal gross open | PnL / additions | PnL / funded max open |
|---|---:|---:|---:|---:|---:|---:|
| TOM native aggregate: all 32 independent members, current sidecars | 37 | $16,457,691.52 | $584,960,000.00 | $478,800,000.00 | **2.8135%** | **3.4373%** |
| TOM counterfactual: all 32 members, strip combined 11U/DAY DXY, retain each member's current energy state | 37 | $15,256,034.98 | $458,240,000.00 | $352,080,000.00 | **3.3293%** | **4.3331%** |
| Current ex-post best member, full V3A/V3A + 11U energy + DXY | 37 | $753,361.68 | $21,505,000.00 | $18,275,000.00 | **3.5032%** | **4.1224%** |
| Counterfactual V3A/V3A + 11U energy, no combined DXY | 37 | $715,809.91 | $17,545,000.00 | $14,315,000.00 | **4.0799%** | **5.0004%** |

For the 32-book DXY-free case, the supplied daily file reports the extra 10U DXY sleeve separately; the integrated core 1U/DAY DXY sleeve is 1/10 of the same schedule under the existing model construction. The carve-out therefore subtracts **1.1× the recorded 10U DXY PnL, additions, and open notional** from each member. It removes about **$1.202M** modeled PnL and **$126.72M** gross additions from the native TOM sum. The sleeve itself works out to about **0.9483% PnL/additions**. Figures are recomputed from rounded daily source columns, so aggregate cent-level differences from the summary's independently rounded DXY totals are immaterial.

Screening the 32 members after this same DXY removal:

- Best with the 11U energy sidecar: **V3A core + V3A force**, 4.0799% PnL/additions.
- Best without the extra energy sidecar: **V3A core + V3A force**, 2.5800% PnL/additions.
- Thus energy raises the best full-model ratio in this window; the overall TOM 32-member aggregate still dilutes any one-book result because all 32 are summed as separately funded books.

### Normalized $1M full-model view

The DXY-free V3A/V3A + 11U-energy counterfactual has $14.315M maximum gross open notional on Oct. 26. Uniformly scaling it to a $1M fully funded open-notional base gives:

| PnL | Gross additions | Max gross open / assumed funded base | PnL / additions | PnL / funded base | Scaled max drawdown |
|---:|---:|---:|---:|---:|---:|
| $50,004.19 | $1,225,637.44 | $1,000,000.00 | 4.0799% | **5.0004%** | $7,373.09 |

This is an analytical counterfactual, not a change to the official TOM winner or TWM_1M_MAX definition.

## Sidecar-only ceiling

The 11U/DAY energy file has ticker-separated long daily-buy schedules. The numbers below use each sleeve's supplied active marks only; no prices are backfilled before the first supplied active mark.

| Isolated sleeve | Active-mark window | Modeled terminal PnL | Gross additions = open notional | PnL / additions and funded open | Max drawdown | Drawdown / open |
|---|---|---:|---:|---:|---:|---:|
| **BRENT only — highest observed ratio** | 2026-09-23–2026-10-26 (24) | $201,488.22 | $2,640,000.00 | **7.6321%** | $46,519.10 | 1.7621% |
| OIL only | 2026-09-10–2026-10-26 (33) | $223,430.87 | $3,630,000.00 | 6.1551% | $141,993.38 | 3.9117% |
| BRENT + OIL | component start dates differ | $424,919.09 | $6,270,000.00 | 6.7770% | — | — |

**BRENT-only scaled to $1M open notional:** multiply all sleeve values by $1,000,000 / $2,640,000 = **0.378787879×**. That yields **$76,321.30 PnL**, **$1,000,000 gross additions/open notional**, and **$17,620.87 historical max drawdown**; both percentage measures remain **7.6321%** because this sleeve's daily buys remain open and additions equal terminal open notional.

The result screens higher than the combined energy sleeve because BRENT's observed ratio exceeds OIL's in this particular sample. Selecting BRENT after reviewing both same-period results is a further source of selection bias. The sidecar is a concentrated, buy-only overlay with no modeled exit/risk-control rule; it should be treated as an experimental candidate, not adopted as a portfolio recommendation.

## TWM comparison and practical frontier

| Existing or calculated view | PnL / additions | PnL / $1M funded gross-open base | Interpretation |
|---|---:|---:|---|
| TWM_1M_FULL: V3A/V3A + 11U energy + combined DXY | 3.5032% | 4.1224% | Full current winner construction |
| TWM_1M_LIGHT: keeps chart DXY, removes 10U DXY add-on and energy sidecar | 2.5295% | 3.5015% | Not a no-DXY view; chart DXY remains |
| TWM_1M_MAX: no DXY + 10U energy | 3.9893% | 4.9267% | Existing defined MAX replay; do not relabel it |
| DXY-free V3A/V3A + **11U** energy (calculated above) | **4.0799%** | **5.0004%** | New 11U counterfactual, not official MAX |
| LMT-only core book, $1M scaled | **23.5066%** | **23.5066%** | Highest observed ticker ROI; 16 active sessions, one-stock concentration |
| BRENT-only 11U/DAY sidecar, $1M scaled | **7.6321%** | **7.6321%** | Highest energy-sleeve ROI; partial-window, concentrated, not a full model |

## Proposed research answer

If the objective is **maximum historical percentage**, the literal answer is: **test the isolated LMT core-only book** as the highest-return challenger, with DXY-free V3A/V3A + 11U energy retained as the full-model control and BRENT-only as the sidecar challenger. Do **not** rewrite the existing TWM/TOM results or winner record based on this same-window screen.

Before treating LMT-only as a real contender, freeze it and evaluate it on future supplied TradingView marks. Include spreads/costs, realized-vs-unrealized reporting, drawdown and single-name concentration limits, and a predeclared ticker-selection rule. A further same-period comparison of all assets is not independent validation. The displayed 23.51% is a historical mark-based result, not a forecast or expected future return.

## Sources and calculation

- [TOM / TWM 1K–10K ROI Design Sheet — 2026-10-26](TOM-TWM%201K-10K%20ROI%20Design%20Sheet%20%E2%80%94%202026-10-26.md) — $1K/$10K implementations and explicit V3A core-only choices.
- [`data/model_performance_tickers.csv`](../data/model_performance_tickers.csv) and [`data/core_portfolio_asset_breakdown_20261026.csv`](../data/core_portfolio_asset_breakdown_20261026.csv): terminal core ticker PnL and deployed units / open exposure. Core 1U additions are units deployed × $10,000.
- [`data/force_multiplier_variant_eod_positions_v1.csv`](../data/force_multiplier_variant_eod_positions_v1.csv) plus the existing strategy-comparison builder's realized-lot output: ticker-separated variant-force additions and mark-to-market paths used to check the force-only ceiling.
- [`data/the_one_model_split_portfolios_v1.csv`](../data/the_one_model_split_portfolios_v1.csv) and [`data/the_one_model_split_portfolios_v1_summary.json`](../data/the_one_model_split_portfolios_v1_summary.json): daily 32-book portfolios, independent sidecar columns, and published native summary.
- [`data/the_one_model_energy_11u_sidecar_daily_v1.csv`](../data/the_one_model_energy_11u_sidecar_daily_v1.csv): ticker-separated BRENT/OIL daily-buy PnL, additions, and TradingView mark flags.
- [`data/the_one_model_vs_winning_model_v1_summary.json`](../data/the_one_model_vs_winning_model_v1_summary.json): existing TWM_1M_FULL, TWM_1M_LIGHT, and TWM_1M_MAX scale views.
- Ratios are terminal modeled PnL divided by cumulative gross additions, or separately divided by maximum gross open notional as the assumed fully funded cash base. The DXY-free rows are counterfactual arithmetic carve-outs from supplied daily series, not a rerun of user events and not verified fills.
