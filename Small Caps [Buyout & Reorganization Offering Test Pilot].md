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
| 2026-10-23 | $3.55 | 5 | $50,000 | $+5,289.53 | +10.579% |

- At the Oct. 22 historical comparison cutoff, four entries are active: **$40,000 deployed**, marked at **$3.46**, with **$+3,916.64** open PnL.
- The Oct. 23 EOD view includes all five entries: **$50,000 deployed**, marked at **$3.55**, with **$+5,289.53** open PnL. This is the LCID mark used in the current four-model daily replay.
- The four model variants have the same LCID contribution because the pilot contains LONG entries only; this adds exposure and PnL but does not alter the variants' relative LCID path.
- Daily marks `$3.27`, `$3.21`, `$3.46`, and `$3.55` map in order to Oct. 20, 21, 22, and 23, as supplied. They are kept separately from the five entry fills in `trades/LCID.txt`.
- Entry fills use the user's provided prices; PnL is `notional × (daily mark / entry price − 1)`. No commissions or other costs are included.

Daily export: [`lcid_small_caps_pilot_daily_pnl.csv`](data/lcid_small_caps_pilot_daily_pnl.csv).

Ledger: [`trades/LCID.txt`](trades/LCID.txt).

Main comparison: [`Model Performance Comparison.md`](Model%20Performance%20Comparison.md).
