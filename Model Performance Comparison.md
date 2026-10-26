# THE ONE MODEL

![THE ONE MODEL vs THE WINNING MODEL — equal terminal gross additions](Charts/superstructure/the-one-model-vs-winning-model.png)

*Equal-gross comparison with the top terminal-PnL constituent selected ex post from this same period; its daily path is scaled to match THE ONE MODEL's terminal gross additions. This is a hypothetical, selection-biased comparison—not out-of-sample evidence.*

> **TradingView-only interim recalculation — 2026-10-24.** Core results below combine the 31 supplied direct-price TradingView symbols with a 1U/DAY/DXY currency-index sleeve across 36 common sessions. The DXY sleeve adds one 1U tranche each active EOD in the latest charted LONG/REBUY/SHORT direction; its current single LONG badge controls despite the conflicting caption. BTC and ETH remain excluded pending recalibration. No legacy or substitute prices are used. XRH0 has five transparently flagged carry-forward marks from prior supplied TradingView closes. See [`data/tradingview_benchmark_coverage_20261024.csv`](data/tradingview_benchmark_coverage_20261024.csv), [`data/tradingview_benchmark_session_marks_20261024.csv`](data/tradingview_benchmark_session_marks_20261024.csv), and the [crypto pending page](Crypto%20Sidecar%20%E2%80%94%20Pending%20TradingView%20Recalibration.md).
> **Updated source archive:** the revised Part B ZIP changes LLY's Oct. 20 TradingView mark from `$12,833.66` to `$1,283.66`; all model results below use the revised source and have been regenerated. See [`research/notes/tradingview-benchmark-import-20261024.md`](research/notes/tradingview-benchmark-import-20261024.md) and the Part B manifest.

![THE ONE MODEL 32-portfolio split-strategy superstructure](Charts/superstructure/the-one-model.png)

*Four-by-four Core × variant-specific 1U/EOD pairings, each tracked with and without its own energy sidecar; all 32 portfolios are summed without netting.*

![THE ONE MODEL 32-portfolio split-strategy aggregate PnL, gross notional, and deployed-notional ratio](Charts/superstructure/the-one-model-split-portfolio.png)

*Aggregate of 32 independent portfolios; percentage is PnL ÷ gross notional added, not an account return.*

## Model Performance Comparison — *Fall (Arizona) [2026]*

Day-by-day (and, where market data supports it, intraday) comparison of the four portfolio models carried on the same standardized book: **[`trades/`](trades/)** / **[`trades.zip`](trades.zip)** — `31` direct-price core tickers plus the integrated 1U/DAY/DXY sleeve, `89` direct-price events plus `1` DXY direction signals out of `101` total 2026 log events (`9` other events outside scope; `2` direct events after cutoff), `1U = $10,000.00` standard notional, all timestamps in Arizona year-round **`MST` / `UTC-07:00`**, marked against the **Friday, October 23, 2026** close. Intraday plots remain on their supplied Oct. 22 hourly scope.

> **Post-cutoff manual replenishments:** 2026-10-25 BRENT LONG 10U at $115.792; 2026-10-25 USOIL (internal ticker OIL) LONG 10U at $101.74 are recorded in the trade logs but fall after the Oct. 23 terminal mark. No post-entry EOD marks are included, so these entries are excluded from current core PnL and composites pending a later benchmark refresh.

> **Oil cost-basis savings:** the prior target trims' realized PnL is credited once against the remaining-plus-replenishment lot basis, as a PnL reclassification rather than additional profit. The Oct. 25 replenishments are outside the Oct. 23 mark window, so the current core totals remain unchanged. See [`Oil Cost Basis Savings Model.md`](Oil%20Cost%20Basis%20Savings%20Model.md) and [`oil_cost_basis_savings_v1.csv`](data/oil_cost_basis_savings_v1.csv).

