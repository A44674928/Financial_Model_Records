# Hypothetical Securities Offering Briefing

**Working discussion draft · Fall (Arizona) [2026] paper-trade model · Not an offering document**

> **Important status notice.** This is an educational description of a hypothetical model architecture. It is not a prospectus, private-placement memorandum, offer to sell or solicitation to buy a security, investment recommendation, or promise of return. No actual issuer, security, price, minimum subscription, use of proceeds, fee schedule, redemption right, liquidity term, or offering authorization has been supplied; the illustrative unit price at the end is not an actual offering term. Do not circulate it as offering material without appropriate securities counsel, compliance review, complete offering terms, and substantiated performance disclosures.
>
> **Historical draft—not a current performance disclosure (2026-10-24).** The comparison figures and 32-portfolio tables in this educational draft were generated from the prior benchmark/source mix and are retained only as historical material. Do not present them as results from the refreshed TradingView core or use them as offering performance claims. The current four-model results use 31 supplied TradingView direct-price symbols plus an integrated chart-directed 1U/DAY/DXY index-return sleeve; BTC/ETH are excluded pending recalibration, and XRH0 has five flagged provisional carry-forwards. Refer to [`Model Performance Comparison.md`](Model%20Performance%20Comparison.md), [`Strategy and Sidecar Comparison.md`](Strategy%20and%20Sidecar%20Comparison.md), and the [`TradingView Energy and Currency Desk Sidecars.md`](TradingView%20Energy%20and%20Currency%20Desk%20Sidecars.md) for current benchmark outputs and scope.

## 1. Purpose and operating model

The model is a set of historical paper-trade replays built from chart posts and manually entered trade records. The source ledger is maintained in [`trades/`](trades/) and [`trades.zip`](trades.zip); supporting assumptions and calculation rules are in [`Model Calculation Guide.md`](Model%20Calculation%20Guide.md). The covered book has 95 recorded 2026 events, of which 85 are in-scope, price-covered direct-trade events in the current four core replays through October 23, 2026. The remaining records include BTC/ETH, FX, and yield/index events outside those direct-price replays; DXY's logged trade is not replayed as a direct-price position, while its charted direction separately drives the integrated 1U/DAY index-return sleeve.

The scripts can replay logged records and produce reports. **A broker-connected automated trading system is hypothetical, not operational.** This model is built to be operated manually by **Harshal Priyavadan Patel**: he reviews chart posts and trade records, makes discretionary decisions, enters or updates records, and manually reviews and places any paper or hypothetical order. No live automated order routing, real-time signal validation, or independently verified execution is represented here.

For a logged trade, the chart-posting price recorded in the trade log is the entry basis used by the model. Later minute or EOD prices mark the open lot; they do not replace the chart-posting entry. For example, the September 24 INTC short uses the chart-posting price of **$115.11**. This is a model convention, not evidence of a broker fill.

### What the historical replay does—and does not—show

- It compares rule-defined hypothetical position paths on one manually assembled paper-trade book; it is not a verified client account or audited investment track record.
- The current core replay covers 31 direct-price TradingView symbols plus an integrated chart-directed 1U/DAY/DXY index-return sleeve on a common EOD calendar through Oct. 23, 2026. BTC/ETH remain outside the core pending recalibration. Intraday source coverage is separate and shorter.
- All current core marks, including BRENT and OIL, are from the normalized user-provided TradingView lists in [`data/tradingview_benchmark_session_marks_20261024.csv`](data/tradingview_benchmark_session_marks_20261024.csv). The standalone energy schedules, DXY 1U audit, and 0.05U/10U DXY alternatives are in [`TradingView Energy and Currency Desk Sidecars.md`](TradingView%20Energy%20and%20Currency%20Desk%20Sidecars.md); do not add the integrated DXY 1U sleeve twice. XRH0 has five flagged provisional carry-forwards; no legacy price fills are used.
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

