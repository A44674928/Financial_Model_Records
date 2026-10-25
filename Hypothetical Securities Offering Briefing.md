# Hypothetical Securities Offering Briefing

**Working discussion draft · Fall (Arizona) [2026] paper-trade model · Not an offering document**

> **Important status notice.** This is an educational description of a hypothetical model architecture. It is not a prospectus, private-placement memorandum, offer to sell or solicitation to buy a security, investment recommendation, or promise of return. No actual issuer, security, price, minimum subscription, use of proceeds, fee schedule, redemption right, liquidity term, or offering authorization has been supplied; the illustrative unit price at the end is not an actual offering term. Do not circulate it as offering material without appropriate securities counsel, compliance review, complete offering terms, and substantiated performance disclosures.
>
> **Current-model snapshot — TradingView benchmark through 2026-10-23; regenerated from the revised Part B archive.** This briefing's model figures and 32-portfolio matrix now match the current reports. Each core variant includes the chart-directed **1U/DAY/DXY** index-return sleeve; its 1U daily schedule is already included and must not be added again. The 0.05U DXY schedule remains an alternative; THE ONE MODEL adds the 10U/DAY schedule to each portfolio alongside core’s integrated 1U/DAY sleeve (11U/DAY total). BTC/ETH remain excluded pending recalibration; XRH0 has five flagged provisional carry-forwards. The revised Part B archive corrects LLY's Oct. 20 close to **$1,283.66**; no legacy or substitute marks are used. The core also includes additional 50U Manual-Automatic LONG entries in BRENT at $111.412 and USOIL at $99.04, plus targeted 10U trims at $117 and $102. These are additive to the original Oct. 19 1U core entries; the first recorded EOD marks at/above targets are Oct. 23, which does not verify an intraday touch or fill. See [`Model Performance Comparison.md`](Model%20Performance%20Comparison.md), [`Strategy and Sidecar Comparison.md`](Strategy%20and%20Sidecar%20Comparison.md), [`TradingView Energy and Currency Desk Sidecars.md`](TradingView%20Energy%20and%20Currency%20Desk%20Sidecars.md), and [`research/notes/tradingview-benchmark-import-20261024.md`](research/notes/tradingview-benchmark-import-20261024.md).
>
> The figures remain hypothetical historical model results, **not** a verified account track record, customer return, offering performance claim, or investment recommendation.

## 1. Purpose and operating model

The model is a set of historical paper-trade replays built from chart posts and manually entered trade records. The source ledger is maintained in [`trades/`](trades/) and [`trades.zip`](trades.zip); supporting assumptions and calculation rules are in [`Model Calculation Guide.md`](Model%20Calculation%20Guide.md). The covered book has 99 recorded 2026 events: 89 in-scope, price-covered direct-trade events plus one DXY direction signal used to activate the integrated daily sleeve, through October 23, 2026. The remaining records include BTC/ETH, FX, and yield/index events outside these portfolio replays. DXY's logged chart trade is not replayed as a direct-price security position; its charted direction drives one 1U index-return tranche at each active EOD.

The scripts can replay logged records and produce reports. **A broker-connected automated trading system is hypothetical, not operational.** This model is built to be operated manually by **Harshal Priyavadan Patel**: he reviews chart posts and trade records, makes discretionary decisions, enters or updates records, and manually reviews and places any paper or hypothetical order. No live automated order routing, real-time signal validation, or independently verified execution is represented here.

For a logged trade, the chart-posting price recorded in the trade log is the entry basis used by the model. Later minute or EOD prices mark the open lot; they do not replace the chart-posting entry. For example, the September 24 INTC short uses the chart-posting price of **$115.11**. This is a model convention, not evidence of a broker fill.

### What the historical replay does—and does not—show

