# Hypothetical Securities Offering Briefing

**Working discussion draft · Fall (Arizona) [2026] paper-trade model · Not an offering document**

> **Important status notice.** This is an educational description of a hypothetical model architecture. It is not a prospectus, private-placement memorandum, offer to sell or solicitation to buy a security, investment recommendation, or promise of return. No actual issuer, security, price, minimum subscription, use of proceeds, fee schedule, redemption right, liquidity term, or offering authorization has been supplied; the illustrative unit price at the end is not an actual offering term. Do not circulate it as offering material without appropriate securities counsel, compliance review, complete offering terms, and substantiated performance disclosures.
>
> **Current-model snapshot — TradingView benchmark through 2026-10-23; regenerated from the revised Part B archive.** This briefing's model figures and 32-portfolio matrix now match the current reports. Each core variant includes the chart-directed **1U/DAY/DXY** index-return sleeve; its 1U daily schedule is already included and must not be added again. The 0.05U and 10U DXY schedules are standalone alternatives only. BTC/ETH remain excluded pending recalibration; XRH0 has five flagged provisional carry-forwards. The revised Part B archive corrects LLY's Oct. 20 close to **$1,283.66**; no legacy or substitute marks are used. See [`Model Performance Comparison.md`](Model%20Performance%20Comparison.md), [`Strategy and Sidecar Comparison.md`](Strategy%20and%20Sidecar%20Comparison.md), [`TradingView Energy and Currency Desk Sidecars.md`](TradingView%20Energy%20and%20Currency%20Desk%20Sidecars.md), and [`research/notes/tradingview-benchmark-import-20261024.md`](research/notes/tradingview-benchmark-import-20261024.md).
>
> The figures remain hypothetical historical model results, **not** a verified account track record, customer return, offering performance claim, or investment recommendation.

## 1. Purpose and operating model

The model is a set of historical paper-trade replays built from chart posts and manually entered trade records. The source ledger is maintained in [`trades/`](trades/) and [`trades.zip`](trades.zip); supporting assumptions and calculation rules are in [`Model Calculation Guide.md`](Model%20Calculation%20Guide.md). The covered book has 95 recorded 2026 events: 85 in-scope, price-covered direct-trade events plus one DXY direction signal used to activate the integrated daily sleeve, through October 23, 2026. The remaining records include BTC/ETH, FX, and yield/index events outside these portfolio replays. DXY's logged chart trade is not replayed as a direct-price security position; its charted direction drives one 1U index-return tranche at each active EOD.

The scripts can replay logged records and produce reports. **A broker-connected automated trading system is hypothetical, not operational.** This model is built to be operated manually by **Harshal Priyavadan Patel**: he reviews chart posts and trade records, makes discretionary decisions, enters or updates records, and manually reviews and places any paper or hypothetical order. No live automated order routing, real-time signal validation, or independently verified execution is represented here.

For a logged trade, the chart-posting price recorded in the trade log is the entry basis used by the model. Later minute or EOD prices mark the open lot; they do not replace the chart-posting entry. For example, the September 24 INTC short uses the chart-posting price of **$115.11**. This is a model convention, not evidence of a broker fill.

### What the historical replay does—and does not—show

- It compares rule-defined hypothetical position paths on one manually assembled paper-trade book; it is not a verified client account or audited investment track record.
- The current core replay covers 31 direct-price TradingView symbols plus an integrated chart-directed 1U/DAY/DXY index-return sleeve on a common EOD calendar through Oct. 23, 2026. BTC/ETH remain outside the core pending recalibration. Intraday source coverage is separate and shorter.
- All current core marks, including BRENT and OIL, use the normalized user-provided TradingView lists in [`data/tradingview_benchmark_session_marks_20261024.csv`](data/tradingview_benchmark_session_marks_20261024.csv). The revised Part B archive is pinned in [`data/tradingview_benchmark_source_manifest_part_b_20261024.json`](data/tradingview_benchmark_source_manifest_part_b_20261024.json); it corrects LLY's Oct. 20 close to $1,283.66. The 1U/DAY/DXY schedule is integrated in each core result; its 0.05U and 10U rows are alternatives, not extra core positions. XRH0 has five flagged provisional carry-forwards; no legacy price fills are used.
- The current core uses only the supplied TradingView lists; their source files, coverage, and mark statuses are recorded in the benchmark manifest and session-mark data. The archived source registry applies to historical views only.
- The replay does not comprehensively charge commissions, bid/ask spread, slippage, taxes, borrow, financing, margin, market impact, option premium, or operational costs. It does not establish executable capacity or customer-level returns.
- “PnL,” “deployed notional,” “open notional,” and percentage-gain ratios are model measures. The percentage-gain chart uses cumulative PnL divided by cumulative gross notional added; it is a **deployed-notional ratio, not an account return**.