**Interpretation of the family:** its comparison includes each member standalone, with oil, and in all 16 core-variant × 1U-variant pairings (matching and cross-variant), with and without oil. Composite PnL and notionals are additive reporting sums; holdings, cash, collateral, and risk are not netted.

### 2.8 Oil-desk EOD accumulation sidecar

The historical oil sidecar is a separate long-only schedule: add **10U ($100,000 notional)** in each energy instrument at every supplied EOD session. BRENT has 23 covered sessions and OIL has 32, for $5.5 million of cumulative daily-buy notional. Each lot is bought at the exact supplied EOD close, remains open through the terminal date, and its PnL is not reinvested into future lot size. No sidecar exits, fees, financing, or margin are modeled.

The historical sidecar’s Oct. 23 daily-buy PnL is **$499,705.92** before considering the separately shown chart-opened energy positions. Those chart-opened positions already belong to the core book; a composite adds only the sidecar’s incremental daily-buy lots, never those core positions a second time. The large daily notional means the oil sleeve can dominate raw-dollar composites.

**Interpretation:** this is a capital-intensive hypothetical, not a forecast and not an automatic hedge. Treat it as its own sleeve with its own capital, commodity, roll/contract, liquidity, and concentration analysis.

### 2.9 Whole-portfolio DXY numeraire and FX positions

The separate DXY-equivalent analysis divides USD account value by the daily DXY close to express the same account in DXY-equivalent units. **DXY is a numeraire in that report, not an added $10,000 position and not a live conversion instruction.** The analysis has separate capital bases and includes separately modeled FX/US30Y trade marks as documented in [`DXY-Equivalent Portfolio Snapshot.md`](DXY-Equivalent%20Portfolio%20Snapshot.md).

The current model does not decide when to convert USD into a DXY-linked instrument or back, nor does it apply a dynamic “DXY weight.” A true conversion sleeve would require a defined tradable vehicle, currency and settlement convention, allocation formula, rebalance timing, spread/fee/slippage inputs, custody/cash treatment, and limits. A numeraire comparison alone does not implement or validate that sleeve.

### 2.10 Yield multipliers and inflation-adjusted management

Two different yield-related calculations appear in the repository and should not be conflated:

1. **Legacy per-model additive US10Y carry** is preserved as a reference in the core comparison. It applies a spread over the 4.865% baseline to cumulative deployed notional over actual calendar days. It is not the active whole-account scenario and is not CPI inflation.
2. **Whole-account US10Y / US30Y scenarios** apply compounded yield-spread factors to a separate portfolio account basis. The combined scenario is US10Y × US30Y. The yields are not additional $10,000 positions; a separately logged US30Y trade, where included, remains distinct from the blanket factor.

Neither calculation is a Treasury total-return model or an inflation-adjusted return. To report real purchasing power, the model would need a selected CPI series, base date, release-lag convention, interval methodology, and an explicit account-level formula. “Yield maximizing” is not an implemented or validated objective; the factors are scenarios, not an optimizer.

### 2.11 Composite stacks and “options stacking”

The existing comparison’s “stacking” is **additive model composition**, not trading options contracts. A reported composite can add a chosen core model to one permitted sizing alternative and/or the incremental oil daily-buy sidecar, if the chart/table labels that combination. In all such comparisons:

- Do not stack the fixed-$500 alternative and a competing 1U force alternative as if both were one strategy.
- Do not stack the shared-direction force model with a variant-specific force model, or combine multiple variant rules into one book.
- Do not add core chart-opened BRENT/OIL positions to the oil sidecar a second time.
- Report PnL, cumulative gross notional, open notional, and the assumed account capital separately. Additive PnL lines do not net shares, contracts, cash, margin, or correlated risk.
- The all-32 percentage-gain view is cumulative composite PnL ÷ cumulative gross notional added. It is a deployed-notional ratio, **not an account return**.

