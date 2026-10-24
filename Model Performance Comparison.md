# Model Performance Comparison — *Fall (Arizona) [2026]*

Day-by-day (and, where market data supports it, intraday) comparison of the four portfolio models carried on the same standardized book: **[`trades/`](trades/)** / **[`trades.zip`](trades.zip)** — `33` price-covered symbols, `88` in-window price-covered events out of `95` total 2026 log events (`7` outside direct-price scope; `0` after cutoff), `1 unit = $10,000.00` initial notional, all timestamps in Arizona year-round **`MST` / `UTC-07:00`**, marked against the **Friday, October 23, 2026** close. Intraday plots remain on their supplied Oct. 22 hourly scope.

> **Interactive version:** open **[`Model Performance Explorer.html`](Model%20Performance%20Explorer.html)** for a self-contained explorer with toggleable series, a hover crosshair, and per-ticker breakdowns. Machine-readable exports live in [`data/`](data/): [`model_performance_daily.csv`](data/model_performance_daily.csv), [`model_performance_tickers.csv`](data/model_performance_tickers.csv), [`model_performance_summary.json`](data/model_performance_summary.json).
> **Whole-portfolio DXY and yield-multiplier scenarios:** **[`DXY-Equivalent Portfolio Snapshot.md`](DXY-Equivalent%20Portfolio%20Snapshot.md)** includes the daily DXY-numeraire comparison and the toggleable whole-account scenarios (no factor, US10Y, US10Y × US30Y) in **[`Whole Portfolio Yield Multiplier Explorer.html`](Whole%20Portfolio%20Yield%20Multiplier%20Explorer.html)**.
> **Small Caps pilot:** **[`Small Caps [Buyout & Reorganization Offering Test Pilot].md`](Small%20Caps%20%5BBuyout%20%26%20Reorganization%20Offering%20Test%20Pilot%5D.md)** tracks the five LCID entries; all five are included in the Oct. 23 four-model comparison.
> **Oil desk hypothetical:** **[`Oil Desk EOD Accumulation Hypothetical.md`](Oil%20Desk%20EOD%20Accumulation%20Hypothetical.md)** shows 10 new $10,000 long units per supplied EOD session for each exact energy benchmark, separately and combined with the chart-opened energy positions.

## The Four Models

| Model | Rule | Units deployed | Realized | Unrealized | Base PnL | Legacy additive US10Y carry (reference) | **Legacy adjusted PnL** | **Legacy adjusted ROI** |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| **Variant 1 — 1u Open** | every line is 1 unit; positions stay open | 84u ($845,000) | $25,561.44 | $74,038.24 | $99,599.67 | $160.90 | **$99,760.58** | **11.81%** |
| **Variant 2 — 1u SAR** | every line is 1 unit; LONG/REBUY stops-and-reverses open shorts | 84u ($845,000) | $31,385.57 | $43,496.78 | $74,882.36 | $160.90 | **$75,043.26** | **8.88%** |
| **Variant 3A — Nu Open** | compounded shorts sized to the preceding full exit; positions stay open | 94u ($935,000) | $25,561.44 | $118,241.58 | $143,803.02 | $184.13 | **$143,987.15** | **15.40%** |
| **Variant 3B — Nu SAR** | compounded shorts *and* stop-and-reverse | 94u ($935,000) | $42,552.27 | $43,496.78 | $86,049.06 | $184.13 | **$86,233.19** | **9.22%** |

## Oct. 23 Endpoint Price Corrections Applied

The performance calculations, charts, and ticker-contribution exports below use the active v7 endpoint source. Versioned v1–v6 close sets remain preserved. Exact user-provided BlackBull Brent Cash marks cover every session from the first Brent position (Sep. 23) through Oct. 23; exact TVC:USOIL marks cover every session from the first WTI position (Sep. 10) through Oct. 23. Only pre-entry context retains Yahoo futures proxies.

