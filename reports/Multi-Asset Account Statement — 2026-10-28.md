# Multi-Asset Account Statement — October 28, 2026

> **Source-separated position and event register, not a reconciled brokerage statement.** No single account map, funded cash balance, or verified execution ledger is available across these source books.

## Statement basis and boundary

This statement gathers the repository's identified multi-asset holdings, modeled lots, user-directed snapshots, and audit references dated October 28 or earlier. The source evidence has differing as-of dates. The latest permitted non-Oil main-model mark is **October 19** under the standing TradingView cutoff; the separately authorized Oil v2 mark-forward uses aligned EOD marks through **October 26**, with trade events still cut off at October 19. The ALIUSD export is a source snapshot from October 28, not an EOD mark. The older Private Fund LCID screenshot has no capture timestamp.

The CSV is intentionally a **register**, not a portfolio valuation. It keeps separate source books, alternative model variants, and audit-only scenarios on separate rows. It does not add their notionals, market values, profit estimates, or PnL into an account total. The four core-model variants are alternative paths, not additive holdings.

## Row coverage

The register contains **236 rows**. By category: AI_FUND_HISTORICAL_EVENT_AUDIT_ONLY: 41; OIL_AUDIT_SCENARIO_OR_REFERENCE: 46; OIL_V2_BASE_POSITION: 18; POST_CUTOFF_LCID_PILOT_LOT: 5; POST_CUTOFF_LEDGER_EVENT_AUDIT_ONLY: 14; PRIVATE_FUND_OPEN_POSITION_RESTORED: 2; PRIVATE_FUND_POSITION_SNAPSHOT: 1; SCREENED_MAIN_MODEL_OPEN_LOT: 98; UNPRICED_OR_SCREENED_SOURCE_ENTRY: 10; USER_DIRECTED_POSITION_SNAPSHOT: 1.

- **Screened main model:** open paper-model lots through October 19 across four alternative variants. Blocked tickers and commentary-derived records are not represented as active; after-cutoff trade-log events are separately retained as audit-only rows.
- **Oil:** the active Oil v2 pre-cutoff lots are shown at October 26 marks; ATS/manual, under-duress, legacy, and liquidation references remain separately labeled and non-additive. The two separate-book Private Fund longs are retained open at their earlier reported entries ($114.043 BRENT; $99.18 USOIL); entry dates and current marks are unknown. Their October 29 close records are nullified/voided in the change log, not treated as exits.
- **ALIUSD:** user-directed long from an October 28 platform export, with the user-corrected $2,999.99 entry and $3,070.60 export snapshot. The raw quantity is preserved; contract multiplier and account mapping are unknown. Its conditional $46,639,362,534.94 gross basis and $1,097,738,788.66 snapshot price-only change are arithmetic references, not funded capital or verified account PnL; platform 50×/margin fields are not applied.
- **LCID:** an older open-long screenshot is retained with its capture date unknown. Five Oct. 20–23 Small Caps pilot units are separate model rows and remain post-cutoff audit-only; they are not combined with the large screenshot position.
- **AI Fund history:** the prior segregated AI Fund v2 event ledger is included row-by-row as historical audit data, not as active holdings; its blocked-ticker/commentary events remain excluded under the October 29 screen.
- **Unpriced / screened source records:** BTC, ETH, FX, DXY, and Treasury-yield references are retained with their source status. Yield quotes are not bond prices; no quantity, duration, FX conversion, or current mark is invented.

## Reconciliation limitations

The historical screened replay is a paper model, not an account custody record. Oil is separately modeled and appears in separate Oil rows; older combined model rows are not netted against it. The older AI Fund ledger contains records for policy-blocked tickers/commentary and is not treated as a current active portfolio after the October 29 screen. The Private Fund's prior profit-only carry-in is a selected model estimate, not verified cash, and is not represented as an asset or added to any position value.

No inferred leverage, financing, cash, or funding source is included. TradingView Paper Trading screenshots and model outputs are not independently audited brokerage executions. The $1.31B LCID market-cap reference is hypothetical and belongs in the October 29 change log, not this October 28 statement.

## Files

- Machine-readable register: [`data/multi_asset_account_statement_2026-10-28_v1.csv`](../data/multi_asset_account_statement_2026-10-28_v1.csv).
- October 29 changes: [change log report](Account%20Change%20Log%20%E2%80%94%202026-10-29.md) and [CSV](../data/account_change_log_2026-10-29_v1.csv).
- Supporting source records: [Oil v2 update](Oil%20Portfolio%20%E2%80%94%202026-10-26%20Update.md), [ALIUSD position note](ALIUSD%20User-Directed%20LONG%20Position.md), [Private Fund balance sheet](Harshal's%20Private%20Fund%20%E2%80%94%20November%202026++%20Experiment.md), and [screened replay](Influencer%20and%20AI%20Screened%20Replay%20%E2%80%94%202026-10-29.md).
