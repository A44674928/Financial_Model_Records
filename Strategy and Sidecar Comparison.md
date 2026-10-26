# Strategy and Sidecar Comparison

> **TradingView-only interim refresh — 2026-10-24.** Core comparisons use 31 supplied direct-price symbols plus the chart-directed 1U/DAY/DXY index-return sleeve integrated into each core variant; BTC/ETH are excluded pending recalibration. The energy add-on below uses the independently published 10U daily-buy schedule from the same TradingView benchmark. XRH0 includes five flagged carry-forward marks; see the benchmark coverage and session-mark files.
> **Updated Part B source:** the revised user-provided archive corrects LLY's Oct. 20 close to `$1,283.66`, superseding the prior `$12,833.66` row; all strategy/core figures below use the revised mark.

![Core models, both direction-following model sizes, and sidecar combinations](Charts/performance/20-strategy-sidecar-comparison.png)

Calculation detail for the core variants and daily lot rules: [`Model Calculation Guide.md`](Model%20Calculation%20Guide.md).

## Model rules and combination math

- **Core variants:** existing V1, V2, V3A, and V3B model replays from the main comparison. The core logs also contain separate hypothetical 10U SHORT force-multiplier lots in BRENT at $117 and OIL at $102, modeled at the Oct. 23 target-level EOD trigger (not a verified intraday execution). Their explicit modeled exits are $114.627 BRENT and $100.74 OIL at 2026-10-25 20:35 MST, after the four earlier Oct. 25 replenishments and simultaneous with separate 35U BRENT/34U OIL LONG Weekend Oil buys; the buys count toward weekly supply, but the short closures do not. They raise post-close all-core oil long exposure from 65U BRENT + 66U OIL to 100U each (200U combined). The $115.792 BRENT/$101.74 OIL lots use the user-recalled 17:20–17:25 MST window, modeled at 17:22; the $114.80 BRENT/$101.00 OIL lot times are approximate around 20:00 MST per the user's recollection. These lot-specific exits override SAR only for the two tagged shorts; prices and timings are hypothetical model inputs, not verified executions. All these events are post-cutoff, so current terminal core metrics remain marked at Oct. 23. These short positions are part of core, not the energy sidecar.
- **Exponential ($500/EOD):** after a ticker first has a logged direction, add a new fixed **$500 notional** lot in its latest LONG/SHORT/REBUY direction each EOD. $500 does not compound.
- **Shared-direction force multiplier (1U/EOD):** one 1U tranche per symbol with a carried direction each priced EOD; close all prior lots at the EOD mark on any LONG/SHORT flip. This remains a separate alternative to the $500 model.
- **Variant-specific 1U/EOD force family:** four separate daily-addition replays apply V1, V2, V3A, or V3B position handling to the 1U schedule. Explicit EXIT/TAKE PROFIT records close open long lots at their logged prices in all four; the carried direction remains active, so the scheduled EOD addition still occurs. V1/V3A leave opposite-side lots open on direction changes. V2/V3B cover shorts on LONG/REBUY at the logged signal price; as in the core implementation, SHORT does not close open longs. A qualifying V3A/V3B compounded-short entry uses the preceding full-exit unit count for that event-day tranche only; subsequent carried days return to 1U additions.
- **Signal timing:** direction-bearing LONG/SHORT/REBUY events map to the first priced session on or after their log date; the last directional event for a ticker on that session selects the EOD addition direction. EXIT / TAKE PROFIT rows do not clear carried direction. No separate authorization feed exists.
- **Additive comparisons:** each core base already contains the 1U/DAY/DXY index-return sleeve. The comparison adds shared $500/1U alternatives and the 10U TradingView energy schedule; variant-specific force models are shown alone, with energy, and in all 16 core-variant × 1U-variant pairings plus energy. Matching and cross-variant combinations are included. Do not add the DXY 1U sleeve a second time, net positions/capital, duplicate chart-opened energy positions, or stack alternative force models or variant rules.
- Universe: all 31 directly price-covered TradingView core tickers plus DXY as an integrated index-return sleeve; BTC/ETH are pending recalibration, and EURUSD, JPYUSD, US10Y, and US30Y are outside this portfolio comparison.

## Standalone model and sidecar terminal comparison — Oct. 23, 2026

| Component/scenario | Terminal PnL | Cumulative notional added | Open notional |
|---|---:|---:|---:|
| Exponential — fixed $500/EOD | $+5,917.91 | $328,000.00 | $253,000.00 |
| Shared-direction force — 1U per EOD | $+118,358.22 | $6,560,000.00 | $5,060,000.00 |
| 10U TradingView energy daily-buy sidecar | $+500,808.26 | $5,500,000.00 | $5,500,000.00 |
| $500 model + 10U energy sidecar | $+506,726.17 | $5,828,000.00 | $5,753,000.00 |
| 1U model + 10U energy sidecar | $+619,166.48 | $12,060,000.00 | $10,560,000.00 |

