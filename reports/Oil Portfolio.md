# Oil Portfolio

> Separate portfolio for all recorded OIL/USOIL and BRENT trade-log events, the Weekend Oil campaign, and oil-linked equity trades. A simulated portfolio ledger is not a claim of a funded account or independently verified brokerage executions.

## Portfolio scope

- **Direct crude:** `OIL` (TVC:USOIL / WTI) and `BRENT` (Brent Cash). All their standardized trade-log rows are carried into the Oil ledger, including the 50U Weekend Oil entries and later Weekend Oil adds.
- **Oil/energy-linked equity sleeve:** `CVX`, `VLO`, and `XLE`, kept separately identified from crude exposure. CVX includes the user-recorded Brent-caption-linked position.
- The prior `HARSHAL_PRIYAVADAN_PATEL_AI_FUND` version 1 included two OIL commentary entries and one CVX commentary event. Those entries are now moved into this Oil portfolio in fund version 2; v1 is preserved as history and is not the current fund allocation.
- Active model window: **2026-09-03 through 2026-10-19**. October 20, 2026 onward remains blocked for TradingView-derived active use. Later oil events are preserved in the event ledger but not used in the active replay.
- The Oil portfolio does not include DXY. Private-fund screenshot closes, user-reported ATS locked-foundation liquidations, and duress scenario rows are indexed separately; they are not merged into this active model or netted across books.

## Active replay results through October 19, 2026

| Variant | Realized PnL | Unrealized PnL | Total PnL | ROI | Deployed notional | Open units |
|---|---:|---:|---:|---:|---:|---:|
| V1 — Variant 1 — 1U Open | $0.00 | $1,723.09 | $1,723.09 | 0.1485% | $1,160,000.00 | 116.0000 |
| V2 — Variant 2 — 1U SAR | $0.00 | $1,723.09 | $1,723.09 | 0.1485% | $1,160,000.00 | 116.0000 |
| V3A — Variant 3A — Nu Open | $0.00 | $1,723.09 | $1,723.09 | 0.1485% | $1,160,000.00 | 116.0000 |
| V3B — Variant 3B — Nu SAR | $0.00 | $1,723.09 | $1,723.09 | 0.1485% | $1,160,000.00 | 116.0000 |

The four variants retain their existing model definitions. Total return combines the direct-crude and separately labeled energy-equity sleeves; see the per-ticker breakdown in the summary JSON. No funding or account mapping is inferred.

## Weekend Oil lots

The 2026-10-19 50U BRENT and 50U OIL Weekend Oil lots are included in all four core variants as separate, additional simulated lots. At the October 19 EOD mark they are marked against their user-provided entry prices; they are not proof of ATS or brokerage fills. The requested ATS/MANUAL 40U/10U split is a ceiling/proxy only, not a verified allocation.

The October 23 target trims/short entries, October 25 Weekend Oil replenishments/short-cover-linked entries, and October 26 screenshot-linked entries/closes are preserved in the ledger but excluded from active PnL because they are after the current replay cutoff. The screenshot-reported paired 50U close is not converted into an active TradingView input.

## Ledger, related books, and audit links

- Standardized Oil/energy trade-log rows indexed: **34**; rows used through cutoff: **18**; later rows preserved but not used: **16**.
- Separate-book references retained: **5**. [`oil_portfolio_related_book_records_v1.csv`](../data/oil_portfolio_related_book_records_v1.csv) includes the two screenshot-reported October 29 Private Fund oil closes (transaction PnL only, not independently audited) and the three user-reported ATS locked-foundation liquidation records with unknown exact quantities/fills. They are not part of the core totals.
- [All oil/energy trade-log events](../data/oil_portfolio_trade_ledger_v1.csv); [daily model series](../data/oil_portfolio_daily_v1.csv); [summary and per-ticker breakdown](../data/oil_portfolio_summary_v1.json); [SHA-256 source manifest](../data/oil_portfolio_manifest_v1.json).
- Related but distinct scenario: [Under-Duress Oil Sale Void Replay](Under-Duress%20Oil%20Sale%20Void%20Replay.md). That is a hypothetical replay, not an additional Oil holding.

## Accounting and provenance

All active results are hypothetical unit-notional model calculations. They are not audited brokerage executions, account balances, or a reconciled total across the public, ATS, and Private Fund books. The all-cash/debit convention remains in force; no leverage or financing is inferred. Screenshot-reported realized PnL from a separate TradingView Paper Trading account remains source-record-only and is not included in these results.