## 2. Component models in the superstructure

The sections below distinguish the implemented historical models from the proposed combination layer. Similar names do not mean that the model books are interchangeable or automatically additive. In this brief, **1U / 1 Unit = $10,000 of entry notional**. Notional is not cash, equity, margin, or a guarantee of maximum loss.

### 2.1 Core V1 — 1U Open

V1 opens a lot for each logged LONG, REBUY, or SHORT using the logged unit size. An explicit EXIT or TAKE PROFIT closes open long lots. A later LONG/REBUY does **not** automatically cover an existing short, so long and short lots in the same ticker may coexist. “Open” means there is no LONG-triggered short-cover rule; explicit exits still operate.

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
- Every core model already includes one shared 1U/DAY/DXY index-return sleeve (35 daily lots; $350,000 gross notional added; +$2,492.30 terminal proxy PnL). Do not add that 1U DXY schedule again; only the 0.05U and 10U DXY schedules are standalone alternatives.
- Do not add core chart-opened BRENT/OIL positions to the energy sidecar a second time.
- Report PnL, cumulative gross notional, open notional, and the assumed account capital separately. Additive PnL lines do not net shares, contracts, cash, margin, or correlated risk.
- The all-32 percentage-gain view is cumulative composite PnL ÷ cumulative gross notional added. It is a deployed-notional ratio, **not an account return**.

No listed-options or other derivative-option strategy is modeled. There are no option chains, strikes, premiums, implied volatilities, Greeks, expirations, exercise/assignment treatment, or option collateral assumptions in these historical calculations. Any future option layer would be a separate model with separate authorization, risk limits, and disclosure; it cannot be inferred from the word “stacking.”

## 3. Current TradingView-only comparison snapshot

These are hypothetical model outputs through the **Oct. 23, 2026 EOD close**, not customer returns or estimates of future performance. The current core uses 31 direct-price symbols plus the integrated chart-directed 1U/DAY/DXY index-return sleeve. Core PnL and cumulative notional below **already include** the same DXY sleeve: 35 daily lots, $350,000 gross notional added, and +$2,492.30 terminal proxy PnL per core variant. BTC/ETH remain excluded. The updated Part B source corrects LLY's Oct. 20 mark from $12,833.66 to $1,283.66. With the corrected mark, Oct. 20 core daily PnL changes are V1 +$916.96, V2 +$623.64, V3A +$1,617.74, and V3B +$623.64; the prior artificial spike is removed.

| Current model/output | Terminal PnL | Cumulative gross notional added | Scope note |
|---|---:|---:|---|
| Core V1 — 1U Open | $+58,191.29 | $1,165,000.00 | 116.5U total, including the 35U integrated DXY sleeve |
| Core V2 — 1U SAR | $+55,348.09 | $1,165,000.00 | 116.5U total, including the 35U integrated DXY sleeve |
| Core V3A — Nu Open | $+79,474.78 | $1,255,000.00 | 125.5U total, including the 35U integrated DXY sleeve |
| Core V3B — Nu SAR | $+66,514.79 | $1,255,000.00 | 125.5U total, including the 35U integrated DXY sleeve |
| Fixed-$500/EOD direction-following alternative | $+5,917.91 | $328,000.00 | Separate alternative; $500 per active ticker/EOD |
| Shared-direction 1U/EOD force alternative | $+118,358.22 | $6,560,000.00 | Separate alternative; same schedule as $500 model at 20× tranche size |
| Variant-specific 1U/EOD V1 | $+127,180.97 | $6,560,000.00 | V1 close/size rules |
| Variant-specific 1U/EOD V2 | $+125,900.58 | $6,560,000.00 | V2 close/size rules |
| Variant-specific 1U/EOD V3A | $+148,084.09 | $6,650,000.00 | V3A close/size rules |
| Variant-specific 1U/EOD V3B | $+136,581.98 | $6,650,000.00 | V3B close/size rules |
| 10U TradingView energy sidecar | $+500,808.26 | $5,500,000.00 | Standalone daily-buy lots; composites add this sleeve once |

The DXY sizing alternatives are distinct from the integrated core sleeve:

| DXY daily schedule | Terminal proxy PnL | Cumulative notional added | Treatment |
|---|---:|---:|---|
| 0.05U/DAY | +$124.62 | $17,500.00 | Standalone alternative; not in core |
| 1U/DAY | +$2,492.30 | $350,000.00 | Integrated once in each core variant; do not add again |
| 10U/DAY | +$24,923.03 | $3,500,000.00 | Standalone alternative; not in core |

The separate one-time chart-opened DXY position has a displayed +$268.85 proxy PnL and is not part of the daily DXY sleeve or core totals. The DXY post has one LONG badge, although its caption conflicts; the replay follows the badge. DXY is an index-return proxy, not a modeled futures/ETF contract. Full marks, status flags, and schedule details are in [`TradingView Energy and Currency Desk Sidecars.md`](TradingView%20Energy%20and%20Currency%20Desk%20Sidecars.md).

### Core composites with standalone add-ons — terminal PnL

| Core variant | Core only | + $500/EOD | + shared 1U/EOD | + 10U energy | + $500 and energy | + shared 1U and energy |
|---|---:|---:|---:|---:|---:|---:|
| V1 | $+58,191.29 | $+64,109.20 | $+176,549.51 | $+558,999.55 | $+564,917.46 | $+677,357.77 |
| V2 | $+55,348.09 | $+61,266.00 | $+173,706.31 | $+556,156.35 | $+562,074.26 | $+674,514.57 |
| V3A | $+79,474.78 | $+85,392.69 | $+197,833.00 | $+580,283.04 | $+586,200.95 | $+698,641.26 |
| V3B | $+66,514.79 | $+72,432.70 | $+184,873.01 | $+567,323.05 | $+573,240.96 | $+685,681.27 |

These add-on examples combine core PnL with the relevant standalone schedule; the integrated DXY sleeve remains counted only through the core. The 1U/EOD alternatives use distinct direction-following or variant-specific rules described above. Notional and account capital are not netted. The 10U energy PnL is +$500,808.26 on $5,500,000.00 cumulative additions.

## 4. “THE ONE MODEL” — 32-portfolio split strategy

![THE ONE MODEL 32-portfolio split strategy and aggregate statistics](Charts/superstructure/the-one-model.png)

**Construction:** each portfolio combines one of four current core variants (V1, V2, V3A, V3B), each of which already includes the chart-directed 1U/DAY/DXY sleeve, with one of four variant-specific 1U/EOD models. All **16 Core × 1U/EOD pairings**, including cross-variant pairs, are represented once without and once with the **10U TradingView energy sidecar**, for **32 independently tracked portfolios**. The DXY 1U/DAY sleeve appears inside each core component exactly once; it is not a separate 33rd sidecar or an extra allocation layered on top. The 0.05U and 10U DXY schedules are not included in this 32-portfolio aggregate.

### Aggregate split-portfolio result (Sep. 3–Oct. 23, 2026; 36 sessions)

| Aggregate statistic | Result |
|---|---:|
| Portfolios in aggregate | 32 (16 without energy + 16 with energy) |
| Terminal aggregate modeled PnL | **$14,391,144.72** |
| Cumulative gross notional added, summed across all portfolios | **$338,080,000.00** |
| Gross open notional at period end, summed across all portfolios | **$303,200,000.00** |
| Aggregate PnL ÷ cumulative gross notional added | **4.2567%** |
| Aggregate PnL peak-to-trough decline | **$1,776,663.92** |
| Peak to trough | **09-28: +$1,803,351.28 → 09-29: +$26,687.36** |
| Portfolios with positive terminal modeled PnL | **32 of 32** |
| Mean / median terminal PnL per portfolio | $449,723.27 / $454,807.90 |

The 4.2567% figure is a **deployed-notional ratio, not an account return**. The drawdown is the peak-to-trough change in the sum of the modeled PnL series, not a loss percentage on defined account equity. The summed total assumes separate funding and gross exposure for all 32 portfolios; positions, capital, and risk are not netted or shared. Since each portfolio's core contains a $350,000 DXY sleeve, the aggregate reflects that sleeve once per portfolio; no separate DXY alternative schedule is added.

![THE ONE MODEL aggregate modeled PnL, gross notional, and deployed-notional ratio](Charts/superstructure/the-one-model-split-portfolio.png)