No listed-options or other derivative-option strategy is modeled. There are no option chains, strikes, premiums, implied volatilities, Greeks, expirations, exercise/assignment treatment, or option collateral assumptions in these historical calculations. Any future option layer would be a separate model with separate authorization, risk limits, and disclosure; it cannot be inferred from the word “stacking.”

## 3. Historical comparison snapshot

These figures are **historical paper-model outputs through Oct. 23, 2026**, not customer returns or estimates of future performance. The core variants have different deployed notional, so raw PnL alone is not a like-for-like risk comparison.

| Historical model/output | Terminal PnL | Cumulative gross notional added | Scope note |
|---|---:|---:|---|
| Core V1 — 1U Open | $+82,270.58 | $845,000 | 84.5U; direct-price core replay |
| Core V2 — 1U SAR | $+57,553.26 | $845,000 | 84.5U; direct-price core replay |
| Core V3A — Nu Open | $+126,473.92 | $935,000 | 93.5U; includes qualifying compounded shorts |
| Core V3B — Nu SAR | $+68,719.96 | $935,000 | 93.5U; includes qualifying compounded shorts |
| Fixed-$500/EOD alternative | $-1,080.89 | $364,000 | Standalone daily accumulation |
| Shared-direction 1U/EOD alternative | $-21,617.85 | $7,280,000 | Standalone daily accumulation |
| Oil-desk daily-buy sidecar | $+499,705.92 | $5,500,000 | Standalone daily accumulation; 55 energy sessions total |

The separate variant-specific 1U/EOD force family produced standalone PnL of $+93,942.18 (V1), $-14,075.42 (V2), $+138,282.94 (V3A), $-3,394.02 (V3B), on $7.28 million / $7.37 million of cumulative additions as applicable. These are separately defined historical paths, not an endorsement of the highest terminal PnL.

Among the 32 pairings, the top individual terminal deployed-notional ratios were Core V3A + 1U V3A with oil (5.54%), Core V1 + 1U V3A with oil (5.25%), Core V3A + 1U V1 with oil (5.25%), Core V3B + 1U V3A with oil (5.12%). These are **individual-portfolio** ratios, not the ratio for the total split portfolio. The earlier **8.88% static single-composite proxy is not a result for this 32-portfolio split**. The all-32 aggregate result is calculated by summing the 32 separate portfolio PnLs and gross notionals below; all 16 Core × 1U/EOD pairings, including cross-variant pairs, are retained. Full definitions and data are in [`Model Performance Comparison.md`](Model%20Performance%20Comparison.md), [`Strategy and Sidecar Comparison.md`](Strategy%20and%20Sidecar%20Comparison.md), and [`DXY-Equivalent Portfolio Snapshot.md`](DXY-Equivalent%20Portfolio%20Snapshot.md).

## 4. “THE ONE MODEL” — 32-portfolio split strategy

![THE ONE MODEL 32-portfolio split strategy and aggregate statistics](Charts/superstructure/the-one-model.png)

**Construction:** run each of the four Core variants (V1, V2, V3A, V3B) against each of the four variant-specific 1U/EOD variants (V1, V2, V3A, V3B), creating all **16 Core × 1U/EOD pairings**, including cross-variant pairs. Run every pairing twice as two **separate portfolios**: once without oil and once with its own exact-mark oil daily-buy sidecar. This produces **32 independently tracked portfolios**, not one 32-way choice or a daily selector.

### Aggregate split-portfolio result (Sep. 3–Oct. 23, 2026; 36 sessions)

| Aggregate statistic | Result |
|---|---:|
| Portfolios in aggregate | 32 (16 without oil + 16 with oil) |
| Terminal aggregate modeled PnL | **$12,393,481.92** |
| Cumulative gross notional added, summed across all portfolios | **$350,880,000.00** |
| Gross open notional at period end, summed across all portfolios | **$316,000,000.00** |
| Aggregate PnL ÷ cumulative gross notional added | **3.5321%** |
| Aggregate PnL peak-to-trough decline | **$1,844,483.12** |
| Peak to trough | **09-28: +$2,622,698.32 → 09-29: +$778,215.20** |
| Portfolios with positive terminal modeled PnL | **32 of 32** |
| Mean / median terminal PnL per portfolio | $387,296.31 / $403,970.31 |