| Ticker | Prior mark | Active v7 mark | Correction basis |
|---|---:|---:|---|
| `NFLX` | $762.10 | **$65.85** | User-confirmed v1 (v2→v3) |
| `BTC` | $68,250.00 | **$81,227.04** | User-confirmed v1 (v2→v3) |
| `ETH` | $2,640.00 | **$2,408.47** | User-confirmed v1 (v2→v3) |
| `RIVN` | $11.25 | **$11.83** | User-confirmed v1 (v2→v3) |
| `LCID` | $3.55 | **$3.52** | User-provided correction (v2→v3) |
| `XRH0` | $790.00 | **$785.00** | User-provided correction (v2→v3) |
| `CVX` | $151.30 | **$233.21** | Selected preserved v1 Yahoo mark (v3→v4) |
| `WMT` | $81.15 | **$119.89** | Selected preserved v1 Yahoo mark (v3→v4) |
| `TMO` | $524.30 | **$673.82** | Selected preserved v1 Yahoo mark (v3→v4) |
| `UPS` | $134.60 | **$101.06** | Reported ~$101 corroborated by v1 (v4→v5) |
| `BRENT` | $113.81 | **$117.345** | User-provided exact BlackBull Brent Cash EOD (v6→v7) |
| `OIL` | $97.53 | **$103.45** | User-provided exact TradingView TVC:USOIL EOD (v6→v7) |

LCID's Oct. 20–22 marks remain $3.27, $3.21, and $3.46. XRH0 remains $790 through Oct. 22 and changes only at the Oct. 23 endpoint; no interim marks are invented. Endpoint audits: [`eod_close_reconciliation_20261023_v2_to_v3.csv`](data/eod_close_reconciliation_20261023_v2_to_v3.csv), [`eod_close_reconciliation_20261023_v3_to_v4.csv`](data/eod_close_reconciliation_20261023_v3_to_v4.csv), [`eod_close_reconciliation_20261023_v4_to_v5.csv`](data/eod_close_reconciliation_20261023_v4_to_v5.csv), [`eod_close_reconciliation_20261023_v5_to_v6.csv`](data/eod_close_reconciliation_20261023_v5_to_v6.csv), and [`eod_close_reconciliation_20261023_v6_to_v7.csv`](data/eod_close_reconciliation_20261023_v6_to_v7.csv). Exact daily energy data: [`energy_provider_eod_marks_v1.csv`](data/energy_provider_eod_marks_v1.csv).

## Legacy Model-Level US10Y Additive Carry (Reference Only)

This inherited per-model additive overlay is retained for audit comparison, but it is not the active whole-portfolio blanket factor and is not included in the new DXY-view scenarios. Use the linked Whole Portfolio Yield Multiplier Explorer to compare the full account value with no yield factor, US10Y alone, and US10Y compounded with US30Y. This yield-based overlay is not a CPI inflation measure or Treasury total-return calculation. It treats the user-provided daily US10Y closes as annualized carry relative to the `4.865%` baseline from `2026-09-10`. For each interval, the adjustment is the model's cumulative deployed notional (the same denominator used for ROI; it does not fall after a position closes) × ((yield close − 4.865) / 100) × actual calendar days / 365. Values above baseline add positive adjustment; below baseline subtract. Per your confirmation, the Oct 9 close (5.24%) is carried across the Oct 12 Treasury holiday; the export records the original source date. The Oct 23 close (4.986%) is marked at the latest session; the Oct 22-to-Oct 23 carry interval uses the Oct 22 close (4.96%) under the existing start-of-interval convention.

![US10Y yield baseline and cumulative adjustment](Charts/performance/15-us10y-baseline-adjustment.png)

Session-level rates, forward-fill dates, actual/365 accruals, and adjusted totals: [`model_performance_us10y_adjustment.csv`](data/model_performance_us10y_adjustment.csv).

## Energy EOD Marks and Separate Approximate Quotes

> The Oct 23 exact user-provided EOD marks ($117.345 BlackBull Brent Cash / $103.45 TVC:USOIL) and the full active-position-period history are included in daily model totals. Only pre-entry context uses Yahoo BZ=F/CL=F proxies. Separate approximate user quotes ($115.72 / $100.94; provider/time unspecified) remain outside those totals.

![Separate energy mark and PnL comparison](Charts/performance/14-energy-live-mark-overlay.png)

Detailed marks and calculations: [`data/energy_live_mark_overlay.csv`](data/energy_live_mark_overlay.csv).

All four models agree on `29` of the `33` tickers. They diverge only on **`CAT`, `INTC`, `META` and `PLTR`** — the four symbols where a short is followed by a long (or a full exit is compounded into a short). Everything below is driven by those four.

