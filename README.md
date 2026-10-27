# Paper Trades — Repository Guide

This repository contains the Fall (Arizona) 2026 paper-trading ledger, model analysis, source records, and supporting research. The refreshed model comparison uses the supplied TradingView benchmark through the **October 23, 2026** EOD close: 31 direct-price core symbols plus an integrated 1U/DAY/DXY index-return sleeve; BTC/ETH remain pending recalibration. Four separate manual 10U LONG oil replenishment entries (two per ticker) are logged on Oct. 25: the $115.792 BRENT/$101.74 OIL lots use the user-recalled 17:20–17:25 MST window, modeled at a 17:22 MST midpoint, and the $114.80 BRENT/$101.00 OIL lots use an approximate 20:00 MST timestamp per the user's recollection. At 20:35 MST, additional Weekend Oil buys of 35U BRENT at $114.627 and 34U OIL at $100.74 are modeled simultaneously with closing the separate 10U SHORT lots. The 35U/34U LONG lots count toward weekly buy supply; the short closures do not. Against the 65U BRENT + 66U OIL existing all-core long exposure after the modeled short closes, they bring the total to 100U per ticker, 200U combined ($2,000,000 fixed-unit notional). These post-cutoff events are excluded from current PnL pending later EOD marks. The short exits override SAR only for the tagged shorts; prices/timing are hypothetical model assumptions, not verified executions. THE ONE MODEL adds the 10U/DAY DXY schedule to each of its 32 independent portfolios, for 11U/DAY combined DXY exposure; its 16 energy-inclusive portfolios use 11U/DAY per active BRENT and OIL ticker, matching that combined currency size. The 16 no-energy variants remain in the split. The 0.05U DXY schedule remains an alternative. Other strategy-comparison scopes are unchanged. Legacy whole-portfolio DXY/yield views are explicitly historical and retain their previous benchmark.

## Start here

- [Model Performance Comparison](Model%20Performance%20Comparison.md) — four-model daily and intraday comparison.
- [Core Portfolio Asset Breakdown](Core%20Portfolio%20Asset%20Breakdown.md) — open long/short exposures, asset concentration, and PnL by ticker across the four core variants.
- [THE ONE MODEL vs THE WINNING MODEL](THE%20ONE%20MODEL%20vs%20THE%20WINNING%20MODEL.md) — equal-gross comparison of the 32-portfolio aggregate and its ex-post top terminal-PnL constituent.
- [TWM Chart-to-Model Series — Clean-Sheet Specification](TWM%20Chart-to-Model%20Series%20%E2%80%94%20Clean-Sheet%20Specification.md) — private-chart intake, TWM_1M/TWM_20B boundaries, and optional accumulator rules.
- [THE ONE MODEL — Winning Model and Contender Specification](THE%20ONE%20MODEL%20%E2%80%94%20Winning%20Model%20and%20Contender%20Specification.md) — current champion, all 32 candidates, and how future models such as V4 can contend.
- [THE ONE MODEL (TOM) — Clean-Sheet Specification](THE%20ONE%20MODEL%20%28TOM%29%20%E2%80%94%20Clean-Sheet%20Specification.md) — TOM construction, winner rules, and aggregate vs per-constituent $1K/$10K sizing.
- [TOM / TWM 1K–10K ROI Design Sheet — 2026-10-26](reports/TOM-TWM%201K-10K%20ROI%20Design%20Sheet%20%E2%80%94%202026-10-26.md) — $1K/$10K projections for V3A core-only, DXY-free, LMT-only, BRENT-only, TWM, and TOM aggregate/per-member designs.
- [Weightless Randomized Demo Portfolios — 2026-10-26](reports/Weightless%20Randomized%20Demo%20Portfolios%20%E2%80%94%202026-10-26.md) — fixed-seed equal-dollar mixed compositions, daily aggregate paths, and a composition-agnostic accounting demonstration (not a profitability forecast).
- [Model Performance Explorer](Model%20Performance%20Explorer.html) — interactive view of model results.
- [Model Calculation Guide](Model%20Calculation%20Guide.md) — plain-language unit sizing, daily position handling, reversal logic, and PnL formulas.
- [Oil Cost Basis Savings Model](Oil%20Cost%20Basis%20Savings%20Model.md) — realized target-trim and modeled SHORT-exit PnL credited once to the effective basis of the residual and replenishment lots, mapped across all 32 portfolios.
- [Trades Zip PnL](Trades%20Zip%20PnL.md) — master historical PnL report; see its scope note for reconciliation status.
- [TradingView Energy and Currency Desk Sidecars](TradingView%20Energy%20and%20Currency%20Desk%20Sidecars.md) — standard 10U energy and DXY sizing schedules; the THE ONE MODEL uses a derived 11U/DAY energy tranche per active ticker, while its 1U/DAY core DXY sleeve plus 10U/DAY add-on gives 11U/day combined currency exposure.
- [Crypto Sidecar — Pending TradingView Recalibration](Crypto%20Sidecar%20%E2%80%94%20Pending%20TradingView%20Recalibration.md) — BTC/ETH excluded until source calibration.
- [Small Caps pilot](Small%20Caps%20%5BBuyout%20%26%20Reorganization%20Offering%20Test%20Pilot%5D.md) — LCID Buyout & Reorganization Offering test basket.
- [Strategy and Sidecar Comparison](Strategy%20and%20Sidecar%20Comparison.md) — standard variants, $500 and shared/variant-specific 1U/EOD models, 10U TradingView energy sidecar, and composites.
- [Chart Archive Review](Chart%20Archive%20Review.md), [Triangle Signals](Triangle%20Signals.md), and [Unrealized PnL](Unrealized%20PnL.md) — source reconciliation and focused trade views.

