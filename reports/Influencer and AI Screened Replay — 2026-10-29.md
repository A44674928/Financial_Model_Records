# Influencer and AI-Screened Replay — 2026-10-29

> Versioned retroactive replay. Existing reports, ledgers, screenshots, and source records were not overwritten or deleted.

## Policy applied

- Excluded the approved broad AI-exposure ticker screen: `AAPL`, `AMZN`, `INTC`, `META`, `NVDA`, `PLTR`, `TSLA`.
- Excluded trade events whose stored provenance explicitly identifies third-party/community commentary or recommendation badges.
- Excluded the DXY directional sleeve because its logged directions are chart-commentary signals; raw DXY marks alone are not a position signal.
- Enforced the standing TradingView cutoff by ending the replay on **2026-10-19**. No October 20-or-later TradingView marks or events enter the replay.
- Official issuer filings, raw market observations, and user trade-ledger records are eligible. The block is on commentary and the selected securities, not on the listed source types.

## Recomputed terminal results

| Variant | Realized PnL | Unrealized PnL | Total PnL | ROI | Deployed notional | Open units |
|---|---:|---:|---:|---:|---:|---:|
| V1 — Variant 1 — 1U Open | $0.00 | $6,139.94 | $6,139.94 | 0.4449% | $1,380,000.00 | 138.0000 |
| V2 — Variant 2 — 1U SAR | $1,562.62 | $4,533.48 | $6,096.11 | 0.4417% | $1,380,000.00 | 137.0000 |
| V3A — Variant 3A — Nu Open | $0.00 | $7,746.39 | $7,746.39 | 0.5573% | $1,390,000.00 | 139.0000 |
| V3B — Variant 3B — Nu SAR | $3,125.25 | $4,533.48 | $7,658.73 | 0.5510% | $1,390,000.00 | 137.0000 |

These are simulated paper-model results under the screened inputs, not brokerage results or a cash-balance reconciliation. The existing accounting convention remains all-cash/debit; no leverage or financing is inferred.

## Audit and output files

- Removed records in the audit index: **80 rows** (counts overlap when multiple policies apply).
- Explicit third-party commentary event rows: **15**.
- Event rows in the seven blocked tickers: **40**.
- DXY directional events screened out: **1**.
- [Blocked-input audit CSV](../data/influencer_ai_blocked_inputs_v1.csv) records each source line, reason, and preservation status.
- [Daily replay CSV](../data/model_performance_influencer_ai_screened_daily_v1.csv) and [summary JSON](../data/model_performance_influencer_ai_screened_summary_v1.json) are separate versioned outputs.
- [Replay manifest](../data/influencer_ai_screened_replay_manifest_v1.json) includes SHA-256 hashes for the consumed benchmark and trade logs.
- The previous [Model Performance Comparison](../Model%20Performance%20Comparison.md) remains unchanged as a historical record.

## Provenance limits

Historical trade notes do not consistently identify the author or origin of each idea. This replay excludes records with explicit commentary provenance and the user-selected securities; it does not label an un-attributed note as influencer content without evidence. The rule is fail-closed for new source inputs: unclassified commentary is not eligible until it is documented as an allowed source class. The audit CSV is a source screen, not a claim that every historic recommendation has been exhaustively attributed.

The replay uses the repository's existing standardized paper-trade logs and the pre-cutoff benchmark marks. It preserves the prior report and original ledgers; it does not rewrite their historical conclusions.