- It compares rule-defined hypothetical position paths on one manually assembled paper-trade book; it is not a verified client account or audited investment track record.
- The current core replay covers 31 direct-price TradingView symbols plus an integrated chart-directed 1U/DAY/DXY index-return sleeve on a common EOD calendar through Oct. 23, 2026. BTC/ETH remain outside the core pending recalibration. Intraday source coverage is separate and shorter.
- All current core marks, including BRENT and OIL, use the normalized user-provided TradingView lists in [`data/tradingview_benchmark_session_marks_20261024.csv`](data/tradingview_benchmark_session_marks_20261024.csv). The revised Part B archive is pinned in [`data/tradingview_benchmark_source_manifest_part_b_20261024.json`](data/tradingview_benchmark_source_manifest_part_b_20261024.json); it corrects LLY's Oct. 20 close to $1,283.66. The 1U/DAY/DXY schedule is integrated in each core result. THE ONE MODEL additionally includes the 10U/DAY DXY schedule in each of its 32 portfolios; energy-inclusive variants use 11U/DAY per active BRENT and OIL ticker. The 0.05U DXY schedule remains an alternative. XRH0 has five flagged provisional carry-forwards; no legacy price fills are used.
- The current core uses only the supplied TradingView lists; their source files, coverage, and mark statuses are recorded in the benchmark manifest and session-mark data. The archived source registry applies to historical views only.
- The replay does not comprehensively charge commissions, bid/ask spread, slippage, taxes, borrow, financing, margin, market impact, option premium, or operational costs. It does not establish executable capacity or customer-level returns.
- “PnL,” “deployed notional,” “open notional,” and percentage-gain ratios are model measures. The percentage-gain chart uses cumulative PnL divided by cumulative gross notional added; it is a **deployed-notional ratio, not an account return**.

## 2. Component models in the superstructure

The sections below distinguish the implemented historical models from the proposed combination layer. Similar names do not mean that the model books are interchangeable or automatically additive. In this brief, **1U / 1 Unit = $10,000 of entry notional**. Notional is not cash, equity, margin, or a guarantee of maximum loss.

### 2.1 Core V1 — 1U Open

V1 opens a lot for each logged LONG, REBUY, or SHORT using the logged unit size. A generic EXIT or TAKE PROFIT closes all open long lots; a specifically tagged Manual-Automatic target trim closes only the logged quantity from its tagged entry and leaves other lots untouched. A later LONG/REBUY does **not** automatically cover an existing short, so long and short lots in the same ticker may coexist. “Open” means there is no LONG-triggered short-cover rule; explicit exits still operate.

**How to read it:** V1 is a position-persistence baseline. Its open exposure can remain larger than a reader expects when a signal changes direction. It is not a netted or cash-neutral book.

### 2.2 Core V2 — 1U SAR

V2 uses the same entries, logged sizes, and explicit long exits as V1. In addition, a LONG or REBUY closes all open short lots for that ticker at the new event’s logged price before opening the new long. A new SHORT does not automatically close existing longs; the implemented SAR rule is therefore asymmetric rather than a symmetric “close the opposite side” rule.

**How to read it:** V2 can reduce short exposure when a long signal arrives, but a new short may coexist with open longs until an explicit exit handles them.

### 2.3 Core V3A — Nu Open

V3A follows V1’s open/exit behavior. For a SHORT specifically tagged “Compounded short,” if the preceding full exit for that ticker recorded more than one unit, that short is sized using the preceding exit’s unit count. This does not scale ordinary long entries or every later short; it is a qualifying event rule.

**How to read it:** V3A combines the open-book path with selective short sizing. Larger exposure can magnify both favorable and adverse moves.

### 2.4 Core V3B — Nu SAR

V3B combines V3A’s qualifying compounded-short sizing with V2’s LONG/REBUY-triggered short cover. Like V2, a new SHORT does not automatically close open longs.

**How to read it:** V3B adds both a sizing override for qualifying compounded shorts and the asymmetric SAR close rule. It is a distinct rule set, not a blend of V2 and V3A results after the fact.

### 2.5 Fixed-$500/EOD exponential alternative

After a ticker has a carried LONG/SHORT/REBUY direction, this alternative adds one **fixed $500 notional** lot per active ticker at every priced EOD. It closes all prior lots at the EOD mark when the carried direction flips. The $500 tranche does not grow with PnL, so this model is not compounding the tranche size.

**Interpretation:** it is a separate, smaller-sized daily accumulation strategy. It is not a $500 add-on to the 1U force model unless a comparison explicitly defines that composite.

### 2.6 Shared-direction 1U/EOD force alternative