> **Interactive version:** open **[`Model Performance Explorer.html`](Model%20Performance%20Explorer.html)** for a self-contained explorer with toggleable series, a hover crosshair, and per-ticker breakdowns. Machine-readable exports live in [`data/`](data/): [`model_performance_daily.csv`](data/model_performance_daily.csv), [`model_performance_tickers.csv`](data/model_performance_tickers.csv), [`model_performance_summary.json`](data/model_performance_summary.json).
> **DXY and historical account views:** the 1U/DAY/DXY index-return sleeve is included in every core variant. THE ONE MODEL's 32-portfolio split aggregate additionally adds the 10U/DAY DXY schedule to each portfolio, for 11U/DAY total; its regenerated totals are shown in the aggregate chart and portfolio audit export. Do not add the 1U sleeve twice. The 0.05U schedule remains an alternative. The separate DXY-numeraire and yield-multiplier views have been rebuilt using the current core paths; they remain sensitivities rather than additional core PnL.
> **Small Caps pilot:** **[`Small Caps [Buyout & Reorganization Offering Test Pilot].md`](Small%20Caps%20%5BBuyout%20%26%20Reorganization%20Offering%20Test%20Pilot%5D.md)** tracks the five LCID entries; all five are included in the Oct. 23 four-model comparison.
> **Energy and DXY sizing:** **[`TradingView Energy and Currency Desk Sidecars.md`](TradingView%20Energy%20and%20Currency%20Desk%20Sidecars.md)** provides the standard energy sizes and DXY schedule audit. The DXY 1U/DAY series is included in core variants. THE ONE MODEL adds the 10U/DAY DXY schedule to every split portfolio (11U/DAY combined) and uses 11U/DAY energy tranches per active ticker in its 16 energy-inclusive portfolios. The strategy-comparison composites below retain their existing 10U energy schedule; 0.05U DXY remains an alternative. The user-specified 50U-long BRENT plus 50U-long USOIL Manual-Automatic entries and their targeted 10U trims are now included in all four core variants and flow into downstream core-based results. [`Weekend Oil 50U Position Hypothetical.md`](Weekend%20Oil%2050U%20Position%20Hypothetical.md) is a lot-level attribution of those same core lots, not an additional overlay.
> **Strategy and sidecar comparison:** **[`Strategy and Sidecar Comparison.md`](Strategy%20and%20Sidecar%20Comparison.md)** compares the existing variants, the fixed-$500/EOD and shared/variant-specific 1U/EOD force models, and additive composites using the 10U TradingView energy schedule.
> **How the models work:** **[`Model Calculation Guide.md`](Model%20Calculation%20Guide.md)** explains unit sizing, day-by-day lot handling, close/reversal behavior, and PnL formulas.

## The Four Models

| Model | Rule | Units deployed | Realized | Unrealized | Base PnL | Legacy additive US10Y carry (reference) | **Legacy adjusted PnL** | **Legacy adjusted ROI** |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| **Variant 1 — 1U Open** | logged entry sizes; explicit exits close longs | 216.5U ($2,165,000) | $33,565.74 | $71,741.96 | $105,307.70 | $241.29 | **$105,548.99** | **4.88%** |
| **Variant 2 — 1U SAR** | V1 sizing plus LONG/REBUY closes open shorts | 216.5U ($2,165,000) | $39,389.88 | $63,074.62 | $102,464.50 | $241.29 | **$102,705.79** | **4.74%** |
| **Variant 3A — Nu Open** | V1 behavior; qualifying compounded shorts use preceding full-exit units | 225.5U ($2,255,000) | $33,565.74 | $93,025.45 | $126,591.19 | $264.52 | **$126,855.71** | **5.63%** |
| **Variant 3B — Nu SAR** | V2 behavior plus qualifying compounded shorts | 225.5U ($2,255,000) | $50,556.58 | $63,074.62 | $113,631.20 | $264.52 | **$113,895.72** | **5.05%** |

Displayed dollar components are rounded to cents and reconciled so realized plus unrealized equals Base PnL; legacy adjusted PnL equals displayed Base PnL plus the displayed carry. Unrounded replay values drive model calculations and charts.

## TradingView Benchmark and Alignment

The 31 directly priced core tickers use the normalized user-provided Part A and Part B TradingView lists only, aligned to the 36-session common calendar. A 1U/DAY/DXY index-return sleeve, activated by charted direction, is integrated into each model total and deployed-notional denominator; DXY is not represented as a directly traded security. The session marks and provenance are in [`tradingview_benchmark_session_marks_20261024.csv`](data/tradingview_benchmark_session_marks_20261024.csv); raw imported rows, coverage, and archive hashes are preserved alongside them. BTC and ETH have no marks in this core and remain pending recalibration.

**Provisional XRH0 convention:** five missing source sessions (`2026-09-15`, `2026-10-07`, `2026-10-08`, `2026-10-19`, and `2026-10-22`) carry forward the previous supplied TradingView close. Each row is explicitly flagged. No external or legacy price is inserted; revisit this convention if a different gap treatment is preferred.

Crypto status: [**Crypto Sidecar — Pending TradingView Recalibration**](Crypto%20Sidecar%20%E2%80%94%20Pending%20TradingView%20Recalibration.md). Energy schedules, DXY index-return assumptions, and standalone DXY sizing alternatives: [**TradingView Energy and Currency Desk Sidecars**](TradingView%20Energy%20and%20Currency%20Desk%20Sidecars.md). The 1U/DAY/DXY schedule from that page is already included in core PnL.

