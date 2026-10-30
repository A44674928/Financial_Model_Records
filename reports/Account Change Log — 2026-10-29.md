# Account Change Log — October 29, 2026

> Chronological source log. Transaction times are used only where shown; no timezone is inferred. Model/policy changes are distinguished from transactions.

## Reported activity and recorded changes

| Time (as shown) | Book / type | Instrument | Recorded change | Recognized amount / source display |
|---|---|---|---|---|
| 10:41:38 screenshot time; void time not supplied | Separate Private Fund / close nullification | USOIL | Close-long record **nullified and voided**; retain 601,218,118-unit long open at $99.18 entry | $0.00 realized; screenshot close $102.14 / +$1,779,605,629.28 preserved only as voided-source evidence; no mark assigned |
| 10:41:44 screenshot time; void time not supplied | Separate Private Fund / close nullification | BRENT | Close-long record **nullified and voided**; retain 538,566,907-unit long open at $114.043 entry | $0.00 realized; screenshot close $115.777 / +$933,875,016.74 preserved only as voided-source evidence; no mark assigned |
| 11:05:57; timezone not shown | Private Fund report / filled order | LCID | Buy market, 301,204,819.27 shares at $3.32; order 3736492349 | $999,999,999.98 purchase value; distinct lot, not realized PnL |
| Date only | User-directed hypothetical offer reference | LCID | Record the hypothetical offer at the supplied current market capitalization | $1.31B user-supplied; not independently verified; no per-share price or exchange ratio calculated |
| Date only | Model/policy control | Multi-asset | Retroactive influencer/AI screen applied; listed tickers and third-party commentary excluded from active replay | Historical records preserved; not a trade or cash movement |
| Date only | Model/policy control | Oil | Authorized Oil v2 mark-forward through October 26 while retaining October 19 trade-event cutoff | Not an October 29 valuation; no later trade events used |
| Date only | Audit scenario | BRENT / OIL | Eight short lifecycle scenarios represented as un-nullified for audit testing | Scenario-only; source history unchanged; not active account positions |

## Interpretation and controls

- The source screenshots display two Private Fund / TradingView Paper Trading long closes. Per the user's clarification, both closes are **nullified and voided**; retain the earlier longs open at $114.043 (BRENT) and $99.18 (USOIL), using the reported quantities. Entry dates/times and account mapping remain unknown. The screenshot close prices are not used as marks, and **$0.00 is recognized as realized PnL**. Platform void status is not independently confirmed; the screenshots remain preserved as source evidence.
- The LCID order is a **buy**, not a sell or close. Its account selector is truncated, no post-fill mark or funding source is supplied, and it is not netted with the older LCID screenshot position.
- The LCID $1.31B market-cap figure is the user's hypothetical reference as of October 29. It is not an actual bid, agreed consideration, completed transaction, per-share value, or exchange ratio.
- The Oil v2 mark-forward and AI/ticker screen are control/replay changes, not transactions. The under-duress short restoration changes the audit-test representation only; source records and active Oil v2 remain unchanged.
- No cross-book realized PnL, cash, NAV, or account total is calculated. No financing or leverage is inferred.

## Machine-readable log

[`data/account_change_log_2026-10-29_v1.csv`](../data/account_change_log_2026-10-29_v1.csv) contains the source IDs, files, timestamps, quantities, prices, amounts, and status notes.
