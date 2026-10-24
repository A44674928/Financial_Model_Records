# Comprehensive Portfolio History v5 — Update Audit Only

**Scope:** audit the newly attached `comprehensive_portfolio_history_20261023.csv` against the prior v4 file, the active Oct. 23 v2 close set, current model-session marks, and the authoritative US10Y/US30Y input files. **This is an audit only: v5 has not been adopted, and no model input, report, chart, or output was changed.**

## Audit files

- New attached input, preserved as v5: [`data/comprehensive_portfolio_history_20261023_v5.csv`](../../data/comprehensive_portfolio_history_20261023_v5.csv)
- Full v4-to-v5 row audit (1,365 rows): [`data/comprehensive_history_reconciliation_v4_to_v5.csv`](../../data/comprehensive_history_reconciliation_v4_to_v5.csv)
- Oct. 23 v5 comparison with active v2 and preserved v1 (35 rows): [`data/comprehensive_history_endpoint_vs_active_v2_20261023_v5.csv`](../../data/comprehensive_history_endpoint_vs_active_v2_20261023_v5.csv)
- Current model-session comparison (1,188 rows): [`data/comprehensive_history_vs_model_sessions_v5.csv`](../../data/comprehensive_history_vs_model_sessions_v5.csv)
- US10Y/US30Y comparison against existing user-provided close files (78 rows): [`data/comprehensive_history_yields_vs_active_inputs_v5.csv`](../../data/comprehensive_history_yields_vs_active_inputs_v5.csv)
- Prior v4 audit: [`comprehensive-history-v4-reconciliation.md`](comprehensive-history-v4-reconciliation.md)

## Coverage and changes from v4

V4 and v5 have identical coverage: **1,365 date/ticker rows**, 39 dates, and 35 tickers, with no missing or duplicate keys. Relative to v4:

- **1,352** numeric closes changed; **13** are unchanged.
- Source labels changed on **117** rows: all 39 US10Y, 39 US30Y, and 39 XRH0 rows.
- 1,238 rows changed only their value; 114 changed both value and source; three changed source only; ten were fully unchanged. In total, 1,355 rows changed in at least one field.
- The model-session calendar overlaps v5 on 36 sessions for each of 33 modeled symbols. **1,178 of 1,188** model prices differ from the current marks.

The update restores several values that were out of scale in v4: for example, Oct. 23 BTC changes from $411.72 to **$68,250.00**, ETH from $382.72 to **$2,540.00**, and RIVN from $267.90 to **$11.25**. NFLX remains **$65.85** on Oct. 23.

## Oct. 23 endpoint vs active v2

Only **12 of 35 prices match** the active v2 file; **23 differ**. Four source labels differ (BRENT, OIL, LCID, and XRH0). The detailed deltas are in the endpoint CSV.

Examples of material or constraint-related differences:

| Ticker | v5 | Active v2 | Note |
|---|---:|---:|---|
| NFLX | $65.85 | $762.10 | v5 matches preserved v1 ($65.85) |
| GEV | $175.20 | $185.60 | v5 differs from active endpoint |
| INTC | $22.40 | $24.85 | v5 differs from active endpoint |
| TMO | $572.10 | $524.30 | v5 differs from active endpoint |
| LCID | $3.52 | $3.55 | Active value is the user-confirmed constraint |
| XRH0 | $780.00 | $790.00 | Active value is the system constraint |

The v5 LCID closes for Oct. 20–23 are **$3.492, $3.476, $3.526, and $3.52**, not the user-specified **$3.27, $3.21, $3.46, and $3.55**. V5 marks XRH0 at $780 on Oct. 23 rather than the established $790 constraint.

## Treasury-series cross-check

V5 has 39 rows each for US10Y and US30Y. Compared with the existing user-provided yield inputs, each series has 37 overlapping dates: **36 values differ and one (Oct. 23) matches**. The two dates without an active close in the existing files are Sep. 7 and Oct. 12. For example, v5 gives Oct. 22 US10Y **4.879%** versus the active **4.96%**, and US30Y **5.422%** versus **5.29%**. The current user-provided Treasury inputs were not replaced.

## Energy-only impact check

V5’s Oct. 23 BRENT/OIL marks match the active values: **$117.345 / $103.45**. On Oct. 22, v5 has **$117.554 / $103.083**, versus the current model’s pinned marks of $113.17 / $99.47. A controlled calculation replacing only BRENT/OIL history with v5 and holding all other data and the active Oct. 23 marks fixed changes each model’s Oct. 22 total by **+$4,382.31**; the largest daily total change is **$7,585.12**. The Oct. 23 terminal energy PnL is unchanged in that energy-only comparison.

The NFLX Oct. 23 mark remains consequential: using only v5’s $65.85 close, while holding other current inputs fixed, would change the one-unit LONG’s unrealized PnL from **+$103,644.50** at active v2’s $762.10 to **−$180.44**. This is an isolated cell comparison, not a v5 portfolio recalculation.

## Provenance

The v4 input SHA-256 is `1b33da61e1abb94d42c78109e5a95e3849aa6e60587448aab3d8e91ca269cc2b`; the new v5 input SHA-256 is `47d195834223ff6d98fb257615172c5c694d1377dbae2541b3d8c739af0c7a8c`.