## Legacy Model-Level US10Y Additive Carry (Reference Only)

This inherited per-model additive overlay is retained for audit comparison, but it is not the active whole-portfolio blanket factor and is not included in the new DXY-view scenarios. Use the linked Whole Portfolio Yield Multiplier Explorer to compare the full account value with no yield factor, US10Y alone, and US10Y compounded with US30Y. This yield-based overlay is not a CPI inflation measure or Treasury total-return calculation. It treats the user-provided daily US10Y closes as annualized carry relative to the `4.865%` baseline from `2026-09-10`. For each interval, the adjustment is the model's cumulative deployed notional (the same denominator used for ROI; it does not fall after a position closes) × ((yield close − 4.865) / 100) × actual calendar days / 365. Values above baseline add positive adjustment; below baseline subtract. Per your confirmation, the Oct 9 close (5.24%) is carried across the Oct 12 Treasury holiday; the export records the original source date. The Oct 23 close (4.986%) is marked at the latest session; the Oct 22-to-Oct 23 carry interval uses the Oct 22 close (4.96%) under the existing start-of-interval convention.

![US10Y yield baseline and cumulative adjustment](Charts/performance/15-us10y-baseline-adjustment.png)

Session-level rates, forward-fill dates, actual/365 accruals, and adjusted totals: [`model_performance_us10y_adjustment.csv`](data/model_performance_us10y_adjustment.csv).

## TradingView Energy Sidecar

Brent and WTI core positions use the supplied aligned TradingView marks. Energy and DXY sizing alternatives are documented with per-session source flags in [`TradingView Energy and Currency Desk Sidecars.md`](TradingView%20Energy%20and%20Currency%20Desk%20Sidecars.md). The 1U/DAY/DXY index-return sleeve is already included in each core variant; do not add the 1U DXY schedule twice. Standard strategy composites add the 10U energy schedule. THE ONE MODEL separately uses 11U/DAY per active energy ticker in its 16 energy-inclusive portfolios; its derived machine-readable schedule is [`the_one_model_energy_11u_sidecar_daily_v1.csv`](data/the_one_model_energy_11u_sidecar_daily_v1.csv). Chart-opened core energy positions are shown separately and are not double-counted. Machine-readable standard schedules: [`tradingview_energy_sidecar_daily_20261024.csv`](data/tradingview_energy_sidecar_daily_20261024.csv) and [`dxy_currency_desk_sidecar_daily_20261024.csv`](data/dxy_currency_desk_sidecar_daily_20261024.csv).
**Integrated 1U/DAY/DXY sleeve (same across all four core variants):** 35 daily units, **$350,000.00** gross notional added, terminal proxy PnL **$+2,492.30**. This is already included in the four-model results above.

![TradingView-sourced energy EOD mark history](Charts/performance/14-energy-eod-mark-history.png)

All four models agree on `27` of the `31` tickers. They diverge only on **`CAT`, `INTC`, `META` and `PLTR`** — the four symbols where a short is followed by a long (or a full exit is compounded into a short). Everything below is driven by those four.

## Headline Chart

![Cumulative base trading PnL by session](Charts/performance/01-cumulative-pnl-by-session.png)

**Reading it:** the models begin close together, then spread as the reversal-sensitive positions develop. At the Oct. 23 close the base and legacy additive US10Y-adjusted rankings are **V3A > V3B > V1 > V2** and **V3A > V3B > V1 > V2**, respectively.

## Base Return on Capital

![Cumulative base ROI by session](Charts/performance/02-cumulative-roi-by-session.png)

This chart shows base trading PnL before the legacy additive US10Y carry; the legacy adjusted ROI is shown for reference in the model table above and selectable in the interactive explorer. For whole-account factor scenarios, use the linked Yield Multiplier Explorer.

Raw dollars flatter V3A/V3B because they deploy more capital — `225.5` units (`$2,255,000.00`) against V1/V2's `216.5` units (`$2,165,000.00`). ROI normalises for that, and the terminal ranking is unchanged: compounding shorts into full exits beats flat sizing on both capital bases, and *not* stop-and-reversing beats stop-and-reversing on both.

## Day-by-Day Moves

![Day-by-day PnL change](Charts/performance/03-daily-pnl-change.png)