## Headline Chart

![Cumulative base trading PnL by session](Charts/performance/01-cumulative-pnl-by-session.png)

**Reading it:** the models begin close together, then spread as the reversal-sensitive positions develop. At the Oct. 23 close the base and legacy additive US10Y-adjusted rankings are **V3A > V1 > V3B > V2** and **V3A > V1 > V3B > V2**, respectively.

## Base Return on Capital

![Cumulative base ROI by session](Charts/performance/02-cumulative-roi-by-session.png)

This chart shows base trading PnL before the legacy additive US10Y carry; the legacy adjusted ROI is shown for reference in the model table above and selectable in the interactive explorer. For whole-account factor scenarios, use the linked Yield Multiplier Explorer.

Raw dollars flatter V3A/V3B because they deploy more capital — `94` units (`$935,000.00`) against V1/V2's `84` units (`$845,000.00`). ROI normalises for that, and the terminal ranking is unchanged: compounding shorts into full exits beats flat sizing on both capital bases, and *not* stop-and-reversing beats stop-and-reversing on both.

## Day-by-Day Moves

![Day-by-day PnL change](Charts/performance/03-daily-pnl-change.png)

| Session | V1 | V2 | V3A | V3B | Note |
|---|---:|---:|---:|---:|---|
| `2026-09-03` | +3,439.92 | +3,439.92 | +3,439.92 | +3,439.92 | Season open |
| `2026-09-04` | -318.25 | -318.25 | -318.25 | -318.25 |  |
| `2026-09-08` | +440.82 | +440.82 | +440.82 | +440.82 |  |
| `2026-09-09` | +1,097.81 | +1,097.81 | +1,097.81 | +1,097.81 |  |
| `2026-09-10` | -249.17 | -249.17 | -249.17 | -249.17 |  |
| `2026-09-11` | +1,249.22 | +1,249.22 | +1,249.22 | +1,249.22 |  |
| `2026-09-14` | -335.70 | -6.90 | -335.70 | -6.90 |  |
| `2026-09-15` | -877.37 | -917.93 | -877.37 | -917.93 |  |
| `2026-09-16` | +460.57 | +556.83 | +460.57 | +556.83 |  |
| `2026-09-17` | +5,116.50 | +5,219.25 | +5,116.50 | +5,219.25 |  |
| `2026-09-18` | -626.35 | -550.64 | -626.35 | -550.64 |  |
| `2026-09-21` | +14,580.43 | +14,875.16 | +14,580.43 | +14,875.16 |  |
| `2026-09-22` | +2,180.78 | +2,283.53 | +3,203.51 | +3,306.27 | widest split (V3B best, V1 worst) |
| `2026-09-23` | +77.67 | +445.42 | +474.18 | +841.92 | widest split (V3B best, V1 worst) |
| `2026-09-24` | +1,021.01 | +1,064.27 | -908.98 | -865.72 | widest split (V2 best, V3A worst) |
| `2026-09-25` | +934.19 | +1,182.92 | +3,663.63 | +5,538.96 | widest split (V3B best, V1 worst) |
| `2026-09-28` | +2,348.25 | +3,637.06 | +6,415.15 | +9,395.86 | widest split (V3B best, V1 worst) |
| `2026-09-29` | -3,479.09 | -3,222.10 | -4,652.10 | -3,222.10 | widest split (V2 best, V3A worst) |
| `2026-09-30` | +399.43 | +938.73 | -246.22 | +938.73 | widest split (V3B best, V3A worst) |
| `2026-10-01` | +2,797.26 | +2,930.63 | +2,830.65 | +2,930.63 |  |
| `2026-10-02` | -104.95 | -257.68 | -5.87 | -257.68 |  |
| `2026-10-05` | -538.72 | -843.77 | -269.02 | -843.77 | widest split (V3A best, V2 worst) |
| `2026-10-06` | +1,759.52 | +1,253.80 | +3,092.28 | +1,268.37 | widest split (V3A best, V2 worst) |
| `2026-10-07` | -1,692.93 | -1,707.77 | -400.94 | -1,134.04 | widest split (V3A best, V2 worst) |
| `2026-10-08` | +4,166.63 | +3,413.29 | +6,293.29 | +3,617.40 | widest split (V3A best, V2 worst) |
| `2026-10-09` | +205.08 | +337.64 | +1,019.83 | +288.02 | widest split (V3A best, V1 worst) |
| `2026-10-12` | +1,772.84 | +1,531.23 | +1,577.06 | +1,543.95 |  |
| `2026-10-13` | +3,773.47 | +4,251.27 | +2,605.75 | +4,558.77 | widest split (V3B best, V3A worst) |
| `2026-10-14` | +1,106.80 | -410.41 | +4,155.46 | -135.17 | widest split (V3A best, V2 worst) |
| `2026-10-15` | +2,667.60 | +2,176.28 | +3,729.89 | +2,330.55 | widest split (V3A best, V2 worst) |
| `2026-10-16` | +4,421.04 | +2,368.72 | +7,638.41 | +2,425.16 | widest split (V3A best, V2 worst) |
| `2026-10-19` | -2,421.56 | -1,715.92 | -2,847.88 | -1,702.28 | widest split (V3B best, V3A worst) |
| `2026-10-20` | +2,273.84 | +1,981.94 | +2,968.90 | +1,981.94 | widest split (V3A best, V2 worst) |
| `2026-10-21` | -3,173.24 | -2,254.17 | -3,916.01 | -2,254.17 | widest split (V2 best, V3A worst) |
| `2026-10-22` | +8,371.26 | +5,784.87 | +13,670.25 | +5,784.87 | widest split (V3A best, V2 worst) |
| `2026-10-23` | +46,755.09 | +24,876.47 | +69,733.40 | +24,876.47 | Terminal mark; widest split (V3A best, V3B worst) |

