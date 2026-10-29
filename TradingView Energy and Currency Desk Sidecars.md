# TradingView Energy and Currency Desk Sidecars

> **TradingView sidecar schedules through 2026-10-26.** Historical prices use the user-provided Part A/Part B TradingView lists; the Oct. 26 direct-price update and DXY close are user-supplied. 1U = $10,000 notional; displayed standard daily allocations are 0.05U ($500), 1U ($10,000), and 10U ($100,000). The 1U/DAY/DXY schedule is integrated into every core variant. THE ONE MODEL adds 10U/DAY DXY to all 32 portfolios (11U/DAY combined), and uses a derived 11U/DAY energy tranche per active BRENT and OIL ticker in its 16 energy-inclusive portfolios. 0.05U DXY remains an alternative. These are hypothetical dollar-notional/index-return exposures, not an actual DXY security trade, broker fills, or account returns.

## Energy desk: separate Brent and WTI daily-buy schedules

Each size option adds a fixed-notional long lot at that session's EOD mark beginning with the first logged chart position for the instrument. The purchase-day mark-to-market is zero. Energy-sidecar PnL below includes only the new daily-buy lots; the pre-existing chart position PnL is displayed separately for context and is not counted again in model composites.

For THE ONE MODEL only, the 11U/DAY schedule per active ticker is derived from the audited 10U TradingView energy rows so each active energy tranche matches the model's combined 11U/DAY DXY exposure. The 10U schedule remains the size used in the separate strategy-comparison composites. Derived THE ONE MODEL schedule: [`the_one_model_energy_11u_sidecar_daily_v1.csv`](data/the_one_model_energy_11u_sidecar_daily_v1.csv).

| Daily size | Ticker | Daily notional | Sessions | Cumulative notional added | Daily-buy terminal PnL | Chart-position PnL (separate) |
|---|---|---:|---:|---:|---:|---:|
| 0.05U | BRENT | $500.00 | 24 | $12,000.00 | $+915.86 | $+20,799.95 |
| 0.05U | OIL | $500.00 | 33 | $16,500.00 | $+1,015.59 | $+16,112.31 |
| 1U | BRENT | $10,000.00 | 24 | $240,000.00 | $+18,317.11 | $+20,799.95 |
| 1U | OIL | $10,000.00 | 33 | $330,000.00 | $+20,311.90 | $+16,112.31 |
| 10U | BRENT | $100,000.00 | 24 | $2,400,000.00 | $+183,171.11 | $+20,799.95 |
| 10U | OIL | $100,000.00 | 33 | $3,300,000.00 | $+203,118.97 | $+16,112.31 |

## One-time Weekend Oil position overlay

The user-specified 50U LONG BRENT and 50U LONG USOIL Manual-Automatic lots opened at the supplied TradingView marks on 2026-10-19, with 10U target trims at $117 and $102 respectively, are integrated in all four core variants and therefore flow into core-based strategy composites and THE ONE MODEL. Their first recorded EOD marks at/above target are on 2026-10-23; intraday touch and execution are unverified. Separate user-directed hypothetical 10U SHORT lots at those same target levels are recorded as a force-multiplier sentiment overlay. Their explicit modeled exits are $114.627 BRENT and $100.74 OIL on 2026-10-25 at 20:35 MST, after the four earlier Oct. 25 LONG replenishments and simultaneous with distinct 35U BRENT and 34U OIL LONG Weekend Oil buys. The buys count toward weekly buy supply; the 10U short closures do not. After the modeled exits, the all-core oil long exposure reaches 100U BRENT + 100U OIL = 200U combined ($2,000,000 fixed-unit notional). Those lot-specific exits override SAR auto-close only for these shorts and all prices/timing remain hypothetical, not verified executions. [`Weekend Oil 50U Position Hypothetical.md`](Weekend%20Oil%2050U%20Position%20Hypothetical.md) attributes only the tagged long lots, not these separate shorts or the daily-buy schedule. Four separate manual LONG 10U replenishment entries are logged after the preserved Oct. 23 baseline and before the current Oct. 26 EOD mark, all on Oct. 25: BRENT at $115.792 and OIL at $101.74 use the user-recalled 17:20–17:25 MST window, modeled at a 17:22 midpoint, while BRENT at $114.80 and OIL at $101.00 use an approximate 20:00 MST timestamp per the user's recollection. Both times are modeling assumptions, not verified transaction times; the supplied prices remain the modeled replenishment prices. All current BRENT/OIL long lots are marked at the user-supplied Oct. 26 EOD closes ($115.38/$101.30), without claiming verified brokerage positions or execution. The four replenishments, 35U BRENT and 34U OIL approved orders, and explicit Oct. 25 20:35 MST SHORT exits were entered after the preserved Oct. 23 baseline; they are included in the current Oct. 26 replay at supplied marks. The additional buys are distinct LONG lots; their simultaneous short closures do not count toward weekly buy supply. Together with existing post-close all-core exposure of 65U BRENT + 66U OIL, the buys bring the all-core long total to 100U per ticker, 200U combined. The user-specified short-exit prices override SAR only for these two tagged shorts.

