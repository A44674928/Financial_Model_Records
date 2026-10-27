# THE ONE MODEL (TOM) — Clean-Sheet Specification

**Purpose:** define TOM as an auditable family of independent chart-derived paper-model portfolios, its current 32-member universe, its current same-window winner, and clearly distinguished $1K/$10K sizing views.

**Snapshot:** current supplied TradingView replay from **2026-09-03 through 2026-10-26** (37 sessions). All results are hypothetical model output, not verified brokerage executions, account returns, forecasts, or investment advice.

## 1. Identity and boundaries

**THE ONE MODEL (TOM)** is the name of a fixed comparison universe of **32 separately modeled portfolios**. It is not one merged account, not a netted basket, and not an automatic system that moves capital to whichever line currently leads. Each portfolio retains its own core rules, its own variant-specific 1U/EOD schedule, its sidecar setting, and—if ever enabled—its own accumulator ledger.

TOM is built from the user's chart/trade-event interpretation and supplied marks. The chart-to-model intake process is human-in-the-loop: the user declares position/direction and the assistant normalizes confirmed events; ambiguous chart content is not treated as an implicit trade. Preserve user-provided categories (including ATS/manual), quantities, prices, and timing; do not infer fills or represent modeled events as verified executions. Valuation marks are TradingView-only: never substitute a legacy price source. Use **DXY**, not “DS,” and do not duplicate or double-count its sleeves. See [TWM Chart-to-Model Series — Clean-Sheet Specification](TWM%20Chart-to-Model%20Series%20%E2%80%94%20Clean-Sheet%20Specification.md) for the full chart-post template and event-intake rules. TOM's model rules and outputs are specific to its 32-portfolio universe.

**TOM is distinct from both:**

- **THE WINNING MODEL**, which currently means the single highest terminal-PnL member selected ex post from this 32-way universe for a stated date window; it is a replaceable label, not another name for all 32 portfolios.
- **TWM_1M / TWM_20B / TWM_MICRO**, which are separate sizing/pool wrappers and may use one selected model recipe. They do not replace or redefine TOM's 32 members.

## 2. Portfolio construction

TOM contains every combination of:

1. **Four core variants:** V1, V2, V3A, V3B.
2. **Four variant-specific 1U/EOD force variants:** V1, V2, V3A, V3B.
3. **Two energy-sidecar states:** no extra daily-buy energy sidecar, or 11U/DAY per active BRENT and OIL ticker.

Thus: `4 core variants × 4 force variants × 2 energy states = 32 independent portfolios`.

All 32 also contain core's integrated chart-directed **1U/DAY DXY** index-return sleeve plus the separate **10U/DAY DXY** schedule, for **11U/DAY combined DXY exposure**. DXY is modeled as an index-return proxy, not shares or a direct-price contract. The 0.05U DXY alternative is excluded. “No energy sidecar” only omits the additional daily energy schedule; it does not remove chart-directed core BRENT/OIL positions. Do not double-count chart-opened core positions or integrated DXY.

## 3. Core and 1U/EOD rulebook

The base unit convention is **1U = $10,000 entry notional**. A unit is a notional sizing measure, not a fixed quantity of shares. Long and short lot PnL is proportional to price movement from the logged entry basis, marked with the supplied TradingView EOD series.

| Variant | Core rule | Variant-specific 1U/EOD rule |
|---|---|---|
| **V1 — 1U Open** | Uses logged entry units; explicit EXIT/TAKE PROFIT closes open longs; later LONG/REBUY does not automatically cover shorts; SHORT does not automatically close longs. | Adds 1U per active ticker at each priced EOD, applying V1 close handling. |
| **V2 — 1U SAR** | Uses logged entry units; explicit exits close longs; LONG/REBUY covers shorts before the new long; SHORT does not automatically close longs. | Adds 1U per active ticker at each priced EOD, applying V2 LONG/REBUY short cover. |
| **V3A — Nu Open** | Uses logged units, except qualifying compounded-short events use the preceding full-exit unit count for that event only; V1-style open-book reversals. | Adds the daily 1U tranche, except a qualifying compounded-short event-day tranche can use the preceding full-exit unit count; subsequent carried days return to 1U. |
| **V3B — Nu SAR** | V3A's selective compounded-short size rule plus V2's LONG/REBUY short cover. | Applies the V3B core close/size rules to the 1U/EOD schedule. |

The 1U/EOD schedule is a separate modeled path paired with core, not the same core lot ledger. EXIT/TAKE PROFIT closes do not automatically clear the carried direction; direction-bearing LONG/SHORT/REBUY signals map to the first priced session on or after the event date. Model events, user-reported inputs, chart interpretation, and supplied EOD marks remain separately identified.

## 4. Sidecar rules

