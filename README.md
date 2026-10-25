# Paper Trades — Repository Guide

This repository contains the Fall (Arizona) 2026 paper-trading ledger, model analysis, source records, and supporting research. The refreshed model comparison uses the supplied TradingView benchmark through the **October 23, 2026** EOD close: 31 direct-price core symbols plus an integrated 1U/DAY/DXY index-return sleeve; BTC/ETH remain pending recalibration. DXY sizing alternatives are documented in the currency-desk sidecar report. Legacy whole-portfolio DXY/yield views are explicitly historical and retain their previous benchmark.

## Start here

- [Model Performance Comparison](Model%20Performance%20Comparison.md) — four-model daily and intraday comparison.
- [Model Performance Explorer](Model%20Performance%20Explorer.html) — interactive view of model results.
- [Model Calculation Guide](Model%20Calculation%20Guide.md) — plain-language unit sizing, daily position handling, reversal logic, and PnL formulas.
- [Trades Zip PnL](Trades%20Zip%20PnL.md) — master historical PnL report; see its scope note for reconciliation status.
- [TradingView Energy and Currency Desk Sidecars](TradingView%20Energy%20and%20Currency%20Desk%20Sidecars.md) — energy and DXY daily-investment schedules; the 1U/DAY/DXY sleeve is already included in core totals.
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
PYTHONPATH=scripts python3 scripts/build_strategy_sidecar_comparison.py
PYTHONPATH=scripts python3 scripts/build_the_one_model_split_portfolios.py
PYTHONPATH=scripts python3 scripts/audit_actionable_tickers.py
```

Do not rebuild the historical whole-portfolio DXY/yield pages as if they were current TradingView results; their local FX/yield inputs and portfolio basis remain historical.

Some chart-generation and test dependencies (for example, Matplotlib and Pillow) may need to be installed in the local environment first.
