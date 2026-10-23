# Model Performance Comparison — *Fall (Arizona) [2026]*

Day-by-day (and, where market data supports it, intraday) comparison of the four portfolio models carried on the same standardized book: **[`trades/`](trades/)** / **[`trades.zip`](trades.zip)** — `32` price-covered symbols, `82` modeled log events out of `89` total 2026 log events, `1 unit = $10,000.00` initial notional, all timestamps in Arizona year-round **`MST` / `UTC-07:00`**, marked against the **Thursday, October 22, 2026** close.

> **Interactive version:** open **[`Model Performance Explorer.html`](Model%20Performance%20Explorer.html)** for a self-contained explorer with toggleable series, a hover crosshair, and per-ticker breakdowns. Machine-readable exports live in [`data/`](data/): [`model_performance_daily.csv`](data/model_performance_daily.csv), [`model_performance_tickers.csv`](data/model_performance_tickers.csv), [`model_performance_summary.json`](data/model_performance_summary.json).
> **Whole-portfolio DXY view:** **[`DXY-Equivalent Portfolio Snapshot.md`](DXY-Equivalent%20Portfolio%20Snapshot.md)** documents the corrected numeraire method and the remaining daily EUR/USD and JPY/USD closes needed for the requested graph.

## The Four Models

| Model | Rule | Units deployed | Realized | Unrealized | Base PnL | US10Y adjustment | **Adjusted PnL** | **Adjusted ROI** |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| **Variant 1 — 1u Open** | every line is 1 unit; positions stay open | 77u ($770,000) | $25,561.44 | $23,158.21 | $48,719.64 | $158.44 | **$48,878.08** | **6.35%** |
| **Variant 2 — 1u SAR** | every line is 1 unit; LONG/REBUY stops-and-reverses open shorts | 77u ($770,000) | $31,385.57 | $14,495.38 | $45,880.95 | $158.44 | **$46,039.39** | **5.98%** |
| **Variant 3A — Nu Open** | compounded shorts sized to the preceding full exit; positions stay open | 86u ($860,000) | $25,561.44 | $44,383.25 | $69,944.68 | $181.43 | **$70,126.12** | **8.15%** |
| **Variant 3B — Nu SAR** | compounded shorts *and* stop-and-reverse | 86u ($860,000) | $42,552.27 | $14,495.38 | $57,047.65 | $181.43 | **$57,229.09** | **6.65%** |

## US10Y Baseline Adjustment

This user-requested, yield-based inflation-style carry is a model adjustment, not a CPI inflation measure or a Treasury total-return calculation. It treats the user-provided daily US10Y closes as annualized carry relative to the `4.865%` baseline from `2026-09-10`. For each interval, the adjustment is the model's cumulative deployed notional (the same denominator used for ROI; it does not fall after a position closes) × ((yield close − 4.865) / 100) × actual calendar days / 365. Values above baseline add positive adjustment; below baseline subtract. Per your confirmation, the Oct 9 close (5.24%) is carried across the Oct 12 Treasury holiday; the export records the original source date. The Oct 23 screenshot yield is kept separate from Oct 22 historical model totals.

![US10Y yield baseline and cumulative adjustment](Charts/performance/15-us10y-baseline-adjustment.png)

Session-level rates, forward-fill dates, actual/365 accruals, and adjusted totals: [`model_performance_us10y_adjustment.csv`](data/model_performance_us10y_adjustment.csv).

## Energy Ticker Update — Separate Oct 23 Snapshot

> This energy-only update is **not** part of the Oct 22 portfolio totals above. BRENT and OIL use the approximate user-provided Oct 23 marks; provider and quote time were not specified. Historical marks are Oct 22 Yahoo futures proxies, not guaranteed cash/CFD matches.

![Separate energy mark and PnL comparison](Charts/performance/14-energy-live-mark-overlay.png)

Detailed marks and calculations: [`data/energy_live_mark_overlay.csv`](data/energy_live_mark_overlay.csv).

All four models agree on `28` of the `32` tickers. They diverge only on **`CAT`, `INTC`, `META` and `PLTR`** — the four symbols where a short is followed by a long (or a full exit is compounded into a short). Everything below is driven by those four.

## Headline Chart

![Cumulative base trading PnL by session](Charts/performance/01-cumulative-pnl-by-session.png)

**Reading it:** the models begin close together, then spread as the reversal-sensitive positions develop. At the Oct 22 mark both the base and US10Y-adjusted dollar rankings are **V3A > V3B > V1 > V2**.

## Base Return on Capital

![Cumulative base ROI by session](Charts/performance/02-cumulative-roi-by-session.png)

This chart shows trading PnL before the US10Y carry; the adjusted ROI is shown in the model table above and is selectable in the interactive explorer.