This model uses the same direction state, EOD schedule, and flip logic as the fixed-$500 model, but adds one **1U ($10,000 notional)** tranche per active ticker per priced EOD. It is called a force multiplier in the repository, but it is a different tranche-size alternative—not an instruction to leverage or multiply an account balance. PnL is not reinvested into later tranche size.

**Interpretation:** when direction state and trade handling are identical, the unrounded exposure and PnL scale about 20× the fixed-$500 alternative. That is a sizing relationship, not proof of superior risk-adjusted performance.

### 2.7 Variant-specific 1U/EOD force family

These four separate daily-addition models place one 1U tranche per active ticker/EOD while applying the corresponding V1, V2, V3A, or V3B position-handling rule. Explicit EXIT/TAKE PROFIT events close open long lots at their logged prices but do not clear the carried direction; if a direction remains active, the scheduled EOD addition still occurs. They are alternatives to the shared-direction 1U force model and to each other.

#### Variant-specific 1U V1 — Open

Keeps opposite-direction lots open as V1 does; explicit exits close long lots. New daily lots follow the carried direction.

#### Variant-specific 1U V2 — SAR

LONG/REBUY closes open short lots at the logged signal price before the scheduled EOD long tranche. SHORT does not close existing longs.

#### Variant-specific 1U V3A — Nu Open

Uses V1 open behavior plus the qualifying compounded-short event-day sizing override. The event-day tranche can use the preceding full-exit unit count; following carried days return to the baseline 1U addition.

#### Variant-specific 1U V3B — Nu SAR

Uses V2’s LONG/REBUY short-cover behavior and V3A’s qualifying compounded-short event-day sizing override.

**Interpretation of the family:** its comparison includes each member standalone, with the energy sidecar, and in all 16 core-variant × 1U-variant pairings (matching and cross-variant), with and without the energy sidecar. Composite PnL and notionals are additive reporting sums; holdings, cash, collateral, and risk are not netted.

### 2.8 Energy-desk EOD accumulation sidecar

The current energy sidecar is a separate long-only schedule: add **10U ($100,000 notional)** in each energy instrument at every supplied EOD session. BRENT has 23 covered sessions and OIL has 32, for $5.5 million of cumulative daily-buy notional. Each lot is bought at the exact supplied EOD close, remains open through the terminal date, and its PnL is not reinvested into future lot size. No sidecar exits, fees, financing, or margin are modeled.

The 10U energy sidecar’s Oct. 23 daily-buy PnL is **$500,808.26** on $5,500,000.00 cumulative daily-buy notional, before considering the separately shown chart-opened energy positions. Those chart-opened positions already belong to the core book; a composite adds only the sidecar’s incremental daily-buy lots, never those core positions a second time. The large daily notional means the energy sleeve can dominate raw-dollar composites.

**Interpretation:** this is a capital-intensive hypothetical, not a forecast and not an automatic hedge. Treat it as its own sleeve with its own capital, commodity, roll/contract, liquidity, and concentration analysis.

### 2.9 Whole-portfolio DXY numeraire and FX positions

The separate DXY-equivalent analysis divides USD account value by the daily DXY close to express the same account in DXY-equivalent units. **DXY is a numeraire in that historical report, not an added $10,000 position and not a live conversion instruction.** The current core's 1U/DAY/DXY index-return sleeve is a separate modeled exposure, already included in core PnL; do not add it to the DXY-numeraire conversion. The numeraire analysis retains a prior benchmark and separate capital basis, with FX/US30Y marks as documented in [`DXY-Equivalent Portfolio Snapshot.md`](DXY-Equivalent%20Portfolio%20Snapshot.md).

The current model does not decide when to convert USD into a DXY-linked instrument or back, nor does it apply a dynamic “DXY weight.” A true conversion sleeve would require a defined tradable vehicle, currency and settlement convention, allocation formula, rebalance timing, spread/fee/slippage inputs, custody/cash treatment, and limits. A numeraire comparison alone does not implement or validate that sleeve.

### 2.10 Yield multipliers and inflation-adjusted management

Two different yield-related calculations appear in the repository and should not be conflated:

1. **Legacy per-model additive US10Y carry** is preserved as a reference in the core comparison. It applies a spread over the 4.865% baseline to cumulative deployed notional over actual calendar days. It is not the active whole-account scenario and is not CPI inflation.
2. **Whole-account US10Y / US30Y scenarios** apply compounded yield-spread factors to a separate portfolio account basis. The combined scenario is US10Y × US30Y. The yields are not additional $10,000 positions; a separately logged US30Y trade, where included, remains distinct from the blanket factor.

Neither calculation is a Treasury total-return model or an inflation-adjusted return. To report real purchasing power, the model would need a selected CPI series, base date, release-lag convention, interval methodology, and an explicit account-level formula. “Yield maximizing” is not an implemented or validated objective; the factors are scenarios, not an optimizer.

### 2.11 Composite stacks and “options stacking”

The existing comparison’s “stacking” is **additive model composition**, not trading options contracts. A reported composite can add a chosen core model to one permitted sizing alternative and/or the incremental energy daily-buy sidecar, if the chart/table labels that combination. In all such comparisons:

- Do not stack the fixed-$500 alternative and a competing 1U force alternative as if both were one strategy.
- Do not stack the shared-direction force model with a variant-specific force model, or combine multiple variant rules into one book.
- Every core model already includes one shared 1U/DAY/DXY index-return sleeve (35 daily lots; $350,000 gross notional added; +$2,492.30 terminal proxy PnL). Do not add that 1U schedule twice. The 10U/DAY DXY schedule is separately added to each THE ONE MODEL portfolio; 0.05U remains an alternative.
- Do not add core chart-opened BRENT/OIL positions to the energy sidecar a second time.
- Report PnL, cumulative gross notional, open notional, and the assumed account capital separately. Additive PnL lines do not net shares, contracts, cash, margin, or correlated risk.
- The all-32 percentage-gain view is cumulative composite PnL ÷ cumulative gross notional added. It is a deployed-notional ratio, **not an account return**.

No listed-options or other derivative-option strategy is modeled. There are no option chains, strikes, premiums, implied volatilities, Greeks, expirations, exercise/assignment treatment, or option collateral assumptions in these historical calculations. Any future option layer would be a separate model with separate authorization, risk limits, and disclosure; it cannot be inferred from the word “stacking.”

## 3. Current TradingView-only comparison snapshot

These are hypothetical model outputs through the **Oct. 23, 2026 EOD close**, not customer returns or estimates of future performance. The current core uses 31 direct-price symbols plus the integrated chart-directed 1U/DAY/DXY index-return sleeve. It now also includes the user-specified **Manual-Automatic Entry** lots: additional 50U LONG BRENT at $111.412 and 50U LONG USOIL (repository ticker `OIL`) at $99.04, on top of the original Oct. 19 1U lots. The tagged lots model automatic 10U target trims at $117/$102 on the first available EOD mark at/above target (Oct. 23), leaving 40U of each new lot and preserving the original 1U lots. This EOD trigger does not prove an intraday touch or execution. The entries/trim are in all four core variants and downstream core-based outputs; the linked Weekend Oil report is lot attribution only, not an extra overlay. BTC/ETH remain excluded. The updated Part B source corrects LLY's Oct. 20 mark from $12,833.66 to $1,283.66. Oct. 20 core daily net PnL changes, including the Manual-Automatic oil positions, are V1 -$575.22, V2 -$868.55, V3A +$125.56, and V3B -$868.55; the daily totals include both the corrected LLY mark and the oil lots' EOD changes.

| Current model/output | Terminal PnL | Cumulative gross notional added | Scope note |
|---|---:|---:|---|
| Core V1 — 1U Open | $+105,307.70 | $2,165,000.00 | 216.50U total, incl. 100U new Manual-Automatic oil lots and 35U integrated DXY |
| Core V2 — 1U SAR | $+102,464.50 | $2,165,000.00 | 216.50U total, incl. 100U new Manual-Automatic oil lots and 35U integrated DXY |
| Core V3A — Nu Open | $+126,591.19 | $2,255,000.00 | 225.50U total, incl. 100U new Manual-Automatic oil lots and 35U integrated DXY |
| Core V3B — Nu SAR | $+113,631.20 | $2,255,000.00 | 225.50U total, incl. 100U new Manual-Automatic oil lots and 35U integrated DXY |
| Fixed-$500/EOD direction-following alternative | $+5,917.91 | $328,000.00 | Separate alternative; $500 per active ticker/EOD |
| Shared-direction 1U/EOD force alternative | $+118,358.22 | $6,560,000.00 | Separate alternative; $10,000 per active ticker/EOD |
| Variant-specific 1U/EOD V1 | $+127,180.97 | $6,560,000.00 | V1 close/size rules |
| Variant-specific 1U/EOD V2 | $+125,900.58 | $6,560,000.00 | V2 close/size rules |
| Variant-specific 1U/EOD V3A | $+148,084.09 | $6,650,000.00 | V3A close/size rules |
| Variant-specific 1U/EOD V3B | $+136,581.98 | $6,650,000.00 | V3B close/size rules |
| 10U TradingView energy sidecar | $+500,808.26 | $5,500,000.00 | Standalone daily-buy lots; standard composites add this sidecar once |

