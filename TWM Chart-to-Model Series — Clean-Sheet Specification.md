# TWM Chart-to-Model Series — Clean-Sheet Specification

**Purpose:** define how user-supplied private charts and the user's stated position/direction are translated into auditable TWM paper-model paths. This is the chart-to-model operating contract; it does not claim that the current repository automatically reads chart images or places trades.

**Scope:** TWM_1M sizing family, the proposed TWM_20B pool wrapper, and an optional realized-PnL share/model-unit accumulator. The model names identify hypothetical paper replays—not brokerage accounts, verified fills, or investment advice.

## TWM terminology

**TWM** is the prefix for the **The Winning Model** chart-to-model series described here. In this document, TWM names the family of chart-driven replay and sizing configurations; it does not mean every TWM configuration is itself the current winner selected from THE ONE MODEL. In particular, `TWM_1M_FULL`, `TWM_1M_LIGHT`, and `TWM_1M_MAX` have distinct sidecar scopes, and the current THE ONE MODEL winner is a dated, replaceable selection. See the [THE ONE MODEL winner and contender specification](THE%20ONE%20MODEL%20%E2%80%94%20Winning%20Model%20and%20Contender%20Specification.md) for that selection and its future-contender rules.

## 1. Governing principles

1. **The user supplies intent.** A chart may show context, but only the user's explicit direction/position statement authorizes a model event. The model must not infer a LONG, SHORT, exit, price, quantity, fill, or position state from an ambiguous picture.
2. **Keep source and interpretation separate.** Preserve the supplied chart reference and the user's words; separately record normalized model events and any assistant interpretation. Ask before applying an ambiguous event.
3. **No invented executions.** Label every price and action as a user-reported input, chart-observed mark, model assumption, or verified source mark. A modeled signal/trigger is not proof of a fill.
4. **TradingView-only valuation marks.** Use the designated user-provided TradingView EOD close series for model marking. Do not substitute legacy prices or another vendor. A chart price supplied by the user may be an event price; it does not silently become the official EOD mark series.
5. **Separate PnL, exposure, cash, and share quantity.** Cumulative additions are turnover, not cash deposited or current open exposure. An accumulator's share counts are not PnL. Its accounting basis is not the same as new out-of-pocket cash.
6. **Retain model identity.** Run each chosen variant independently. Do not blend rule sets or net capital/positions between model books unless a new, explicit specification says to do so.
7. **Private chart handling.** Use a private chart only to answer the user's request in this conversation. Do not publish, share, or include its image in a public-facing report without explicit permission. The normalized event ledger should cite the user's supplied source without implying the image is public.

## 2. Chart submission and event-intake contract

The user may post one chart or a batch. For each ticker/chart, supply as much of the following as applies; missing required details are queried, not guessed.

| Intake field | What to provide |
|---|---|
| Instrument | Exact ticker/symbol and, if needed, mapping (for example, OIL/USOIL). DXY is an index-return proxy, not a direct-price share. |
| Chart context | Chart date/time, timezone, timeframe, and any panel/indicator whose interpretation matters. |
| User-declared position/direction | LONG, SHORT, flat, or hold; whether this is current position, a new signal, or a requested model action. Explain what the user believes the chart says. |
| Event/action | Entry, REBUY, exit, partial trim, reversal, add, or observation only. State whether it is a hypothetical model event or a reported paper-trade event. |
| Event price and size | User-provided price and units/notional, if known. Identify exact vs approximate/recalled values. Do not derive a fill from a chart line. |
| Model target | TWM_1M_FULL/LIGHT/MAX, TWM_20B, the core comparison, THE ONE MODEL constituent, or a named research-only path. State whether the accumulator is ON or OFF. |
| Valuation date/source | Which supplied TradingView EOD mark file/session window should be used. A price absent from that input remains absent; no legacy substitution. |
| Special handling | Direction carry, exit treatment, sidecar, DXY scope, and any ticker-specific override. State if an override should apply to one model only or all models. |

### Recommended chart-post template

```text
Ticker / instrument:
Chart date-time and timezone:
Chart timeframe:
My position now (long / short / flat) and my read of the chart:
New action, if any (entry / rebuy / add / trim / exit / none):
Price and size (exact, approximate, or unknown):
Event status (user-reported paper event / hypothetical instruction / visual context only):
Model(s) to run:
Accumulator (OFF / ON):
TradingView EOD mark window or supplied source:
Notes / exceptions:
```

### Assistant intake response

Before replay, return a compact event recap: symbol, user-stated direction/action, date/time/timezone, price, size, model targets, source/status, and unresolved assumptions. Ask targeted questions where entries, exit scope, units, timing, DXY treatment, or accumulator treatment are ambiguous. A chart-only upload with no direction statement is context—not an implicit trade.

