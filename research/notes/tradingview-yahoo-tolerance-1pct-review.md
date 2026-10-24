# TradingView vs. Yahoo Finance — 1% Source-Selection Review

**Decision applied:** use TradingView when its daily close is within **1.0% relative difference** of the Yahoo Finance daily close. When it is outside tolerance, **flag the row and select neither source**; no Yahoo or custom fallback is applied. This follows the user's approved tolerance and fallback choice.

## Result

Across the 30 Yahoo-comparable instruments (28 U.S.-listed equities/ETFs, BTC, and ETH), the 39-date grid produced **1,142 date-level comparisons**:

- **42/1,142 (3.68%)** TradingView closes are within 1% of Yahoo.
- **1,100** rows exceed tolerance and are marked `OUT_OF_TOLERANCE_FLAG` with no selected close.
- **0 of 30** Yahoo-comparable instruments pass for their entire available history.
- Only **41** rows select TradingView in the candidate output because an in-tolerance LCID row is selected from the user's explicit LCID mark instead.

This is insufficient coverage for a complete portfolio-performance recalculation. **The existing portfolio performance graphs, model outputs, and active close inputs were not changed.** Recalculating them with 96.32% of comparable rows unresolved would either produce incomplete results or require an unapproved fallback.

## Data and exceptional handling

- Yahoo historical closes for U.S. equities/ETFs from Sep. 3 through Oct. 22 are taken from the repository's Yahoo historical series in [`scripts/daily_closes.py`](../../scripts/daily_closes.py). Its Oct. 23 array entries are the active consolidated close set, not historical Yahoo observations, and were excluded from the comparison.
- Sep. 1–2 and Oct. 23 U.S. equity/ETF closes were retrieved directly from the Yahoo Finance chart endpoint. For BTC/ETH, the comparison uses UTC daily bars and excludes the partial current-day quote. LCID's Sep. 1–Oct. 23 Yahoo series was retrieved directly.
- Sep. 7 U.S. equity/ETF rows and Treasury no-session rows are left without selected prices. All 39 dates remain in the selection file.
- LCID marks on Oct. 20–23 are selected from the user's values ($3.27, $3.21, $3.46, $3.55), not replaced by TradingView or a mean. The user-provided Treasury daily closes remain authoritative. BRENT/OIL are not tolerance-compared because their user-facing cash/CFD marks and Yahoo futures proxies are not interchangeable. XRH0 has no reliable Yahoo history; its $790 user constraint is retained for Oct. 23 only.

## Files

- [`data/multi_source_tv_yahoo_selection_1pct_v1.csv`](../../data/multi_source_tv_yahoo_selection_1pct_v1.csv) — 1,365 rows with Yahoo close, relative difference, pass/fail status, and selected value/source. Out-of-tolerance rows have no selected price.
- [`data/multi_source_tv_yahoo_match_summary_1pct.csv`](../../data/multi_source_tv_yahoo_match_summary_1pct.csv) — per-ticker pass counts and rates.
- [`Charts/performance/tradingview_yahoo_tolerance_1pct.html`](../../Charts/performance/tradingview_yahoo_tolerance_1pct.html) — visual pass-rate chart for review.
- The original candidate `data/multi_source_portfolio_audit_v1.csv` remains preserved unchanged; the prior endpoint-only refresh is also audit-only.

**Conclusion:** the TradingView column does not verify against Yahoo at the approved tolerance for most rows. Do not use this source-selection file as a complete price history or to update portfolio performance graphs until the flagged source data are resolved.
