# DXY-Equivalent Portfolio Snapshot — Oct. 22, 2026

A terminal portfolio view at the agreed Oct. 22 historical close. It adds the user-provided DXY, EUR/USD, and JPY/USD marks and the daily-marked US30Y SHORT to the four core model variants, then recalculates the US10Y spread carry over the expanded deployed-notional base.

> **DXY units:** PnL equivalents use the user-selected ICE DX futures-equivalent scale of **$1,000 per DXY index point**. This is a reporting conversion only; the logged DXY position is TVC:DXY, not an actual ICE futures contract. Standard portfolio units remain **$10,000 notional each**.

## Oct. 22 Portfolio Totals

| Variant | Deployed units | Open units incl. US10Y refs | Deployed notional | Base realized | Total unrealized | US10Y carry | **Adjusted total USD** | **Adjusted DXY-point equivalent** | **Adjusted ROI** |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **Variant 1 — 1u Open** | 83u | 68u | $830,000.00 | $25,561.44 | $19,522.21 | $176.77 | **$45,260.41** | **+45.260** | **5.453%** |
| **Variant 2 — 1u SAR** | 83u | 63u | $830,000.00 | $31,385.57 | $10,859.38 | $176.77 | **$42,421.72** | **+42.422** | **5.111%** |
| **Variant 3A — Nu Open** | 92u | 77u | $920,000.00 | $25,561.44 | $40,747.24 | $199.76 | **$66,508.44** | **+66.508** | **7.229%** |
| **Variant 3B — Nu SAR** | 92u | 63u | $920,000.00 | $42,552.27 | $10,859.38 | $199.76 | **$53,611.42** | **+53.611** | **5.827%** |

## Added Terminal Marks and Unrealized PnL

| Position | Side | Entry | Oct. 22 mark | Units | Unrealized USD | DXY-point equivalent |
|---|---|---:|---:|---:|---:|---:|
| DXY | LONG | 99.087000 DXY index points | 101.616000 DXY index points | 1 | $+255.23 | +0.255 |
| EURUSD | LONG | 1.153880 USD per EUR | 1.121690 USD per EUR | 1 | $-278.97 | -0.279 |
| JPYUSD | LONG | 0.010160 USD per JPY | 0.006376 USD per JPY | 1 | $-3,724.41 | -3.724 |
| US30Y | SHORT | 5.350000 yield percent | 5.290000 yield percent | 1 | $+112.15 | +0.112 |

EUR/USD and JPY/USD PnL is calculated in USD using each pair's quoted USD-per-base-currency close and the standard $10,000 entry notional. DXY and the US30Y yield are valued by proportional quote return on the same $10,000 notional; the US30Y result is a quote-return proxy, not a bond-duration or futures-contract valuation.

US30Y Oct. 22 close: `5.290%` (source date `2026-10-22`; carried-forward flag `False`). The missing Oct. 12 Treasury observation is transparently carried from Oct. 9 (`5.600%`) for that session, consistent with the confirmed US10Y holiday treatment.

## All Open Unrealized PnL by Symbol

The full position-level ledger (including every open core lot and the added DXY/FX/US30Y marks) is in [`data/dxy_portfolio_open_positions_oct22.csv`](data/dxy_portfolio_open_positions_oct22.csv). US10Y entries are included as two $10,000 carry-reference units but deliberately have no standalone yield-quote PnL; their role is represented by the US10Y portfolio carry.

### Variant 1 — 1u Open

| Symbol | Open units | Unrealized USD | DXY-point equivalent |
|---|---:|---:|---:|
| AAPL | 4 | $+2,096.46 | +2.096 |
| AMZN | 1 | $-317.12 | -0.317 |
| BRENT | 5 | $+3,068.78 | +3.069 |
| BTC | 2 | $+2,920.54 | +2.921 |
| CAT | 2 | $+1,507.94 | +1.508 |
| CVX | 3 | $+2,470.96 | +2.471 |
| DIS | 1 | $-853.88 | -0.854 |
| DXY | 1 | $+255.23 | +0.255 |
| ETH | 1 | $-190.39 | -0.190 |
| EURUSD | 1 | $-278.97 | -0.279 |
| GEV | 1 | $-1,779.81 | -1.780 |
| HD | 1 | $+668.64 | +0.669 |
| INTC | 5 | $+188.67 | +0.189 |
| JPYUSD | 1 | $-3,724.41 | -3.724 |
| LLY | 1 | $+1,080.50 | +1.080 |
| LMT | 4 | $+5,880.21 | +5.880 |
| LULU | 1 | $+844.10 | +0.844 |
| META | 3 | $-401.02 | -0.401 |
| NET | 1 | $-871.34 | -0.871 |
| NFLX | 1 | $-1.49 | -0.001 |
| NVDA | 1 | $-757.00 | -0.757 |
| OIL | 6 | $+4,051.72 | +4.052 |
| ORCL | 1 | $-209.78 | -0.210 |
| PEP | 1 | $+817.36 | +0.817 |
| PLTR | 3 | $-99.94 | -0.100 |
| RIVN | 1 | $-1,566.43 | -1.566 |
| SPCX | 3 | $+2,929.12 | +2.929 |
| TMO | 1 | $+204.38 | +0.204 |
| TSLA | 1 | $-177.15 | -0.177 |
| UPS | 2 | $-1,519.99 | -1.520 |
| US30Y | 1 | $+112.15 | +0.112 |
| V | 1 | $+749.51 | +0.750 |
| VLO | 1 | $+51.40 | +0.051 |
| WMT | 1 | $+1,617.11 | +1.617 |
| XLE | 1 | $+756.13 | +0.756 |
| XRH0 | 1 | $+0.00 | +0.000 |