The DXY sizing alternatives are distinct from the integrated core sleeve:

| DXY daily schedule | Terminal proxy PnL | Cumulative notional added | Treatment |
|---|---:|---:|---|
| 0.05U/DAY | +$124.62 | $17,500.00 | Standalone alternative; not in core |
| 1U/DAY | +$2,492.30 | $350,000.00 | Integrated once in each core variant; do not add again |
| 10U/DAY | +$24,923.03 | $3,500,000.00 | Not in core variants; selected as an add-on in every THE ONE MODEL portfolio |

The separate one-time chart-opened DXY position has a displayed +$268.85 proxy PnL and is not part of the daily DXY sleeve or core totals. The DXY post has one LONG badge, although its caption conflicts; the replay follows the badge. DXY is an index-return proxy, not a modeled futures/ETF contract. Full marks, status flags, and schedule details are in [`TradingView Energy and Currency Desk Sidecars.md`](TradingView%20Energy%20and%20Currency%20Desk%20Sidecars.md).

### Core composites with standalone add-ons — terminal PnL

| Core variant | Core only | + $500/EOD | + shared 1U/EOD | + 10U energy | + $500 and energy | + shared 1U and energy |
|---|---:|---:|---:|---:|---:|---:|
| V1 | $+105,307.70 | $+111,225.61 | $+223,665.92 | $+606,115.96 | $+612,033.87 | $+724,474.18 |
| V2 | $+102,464.50 | $+108,382.41 | $+220,822.72 | $+603,272.76 | $+609,190.67 | $+721,630.98 |
| V3A | $+126,591.19 | $+132,509.10 | $+244,949.41 | $+627,399.45 | $+633,317.36 | $+745,757.67 |
| V3B | $+113,631.20 | $+119,549.11 | $+231,989.42 | $+614,439.46 | $+620,357.37 | $+732,797.68 |

These additive examples combine updated core PnL with each permitted separate schedule. The integrated DXY sleeve remains counted only through core. The Manual-Automatic BRENT/USOIL lots are already in core, so do not add the Weekend Oil attribution a second time. The standard comparison energy schedule remains 10U; the sidecar's terminal PnL is +$500,808.26 on $5,500,000.00 cumulative additions.

## 4. “THE ONE MODEL” — 32-portfolio split strategy

![THE ONE MODEL 32-portfolio split strategy and aggregate statistics](Charts/superstructure/the-one-model.png)

**Construction:** each portfolio pairs one of four current core variants with one of four variant-specific 1U/EOD models. All **16 Core × 1U/EOD pairings** are represented once without and once with an energy sidecar, for **32 independently tracked portfolios**. The energy-inclusive 16 use **11U/DAY per active BRENT and OIL ticker**, meeting the combined DXY exposure of **11U/DAY** (the core-integrated 1U plus the 10U DXY add-on). The other 16 remain explicit no-energy alternatives. DXY is counted once in core and once as the selected 10U sidecar; the 0.05U DXY schedule remains an alternative.

### Aggregate split-portfolio result (Sep. 3–Oct. 23, 2026; 36 sessions)

