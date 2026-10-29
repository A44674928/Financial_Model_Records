# HARSHAL_PRIYAVADAN_PATEL_AI_FUND

> Segregated, hypothetical paper-model portfolio containing records kept out of the screened main replay. This is a portfolio allocation, not a claim of a funded legal entity or actual brokerage account.

## Transfer scope and separation

- Receives all pre-cutoff ledger events for the seven user-approved tickers: `AAPL`, `AMZN`, `INTC`, `META`, `NVDA`, `PLTR`, `TSLA`.
- Receives explicitly evidenced third-party/community commentary events on other modeled instruments. Where a record also belongs to one of the seven tickers, it is transferred once and carries both reasons in the event ledger.
- Version 2 transfers all oil and oil-linked trade records to the separate [Oil portfolio](Oil%20Portfolio.md); OIL and CVX records from the prior fund version are no longer in this active fund replay. Version 1 remains preserved as a historical snapshot.
- Receives the DXY directional sleeve as a single segregated component. Its source signal is retained in the transfer ledger; the sleeve is not duplicated as a separate DXY entry lot.
- Uses sessions through **2026-10-19** only, preserving the standing TradingView cutoff. No October 20-or-later TradingView inputs were used.
- The screened main replay remains separate and unchanged. The policy block remains in force for other portfolios; this is the user-requested segregated portfolio for the excluded records.

## Recomputed fund results

| Variant | Realized PnL | Unrealized PnL | Total PnL | ROI | Deployed notional | Open units |
|---|---:|---:|---:|---:|---:|---:|
| V1 — Variant 1 — 1U Open | $23,887.09 | $3,784.47 | $27,671.57 | 4.2572% | $650,000.00 | 53.0000 |
| V2 — Variant 2 — 1U SAR | $28,148.61 | $-1,311.26 | $26,837.35 | 4.1288% | $650,000.00 | 49.0000 |
| V3A — Variant 3A — Nu Open | $23,887.09 | $18,146.06 | $42,033.15 | 5.7580% | $730,000.00 | 61.0000 |
| V3B — Variant 3B — Nu SAR | $37,752.69 | $-1,311.26 | $36,441.43 | 4.9920% | $730,000.00 | 49.0000 |

The four variants retain their existing definitions from the core model. These are not brokerage results, realized cash balances, or a statement of actual funding. The all-cash/debit convention remains in force; no leverage or financing is inferred.

## Transfer and valuation ledger

- Unique pre-cutoff event records transferred: **41**; ticker event rows: **33**; explicit commentary rows: **12**; DXY signal rows: **1**. Category counts overlap.
- US10Y/US30Y yield-only event rows retained but not included in PnL: **3**. A yield quote is not a bond price; no duration, futures contract, or yield-to-price conversion is inferred. See [unpriced event register](../data/harshal_priyavadan_patel_ai_fund_unpriced_events_v2.csv).
- EURUSD is modeled as a 1U LONG from the logged 2026-09-15 entry using the user-provided daily close series through October 19. The provider/feed and close convention are not independently verified; this leg is identified separately in the builder and manifest.
- [Transferred event ledger](../data/harshal_priyavadan_patel_ai_fund_event_ledger_v2.csv), [daily replay](../data/harshal_priyavadan_patel_ai_fund_daily_v2.csv), [summary JSON](../data/harshal_priyavadan_patel_ai_fund_summary_v2.json), and [SHA-256 manifest](../data/harshal_priyavadan_patel_ai_fund_manifest_v2.json) preserve lineage.

The user trade logs and prior screened outputs remain unchanged. These portfolio results do not reverse or reinterpret any actual transaction, funding source, or source record; they only segregate and replay the specified historical records.
