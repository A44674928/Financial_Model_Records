# Multi-Source Portfolio Audit — v1

**Scope:** inspect the attached `multi_source_portfolio_audit 3.csv` without adopting it. It is preserved as [`data/multi_source_portfolio_audit_v1.csv`](../../data/multi_source_portfolio_audit_v1.csv). No active price series, model input, report, chart, or output was changed.

## Structure and arithmetic

The file has **1,365 rows**: 35 tickers × 39 dates from Sep. 1 to Oct. 23, 2026. Date/ticker keys are unique and all four price/average columns are populated.

The average column is arithmetically consistent: all **1,365/1,365** values equal the arithmetic mean of `TradingView_Price`, `YahooFinance_Price`, and `Custom_Override_Price` at the displayed precision. That checks the formula, not the accuracy or independence of the inputs:

- `Custom_Override_Price` equals the TV/Yahoo midpoint to cents on **1,338/1,365** rows.
- The supposed independent average equals the custom column exactly on **1,216/1,365** rows.
- The source columns have no per-row URL, retrieval time, instrument identifier, or override rationale.

## Data-quality flags

The series have a strong formula-generated/normalized-data signature and do not look like reliable observed EOD histories without source evidence:

- `TradingView_Price` and `YahooFinance_Price` are monotonically rising for **33 of 35 tickers** across all 39 dates. `Custom_Override_Price` rises monotonically for **all 35**; the average rises for 33.
- For AAPL, the TradingView column rises in near-fixed daily increments (mostly $0.90–$0.92). A spot-check of the Yahoo chart response for Sep. 1 gives **$325.13**, while this file's `YahooFinance_Price` says **$313.59**. [Yahoo chart query](https://query1.finance.yahoo.com/v8/finance/chart/AAPL?period1=1788220800&period2=1792886400&interval=1d).
- The file assigns equity prices to **Sep. 7**, a U.S. market holiday, so those cannot be normal U.S. equity EOD closes.

These are internal consistency and provenance checks; the file's “independent auditor” label is not itself evidence of independent verification.

## Differences from active references

On the Oct. 23 endpoint, the file's arithmetic-average column matches **8/35** active v2 marks and **14/35** v6 marks. All ticker-by-ticker values and deltas are in [`data/multi_source_portfolio_endpoint_comparison.csv`](../../data/multi_source_portfolio_endpoint_comparison.csv).

The file's average for BRENT/OIL is **$115.425 / $100.81**, while the active source-specific overrides are **$117.345 / $103.45**. Substituting those averages for the overrides would reduce the current energy open PnL from **+$11,641.13** to **+$9,040.81** (−$2,600.33). It would not be appropriate to replace the named BlackBull/TradingView marks with a cross-source mean without explicit approval.

It also conflicts with confirmed constraints: LCID's Oct. 23 average is $3.52 versus the specified $3.55, and XRH0's is $780 versus the $790 system constraint. The 10/23 match counts do not resolve the broader historical concerns.

## Live Yahoo endpoint refresh (partial; audit candidate only)

Live Yahoo Finance chart data for **Oct. 23, 2026** was used to update the Yahoo field in a separate 1,365-row refresh candidate for **28 U.S.-listed equities/ETFs plus BTC and ETH**. The crypto values use the last fully completed UTC daily close, not the then-current partial quote. Thirty instruments were updated; six already matched to cents. Their arithmetic means were recalculated from the displayed TradingView, refreshed Yahoo, and custom inputs. This is an endpoint-only update: historical rows other than identified no-session rows were not refreshed.

Examples of material Yahoo-column changes include GEV **$172.40 → $815.00**, LLY **$780.50 → $1,273.46**, CAT **$321.40 → $687.00**, VLO **$128.40 → $419.28**, and LULU **$315.20 → $99.01**. This reinforces that the original series should not be treated as verified history. The unchanged candidate itself remains preserved at v1.

Two Treasury benchmark values were also checked on Yahoo (^TNX **4.988%**, ^TYX **5.315%**) but **not substituted** because the user-provided Treasury close files remain authoritative. The Yahoo energy-futures feeds were still in-session at retrieval, so they were not used to replace source-specific BRENT/OIL marks or calculate an energy mean. Yahoo returned no data for XRH0. LCID's user-specified marks ($3.27, $3.21, $3.46, $3.55), XRH0's $790 constraint, the separate US30Y entry at 5.311%, and ORCL's $125.83 entry quote remain explicitly noted in the refreshed file; none is overridden by an arithmetic mean. **No active model input or output was changed.**

The refresh keeps all 39 dates. It blanks the unsupported Sep. 7 U.S. equity/ETF closes and the Treasury rows on Sep. 7 and Oct. 12, labeling them no-session; their supplied candidate values are retained in a companion audit CSV. BRENT/OIL averages are left blank rather than blending unlike energy marks. Files: [`data/multi_source_portfolio_live_refresh_v2.csv`](../../data/multi_source_portfolio_live_refresh_v2.csv), [`data/multi_source_portfolio_no_session_source_values_v2.csv`](../../data/multi_source_portfolio_no_session_source_values_v2.csv), and the row-level Yahoo evidence [`data/multi_source_portfolio_live_yahoo_endpoint_check.csv`](../../data/multi_source_portfolio_live_yahoo_endpoint_check.csv).

This does **not** complete live verification across all 39 dates × 35 tickers; unverified historical source values remain candidate-only. The refreshed file is not adopted for any model, report, chart, or portfolio result.

## Row-level audit artifacts

- [`data/multi_source_portfolio_formula_check.csv`](../../data/multi_source_portfolio_formula_check.csv) — each source value, recalculated mean, rounding check, and custom-vs-midpoint check (1,365 rows).
- [`data/multi_source_portfolio_endpoint_comparison.csv`](../../data/multi_source_portfolio_endpoint_comparison.csv) — all 35 Oct. 23 tickers against active v2 and v6.
- [`data/multi_source_portfolio_pattern_summary.csv`](../../data/multi_source_portfolio_pattern_summary.csv) — per-ticker trend, source spread, and endpoint comparisons.

**Assessment:** structurally complete and its average formula checks out, but source provenance, smooth monotonic series, the holiday rows, and conflicts with confirmed marks mean it is **not suitable as an accurate EOD price file yet**. Keep it as an audit candidate; do not use it to refresh model results until the underlying source values are verified.

Input SHA-256: `c0afecb11ddf8cb952ae2b47a4b95456604a5583ba99d6c04ea9ccb25343813b` (**independently recalculated against the preserved CSV; matches**).
