# Whole-Portfolio DXY Numeraire — Daily Comparison

The new first chart compares each variant's cumulative total PnL in dollars with the daily DXY close. Total USD PnL includes realized PnL, open unrealized PnL (including FX and US30Y marks), and the established US10Y carry adjustment. DXY is the numeraire for the whole portfolio, not a standalone $10,000 position. The second graph retains the open-unrealized-PnL and USD-versus-DXY-return views.

![DXY Close vs. Whole-Portfolio PnL in Dollars](Charts/performance/17-dxy-close-vs-whole-portfolio-pnl-usd.png)

![Whole-portfolio unrealized PnL and USD/DXY returns](Charts/performance/16-whole-portfolio-dxy-vs-usd-pnl.png)

## Oct. 22 Terminal Results

| Variant | Capital basis | Open unrealized PnL (USD) | Realized PnL (USD) | US10Y carry | Total PnL (USD) | USD return | DXY-equivalent account value (index units) | DXY-numeraire return |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **Variant 1 — 1u Open** | $830,000 | $+22,529.30 | $+25,561.44 | $+158.44 | $+48,249.17 | +5.399% | 8,558.10 DXY-eq units | +2.027% |
| **Variant 2 — 1u SAR** | $830,000 | $+13,866.47 | $+31,385.57 | $+158.44 | $+45,410.48 | +5.057% | 8,530.33 DXY-eq units | +1.696% |
| **Variant 3A — Nu Open** | $920,000 | $+43,754.34 | $+25,561.44 | $+181.43 | $+69,497.21 | +7.180% | 9,646.42 DXY-eq units | +3.751% |
| **Variant 3B — Nu SAR** | $920,000 | $+13,866.47 | $+42,552.27 | $+181.43 | $+56,600.18 | +5.778% | 9,520.25 DXY-eq units | +2.394% |

## DXY and FX Basis

- DXY daily closes run from `2026-09-03` (`98.95`) through `2026-10-22` (`102.22`). This series' Oct. 22 close of 102.22 supersedes the earlier 101.616 terminal mark, as directed.
- EUR/USD PnL uses the uploaded daily close on its entry date as its cost basis: `2026-09-15` close `1.1024`. The original chart quote `1.15388` remains in the trade log as source evidence; the graph does not use it as the PnL basis, per your instruction.
- JPY/USD PnL uses the uploaded daily close on its entry date as its cost basis: `2026-09-07` close `0.007068`. The original chart quote `0.010160` remains in the trade log as source evidence; the graph does not use it as the PnL basis, per your instruction.
- DXY-equivalent account value is computed as `USD account value ÷ daily DXY close`; returns are normalized to the Sep. 3 DXY-equivalent starting value. The USD capital bases are the $830,000 / $920,000 portfolio amounts you specified.
- The DXY LONG log entry is retained as historical reference evidence, but this comparison does not treat it as an additional $10,000 position or add separate DXY-trade PnL.

## PnL, Carry, and Position Treatment

- Daily EUR/USD and JPY/USD unrealized PnL is calculated from the entry-date daily close, then marked to each uploaded daily close at $10,000 standard notional per position.
- The Sep. 15 US30Y SHORT is marked daily with a proportional quote-return proxy on $10,000 notional. This is not a bond-duration/futures valuation. The Oct. 23 US30Y LONG at 5.311% is outside this Oct. 22 graph.
- The US10Y spread carry preserves the established 4.865% baseline, actual/365 accrual, and cumulative deployed-notional basis from the core model comparison. Supplementary FX and US30Y PnL are included in the USD account value, but are not used to retroactively change the carry denominator. DXY itself is excluded because it is the numeraire.
- US10Y positions are carry references, not independent yield-quote PnL rows. For the Oct. 12 market holiday, the user-approved US10Y 5.24% close from Oct. 9 is carried; the US30Y mark likewise carries its Oct. 9 5.60% close. The daily export records the US30Y source date explicitly.

Daily values and conversion factors: [`whole_portfolio_dxy_vs_usd_daily.csv`](data/whole_portfolio_dxy_vs_usd_daily.csv).

Terminal variant summary: [`whole_portfolio_dxy_vs_usd_summary.csv`](data/whole_portfolio_dxy_vs_usd_summary.csv).