| Session | V1 | V2 | V3A | V3B | Note |
|---|---:|---:|---:|---:|---|
| `2026-09-03` | +59.27 | +59.27 | +59.27 | +59.27 | Season open |
| `2026-09-04` | +220.34 | +220.34 | +220.34 | +220.34 |  |
| `2026-09-08` | +795.47 | +795.47 | +795.47 | +795.47 |  |
| `2026-09-09` | +1,369.90 | +1,369.90 | +1,369.90 | +1,369.90 |  |
| `2026-09-10` | +191.53 | +191.53 | +191.53 | +191.53 |  |
| `2026-09-11` | +601.19 | +601.19 | +601.19 | +601.19 |  |
| `2026-09-14` | -45.86 | +282.95 | -45.86 | +282.95 |  |
| `2026-09-15` | +404.96 | +364.40 | +404.96 | +364.40 |  |
| `2026-09-16` | +468.60 | +564.86 | +468.60 | +564.86 |  |
| `2026-09-17` | +4,993.41 | +5,096.16 | +4,993.41 | +5,096.16 |  |
| `2026-09-18` | -2,750.54 | -2,674.82 | -2,750.54 | -2,674.82 |  |
| `2026-09-21` | +12,567.08 | +12,861.82 | +12,567.08 | +12,861.82 |  |
| `2026-09-22` | +2,559.14 | +2,661.89 | +3,581.87 | +3,684.63 | widest split (V3B best, V1 worst) |
| `2026-09-23` | +95.27 | +463.02 | +491.78 | +859.53 | widest split (V3B best, V1 worst) |
| `2026-09-24` | +2,681.45 | +2,724.72 | +751.46 | +794.73 | widest split (V2 best, V3A worst) |
| `2026-09-25` | +684.88 | +933.61 | +3,414.32 | +5,289.65 | widest split (V3B best, V1 worst) |
| `2026-09-28` | +2,397.03 | +3,685.84 | +6,463.93 | +9,444.64 | widest split (V3B best, V1 worst) |
| `2026-09-29` | -3,106.04 | -2,849.06 | -4,279.05 | -2,849.06 | widest split (V2 best, V3A worst) |
| `2026-09-30` | +313.03 | +852.33 | -332.62 | +852.33 | widest split (V2 best, V3A worst) |
| `2026-10-01` | +3,638.52 | +3,771.89 | +3,671.91 | +3,771.89 |  |
| `2026-10-02` | -392.62 | -545.36 | -293.54 | -545.36 |  |
| `2026-10-05` | -660.79 | -965.85 | -391.10 | -965.85 | widest split (V3A best, V2 worst) |
| `2026-10-06` | +1,404.45 | +1,169.14 | +2,737.21 | +1,183.71 | widest split (V3A best, V2 worst) |
| `2026-10-07` | +317.60 | +32.36 | +1,609.59 | +606.09 | widest split (V3A best, V2 worst) |
| `2026-10-08` | +4,727.52 | +3,974.18 | +6,854.18 | +4,178.30 | widest split (V3A best, V2 worst) |
| `2026-10-09` | +216.74 | +349.29 | +1,031.49 | +299.68 | widest split (V3A best, V1 worst) |
| `2026-10-12` | +3,230.48 | +2,988.87 | +3,034.70 | +3,001.59 |  |
| `2026-10-13` | +2,038.33 | +2,516.12 | +870.61 | +2,823.63 | widest split (V3B best, V3A worst) |
| `2026-10-14` | +3,080.41 | +1,563.20 | +6,129.07 | +1,838.44 | widest split (V3A best, V2 worst) |
| `2026-10-15` | +514.60 | +23.27 | +1,576.89 | +177.54 | widest split (V3A best, V2 worst) |
| `2026-10-16` | +4,673.10 | +2,620.71 | +7,890.72 | +2,677.15 | widest split (V3A best, V2 worst) |
| `2026-10-19` | -8,537.33 | -7,830.20 | -8,969.63 | -7,816.55 | widest split (V3B best, V3A worst) |
| `2026-10-20` | -575.22 | -868.55 | +125.56 | -868.55 | widest split (V3A best, V2 worst) |
| `2026-10-21` | -3,665.40 | -2,746.32 | -4,408.17 | -2,746.32 | widest split (V2 best, V3A worst) |
| `2026-10-22` | +30,024.23 | +27,437.84 | +35,323.21 | +27,437.84 | widest split (V3A best, V3B worst) |
| `2026-10-23` | +40,772.99 | +40,768.48 | +40,831.44 | +40,768.48 | Terminal mark |

## Where the Models Diverge

![Model spreads](Charts/performance/04-model-spreads.png)

![Compounding effect](Charts/performance/05-compounding-effect.png)