## 3. From chart statement to replay input

1. **Preserve the source:** associate the chart attachment/name or conversation reference with a private event note. Keep it distinct from TradingView mark files.
2. **Normalize only confirmed events:** map the user's stated action into the repository's event vocabulary (`LONG`, `REBUY`, `SHORT`, entry/exit, units, event price, note). Keep the original user-provided price, quantity, and timing. Annotate approximate/recalled facts as such.
3. **Validate chronology and scope:** sort by date/time/ticker/source order; check duplicate/contradictory events; confirm that a model-specific override is not accidentally applied to sibling variants.
4. **Map events to sessions:** current core replay maps an event to the first priced session on or after its date. Weekend/holiday events therefore take effect on the next available session. Do not pretend an out-of-window event occurred at the final available mark.
5. **Apply a chosen rule set:** run the same confirmed event set through each requested model independently. Do not add the $500 alternative, shared-direction 1U alternative, and variant-specific 1U family together unless explicitly specified.
6. **Mark and report:** mark open positions at the supplied TradingView EOD close. Show realized PnL, unrealized PnL, total PnL, open gross notional, cumulative gross additions, share/U counts (if enabled), and source coverage separately.
7. **Reconcile:** check ticker-level results against portfolio totals; identify missing marks, provisional/carry-forward marks, ignored records, and excluded events. Preserve the input revision/date in the output.

The parser in this repository currently consumes standardized text records in `trades/*.txt`. Chart-image ingestion is a **human-in-the-loop specification**, not a claim of automated OCR or automated position recognition.

## 4. Core position math and variants

The standard model unit is **1U = $10,000 of entry notional**. It is a sizing convention, not a fixed share count. For `q` units, entry price `E`, and close or mark `P`:

- Long PnL = `q × $10,000 × (P / E − 1)`
- Short PnL = `q × $10,000 × (1 − P / E)`

Open-lot mark-to-market uses supplied TradingView EOD marks. The current core variants are separate rule sets:

| Core path | Sizing | Close / reversal behavior |
|---|---|---|
| **V1 — 1U Open** | Logged entry units | Explicit exits close open longs. A later LONG/REBUY does not automatically cover shorts. |
| **V2 — 1U SAR** | Logged entry units | Explicit exits close open longs; LONG/REBUY covers open shorts before the new long. A SHORT does not automatically close longs. |
| **V3A — Nu Open** | Logged units, with the qualifying compounded-short override | Uses V1's open-book behavior. A qualifying compounded short uses the preceding full-exit unit count for that event only; ordinary longs and subsequent carried shorts are not automatically scaled. |
| **V3B — Nu SAR** | V3A's qualifying sizing override | Uses V2's LONG/REBUY short-cover behavior plus V3A's event-day compounded-short override. |

The direction-following 1U/EOD models are additional paths: one 1U tranche is added for each active ticker at each priced EOD under its carried direction, with the selected variant's exit/SAR/compounding rules. They are not the same thing as a core entry and are not automatically stacked with the core's lots as one account.

For all variants, daily reporting must keep these measures distinct:

- **Realized PnL:** closed-lot PnL at the modeled/user-specified close.
- **Unrealized PnL:** EOD mark-to-market of open lots.
- **Total PnL:** realized + unrealized.
- **Gross open notional:** current open exposure, based on the model's original-notional lot convention.
- **Cumulative gross additions:** historical turnover/activity; not a new-deposit total.
- **Funded cash base:** explicitly stated for a sizing scenario. In the TWM_1M convention it is the all-cash $1,000,000 base, with no leverage, financing, or borrowing.

## 5. TWM_1M series

The **TWM scale family** separates native 1× sizing from the $1M open-notional views. `TWM_1X` is the unscaled current THE WINNING MODEL construction; it is not a $1M-PnL target, a $1M capital account, or a claim that every TWM variant uses that recipe. **TWM_1M** is the normalized sizing family below: each member scales its source path to **$1,000,000 terminal gross open notional**. In this historical window, the $1M terminal open is also the peak open. Scaling is arithmetic and does not establish fill capacity or execution.