Raw dollars flatter V3A/V3B because they deploy more capital — `86` units (`$860,000.00`) against V1/V2's `77` units (`$770,000.00`). ROI normalises for that, and the terminal ranking is unchanged: compounding shorts into full exits beats flat sizing on both capital bases, and *not* stop-and-reversing beats stop-and-reversing on both.

## Day-by-Day Moves

![Day-by-day PnL change](Charts/performance/03-daily-pnl-change.png)

| Session | V1 | V2 | V3A | V3B | Note |
|---|---:|---:|---:|---:|---|
| `2026-09-03` | +3,439.92 | +3,439.92 | +3,439.92 | +3,439.92 | Season open |
| `2026-09-04` | -318.25 | -318.25 | -318.25 | -318.25 |  |
| `2026-09-08` | +440.82 | +440.82 | +440.82 | +440.82 |  |
| `2026-09-09` | +1,097.81 | +1,097.81 | +1,097.81 | +1,097.81 |  |
| `2026-09-10` | -399.19 | -399.19 | -399.19 | -399.19 |  |
| `2026-09-11` | +1,406.43 | +1,406.43 | +1,406.43 | +1,406.43 |  |
| `2026-09-14` | -393.25 | -64.44 | -393.25 | -64.44 |  |
| `2026-09-15` | -792.08 | -832.64 | -792.08 | -832.64 |  |
| `2026-09-16` | +466.73 | +563.00 | +466.73 | +563.00 |  |
| `2026-09-17` | +5,158.63 | +5,261.38 | +5,158.63 | +5,261.38 |  |
| `2026-09-18` | -212.25 | -136.54 | -212.25 | -136.54 |  |
| `2026-09-21` | +14,473.56 | +14,768.30 | +14,473.56 | +14,768.30 |  |
| `2026-09-22` | +2,805.00 | +2,907.75 | +3,827.74 | +3,930.49 | widest split (V3B best, V1 worst) |
| `2026-09-23` | -1,059.98 | -692.24 | -663.48 | -295.73 | widest split (V3B best, V1 worst) |
| `2026-09-24` | +1,229.60 | +1,272.86 | -700.39 | -657.13 | widest split (V2 best, V3A worst) |
| `2026-09-25` | +1,073.31 | +1,322.04 | +3,802.74 | +5,678.07 | widest split (V3B best, V1 worst) |
| `2026-09-28` | +2,055.78 | +3,344.59 | +6,122.68 | +9,103.39 | widest split (V3B best, V1 worst) |
| `2026-09-29` | -2,915.77 | -2,658.79 | -4,088.78 | -2,658.79 | widest split (V2 best, V3A worst) |
| `2026-09-30` | +116.01 | +655.30 | -529.64 | +655.30 | widest split (V2 best, V3A worst) |
| `2026-10-01` | +2,200.22 | +2,333.59 | +2,233.61 | +2,333.59 |  |
| `2026-10-02` | -582.11 | -734.85 | -483.04 | -734.85 |  |
| `2026-10-05` | -550.56 | -855.61 | -280.86 | -855.61 | widest split (V3A best, V2 worst) |
| `2026-10-06` | +1,365.84 | +860.12 | +2,698.60 | +874.69 | widest split (V3A best, V2 worst) |
| `2026-10-07` | -1,781.81 | -1,796.64 | -489.82 | -1,222.92 | widest split (V3A best, V2 worst) |
| `2026-10-08` | +4,948.39 | +4,195.06 | +7,075.06 | +4,399.17 | widest split (V3A best, V2 worst) |
| `2026-10-09` | -57.60 | +74.95 | +757.15 | +25.34 | widest split (V3A best, V1 worst) |
| `2026-10-12` | +2,239.07 | +1,997.46 | +2,043.29 | +2,010.18 |  |
| `2026-10-13` | +2,647.45 | +3,125.25 | +1,479.74 | +3,432.75 | widest split (V3B best, V3A worst) |
| `2026-10-14` | +1,708.59 | +191.38 | +4,757.26 | +466.62 | widest split (V3A best, V2 worst) |
| `2026-10-15` | +3,085.92 | +2,594.60 | +4,148.22 | +2,748.87 | widest split (V3A best, V2 worst) |
| `2026-10-16` | +5,454.72 | +3,402.40 | +8,672.09 | +3,458.84 | widest split (V3A best, V2 worst) |
| `2026-10-19` | -86.60 | +619.04 | -512.92 | +632.68 | widest split (V3B best, V3A worst) |
| `2026-10-20` | -1,186.21 | -1,478.11 | -491.15 | -1,478.11 | widest split (V3A best, V2 worst) |
| `2026-10-21` | -5,401.29 | -4,482.21 | -6,144.05 | -4,482.21 | widest split (V2 best, V3A worst) |
| `2026-10-22` | +7,042.80 | +4,456.41 | +12,341.78 | +4,456.41 | Terminal mark; widest split (V3A best, V2 worst) |