- **Stop-and-reverse (V1 − V2) ends at $2,843.20; (V3A − V3B) ends at $12,959.98.**
- **Compounding (V3A − V1) ends at $21,283.49** — the single largest structural effect in the book.

## Risk — Drawdown from Running Peak

![Drawdown](Charts/performance/06-drawdown.png)

| Model | Peak | Peak day | Trough | Trough day | Max drawdown | Max DD day | Best day | Worst day |
|---|---:|---|---:|---:|---|---:|---|---:|
| **Variant 1 — 1U Open** | $105,307.70 | `2026-10-23` | $59.27 | `2026-09-03` | -$12,777.95 | `2026-10-21` | $40,772.99 (`2026-10-23`) | -$8,537.33 (`2026-10-19`) |
| **Variant 2 — 1U SAR** | $102,464.50 | `2026-10-23` | $59.27 | `2026-09-03` | -$11,445.07 | `2026-10-21` | $40,768.48 (`2026-10-23`) | -$7,830.20 (`2026-10-19`) |
| **Variant 3A — Nu Open** | $126,591.19 | `2026-10-23` | $59.27 | `2026-09-03` | -$13,252.24 | `2026-10-21` | $40,831.44 (`2026-10-23`) | -$8,969.63 (`2026-10-19`) |
| **Variant 3B — Nu SAR** | $113,631.20 | `2026-10-23` | $59.27 | `2026-09-03` | -$11,431.43 | `2026-10-21` | $40,768.48 (`2026-10-23`) | -$7,816.55 (`2026-10-19`) |

## Terminal Composition

![Terminal composition](Charts/performance/07-terminal-composition.png)

| Model | Realized (closed) | Unrealized (open) | Closed lots | Open lots |
|---|---:|---:|---:|---:|
| **Variant 1 — 1U Open** | $33,565.74 | $71,741.96 | 17 | 102 |
| **Variant 2 — 1U SAR** | $39,389.88 | $63,074.62 | 22 | 97 |
| **Variant 3A — Nu Open** | $33,565.74 | $93,025.45 | 17 | 102 |
| **Variant 3B — Nu SAR** | $50,556.58 | $63,074.62 | 22 | 97 |

## Contribution by Ticker

![Ticker contribution](Charts/performance/08-ticker-contribution.png)

### The four divergence tickers

| Ticker | V1 | V2 | V3A | V3B |
|---|---:|---:|---:|---:|
| `CAT` | $3,456.26 | $2,963.84 | $5,511.31 | $4,526.46 |
| `INTC` | $11,319.86 | $8,383.08 | $23,954.58 | $15,435.24 |
| `META` | $9,937.17 | $8,926.72 | $16,530.89 | $11,478.64 |
| `PLTR` | $2,314.90 | $3,911.35 | $2,314.90 | $3,911.35 |

### Top contributors (V3A)

| Ticker | Units | Realized | Unrealized | **Total** |
|---|---:|---:|---:|---:|
| `BRENT` | 55U | $5,015.62 | $26,327.68 | **$31,343.30** |
| `OIL` | 56U | $2,988.69 | $24,425.55 | **$27,414.24** |
| `INTC` | 14U | $10,955.99 | $12,998.59 | **$23,954.58** |
| `META` | 13U | $10,430.36 | $6,100.53 | **$16,530.89** |
| `LMT` | 4U | $0.00 | $6,990.06 | **$6,990.06** |
| `CAT` | 5U | $1,984.84 | $3,526.47 | **$5,511.31** |
| `LCID` | 5U | $0.00 | $4,822.30 | **$4,822.30** |
| `CVX` | 3U | $0.00 | $3,406.36 | **$3,406.36** |
| `DXY` | 35U | $0.00 | $2,492.30 | **$2,492.30** |
| `SPCX` | 3U | $0.00 | $2,416.69 | **$2,416.69** |

Ticker units preserve fractional logged sizes. Each ticker total equals its cent-rounded realized plus unrealized components; summing independently rounded ticker rows can differ from the unrounded model total by a few cents.

### Bottom contributors (V3A)

| Ticker | Units | Realized | Unrealized | **Total** |
|---|---:|---:|---:|---:|
| `GEV` | 1U | $0.00 | -$1,903.20 | **-$1,903.20** |
| `RIVN` | 1U | $0.00 | -$1,727.27 | **-$1,727.27** |
| `UPS` | 2U | $0.00 | -$1,422.48 | **-$1,422.48** |
| `DIS` | 2U | -$310.50 | -$795.36 | **-$1,105.86** |
| `NVDA` | 1U | $0.00 | -$811.45 | **-$811.45** |
| `AMZN` | 1U | $0.00 | -$409.16 | **-$409.16** |
| `NET` | 1U | $0.00 | -$206.26 | **-$206.26** |
| `NFLX` | 1U | $0.00 | -$180.44 | **-$180.44** |
| `VLO` | 1U | $0.00 | -$113.65 | **-$113.65** |
| `TSLA` | 1U | $0.00 | -$113.03 | **-$113.03** |