The $500 model ends at **$+5,917.91** (realized $+6,846.60; unrealized $-928.69). The shared-direction 1U force model ends at **$+118,358.22** (realized $+136,931.93; unrealized $-18,573.72). With identical direction state and no tranche compounding, its PnL and exposure are 20× the $500 model before display rounding.

## Variant-specific 1U/EOD force models and energy combinations — terminal

The four separate 1U/EOD models apply V1, V2, V3A, or V3B exit/SAR/short-compounding behavior. The energy sidecar contributes only its daily-buy PnL and gross notional. The graph below covers all 16 core-variant × 1U-variant pairings; each panel fixes the core variant and plots all four 1U models. Matching pairings are labeled, while the cross-variant pairings expose alternative position-management combinations.

The generated CSV retains legacy `oil` suffixes for compatibility; these now refer to the 10U TradingView energy schedule. All composite PnL/notional figures are additive USD totals. Positions and capital are not netted, and energy chart-opened core positions are not duplicated in the sidecar.

![All core variant and 1U force variant pairings with energy sidecar](Charts/performance/21-force-variant-oil-comparison.png)

| 1U/EOD variant rule | Standalone force PnL | Cumulative notional added | Open notional |
|---|---:|---:|---:|
| Variant 1 — 1U Open | $+127,180.97 | $6,560,000.00 | $5,790,000.00 |
| Variant 2 — 1U SAR | $+125,900.58 | $6,560,000.00 | $5,590,000.00 |
| Variant 3A — Nu Open | $+148,084.09 | $6,650,000.00 | $5,880,000.00 |
| Variant 3B — Nu SAR | $+136,581.98 | $6,650,000.00 | $5,590,000.00 |

| 1U/EOD variant rule | Force model + energy PnL | Combined cumulative notional | Combined open notional |
|---|---:|---:|---:|
| Variant 1 — 1U Open + energy | $+627,989.23 | $12,060,000.00 | $11,290,000.00 |
| Variant 2 — 1U SAR + energy | $+626,708.84 | $12,060,000.00 | $11,090,000.00 |
| Variant 3A — Nu Open + energy | $+648,892.35 | $12,150,000.00 | $11,380,000.00 |
| Variant 3B — Nu SAR + energy | $+637,390.24 | $12,150,000.00 | $11,090,000.00 |

## All core + 1U force variant pairings + 10U energy schedule — terminal

### Core V1 — Variant 1 — 1U Open

Core PnL: **$+103,591.26**; energy sidecar PnL: **$+500,808.26**.

| 1U/EOD force variant | Pairing | Force PnL | Composite PnL | Gross cumulative notional | Gross open notional |
|---|---|---:|---:|---:|---:|
| Variant 1 — 1U Open | Matching | $+127,180.97 | $+731,580.49 | $14,425,000.00 | $13,305,000.00 |
| Variant 2 — 1U SAR | Cross-variant | $+125,900.58 | $+730,300.10 | $14,425,000.00 | $13,105,000.00 |
| Variant 3A — Nu Open | Cross-variant | $+148,084.09 | $+752,483.61 | $14,515,000.00 | $13,395,000.00 |
| Variant 3B — Nu SAR | Cross-variant | $+136,581.98 | $+740,981.50 | $14,515,000.00 | $13,105,000.00 |

### Core V2 — Variant 2 — 1U SAR

Core PnL: **$+100,748.06**; energy sidecar PnL: **$+500,808.26**.

| 1U/EOD force variant | Pairing | Force PnL | Composite PnL | Gross cumulative notional | Gross open notional |
|---|---|---:|---:|---:|---:|
| Variant 1 — 1U Open | Cross-variant | $+127,180.97 | $+728,737.29 | $14,425,000.00 | $13,255,000.00 |
| Variant 2 — 1U SAR | Matching | $+125,900.58 | $+727,456.90 | $14,425,000.00 | $13,055,000.00 |
| Variant 3A — Nu Open | Cross-variant | $+148,084.09 | $+749,640.41 | $14,515,000.00 | $13,345,000.00 |
| Variant 3B — Nu SAR | Cross-variant | $+136,581.98 | $+738,138.30 | $14,515,000.00 | $13,055,000.00 |

### Core V3A — Variant 3A — Nu Open

Core PnL: **$+124,874.75**; energy sidecar PnL: **$+500,808.26**.

| 1U/EOD force variant | Pairing | Force PnL | Composite PnL | Gross cumulative notional | Gross open notional |
|---|---|---:|---:|---:|---:|
| Variant 1 — 1U Open | Cross-variant | $+127,180.97 | $+752,863.98 | $14,515,000.00 | $13,395,000.00 |
| Variant 2 — 1U SAR | Cross-variant | $+125,900.58 | $+751,583.59 | $14,515,000.00 | $13,195,000.00 |
| Variant 3A — Nu Open | Matching | $+148,084.09 | $+773,767.10 | $14,605,000.00 | $13,485,000.00 |
| Variant 3B — Nu SAR | Cross-variant | $+136,581.98 | $+762,264.99 | $14,605,000.00 | $13,195,000.00 |

