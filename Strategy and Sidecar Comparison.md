# Strategy and Sidecar Comparison

![Core models, both direction-following model sizes, and sidecar combinations](Charts/performance/20-strategy-sidecar-comparison.png)

Calculation detail for the core variants and daily lot rules: [`Model Calculation Guide.md`](Model%20Calculation%20Guide.md).

## Model rules and combination math

- **Core variants:** existing V1, V2, V3A, and V3B model replays from the main comparison.
- **Exponential ($500/EOD):** after a ticker first has a logged direction, add a new fixed **$500 notional** lot in its latest LONG/SHORT/REBUY direction each EOD. $500 does not compound.
- **Shared-direction force multiplier (1U/EOD):** one 1U tranche per symbol with a carried direction each priced EOD; close all prior lots at the EOD mark on any LONG/SHORT flip. This remains a separate alternative to the $500 model.
- **Variant-specific 1U/EOD force family:** four separate daily-addition replays apply V1, V2, V3A, or V3B position handling to the 1U schedule. Explicit EXIT/TAKE PROFIT records close open long lots at their logged prices in all four; the carried direction remains active, so the scheduled EOD addition still occurs. V1/V3A leave opposite-side lots open on direction changes. V2/V3B cover shorts on LONG/REBUY at the logged signal price; as in the core implementation, SHORT does not close open longs. A qualifying V3A/V3B compounded-short entry uses the preceding full-exit unit count for that event-day tranche only; subsequent carried days return to 1U additions.
- **Signal timing:** direction-bearing LONG/SHORT/REBUY events map to the first priced session on or after their log date; the last directional event for a ticker on that session selects the EOD addition direction. EXIT / TAKE PROFIT rows do not clear carried direction. No separate authorization feed exists.
- **Additive comparisons:** core models are shown with shared $500/1U add-ons and oil; variant-specific force models are shown alone, with oil, and in all 16 core-variant × 1U-variant pairings plus oil. Matching and cross-variant combinations are included. These are separately modeled PnL/notional sums: do not net positions or capital, duplicate core chart-opened energy positions in the oil sidecar, or stack alternative force models or variant rules.
- Universe: all 33 directly price-covered core tickers; DXY, EURUSD, JPYUSD, US10Y, and US30Y are outside this price-position comparison.

## Standalone model and sidecar terminal comparison — Oct. 23, 2026

| Component/scenario | Terminal PnL | Cumulative notional added | Open notional |
|---|---:|---:|---:|
| Exponential — fixed $500/EOD | $+21,118.86 | $364,000.00 | $315,500.00 |
| Shared-direction force — 1U per EOD | $+422,377.26 | $7,280,000.00 | $6,310,000.00 |
| Oil-desk daily-buy add-on | $+499,705.92 | $5,500,000.00 | $5,500,000.00 |
| $500 model + oil daily buys | $+520,824.78 | $5,864,000.00 | $5,815,500.00 |
| 1U model + oil daily buys | $+922,083.18 | $12,780,000.00 | $11,810,000.00 |

The $500 model ends at **$+21,118.86** (realized $+4,356.35; unrealized $+16,762.51). The shared-direction 1U force model ends at **$+422,377.26** (realized $+87,127.05; unrealized $+335,250.21). With identical direction state and no tranche compounding, its PnL and exposure are 20× the $500 model before display rounding.

## Variant-specific 1U/EOD force models and oil combinations — terminal

The four separate 1U/EOD models apply V1, V2, V3A, or V3B exit/SAR/short-compounding behavior. The oil sidecar contributes only its daily-buy PnL and gross notional. The graph below covers all 16 core-variant × 1U-variant pairings; each panel fixes the core variant and plots all four 1U models. Matching pairings are labeled, while the cross-variant pairings expose alternative position-management combinations.

All composite PnL/notional figures are additive USD totals. Positions and capital are not netted, and energy chart-opened core positions are not duplicated in the sidecar.

![All core variant and 1U force variant pairings with oil sidecar](Charts/performance/21-force-variant-oil-comparison.png)

| 1U/EOD variant rule | Standalone force PnL | Cumulative notional added | Open notional |
|---|---:|---:|---:|
| Variant 1 — 1U Open | $+537,937.28 | $7,280,000.00 | $6,510,000.00 |
| Variant 2 — 1U SAR | $+429,919.69 | $7,280,000.00 | $6,310,000.00 |
| Variant 3A — Nu Open | $+582,278.04 | $7,370,000.00 | $6,600,000.00 |
| Variant 3B — Nu SAR | $+440,601.08 | $7,370,000.00 | $6,310,000.00 |

| 1U/EOD variant rule | Force model + oil PnL | Combined cumulative notional | Combined open notional |
|---|---:|---:|---:|
| Variant 1 — 1U Open + oil | $+1,037,643.20 | $12,780,000.00 | $12,010,000.00 |
| Variant 2 — 1U SAR + oil | $+929,625.61 | $12,780,000.00 | $11,810,000.00 |
| Variant 3A — Nu Open + oil | $+1,081,983.96 | $12,870,000.00 | $12,100,000.00 |
| Variant 3B — Nu SAR + oil | $+940,307.00 | $12,870,000.00 | $11,810,000.00 |

## All core + 1U force variant pairings + oil — terminal

### Core V1 — Variant 1 — 1U Open

Core PnL: **$+99,599.67**; oil sidecar PnL: **$+499,705.92**.

