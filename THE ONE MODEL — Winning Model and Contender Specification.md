# THE ONE MODEL — Winning Model and Contender Specification

**Purpose:** define the current candidate universe, the model currently designated **THE WINNING MODEL**, and the change-control rules for future contenders (including a possible V4 series). The winner designation is a dated, replaceable benchmark—not a permanent assertion that one model will always lead.

**Current snapshot:** TradingView-only replay, 37 sessions, 2026-09-03 through 2026-10-26. All numbers below are modeled paper results, not verified brokerage executions, forecasts, or account returns.

## 1. What THE ONE MODEL is

THE ONE MODEL is a **fixed comparison universe of 32 separate portfolios**, not one blended portfolio and not a dynamic selector that automatically invests in whichever line wins. The universe is formed by:

- four independent core position-management variants: V1, V2, V3A, V3B;
- four independent variant-specific 1U/EOD force-model variants: V1, V2, V3A, V3B;
- two energy-sidecar states for every core × force pairing: no additional daily energy sidecar, or an 11U/DAY TradingView energy sidecar per active BRENT and OIL ticker.

That is `4 × 4 × 2 = 32` independently modeled portfolios. Positions, capital, and risk are **not netted** across them.

Every constituent also has the 1U/DAY DXY index-return sleeve integrated in its core **plus** a separate 10U/DAY DXY schedule, or 11U/DAY combined. DXY is an index-return proxy, not a directly priced stock/share. The optional 0.05U DXY schedule is not part of this universe. “No energy sidecar” means no extra daily-buy energy sleeve; it does **not** erase any chart-directed core BRENT/OIL positions.

## 2. Core candidate rule sets

| Core ID | Rule-set name | Position sizing | Close / reversal behavior | Main difference from V3A |
|---|---|---|---|---|
| **V1** | 1U Open | Uses logged entry units | Explicit EXIT/TAKE PROFIT closes open longs. A later LONG/REBUY does not automatically close shorts. A SHORT does not automatically close longs. | Flat/logged sizing; shorts remain open through a later LONG/REBUY. |
| **V2** | 1U SAR | Uses logged entry units | Explicit exits close open longs. LONG/REBUY closes open shorts before opening the new long. A SHORT does not automatically close open longs. | Logged sizing plus asymmetric stop-and-reverse cover rule. |
| **V3A** | Nu Open | Uses logged units except qualifying compounded-short events, which use the preceding full-exit unit count for that event | V1-style open-book treatment; no LONG/REBUY-triggered short cover | Adds the selective compounded-short sizing rule while leaving opposite lots open on later direction changes. |
| **V3B** | Nu SAR | Same qualifying V3A compounded-short event override | V2-style LONG/REBUY short cover; a SHORT does not automatically close open longs | Combines V3A sizing with V2's short-cover rule. |

The standard model unit is **1U = $10,000 entry notional**, not a fixed share count. Long/short PnL is proportional to the price change from each lot's entry basis. Core PnL is realized plus unrealized; current open gross notional and cumulative additions are separately reported.

## 3. Variant-specific 1U/EOD contenders

For each core variant there is a separate 1U/EOD force schedule using that core variant's close/size rules. It adds one 1U tranche per active ticker at each priced EOD; logged entry sizes are generally ignored by this separate daily schedule, subject to the qualifying V3A/V3B compounded-short event-day override. Explicit EXIT/TAKE PROFIT events close open long lots at their logged price but do not by themselves erase the carried direction. Variant-specific force models are **not** the shared-direction force model, and the different force families are not stacked.

The “force variant” is a separate model path paired with the core; matching labels do not mean the two books have become one lot ledger. Thus `V3A Core + V3A 1U/EOD` is one pairing, and `V3A Core + V2 1U/EOD` is a distinct cross-variant contender.

## 4. Current 32-portfolio comparison sheet