### Variant 2 — 1u SAR

| Symbol | Open units | Unrealized USD | DXY-point equivalent |
|---|---:|---:|---:|
| AAPL | 4 | $+2,096.46 | +2.096 |
| AMZN | 1 | $-317.12 | -0.317 |
| BRENT | 5 | $+3,068.78 | +3.069 |
| BTC | 2 | $+2,920.54 | +2.921 |
| CAT | 1 | $-349.93 | -0.350 |
| CVX | 3 | $+2,470.96 | +2.471 |
| DIS | 1 | $-853.88 | -0.854 |
| DXY | 1 | $+255.23 | +0.255 |
| ETH | 1 | $-190.39 | -0.190 |
| EURUSD | 1 | $-278.97 | -0.279 |
| GEV | 1 | $-1,779.81 | -1.780 |
| HD | 1 | $+668.64 | +0.669 |
| INTC | 3 | $-5,658.85 | -5.659 |
| JPYUSD | 1 | $-3,724.41 | -3.724 |
| LLY | 1 | $+1,080.50 | +1.080 |
| LMT | 4 | $+5,880.21 | +5.880 |
| LULU | 1 | $+844.10 | +0.844 |
| META | 2 | $-1,968.48 | -1.968 |
| NET | 1 | $-871.34 | -0.871 |
| NFLX | 1 | $-1.49 | -0.001 |
| NVDA | 1 | $-757.00 | -0.757 |
| OIL | 6 | $+4,051.72 | +4.052 |
| ORCL | 1 | $-209.78 | -0.210 |
| PEP | 1 | $+817.36 | +0.817 |
| PLTR | 2 | $+510.09 | +0.510 |
| RIVN | 1 | $-1,566.43 | -1.566 |
| SPCX | 3 | $+2,929.12 | +2.929 |
| TMO | 1 | $+204.38 | +0.204 |
| TSLA | 1 | $-177.15 | -0.177 |
| UPS | 2 | $-1,519.99 | -1.520 |
| US30Y | 1 | $+112.15 | +0.112 |
| V | 1 | $+749.51 | +0.750 |
| VLO | 1 | $+51.40 | +0.051 |
| WMT | 1 | $+1,617.11 | +1.617 |
| XLE | 1 | $+756.13 | +0.756 |
| XRH0 | 1 | $+0.00 | +0.000 |

### Variant 3A — Nu Open

| Symbol | Open units | Unrealized USD | DXY-point equivalent |
|---|---:|---:|---:|
| AAPL | 4 | $+2,096.46 | +2.096 |
| AMZN | 1 | $-317.12 | -0.317 |
| BRENT | 5 | $+3,068.78 | +3.069 |
| BTC | 2 | $+2,920.54 | +2.921 |
| CAT | 3 | $+3,365.81 | +3.366 |
| CVX | 3 | $+2,470.96 | +2.471 |
| DIS | 1 | $-853.88 | -0.854 |
| DXY | 1 | $+255.23 | +0.255 |
| ETH | 1 | $-190.39 | -0.190 |
| EURUSD | 1 | $-278.97 | -0.279 |
| GEV | 1 | $-1,779.81 | -1.780 |
| HD | 1 | $+668.64 | +0.669 |
| INTC | 9 | $+13,285.99 | +13.286 |
| JPYUSD | 1 | $-3,724.41 | -3.724 |
| LLY | 1 | $+1,080.50 | +1.080 |
| LMT | 4 | $+5,880.21 | +5.880 |
| LULU | 1 | $+844.10 | +0.844 |
| META | 7 | $+5,868.83 | +5.869 |
| NET | 1 | $-871.34 | -0.871 |
| NFLX | 1 | $-1.49 | -0.001 |
| NVDA | 1 | $-757.00 | -0.757 |
| OIL | 6 | $+4,051.72 | +4.052 |
| ORCL | 1 | $-209.78 | -0.210 |
| PEP | 1 | $+817.36 | +0.817 |
| PLTR | 3 | $-99.94 | -0.100 |
| RIVN | 1 | $-1,566.43 | -1.566 |
| SPCX | 3 | $+2,929.12 | +2.929 |
| TMO | 1 | $+204.38 | +0.204 |
| TSLA | 1 | $-177.15 | -0.177 |
| UPS | 2 | $-1,519.99 | -1.520 |
| US30Y | 1 | $+112.15 | +0.112 |
| V | 1 | $+749.51 | +0.750 |
| VLO | 1 | $+51.40 | +0.051 |
| WMT | 1 | $+1,617.11 | +1.617 |
| XLE | 1 | $+756.13 | +0.756 |
| XRH0 | 1 | $+0.00 | +0.000 |