- **DXY:** every TOM constituent gets the integrated 1U/DAY core sleeve and a separate 10U/DAY sidecar. Combined 11U/DAY exposure appears once per constituent. Do not add another DXY row or the 0.05U alternative.
- **Energy:** 16 constituents have the 11U/DAY TradingView buy schedule per active BRENT/OIL ticker; the other 16 omit that extra schedule. The schedule is a distinct long daily-buy sleeve; it does not close the chart-opened core lots or substitute for them.
- **No sidecar netting:** each of the 32 books is independently funded/modelled. Aggregate output is an arithmetic sum of independent paths, not a single account where positions, risk, margin, or capital net against each other.

## 5. Current 32-member scorecard

Each row represents two members: one without the extra energy sidecar and one with the 11U/DAY energy sidecar. All rows include the same 11U/DAY combined DXY schedule. Values are current terminal modeled PnL and PnL divided by cumulative gross additions; the percentage is a **deployed-notional ratio, not an account return**.

| Core | 1U/EOD | No extra energy: PnL (PnL/additions) | With 11U/DAY energy: PnL (PnL/additions) |
|---|---|---:|---:|
| V1 | V1 | $286,800.23 (1.9050%) | $711,719.32 (3.3375%) |
| V1 | V2 | $287,739.03 (1.9113%) | $712,658.12 (3.3419%) |
| V1 | V3A | $307,130.78 (2.0279%) | $732,049.87 (3.4184%) |
| V1 | V3B | $298,420.42 (1.9704%) | $723,339.51 (3.3777%) |
| V2 | V1 | $284,202.37 (1.8878%) | $709,121.46 (3.3253%) |
| V2 | V2 | $285,141.17 (1.8940%) | $710,060.26 (3.3297%) |
| V2 | V3A | $304,532.92 (2.0108%) | $729,452.01 (3.4063%) |
| V2 | V3B | $295,822.56 (1.9533%) | $720,741.65 (3.3656%) |
| V3A | V1 | $308,112.04 (2.0344%) | $733,031.13 (3.4230%) |
| V3A | V2 | $309,050.84 (2.0406%) | $733,969.93 (3.4274%) |
| **V3A** | **V3A** | $328,442.59 (2.1558%) | **$753,361.68 (3.5032%)** |
| V3A | V3B | $319,732.23 (2.0987%) | $744,651.32 (3.4627%) |
| V3B | V1 | $295,369.08 (1.9503%) | $720,288.17 (3.3635%) |
| V3B | V2 | $296,307.88 (1.9565%) | $721,226.97 (3.3679%) |
| V3B | V3A | $315,699.63 (2.0722%) | $740,618.72 (3.4439%) |
| V3B | V3B | $306,989.27 (2.0150%) | $731,908.36 (3.4034%) |

Current aggregate across 32 separately modeled portfolios: **$16,457,691.52 terminal PnL**, **$584,960,000.00 cumulative gross additions**, **$478,800,000.00 terminal gross open notional**, and **2.813473% PnL/additions**. These totals are not netted exposure or a promised account return.

## 6. Current THE WINNING MODEL selection

For this 37-session snapshot, the single highest terminal PnL member is:

> **V3A Core + V3A-specific 1U/EOD + 11U/DAY energy per active ticker**, including 11U/DAY combined DXY. ID: `core_v3a__1u_v3a__with_oil`.

| Metric | Snapshot result |
|---|---:|
| Terminal PnL | $753,361.68 |
| Cumulative gross additions | $21,505,000.00 |
| Terminal gross open notional | $18,275,000.00 |
| PnL/additions | 3.503193% |
| Peak-to-trough PnL drawdown | $101,438.78 |

This is a same-window, ex-post selection and therefore carries selection/look-ahead bias. Preserve the winner designation with its date window, rule version, and mark revision. A future model series such as V4 may take the lead; it should be added as a versioned candidate and compared under frozen inputs, not substituted into historical results.

## 7. TOM_1K and TOM_10K: define what the target applies to

Unlike TWM_1K/10K, TOM contains **32 independent books**. Therefore “TOM_1K” is ambiguous unless the target says whether it applies to the 32-book aggregate or to each member. The clean sheet preserves both choices rather than silently selecting one.

### Mode A — one target for the entire TOM aggregate

Apply one common scale factor to all 32 positions, preserving the current proportional weights. This makes the **sum** of terminal gross open notional $1,000 or $10,000:

| Proposed aggregate scale | Common factor vs native TOM | Aggregate terminal open | Projected aggregate PnL | Projected additions | PnL/additions |
|---|---:|---:|---:|---:|---:|
| **TOM_1K_TOTAL** | 0.000002088554720134× | $1,000.00 | $34.37 | $1,221.72 | 2.813473% |
| **TOM_10K_TOTAL** | 0.000020885547201337× | $10,000.00 | $343.73 | $12,217.21 | 2.813473% |