## Repository layout

- `trades/` — standardized symbol ledgers; `trades/2024/` holds the separate 2024 cohort; its [standalone PnL report](reports/2024/2024%20Trades%20PnL.md) is organized under `reports/`.
- `trades.zip` — synchronized archive of the `trades/` tree.
- `Charts/` — original and labeled chart images, plus generated performance charts.
- `Archive/` — source screenshot archives and duplicate captures.
- `reports/` — historical standalone reports, including the 2024 trade report.
- `data/` — user-provided input series, audit tables, and generated model exports. The active core benchmark is [`tradingview_benchmark_session_marks_20261024.csv`](data/tradingview_benchmark_session_marks_20261024.csv), with raw lists, source manifests, and coverage tables beside it. Five provisional XRH0 carry-forwards are flagged; BTC/ETH are omitted from the core, while a chart-directed 1U/DAY/DXY index-return sleeve is integrated into core PnL without treating DXY as a direct-price ticker. Legacy close sets are preserved for historical audits only.
- `scripts/` — TradingView import/alignment tools, the core replay, energy/DXY sidecar builders, composite builders, and audit tooling. `build_oil_desk_hypothetical.py` is retained for the historical superseded schedule only.
- `tests/` — regression tests for the ledgers, marks, model calculations, and generated outputs.
- `research/` — topical research reports and working notes, grouped by subject.
- `references/` — standalone reference documents, including the supplied ledger PDF.

## Rebuilds

Run the relevant builder from the repository root:

```bash
# Benchmark source files are already imported and preserved in data/.
PYTHONPATH=scripts python3 scripts/build_tradingview_benchmark.py
PYTHONPATH=scripts python3 scripts/build_tradingview_sidecars.py
PYTHONPATH=scripts python3 scripts/build_model_performance.py
PYTHONPATH=scripts python3 scripts/build_core_asset_breakdown.py
PYTHONPATH=scripts python3 scripts/build_strategy_sidecar_comparison.py
PYTHONPATH=scripts python3 scripts/build_the_one_model_split_portfolios.py
python3 scripts/build_weightless_randomized_demo_portfolios.py
PYTHONPATH=scripts python3 scripts/build_weekend_oil_50u_positions.py
PYTHONPATH=scripts python3 scripts/build_oil_cost_basis_savings.py
PYTHONPATH=scripts python3 scripts/audit_actionable_tickers.py
```

Do not rebuild the historical whole-portfolio DXY/yield pages as if they were current TradingView results; their local FX/yield inputs and portfolio basis remain historical.

Some chart-generation and test dependencies (for example, Matplotlib and Pillow) may need to be installed in the local environment first.
