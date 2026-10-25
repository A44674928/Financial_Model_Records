# Model Calculation Guide

This guide explains how the repository's portfolio models turn the trade logs into daily lots, PnL, exposure, and comparison lines. It covers the four core variants, the shared-direction $500/1U models, four variant-specific 1U/EOD force models, and the TradingView energy sidecar. BTC/ETH remain outside the core pending recalibration; DXY's chart-directed 1U/DAY index-return sleeve is integrated into core PnL, with sizing alternatives detailed separately. The calculations are a historical paper-trade replay—not a live execution system, forecast, or investment recommendation.

## At a glance

| Book | What determines a new position? | How does an open position close? | Unit / sizing |
|---|---|---|---|
| Core V1 — 1U Open | Each logged `LONG`, `REBUY`, or `SHORT` entry | Explicit EXIT/TAKE PROFIT closes open longs. No automatic short cover on a later LONG/REBUY. | Logged entry units × 1U notional |
| Core V2 — 1U SAR | Same entries and logged sizes as V1 | Explicit exit closes open longs; a LONG/REBUY also closes all open shorts. | Logged entry units × 1U notional |
| Core V3A — Nu Open | Same as V1, except qualifying compounded shorts can be larger | Same close behavior as V1 | Logged units, except a qualifying compounded short uses the preceding full-exit unit count |
| Core V3B — Nu SAR | Same as V3A | Same close behavior as V2 | Same short compounding as V3A |
| Exponential alternative | Latest logged direction, carried forward; add a lot each priced EOD | Close all old lots at EOD when the carried direction flips | Fixed $500 per active symbol per EOD |
| Shared-direction force alternative | Same direction path and daily schedule as the $500 model | Close all old-direction lots on any direction flip | Fixed 1U per active symbol per EOD |
| Variant-specific force family | Same 1U/EOD schedule with V1, V2, V3A, or V3B close/short-compounding rules | Variant-specific | One 1U tranche per active symbol/EOD; V3 compounding can size the event-day short tranche up |
| DXY currency sleeve | Adds 1U per active EOD in the latest charted direction | Carries LONG/REBUY/SHORT direction; reversals close prior daily lots at EOD | 1U/DAY integrated into every core variant; alternative sizes documented separately |
| TradingView energy sidecar | Adds a fixed-notional long at each supplied energy EOD | No exits during the schedule | Standalone 0.05U, 1U, or 10U alternatives per energy ticker |

The $500 model, shared-direction 1U model, and four variant-specific 1U/EOD models are separate alternatives; do not stack those force-model families or the four variant rules together. Energy-sidecar composites add the daily-buy lots only; they do not add the energy chart positions a second time.

## 1. Common inputs and daily timeline

- The core replay reads the standardized records in `trades/*.txt`, orders events by date, time, ticker, then source-file order, and calculates the four core variants separately.
- Each event's entry or exit date is assigned to the first priced session on or after that date. This carries weekend and market-holiday events to the next priced session. Events after the October 23, 2026 cutoff are outside this replay.
- The entry/exit event price in the log is used as the lot's entry basis or close price. Open lots are marked against that ticker's configured EOD price series. The current core marks use only the normalized user-provided TradingView lists; the session-mark file records source rows and explicitly flags provisional XRH0 carry-forwards.
- The four core models directly price 31 TradingView symbols and also include a chart-directed 1U/DAY/DXY index-return sleeve. The DXY signal is the logged LONG/REBUY/SHORT direction carried forward; the current log has one LONG badge, although its caption conflicts. DXY is not modeled as a futures/ETF contract. BTC/ETH remain pending recalibration; EURUSD, JPYUSD, US10Y, and US30Y remain outside these position replays. Whole-account DXY/yield views are historical, not recalculated on this benchmark.
- A unit is a notional sizing measure, not a fixed number of shares. In these calculations, **1U corresponds to $10,000 of entry notional**. Core V1/V2 use each entry's logged unit size; V3A/V3B normally do too, subject to the compounded-short override below. Most current entries are 1U, and the ORCL entry is 2.5U. The `1U` labels describe standard sizing, not a rule that overrides a different size written in the log.

