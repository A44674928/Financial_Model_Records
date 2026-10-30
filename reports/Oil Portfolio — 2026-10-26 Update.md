# Oil Portfolio Update — October 26, 2026

> Version 2 re-marks the existing Oil portfolio through the latest complete aligned TradingView EOD set. This is a model update, not evidence of funded positions or audited brokerage executions.

## Scope and data coverage

- **Latest complete aligned EOD marks:** 2026-10-26; requested current date: **2026-10-29**.
- **Active trade-event cutoff remains:** 2026-10-19. This update revalues positions already in the active book; it does not ingest later trade-log events, ATS scenario trades, or the hypothetical under-duress replay.
- **Post-cutoff price marks used:** 25 direct marks across 5 sessions and five symbols. **Post-cutoff trade events used: 0.**
- The available aligned EOD package ends October 26. The repository has no complete five-symbol EOD set for October 27–29. October 28 oil chart captures are intraday quotes, not EOD marks; October 29 Private Fund screenshots are separate-book close transactions, not a common EOD price set.
- Therefore this is the latest supportable aligned mark-to-model update, **not a fully current October 29 valuation**. No prices are interpolated or carried forward to imply current-date marks.

Post-cutoff trade-log rows remain preserved for manual review. In particular, legacy target/short rows and later manual/ATS scenario-linked lots are not treated as verified active positions in this mark-forward update.

## Active replay through latest complete EOD marks

| Variant | Realized PnL | Unrealized PnL | Total PnL | ROI | Deployed notional | Open units |
|---|---:|---:|---:|---:|---:|---:|
| V1 — Variant 1 — 1U Open | $0.00 | $42,935.36 | $42,935.36 | 3.7013% | $1,160,000.00 | 116.0000 |
| V2 — Variant 2 — 1U SAR | $0.00 | $42,935.36 | $42,935.36 | 3.7013% | $1,160,000.00 | 116.0000 |
| V3A — Variant 3A — Nu Open | $0.00 | $42,935.36 | $42,935.36 | 3.7013% | $1,160,000.00 | 116.0000 |
| V3B — Variant 3B — Nu SAR | $0.00 | $42,935.36 | $42,935.36 | 3.7013% | $1,160,000.00 | 116.0000 |

All open positions in this replay are long; realized PnL is unchanged because no post-cutoff trade events were included. Later short and close records remain audit-only pending the position-by-position review.

| Ticker | Oct. 26 EOD mark | Realized PnL | Unrealized PnL | Total PnL | Open units |
|---|---:|---:|---:|---:|---:|
| BRENT | $115.38 | $0.00 | $21,912.90 | $21,912.90 | 55.0000 |
| CVX | $232.01 | $0.00 | $3,234.46 | $3,234.46 | 3.0000 |
| OIL | $101.30 | $0.00 | $16,639.64 | $16,639.64 | 56.0000 |
| VLO | $426.76 | $0.00 | $62.72 | $62.72 | 1.0000 |
| XLE | $69.64 | $0.00 | $1,085.64 | $1,085.64 | 1.0000 |

### Change from the October 19 snapshot

| Ticker | Oct. 19 PnL | Oct. 26 PnL | Mark-to-market change |
|---|---:|---:|---:|
| BRENT | $-590.87 | $21,912.90 | $22,503.77 |
| CVX | $2,140.06 | $3,234.46 | $1,094.40 |
| OIL | $-836.01 | $16,639.64 | $17,475.65 |
| VLO | $217.17 | $62.72 | $-154.45 |
| XLE | $792.74 | $1,085.64 | $292.90 |
| **Total** | **$1,723.09** | **$42,935.36** | **$41,212.27** |

The comparison is mark-to-market only: it uses the same active event set through October 19 and the same all-cash/debit model convention; no new post-cutoff position entries are assumed.

### Historical AI Fund transfer reconciliation (October 19)

The earlier AI Fund decrease of $1,214.71 remains attributable to two OIL longs and one CVX long transferred into Oil, as documented in the historical October 19 report. The new Oil mark-forward result does not change that original transfer arithmetic; it only updates the prices of the active Oil lots through October 26.

## October 27–29 data still needed

To complete the requested October 29 EOD valuation, provide a date-specific EOD close for each of `BRENT`, `OIL`/`TVC:USOIL`, `CVX`, `VLO`, and `XLE` for October 27, 28, and 29, or an aligned source file with those marks and provenance. Do not substitute the October 28 intraday chart quotes or the separate Private Fund transaction fills.

If later position events are also to enter the active model, they need a separate position-by-position review first. This update intentionally does not fold the under-duress replay or its scenario trades into the active portfolio.

## Audit files and provenance

- Trade-log rows indexed: **34**; rows included as active trade events through 2026-10-19: **18**; later rows preserved but not replayed: **16**.
- Separate-book records retained: **5**; none were consolidated into the active Oil model.
- [Version 2 daily series](../data/oil_portfolio_daily_v2.csv); [trade-event audit ledger](../data/oil_portfolio_trade_ledger_v2.csv); [summary and ticker breakdown](../data/oil_portfolio_summary_v2.json); [source manifest](../data/oil_portfolio_manifest_v2.json); [related-book register](../data/oil_portfolio_related_book_records_v2.csv).
- [October 19 historical Oil report](Oil%20Portfolio.md); [historical PnL reconciliation](../data/oil_pnl_reconciliation_v1.csv); [Under-Duress Oil Sale Void Replay](Under-Duress%20Oil%20Sale%20Void%20Replay.md) remains a separate hypothetical scenario.

All figures remain hypothetical model calculations, not audited brokerage execution PnL, cash balances, or reconciled account totals. No funding source or leverage is inferred.
