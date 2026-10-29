# TradingView PaperTrading Block — Post-October 19 Policy

**Effective date: October 20, 2026** (October 19 remains permitted)

> **STRICT BLOCK:** No TradingView-sourced input dated October 20, 2026 or later may be newly added to, or used in, an active portfolio/trading calculation in this repository. This includes Paper Trading orders and fills, charts/screenshots, price or EOD marks, alerts, and other TradingView-derived values. The rule is source-based and applies to both public and private books.

## Scope and date rule

- The cutoff is date-based: the platform/source's recorded trading date on or after **2026-10-20** is blocked. Do not infer a timezone when none is shown.
- TradingView inputs dated through **2026-10-19** remain eligible under this policy. Non-TradingView sources after the cutoff are not blocked by this specific rule, but still require their normal provenance checks.
- An ATS-generated order is not automatically a TradingView input merely because the ATS is used in a portfolio. Conversely, a chart, signal, mark, or ATS action derived from TradingView data after the cutoff is prohibited unless a future policy amendment explicitly says otherwise.
- This is a repository portfolio-control rule; it does not assert that an external TradingView account, ATS, brokerage, or third-party system has actually disabled activity.

## Existing post-cutoff records

Pre-existing post-cutoff records are **flagged, preserved, and not automatically recalculated**. The policy does not delete historical screenshots or trade events, and it does not silently rewrite prior PnL or model outputs. A flagged historical record is an audit exception—not approval to use the record in a new active model. Review and an explicit user decision are required before an affected output is rebuilt or reused.

The generated [post-cutoff exception index](../data/tradingview_post_cutoff_exceptions_v1.csv) currently lists **97 artifact/record groups**. Its aggregate count of **1,066 rows across source and dependent artifacts includes duplicate versions and derived outputs; it is not a unique-trade count**. Trade-log rows without an explicit platform label are conservatively flagged when they are post-cutoff simulated-paper entries. The index builder is [`build_tradingview_post_cutoff_exceptions.py`](../scripts/build_tradingview_post_cutoff_exceptions.py); rerunning it refreshes flags only, not PnL.

Known screenshot exceptions include the October 29 oil close screenshots and the October 29 LCID Paper Trading order screenshot. The existing October 20–26 TradingView benchmark/mark artifacts, other logged post-cutoff TradingView-sourced items, and reports that depend on them are also flagged. Existing reports and numbers remain as historical outputs until reviewed; they must not be represented as compliant with the new cutoff.

## Enforcement for new inputs

Use the shared guard in [`tradingview_policy.py`](../scripts/tradingview_policy.py) before accepting a new dated source. `require_active_input_allowed(source, source_date)` permits non-TradingView data and pre-cutoff TradingView data, and raises `TradingViewPolicyError` for post-cutoff TradingView inputs. `classify_existing_record` labels a retained record as a legacy exception; it does **not** make that record usable in active calculations.

The Part A/Part B archive importers and active benchmark builder reject post-cutoff TradingView data by default. Their `--preserve-flagged-legacy` switch is only for explicit archival reproduction: it writes policy labels such as `FLAGGED_LEGACY_EXCEPTION_NOT_FOR_ACTIVE_USE`, and the resulting data remain barred from active use. The exception-index builder intentionally preserves and flags legacy records only; it is not an ingestion override and does not relax the block.

## Portfolio separation

The cutoff applies to TradingView as a source regardless of whether a record belongs to the public or private portfolio. It does not treat the private ATS's unlogged, personalized decisions as TradingView activity without evidence of that source. Likewise, the public-portfolio ATS manual-review/rollback note in the [audit log](Under-Duress%20Audit%20Rollback%20Log.md) is separate from this source-date block. Do not infer one portfolio's ATS decisions, human review, or trade requests from the other's records.
