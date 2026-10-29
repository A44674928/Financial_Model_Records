# Influencer, AI, and Third-Party Commentary Block Policy

**Effective date: October 29, 2026**  
**Retroactive treatment:** preserve the original records and reports; exclude affected inputs from a separate screened replay and retain an audit index.

## User-approved scope

This policy applies to both source inputs and securities:

- Block all influencer recommendations and all third-party commentary, whether or not the author or source is labeled an influencer.
- Block AI-generated commentary and commentary supplied by AI companies, including Arena.ai. The general commentary rule is not limited to a finite vendor-name list.
- Exclude the user-approved broad AI-exposure ticker screen: **AAPL, AMZN, INTC, META, NVDA, PLTR, and TSLA**. This is the user's chosen broad screen, not an independently researched taxonomy of every AI-exposed issuer.
- Allow official issuer filings and raw market data. User trade-ledger records remain the primary record of the user's simulated transactions; this does not authorize third-party rationale embedded in them.

The machine-readable symbol/source register is [`influencer_ai_policy_blocklist_v1.csv`](../data/influencer_ai_policy_blocklist_v1.csv). The shared classifier and event-screen logic are in [`influencer_ai_policy.py`](../scripts/influencer_ai_policy.py).

## Retroactive screened replay

The prior [`Model Performance Comparison.md`](../Model%20Performance%20Comparison.md), its source records, and prior data artifacts are preserved unchanged. The separate [screened replay](Influencer%20and%20AI%20Screened%20Replay%20%E2%80%94%202026-10-29.md) recomputes the four model variants from filtered inputs and creates versioned data outputs.

The replay:

1. Removes the seven approved tickers and their ledger events.
2. Removes historic trade events whose stored provenance explicitly identifies a TradingView/community post, a directional badge, or an external recommendation.
3. Removes the DXY directional sleeve because its logged positions depend on chart commentary; raw DXY price marks alone remain allowable.
4. Uses only sessions through **October 19, 2026**. This honors the separate strict TradingView cutoff effective October 20; no later TradingView marks or events are used.
5. Preserves screened-out record details, original line references, reasons, and a content-derived record ID in [`influencer_ai_blocked_inputs_v1.csv`](../data/influencer_ai_blocked_inputs_v1.csv). Original source files are not edited.

Outputs:

- [`model_performance_influencer_ai_screened_daily_v1.csv`](../data/model_performance_influencer_ai_screened_daily_v1.csv)
- [`model_performance_influencer_ai_screened_summary_v1.json`](../data/model_performance_influencer_ai_screened_summary_v1.json)
- [`influencer_ai_screened_replay_manifest_v1.json`](../data/influencer_ai_screened_replay_manifest_v1.json) — SHA-256 source hashes and output lineage
- Builder: [`build_influencer_ai_screened_replay.py`](../scripts/build_influencer_ai_screened_replay.py)

## Provenance and enforcement

Historical ledger notes do not consistently identify the author or origin of each idea. The retrospective source filter therefore blocks only entries with explicit commentary provenance; it does not invent an author for un-attributed notes. This is an evidence limitation, not an approval of unknown third-party sources. For new active inputs, source classification is fail-closed: only official issuer filings, raw market data, and user trade-ledger records are allowed. Unclassified commentary must not enter a model until its source class is documented as allowed.

A permitted market-data source may supply raw observations, but its opinions, forecasts, recommendations, or signals are still third-party commentary and are blocked. Official filings may be used as issuer disclosures; third-party summaries of filings are not official filings. Neither this policy nor the screened replay establishes brokerage executions, realized cash balances, or financing. The all-cash/debit convention remains in force; no leverage or financing is inferred.

This is a repository-level control. It does not assert that any outside account, vendor, broker, or AI service has disabled or removed content.
