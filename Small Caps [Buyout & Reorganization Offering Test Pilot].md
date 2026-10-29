# Small Caps [Buyout & Reorganization Offering Test Pilot]

A separate small-cap pilot book for five user-specified LCID LONG entries. All five entries are $10,000 each (five standard units, $50,000 total after Oct. 23). The current four-model daily replay now includes all five entries through the Oct. 23 EOD close; the Oct. 22 historical comparison remains available as an earlier row in the daily exports.

## Pilot Basket

| Date | Side | Entry | Notional |
|---|---|---:|---:|
| 2026-10-20 | LONG | $2.92 | $10,000 |
| 2026-10-20 | LONG | $3.01 | $10,000 |
| 2026-10-21 | LONG | $3.30 | $10,000 |
| 2026-10-22 | LONG | $3.43 | $10,000 |
| 2026-10-23 | LONG | $3.47 | $10,000 |

## User-Provided Daily Marks and Basket PnL

![LCID small-caps pilot daily PnL and marks](Charts/performance/18-lcid-small-caps-pilot-pnl.png)

| Date | Daily mark | Active entries | Deployed | Open PnL | Return on deployed |
|---|---:|---:|---:|---:|---:|
| 2026-10-20 | $3.27 | 2 | $20,000 | $+2,062.42 | +10.312% |
| 2026-10-21 | $3.21 | 3 | $30,000 | $+1,384.88 | +4.616% |
| 2026-10-22 | $3.46 | 4 | $40,000 | $+3,916.64 | +9.792% |
| 2026-10-23 | $3.52 | 5 | $50,000 | $+4,822.30 | +9.645% |

- At the Oct. 22 historical comparison cutoff, four entries are active: **$40,000 deployed**, marked at **$3.46**, with **$+3,916.64** open PnL.
- The Oct. 23 EOD view includes all five entries: **$50,000 deployed**, marked at **$3.52**, with **$+4,822.30** open PnL. This is the LCID mark used in the current four-model daily replay.
- The four model variants have the same LCID contribution because the pilot contains LONG entries only; this adds exposure and PnL but does not alter the variants' relative LCID path.
- Daily marks are `$3.27`, `$3.21`, `$3.46`, and the user-corrected `$3.52` for Oct. 20–23, respectively. The prior Oct. 23 `$3.55` mark is preserved in `data/lcid_small_caps_pilot_daily_marks_v1.csv`; the active correction is separate from the five entry fills in `trades/LCID.txt`.
- Entry fills use the user's provided prices; PnL is `notional × (daily mark / entry price − 1)`. No commissions or other costs are included.

Daily export: [`lcid_small_caps_pilot_daily_pnl.csv`](data/lcid_small_caps_pilot_daily_pnl.csv).

Ledger: [`trades/LCID.txt`](trades/LCID.txt).

## Current-date hypothetical buyout offer — 2026-10-29

At the user's direction, record a **market-cap-level hypothetical offer** without deriving a per-share price or exchange ratio:

| Term | User-directed amount |
|---|---:|
| User-supplied LCID current market-cap reference (2026-10-29) | $1,310,000,000 |
| Share/equity consideration, stated as aggregate value | $2,000,000,000 |
| Cash consideration | $2,200,000,000 |
| **Total hypothetical consideration** | **$4,200,000,000** |

The $2.0B share/equity component is $690M, or **52.67%**, above the stated $1.31B current market-cap reference. Total consideration is $2.89B above that reference, equal to **3.21×** the current market cap (**220.61% above**). Since the total includes $2.2B cash, that total-to-market-cap comparison is not a per-share premium calculation.

No share count, diluted share count, exchange ratio, per-share offer price, debt/cash adjustment, or financing source was supplied or inferred. The $1.31B market-cap reference is user-provided for 2026-10-29; its source/time was not supplied. This is a hypothetical planning scenario only—not a submitted, authorized, or public buyout offer, and not a statement that the proposed consideration is funded or available.

### Separate under-duress oil replay funding treatment

For the under-duress oil-sale replay only, the full **$4.2B** hypothetical consideration is tagged as a new scenario restoration-funding pool, separated into **$2.2B cash** and **$2.0B non-cash share/equity value**. The pool is unallocated and unreceived; it does not convert the offer into a real acquisition or make the share component spendable cash. See [`Under-Duress Oil Sale Void Replay.md`](reports/Under-Duress%20Oil%20Sale%20Void%20Replay.md).

Main comparison: [`Model Performance Comparison.md`](Model%20Performance%20Comparison.md).