### Core V3B — Variant 3B — Nu SAR

Core PnL: **$+111,914.76**; energy sidecar PnL: **$+500,808.26**.

| 1U/EOD force variant | Pairing | Force PnL | Composite PnL | Gross cumulative notional | Gross open notional |
|---|---|---:|---:|---:|---:|
| Variant 1 — 1U Open | Cross-variant | $+127,180.97 | $+739,903.99 | $14,515,000.00 | $13,255,000.00 |
| Variant 2 — 1U SAR | Cross-variant | $+125,900.58 | $+738,623.60 | $14,515,000.00 | $13,055,000.00 |
| Variant 3A — Nu Open | Cross-variant | $+148,084.09 | $+760,807.11 | $14,605,000.00 | $13,345,000.00 |
| Variant 3B — Nu SAR | Matching | $+136,581.98 | $+749,305.00 | $14,605,000.00 | $13,055,000.00 |


## Percent gain across all 32 combinations

Percent gain is cumulative composite PnL divided by cumulative gross notional added, expressed as a percentage. It is a deployed-notional ratio, not an account return or capital-normalized ROI. The chart plots all 16 core × 1U variant pairings both without energy and with the 10U TradingView energy daily-buy sidecar (32 lines total). Solid lines omit energy; dashed lines include the energy sidecar. The top four terminal gain ratios are named in the legend; the other 28 pairings remain visible in gray.

![All 32 core and 1U variant pairings with and without energy, shown as percentage gain](Charts/performance/22-force-variant-oil-percent-gain.png)

| Rank | Pairing | 10U energy sidecar | Terminal gain on cumulative notional added |
|---:|---|---|---:|
| 1 | Core V3A + 1U V3A | Included | 5.30% |
| 2 | Core V3A + 1U V3B | Included | 5.22% |
| 3 | Core V3B + 1U V3A | Included | 5.21% |
| 4 | Core V3A + 1U V1 | Included | 5.19% |

## Core variants with add-ons — terminal PnL

| Core variant | Core only | + $500 model | + 1U force multiplier | + energy desk | + $500 and energy | + force multiplier and energy |
|---|---:|---:|---:|---:|---:|---:|
| Variant 1 — 1U Open | $+103,591.26 | $+109,509.17 | $+221,949.48 | $+604,399.52 | $+610,317.43 | $+722,757.74 |
| Variant 2 — 1U SAR | $+100,748.06 | $+106,665.97 | $+219,106.28 | $+601,556.32 | $+607,474.23 | $+719,914.54 |
| Variant 3A — Nu Open | $+124,874.75 | $+130,792.66 | $+243,232.97 | $+625,683.01 | $+631,600.92 | $+744,041.23 |
| Variant 3B — Nu SAR | $+111,914.76 | $+117,832.67 | $+230,272.98 | $+612,723.02 | $+618,640.93 | $+731,081.24 |

The standalone 10U TradingView energy schedule ends at **$+500,808.26** on **$5,500,000.00** cumulative daily-buy notional. Use the notional columns when comparing scale; these additive composites do not apply a common capital base.

## Data and output files

- Daily all-strategy PnL and exposure comparison: [`strategy_sidecar_comparison_daily_v1.csv`](data/strategy_sidecar_comparison_daily_v1.csv).
- Exponential $500 per-symbol EOD audit: [`exponential_eod_positions_v1.csv`](data/exponential_eod_positions_v1.csv).
- Shared-direction force model audit: [`force_multiplier_eod_positions_v1.csv`](data/force_multiplier_eod_positions_v1.csv).
- Variant-specific 1U EOD position audit: [`force_multiplier_variant_eod_positions_v1.csv`](data/force_multiplier_variant_eod_positions_v1.csv).
- Percent-gain chart for all 32 core/1U pairings with and without energy: [`22-force-variant-oil-percent-gain.png`](Charts/performance/22-force-variant-oil-percent-gain.png).
- Price source map: [`tradingview_benchmark_session_marks_20261024.csv`](data/tradingview_benchmark_session_marks_20261024.csv); sidecar schedule: [`tradingview_energy_sidecar_daily_20261024.csv`](data/tradingview_energy_sidecar_daily_20261024.csv).
- Core models: [`Model Performance Comparison.md`](Model%20Performance%20Comparison.md). Energy schedule and DXY sizing/audit alternatives: [`TradingView Energy and Currency Desk Sidecars.md`](TradingView%20Energy%20and%20Currency%20Desk%20Sidecars.md).

**Scope note:** new direction-following models and composites are unadjusted USD PnL comparisons; they are not included in the existing whole-portfolio DXY/yield account scenarios. This historical paper-trade replay is not a live system, risk forecast, or investment recommendation.