Each cell/state below is a separately funded core + variant-specific 1U/EOD pairing. **Every result shown includes the same 11U/DAY combined DXY schedule.** The “with energy” column adds the 11U/DAY energy schedule per active ticker; the “no energy” column omits that extra schedule but retains core oil positions if any. Parentheses show terminal PnL divided by cumulative gross additions—the deployed-notional ratio, **not an account return**.

| Core | 1U/EOD variant | No energy sidecar: terminal PnL (PnL/additions) | With 11U/DAY energy: terminal PnL (PnL/additions) | Current status |
|---|---|---:|---:|---|
| V1 | V1 | $286,800.23 (1.9050%) | $711,719.32 (3.3375%) | Contender |
| V1 | V2 | $287,739.03 (1.9113%) | $712,658.12 (3.3419%) | Contender |
| V1 | V3A | $307,130.78 (2.0279%) | $732,049.87 (3.4184%) | Contender |
| V1 | V3B | $298,420.42 (1.9704%) | $723,339.51 (3.3777%) | Contender |
| V2 | V1 | $284,202.37 (1.8878%) | $709,121.46 (3.3253%) | Contender |
| V2 | V2 | $285,141.17 (1.8940%) | $710,060.26 (3.3297%) | Contender |
| V2 | V3A | $304,532.92 (2.0108%) | $729,452.01 (3.4063%) | Contender |
| V2 | V3B | $295,822.56 (1.9533%) | $720,741.65 (3.3656%) | Contender |
| V3A | V1 | $308,112.04 (2.0344%) | $733,031.13 (3.4230%) | Contender |
| V3A | V2 | $309,050.84 (2.0406%) | $733,969.93 (3.4274%) | Contender |
| **V3A** | **V3A** | $328,442.59 (2.1558%) | **$753,361.68 (3.5032%)** | **Current incumbent: THE WINNING MODEL** |
| V3A | V3B | $319,732.23 (2.0987%) | $744,651.32 (3.4627%) | Contender |
| V3B | V1 | $295,369.08 (1.9503%) | $720,288.17 (3.3635%) | Contender |
| V3B | V2 | $296,307.88 (1.9565%) | $721,226.97 (3.3679%) | Contender |
| V3B | V3A | $315,699.63 (2.0722%) | $740,618.72 (3.4439%) | Contender |
| V3B | V3B | $306,989.27 (2.0150%) | $731,908.36 (3.4034%) | Contender |

The 16 energy-inclusive PnLs exceed their no-energy counterparts by the modeled energy sleeve result. The table is a historical same-period comparison; it does not establish that energy, V3A, or any current leader will lead in a future window.

## 5. Current winner record

As of this snapshot, **THE WINNING MODEL** is exactly:

> **V3A Core + V3A variant-specific 1U/EOD + 11U/DAY TradingView energy per active BRENT/OIL ticker**, with core 1U/DAY DXY plus the separate 10U/DAY DXY schedule (11U/DAY combined). Portfolio ID: `core_v3a__1u_v3a__with_oil`.

| Metric | Current unscaled winner |
|---|---:|
| Terminal modeled PnL | **$753,361.68** |
| Cumulative gross additions | $21,505,000.00 |
| Terminal gross open notional | $18,275,000.00 |
| PnL / cumulative gross additions | 3.503193% |
| Maximum peak-to-trough modeled PnL drawdown | $101,438.78 |
| Evaluation window | 2026-09-03–2026-10-26; 37 sessions |

The designation is **ex post**: the winner is selected from the same 32 portfolios using this period's terminal PnL, so it carries same-period selection/look-ahead bias. It is a current champion label, not a forecast, guarantee, or automatic position switch.

### Keep scale views distinct

- **Unscaled winner:** the current 1× portfolio identified above.
- **Equal-gross comparison:** a separate arithmetic comparison scales that winner by 27.201116× so its cumulative additions match THE ONE MODEL's aggregate additions. This yields $20,492,278.46 modeled PnL on $584,960,000.00 additions and $497,100,395.26 terminal open notional. The ratio remains approximately 3.5032%; the scaling is not proof of executable capacity.
- **TWM_1M_FULL:** a separate all-cash sizing view of the full winning construction to $1,000,000 terminal open notional; current modeled PnL is $41,223.62. Its $1M funded-cash return is distinct from PnL/additions.
- **TWM_1M_MAX:** a separate current-data no-DXY + 10U-energy comparison; do not relabel it as the full 32-universe winner.