## Where the Models Diverge

![Model spreads](Charts/performance/04-model-spreads.png)

![Compounding effect](Charts/performance/05-compounding-effect.png)

- **Stop-and-reverse (V1 − V2) ends at $2,838.69; (V3A − V3B) ends at $12,897.03.**
- **Compounding (V3A − V1) ends at $21,225.04** — the single largest structural effect in the book.

## Risk — Drawdown from Running Peak

![Drawdown](Charts/performance/06-drawdown.png)

| Model | Peak | Peak day | Trough | Trough day | Max drawdown | Max DD day | Best day | Worst day |
|---|---:|---|---:|---:|---|---:|---|---:|
| **Variant 1 — 1u Open** | $48,719.64 | `2026-10-22` | $3,121.67 | `2026-09-04` | -$6,674.10 | `2026-10-21` | $14,473.56 (`2026-09-21`) | -$5,401.29 (`2026-10-21`) |
| **Variant 2 — 1u SAR** | $47,384.86 | `2026-10-19` | $3,121.67 | `2026-09-04` | -$5,960.32 | `2026-10-21` | $14,768.30 (`2026-09-21`) | -$4,482.21 (`2026-10-21`) |
| **Variant 3A — Nu Open** | $69,944.68 | `2026-10-22` | $3,121.67 | `2026-09-04` | -$7,148.13 | `2026-10-21` | $14,473.56 (`2026-09-21`) | -$6,144.05 (`2026-10-21`) |
| **Variant 3B — Nu SAR** | $58,551.56 | `2026-10-19` | $3,121.67 | `2026-09-04` | -$5,960.32 | `2026-10-21` | $14,768.30 (`2026-09-21`) | -$4,482.21 (`2026-10-21`) |

## Terminal Composition

![Terminal composition](Charts/performance/07-terminal-composition.png)

| Model | Realized (closed) | Unrealized (open) | Closed lots | Open lots |
|---|---:|---:|---:|---:|
| **Variant 1 — 1u Open** | $25,561.44 | $23,158.21 | 15 | 62 |
| **Variant 2 — 1u SAR** | $31,385.57 | $14,495.38 | 20 | 57 |
| **Variant 3A — Nu Open** | $25,561.44 | $44,383.25 | 15 | 62 |
| **Variant 3B — Nu SAR** | $42,552.27 | $14,495.38 | 20 | 57 |

## Contribution by Ticker

![Ticker contribution](Charts/performance/08-ticker-contribution.png)

### The four divergence tickers

| Ticker | V1 | V2 | V3A | V3B |
|---|---:|---:|---:|---:|
| `CAT` | $3,492.78 | $3,197.53 | $5,350.65 | $4,760.15 |
| `INTC` | $11,144.66 | $7,964.53 | $24,241.98 | $15,016.69 |
| `META` | $10,029.34 | $9,099.86 | $16,299.19 | $11,651.78 |
| `PLTR` | $2,400.81 | $3,966.98 | $2,400.81 | $3,966.98 |

### Top contributors (V3A)

| Ticker | Units | Realized | Unrealized | **Total** |
|---|---:|---:|---:|---:|
| `INTC` | 14u | $10,955.99 | $13,285.99 | **$24,241.98** |
| `META` | 13u | $10,430.36 | $5,868.83 | **$16,299.19** |
| `LMT` | 4u | $0.00 | $5,880.21 | **$5,880.21** |
| `CAT` | 5u | $1,984.84 | $3,365.81 | **$5,350.65** |
| `OIL` | 6u | $0.00 | $4,051.72 | **$4,051.72** |
| `BRENT` | 5u | $0.00 | $3,068.78 | **$3,068.78** |
| `SPCX` | 3u | $0.00 | $2,929.12 | **$2,929.12** |
| `BTC` | 2u | $0.00 | $2,920.54 | **$2,920.54** |
| `CVX` | 3u | $0.00 | $2,470.96 | **$2,470.96** |
| `PLTR` | 4u | $2,500.75 | -$99.94 | **$2,400.81** |

### Bottom contributors (V3A)

