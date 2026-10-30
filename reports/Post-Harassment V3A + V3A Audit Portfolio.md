# Post-Harassment V3A + V3A Audit Portfolio

**Portfolio type:** Separate hypothetical chart-only model scenario; not a verified brokerage, ATS, or TradingView account.
**Rebuild status:** Recomputed from normalized chart-context records with explicit manual/ATS/user-directed events excluded.
**Valuation as of:** **2026-10-26**, the latest complete synchronized TradingView mark date available in the repository.
**Requested through:** 2026-10-30; **not fully reached** because no complete aligned TradingView marks for October 27–30 are present.
**Account-level restoration:** Not verified; this is a paper-model reconstruction, not proof of historical or current holdings.

## Methodology applied from scratch

- **Strategy:** V3A core + the V3A-specific 1U/EOD force model. This is the requested V3A/V3A method, run as two auditable model components and then summed for the hypothetical scenario.
- **Scope:** No 10U/DAY DXY add-on, no chart-commentary DXY direction, and no energy daily-buy sidecar. Direct chart-originated BRENT/OIL and oil-linked core entries are kept in their own rows in this hypothetical replay; they are not copied from the separate Oil book or its scenarios.
- **Events:** Started from the standardized `trades/*.txt` event records. Chart/trade events are capped at **2026-10-19**. Events explicitly identified as manual, ATS, user-directed/reported, cash-out, or override are excluded, as are explicit third-party commentary/signal-badge items, ambiguous inferred directions, news-based rationale, and records without chart/timeframe/technical context.
- **Screens:** The standing exclusions `AAPL`, `AMZN`, `INTC`, `META`, `NVDA`, `PLTR`, and `TSLA` remain out of active screened analytics. DXY direction is excluded. No formerly blocked ticker is reactivated.
- **Marks and force schedule:** The user’s October 30 request is recorded as a scoped, portfolio-only exception permitting existing TradingView EOD marks and the mechanical V3A 1U/EOD tranche schedule through October 26, based only on chart directions eligible through October 19. No user-sourced event after October 19 is ingested. The exception does not change the global TradingView policy or authorize other portfolios to use post-cutoff data. See [the scoped exception](TradingView%20Scoped%20Exception%20%E2%80%94%20Post-Harassment%20V3A%20%2B%20V3A%20Replay.md).
- **Chart handling:** The replay uses already-normalized chart-context records; it does not OCR or independently reinterpret every image in `Charts/` or `Archive/`. The 126 event records were audited; **38** passed the stated filters. The full include/exclude trail is in the event audit CSV.

## Model result at 2026-10-26

| Component | Realized PnL | Unrealized PnL | Total modeled PnL | Cumulative gross additions | Gross open notional | Open units |
|---|---:|---:|---:|---:|---:|---:|
| V3A core | $0.00 | $25,430.38 | $25,430.38 | $370,000.00 | $370,000.00 | 37U |
| V3A-specific 1U/EOD force | $0.00 | $102,292.92 | $102,292.92 | $3,990,000.00 | $3,990,000.00 | 399U |
| **Combined V3A + V3A scenario** | **$0.00** | **$127,723.30** | **$127,723.30** | **$4,360,000.00** | **$4,360,000.00** | **436U** |

No realized PnL is recorded in this replay. The force model continues its specified 1U/EOD additions in the carried direction through the latest available mark date; those are hypothetical model lots, not actual orders or fills. The modeled peak-to-trough PnL drawdown is **$18,928.61** from September 14 to September 30.

## Populated open-position schedule

The table aggregates the two components by ticker and side; it does **not** net opposing sides. Each `U` is $10,000 of model entry notional, not shares or contracts. Marks and unrealized PnL are as of October 26.