## ATS / manual live-position reconciliation

A separate user-directed reconciliation uses the tagged 50U-per-ticker Weekend Oil positions as the sizing proxy: up to 40U per ticker in the **AUTOMATED TRADING SYSTEM LIVE POSITIONS** ceiling and a distinct 10U **MANUAL LIVE TEST POSITIONS** remainder. ATS exits/shorts at $118 BRENT / $103.50 OIL are shown at 10U, 20U, 30U, and 40U sensitivities because the user reports the activity but does not know the exact executed quantity. This is separate from the legacy Oct. 23 replay above; the earlier 10U trims/shorts are superseded only in the new reconciliation and must not be stacked. The four Oct. 25 10U replenishments remain MANUAL LIVE TEST POSITIONS; the 35U/34U orders are MANUALLY APPROVED SHORT CLOSURE, allocated to open ATS shorts first, with only any excess remaining long and counted as new buy supply. The existing 50U-per-ticker ATS LONG entries at fixed $115 BRENT / $101 OIL are logged on Oct. 26. The later separate 50U ATS USOIL mirror LONG @ $101.11 at 07:51 MST is synchronized with the 50U manual BRENT entry and distinct from the earlier OIL @ $101.00 lot. Later user-reported adds are 10U each via a manually approved ATS order ($115.025 BRENT / $100.96 OIL), 16U BRENT @ $114.90 and 17U OIL @ $100.85 (classification/time unspecified), and a separate 50U manual BRENT LONG @ $115.51 at 07:51:14 MST from a TradingView screenshot. Dates for the user-reported additions are inferred from the conversation context where not explicitly supplied; LONG on the screenshot-supported lot is inferred from the handwritten “PICK UP OPPORTUNITY” annotation. Actual fills are unverified. In the 40U-per-ticker ceiling scenario, the tagged campaign totals 161U BRENT / 161U OIL. See [`ATS and Manual Live Position Reconciliation.md`](ATS%20and%20Manual%20Live%20Position%20Reconciliation.md) and [`ats_manual_live_positions_v1.csv`](data/ats_manual_live_positions_v1.csv). The user now reports that verified account funds and all positions in the locked $200 LONG were automatically liquidated via ATS at the best available prices, with zero oil units remaining, and that the organization dissolved at a profit due to continued harassment of the organizer. The user accepts approximately $2.4B as the conservative endpoint of the model-based estimate. Sale bands are in [`ats_oil_liquidation_reported_v1.csv`](data/ats_oil_liquidation_reported_v1.csv); exact quantities by band, individual fills, timing, and mapping to this sidecar or other books remain unspecified, so the profit claim is not independently reconciled. The sensitivity rows above are pre-liquidation references, not current exposure.

## DXY currency desk: daily long-investment alternatives