| Ticker | Units | Realized | Unrealized | **Total** |
|---|---:|---:|---:|---:|
| `GEV` | 1u | $0.00 | -$1,779.81 | **-$1,779.81** |
| `RIVN` | 1u | $0.00 | -$1,566.43 | **-$1,566.43** |
| `UPS` | 2u | $0.00 | -$1,519.99 | **-$1,519.99** |
| `DIS` | 2u | -$310.50 | -$853.88 | **-$1,164.38** |
| `NET` | 1u | $0.00 | -$871.34 | **-$871.34** |
| `NVDA` | 1u | $0.00 | -$757.00 | **-$757.00** |
| `AMZN` | 1u | $0.00 | -$317.12 | **-$317.12** |
| `ORCL` | 1u | $0.00 | -$209.78 | **-$209.78** |
| `ETH` | 1u | $0.00 | -$190.39 | **-$190.39** |
| `TSLA` | 1u | $0.00 | -$177.15 | **-$177.15** |

## Intraday — Hour by Hour

Daily closes hide *when* inside a session the models pull apart. Zooming to **hourly bars** (7 per session: `06:30`→`13:00 MST`) resolves that.

> **Scope:** the intraday view covers **`CAT`, `INTC`, `META` and `PLTR`** — the divergence sub-book. The other `28` tickers produce byte-identical PnL under all four models, so they cancel exactly out of every comparison below. Every number here is therefore *exact*, not interpolated.

![Intraday divergence sub-book](Charts/performance/09-intraday-sub-book-pnl.png)

### Terminal, divergence sub-book only

| Model | Realized | Unrealized | **Sub-book total** |
|---|---:|---:|---:|
| **Variant 1 — 1u Open** | $25,871.93 | $1,195.66 | **$27,067.59** |
| **Variant 2 — 1u SAR** | $31,696.07 | -$7,467.17 | **$24,228.90** |
| **Variant 3A — Nu Open** | $25,871.93 | $22,420.70 | **$48,292.63** |
| **Variant 3B — Nu SAR** | $42,862.77 | -$7,467.17 | **$35,395.60** |

The sub-book totals differ from the full-portfolio totals above by exactly the 28 invariant tickers, which contribute the same amount to every model.

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

Per-ticker intraday contribution at the Oct 22 close:

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

- **Model coverage:** the four variants directly price the `32` symbols with configured daily market series. `7` log events for DXY, EURUSD, JPYUSD, US10Y and US30Y are not replayed as standalone price positions. The two US10Y events establish the yield-adjustment context; its separate daily rate series applies the baseline carry to the portfolio. DXY/FX/US30Y positions remain outside the four direct-price variants and require their own quote/valuation treatment.
- **Price source:** Yahoo Finance `v8/finance/chart` `interval=1d` for all `32` symbols (`BRENT = BZ=F` Brent futures proxy, `OIL = CL=F` WTI futures proxy, `BTC = BTC-USD`, `ETH = ETH-USD`); pulled 2026-10-23. `BZ=F`/`CL=F` are not exact matches for the trade metadata's Brent Cash / ICE Brent and `TVC:USOIL` WTI CFD instruments.
- **Oct 22 equity EOD recheck:** all `26` stock symbols and the `XLE` ETF were checked against Yahoo Finance daily chart closes on Oct 23. `NET` was corrected from `$306.60` to `$303.61`; the full symbol/source audit is in [`data/oct22_equity_eod_recheck.csv`](data/oct22_equity_eod_recheck.csv).
- **Live energy marks (separate snapshot):** the approximate Oct 23 user-provided quotes and their open-lot calculations are in [`data/energy_live_mark_overlay.csv`](data/energy_live_mark_overlay.csv). They do not alter this Oct 22 historical comparison.
- **Session calendar:** the `35` U.S. equity regular sessions from `2026-09-03` to `2026-10-22`. Futures and crypto are mapped onto the same session index by trade date.
- **`XRH0`** (db Physical Rhodium ETC, LSE) is too illiquid for a usable daily history, so it is held flat at its `$790.00` log entry — matching the [`Trades Zip PnL.md`](Trades%20Zip%20PnL.md) convention.
- **Terminal marks** on `2026-10-22` use the verified settlement set from [`Trades Zip PnL.md`](Trades%20Zip%20PnL.md). This comparison now includes the newly reconciled chart positions for model-priced symbols; the master PnL report has not been recalculated in this update, so its totals will not currently reconcile to this comparison.
- **ROI** is cumulative PnL divided by notional deployed *to date* (units opened on or before that session × `$10,000`), so early sessions show larger percentages on less capital.
- Entry fills use the log's own market prices, not session closes; exits are realised on their log date.
- Excludes commissions, borrow fees, and overnight financing.

---

Master ledger: **[`Trades Zip PnL.md`](Trades%20Zip%20PnL.md)** · Chart-signal report: **[`Triangle Signals.md`](Triangle%20Signals.md)** · Visual book: **[`Unrealized PnL.md`](Unrealized%20PnL.md)** · Pre-2026: **[`2024 Trades PnL.md`](2024%20Trades%20PnL.md)**