| Version | Current construction through 2026-10-26 | Scale | Terminal gross open notional | Terminal modeled PnL | Cumulative additions | Scope |
|---|---|---:|---:|---:|---:|---|
| **TWM_1X** | V3A core + V3A-specific 1U/EOD + 11U/DAY energy per active ticker + combined 11U/DAY DXY (integrated core 1U plus 10U sidecar) | **1.000000×** | **$18,275,000.00** | **$753,361.68** | $21,505,000.00 | Native, unscaled current winner (`core_v3a__1u_v3a__with_oil`); PnL/additions 3.503193%. |
| **TWM_1M_FULL** | Same full winner construction as TWM_1X, scaled to $1M terminal open | 0.054719562244× | $1,000,000.00 | $41,223.62 | $1,176,744.19 | Full current THE WINNING MODEL construction. |
| **TWM_1M_LIGHT** | V3A core + V3A-specific 1U/EOD; retain core DXY; omit the extra 10U/DAY DXY and energy daily-buy sidecar | 0.118976799524× | $1,000,000.00 | $35,015.42 | $1,384,295.06 | Light sidecar scope; still contains core DXY once. |
| **TWM_1M_MAX** | Current-data V3A core + V3A-specific 1U/EOD + 10U/DAY energy, excluding DXY to match its named comparison scope | 0.072753728629× | $1,000,000.00 | $49,267.44 | $1,234,994.54 | Existing no-DXY/10U-energy current-data comparison. It is not an all-sleeve superset of FULL. |

For each TWM_1M row, the $1M open-notional target is treated as a fully funded cash base under the user's debit convention; cumulative additions may exceed it because closed-position cash can be reused. TWM_1X remains at native model sizing and its $18.275M terminal gross open notional is **not** the $1M funded base used by TWM_1M. PnL divided by a funded base is distinct from PnL divided by gross additions. Existing dated outputs and labels control; reruns must use a new version/date when the mark window, event book, or construction changes.

## 6. Proposed TWM_MICRO sizing family: $1K and $10K

**TWM_MICRO** is a smaller-size wrapper around an explicitly selected existing recipe; it changes the target size, not the strategy rules. The two suggested targets are both useful, so the clean-sheet design includes **TWM_1K** and **TWM_10K** as sibling scales rather than forcing a single choice. Here, `1K` and `10K` mean **$1,000 or $10,000 of terminal gross open notional**, respectively—not 1,000/10,000 model units, PnL, or cumulative deposits. One model unit remains 1U = $10,000 entry notional.

The proposed version IDs append the existing scope suffix so FULL/LIGHT/MAX are not conflated. Each small path is the corresponding TWM_1M path uniformly multiplied by **0.001** for TWM_1K or **0.01** for TWM_10K. Values below are cent-rounded arithmetic projections from the Oct. 26 TWM_1M summary, not independently rerun or execution-adjusted results.

| Proposed version | TWM_1M source | Scale relative to source | Terminal open target | Projected PnL | Projected gross additions |
|---|---|---:|---:|---:|---:|
| **TWM_1K_FULL** | TWM_1M_FULL | 0.001× | $1,000.00 | $41.22 | $1,176.74 |
| **TWM_1K_LIGHT** | TWM_1M_LIGHT | 0.001× | $1,000.00 | $35.02 | $1,384.30 |
| **TWM_1K_MAX** | TWM_1M_MAX | 0.001× | $1,000.00 | $49.27 | $1,234.99 |
| **TWM_10K_FULL** | TWM_1M_FULL | 0.01× | $10,000.00 | $412.24 | $11,767.44 |
| **TWM_10K_LIGHT** | TWM_1M_LIGHT | 0.01× | $10,000.00 | $350.15 | $13,842.95 |
| **TWM_10K_MAX** | TWM_1M_MAX | 0.01× | $10,000.00 | $492.67 | $12,349.95 |

Under pure linear scaling, PnL divided by the fully funded $1K/$10K base and PnL divided by gross additions retain the corresponding source ratios (apart from cent rounding). This is a proportional historical paper replay; it does not account for minimum order sizes, whole-share requirements, commissions, spreads, slippage, taxes, or broker constraints. At these small targets, those omitted frictions may materially change real-world results, so the micro table is **not an executable-order specification**.

The optional accumulator toggle can be evaluated alongside either size, but it remains a separate share/U ledger funded only by realized PnL. It is not included in the base target above. If the user wants the $1K/$10K label to cap **all-in** exposure including accumulated holdings, a liquidation/throttling rule must be specified first.

## 7. TWM_20B series and what it does—and does not—mean today

**TWM_20B** is the proposed $20B pool-scale wrapper for the chart-to-model workflow. The repository's current `$20B Paper Portfolio — Units Experiment` is explicitly a **user-estimated hypothetical pool**, not independently verified cash, profit, or equity. It is not currently specified as a `20,000× TWM_1M` clone and must not be scaled that way by implication.

The existing Oct. 26 pool experiment uses current **open gross notional** for selected model-book deductions (not cumulative additions as though all turnover remained invested). It reports a $20,000,000,000 starting pool, $987,245,895.26 of selected model deductions, and $19,012,754,104.74 remaining for a hypothetical 50/50 BRENT/OIL long allocation. The scenario uses $115 BRENT and $101 OIL assumptions, with a lock condition until both supplied EOD marks reach $200. These are dated scenario inputs, not an order, verified balance, or promise of execution. See [`Units Experiment Pool Allocation.md`](Units%20Experiment%20Pool%20Allocation.md).

