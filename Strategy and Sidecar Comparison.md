# Strategy and Sidecar Comparison

![Core models, exponential model, and sidecar combinations](Charts/performance/20-strategy-sidecar-comparison.png)

## Model rules and combination math

- **Core variants:** existing V1, V2, V3A, and V3B model replays from the main comparison.
- **Exponential model (user's label):** on every EOD after a ticker first has a logged direction, add a new **fixed $500 notional** lot in that ticker's most recent LONG/SHORT/REBUY direction. $500 does not compound. Carry direction forward until a new LONG/SHORT/REBUY entry occurs.
- **Risk rule:** when the carried direction changes, close all previously open exponential lots for that ticker at the current EOD close, then open the new $500 tranche in the newly authorized direction. Same-direction signals do not close existing lots. Trade-log EXIT / TAKE PROFIT events are non-directional here and do not clear the carried state, per the selected last-direction rule.
- **Signal basis:** the repository has no separate authorization feed, so the model uses the latest direction-bearing entry tag in `trades/*.txt` as the authorization record. REBUY is treated as LONG; weekend/holiday events take effect at the first priced EOD session on or after the logged date. Symbols do not accumulate $500 lots before their first directional log event.
- **Oil-desk sidecar:** uses only the daily-buy lots from the prior 10-unit / $100,000-per-ticker-per-EOD hypothetical. The sidecar's chart-opened maintenance positions are not added to composites because the core model already contains chart positions; this avoids double counting.
- **Graph combinations:** compare each core variant with each sidecar alone and with both sidecars together. The exponential and oil-desk lines also appear separately and as an incremental sidecar-only total. These are additive USD subtotals; they do not assume shared capital, funding, fees, or margin offsets.
- Universe: all 33 directly price-covered core tickers; DXY, EURUSD, JPYUSD, US10Y, and US30Y remain outside this price-position model.

## Terminal comparison — Oct. 23, 2026

| Strategy | Terminal PnL | Cumulative notional added | Open notional |
|---|---:|---:|---:|
| Exponential ($500 fixed/EOD) | $+21,118.86 | $364,000.00 | $315,500.00 |
| Oil-desk daily-buy sidecar only | $+499,705.92 | $5,500,000.00 | $5,500,000.00 |
| Both sidecars (incremental) | $+520,824.78 | $5,864,000.00 | $5,815,500.00 |
| Variant 1 — 1u Open — core | $+99,599.67 | $845,000.00 | $695,000.00 |
| Variant 1 — 1u Open + exponential | $+120,718.53 | $1,209,000.00 | $1,010,500.00 |
| Variant 1 — 1u Open + oil desk | $+599,305.59 | $6,345,000.00 | $6,195,000.00 |
| Variant 1 — 1u Open + both sidecars | $+620,424.45 | $6,709,000.00 | $6,510,500.00 |
| Variant 2 — 1u SAR — core | $+74,882.36 | $845,000.00 | $645,000.00 |
| Variant 2 — 1u SAR + exponential | $+96,001.22 | $1,209,000.00 | $960,500.00 |
| Variant 2 — 1u SAR + oil desk | $+574,588.28 | $6,345,000.00 | $6,145,000.00 |
| Variant 2 — 1u SAR + both sidecars | $+595,707.14 | $6,709,000.00 | $6,460,500.00 |
| Variant 3A — Nu Open — core | $+143,803.02 | $935,000.00 | $785,000.00 |
| Variant 3A — Nu Open + exponential | $+164,921.88 | $1,299,000.00 | $1,100,500.00 |
| Variant 3A — Nu Open + oil desk | $+643,508.94 | $6,435,000.00 | $6,285,000.00 |
| Variant 3A — Nu Open + both sidecars | $+664,627.80 | $6,799,000.00 | $6,600,500.00 |
| Variant 3B — Nu SAR — core | $+86,049.06 | $935,000.00 | $645,000.00 |
| Variant 3B — Nu SAR + exponential | $+107,167.92 | $1,299,000.00 | $960,500.00 |
| Variant 3B — Nu SAR + oil desk | $+585,754.98 | $6,435,000.00 | $6,145,000.00 |
| Variant 3B — Nu SAR + both sidecars | $+606,873.84 | $6,799,000.00 | $6,460,500.00 |

The exponential model ends at **$+21,118.86** (realized $+4,356.35; unrealized $+16,762.51), with **33 active symbols** and $315,500.00 open notional. It added $364,000.00 notional over the window.

## Data and output files

- Daily all-strategy comparison: [`strategy_sidecar_comparison_daily_v1.csv`](data/strategy_sidecar_comparison_daily_v1.csv).
- Per-symbol, per-session exponential directions, adds, open lots, and unrealized PnL: [`exponential_eod_positions_v1.csv`](data/exponential_eod_positions_v1.csv).
- Price series and source limitations: [`active_price_source_registry_v2.csv`](data/active_price_source_registry_v2.csv); exact energy EOD marks: [`energy_provider_eod_marks_v1.csv`](data/energy_provider_eod_marks_v1.csv).
- Existing core report: [`Model Performance Comparison.md`](Model%20Performance%20Comparison.md). Existing oil-desk assumptions/details: [`Oil Desk EOD Accumulation Hypothetical.md`](Oil%20Desk%20EOD%20Accumulation%20Hypothetical.md).

**Interpretation caveat:** this is a historical paper-trade replay under the requested direction-state and tranche rules, not a live trading system, risk forecast, or investment recommendation. Since $500 is fixed per EOD, the model's dollar exposure grows by accumulation rather than by compounding the tranche size.