| Aggregate statistic | Result |
|---|---:|
| Portfolios in aggregate | 32 (16 without energy + 16 with energy) |
| Terminal aggregate modeled PnL | **$17,497,700.08** |
| Cumulative gross notional added, summed across all portfolios | **$490,880,000.00** |
| Gross open notional at period end, summed across all portfolios | **$449,600,000.00** |
| Aggregate PnL ÷ cumulative gross notional added | **3.564558%** |
| Aggregate PnL peak-to-trough decline | **$1,786,528.08** |
| Peak to trough | **2026-09-28: $2,344,610.48 → 2026-09-29: $558,082.40** |
| Portfolios with positive terminal modeled PnL | **32 of 32** |
| Mean / median terminal PnL per portfolio | $546,803.13 / $551,887.76 |

**Energy/currency unit rule:** in every energy-inclusive portfolio, each active energy ticker receives an 11U tranche per scheduled session, matching the 11U/DAY combined DXY exposure. BRENT’s supplied daily schedule starts Sep. 23; OIL’s starts Sep. 10. No earlier energy entries or prices are invented. On sessions when both energy schedules are active, the combined energy allocation is 22U/DAY across BRENT and OIL. The 16 no-energy states are intentional alternatives, not energy-inclusive portfolios.

The 11U energy sidecar contributes $550,889.09 terminal modeled PnL on $6,050,000.00 cumulative additions per energy-inclusive portfolio. Across the 16 such portfolios, it contributes $8,814,225.44 on $96,800,000.00 additions.

**DXY exposure:** every portfolio has 35 daily 1U core lots plus 35 daily 10U sidecar lots, or **11U/DAY**. Per portfolio the 10U add-on contributes $24,923.03 terminal proxy PnL on $3,500,000.00 additions; combined with the 1U core sleeve, DXY contributes **$27,415.33** on **$3,850,000.00** per portfolio. The 0.05U schedule and the separate one-time chart-opened DXY position are excluded.

The aggregate percentage is a **deployed-notional ratio, not an account return**. Drawdown is the peak-to-trough change in summed modeled PnL, not a loss percentage on defined account equity. The sum assumes distinct funding and gross exposures for all 32 portfolios; positions, capital, and risk are not netted or shared. The Manual-Automatic lots are part of each core path, as are other core entries; the 32-book sum follows the existing independent-portfolio construction. The separate Weekend Oil attribution is not added again.

![THE ONE MODEL aggregate modeled PnL, gross notional, and deployed-notional ratio](Charts/superstructure/the-one-model-split-portfolio.png)

The best individual terminal PnL was **V3A Core + V3A 1U/EOD with the 11U energy sidecar**: $850,487.40 on $18,455,000.00 gross additions and $17,335,000.00 open. The lowest was **V2 Core + V2 1U/EOD without the energy sidecar**: $253,288.11 on $12,225,000.00 added and $10,855,000.00 open. These remain members of the fixed portfolio universe, not a selector that chose a winner.

### Terminal statistics for all 32 portfolios

Every row includes the integrated 1U/DAY DXY core sleeve plus the 10U/DAY DXY sidecar (11U/DAY total). “11U/DAY” under Energy means an 11U tranche for each active energy ticker; “No” preserves the no-energy variant.

