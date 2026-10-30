# TradingView PaperTrading Block — Post-October 19 Policy

**Effective date: October 20, 2026** (October 19 remains permitted)

> **DEFAULT STRICT BLOCK:** No TradingView-sourced input dated October 20, 2026 or later may be newly added to, or used in, an active portfolio/trading calculation in this repository unless a specific, versioned exception is explicitly authorized. This includes Paper Trading orders and fills, charts/screenshots, price or EOD marks, alerts, and other TradingView-derived values. The rule is source-based and applies to both public and private books. One narrow Oil-only mark-forward exception is recorded below; no other model or trade-event cutoff is waived.

## Scope and date rule

- The cutoff is date-based: the platform/source's recorded trading date on or after **2026-10-20** is blocked. Do not infer a timezone when none is shown.
- TradingView inputs dated through **2026-10-19** remain eligible under this policy. Non-TradingView sources after the cutoff are not blocked by this specific rule, but still require their normal provenance checks.
- An ATS-generated order is not automatically a TradingView input merely because the ATS is used in a portfolio. Conversely, a chart, signal, mark, or ATS action derived from TradingView data after the cutoff is prohibited unless a future policy amendment explicitly says otherwise.
- This is a repository portfolio-control rule; it does not assert that an external TradingView account, ATS, brokerage, or third-party system has actually disabled activity.

## Specific user-authorized exception — Oil v2 (October 29, 2026)

On October 29, 2026, the user authorized one versioned Oil-only mark-forward using existing, previously flagged TradingView EOD marks through **October 26, 2026**. The replay revalues the positions already active through October 19; the **trade-event cutoff remains October 19**. It uses no post-cutoff trade-log events, no ATS/manual short sensitivities, and no Under-Duress replay positions. The v1 October 19 snapshot is preserved unchanged; v2 outputs are separately versioned and linked in the [Oil update report](Oil%20Portfolio%20%E2%80%94%202026-10-26%20Update.md).

This is not authorization to ingest new TradingView material, use October 27–29 marks, update the AI Fund or other models, or treat related-book screenshot PnL as active Oil PnL. The available package has no complete aligned five-symbol EOD marks for October 27–29. The October 28 oil chart captures are intraday quotes, and October 29 close screenshots belong to a separate book; neither is substituted for a common EOD mark set.

## Specific user-authorized scoped exception — Post-Harassment V3A + V3A marks (October 30, 2026)

The user's October 30 request to rebuild the separate Post-Harassment V3A + V3A portfolio authorizes use of existing flagged TradingView benchmark EOD marks through **October 26, 2026**, plus the specified mechanical V3A 1U/EOD force tranches through that date based only on pre-cutoff eligible chart directions. This is recorded as [`USER_AUTHORIZED_POST_HARASSMENT_V3A_V3A_MARKS_AND_FORCE_V1`](TradingView%20Scoped%20Exception%20%E2%80%94%20Post-Harassment%20V3A%20%2B%20V3A%20Replay.md). It does not change the general source cutoff or authorize post-cutoff data/model activity in other portfolios.

User-sourced chart/trade events remain capped at **October 19**; no post-cutoff event records are ingested. No complete synchronized marks through October 30 are present, so the replay's latest as-of date is October 26. Manual, ATS, user-directed/reported, third-party commentary, ambiguous-direction, and screened-ticker events remain excluded. The 10U/DAY DXY add-on and energy daily-buy sidecar are not included.

## Existing post-cutoff records

Pre-existing post-cutoff records are **flagged and preserved**. They are not automatically recalculated. The policy does not delete historical screenshots or trade events, and it does not silently rewrite prior PnL or model outputs. A flagged historical record is an audit exception—not blanket approval to use it in a new active model. Review and an explicit, scoped user decision are required before an affected output is rebuilt or reused. Oil v2 is the sole exception authorizing post-cutoff data for an active model calculation. The user-authorized Oil position sheet, October 28 multi-asset register, and October 29 change log are audit documents only: they preserve source/scenario references and do not authorize treating post-cutoff events as executed or active positions.

The generated [post-cutoff exception index](../data/tradingview_post_cutoff_exceptions_v1.csv) currently lists **107 artifact/record groups**. Its aggregate count of **1,142 rows across source and dependent artifacts includes duplicate versions, authorized audit/register documents, and derived outputs; it is not a unique-trade count**. Trade-log rows without an explicit platform label are conservatively flagged when they are post-cutoff simulated-paper entries. The index builder is [`build_tradingview_post_cutoff_exceptions.py`](../scripts/build_tradingview_post_cutoff_exceptions.py); rerunning it refreshes flags only, not PnL.

Known screenshot exceptions include the October 29 oil close screenshots and the October 29 LCID Paper Trading order screenshot. The existing October 20–26 TradingView benchmark/mark artifacts, other logged post-cutoff TradingView-sourced items, and reports that depend on them remain flagged. The Oil v2 outputs covered by the scoped exception are labeled `USER_AUTHORIZED_SCOPED_OIL_V2`; the cross-book Oil sheet, October 28 multi-asset register, and October 29 change log have separate audit-document labels. Those documents preserve source status and do not authorize post-cutoff model calculations or transactions; all other flagged records remain audit-only until separately reviewed.

## Enforcement for new inputs

Use the shared guard in [`tradingview_policy.py`](../scripts/tradingview_policy.py) before accepting a new dated source. `require_active_input_allowed(source, source_date)` permits non-TradingView data and pre-cutoff TradingView data, and raises `TradingViewPolicyError` for post-cutoff TradingView inputs. `classify_existing_record` labels a retained record as a legacy exception; it does **not** make that record usable in active calculations.

The Part A/Part B archive importers and active benchmark builder reject post-cutoff TradingView data by default. Their `--preserve-flagged-legacy` switch is only for explicit archival reproduction: it writes policy labels such as `FLAGGED_LEGACY_EXCEPTION_NOT_FOR_ACTIVE_USE`, and the resulting data remain barred from active use. The exception-index builder intentionally preserves and flags legacy records only; it is not an ingestion override and does not relax the block.

## Portfolio separation

The cutoff applies to TradingView as a source regardless of whether a record belongs to the public or private portfolio. It does not treat the private ATS's unlogged, personalized decisions as TradingView activity without evidence of that source. Likewise, the public-portfolio ATS manual-review/rollback note in the [audit log](Under-Duress%20Audit%20Rollback%20Log.md) is separate from this source-date block. Do not infer one portfolio's ATS decisions, human review, or trade requests from the other's records.