The best individual terminal PnL was **Core V3A + 1U/EOD V3A with the energy sidecar**: $728,367.13 on $13,405,000.00 gross notional added and $12,485,000.00 open, a 5.4335% deployed-notional ratio. The lowest individual terminal PnL was **Core V2 + 1U/EOD V2 without the energy sidecar**: $181,248.67 on $7,725,000.00 added and $6,555,000.00 open, a 2.3463% ratio. These remain two members of the split portfolio, not a selector that chose one winner.

Among the top individual terminal deployed-notional ratios are Core V3A + 1U V3A with energy (5.4335%), Core V3A + 1U V3B with energy (5.3477%), Core V3B + 1U V3A with energy (5.3369%), and Core V3A + 1U V1 with energy (5.3133%). These are individual-portfolio ratios, not the aggregate ratio.

### Terminal statistics for all 32 portfolios

The energy sidecar is included once in each “Yes” portfolio. Those 16 instances are separate allocations. The core DXY 1U/DAY sleeve is already present in every row through its core variant.

| Core variant | 1U/EOD variant | Energy sidecar | Terminal PnL | Gross notional added | Gross open notional | PnL / gross added |
|---|---|:---:|---:|---:|---:|---:|
| V1 | V1 | No | $185,372.26 | $7,725,000.00 | $6,805,000.00 | 2.3996% |
| V1 | V1 | Yes | $686,180.52 | $13,225,000.00 | $12,305,000.00 | 5.1885% |
| V1 | V2 | No | $184,091.87 | $7,725,000.00 | $6,605,000.00 | 2.3831% |
| V1 | V2 | Yes | $684,900.13 | $13,225,000.00 | $12,105,000.00 | 5.1788% |
| V1 | V3A | No | $206,275.38 | $7,815,000.00 | $6,895,000.00 | 2.6395% |
| V1 | V3A | Yes | $707,083.64 | $13,315,000.00 | $12,395,000.00 | 5.3104% |
| V1 | V3B | No | $194,773.27 | $7,815,000.00 | $6,605,000.00 | 2.4923% |
| V1 | V3B | Yes | $695,581.53 | $13,315,000.00 | $12,105,000.00 | 5.2240% |
| V2 | V1 | No | $182,529.06 | $7,725,000.00 | $6,755,000.00 | 2.3628% |
| V2 | V1 | Yes | $683,337.32 | $13,225,000.00 | $12,255,000.00 | 5.1670% |
| V2 | V2 | No | $181,248.67 | $7,725,000.00 | $6,555,000.00 | 2.3463% |
| V2 | V2 | Yes | $682,056.93 | $13,225,000.00 | $12,055,000.00 | 5.1573% |
| V2 | V3A | No | $203,432.18 | $7,815,000.00 | $6,845,000.00 | 2.6031% |
| V2 | V3A | Yes | $704,240.44 | $13,315,000.00 | $12,345,000.00 | 5.2891% |
| V2 | V3B | No | $191,930.07 | $7,815,000.00 | $6,555,000.00 | 2.4559% |
| V2 | V3B | Yes | $692,738.33 | $13,315,000.00 | $12,055,000.00 | 5.2027% |
| V3A | V1 | No | $206,655.75 | $7,815,000.00 | $6,895,000.00 | 2.6443% |
| V3A | V1 | Yes | $707,464.01 | $13,315,000.00 | $12,395,000.00 | 5.3133% |
| V3A | V2 | No | $205,375.36 | $7,815,000.00 | $6,695,000.00 | 2.6280% |
| V3A | V2 | Yes | $706,183.62 | $13,315,000.00 | $12,195,000.00 | 5.3037% |
| V3A | V3A | No | $227,558.87 | $7,905,000.00 | $6,985,000.00 | 2.8787% |
| V3A | V3A | Yes | $728,367.13 | $13,405,000.00 | $12,485,000.00 | 5.4335% |
| V3A | V3B | No | $216,056.76 | $7,905,000.00 | $6,695,000.00 | 2.7332% |
| V3A | V3B | Yes | $716,865.02 | $13,405,000.00 | $12,195,000.00 | 5.3477% |
| V3B | V1 | No | $193,695.76 | $7,815,000.00 | $6,755,000.00 | 2.4785% |
| V3B | V1 | Yes | $694,504.02 | $13,315,000.00 | $12,255,000.00 | 5.2160% |
| V3B | V2 | No | $192,415.37 | $7,815,000.00 | $6,555,000.00 | 2.4621% |
| V3B | V2 | Yes | $693,223.63 | $13,315,000.00 | $12,055,000.00 | 5.2063% |
| V3B | V3A | No | $214,598.88 | $7,905,000.00 | $6,845,000.00 | 2.7147% |
| V3B | V3A | Yes | $715,407.14 | $13,405,000.00 | $12,345,000.00 | 5.3369% |
| V3B | V3B | No | $203,096.77 | $7,905,000.00 | $6,555,000.00 | 2.5692% |
| V3B | V3B | Yes | $703,905.03 | $13,405,000.00 | $12,055,000.00 | 5.2511% |