| Core variant | 1U/EOD variant | Energy sidecar | DXY 10U sidecar | Combined DXY | Terminal PnL | Gross notional added | Gross open notional | PnL / gross added |
|---|---|:---:|:---:|:---:|---:|---:|---:|---:|
| V1 | V1 | No | Yes | 11U/DAY | $257,411.70 | $12,225,000.00 | $11,105,000.00 | 2.105617% |
| V1 | V1 | 11U/DAY | Yes | 11U/DAY | $808,300.79 | $18,275,000.00 | $17,155,000.00 | 4.422987% |
| V1 | V2 | No | Yes | 11U/DAY | $256,131.31 | $12,225,000.00 | $10,905,000.00 | 2.095144% |
| V1 | V2 | 11U/DAY | Yes | 11U/DAY | $807,020.40 | $18,275,000.00 | $16,955,000.00 | 4.415980% |
| V1 | V3A | No | Yes | 11U/DAY | $278,314.82 | $12,315,000.00 | $11,195,000.00 | 2.259966% |
| V1 | V3A | 11U/DAY | Yes | 11U/DAY | $829,203.91 | $18,365,000.00 | $17,245,000.00 | 4.515132% |
| V1 | V3B | No | Yes | 11U/DAY | $266,812.71 | $12,315,000.00 | $10,905,000.00 | 2.166567% |
| V1 | V3B | 11U/DAY | Yes | 11U/DAY | $817,701.80 | $18,365,000.00 | $16,955,000.00 | 4.452501% |
| V2 | V1 | No | Yes | 11U/DAY | $254,568.50 | $12,225,000.00 | $11,055,000.00 | 2.082360% |
| V2 | V1 | 11U/DAY | Yes | 11U/DAY | $805,457.59 | $18,275,000.00 | $17,105,000.00 | 4.407429% |
| V2 | V2 | No | Yes | 11U/DAY | $253,288.11 | $12,225,000.00 | $10,855,000.00 | 2.071886% |
| V2 | V2 | 11U/DAY | Yes | 11U/DAY | $804,177.20 | $18,275,000.00 | $16,905,000.00 | 4.400422% |
| V2 | V3A | No | Yes | 11U/DAY | $275,471.62 | $12,315,000.00 | $11,145,000.00 | 2.236879% |
| V2 | V3A | 11U/DAY | Yes | 11U/DAY | $826,360.71 | $18,365,000.00 | $17,195,000.00 | 4.499650% |
| V2 | V3B | No | Yes | 11U/DAY | $263,969.51 | $12,315,000.00 | $10,855,000.00 | 2.143480% |
| V2 | V3B | 11U/DAY | Yes | 11U/DAY | $814,858.60 | $18,365,000.00 | $16,905,000.00 | 4.437019% |
| V3A | V1 | No | Yes | 11U/DAY | $278,695.19 | $12,315,000.00 | $11,195,000.00 | 2.263055% |
| V3A | V1 | 11U/DAY | Yes | 11U/DAY | $829,584.28 | $18,365,000.00 | $17,245,000.00 | 4.517203% |
| V3A | V2 | No | Yes | 11U/DAY | $277,414.80 | $12,315,000.00 | $10,995,000.00 | 2.252658% |
| V3A | V2 | 11U/DAY | Yes | 11U/DAY | $828,303.89 | $18,365,000.00 | $17,045,000.00 | 4.510231% |
| V3A | V3A | No | Yes | 11U/DAY | $299,598.31 | $12,405,000.00 | $11,285,000.00 | 2.415142% |
| V3A | V3A | 11U/DAY | Yes | 11U/DAY | $850,487.40 | $18,455,000.00 | $17,335,000.00 | 4.608439% |
| V3A | V3B | No | Yes | 11U/DAY | $288,096.20 | $12,405,000.00 | $10,995,000.00 | 2.322420% |
| V3A | V3B | 11U/DAY | Yes | 11U/DAY | $838,985.29 | $18,455,000.00 | $17,045,000.00 | 4.546114% |
| V3B | V1 | No | Yes | 11U/DAY | $265,735.20 | $12,315,000.00 | $11,055,000.00 | 2.157817% |
| V3B | V1 | 11U/DAY | Yes | 11U/DAY | $816,624.29 | $18,365,000.00 | $17,105,000.00 | 4.446634% |
| V3B | V2 | No | Yes | 11U/DAY | $264,454.81 | $12,315,000.00 | $10,855,000.00 | 2.147420% |
| V3B | V2 | 11U/DAY | Yes | 11U/DAY | $815,343.90 | $18,365,000.00 | $16,905,000.00 | 4.439662% |
| V3B | V3A | No | Yes | 11U/DAY | $286,638.32 | $12,405,000.00 | $11,145,000.00 | 2.310668% |
| V3B | V3A | 11U/DAY | Yes | 11U/DAY | $837,527.41 | $18,455,000.00 | $17,195,000.00 | 4.538214% |
| V3B | V3B | No | Yes | 11U/DAY | $275,136.21 | $12,405,000.00 | $10,855,000.00 | 2.217946% |
| V3B | V3B | 11U/DAY | Yes | 11U/DAY | $826,025.30 | $18,455,000.00 | $16,905,000.00 | 4.475889% |


