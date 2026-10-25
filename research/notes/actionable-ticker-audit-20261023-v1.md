# All-actionable-ticker reconciliation — Oct. 23, 2026

> **Historical audit — superseded by the TradingView recalculation of 2026-10-24.** This note documents the preceding 33-ticker/88-event benchmark and its 32-portfolio totals. For the current 31-ticker/85-event audit, use [`data/actionable_ticker_reconciliation_20261023_v1.csv`](../../data/actionable_ticker_reconciliation_20261023_v1.csv) and the refreshed [model report](../../Model%20Performance%20Comparison.md).

## Scope and outcome

An independent replay checked every actionable symbol in the active price universe through the Oct. 23 endpoint: **33 tickers, 36 sessions, 88 logged trade events**. It rebuilt the four core variants, the four variant-specific 1U/EOD schedules, shared-direction 1U/EOD, and fixed-$500/EOD; checked daily and position exports; independently recalculated all 55 exact oil-sidecar marks; and reconciled all 32 Core × 1U/EOD pairings, with and without the separate oil sidecar.

**All ticker marks, position quantities, realized/unrealized PnL, daily schedules, and the 32-portfolio aggregate now reconcile to the source exports within the stated cent-rounding tolerances.** There was no second endpoint mark replacement: the v7-to-v8 close audit still identifies LULU alone as changed. This validates arithmetic and source consistency against the repository's stated marks; it does not independently certify every historical chart-post trade as a brokerage execution or provide live strategy validation.

Covered symbols: AAPL, AMZN, BRENT, BTC, CAT, CVX, DIS, ETH, GEV, HD, INTC, LCID, LLY, LMT, LULU, META, NET, NFLX, NVDA, OIL, ORCL, PEP, PLTR, RIVN, SPCX, TMO, TSLA, UPS, V, VLO, WMT, XLE, and XRH0.

The independent audit utility is [`scripts/audit_actionable_tickers.py`](../../scripts/audit_actionable_tickers.py). Its full per-ticker output is [`data/actionable_ticker_reconciliation_20261023_v1.csv`](../../data/actionable_ticker_reconciliation_20261023_v1.csv). The utility raises on a discrepancy and verifies the v8 close set, active source registry, exact user-provided energy marks, LCID pilot mark series, core daily and ticker exports, all force/fixed position rows, oil-sidecar lots and chart positions, and the 32-book daily aggregates.

## Material contributors are not mark errors

Large aggregate attribution is expected because a ticker's standalone results are repeated across separate comparison portfolios. The following are the largest absolute ticker effects when the four core and four variant-specific 1U/EOD ticker totals are replicated according to the 32-book construction. These are additive model-comparison attributions, **not** netted live positions, brokerage PnL, or evidence that the ticker's mark is wrong. The separate oil sidecar is excluded from this ticker-attribution table.

| Ticker | Contribution across 32 books |
|---|---:|
| PLTR | +$4,448,017.28 |
| HD | +$3,470,284.16 |
| GEV | −$2,823,494.40 |
| INTC | −$2,783,436.96 |
| VLO | −$2,591,258.56 |
| AMZN | −$1,946,413.44 |

The marks and per-ticker calculations for these contributors reconcile to their source rows. Their size comes from repeated portfolio attribution and model outcomes; it is not a newly discovered price-source correction. The exact 32-book endpoint remains **$12,393,481.92 PnL on $350,880,000 gross notional added**, a **3.532114% deployed-notional ratio**. This remains a comparison of 32 separately accounted portfolios, not a single netted account.

## LULU cross-check

The selected LULU close remains **$99.01**, sourced from the v8 endpoint audit and explicitly user-approved. All four core variants show one open 1U lot and **$317.84** unrealized PnL. Each variant-specific 1U/EOD schedule shows 27 open lots, **$270,000** open notional, and **$4,357.18** unrealized PnL; the shared-direction schedule agrees. Fixed-$500/EOD shows 27 lots, 1.35 open units, **$13,500** open notional, and **$217.86** unrealized PnL.

This current ticker attribution is different from the **$14,762,374.40** change in the 32-book aggregate when the stale v7 $265.30 LULU endpoint was replaced by $99.01. The v7-to-v8 mark effect is already exactly reconciled in [`oct23-lulu-mark-adoption-v8.md`](oct23-lulu-mark-adoption-v8.md); it should not be mistaken for LULU's current PnL contribution.

## Reporting correction found during the audit

The core daily `open_units` series had been accumulating every unit ever opened, including units closed in later sessions. That made the field a cumulative-units-added series despite its `open_units` name. It **did not affect realized/unrealized PnL, deployed notional, ticker attribution, or THE ONE MODEL open-notional totals**, but it overstated displayed open-unit exposure on days after exits.

The calculation in `scripts/model_perf_core.py` is corrected so `open_units` now counts only lots actually open on each session. The core performance artifacts have been regenerated, and a regression test now compares each daily value with the open-lot ledger. At Oct. 23, cumulative units added versus corrected current open units are: V1 **84.5 / 69.5**, V2 **84.5 / 64.5**, V3A **93.5 / 78.5**, and V3B **93.5 / 64.5**. The 32-book open-notional total remains **$316,000,000**.