## Where the Models Diverge

![Model spreads](Charts/performance/04-model-spreads.png)

![Compounding effect](Charts/performance/05-compounding-effect.png)

- **Stop-and-reverse (V1 − V2) ends at $24,717.32; (V3A − V3B) ends at $57,753.96.**
- **Compounding (V3A − V1) ends at $44,203.35** — the single largest structural effect in the book.

## Risk — Drawdown from Running Peak

![Drawdown](Charts/performance/06-drawdown.png)

| Model | Peak | Peak day | Trough | Trough day | Max drawdown | Max DD day | Best day | Worst day |
|---|---:|---|---:|---:|---|---:|---|---:|
| **Variant 1 — 1u Open** | $99,599.67 | `2026-10-23` | $3,121.67 | `2026-09-04` | -$3,479.09 | `2026-09-29` | $46,755.09 (`2026-10-23`) | -$3,479.09 (`2026-09-29`) |
| **Variant 2 — 1u SAR** | $74,882.36 | `2026-10-23` | $3,121.67 | `2026-09-04` | -$3,222.10 | `2026-09-29` | $24,876.47 (`2026-10-23`) | -$3,222.10 (`2026-09-29`) |
| **Variant 3A — Nu Open** | $143,803.02 | `2026-10-23` | $3,121.67 | `2026-09-04` | -$4,898.32 | `2026-09-30` | $69,733.40 (`2026-10-23`) | -$4,652.10 (`2026-09-29`) |
| **Variant 3B — Nu SAR** | $86,049.06 | `2026-10-23` | $3,121.67 | `2026-09-04` | -$3,222.10 | `2026-09-29` | $24,876.47 (`2026-10-23`) | -$3,222.10 (`2026-09-29`) |

## Terminal Composition

![Terminal composition](Charts/performance/07-terminal-composition.png)

| Model | Realized (closed) | Unrealized (open) | Closed lots | Open lots |
|---|---:|---:|---:|---:|
| **Variant 1 — 1u Open** | $25,561.44 | $74,038.24 | 15 | 68 |
| **Variant 2 — 1u SAR** | $31,385.57 | $43,496.78 | 20 | 63 |
| **Variant 3A — Nu Open** | $25,561.44 | $118,241.58 | 15 | 68 |
| **Variant 3B — Nu SAR** | $42,552.27 | $43,496.78 | 20 | 63 |

## Contribution by Ticker

![Ticker contribution](Charts/performance/08-ticker-contribution.png)

### The four divergence tickers

