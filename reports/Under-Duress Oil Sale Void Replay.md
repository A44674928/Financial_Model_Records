# Under-Duress Oil Sale Void Replay

> **Scenario overlay, not a change to source history.** At the user's direction, oil sales and closes identified below are treated as voidable under duress in this replay. Original screenshots, trade logs, ATS reports, and historical realized-PnL records remain preserved and unchanged. This is a hypothetical portfolio reconstruction, not audited brokerage accounting or legal advice.

## Replay policy

- A voided close is skipped by the replay; its original event remains in the audit trail. Long sales restore their linked long lots. The ATS sensitivity short openings and their linked covers are explicitly nullified per the user's latest direction, so they create no open short positions. No cross-book netting or silent deletion is performed.
- This replay covers the ATS locked $200 LONG foundation liquidation; the documented legacy oil trims; the named October 26 50U cash-outs; the October 29 TradingView Paper Trading closes; and the ATS 10U/20U/30U/40U close sensitivities. ATS scenario rows are alternatives, not additive positions.
- The ATS foundation is restored from the last pre-liquidation modeled allocation snapshot dated October 26, 2026. Its quantity equivalents and values are model outputs, not verified contracts or broker fills; exact liquidation quantities, fills, and timing remain unknown.
- Per-book marks are the event price or last documented pre-liquidation mark. They are not all a single simultaneous portfolio valuation. Contract multipliers, fees, taxes, funding sources, and leverage are not inferred.

## Restored positions

The following table is an event-level restoration overlay: it adds back lots affected by the voided closes, while unaffected open lots remain in their original book records. It is not a complete account holdings export. Rows in a sensitivity group are alternatives; do **not** add them together. The two foundation rows, the private-fund paper-trade lots, the legacy core lots, and ATS/manual campaign rows are distinct books and are not combined into one fund total.

| Book / scenario | Ticker | Restored side | Quantity | Basis | Mark | Conditional unrealized PnL |
|---|---|---:|---:|---:|---:|---:|
| ATS locked $200 LONG foundation / all-units reported liquidation | BRENT | LONG | 179865012.22971259 modeled quantity equivalent | $108.447312 | $115.380000 (2026-10-26) | $1,246,948,058.69 |
| ATS locked $200 LONG foundation / all-units reported liquidation | OIL (USOIL) | LONG | 204760619.11636445 modeled quantity equivalent | $95.261858 | $101.300000 (2026-10-26) | $1,236,373,664.12 |
| Private fund / TradingView Paper Trading / screenshot close | BRENT | LONG | 538566907 screenshot quantity | $114.043000 | $115.777000 (2026-10-29) | $933,875,016.74 |
| Private fund / TradingView Paper Trading / screenshot close | USOIL | LONG | 601218118 screenshot quantity | $99.180000 | $102.140000 (2026-10-29) | $1,779,605,629.28 |
| Core legacy paper model / legacy baseline target trim | BRENT | LONG | 10 U ($10,000 notional each) | $111.412000 | $117.000000 (2026-10-23) | $5,015.62 |
| Core legacy paper model / legacy baseline target trim | OIL (USOIL) | LONG | 10 U ($10,000 notional each) | $99.040000 | $102.000000 (2026-10-23) | $2,988.69 |
| Core / manual live test lot / paired 50U lot cash-out | BRENT | LONG | 50 U ($10,000 notional each) | $115.510000 | $117.409000 (2026-10-26) | $8,220.07 |
| Core / ATS mirror live test lot / paired 50U lot cash-out | OIL (USOIL) | LONG | 50 U ($10,000 notional each) | $101.110000 | $102.710000 (2026-10-26) | $7,912.17 |
| ATS 50U campaign sensitivity / 10U ATS exit sensitivity | BRENT | LONG | 10 U ($10,000 notional each) | $111.412000 | $118.000000 (2026-10-23) | $5,913.19 |
| ATS 50U campaign sensitivity / 20U ATS exit sensitivity | BRENT | LONG | 20 U ($10,000 notional each) | $111.412000 | $118.000000 (2026-10-23) | $11,826.37 |
| ATS 50U campaign sensitivity / 30U ATS exit sensitivity | BRENT | LONG | 30 U ($10,000 notional each) | $111.412000 | $118.000000 (2026-10-23) | $17,739.56 |
| ATS 50U campaign sensitivity / 40U ATS exit sensitivity | BRENT | LONG | 40 U ($10,000 notional each) | $111.412000 | $118.000000 (2026-10-23) | $23,652.75 |
| ATS 50U campaign sensitivity / 10U ATS exit sensitivity | OIL (USOIL) | LONG | 10 U ($10,000 notional each) | $99.040000 | $103.500000 (2026-10-23) | $4,503.23 |
| ATS 50U campaign sensitivity / 20U ATS exit sensitivity | OIL (USOIL) | LONG | 20 U ($10,000 notional each) | $99.040000 | $103.500000 (2026-10-23) | $9,006.46 |
| ATS 50U campaign sensitivity / 30U ATS exit sensitivity | OIL (USOIL) | LONG | 30 U ($10,000 notional each) | $99.040000 | $103.500000 (2026-10-23) | $13,509.69 |
| ATS 50U campaign sensitivity / 40U ATS exit sensitivity | OIL (USOIL) | LONG | 40 U ($10,000 notional each) | $99.040000 | $103.500000 (2026-10-23) | $18,012.92 |