## Intraday — Hour by Hour

Daily closes hide *when* inside a session the models pull apart. Zooming to **hourly bars** (7 per session: `06:30`→`13:00 MST`) resolves that.

> **Scope:** the intraday view covers **`CAT`, `INTC`, `META` and `PLTR`** — the divergence sub-book. The other `27` tickers produce byte-identical PnL under all four models, so they cancel exactly out of every comparison below. Every number here is therefore *exact*, not interpolated.

![Intraday divergence sub-book](Charts/performance/09-intraday-sub-book-pnl.png)

### Terminal, divergence sub-book only

| Model | Realized | Unrealized | **Sub-book total** |
|---|---:|---:|---:|
| **Variant 1 — 1U Open** | $25,871.93 | $1,195.66 | **$27,067.59** |
| **Variant 2 — 1U SAR** | $31,696.07 | -$7,467.17 | **$24,228.90** |
| **Variant 3A — Nu Open** | $25,871.93 | $22,420.70 | **$48,292.63** |
| **Variant 3B — Nu SAR** | $42,862.77 | -$7,467.17 | **$35,395.60** |

The sub-book totals differ from the full-portfolio totals above by exactly the 27 invariant tickers, which contribute the same amount to every model.

### The regime flips

![Intraday spreads](Charts/performance/10-intraday-spreads.png)

![Crossover zoom](Charts/performance/11-crossover-zoom.png)

| Spread | First > 0 | Stays > 0 from | Peak | Trough | Terminal |
|---|---|---|---:|---:|---:|
| **V1-V2** | `10-15 07:30 MST` | `10-16 07:30 MST` | $2,861.47 @ `10-22 12:30 MST` | -$4,916.98 @ `10-02 07:30 MST` | **$2,838.69** |
| **V3A-V3B** | `10-14 09:30 MST` | `10-14 13:00 MST` | $13,114.19 @ `10-22 11:30 MST` | -$11,985.25 @ `10-02 07:30 MST` | **$12,897.03** |
| **V3A-V1** | `09-22 13:00 MST` | `09-25 07:30 MST` | $21,433.86 @ `10-22 11:30 MST` | -$510.75 @ `09-24 13:00 MST` | **$21,225.04** |
| **V3B-V2** | `09-22 13:00 MST` | `09-25 07:30 MST` | $11,345.49 @ `10-15 07:30 MST` | -$510.75 @ `09-24 13:00 MST` | **$11,166.70** |

**What this says — stop-and-reverse is a help early and a drag late.** Both spreads open the season deeply *negative*, meaning the **SAR books lead** out of the gate: at `10-02 07:30 MST` `V2` is ahead of `V1` by $4,916.98 and `V3B` is ahead of `V3A` by $11,985.25 — the widest SAR lead of the whole season, on the same bar. Flipping a position instead of stacking a new one protects capital while prices run *against* the earlier direction.

That lead then erodes as the trend matures, and the **open books take over for good in the `Oct 14`–`Oct 16` window**: `V3A − V3B` first prints positive at `10-14 09:30 MST` and never looks back from `10-14 13:00 MST`; `V1 − V2` flips a day later and holds from `10-16 07:30 MST`. Once the moves are directional, reversing out of the original entry throws away the winner — which is why the two spreads end the season on opposite sides of zero, and `4.5×` apart in magnitude.

Compounding shorts into full exits, by contrast, is unambiguous: `V3A − V1` turns positive on `09-22 13:00 MST` — the moment the `INTC` `5-unit` full exit at `$127.11` is compounded — and never crosses back.

### Which ticker drives each edge

![Intraday per ticker](Charts/performance/12-intraday-per-ticker.png)

Intraday per-ticker contribution at the Oct 22 close (the hourly archive has no Oct 23 bars):

| Ticker | V1 | V2 | V3A | V3B | Intraday peak bar (V3A) |
|---|---:|---:|---:|---:|---|
| `CAT` | $1,507.94 | -$349.93 | $3,365.81 | -$349.93 | `10-15 07:30 MST` |
| `INTC` | $188.67 | -$5,658.85 | $13,285.99 | -$5,658.85 | `10-22 13:00 MST` |
| `META` | -$401.02 | -$1,968.48 | $5,868.83 | -$1,968.48 | `09-24 12:30 MST` |
| `PLTR` | -$99.94 | $510.09 | -$99.94 | $510.09 | `10-09 13:00 MST` |