| Ticker | V1 | V2 | V3A | V3B |
|---|---:|---:|---:|---:|
| `CAT` | $2,831.28 | -$1,035.73 | $8,260.91 | $526.90 |
| `INTC` | $3,917.60 | -$9,301.20 | $36,097.60 | -$2,249.04 |
| `META` | $9,937.17 | $8,926.73 | $16,530.89 | $11,478.65 |
| `PLTR` | $25,627.43 | $19,006.37 | $25,627.43 | $19,006.37 |

### Top contributors (V3A)

| Ticker | Units | Realized | Unrealized | **Total** |
|---|---:|---:|---:|---:|
| `INTC` | 14u | $10,955.99 | $25,141.62 | **$36,097.60** |
| `PLTR` | 4u | $2,500.75 | $23,126.68 | **$25,627.43** |
| `LULU` | 1u | $0.00 | $17,646.94 | **$17,646.94** |
| `META` | 13u | $10,430.36 | $6,100.53 | **$16,530.89** |
| `ORCL` | 4u | $0.00 | $13,527.15 | **$13,527.15** |
| `SPCX` | 3u | $0.00 | $8,960.45 | **$8,960.45** |
| `CAT` | 5u | $1,984.84 | $6,276.07 | **$8,260.91** |
| `OIL` | 6u | $0.00 | $6,614.56 | **$6,614.56** |
| `LMT` | 4u | $0.00 | $5,296.12 | **$5,296.12** |
| `BRENT` | 5u | $0.00 | $5,026.57 | **$5,026.57** |

### Bottom contributors (V3A)

| Ticker | Units | Realized | Unrealized | **Total** |
|---|---:|---:|---:|---:|
| `GEV` | 1u | $0.00 | -$8,156.11 | **-$8,156.11** |
| `VLO` | 1u | $0.00 | -$6,632.87 | **-$6,632.87** |
| `V` | 1u | $0.00 | -$2,673.50 | **-$2,673.50** |
| `AMZN` | 1u | $0.00 | -$2,557.43 | **-$2,557.43** |
| `LLY` | 1u | $0.00 | -$2,239.27 | **-$2,239.27** |
| `RIVN` | 1u | $0.00 | -$1,727.27 | **-$1,727.27** |
| `UPS` | 2u | $0.00 | -$1,422.48 | **-$1,422.48** |
| `NVDA` | 1u | $0.00 | -$811.45 | **-$811.45** |
| `NET` | 1u | $0.00 | -$206.26 | **-$206.26** |
| `NFLX` | 1u | $0.00 | -$180.44 | **-$180.44** |

## Intraday — Hour by Hour

Daily closes hide *when* inside a session the models pull apart. Zooming to **hourly bars** (7 per session: `06:30`→`13:00 MST`) resolves that.

> **Scope:** the intraday view covers **`CAT`, `INTC`, `META` and `PLTR`** — the divergence sub-book. The other `29` tickers produce byte-identical PnL under all four models, so they cancel exactly out of every comparison below. Every number here is therefore *exact*, not interpolated.

![Intraday divergence sub-book](Charts/performance/09-intraday-sub-book-pnl.png)

### Terminal, divergence sub-book only

| Model | Realized | Unrealized | **Sub-book total** |
|---|---:|---:|---:|
| **Variant 1 — 1u Open** | $25,871.93 | $1,195.66 | **$27,067.59** |
| **Variant 2 — 1u SAR** | $31,696.07 | -$7,467.17 | **$24,228.90** |
| **Variant 3A — Nu Open** | $25,871.93 | $22,420.70 | **$48,292.63** |
| **Variant 3B — Nu SAR** | $42,862.77 | -$7,467.17 | **$35,395.60** |

The sub-book totals differ from the full-portfolio totals above by exactly the 29 invariant tickers, which contribute the same amount to every model.

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

## 1-Minute Close-Up — INTC Hazard-Flip Window

A focused **60-bar, one-minute** view around the Sep 24 `10:00 MST` INTC short. This is a zoom into one high-signal hour, not a replacement for the 35-session hourly sub-book. The lower panel carries INTC-only cumulative realized + open PnL for each model; V1/V2 and V3A/V3B overlap here because their SAR paths have not yet diverged on this date.