### Screenshot PnL treatment

For the October 29 private-fund TradingView Paper Trading closes, the reported transaction PnL is **not realized in this scenario**. If the closes are voided, each lot remains open and its screenshot-reported close price is used as a conditional mark; the prior screenshot PnL is shown as unrealized rather than added again as realized cash. TradingView Paper Trading is not independently audited brokerage execution.

### ATS campaign sensitivities

The modeled ATS long exits restore the corresponding 10U, 20U, 30U, or 40U of the tagged 50U campaign lot. Per the user's latest direction, the matching short-opening and subsequent cover/closure lifecycle is nullified in every sensitivity: **the replay has no open ATS shorts**. The eight nullification decisions remain in the event register but do not appear as restored positions. Quantities are user-reported/model sensitivities, not a verified ATS fill history; each scenario remains separate.

Nullified short-lifecycle records: **8** (BRENT and OIL/USOIL at the 10U, 20U, 30U, and 40U sensitivities). These are audit actions, not positions.

## LCID buyout consideration as scenario funding

| Hypothetical funding component | Amount | Treatment in this replay |
|---|---:|---|
| Cash consideration | $2,200,000,000.00 | Scenario cash funding component; not verified as received or allocated |
| Share/equity consideration | $2,000,000,000.00 | Non-cash scenario value; not treated as spendable cash |
| **Total consideration pool** | **$4,200,000,000.00** | **Hypothetical restoration pool; unallocated across books** |

The LCID terms remain hypothetical, not an actual bid or completed transaction. The $1.31B current market-cap reference is user-provided for 2026-10-29. For this replay only, the full $4.2B consideration is tagged as new scenario funding to compensate for the voided oil-sale scenario, while retaining the $2.2B cash / $2.0B equity distinction. No proceeds are claimed as received; the pool is not assigned to BRENT, OIL, or any specific account, and is not included in a cash balance or reconciled NAV.

## Source event register and audit limits

The versioned event register contains **24** scenario actions, including **8** short-lifecycle nullifications. The restored-position file contains **16** position rows: [`under_duress_oil_restored_positions_v1.csv`](../data/under_duress_oil_restored_positions_v1.csv). The full event register is [`under_duress_oil_void_events_v1.csv`](../data/under_duress_oil_void_events_v1.csv); scenario funding terms are [`under_duress_lcid_scenario_funding_v1.csv`](../data/under_duress_lcid_scenario_funding_v1.csv).

The user's prior report of zero oil units after the ATS liquidation and the earlier realized-PnL records remain part of the preserved historical source record. This replay is a parallel what-if view that marks selected close events voidable; it does not establish that any broker or ATS reversed an execution. Unknown ATS quantities are not turned into actual holdings; only the last documented modeled allocation is restored as quantity equivalents.