Full daily audit series: [`the_one_model_split_portfolios_v1.csv`](data/the_one_model_split_portfolios_v1.csv). Derived 11U energy schedule by ticker: [`the_one_model_energy_11u_sidecar_daily_v1.csv`](data/the_one_model_energy_11u_sidecar_daily_v1.csv). Machine-readable summary and portfolio-level drawdowns: [`the_one_model_split_portfolios_v1_summary.json`](data/the_one_model_split_portfolios_v1_summary.json). The source daily Core × variant-specific 1U/EOD series and generic strategy-comparison composites retain their existing 10U energy size; this split aggregator scales that energy component to 11U only for THE ONE MODEL’s 16 energy-inclusive portfolios.

### Scope and interpretation

- These are **historical hypothetical paper-model outputs**, not actual brokerage executions, a verified account track record, or a customer account return. The aggregate requires enough distinct capital to operate 32 portfolios concurrently.
- Each of the 16 energy-inclusive portfolios receives an 11U/DAY schedule per active BRENT and OIL ticker. The other 16 intentionally contain no energy sidecar. Every portfolio has a 10U/DAY DXY add-on in addition to the 1U/DAY DXY core sleeve; the 0.05U DXY size and one-time chart-opened position remain separate/excluded.
- Cumulative gross notional added is not initial equity, cash, margin, or a denominator for account return; the percentage shown is only aggregate PnL divided by the sum of gross notional added.
- Fixed-$500/EOD and shared-direction 1U/EOD schedules are separate alternatives, not additional members of this 32-portfolio universe. Whole-book DXY-numeraire conversion/weighting, FX trade marks, US10Y/US30Y yield scenarios, CPI adjustment, and options are excluded.
- Trading costs, spread, slippage, taxes, borrow, financing, margin, and operational costs are not fully modeled. Energy marks use the exact user-provided EOD marks described above.
- The underlying records are chart posts and manually entered historical trades; the system remains manually operated by Harshal Priyavadan Patel. The 32-way sum does not represent an autonomous selector or a claim that a live allocation policy is optimal.
### What must be resolved before any customer-facing offering

- Legal issuer, security type, rights, price, unit size, minimum, use of proceeds, fees, liquidity/redemption, transfer, custody, valuation, tax, conflicts, and risk disclosures.
- A complete audited/independently reviewed record distinguishing manually logged paper trades, model simulations, and any live account history.
- A frozen and versioned specification for all 32 portfolio constituents, their capital allocations, sidecar treatment, and any optional DXY/FX, yield, inflation, or eventual options layers.
- Realistic trading costs, execution assumptions, margin/borrow/market impact, capacity, outage and data-error handling, and customer capital/accounting methodology.
- Appropriate legal and compliance review before the material is used to solicit or accept capital.

## 5. Key references

- [THE ONE MODEL vs THE WINNING MODEL](THE%20ONE%20MODEL%20vs%20THE%20WINNING%20MODEL.md) — equal-terminal-gross-additions comparison; the selected winner is an ex-post, same-period benchmark.
- [Model Performance Comparison](Model%20Performance%20Comparison.md)
- [Model Calculation Guide](Model%20Calculation%20Guide.md)
- [Strategy and Sidecar Comparison](Strategy%20and%20Sidecar%20Comparison.md)
- [TradingView Energy and Currency Desk Sidecars](TradingView%20Energy%20and%20Currency%20Desk%20Sidecars.md)
- [Part B benchmark source manifest](data/tradingview_benchmark_source_manifest_part_b_20261024.json)
- [Weekend Oil 50U Position Hypothetical](Weekend%20Oil%2050U%20Position%20Hypothetical.md) — lot-level attribution for the Oct. 19 core-integrated BRENT/USOIL Manual-Automatic entries; not an additional overlay.
- [Historical Oil Desk EOD Accumulation Hypothetical](Oil%20Desk%20EOD%20Accumulation%20Hypothetical.md)
- [Historical DXY-Equivalent Portfolio Snapshot](DXY-Equivalent%20Portfolio%20Snapshot.md)
- [`data/energy_provider_eod_marks_v1.csv`](data/energy_provider_eod_marks_v1.csv)
- [`data/active_price_source_registry_v3.csv`](data/active_price_source_registry_v3.csv)

---

### Hypothetical instrument price

Illustrative only; this is not an actual offering price or a commitment to issue a security. It is separate from the model’s **1U / 1 Unit = $10,000 entry-notional** convention unless final security terms explicitly equate them.

**$10,000/Unit**
