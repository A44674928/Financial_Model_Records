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

## Live Yahoo endpoint spot-check (partial)

A live Yahoo Finance chart-data check of the **Oct. 23, 2026** daily bars verified three representative U.S. equities:

| Ticker | Yahoo daily close | Candidate Yahoo column | Active v2 | v6 |
|---|---:|---:|---:|---:|
| AAPL | $347.73 | $347.73 | $347.73 | $347.73 |
| AMZN | $248.00 | $248.00 | $192.45 | $185.20 |
| NFLX | $65.85 | $65.85 | $762.10 | $65.85 |

The candidate Yahoo values match the live closes for all three. This spot-check also flags likely wrong active-reference endpoints for AMZN and NFLX; **no active model input or output was changed**. Full 39-date × 35-ticker live verification has not been completed, and no broad historical refresh is represented by this three-row spot-check. The row-level live evidence is in [`data/multi_source_portfolio_live_yahoo_endpoint_check.csv`](../../data/multi_source_portfolio_live_yahoo_endpoint_check.csv).

The Sep. 7 U.S. holiday rows remain invalid for listed U.S. equities/ETFs and U.S. Treasury yields; a refreshed file must retain the date grid but mark those rows as no-session, not use their supplied values as closes. The original candidate remains preserved unchanged.

## Row-level audit artifacts

- [`data/multi_source_portfolio_formula_check.csv`](../../data/multi_source_portfolio_formula_check.csv) — each source value, recalculated mean, rounding check, and custom-vs-midpoint check (1,365 rows).
- [`data/multi_source_portfolio_endpoint_comparison.csv`](../../data/multi_source_portfolio_endpoint_comparison.csv) — all 35 Oct. 23 tickers against active v2 and v6.
- [`data/multi_source_portfolio_pattern_summary.csv`](../../data/multi_source_portfolio_pattern_summary.csv) — per-ticker trend, source spread, and endpoint comparisons.

**Assessment:** structurally complete and its average formula checks out, but source provenance, smooth monotonic series, the holiday rows, and conflicts with confirmed marks mean it is **not suitable as an accurate EOD price file yet**. Keep it as an audit candidate; do not use it to refresh model results until the underlying source values are verified.

Input SHA-256: `c0afecb11ddf8cb952ae2b47a4b95456604a5583ba99d6c04ea9ccb25343813b` (**independently recalculated against the preserved CSV; matches**).