Full per-bar series: [`model_performance_intraday.csv`](data/model_performance_intraday.csv) (245 rows).

## Supplemental Portfolio, Pilot, and Sidecar Graphs

The following views extend beyond the four core direct-price variants. They use distinct account bases or sidecar schedules where noted; they are not all on a common capital base, and their positions/capital must not be netted or stacked implicitly.

### Whole-Portfolio DXY Numeraire and Yield Scenarios

> **Historical only—not recalculated on the current TradingView core.** The DXY-numeraire and yield-multiplier graphs below retain their previous portfolio benchmark and must not be read as current results. The current 1U/DAY/DXY index-return sleeve is integrated into the core; its sizing alternatives are in [`TradingView Energy and Currency Desk Sidecars.md`](TradingView%20Energy%20and%20Currency%20Desk%20Sidecars.md).

![DXY close vs whole-portfolio PnL in dollars](Charts/performance/17-dxy-close-vs-whole-portfolio-pnl-usd.png)

![Whole-portfolio unrealized PnL and USD/DXY returns](Charts/performance/16-whole-portfolio-dxy-vs-usd-pnl.png)

### LCID Small-Caps Pilot

The five-entry LCID pilot is already included in the four-model replay through the corrected Oct. 23 mark; this graph is a focused component view, not another add-on to the core totals. See [`Small Caps [Buyout & Reorganization Offering Test Pilot].md`](Small%20Caps%20%5BBuyout%20%26%20Reorganization%20Offering%20Test%20Pilot%5D.md) for entry and mark details.

![LCID small-caps pilot daily PnL and marks](Charts/performance/18-lcid-small-caps-pilot-pnl.png)

### TradingView Energy and Currency Desk Sidecars

The sidecar report presents 0.05U, 1U, and 10U sizing schedules. The chart-directed 1U/DAY/DXY index-return sleeve is integrated in every core variant; THE ONE MODEL adds the 10U schedule to each split portfolio, while 0.05U remains an alternative. Strategy-comparison composites retain their original scope and add the 10U energy schedule, not the DXY 10U schedule. See [`TradingView Energy and Currency Desk Sidecars.md`](TradingView%20Energy%20and%20Currency%20Desk%20Sidecars.md).

![DXY daily-investment sizing options](Charts/performance/23-dxy-daily-sizing-alternatives.png)

*The three panels show 0.05U, 1U, and 10U daily-lot PnL paths on separate scales. The 1U schedule is already included in core PnL; THE ONE MODEL adds the 10U schedule to every split portfolio (11U/DAY combined), while 0.05U remains an alternative.*

The user-specified 50U-long BRENT and 50U-long USOIL Manual-Automatic lots were added to each core variant at the supplied Oct. 19 TradingView marks, with 10U target trims at $117 and $102 respectively. Their first recorded EOD marks at/above target are on Oct. 23; the daily closes do not verify an intraday touch or fill. The lots are included in the core replay and downstream aggregates; [`Weekend Oil 50U Position Hypothetical.md`](Weekend%20Oil%2050U%20Position%20Hypothetical.md) isolates their PnL for attribution only. Existing separate 1U core lots are not trimmed.

![50U long BRENT and 50U long USOIL hypothetical PnL](Charts/CLN25/Weekend%20Oil/24-weekend-oil-50u-positions.png)

### EOD Add-On and Variant-Specific 1U/EOD Comparisons

The fixed-$500/EOD model and 1U/EOD alternatives are separate model families, not stacked on top of one another. The broad comparison distinguishes standalone results from additive composites; composites sum PnL and gross notionals without netting positions or capital. See [`Strategy and Sidecar Comparison.md`](Strategy%20and%20Sidecar%20Comparison.md) and [`Model Calculation Guide.md`](Model%20Calculation%20Guide.md) for full rules and tables.

![Core models, separate $500 and 1U direction-following models, and sidecar combinations](Charts/performance/20-strategy-sidecar-comparison.png)

The next chart contains all **16 Core × variant-specific 1U/EOD pairings**, including matching and cross-variant pairs, each with the 10U TradingView energy daily-buy sidecar. These are additive USD totals; positions and capital are not netted, and the core's chart-opened energy lots are not duplicated in the sidecar.

![All 16 Core × 1U variant pairings with energy sidecar](Charts/performance/21-force-variant-oil-comparison.png)