![INTC one-minute hazard-flip close-up](Charts/performance/13-minute-intc-hazard-flip.png)

**Data-quality flag:** Yahoo's first close after the logged event is **$125.59** at `10:01 MST`, while the trade log records **$115.11** (a **$10.48 / 9.1%** difference). The PnL panel preserves the book's logged entry price; it does not silently reprice or correct the trade. Minute series: [`model_performance_minute_intc.csv`](data/model_performance_minute_intc.csv) (60 rows).

## Method & Caveats

- **Model coverage:** the four variants directly price the `33` symbols with configured daily market series. `88` price-covered events dated on or before the Oct. 23 mark are replayed; `0` price-covered events after the mark are excluded from this current daily replay. `7` DXY, EURUSD, JPYUSD, US10Y and US30Y log events are not replayed as standalone price positions. The two US10Y events establish yield-adjustment context; this report's additive carry is retained only as a legacy reference. Whole-account US10Y and compounded US30Y multiplier scenarios are in the DXY snapshot and linked explorer. DXY/FX/US30Y positions remain outside the four direct-price variants and require their own quote/valuation treatment.
- **Price source:** cached Yahoo Finance histories provide pre-entry context (`BRENT = BZ=F`, `OIL = CL=F`, `BTC = BTC-USD`, `ETH = ETH-USD`). Exact user-provided BlackBull Brent Cash and TVC:USOIL EOD marks override the energy proxies from the first active position date through Oct. 23. Other Oct. 23 endpoints use the consolidated v7 file's per-ticker `Source` labels. LCID retains its separate pilot mark series, which matches the user-corrected consolidated mark at $3.52. `BZ=F`/`CL=F` are only pre-entry context proxies.
- **Oct. 23 price reconciliation:** `data/consolidated_portfolio_closes_v7.csv` is the active close set; v1 through v6 remain preserved. Earlier audits record selected v1 marks for CVX `$233.21`, WMT `$119.89`, TMO `$673.82`, and UPS `$101.06`. User-provided exact energy EOD values are in [`data/energy_provider_eod_marks_v1.csv`](data/energy_provider_eod_marks_v1.csv); the v6-to-v7 audit records the endpoint changes. Exact marks begin on each instrument's first active position date; pre-entry context remains a futures proxy. The active source map is [`data/active_price_source_registry_v2.csv`](data/active_price_source_registry_v2.csv). The saved TradingView/Yahoo comparison candidate remains audit-only. DXY, FX, and yield inputs remain local user-provided daily series and are not independently provider-verified.
- **Approximate energy quotes (separate overlay):** their open-lot calculations versus the exact user-provided EOD marks are in [`data/energy_live_mark_overlay.csv`](data/energy_live_mark_overlay.csv). They remain excluded from model totals.
- **Session calendar:** the `36` U.S. equity regular sessions from `2026-09-03` to `2026-10-23`. Futures and crypto are mapped onto the same session index by trade date.
- **`XRH0`** (db Physical Rhodium ETC, LSE) is too illiquid for a usable daily history, so it remains at the `$790.00` log-entry mark through Oct. 22; the user-corrected Oct. 23 endpoint is `$785.00`. No interim daily prices are invented.
- **Oct. 22 historical marks** remain pinned to the verified settlement set from [`Trades Zip PnL.md`](Trades%20Zip%20PnL.md); the Oct. 23 endpoint uses the user-supplied EOD file above. The Oct. 23 ORCL and LCID entries are now included at that date's close. The master PnL report remains unrecalculated and unreconciled; do not interpret this model replay as a refresh of its totals.
- **ROI** is cumulative PnL divided by notional deployed *to date* (units opened on or before that session × `$10,000`), so early sessions show larger percentages on less capital.
- Entry fills use the log's own market prices, not session closes; exits are realised on their log date.
- Excludes commissions, borrow fees, and overnight financing.

---

Master ledger: **[`Trades Zip PnL.md`](Trades%20Zip%20PnL.md)** · Chart-signal report: **[`Triangle Signals.md`](Triangle%20Signals.md)** · Visual book: **[`Unrealized PnL.md`](Unrealized%20PnL.md)** · Pre-2026: **[`2024 Trades PnL.md`](reports/2024/2024%20Trades%20PnL.md)**
