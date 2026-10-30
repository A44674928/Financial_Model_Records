# Scoped TradingView Exception — Post-Harassment V3A + V3A Replay

**Exception ID:** `USER_AUTHORIZED_POST_HARASSMENT_V3A_V3A_MARKS_AND_FORCE_V1`
**Authorized:** October 30, 2026, by the user's instruction to start from scratch and run the V3A/V3A portfolio to date on all charts.
**Scope:** the separate hypothetical **Post-Harassment V3A + V3A Audit Portfolio** only.

## Authorized use

This scoped exception permits the portfolio-specific replay to use the existing flagged TradingView benchmark EOD marks through **October 26, 2026**, the latest complete synchronized mark date in the repository, and to run the V3A 1U/EOD force model's deterministic daily tranche rule through that date using only pre-cutoff eligible chart directions. It does not revise the general post-October 19 block or authorize post-cutoff marks, events, or model activity in any other portfolio.

User-sourced chart/trade events remain capped at **October 19, 2026**. No post-cutoff event is ingested: the available later records are not eligible chart-only signals for this method, and documented manual, ATS, user-directed/reported, or override events are excluded. The modeled post-cutoff 1U/EOD tranches are generated mechanically from pre-cutoff directions under the specified force rule; they are hypothetical model lots, not actual orders or fills.

## Data limits and exclusions

- No complete synchronized TradingView benchmark marks for **October 27–30, 2026** are present in the repository. The replay therefore ends **October 26** and is not a mark-to-market through October 30.
- The event stream is drawn from the repository's normalized `trades/*.txt` records; it is not an OCR or visual re-interpretation of every file in `Charts/` or `Archive/`.
- Existing ticker and source screens still apply. `AAPL`, `AMZN`, `INTC`, `META`, `NVDA`, `PLTR`, and `TSLA`, DXY direction, explicit third-party/community commentary, ambiguous inferred direction, and non-chart/news rationale are excluded.
- The V3A core plus V3A-specific 1U/EOD force model is replayed without the 10U/DAY DXY add-on or energy daily-buy sidecar. No historical `TWM_1M_LIGHT` manual/ATS/user-reported events or performance are copied.
- Model units and PnL do not establish account ownership, brokerage/ATS execution, available cash, or account-level rollback. No leverage or financing is inferred.

## Versioned output

The exception is applied only to these versioned outputs:

- [`post_harassment_v3a_v3a_chart_only_daily_v1.csv`](../data/post_harassment_v3a_v3a_chart_only_daily_v1.csv)
- [`post_harassment_v3a_v3a_chart_only_positions_v1.csv`](../data/post_harassment_v3a_v3a_chart_only_positions_v1.csv)
- [`post_harassment_v3a_v3a_chart_only_event_audit_v1.csv`](../data/post_harassment_v3a_v3a_chart_only_event_audit_v1.csv)
- [`post_harassment_v3a_v3a_chart_only_summary_v1.json`](../data/post_harassment_v3a_v3a_chart_only_summary_v1.json)
- [`post_harassment_v3a_v3a_chart_only_manifest_v1.json`](../data/post_harassment_v3a_v3a_chart_only_manifest_v1.json)

Builder: [`build_post_harassment_chart_only_replay.py`](../scripts/build_post_harassment_chart_only_replay.py). The complete portfolio record is [Post-Harassment V3A + V3A Audit Portfolio](Post-Harassment%20V3A%20%2B%20V3A%20Audit%20Portfolio.md).