The percentage-gain view plots all **32 series**: the same 16 Core × 1U pairings, each with and without the energy sidecar. Gain is cumulative PnL divided by cumulative gross notional added—a deployed-notional ratio, **not an account return**. Only the top four terminal performers are named in the legend; all 32 are plotted. The earlier **8.88% static single-composite proxy is not a result for this 32-portfolio split**. The leading terminal ratios are Core V3A + 1U V3A with energy sidecar, **5.38%**; Core V3A + 1U V3B with energy sidecar, **5.30%**; Core V3B + 1U V3A with energy sidecar, **5.29%**; Core V3A + 1U V1 with energy sidecar, **5.27%**.

![All 32 Core × 1U variant pairings with and without the energy sidecar, shown as deployed-notional percentage gain](Charts/performance/22-force-variant-oil-percent-gain.png)

## Method & Caveats

- **Model coverage:** the four variants directly price `31` TradingView tickers and include the chart-directed 1U/DAY/DXY index-return sleeve. `89` direct-price trade events plus `1` DXY direction signal are in scope through Oct. 23; `2` direct-price events after the mark are excluded. `9` other BTC, ETH, EURUSD, JPYUSD, US10Y, and US30Y log events are not replayed as direct-price positions. The two US10Y events establish yield-adjustment context; this report's additive carry is retained only as a legacy reference. Whole-account US10Y and compounded US30Y multiplier scenarios remain historical. DXY uses an index-return proxy, not an exchange-traded contract model.
- **Price source:** every direct-price core mark comes from the normalized user-provided TradingView Part A/Part B lists, aligned in [`data/tradingview_benchmark_session_marks_20261024.csv`](data/tradingview_benchmark_session_marks_20261024.csv). DXY's 1U/day proxy uses its separate supplied TradingView index marks and the charted direction signal; it is integrated into the core totals but is not a directly traded security. BTC/ETH remain pending and outside the core. Five missing XRH0 sessions use the last prior supplied TradingView close, with each carry-forward row explicitly flagged; this is a provisional mark convention. No Yahoo or historical-series fill is used.
- **Benchmark provenance and alignment:** Part A and Part B raw observations, per-ticker coverage, and archive hashes are preserved in the paired CSV/JSON artifacts under `data/`. DXY is marked separately from the 31 direct-price tickers but its chart-directed 1U/day proxy is integrated into this core portfolio. EURUSD, JPYUSD, US10Y, and US30Y remain outside. Do not interpret the historical whole-portfolio DXY/yield pages as recalculated from this benchmark.
- **Session calendar:** the `36` U.S. equity regular sessions from `2026-09-03` to `2026-10-23`. DXY index marks align to the same sessions; BTC/ETH remain excluded pending recalibration.
- **XRH0 interim marks:** the source list omits five common sessions (`2026-09-15`, `2026-10-07`, `2026-10-08`, `2026-10-19`, and `2026-10-22`). Those are carried forward from the prior supplied TradingView close and flagged in the session-mark CSV; no external price is inserted. Treat its interim path as provisional.
- **Performance scope:** logged core trade entries/exits retain their chart-posting prices; the additional DXY sleeve adds 1U at each active EOD in the latest charted direction, marked to the supplied TradingView index close. The integrated core totals therefore include DXY daily-investment PnL and notional. Historical whole-account/yield outputs and the master ledger are not recalculated by this run.
- **ROI** is cumulative PnL divided by notional deployed *to date* (units opened on or before that session × 1U standard notional), so early sessions show larger percentages on less capital.
- **Open units** are units still held at each session close; they decline when a position closes. This differs from cumulative units deployed, which continues to include previously closed units.
- **All-actionable-ticker audit:** an independent replay reconciles all 31 TradingView-priced core tickers, the integrated 1U/DAY/DXY sleeve, energy/DXY sizing schedules, position exports, and all 32 portfolio aggregates. See the current [`data/actionable_ticker_reconciliation_20261023_v1.csv`](data/actionable_ticker_reconciliation_20261023_v1.csv) audit output.
- Entry fills use the chart-posting prices recorded in the trade log, not later minute or session closes; the Sep. 24 INTC short uses the chart-posting price `$115.11`. Exits are realised on their log date.
- Excludes commissions, borrow fees, and overnight financing.

---

Master ledger: **[`Trades Zip PnL.md`](Trades%20Zip%20PnL.md)** · Chart-signal report: **[`Triangle Signals.md`](Triangle%20Signals.md)** · Visual book: **[`Unrealized PnL.md`](Unrealized%20PnL.md)** · Pre-2026: **[`2024 Trades PnL.md`](reports/2024/2024%20Trades%20PnL.md)**
