# Comprehensive Portfolio History v4 — Reconciliation Only

**Scope:** compare the revised `comprehensive_portfolio_history_20261023-4.csv` with the prior comprehensive file, the active Oct. 23 v2 close set, and the current model-session marks. This is an audit, not an adoption of v4: **the model inputs, reports, charts, and outputs were not changed.**

## Files

- Revised input: [`data/comprehensive_portfolio_history_20261023_v4.csv`](../../data/comprehensive_portfolio_history_20261023_v4.csv)
- Prior comprehensive input: [`data/comprehensive_portfolio_history_20261023_v3.csv`](../../data/comprehensive_portfolio_history_20261023_v3.csv)
- Full v3-to-v4 row audit (1,365 rows): [`data/comprehensive_history_reconciliation_v3_to_v4.csv`](../../data/comprehensive_history_reconciliation_v3_to_v4.csv)
- Oct. 23 comparison against active v2 and preserved v1 (35 rows): [`data/comprehensive_history_endpoint_vs_active_20261023.csv`](../../data/comprehensive_history_endpoint_vs_active_20261023.csv)
- All modeled sessions compared with v4 (1,188 rows): [`data/comprehensive_history_vs_model_sessions_v4.csv`](../../data/comprehensive_history_vs_model_sessions_v4.csv)

## Coverage and changes

Both comprehensive files contain the same **1,365 date/ticker keys**: 39 dates and 35 tickers, with no missing or duplicate keys. Between v3 and v4:

- **1,354** close values changed; **11** close values are unchanged.
- Source labels changed on **156 rows**: all 39 rows each for LCID, US10Y, US30Y, and XRH0. Their v4 labels are Yahoo Finance, Federal Reserve, Federal Reserve, and London Stock Exchange, respectively.
- In the 1,365-row comparison, 1,202 rows change value only, 152 change both value and source label, four change source only, and seven are fully unchanged.
- The file has dates Sep. 1–Oct. 23. Three dates (Sep. 1, Sep. 2, and Sep. 7) are outside the model’s 36-session calendar.

Against the active Oct. 23 v2 close set, **26 of 35 prices differ** and six source labels differ. In the 1,188 common model-session observations, **1,180 prices differ** from the current model marks.

## Material conflicts requiring review

| Ticker / mark | v4 | Active v2 | Prior v1 / other constraint |
|---|---:|---:|---:|
| NFLX, Oct. 23 | $65.85 | $762.10 | v1 was $65.85 |
| BTC, Oct. 23 | $411.72 | $68,250.00 | v1 was $81,227.04 |
| ETH, Oct. 23 | $382.72 | $2,640.00 | v1 was $2,408.47 |
| RIVN, Oct. 23 | $267.90 | $11.25 | v1 was $11.83 |
| LCID, Oct. 23 | $3.52 | $3.55 | user-specified mark is $3.55 |
| XRH0, Oct. 23 | $780.00 | $790.00 | existing system constraint is $790.00 |

The v4 LCID series is $3.51, $3.52, $3.52, and $3.52 for Oct. 20–23, respectively, differing from the user-specified $3.27, $3.21, $3.46, and $3.55. The v4 Treasury source labels also change to Federal Reserve; the existing user-provided daily series was not replaced.

## Energy-only impact check

V4's Oct. 23 energy closes match active v2: **BRENT $117.345** and **OIL $103.45**. Its Oct. 22 values are **BRENT $116.962** and **OIL $103.09**, compared with the current model's pinned Oct. 22 marks of $113.17 and $99.47. A controlled calculation replacing only BRENT/OIL history with v4 while keeping all other inputs and the active Oct. 23 marks fixed changes each model's Oct. 22 total by **+$4,109.21**; the largest daily total change is **$7,225.12**. The Oct. 23 terminal energy PnL is unchanged in that energy-only comparison.

Using only v4's NFLX Oct. 23 close, while holding every other current input fixed, would change the one-unit LONG's unrealized PnL from **+$103,644.50** at $762.10 to **−$180.44** at $65.85. This illustrates why the source choice is material; it is not a full v4 portfolio recalculation.

## Provenance

The preserved v3 input SHA-256 is `79b60172cd6bec248b44b97f4bdeb424343671ea1927a48be1f1e5be2e2906e5`; the v4 input SHA-256 is `1b33da61e1abb94d42c78109e5a95e3849aa6e60587448aab3d8e91ca269cc2b`.