On a session, the replay processes that session's mapped events, applies any closes and new entries, then marks the remaining open lots to the session's EOD price. A same-day entry can therefore have a gain or loss at EOD if the configured close differs from its logged entry price.

## 2. Core lot and PnL calculations

A core lot sized at `q` units after applying the variant's sizing rule has entry notional `q × 1U`. With entry price `E` and the applicable mark or close price `P`:

- **Long PnL:** `q × 1U × (P / E − 1)`
- **Short PnL:** `q × 1U × (1 − P / E)`

For example, a 1-unit long entered at $100 and marked at $105 has +$500 PnL. A 1-unit short entered at $100 and marked at $105 has −$500 PnL. The calculation is proportional to the price move; it does not recalculate the entry notional as the position gains or loses.

### What the daily totals mean

- **Realized PnL** is the cumulative PnL from lots already closed, calculated at the logged close/flip price.
- **Unrealized PnL** is the current mark-to-market PnL of lots still open.
- **Total PnL** is realized plus unrealized PnL.
- **Cumulative deployed notional** is the sum of the original entry notionals of all lots opened to date. It does not fall when a lot closes; it is not the same as current open exposure or a cash balance.
- The core report's **ROI** is total PnL divided by cumulative deployed notional. It is a model comparison denominator, not a return on a fixed, fully specified account with margin, cash flows, or financing.

The replay does not deduct commissions, spread, borrow costs, financing, taxes, or slippage beyond the prices represented in its inputs.

## 3. The four core variants

All four use the same logs, unit notional, price marks, explicit exit events, and PnL formulas. They differ in whether a LONG/REBUY closes an existing short, and whether a qualifying short after a multi-unit full exit is sized up.

### V1 — 1U Open

- Opens a lot for each logged LONG, REBUY, or SHORT entry using that entry's logged unit count.
- An explicit EXIT or TAKE PROFIT event closes all currently open **long** lots for that ticker.
- Does not automatically close short lots when a later LONG/REBUY appears. A long and short for the same ticker can therefore be open at the same time.
- The name “Open” means no LONG-triggered short-cover rule; explicit exit records still close long lots.

### V2 — 1U SAR

- Uses the same logged entry sizes and explicit long exits as V1.
- In addition, a LONG or REBUY entry closes all currently open **short** lots for that ticker at the new entry's logged price, then opens the new long.
- **Implementation detail:** the short-cover trigger is LONG/REBUY. A new SHORT entry does not automatically close existing longs. So “SAR” here is not a symmetric close-whichever-side-is-opposite rule.

### V3A — Nu Open

- Uses the V1 open/exit behavior.
- For a SHORT entry explicitly noted as a **“Compounded short”**, if the preceding exit for that ticker recorded more than one unit, the new short uses that preceding exit's unit count rather than the short log line's usual 1-unit size.
- Does not automatically close shorts on a later LONG/REBUY.
- This rule compounds qualifying shorts only; it does not scale up ordinary long entries or every subsequent trade.

### V3B — Nu SAR

- Combines V3A's qualifying compounded-short size with V2's LONG/REBUY-triggered closing of open shorts.
- Like V2, a new SHORT does not automatically close existing longs.

### Core example: CAT

The CAT log records 1-unit longs at $787.86 and $785.41, followed by a 2-unit TAKE PROFIT exit at $864.70 and a 1-unit “Compounded short” entry at that same price. The explicit exit closes both long lots in every core variant. V1/V2 open a 1-unit short; V3A/V3B size that compounded short at 2 units, matching the preceding 2-unit full exit.

A later CAT LONG is logged at $729.58. At that event, V1/V3A leave their short open and add a long; V2/V3B close their short at $729.58 and then add a long. The short-close PnL at that price is about +$1,562.62 for V2's 1-unit short and +$3,125.25 for V3B's 2-unit short. Those dollar results illustrate the rule before the new long's separate EOD mark-to-market is considered.

## 4. Direction-following EOD alternatives

These are separate accumulation models, not replays of every core lot entry. They use the latest direction-bearing LONG, SHORT, or REBUY entry for each ticker as a state signal; REBUY is treated as LONG. Trade-log EXIT and TAKE PROFIT rows do not clear that state. The repository has no separate authorization-state feed.