| 1U/EOD force variant | Pairing | Force PnL | Composite PnL | Gross cumulative notional | Gross open notional |
|---|---|---:|---:|---:|---:|
| Variant 1 — 1U Open | Matching | $+537,937.28 | $+1,137,242.87 | $13,625,000.00 | $12,705,000.00 |
| Variant 2 — 1U SAR | Cross-variant | $+429,919.69 | $+1,029,225.28 | $13,625,000.00 | $12,505,000.00 |
| Variant 3A — Nu Open | Cross-variant | $+582,278.04 | $+1,181,583.63 | $13,715,000.00 | $12,795,000.00 |
| Variant 3B — Nu SAR | Cross-variant | $+440,601.08 | $+1,039,906.67 | $13,715,000.00 | $12,505,000.00 |

### Core V2 — Variant 2 — 1U SAR

Core PnL: **$+74,882.36**; oil sidecar PnL: **$+499,705.92**.

| 1U/EOD force variant | Pairing | Force PnL | Composite PnL | Gross cumulative notional | Gross open notional |
|---|---|---:|---:|---:|---:|
| Variant 1 — 1U Open | Cross-variant | $+537,937.28 | $+1,112,525.56 | $13,625,000.00 | $12,655,000.00 |
| Variant 2 — 1U SAR | Matching | $+429,919.69 | $+1,004,507.97 | $13,625,000.00 | $12,455,000.00 |
| Variant 3A — Nu Open | Cross-variant | $+582,278.04 | $+1,156,866.32 | $13,715,000.00 | $12,745,000.00 |
| Variant 3B — Nu SAR | Cross-variant | $+440,601.08 | $+1,015,189.36 | $13,715,000.00 | $12,455,000.00 |

### Core V3A — Variant 3A — Nu Open

Core PnL: **$+143,803.02**; oil sidecar PnL: **$+499,705.92**.

| 1U/EOD force variant | Pairing | Force PnL | Composite PnL | Gross cumulative notional | Gross open notional |
|---|---|---:|---:|---:|---:|
| Variant 1 — 1U Open | Cross-variant | $+537,937.28 | $+1,181,446.22 | $13,715,000.00 | $12,795,000.00 |
| Variant 2 — 1U SAR | Cross-variant | $+429,919.69 | $+1,073,428.63 | $13,715,000.00 | $12,595,000.00 |
| Variant 3A — Nu Open | Matching | $+582,278.04 | $+1,225,786.98 | $13,805,000.00 | $12,885,000.00 |
| Variant 3B — Nu SAR | Cross-variant | $+440,601.08 | $+1,084,110.02 | $13,805,000.00 | $12,595,000.00 |

### Core V3B — Variant 3B — Nu SAR

Core PnL: **$+86,049.06**; oil sidecar PnL: **$+499,705.92**.

| 1U/EOD force variant | Pairing | Force PnL | Composite PnL | Gross cumulative notional | Gross open notional |
|---|---|---:|---:|---:|---:|
| Variant 1 — 1U Open | Cross-variant | $+537,937.28 | $+1,123,692.26 | $13,715,000.00 | $12,655,000.00 |
| Variant 2 — 1U SAR | Cross-variant | $+429,919.69 | $+1,015,674.67 | $13,715,000.00 | $12,455,000.00 |
| Variant 3A — Nu Open | Cross-variant | $+582,278.04 | $+1,168,033.02 | $13,805,000.00 | $12,745,000.00 |
| Variant 3B — Nu SAR | Matching | $+440,601.08 | $+1,026,356.06 | $13,805,000.00 | $12,455,000.00 |


## Core variants with add-ons — terminal PnL

| Core variant | Core only | + $500 model | + 1U force multiplier | + oil desk | + $500 and oil | + force multiplier and oil |
|---|---:|---:|---:|---:|---:|---:|
| Variant 1 — 1U Open | $+99,599.67 | $+120,718.53 | $+521,976.93 | $+599,305.59 | $+620,424.45 | $+1,021,682.85 |
| Variant 2 — 1U SAR | $+74,882.36 | $+96,001.22 | $+497,259.62 | $+574,588.28 | $+595,707.14 | $+996,965.54 |
| Variant 3A — Nu Open | $+143,803.02 | $+164,921.88 | $+566,180.28 | $+643,508.94 | $+664,627.80 | $+1,065,886.20 |
| Variant 3B — Nu SAR | $+86,049.06 | $+107,167.92 | $+508,426.32 | $+585,754.98 | $+606,873.84 | $+1,008,132.24 |

The oil desk sidecar alone adds **$499,705.92** on $5.5M of daily-buy notional, so its scale can dominate the raw-PnL composite panels. Use the cumulative/open notional columns and the drawdown panel when comparing risk and scale; these composites do not apply a common capital base.

## Data and output files

- Daily all-strategy PnL and exposure comparison: [`strategy_sidecar_comparison_daily_v1.csv`](data/strategy_sidecar_comparison_daily_v1.csv).
- Exponential $500 per-symbol EOD audit: [`exponential_eod_positions_v1.csv`](data/exponential_eod_positions_v1.csv).
- Shared-direction force model audit: [`force_multiplier_eod_positions_v1.csv`](data/force_multiplier_eod_positions_v1.csv).
- Variant-specific 1U EOD position audit: [`force_multiplier_variant_eod_positions_v1.csv`](data/force_multiplier_variant_eod_positions_v1.csv).
- Price source map: [`active_price_source_registry_v2.csv`](data/active_price_source_registry_v2.csv); exact energy closes: [`energy_provider_eod_marks_v1.csv`](data/energy_provider_eod_marks_v1.csv).
- Core models: [`Model Performance Comparison.md`](Model%20Performance%20Comparison.md). Oil sidecar assumptions and source rows: [`Oil Desk EOD Accumulation Hypothetical.md`](Oil%20Desk%20EOD%20Accumulation%20Hypothetical.md).

**Scope note:** new direction-following models and composites are unadjusted USD PnL comparisons; they are not included in the existing whole-portfolio DXY/yield account scenarios. This historical paper-trade replay is not a live system, risk forecast, or investment recommendation.