## 6. Contender admission and future V4 protocol

A future model may replace the current winner. Keep the old version and its results intact; add the new contender under a new ID and compare it on the same frozen inputs. A proposed V4 does not enter the record as a model until its operational rules are specified.

### Minimum specification required for a new core/force variant

1. Signal interpretation and event mapping: which user-declared/chart-derived events produce LONG, REBUY, SHORT, entry, exit, or partial trim.
2. Sizing: exact unit formula, including what sizes may compound and when the sizing resets.
3. Close/reversal behavior: which event closes long lots, short lots, or neither; FIFO/lot-tag rules for partial exits.
4. Carry rules: what state persists across sessions and how holidays/weekends map to priced sessions.
5. Sidecar definition: DXY inclusion and energy inclusion/unit size, with explicit no-double-count rules.
6. Price source and valid mark window: supplied TradingView file/revision, missing marks, provisional rows, and cutoff date.
7. Accumulator status: OFF/ON, eligible realized events, ticker-specific loss handling, and whether its open value counts toward the model's exposure cap.
8. Version ID and test cases: at least one regression case for each changed rule and a reproducible daily/ticker audit.

### Fair comparison protocol

- Freeze the session window, source events, TradingView marks, and sidecar sizes for all candidates in a comparison batch.
- Show each candidate at native sizing and, where useful, a like-for-like scale (equal cumulative gross additions or $1M terminal open notional). Never compare an unscaled $20B scenario to a $1M replay as if equal-risk.
- Publish terminal PnL, realized/unrealized split, cumulative gross additions, terminal/maximum gross open notional, drawdown, and the denominator used for every percentage. PnL/additions is a deployed-notional ratio; PnL/funded cash is a different measure.
- Identify selection window and whether the candidate is in-sample, out-of-sample, or walk-forward. A winner chosen on a window is not independently validated on that same window.
- Update “current winner” only with a dated selection record: candidate universe, objective/ranking rule, mark revision, date window, metrics, and authorizing decision. If V4 or another contender leads only on a new window, preserve both window-specific results rather than rewriting the old winner history.
- Keep THE ONE's 32 members fixed for each published snapshot. A newly defined V4 family creates a new candidate-universe version; it does not silently replace V1–V3B rows in the old 32-way output.

## 7. Reproducible IDs and source files

Current IDs follow the pattern:

```text
core_<core-id>__1u_<force-id>__<no_oil|with_oil>
```

Examples: `core_v3a__1u_v3a__with_oil` (current winner), `core_v3a__1u_v3a__no_oil`, and `core_v2__1u_v3b__with_oil` (cross-variant contender). “No oil” denotes no extra energy sidecar; all current IDs still include the 10U DXY add-on as defined above.

Machine-readable portfolio metrics and the daily 32-way series are in:

- [`data/the_one_model_split_portfolios_v1_summary.json`](data/the_one_model_split_portfolios_v1_summary.json)
- [`data/the_one_model_split_portfolios_v1.csv`](data/the_one_model_split_portfolios_v1.csv)
- [`data/the_one_model_energy_11u_sidecar_daily_v1.csv`](data/the_one_model_energy_11u_sidecar_daily_v1.csv)
- [`THE ONE MODEL vs THE WINNING MODEL.md`](THE%20ONE%20MODEL%20vs%20THE%20WINNING%20MODEL.md)
- [`Model Calculation Guide.md`](Model%20Calculation%20Guide.md)

The current 32-way aggregate has $16,457,691.52 terminal modeled PnL, $584,960,000.00 cumulative gross additions, $478,800,000.00 gross open notional, and 2.813473% PnL/additions. Those totals sum 32 separately modeled books; they are not one netted account or a promised return.