### Variant 3B — Nu SAR

| Symbol | Open units | Unrealized USD | DXY-point equivalent |
|---|---:|---:|---:|
| AAPL | 4 | $+2,096.46 | +2.096 |
| AMZN | 1 | $-317.12 | -0.317 |
| BRENT | 5 | $+3,068.78 | +3.069 |
| BTC | 2 | $+2,920.54 | +2.921 |
| CAT | 1 | $-349.93 | -0.350 |
| CVX | 3 | $+2,470.96 | +2.471 |
| DIS | 1 | $-853.88 | -0.854 |
| DXY | 1 | $+255.23 | +0.255 |
| ETH | 1 | $-190.39 | -0.190 |
| EURUSD | 1 | $-278.97 | -0.279 |
| GEV | 1 | $-1,779.81 | -1.780 |
| HD | 1 | $+668.64 | +0.669 |
| INTC | 3 | $-5,658.85 | -5.659 |
| JPYUSD | 1 | $-3,724.41 | -3.724 |
| LLY | 1 | $+1,080.50 | +1.080 |
| LMT | 4 | $+5,880.21 | +5.880 |
| LULU | 1 | $+844.10 | +0.844 |
| META | 2 | $-1,968.48 | -1.968 |
| NET | 1 | $-871.34 | -0.871 |
| NFLX | 1 | $-1.49 | -0.001 |
| NVDA | 1 | $-757.00 | -0.757 |
| OIL | 6 | $+4,051.72 | +4.052 |
| ORCL | 1 | $-209.78 | -0.210 |
| PEP | 1 | $+817.36 | +0.817 |
| PLTR | 2 | $+510.09 | +0.510 |
| RIVN | 1 | $-1,566.43 | -1.566 |
| SPCX | 3 | $+2,929.12 | +2.929 |
| TMO | 1 | $+204.38 | +0.204 |
| TSLA | 1 | $-177.15 | -0.177 |
| UPS | 2 | $-1,519.99 | -1.520 |
| US30Y | 1 | $+112.15 | +0.112 |
| V | 1 | $+749.51 | +0.750 |
| VLO | 1 | $+51.40 | +0.051 |
| WMT | 1 | $+1,617.11 | +1.617 |
| XLE | 1 | $+756.13 | +0.756 |
| XRH0 | 1 | $+0.00 | +0.000 |

## Carry, Scope, and Date Notes

- The US10Y carry is recalculated on the core model's cumulative deployed notional plus all six additional $10,000 units deployed by Oct. 22: DXY, EUR/USD, JPY/USD, the Sep. 15 US30Y SHORT, and both US10Y carry-reference entries. Each interval uses deployed notional × ((US10Y close − 4.865%) / 100) × elapsed calendar days / 365; above-baseline yields add and below-baseline yields subtract.
- The Oct. 23 US30Y LONG at 5.311% is a separate new one-unit position and is not included in Oct. 22 totals.
- User-provided DXY/FX marks are terminal-only. No daily DXY/EURUSD/JPYUSD closes were supplied, so this file is a terminal snapshot and does not invent daily paths for those positions.
- The US10Y LONGs are carry references rather than standalone quote-return positions in this view. The 30Y PnL is shown separately using a proportional quote-return proxy on $10,000; a bond-duration valuation would require a separate instrument/duration model.
- The exported detail lists the Oct. 22 close for each open core position and the source date for the US30Y mark. All currency PnL is shown in USD first, then as DXY-point equivalents using $1,000 per point.

Machine-readable portfolio totals: [`dxy_portfolio_summary_oct22.csv`](data/dxy_portfolio_summary_oct22.csv).

Position-level unrealized ledger: [`dxy_portfolio_open_positions_oct22.csv`](data/dxy_portfolio_open_positions_oct22.csv).

Daily US30Y SHORT marks and PnL recalibration: [`us30y_short_mark_to_market_daily_2026.csv`](data/us30y_short_mark_to_market_daily_2026.csv).
