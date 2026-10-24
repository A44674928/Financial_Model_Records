# Comprehensive Portfolio History v6 — Update Audit Only

**Scope:** audit the newly attached `comprehensive_portfolio_history_20261023 2.csv` against v5, active Oct. 23 v2 closes, current model-session marks, and the active user-provided US10Y/US30Y inputs. **This is audit-only: v6 has not been adopted and no model inputs, reports, charts, or outputs were changed.**

## Audit files

- New attachment preserved as v6: [`data/comprehensive_portfolio_history_20261023_v6.csv`](../../data/comprehensive_portfolio_history_20261023_v6.csv)
- Full v5-to-v6 comparison (1,365 rows): [`data/comprehensive_history_reconciliation_v5_to_v6.csv`](../../data/comprehensive_history_reconciliation_v5_to_v6.csv)
- Oct. 23 comparison with active v2 and v1 (35 rows): [`data/comprehensive_history_endpoint_vs_active_v2_20261023_v6.csv`](../../data/comprehensive_history_endpoint_vs_active_v2_20261023_v6.csv)
- Current model-session comparison (1,188 rows): [`data/comprehensive_history_vs_model_sessions_v6.csv`](../../data/comprehensive_history_vs_model_sessions_v6.csv)
- Treasury comparison against existing user inputs (78 rows): [`data/comprehensive_history_yields_vs_active_inputs_v6.csv`](../../data/comprehensive_history_yields_vs_active_inputs_v6.csv)
- Previous update audit: [`comprehensive-history-v5-reconciliation.md`](comprehensive-history-v5-reconciliation.md)

## Coverage and scope of update

V5 and v6 have the same **1,365 date/ticker keys**, covering 39 dates and 35 tickers, with no duplicate keys. Source labels are unchanged. However, **1,343 numeric values changed** and only 22 rows are identical; every ticker has at least some changed values. This is a broad data revision, not a small cell-only patch.

Against active v2 on Oct. 23, **24 of 35 prices differ** and four source labels differ. Across 33 modeled tickers and 36 model sessions, **1,179 of 1,188 closes differ** from the current model marks.

## Review flags

Some v6 values restore plausible scale relative to v5—for example, BTC and RIVN remain near their active-v2 levels, and NFLX remains $65.85. But the v6 rows also contain abrupt adjacent-day moves that warrant cell-level verification before adoption. Examples from Oct. 22 to Oct. 23 include:

- ETH: **$104.42 → $2,650.00** (+2,438%)
- LLY: **$104.32 → $780.50** (+648%)
- TMO: **$104.20 → $540.20** (+418%)
- LMT: **$104.71 → $460.00** (+339%)
- SPCX: **$104.48 → $31.40** (−70%)

The endpoint audit contains all 35 row deltas. Larger differences versus active v2 include NFLX **$65.85 vs. $762.10**, SPCX **$31.40 vs. $112.50**, LMT **$460.00 vs. $582.40**, and CAT **$320.15 vs. $395.20**. NFLX v6 matches preserved v1 at $65.85.

User-confirmed constraints still conflict with v6: its Oct. 20–23 LCID values are **$3.53, $3.57, $3.54, and $3.52**, versus the specified **$3.27, $3.21, $3.46, and $3.55**; XRH0 remains $780 rather than the active $790 system constraint.

## Treasury inputs

For each of US10Y and US30Y, v6 has 39 rows, with 37 overlapping dates in the active user-provided files. **36 values differ and one (Oct. 23) matches**; Sep. 7 and Oct. 12 have no active close in those files. The audit CSV gives every date-level difference. The active Treasury inputs were not replaced.

## Energy-only impact check

The Oct. 23 BRENT/OIL marks still match active v2 at **$117.345 / $103.45**. V6's Oct. 22 marks are **$117.091 / $102.928**, versus the current model's pinned **$113.17 / $99.47**. Replacing only the energy history with v6 while keeping all other current inputs and active Oct. 23 marks fixed would move each model's Oct. 22 total by **+$4,065.38**; the largest daily total change would be **$8,078.80**. The Oct. 23 terminal energy PnL would be unchanged in that isolated comparison.

## Conclusion and provenance

The file is structurally complete, but the number of changed rows, the adjacent-day discontinuities, conflicts with confirmed LCID/XRH0 values, and Treasury differences make it **not ready for direct model adoption without resolving the flagged cells/source basis**. No model outputs were refreshed.

V5 SHA-256: `47d195834223ff6d98fb257615172c5c694d1377dbae2541b3d8c739af0c7a8c`

V6 SHA-256: `16d8d9e131db5e24cc490939ce90ca08bf23b1170d31eae83c0ec673edb57855`
