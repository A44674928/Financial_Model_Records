# Paper Trades — Repository Guide

This repository contains the Fall (Arizona) 2026 paper-trading ledger, model analysis, source records, and supporting research. The daily model and whole-portfolio comparisons run through the **October 23, 2026** EOD close. Intraday plots and explicitly historical reports retain their stated earlier cutoffs.

## Start here

- [Model Performance Comparison](Model%20Performance%20Comparison.md) — four-model daily and intraday comparison.
- [Model Performance Explorer](Model%20Performance%20Explorer.html) — interactive view of model results.
- [Trades Zip PnL](Trades%20Zip%20PnL.md) — master historical PnL report; see its scope note for reconciliation status.
- [Whole-Portfolio DXY Snapshot](DXY-Equivalent%20Portfolio%20Snapshot.md) — USD and DXY-numeraire comparison.
- [Small Caps pilot](Small%20Caps%20%5BBuyout%20%26%20Reorganization%20Offering%20Test%20Pilot%5D.md) — LCID Buyout & Reorganization Offering test basket.
- [Chart Archive Review](Chart%20Archive%20Review.md), [Triangle Signals](Triangle%20Signals.md), and [Unrealized PnL](Unrealized%20PnL.md) — source reconciliation and focused trade views.

## Repository layout

- `trades/` — standardized symbol ledgers; `trades/2024/` holds the separate 2024 cohort; its [standalone PnL report](reports/2024/2024%20Trades%20PnL.md) is organized under `reports/`.
- `trades.zip` — synchronized archive of the `trades/` tree.
- `Charts/` — original and labeled chart images, plus generated performance charts.
- `Archive/` — source screenshot archives and duplicate captures.
- `reports/` — historical standalone reports, including the 2024 trade report.
- `data/` — user-provided input series, audit tables, and generated model exports. The active Oct. 23 close set is [`consolidated_portfolio_closes_v6.csv`](data/consolidated_portfolio_closes_v6.csv). Versioned v1–v5 close sets and reconciliation audits through v5→v6 are preserved under `data/`. The active source map is [`active_price_source_registry_v1.csv`](data/active_price_source_registry_v1.csv). The chart-price transcription input is [`current_price_points.csv`](data/current_price_points.csv).
- `scripts/` — model engines, report builders, and chart-label tooling.
- `tests/` — regression tests for the ledgers, marks, model calculations, and generated outputs.
- `research/` — topical research reports and working notes, grouped by subject.
- `references/` — standalone reference documents, including the supplied ledger PDF.

## Rebuilds

Run the relevant builder from the repository root:

```bash
PYTHONPATH=scripts python3 scripts/build_model_performance.py
PYTHONPATH=scripts python3 scripts/build_whole_portfolio_dxy_view.py
PYTHONPATH=scripts python3 scripts/build_small_caps_pilot.py
```

Some chart-generation and test dependencies (for example, Matplotlib and Pillow) may need to be installed in the local environment first.