These are native aggregate TOM results multiplied by the same factor. Each constituent's open notional becomes a small fraction of the total target; this is not $1K/$10K per constituent.

### Mode B — target each of the 32 independent members

Alternatively, scale each TOM member separately to **$1,000 or $10,000 terminal open notional per book**. That produces aggregate terminal open notional of **$32,000 or $320,000**, respectively.

| Proposed per-member scale | Terminal open per member | Aggregate terminal open | Projected sum of member PnL | Projected sum of additions |
|---|---:|---:|---:|---:|
| **TOM_1K_EACH** | $1,000.00 | $32,000.00 | $1,050.87 | $39,424.47 |
| **TOM_10K_EACH** | $10,000.00 | $320,000.00 | $10,508.70 | $394,244.73 |

Each member gets its own scale factor because native open notionals differ. These figures are arithmetic projections from the current portfolio summary, rounded to cents—not a new event-by-event model execution. Since per-member scaling changes each member by a different factor, it must not replace the native-dollar selection criterion or be used to silently rename the current winner. Report the target convention (`TOTAL` or `EACH`) in every TOM micro output.

Both micro modes assume fully funded cash/debit positions, no borrowing, and no leverage. They do not model commissions, minimum order values, whole-share constraints, spreads, taxes, market impact, or broker-specific fractional-share rules. At these scales the omitted frictions can materially affect real results; the micro outputs are analytical paper views, not execution instructions.

## 8. Optional accumulator — proposed TOM behavior

Accumulator is **OFF by default** for TOM and is not currently implemented as a 32-way TOM companion. If enabled in a future version, it must be tracked independently for every `(portfolio_id, ticker)` pair—never pool gains or losses across the 32 members.

- Only realized PnL funds purchases; unrealized gains are not reinvested.
- Use the first supplied TradingView EOD mark strictly after realization. Equities become fractional same-ticker shares; BRENT/OIL remain separate model-U equivalents; DXY is not duplicated.
- Later realized losses sell same-ticker accumulated shares/units at the next supplied mark; carry any shortfall against that same portfolio/ticker's future realized profits before buying more.
- Show pending realized PnL, purchases/sales, shares/U, accounting basis, incremental overlay PnL, and additional out-of-pocket cash separately. Profit-funded holdings have nonzero accounting basis even when new outside cash contributed is $0.
- Specify whether accumulator holdings count toward a $1K/$10K target or are an overlay outside the base target before enabling it. This cap policy is not yet frozen for TOM.

## 9. Reporting, validation, and versioning

Each TOM snapshot must record:

1. user-confirmed event set and any chart interpretation/overrides;
2. TradingView mark files, source revisions, date window, missing/provisional mark treatment;
3. core ID, force ID, energy state, DXY scope, scale mode, and all scale factors;
4. per-member realized/unrealized/total PnL, cumulative additions, terminal/maximum open notional, and drawdown;
5. aggregate arithmetic, with no cross-book netting;
6. accumulator OFF/ON state and, if enabled, independent member/ticker ledgers;
7. whether the result is native, TOM_1K_TOTAL, TOM_10K_TOTAL, TOM_1K_EACH, or TOM_10K_EACH.

Keep source input files and older snapshots. Adding a new core/force family such as V4 creates a new candidate-universe version; it does not overwrite V1–V3B results or their 32-member snapshot. Preserve the same-period selection-bias warning whenever THE WINNING MODEL is selected from the evaluated sample.

## 10. Source references

- [THE ONE MODEL vs THE WINNING MODEL](THE%20ONE%20MODEL%20vs%20THE%20WINNING%20MODEL.md) — current comparison and TWM_1M scale views.
- [THE ONE MODEL winner/contender specification](THE%20ONE%20MODEL%20%E2%80%94%20Winning%20Model%20and%20Contender%20Specification.md) — detailed core/force candidate registry and V4 protocol.
- [TWM chart-to-model specification](TWM%20Chart-to-Model%20Series%20%E2%80%94%20Clean-Sheet%20Specification.md) — chart-intake contract and optional share/unit accumulator rules.
- [`data/the_one_model_split_portfolios_v1_summary.json`](data/the_one_model_split_portfolios_v1_summary.json) — current individual portfolio metrics, selected winner, and aggregate summary.
- [`data/the_one_model_split_portfolios_v1.csv`](data/the_one_model_split_portfolios_v1.csv) — daily data for all 32 TOM members.
- [`data/the_one_model_energy_11u_sidecar_daily_v1.csv`](data/the_one_model_energy_11u_sidecar_daily_v1.csv) — derived 11U energy schedule used in the 16 energy-inclusive members.