The 3.5321% figure is a **deployed-notional ratio, not an account return**. The drawdown is the peak-to-trough change in the sum of the modeled PnL series, not a loss percentage on defined account equity. The summed total assumes separate funding and gross exposure for all 32 portfolios; positions, capital, and risk are not netted or shared.

![THE ONE MODEL aggregate modeled PnL, gross notional, and deployed-notional ratio](Charts/superstructure/the-one-model-split-portfolio.png)

The best individual terminal PnL was **Core V3A + 1U/EOD V3A with oil**: $764,462.78 PnL on $13,805,000.00 gross notional added and $12,885,000.00 open, a 5.5376% deployed-notional ratio. The lowest individual terminal PnL was **Core V2 + 1U/EOD V2 without oil**: $43,477.84 on $8,125,000.00 added and $6,955,000.00 open, a 0.5351% ratio. These remain two members of the split portfolio, not a selector that chose one winner.

### Terminal statistics for all 32 portfolios

The oil sidecar is included once in each “Yes” portfolio. Those 16 instances are separate portfolio allocations, not duplicate counting within any one portfolio.

| Core variant | 1U/EOD variant | Oil sidecar | Terminal PnL | Gross notional added | Gross open notional | PnL / gross added |
|---|---|:---:|---:|---:|---:|---:|
| V1 | V1 | No | $176,212.76 | $8,125,000.00 | $7,205,000.00 | 2.1688% |
| V1 | V1 | Yes | $675,918.68 | $13,625,000.00 | $12,705,000.00 | 4.9609% |
| V1 | V2 | No | $68,195.16 | $8,125,000.00 | $7,005,000.00 | 0.8393% |
| V1 | V2 | Yes | $567,901.08 | $13,625,000.00 | $12,505,000.00 | 4.1681% |
| V1 | V3A | No | $220,553.52 | $8,215,000.00 | $7,295,000.00 | 2.6848% |
| V1 | V3A | Yes | $720,259.44 | $13,715,000.00 | $12,795,000.00 | 5.2516% |
| V1 | V3B | No | $78,876.56 | $8,215,000.00 | $7,005,000.00 | 0.9602% |
| V1 | V3B | Yes | $578,582.48 | $13,715,000.00 | $12,505,000.00 | 4.2186% |
| V2 | V1 | No | $151,495.44 | $8,125,000.00 | $7,155,000.00 | 1.8646% |
| V2 | V1 | Yes | $651,201.36 | $13,625,000.00 | $12,655,000.00 | 4.7795% |
| V2 | V2 | No | $43,477.84 | $8,125,000.00 | $6,955,000.00 | 0.5351% |
| V2 | V2 | Yes | $543,183.76 | $13,625,000.00 | $12,455,000.00 | 3.9867% |
| V2 | V3A | No | $195,836.20 | $8,215,000.00 | $7,245,000.00 | 2.3839% |
| V2 | V3A | Yes | $695,542.12 | $13,715,000.00 | $12,745,000.00 | 5.0714% |
| V2 | V3B | No | $54,159.24 | $8,215,000.00 | $6,955,000.00 | 0.6593% |
| V2 | V3B | Yes | $553,865.16 | $13,715,000.00 | $12,455,000.00 | 4.0384% |
| V3A | V1 | No | $220,416.10 | $8,215,000.00 | $7,295,000.00 | 2.6831% |
| V3A | V1 | Yes | $720,122.02 | $13,715,000.00 | $12,795,000.00 | 5.2506% |
| V3A | V2 | No | $112,398.50 | $8,215,000.00 | $7,095,000.00 | 1.3682% |
| V3A | V2 | Yes | $612,104.42 | $13,715,000.00 | $12,595,000.00 | 4.4630% |
| V3A | V3A | No | $264,756.86 | $8,305,000.00 | $7,385,000.00 | 3.1879% |
| V3A | V3A | Yes | $764,462.78 | $13,805,000.00 | $12,885,000.00 | 5.5376% |
| V3A | V3B | No | $123,079.90 | $8,305,000.00 | $7,095,000.00 | 1.4820% |
| V3A | V3B | Yes | $622,785.82 | $13,805,000.00 | $12,595,000.00 | 4.5113% |
| V3B | V1 | No | $162,662.14 | $8,215,000.00 | $7,155,000.00 | 1.9801% |
| V3B | V1 | Yes | $662,368.06 | $13,715,000.00 | $12,655,000.00 | 4.8295% |
| V3B | V2 | No | $54,644.54 | $8,215,000.00 | $6,955,000.00 | 0.6652% |
| V3B | V2 | Yes | $554,350.46 | $13,715,000.00 | $12,455,000.00 | 4.0419% |
| V3B | V3A | No | $207,002.90 | $8,305,000.00 | $7,245,000.00 | 2.4925% |
| V3B | V3A | Yes | $706,708.82 | $13,805,000.00 | $12,745,000.00 | 5.1192% |
| V3B | V3B | No | $65,325.94 | $8,305,000.00 | $6,955,000.00 | 0.7866% |
| V3B | V3B | Yes | $565,031.86 | $13,805,000.00 | $12,455,000.00 | 4.0930% |