Full daily audit series: [`the_one_model_split_portfolios_v1.csv`](data/the_one_model_split_portfolios_v1.csv). Machine-readable summary and portfolio-level drawdowns: [`the_one_model_split_portfolios_v1_summary.json`](data/the_one_model_split_portfolios_v1_summary.json). The source is the current daily Core × variant-specific 1U/EOD comparison with and without the exact-mark 10U energy sidecar. The split aggregator reconciles each energy-inclusive series against its no-energy pairing plus the energy schedule; DXY remains part of core on both sides.

### Scope and interpretation

- These are **historical hypothetical paper-model outputs**, not actual brokerage executions, a verified account track record, or a customer account return. The aggregate requires enough distinct capital to operate 32 portfolios concurrently.
- Each of the 16 with-energy portfolios receives one separately modeled 10U energy-sidecar schedule. Each of the 32 portfolios also includes the DXY 1U/DAY sleeve within core; its daily notional is not counted a second time as an add-on.
- Cumulative gross notional added is not initial equity, cash, margin, or a denominator for account return; the percentage shown is only aggregate PnL divided by the sum of gross notional added.
- Fixed-$500/EOD and shared-direction 1U/EOD schedules are separate alternatives, not additional members of this 32-portfolio universe. The 0.05U and 10U DXY sizing schedules are also separate alternatives and are excluded.
- Whole-book DXY-numeraire conversion/weighting, FX trade marks, US10Y/US30Y yield scenarios, CPI adjustment, and options are excluded from this aggregate; the chart-directed DXY 1U/DAY index-return sleeve is included through each core model.
- Trading costs, spread, slippage, taxes, borrow, financing, margin, and operational costs are not fully modeled. Energy marks use the exact user-provided EOD marks described above.
- The underlying records are chart posts and manually entered historical trades; the system remains manually operated by Harshal Priyavadan Patel. The 32-way sum does not represent an autonomous selector or a claim that a live allocation policy is optimal.

### What must be resolved before any customer-facing offering

- Legal issuer, security type, rights, price, unit size, minimum, use of proceeds, fees, liquidity/redemption, transfer, custody, valuation, tax, conflicts, and risk disclosures.
- A complete audited/independently reviewed record distinguishing manually logged paper trades, model simulations, and any live account history.
- A frozen and versioned specification for all 32 portfolio constituents, their capital allocations, sidecar treatment, and any optional DXY/FX, yield, inflation, or eventual options layers.
- Realistic trading costs, execution assumptions, margin/borrow/market impact, capacity, outage and data-error handling, and customer capital/accounting methodology.
- Appropriate legal and compliance review before the material is used to solicit or accept capital.

## 5. Key references

- [Model Performance Comparison](Model%20Performance%20Comparison.md)
- [Model Calculation Guide](Model%20Calculation%20Guide.md)
- [Strategy and Sidecar Comparison](Strategy%20and%20Sidecar%20Comparison.md)
- [TradingView Energy and Currency Desk Sidecars](TradingView%20Energy%20and%20Currency%20Desk%20Sidecars.md)
- [Part B benchmark source manifest](data/tradingview_benchmark_source_manifest_part_b_20261024.json)
- [Historical Oil Desk EOD Accumulation Hypothetical](Oil%20Desk%20EOD%20Accumulation%20Hypothetical.md)
- [Historical DXY-Equivalent Portfolio Snapshot](DXY-Equivalent%20Portfolio%20Snapshot.md)
- [`data/energy_provider_eod_marks_v1.csv`](data/energy_provider_eod_marks_v1.csv)
- [`data/active_price_source_registry_v3.csv`](data/active_price_source_registry_v3.csv)

---

### Hypothetical instrument price

Illustrative only; this is not an actual offering price or a commitment to issue a security. It is separate from the model’s **1U / 1 Unit = $10,000 entry-notional** convention unless final security terms explicitly equate them.

**$10,000/Unit**
