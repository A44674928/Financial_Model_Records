# Strategy and Sidecar Comparison

> **TradingView-only interim refresh — 2026-10-24.** Core comparisons use 31 supplied direct-price symbols plus the chart-directed 1U/DAY/DXY index-return sleeve integrated into each core variant; BTC/ETH are excluded pending recalibration. The energy add-on below uses the independently published 10U daily-buy schedule from the same TradingView benchmark. XRH0 includes five flagged carry-forward marks; see the benchmark coverage and session-mark files.

![Core models, both direction-following model sizes, and sidecar combinations](Charts/performance/20-strategy-sidecar-comparison.png)

Calculation detail for the core variants and daily lot rules: [`Model Calculation Guide.md`](Model%20Calculation%20Guide.md).

## Model rules and combination math

- **Core variants:** existing V1, V2, V3A, and V3B model replays from the main comparison.
- **Exponential ($500/EOD):** after a ticker first has a logged direction, add a new fixed **$500 notional** lot in its latest LONG/SHORT/REBUY direction each EOD. $500 does not compound.
- **Shared-direction force multiplier (1U/EOD):** one 1U tranche per symbol with a carried direction each priced EOD; close all prior lots at the EOD mark on any LONG/SHORT flip. This remains a separate alternative to the $500 model.
- **Variant-specific 1U/EOD force family:** four separate daily-addition replays apply V1, V2, V3A, or V3B position handling to the 1U schedule. Explicit EXIT/TAKE PROFIT records close open long lots at their logged prices in all four; the carried direction remains active, so the scheduled EOD addition still occurs. V1/V3A leave opposite-side lots open on direction changes. V2/V3B cover shorts on LONG/REBUY at the logged signal price; as in the core implementation, SHORT does not close open longs. A qualifying V3A/V3B compounded-short entry uses the preceding full-exit unit count for that event-day tranche only; subsequent carried days return to 1U additions.
- **Signal timing:** direction-bearing LONG/SHORT/REBUY events map to the first priced session on or after their log date; the last directional event for a ticker on that session selects the EOD addition direction. EXIT / TAKE PROFIT rows do not clear carried direction. No separate authorization feed exists.
- **Additive comparisons:** each core base already contains the 1U/DAY/DXY index-return sleeve. The comparison adds shared $500/1U alternatives and the 10U TradingView energy schedule; variant-specific force models are shown alone, with energy, and in all 16 core-variant × 1U-variant pairings plus energy. Matching and cross-variant combinations are included. Do not add the DXY 1U sleeve a second time, net positions/capital, duplicate chart-opened energy positions, or stack alternative force models or variant rules.
- Universe: all 31 directly price-covered TradingView core tickers plus DXY as an integrated index-return sleeve; BTC/ETH are pending recalibration, and EURUSD, JPYUSD, US10Y, and US30Y are outside this portfolio comparison.

## Standalone model and sidecar terminal comparison — Oct. 23, 2026

| Component/scenario | Terminal PnL | Cumulative notional added | Open notional |
|---|---:|---:|---:|
| Exponential — fixed $500/EOD | $+5,471.50 | $328,000.00 | $279,500.00 |
| Shared-direction force — 1U per EOD | $+109,429.96 | $6,560,000.00 | $5,590,000.00 |
| 10U TradingView energy daily-buy sidecar | $+500,808.26 | $5,500,000.00 | $5,500,000.00 |
| $500 model + 10U energy sidecar | $+506,279.76 | $5,828,000.00 | $5,779,500.00 |
| 1U model + 10U energy sidecar | $+610,238.22 | $12,060,000.00 | $11,090,000.00 |

The $500 model ends at **$+5,471.50** (realized $+4,342.56; unrealized $+1,128.94). The shared-direction 1U force model ends at **$+109,429.96** (realized $+86,851.11; unrealized $+22,578.85). With identical direction state and no tranche compounding, its PnL and exposure are 20× the $500 model before display rounding.

