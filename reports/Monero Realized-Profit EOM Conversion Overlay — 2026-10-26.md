# Monero Realized-Profit EOM Conversion Overlay — 2026-10-26

## Rule requested

This model records the user-stated assumption that **1% of aggregate net realized profit across the included books** is reserved for a USD-to-Monero conversion at the end of each month. This is a modeled allocation rule, not an independently confirmed payment, payer, brokerage cash flow, or Monero receipt.

1. Sum **realized PnL only** across all included, separately identified books for each calendar month. Realized losses in one included book offset realized gains in other included books for that same month, as directed. Positions and capital are not netted; only the monthly payout base is aggregated.
2. If monthly aggregate realized PnL is positive, set the eligible base to that positive net amount and reserve **1%**. If monthly net realized PnL is zero or negative, reserve **$0**. No unrealized PnL or mark-to-market gain enters the base.
3. At EOM, convert the pending USD reserve (including any reserve carried from an earlier missing-mark month) using the **supplied TradingView Kraken XMR/USD EOD close** dated on that month's final calendar day. The model also requires the realized-PnL source window to extend to within 3 calendar days of that mark; stale partial-month history cannot trigger conversion. It reports XMR quantity equivalent, not a purchase or receipt.
4. If that EOM mark is missing, leave the reserve in USD and carry it forward. No screenshot price, outside price, interpolation, or legacy mark is substituted. The model currently assumes no cross-month loss carryforward; each month is netted independently.
5. Record the 1% reserve separately from gross additions and funded capital. Only the residual realized net profit after reserve remains available for modeled reinvestment, subject to the existing explicit cash-flow rules.

The source strategy/model PnL series remain **gross of this overlay**. The conversion reserve is a separate monthly cash-flow deduction from available realized profit; it does not alter position PnL, additions, open notional, or unrealized marks. The machine-readable monthly file exposes both gross monthly realized PnL and the after-reserve amount.

## Included book scope

The first implementation follows the independent books explicitly listed in the current $20B pool bridge:

- Each of the **32 TOM member books**, with its own core and variant-specific 1U/EOD realized trade events. Their monthly totals are added once as the 32-book portfolio set; the TOM aggregate is not added a second time.
- The separately funded, equal-gross scaled WINNING MODEL as one additional book (the selected winner is ex post from the same period; this is still subject to same-period selection bias). The supplemental oil scenario reclassifies the existing 50U BRENT / 50U OIL source lots to this Winner allocation; because no realized close for those lots appears in this window, the transfer adds no historical realized PnL, and their unrealized mark change is excluded.
- The separate fixed-$500/EOD and shared-direction 1U/EOD force alternatives.
- Generic energy, 0.05U/DAY DXY, and one-time chart-opened DXY books. They contribute zero realized PnL in this supplied window because no realized close is present for those positions; their unrealized mark PnL is excluded.

The individual core series and variant-force paths are source components within TOM books, not extra funded books in this pool scope. TWM_1M sizing views, randomly composed demo mixes, and other comparison-only charts are not added as separate simultaneous books unless their separate funding is explicitly specified. This prevents alternative sizing views of the same model history from being counted as extra profits by default. The locked BRENT/OIL foundation contributes no realized profit until a qualifying close is explicitly modeled; its current mark does not count.

## Current historical illustration

The underlying model window is **2026-09-03–2026-10-26**. September starts on Sep. 3, so its record is a partial-month history; October is month-to-date through Oct. 26. Modeled EOM conversion equivalent(s): 2026-09: $41,183.97 at $544.86/XMR = 75.58633410 XMR-equivalent (not a verified crypto purchase). No qualifying EOM close is supplied for 2026-10; reserve remains in USD. The current pending USD reserve is **$61,831.32**. These are modeled amounts, not a cash withdrawal or proof of received income. The 2026-09-30 close of **$544.86** was supplied by the user in chat as the TradingView Kraken XMR/USD EOD mark; no chart capture/export was attached for independent validation.

| Month | Model coverage | Aggregate net realized PnL | 1% reserve generated | Net realized PnL after reserve | Supplied EOM mark date | XMR/USD EOM close | XMR equivalent | Pending USD reserve |
|---|---|---:|---:|---:|---|---:|---:|---:|
| 2026-09 | partial history from 2026-09-03 | $4,118,396.62 | $41,183.97 | $4,077,212.65 | 2026-09-30 | 544.86000000 | 75.58633410 | $0.00 |
| 2026-10 | month-to-date through 2026-10-26 (no EOM source mark) | $6,183,132.26 | $61,831.32 | $6,121,300.94 | missing | pending | — | $61,831.32 |

September's reserve is based only on the Sep. 3–30 available source window. October's figure is provisional month-to-date; it is not a completed October EOM payout. The month-end reserve is not converted using the supplied screenshots because they show intraday 15-minute chart contexts around Sep. 20–22, not EOM closes.

## Screenshot/source archive

The three user-supplied TradingView posts are preserved in [`Archive/Monero_EOM_conversion/`](../Archive/Monero_EOM_conversion/README.md). They identify Monero / U.S. Dollar on **Kraken, 15-minute** charts, with displayed intraday quotes around $542.83–$569.45. They are context only and are **not** used as month-end valuation marks.

## Machine-readable files and rebuild

- [`data/monero_realized_pnl_by_book_monthly_v1.csv`](../data/monero_realized_pnl_by_book_monthly_v1.csv) — monthly realized PnL by independently counted book.
- [`data/monero_eom_conversion_monthly_v1.csv`](../data/monero_eom_conversion_monthly_v1.csv) — aggregate net, 1% reserve, EOM mark, modeled XMR equivalent, and pending USD balance.
- [`data/monero_tradingview_kraken_eom_marks_v1.csv`](../data/monero_tradingview_kraken_eom_marks_v1.csv) — input records user-supplied TradingView Kraken XMR/USD month-end EOD marks; September's close was entered from the user's chat statement.
- Builder: [`scripts/build_monero_eom_conversion_overlay.py`](../scripts/build_monero_eom_conversion_overlay.py). Rebuild with `python scripts/build_monero_eom_conversion_overlay.py`.

> The source models are hypothetical paper replays, not verified brokerage books. The 1% reserve and XMR equivalent are consequently modeled amounts—not confirmed income, tax treatment, external payment, or crypto transaction.