| Ticker | Side | V3A core (U) | V3A force (U) | Combined (U) | Gross model notional | Unrealized PnL |
|---|---|---:|---:|---:|---:|---:|
| BRENT | LONG | 5 | 24 | 29 | $290,000.00 | $22,422.23 |
| CAT | LONG | 1 | 6 | 7 | $70,000.00 | -$2,177.80 |
| CAT | SHORT | 2 | 10 | 12 | $120,000.00 | $16,379.55 |
| CVX | LONG | 2 | 28 | 30 | $300,000.00 | $26,882.31 |
| DIS | SHORT | 1 | 26 | 27 | $270,000.00 | -$8,672.63 |
| GEV | LONG | 1 | 12 | 13 | $130,000.00 | -$9,225.56 |
| HD | LONG | 1 | 29 | 30 | $300,000.00 | $21,034.23 |
| LLY | LONG | 1 | 11 | 12 | $120,000.00 | $3,784.23 |
| LMT | LONG | 4 | 16 | 20 | $200,000.00 | $38,654.97 |
| NET | LONG | 1 | 28 | 29 | $290,000.00 | -$2,969.18 |
| NFLX | LONG | 1 | 16 | 17 | $170,000.00 | -$11,972.51 |
| OIL | LONG | 4 | 25 | 29 | $290,000.00 | $23,329.38 |
| ORCL | LONG | 1 | 6 | 7 | $70,000.00 | -$1,033.25 |
| PEP | LONG | 1 | 12 | 13 | $130,000.00 | $4,014.27 |
| RIVN | LONG | 1 | 16 | 17 | $170,000.00 | -$21,596.73 |
| SPCX | SHORT | 3 | 15 | 18 | $180,000.00 | $9,863.55 |
| TMO | LONG | 1 | 15 | 16 | $160,000.00 | $2,825.23 |
| UPS | SHORT | 1 | 11 | 12 | $120,000.00 | -$3,093.68 |
| V | LONG | 1 | 11 | 12 | $120,000.00 | $1,089.63 |
| VLO | LONG | 1 | 13 | 14 | $140,000.00 | -$3,200.26 |
| WMT | LONG | 1 | 16 | 17 | $170,000.00 | $9,564.25 |
| XLE | LONG | 1 | 16 | 17 | $170,000.00 | $8,314.80 |
| XRH0 | LONG | 1 | 37 | 38 | $380,000.00 | $3,506.28 |

Position-level unrealized PnL is rounded to cents per ticker/side; summing those rounded rows can differ from the unrounded model total by $0.01.

## Limits and restoration status

This is the most complete **chart-context-only model replay supported by the current normalized inputs and eligible screens**, not a verified account restoration or proof of zero manual influence in the source history. The 88 excluded records, including all explicitly tagged manual/ATS/user-directed events, remain preserved in the audit CSV. Unattributed provenance cannot be proven manual-free merely by absence of a manual tag.

The previous user-specified rollback-test short list (INTC/META/CAT/PLTR/TSLA) is **not** used as this chart-only portfolio’s holdings. Those test quantities remain in the separate October rollback test; blocked tickers remain excluded here. No account mapping, opening cash, actual share count, broker/ATS fills, funding, current NAV, or financing is inferred. The all-cash/debit convention is preserved; model notional does not establish that the hypothetical account had funds to hold it. Costs, taxes, and slippage are not modeled.

The original `TWM_1M_LIGHT` output is not reused: it includes manual/ATS/user-reported inputs. This replay is a separate, source-filtered V3A/V3A reconstruction and is **not an independently reselected performance winner**. Its reported PnL is historical model output, not an account return or forecast.

## Reproducible artifacts

- [Daily V3A/V3A replay](../data/post_harassment_v3a_v3a_chart_only_daily_v1.csv)
- [Open positions by component and ticker](../data/post_harassment_v3a_v3a_chart_only_positions_v1.csv)
- [Included/excluded normalized-event audit](../data/post_harassment_v3a_v3a_chart_only_event_audit_v1.csv)
- [Machine-readable summary](../data/post_harassment_v3a_v3a_chart_only_summary_v1.json)
- [Input hash and output manifest](../data/post_harassment_v3a_v3a_chart_only_manifest_v1.json)
- Builder: [`scripts/build_post_harassment_chart_only_replay.py`](../scripts/build_post_harassment_chart_only_replay.py)
- The separate [October 2026 Short Closure Rollback Test](October%202026%20Short%20Closure%20Rollback%20Test.md) remains scenario-only and unchanged; source books/logs were not rewritten.