Full daily audit series: [`the_one_model_split_portfolios_v1.csv`](data/the_one_model_split_portfolios_v1.csv). Machine-readable summary and portfolio-level drawdowns: [`the_one_model_split_portfolios_v1_summary.json`](data/the_one_model_split_portfolios_v1_summary.json). The source is the existing daily Core × variant-specific 1U/EOD comparison with and without the exact-mark oil sidecar; the split aggregator reconciles the oil-inclusive series against each no-oil pairing plus the sidecar.

### Scope and interpretation

- These are **historical hypothetical paper-model outputs**, not actual brokerage executions, a verified account track record, or a customer account return. The aggregate requires enough distinct capital to operate 32 portfolios concurrently.
- Each of the 16 with-oil portfolios receives one separately modeled oil sidecar schedule. Consequently, the aggregate contains 16 sidecar allocations (their gross additions are included once in each corresponding portfolio).
- Cumulative gross notional added is not initial equity, cash, margin, or a denominator for account return; the percentage shown is only aggregate PnL divided by the sum of gross notional added.
- Fixed-$500/EOD and shared-direction 1U/EOD schedules are separate alternatives, not additional members of this 32-portfolio universe. The 32 portfolio books do not net against each other.
- DXY conversion/weighting, US10Y/US30Y yield scenarios, CPI adjustment, and options are excluded; the available records do not define an integrated rule or compatible common capital basis for them.
- Trading costs, spread, slippage, taxes, borrow, financing, margin, and operational costs are not fully modeled. Oil marks use the exact user-provided EOD marks described above.
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
- [Oil Desk EOD Accumulation Hypothetical](Oil%20Desk%20EOD%20Accumulation%20Hypothetical.md)
- [DXY-Equivalent Portfolio Snapshot](DXY-Equivalent%20Portfolio%20Snapshot.md)
- [`data/energy_provider_eod_marks_v1.csv`](data/energy_provider_eod_marks_v1.csv)
- [`data/active_price_source_registry_v3.csv`](data/active_price_source_registry_v3.csv)

---

### Hypothetical instrument price

Illustrative only; this is not an actual offering price or a commitment to issue a security. It is separate from the model’s **1U / 1 Unit = $10,000 entry-notional** convention unless final security terms explicitly equate them.

**$10,000/Unit**