For each priced EOD:

1. Find the last direction-bearing event for each ticker mapped to that session. If there are multiple direction events for one ticker on the same day, the last one in event order determines that day's carried direction.
2. If that direction differs from the previously carried direction, close **all** open model lots for that ticker at the session's EOD mark. Record their PnL as realized.
3. Add one fresh fixed-notional lot in the current direction for every ticker that has a direction state, including on its first signal session.
4. Mark all remaining open lots to the session close. The direction state carries through later sessions until a new LONG/SHORT/REBUY entry changes it.

A weekend or holiday signal begins on the first priced EOD session on or after its logged date. Unlike the core lot models, this daily-addition model ignores the trade log's position-size field: the tranche is fixed by the chosen alternative.

- **Exponential ($500/EOD):** one new $500-notional tranche per active ticker per priced EOD. The tranche size is fixed; PnL is not compounded into later tranche size.
- **Force multiplier (1U/EOD):** identical signals, timing, and flip logic, but one 1U tranche per active ticker per priced EOD. Its unrounded PnL and notional are 20× the $500 model's; displayed cents can differ slightly when totals are rounded separately.

For either shared-direction model, an active ticker can accumulate several same-direction lots. On a flip, all old-direction lots close at that EOD mark before the first new-direction tranche is added. A close is not triggered merely because the source trade log contains an EXIT or TAKE PROFIT row.

## 5. Variant-specific 1U/EOD force models

These are four additional alternatives that retain the one-per-active-symbol-per-EOD schedule but apply the core variants' position handling. They are distinct from the shared-direction force model above; neither family is stacked with the other.

On every priced EOD with a carried direction, the variant model adds one 1U lot. Trade-log entry sizes are ignored except for the V3A/V3B compounded-short rule below. Explicit EXIT/TAKE PROFIT events close all open long lots at the event's logged price, but do not erase the carried direction; if a direction remains active after processing the day's events, its scheduled EOD lot is still added. A new lot is opened at the EOD mark and marked from that close.

- **V1/V3A Open behavior:** a new opposite-direction signal does not close the previously accumulated lots. Longs and shorts for a ticker may coexist until an explicit long exit closes the longs.
- **V2/V3B SAR behavior:** LONG/REBUY closes all accumulated short lots at that event's logged price before the day's EOD long lot is added. SHORT does not close open long lots, matching the asymmetry in the core implementation.
- **V3A/V3B natural-unit behavior:** if a SHORT event is tagged “Compounded short” and the preceding full exit recorded more than 1 unit, that event-day tranche uses the preceding exit's unit count (for example, 2U or 5U). Subsequent carried SHORT days return to 1U additions. This is a one-day sizing override to the baseline daily 1U schedule, not a compounded or reinvested PnL amount.
- If several directional events for a ticker occur on one session, process them in log order; the final direction determines that session's EOD addition. Weekend/holiday events apply on the first priced session on or after the event date.

The comparison includes each variant-specific model alone and with the incremental 10U TradingView energy daily-buy sidecar, plus all 16 additive pairings of a core variant with any of the four variant-specific 1U models and the energy sidecar. Matching and cross-variant pairings are shown separately. These are illustrative additive PnL/gross-notional comparisons, not account simulations; positions and capital are not netted or merged.

## 6. TradingView energy sidecar and integrated DXY sleeve

The energy sidecar is a separate long-only accumulation schedule for BRENT and OIL. DXY is a hypothetical currency-desk index-return proxy whose 1U/DAY schedule is integrated into every core model:

- Energy alternatives are 0.05U ($500), 1U ($10,000), and 10U ($100,000) per ticker/session; each schedule is standalone and is not stacked with the other sizes.
- Each new energy lot starts at that session's EOD mark, has zero purchase-day PnL, and remains open through October 23. The 10U energy schedule is the only energy size added by strategy composites.
- For DXY, one 1U ($10,000 notional) long/short index-return lot is added at each EOD while a charted direction is active. The current log has one LONG badge on Sep. 4; the badge controls despite the conflicting caption. A later direction reversal closes older daily lots at that session's EOD mark, then additions follow the new direction. There are no such reversals in the current log.
- The integrated 1U/DAY/DXY schedule contributes **35 daily lots** and is included in each core variant's PnL, deployed notional, and open exposure. The sidecar report also shows 0.05U and 10U alternatives; do not add its 1U row again to core results. DXY is an index-return/notional proxy—not a modeled futures or ETF contract.
- The daily DXY lots are distinct from the one-time chart-opened DXY position; the logged chart-position PnL is displayed separately and is not counted in core totals. Fees, financing, contract multipliers, collateral, and tracking error are not modeled.

The energy sidecar report shows daily-buy PnL separately from chart-opened energy positions. When combined with a core variant, only the **incremental 10U daily-buy energy lots** are added: chart-opened energy lots already belong to the core replay and must not be counted twice.

## 7. How composite lines are formed

A composite line is additive PnL, session by session:

`composite PnL = core-variant PnL + selected independent add-on PnL(s)`

A composite adds the core PnL to a selected 1U/$500 force-model alternative and/or the 10U TradingView energy daily-buy sidecar, as labeled in the comparison. The four variant-specific 1U/EOD models are alternatives to one another and to the shared-direction 1U model; they are never stacked together. The comparison shows all 16 core-variant × 1U-variant pairings, both with and without the energy sidecar, including matching and cross-variant combinations. The percentage-gain graph defines gain as cumulative composite PnL divided by cumulative gross notional added. This deployed-notional ratio is not an account return or capital-normalized ROI; raw dollar PnL, gross cumulative notional, and gross open notional remain separately reported. They are not included in the separate whole-portfolio DXY/yield multiplier scenarios.

## 8. Where to inspect the calculations

- Core definitions and daily calculations: [`scripts/model_perf_core.py`](scripts/model_perf_core.py).
- Direction-following models and variant-specific EOD alternatives: [`scripts/build_strategy_sidecar_comparison.py`](scripts/build_strategy_sidecar_comparison.py), [`data/exponential_eod_positions_v1.csv`](data/exponential_eod_positions_v1.csv), [`data/force_multiplier_eod_positions_v1.csv`](data/force_multiplier_eod_positions_v1.csv), and [`data/force_multiplier_variant_eod_positions_v1.csv`](data/force_multiplier_variant_eod_positions_v1.csv).
- Daily composite PnL, exposure, and return-ratio series: [`data/strategy_sidecar_comparison_daily_v1.csv`](data/strategy_sidecar_comparison_daily_v1.csv); all 16 core/1U variant pairings with the 10U energy schedule: [`Charts/performance/21-force-variant-oil-comparison.png`](Charts/performance/21-force-variant-oil-comparison.png); all 32 with/without-energy percentage-gain series: [`Charts/performance/22-force-variant-oil-percent-gain.png`](Charts/performance/22-force-variant-oil-percent-gain.png).
- Energy and DXY daily schedules: [`data/tradingview_energy_sidecar_daily_20261024.csv`](data/tradingview_energy_sidecar_daily_20261024.csv) and [`data/dxy_currency_desk_sidecar_daily_20261024.csv`](data/dxy_currency_desk_sidecar_daily_20261024.csv); visible assumptions and sizing rows: [`TradingView Energy and Currency Desk Sidecars.md`](TradingView%20Energy%20and%20Currency%20Desk%20Sidecars.md).
- Price-source details: [`data/tradingview_benchmark_session_marks_20261024.csv`](data/tradingview_benchmark_session_marks_20261024.csv) and [`data/tradingview_benchmark_coverage_20261024.csv`](data/tradingview_benchmark_coverage_20261024.csv).
- Latest core results: [`Model Performance Comparison.md`](Model%20Performance%20Comparison.md) and [`Strategy and Sidecar Comparison.md`](Strategy%20and%20Sidecar%20Comparison.md). Historical whole-account DXY/yield views are not recalculated on this benchmark.

For a concise description of the four core variants, see the “The Four Models” table in the main comparison. This guide adds the operational details on lot creation, mark-to-market, and close behavior so the table labels are not mistaken for more symmetric rules than the code actually applies.