Before a TWM_20B result is called a model replay, the run sheet must say which capital definition applies:

| TWM_20B sizing mode | Meaning | Current status |
|---|---|---|
| **Pool bridge** | Start from the user-estimated $20B scenario, subtract explicitly selected books by current open gross notional, and report remaining hypothetical pool | Existing historical experiment; deductions and downstream $200 long scenario must be versioned. |
| **Open-notional target** | Treat $20B as the funded gross-open cap/target for a chosen model recipe | Not established by the current pool-bridge report; requires an explicit sizing and concentration rule. |
| **Proportional TWM_1M scaling** | Multiply a $1M path by 20,000 | Not authorized or established. Do not use unless the user explicitly selects this interpretation and accepts the limits of linear scaling. |

Every TWM_20B report must display selected books, gross open notional, cumulative additions, funded-pool assumption, unallocated balance, ticker concentration, any reserve/lock rules, and the explicit scaling definition. The 20B paper pool must never be described as verified capital or as executable capacity.

## 8. Optional realized-PnL accumulator: OFF / ON

The accumulator is a separate, explicit toggle (`ACCUMULATOR=OFF|ON`) applied alongside a named base model. It is designed for share/model-unit control—not to overwrite the base model's dollar PnL.

### OFF (default)

- No profit-funded shares or U-equivalents are bought.
- The base TWM path, scale, dollar PnL, exposure, and cost-basis treatment remain unchanged.

### ON

- Only **realized** PnL is eligible. Unrealized gains are not reinvested.
- Net same-ticker realized PnL is processed at the first supplied TradingView EOD mark strictly after the close/session. A future mark outside the current file is pending; do not infer the next day's mark.
- Equities buy fractional shares of the same ticker. BRENT/OIL remain separate model-U equivalents, never shares. DXY is not turned into an extra share sleeve or counted twice.
- Later realized losses sell the same ticker's accumulated shares/U-equivalents at the next supplied EOD mark. If holdings cannot cover the loss, carry the shortfall against that ticker's future realized profits before new accumulation.
- **No new out-of-pocket cash is contributed by the overlay.** Its accounting cost basis is still nonzero: it is funded from previously realized PnL already present in the base replay. Report both values to avoid calling accounting basis zero.
- The current prototype has been generated for TWM_1M_MAX through 2026-10-26. It does not alter the base TWM_1M_MAX PnL or sizing; its holdings and incremental PnL are separate. Do not silently claim the same accumulator has been implemented for FULL, LIGHT, or TWM_20B.
- The current accumulator is **outside the base open-notional path**. If a strict all-in $1M/$20B gross-exposure cap is required, define whether accumulator market value counts toward that cap and how to throttle or liquidate before enabling it.

## 9. Standard output package and versioning

Each accepted chart batch/model run should produce or update, with a visible as-of date and source revision:

1. normalized event ledger and source/ambiguity notes;
2. ticker/session position audit (entries, exits, direction, units, marks, open lots);
3. daily PnL series split realized/unrealized, gross open notional, and cumulative additions;
4. scenario summary with sizing, scale factor, marks, exclusions, and all-cash base where applicable;
5. accumulator ON/OFF status and, if ON, ticker-level share/U counts, purchase/sale events, loss carry, pending realized PnL, accounting basis, and incremental overlay PnL;
6. a clear statement that model outputs are hypothetical replays, not confirmed executions.

Never overwrite an old result as though it used the same inputs when the chart event book, price-source revision, mark window, sidecar scope, or model rules change. Keep `TWM_1M_FULL`, `TWM_1M_LIGHT`, and `TWM_1M_MAX` names intact; any new TWM_20B sizing rule or V4 chart interpretation receives a versioned specification before it is used.

## 10. Key references

- [`THE ONE MODEL vs THE WINNING MODEL.md`](THE%20ONE%20MODEL%20vs%20THE%20WINNING%20MODEL.md) — current TWM_1M comparisons and construction.
- [`TWM_1M_MAX Realized-PnL Share Accumulator.md`](TWM_1M_MAX%20Realized-PnL%20Share%20Accumulator.md) — current accumulator prototype and ledgers.
- [`Model Calculation Guide.md`](Model%20Calculation%20Guide.md) — detailed core/sidecar replay mechanics.
- [`Units Experiment Pool Allocation.md`](Units%20Experiment%20Pool%20Allocation.md) — historical $20B hypothetical pool bridge.
- [`data/the_one_model_vs_winning_model_v1_summary.json`](data/the_one_model_vs_winning_model_v1_summary.json) and [`data/the_one_model_split_portfolios_v1_summary.json`](data/the_one_model_split_portfolios_v1_summary.json) — current machine-readable comparison definitions and metrics.
