# Strategy and Sidecar Comparison

![Core models, both direction-following model sizes, and sidecar combinations](Charts/performance/20-strategy-sidecar-comparison.png)

## Model rules and combination math

- **Core variants:** existing V1, V2, V3A, and V3B model replays from the main comparison.
- **Exponential ($500/EOD):** after a ticker first has a logged direction, add a new fixed **$500 notional** lot in its latest LONG/SHORT/REBUY direction each EOD. $500 does not compound.
- **Force multiplier ($10,000/EOD):** same direction state, EOD additions, and close/reverse rule, but each new tranche is **1 unit = $10,000 notional**. It is an alternative 20× sizing of the $500 model—not an extra tranche stacked on top of it.
- **Direction and reversal:** carry the latest direction-bearing entry tag in `trades/*.txt`; REBUY is LONG. On a direction change, close all prior opposite-direction lots at that EOD close before adding the new tranche. EXIT / TAKE PROFIT events do not clear the direction. Weekend/holiday signals apply at the first priced EOD on or after the event date. The repository has no separate authorization feed.
- **Oil-desk sidecar:** adds only its daily-buy lots to composites. Its chart-opened maintenance positions are already in each core replay and are not counted twice.
- **Composite lines:** each core model is compared with each sizing variant, oil buys, and the two valid model-plus-oil combinations. The two direction-following sizes are alternatives and are never summed together. Composites are additive USD PnL, not capital-normalized account simulations.
- Universe: all 33 directly price-covered core tickers; DXY, EURUSD, JPYUSD, US10Y, and US30Y are outside this price-position comparison.

## Standalone model and sidecar terminal comparison — Oct. 23, 2026

| Component/scenario | Terminal PnL | Cumulative notional added | Open notional |
|---|---:|---:|---:|
| Exponential — fixed $500/EOD | $+21,118.86 | $364,000.00 | $315,500.00 |
| Force multiplier — $10,000 / 1 unit per EOD | $+422,377.26 | $7,280,000.00 | $6,310,000.00 |
| Oil-desk daily-buy add-on | $+499,705.92 | $5,500,000.00 | $5,500,000.00 |
| $500 model + oil daily buys | $+520,824.78 | $5,864,000.00 | $5,815,500.00 |
| $10,000 model + oil daily buys | $+922,083.18 | $12,780,000.00 | $11,810,000.00 |

The $500 model ends at **$+21,118.86** (realized $+4,356.35; unrealized $+16,762.51). The force-multiplier model ends at **$+422,377.26** (realized $+87,127.05; unrealized $+335,250.21). With identical direction state and no tranche compounding, force-multiplier PnL and exposure are exactly 20× the $500 model before display rounding.

## Core variants with add-ons — terminal PnL

| Core variant | Core only | + $500 model | + $10,000 force multiplier | + oil desk | + $500 and oil | + force multiplier and oil |
|---|---:|---:|---:|---:|---:|---:|
| Variant 1 — 1u Open | $+99,599.67 | $+120,718.53 | $+521,976.93 | $+599,305.59 | $+620,424.45 | $+1,021,682.85 |
| Variant 2 — 1u SAR | $+74,882.36 | $+96,001.22 | $+497,259.62 | $+574,588.28 | $+595,707.14 | $+996,965.54 |
| Variant 3A — Nu Open | $+143,803.02 | $+164,921.88 | $+566,180.28 | $+643,508.94 | $+664,627.80 | $+1,065,886.20 |
| Variant 3B — Nu SAR | $+86,049.06 | $+107,167.92 | $+508,426.32 | $+585,754.98 | $+606,873.84 | $+1,008,132.24 |

The oil desk sidecar alone adds **$499,705.92** on $5.5M of daily-buy notional, so its scale can dominate the raw-PnL composite panels. Use the cumulative/open notional columns and the drawdown panel when comparing risk and scale; these composites do not apply a common capital base.

## Data and output files

- Daily all-strategy PnL and exposure comparison: [`strategy_sidecar_comparison_daily_v1.csv`](data/strategy_sidecar_comparison_daily_v1.csv).
- Exponential $500 per-symbol EOD audit: [`exponential_eod_positions_v1.csv`](data/exponential_eod_positions_v1.csv).
- Force multiplier $10,000 per-symbol EOD audit: [`force_multiplier_eod_positions_v1.csv`](data/force_multiplier_eod_positions_v1.csv).
- Price source map: [`active_price_source_registry_v2.csv`](data/active_price_source_registry_v2.csv); exact energy closes: [`energy_provider_eod_marks_v1.csv`](data/energy_provider_eod_marks_v1.csv).
- Core models: [`Model Performance Comparison.md`](Model%20Performance%20Comparison.md). Oil sidecar assumptions and source rows: [`Oil Desk EOD Accumulation Hypothetical.md`](Oil%20Desk%20EOD%20Accumulation%20Hypothetical.md).

**Scope note:** new direction-following models and composites are unadjusted USD PnL comparisons; they are not included in the existing whole-portfolio DXY/yield account scenarios. This historical paper-trade replay is not a live system, risk forecast, or investment recommendation.