## Variant-specific 1U/EOD force models and energy combinations — terminal

The four separate 1U/EOD models apply V1, V2, V3A, or V3B exit/SAR/short-compounding behavior. The energy sidecar contributes only its daily-buy PnL and gross notional. The graph below covers all 16 core-variant × 1U-variant pairings; each panel fixes the core variant and plots all four 1U models. Matching pairings are labeled, while the cross-variant pairings expose alternative position-management combinations.

The generated CSV retains legacy `oil` suffixes for compatibility; these now refer to the 10U TradingView energy schedule. All composite PnL/notional figures are additive USD totals. Positions and capital are not netted, and energy chart-opened core positions are not duplicated in the sidecar.

![All core variant and 1U force variant pairings with energy sidecar](Charts/performance/21-force-variant-oil-comparison.png)

| 1U/EOD variant rule | Standalone force PnL | Cumulative notional added | Open notional |
|---|---:|---:|---:|
| Variant 1 — 1U Open | $+118,252.71 | $6,560,000.00 | $5,790,000.00 |
| Variant 2 — 1U SAR | $+116,972.32 | $6,560,000.00 | $5,590,000.00 |
| Variant 3A — Nu Open | $+139,155.83 | $6,650,000.00 | $5,880,000.00 |
| Variant 3B — Nu SAR | $+127,653.72 | $6,650,000.00 | $5,590,000.00 |

| 1U/EOD variant rule | Force model + energy PnL | Combined cumulative notional | Combined open notional |
|---|---:|---:|---:|
| Variant 1 — 1U Open + energy | $+619,060.97 | $12,060,000.00 | $11,290,000.00 |
| Variant 2 — 1U SAR + energy | $+617,780.58 | $12,060,000.00 | $11,090,000.00 |
| Variant 3A — Nu Open + energy | $+639,964.09 | $12,150,000.00 | $11,380,000.00 |
| Variant 3B — Nu SAR + energy | $+628,461.98 | $12,150,000.00 | $11,090,000.00 |

## All core + 1U force variant pairings + 10U energy schedule — terminal

### Core V1 — Variant 1 — 1U Open

Core PnL: **$+58,191.29**; energy sidecar PnL: **$+500,808.26**.

| 1U/EOD force variant | Pairing | Force PnL | Composite PnL | Gross cumulative notional | Gross open notional |
|---|---|---:|---:|---:|---:|
| Variant 1 — 1U Open | Matching | $+118,252.71 | $+677,252.26 | $13,225,000.00 | $12,305,000.00 |
| Variant 2 — 1U SAR | Cross-variant | $+116,972.32 | $+675,971.87 | $13,225,000.00 | $12,105,000.00 |
| Variant 3A — Nu Open | Cross-variant | $+139,155.83 | $+698,155.38 | $13,315,000.00 | $12,395,000.00 |
| Variant 3B — Nu SAR | Cross-variant | $+127,653.72 | $+686,653.27 | $13,315,000.00 | $12,105,000.00 |

### Core V2 — Variant 2 — 1U SAR

Core PnL: **$+55,348.09**; energy sidecar PnL: **$+500,808.26**.

| 1U/EOD force variant | Pairing | Force PnL | Composite PnL | Gross cumulative notional | Gross open notional |
|---|---|---:|---:|---:|---:|
| Variant 1 — 1U Open | Cross-variant | $+118,252.71 | $+674,409.06 | $13,225,000.00 | $12,255,000.00 |
| Variant 2 — 1U SAR | Matching | $+116,972.32 | $+673,128.67 | $13,225,000.00 | $12,055,000.00 |
| Variant 3A — Nu Open | Cross-variant | $+139,155.83 | $+695,312.18 | $13,315,000.00 | $12,345,000.00 |
| Variant 3B — Nu SAR | Cross-variant | $+127,653.72 | $+683,810.07 | $13,315,000.00 | $12,055,000.00 |