The DXY log has one LONG badge on Sep. 4 at 99.087 (the original post's caption says the dollar weakens, which conflicts with its LONG badge). The logged badge is treated as the activation signal; daily 1U lots follow the latest charted LONG/REBUY/SHORT direction. The 1U/DAY schedule shown here is the same sleeve integrated into each core variant, not an additional allocation to stack on top. Because DXY is an index rather than a directly investable security, this is a hypothetical notional/index-return proxy; no futures/ETF contract, multiplier, collateral, or tracking error is modeled. The logged one-time 1U chart-position result is shown separately and is not part of the daily sleeve.

| Daily size | Daily notional | Sessions | Cumulative notional added | Daily-investment terminal PnL | Logged 1U chart-position PnL (separate) |
|---|---:|---:|---:|---:|---:|
| 0.05U | $500.00 | 36 | $18,000.00 | $+170.69 | $+295.70 |
| 1U | $10,000.00 | 36 | $360,000.00 | $+3,413.80 | $+295.70 |
| 10U | $100,000.00 | 36 | $3,600,000.00 | $+34,137.97 | $+295.70 |

## One-time 40% DXY withdrawal sizing reference

This scenario values the user-requested one-time 40% withdrawal from the selected combined DXY allocation: the integrated 1U/DAY core sleeve plus THE ONE MODEL's 10U/DAY add-on. The request predates the Oct. 26 mark, so its 35 active sessions (385U; 154U planned for withdrawal, $1,540,000 initial-notional basis) are valued at the supplied 2026-10-26 DXY close of 102.017; Oct. 26 daily additions are excluded from the withdrawal base. The modeled withdrawal value is $1,555,020.71, leaving 231.0000U / $2,310,000.00 basis before later daily additions. This is a valuation scenario only; no withdrawal, cash transfer, or brokerage execution is reported as completed. Future daily sizing stays at 11U/DAY. The one-time chart-position 1U and unselected 0.05U alternative are excluded. The baseline historical results through Oct. 23 remain unchanged; THE ONE's 32 portfolios are alternative modeled books, not one account position.

| Component | Units before | Notional basis before | Marked value at 2026-10-26 | Units planned to withdraw | Notional basis planned for withdrawal | Estimated value at 2026-10-26 mark | 40% PnL share at 2026-10-26 mark | Units remaining | Remaining marked value | Remaining PnL |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Integrated core sleeve | 35U | $350,000.00 | $353,413.80 | 14U | $140,000.00 | $141,365.52 | $+1,365.52 | 21U | $212,048.28 | $+2,048.28 |
| THE ONE add-on | 350U | $3,500,000.00 | $3,534,137.97 | 140U | $1,400,000.00 | $1,413,655.19 | $+13,655.19 | 210U | $2,120,482.78 | $+20,482.78 |
| Combined DXY allocation | 385U | $3,850,000.00 | $3,887,551.77 | 154U | $1,540,000.00 | $1,555,020.71 | $+15,020.71 | 231U | $2,332,531.06 | $+22,531.06 |

Reference export: [`dxy_withdrawal_scenario_v1.csv`](data/dxy_withdrawal_scenario_v1.csv). The 2026-10-26 amount is a modeled valuation—not a verified fill, withdrawal, or cash balance.

## DXY → cash → oil bridge (modeled valuation; not reported executed)

The supplied 2026-10-26 DXY close now allows the requested 40% withdrawal scenario to be valued. It uses only the pre-request 385U combined allocation (154U withdrawal; the Oct. 26 daily addition is excluded), then models routing proceeds through cash to fund up to $690,000 of the logged 35U BRENT and 34U OIL buys. Excess is a separate cash-support scenario for existing positions; any shortfall is disclosed without assuming new funding. No actual withdrawal, transfer, or brokerage execution was reported. Future DXY daily additions remain at 11U/DAY.

| Bridge item | Modeled treatment at 2026-10-26 | Scenario value |
|---|---:|---:|
| DXY withdrawal value | 40% of pre-request 385U; 154U | $1,555,020.71 |
| Oil purchases funded from withdrawal cash | Up to $690,000.00 | $690,000.00 |
| Excess cash support for existing positions | Cash only; no new units | $865,020.71 |
| Oil-buy funding shortfall | No extra funding assumed | $0.00 |
| New portfolio size from this internal transfer | $0.00 | $0.00 |

Bridge ledger: [`dxy_cash_oil_bridge_v1.csv`](data/dxy_cash_oil_bridge_v1.csv). The reference column is not an actual withdrawal or cash balance.

![Three DXY daily-investment sizing options](Charts/performance/23-dxy-daily-sizing-alternatives.png)

*Three-panel view of the 0.05U, 1U, and 10U DXY daily-lot PnL paths. Each panel uses its own dollar scale; the size labels show daily and cumulative notional. The 1U/DAY schedule is included in every core model. THE ONE MODEL adds the 10U/DAY schedule on top, for 11U/DAY total; 0.05U remains an alternative.*

The 0.05U, 1U, and 10U rows show sizing scenarios. The 1U/DAY/DXY PnL and notional are already included in each core model; do not add the 1U schedule a second time. THE ONE MODEL selects the 10U/DAY schedule as a separate add-on in each of its 32 portfolios, making 11U/DAY combined DXY exposure; 0.05U remains an unselected alternative. Other strategy-comparison composites retain their existing scope. Do not treat the one-time chart-position context as included in the daily-investment results.

The crypto positions have been removed from the core comparison pending source calibration. See [`Crypto Sidecar — Pending TradingView Recalibration.md`](Crypto%20Sidecar%20%E2%80%94%20Pending%20TradingView%20Recalibration.md); no BTC/ETH marks or PnL are used here.

Machine-readable daily schedules: [`tradingview_energy_sidecar_daily_20261026.csv`](data/tradingview_energy_sidecar_daily_20261026.csv), [`dxy_currency_desk_sidecar_daily_20261026.csv`](data/dxy_currency_desk_sidecar_daily_20261026.csv). Price source/mark flags: [`tradingview_benchmark_session_marks_20261026.csv`](data/tradingview_benchmark_session_marks_20261026.csv).