### Core V3A — Variant 3A — Nu Open

Core PnL: **$+79,474.78**; energy sidecar PnL: **$+500,808.26**.

| 1U/EOD force variant | Pairing | Force PnL | Composite PnL | Gross cumulative notional | Gross open notional |
|---|---|---:|---:|---:|---:|
| Variant 1 — 1U Open | Cross-variant | $+118,252.71 | $+698,535.75 | $13,315,000.00 | $12,395,000.00 |
| Variant 2 — 1U SAR | Cross-variant | $+116,972.32 | $+697,255.36 | $13,315,000.00 | $12,195,000.00 |
| Variant 3A — Nu Open | Matching | $+139,155.83 | $+719,438.87 | $13,405,000.00 | $12,485,000.00 |
| Variant 3B — Nu SAR | Cross-variant | $+127,653.72 | $+707,936.76 | $13,405,000.00 | $12,195,000.00 |

### Core V3B — Variant 3B — Nu SAR

Core PnL: **$+66,514.79**; energy sidecar PnL: **$+500,808.26**.

| 1U/EOD force variant | Pairing | Force PnL | Composite PnL | Gross cumulative notional | Gross open notional |
|---|---|---:|---:|---:|---:|
| Variant 1 — 1U Open | Cross-variant | $+118,252.71 | $+685,575.76 | $13,315,000.00 | $12,255,000.00 |
| Variant 2 — 1U SAR | Cross-variant | $+116,972.32 | $+684,295.37 | $13,315,000.00 | $12,055,000.00 |
| Variant 3A — Nu Open | Cross-variant | $+139,155.83 | $+706,478.88 | $13,405,000.00 | $12,345,000.00 |
| Variant 3B — Nu SAR | Matching | $+127,653.72 | $+694,976.77 | $13,405,000.00 | $12,055,000.00 |


## Percent gain across all 32 combinations

Percent gain is cumulative composite PnL divided by cumulative gross notional added, expressed as a percentage. It is a deployed-notional ratio, not an account return or capital-normalized ROI. The chart plots all 16 core × 1U variant pairings both without energy and with the 10U TradingView energy daily-buy sidecar (32 lines total). Solid lines omit energy; dashed lines include the energy sidecar. The top four terminal gain ratios are named in the legend; the other 28 pairings remain visible in gray.

![All 32 core and 1U variant pairings with and without energy, shown as percentage gain](Charts/performance/22-force-variant-oil-percent-gain.png)

| Rank | Pairing | 10U energy sidecar | Terminal gain on cumulative notional added |
|---:|---|---|---:|
| 1 | Core V3A + 1U V3A | Included | 5.37% |
| 2 | Core V3A + 1U V3B | Included | 5.28% |
| 3 | Core V3B + 1U V3A | Included | 5.27% |
| 4 | Core V3A + 1U V1 | Included | 5.25% |

## Core variants with add-ons — terminal PnL

| Core variant | Core only | + $500 model | + 1U force multiplier | + energy desk | + $500 and energy | + force multiplier and energy |
|---|---:|---:|---:|---:|---:|---:|
| Variant 1 — 1U Open | $+58,191.29 | $+63,662.79 | $+167,621.25 | $+558,999.55 | $+564,471.05 | $+668,429.51 |
| Variant 2 — 1U SAR | $+55,348.09 | $+60,819.59 | $+164,778.05 | $+556,156.35 | $+561,627.85 | $+665,586.31 |
| Variant 3A — Nu Open | $+79,474.78 | $+84,946.28 | $+188,904.74 | $+580,283.04 | $+585,754.54 | $+689,713.00 |
| Variant 3B — Nu SAR | $+66,514.79 | $+71,986.29 | $+175,944.75 | $+567,323.05 | $+572,794.55 | $+676,753.01 |

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
