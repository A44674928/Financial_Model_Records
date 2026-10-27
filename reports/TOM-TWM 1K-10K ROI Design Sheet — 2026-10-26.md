# TOM / TWM 1K–10K ROI Design Sheet — 2026-10-26

**Snapshot:** supplied TradingView marks through **2026-10-26**, 37 sessions from 2026-09-03. LMT and BRENT-only designs have later starts; their actual active-mark windows are shown. This is a sizing/design sheet for historical paper-model replays—not verified fills, forecasts, or investment advice.

## Sizing contract

- A **$1K or $10K target means maximum gross open notional for a single-book design**, treated as its fully funded cash/debit base. There is no leverage or borrowing. In this sample, each listed single-book model's maximum gross open notional occurs at its endpoint.
- Each projection applies one constant scale factor: `target gross open notional ÷ native maximum gross open notional`. Projected PnL, additions, and drawdown scale linearly; percentage ratios do not.
- **PnL / additions** is the deployed-notional ratio. **PnL / funded gross-open base** is a separate return view. Do not call them interchangeable.
- For TOM's 32 books, `TOTAL` means $1K/$10K summed across all 32; `EACH` means that target per member, so aggregate open notional is 32× the per-member amount. `EACH` scales each portfolio separately and is not a uniform scaling of the aggregate.
- Values are projections from the supplied replay, rounded to cents. They are not rerun trades or execution lots. Costs, minimum order sizes, taxes, spreads, slippage, capacity, and fractional-share/broker rules are not modeled.

## Single-book 1K / 10K designs

Each cell under a target shows **modeled PnL / gross additions / historical maximum drawdown** at that fully funded open-notional target.

| Design ID and construction | Active window | Native PnL / additions / max open | PnL / additions | PnL / funded base | **$1K target:** PnL / additions / MDD | **$10K target:** PnL / additions / MDD |
|---|---|---:|---:|---:|---:|---:|
| **V3A_CORE_ONLY** — V3A core book alone; retains integrated chart-directed 1U/DAY DXY; excludes the separate 10U/DAY DXY sidecar, the variant-specific 1U/EOD force book, and energy daily-buy sidecar | 37 sessions | $135,836.06 / $4,675,000 / $2,955,000 | 2.9056% | 4.5968% | $45.97 / $1,582.06 / $4.48 | $459.68 / $15,820.64 / $44.85 |
| **V3A_CORE_ONLY_NO_DXY** — same V3A core, but also remove the integrated 1U/DAY DXY sleeve; arithmetic counterfactual, not the canonical core definition | 37 sessions | $132,422.26 / $4,315,000 / $2,595,000 | 3.0689% | 5.1030% | $51.03 / $1,662.81 / $4.99 | $510.30 / $16,628.13 / $49.94 |
| **V3A_V3A_FORCE_11U_NO_DXY** — V3A core + V3A-specific 1U/EOD force + 11U/DAY energy per active ticker; removes both DXY components (integrated core 1U and separate 10U) | 37 sessions | $715,809.91 / $17,545,000 / $14,315,000 | 4.0799% | 5.0004% | $50.00 / $1,225.64 / $7.37 | $500.04 / $12,256.37 / $73.73 |
| **LMT_CORE_ONLY** — isolate the existing four-lot LMT core contribution; no DXY, other tickers, force, or energy overlay | 2026-10-05–2026-10-26; 16 active sessions | $9,402.64 / $40,000 / $40,000 | **23.5066%** | **23.5066%** | **$235.07 / $1,000.00 / $11.70** | **$2,350.66 / $10,000.00 / $116.99** |
| **BRENT_11U_ONLY** — isolate the 11U/DAY TradingView BRENT daily-buy sidecar; no core, DXY, force, or OIL | 2026-09-23–2026-10-26; 24 active marks | $201,488.22 / $2,640,000 / $2,640,000 | 7.6321% | 7.6321% | $76.32 / $1,000.00 / $17.62 | $763.21 / $10,000.00 / $176.21 |
| **TWM_1M_FULL** — V3A/V3A winner construction, 11U/DAY energy + combined 11U/DAY DXY | 37 sessions | $41,223.62 / $1,176,744.19 / $1,000,000 | 3.5032% | 4.1224% | $41.22 / $1,176.74 / $5.55 | $412.24 / $11,767.44 / $55.51 |
| **TWM_1M_LIGHT** — V3A core + V3A force; retains core chart DXY, excludes extra 10U DXY and energy sidecar | 37 sessions | $35,015.42 / $1,384,295.06 / $1,000,000 | 2.5295% | 3.5015% | $35.02 / $1,384.30 / $3.31 | $350.15 / $13,842.95 / $33.14 |
| **TWM_1M_MAX** — current-data no-DXY V3A/V3A + 10U/DAY energy construction | 37 sessions | $49,267.44 / $1,234,994.54 / $1,000,000 | 3.9893% | 4.9267% | $49.27 / $1,234.99 / $6.91 | $492.67 / $12,349.95 / $69.07 |

### V3A by itself: what the row means

Yes—**V3A core-only is included as its own design**, separate from the current V3A Core + V3A 1U/EOD force + energy winner. Under the established core definition, V3A core-only still has its integrated chart-directed 1U/DAY DXY sleeve. To answer the DXY carve-out question cleanly, the adjacent `V3A_CORE_ONLY_NO_DXY` row removes that sleeve explicitly. Neither row adds the separate 10U/DAY DXY schedule, energy daily-buy sidecar, or force model.

The core-only standard V3A view therefore returns 4.5968% on the assumed funded base; its DXY-free counterfactual returns 5.1030%. The latter has a somewhat higher additions ratio too, but it is a distinct scope and must not be described as the unchanged canonical V3A core.

## Optional per-ticker sleeve-based investing design

A user may select one or more ticker sleeves instead of funding a whole multi-ticker core or TOM/TWM composite. A sleeve is keyed by `(model family, variant, ticker, sidecar scope)`—for example, `CORE_V3A / INTC / no extra sidecars`. Each sleeve keeps its own confirmed trade events, realized and unrealized PnL, gross additions, open lots, drawdown, marks, and scale factor. A sleeve is not an inferred live order or a substitute for the underlying all-ticker model record.

### Allocation modes

- **`TICKER_EACH`** — assign the $1K or $10K maximum-gross-open target to each selected ticker/variant sleeve independently. With N selected sleeves, aggregate funded open notional is N × the per-sleeve target. Each sleeve uses its own scale factor.
- **`TICKER_TOTAL`** — cap the combined selected sleeves at $1K or $10K maximum gross open. The allocation weights must be supplied and recorded. Do not silently pick equal weights; an equal-weight proposal, if requested, is a separately labeled assumption.

For either mode, display both PnL/additions and PnL/funded max-open return. Keep additions and funded cash denominators distinct; do not pool or net risk across tickers. Any reinvestment or transfer of realized PnL between sleeves would require a separate, explicit cash-flow rule.

### INTC example: standalone core ticker sleeve, Oct. 26 supplied mark

INTC's supplied TradingView EOD mark is **$90.47 on 2026-10-26**. Across the four core variants, the INTC book has **9 open units / $90,000 maximum gross open notional**. Native additions differ by variant ($160K for V1/V2; $200K for V3A/V3B), because previously closed lots remain in cumulative additions. The 1K and 10K projections uniformly scale each variant's complete INTC-only history by **1/90** and **1/9**, respectively.

| Sleeve ID | Native realized / unrealized / total PnL | Native additions / max open | PnL / additions | PnL / funded max open | **$1K target:** PnL / additions / MDD | **$10K target:** PnL / additions / MDD |
|---|---:|---:|---:|---:|---:|---:|
| **INTC_CORE_V1** | $16,462.48 / −$2,239.77 / $14,222.71 | $160,000 / $90,000 | 8.8892% | 15.8030% | $158.03 / $1,777.78 / $79.36 | $1,580.30 / $17,777.78 / $793.57 |
| **INTC_CORE_V2** | $13,623.38 / −$2,239.77 / $11,383.61 | $160,000 / $90,000 | 7.1148% | 12.6485% | $126.48 / $1,777.78 / $79.36 | $1,264.85 / $17,777.78 / $793.57 |
| **INTC_CORE_V3A** | $28,911.54 / −$2,239.77 / **$26,671.77** | $200,000 / $90,000 | **13.3359%** | **29.6353%** | **$296.35 / $2,222.22 / $79.36** | **$2,963.53 / $22,222.22 / $793.57** |
| **INTC_CORE_V3B** | $20,675.54 / −$2,239.77 / $18,435.77 | $200,000 / $90,000 | 9.2179% | 20.4842% | $204.84 / $2,222.22 / $79.36 | $2,048.42 / $22,222.22 / $793.57 |

The projected percentages are unchanged by uniform scaling. For example, INTC V3A's **13.3359%** is PnL divided by $200K cumulative additions; **29.6353%** is PnL divided by the $90K maximum-open funded base. Its $1K sleeve projects $296.35 PnL on $2,222.22 cumulative additions, not $296.35 on $1K of additions. The historical INTC maximum peak-to-trough drawdown is $7,142.13 natively, shown scaled in the target columns.

### Sleeve bookkeeping and limits

- Keep ticker, variant, direction, entry/exit type, supplied quantity/price/timing, and ATS/manual categories intact. Do not infer fills or trades from screenshots; use the established user-confirmed event ledger.
- Use TradingView-only valuation marks and the supplied session calendar. Keep legacy marks out. DXY remains a separate index-return sleeve—not an equity ticker—and must not be duplicated. BRENT/OIL sidecars remain separate U-equivalents, never shares.
- A selected ticker sleeve is a historical research view. Selecting INTC V3A from a same-window comparison is subject to the same ex-post selection bias as selecting LMT or any other best-performing ticker. This sheet does not enable automatic ticker selection, broker execution, or cross-sleeve cash transfers.
- Dollar scaling is mathematical. Whole-share/fractional-share rules, costs, slippage, taxes, spreads, market impact, and capacity remain unmodeled.

## TOM aggregate designs: TOTAL vs EACH

All 32 TOM members are independent books; no positions, risk, or capital are netted. Native TOM currently includes the combined 11U/DAY DXY sleeve in every member. The no-DXY rows are counterfactual arithmetic carve-outs that remove both the integrated 1U/DAY core DXY and separate 10U/DAY DXY sleeve.

| TOM design | Target convention | Aggregate maximum open / funded base | **$1K setting:** PnL / additions / MDD | **$10K setting:** PnL / additions / MDD | PnL / additions | PnL / funded base |
|---|---|---:|---:|---:|---:|---:|
| **TOM_CURRENT_TOTAL** | $1K or $10K over all 32, one common factor | $1,000 / $10,000 | $34.37 / $1,221.72 / $3.73 | $343.73 / $12,217.21 / $37.31 | 2.8135% | 3.4373% |
| **TOM_NO_DXY_TOTAL** | $1K or $10K over all 32, one common factor; DXY removed | $1,000 / $10,000 | $43.33 / $1,301.52 / $5.40 | $433.31 / $13,015.22 / $53.97 | 3.3293% | 4.3331% |
| **TOM_CURRENT_EACH** | $1K or $10K terminal open per member; per-book factors differ | $32,000 / $320,000 | $1,050.87 / $39,424.47 / $106.62 | $10,508.70 / $394,244.73 / $1,066.22 | 2.6655% | 3.2840% |

`TOM_CURRENT_EACH`'s **$1K setting** means $1,000 per each of 32 members ($32,000 aggregate); its **$10K setting** means $10,000 per each ($320,000 aggregate). The listed aggregate PnL and additions are sums of the independently scaled members. Because the scale factors differ, the resulting ratio is not the native aggregate TOM ratio and does not change which member is the native-dollar winner.

## Scaling factors

These constant factors reproduce the table projections and scale the full historical path. For target-based TOM modes, the factor is applied to the relevant single book or aggregate; `EACH` uses a different factor for every one of the 32 members.

| Design | Factor for $1K target | Factor for $10K target |
|---|---:|---:|
| V3A_CORE_ONLY | 0.000338409475× | 0.003384094755× |
| V3A_CORE_ONLY_NO_DXY | 0.000385356455× | 0.003853564547× |
| V3A_V3A_FORCE_11U_NO_DXY | 0.000069856794× | 0.000698567936× |
| LMT_CORE_ONLY | 0.025000000× | 0.250000000× |
| BRENT_11U_ONLY | 0.000378788× | 0.003787879× |
| TOM_CURRENT_TOTAL | 0.000002088555× | 0.000020885547× |
| TOM_NO_DXY_TOTAL | 0.000002840264× | 0.000028402636× |
| TWM_1M_FULL / LIGHT / MAX | 0.001000000× | 0.010000000× |

## Guardrails and interpretation

- The **23.5066% LMT** result is the highest single-ticker core contribution found in this in-sample screen, but it covers only 16 active marks and is a one-stock concentration. Scaling it to $1K/$10K does not make the same past return likely or guarantee execution.
- The **7.6321% BRENT** result is a separate buy-only sidecar with a 24-mark window. It is not a full portfolio and does not include a modeled exit rule.
- DXY made positive modeled dollars in the replay; its low return per added dollar diluted the percentage when combined with more efficient sleeves. Removing it is a counterfactual sensitivity, not a general conclusion that DXY should always be excluded.
- All PnL remains clearly distinguished as realized or mark-to-market where the source exposes that split; the daily-buy energy sleeve's reported PnL is unrealized at supplied marks. No missing marks are invented, no legacy prices substituted, and no image-derived trades or fills are inferred.
- V3A core, V3A core without DXY, DXY-free V3A/V3A + 11U energy, and one-ticker sleeves are **research designs**, not replacements for the current TOM/TWM scorecards or winner. The same-window winner/ticker selection bias remains.

## Source data

- [`data/model_performance_summary.json`](../data/model_performance_summary.json), [`data/model_performance_daily.csv`](../data/model_performance_daily.csv), [`data/model_performance_tickers.csv`](../data/model_performance_tickers.csv), and [`data/core_portfolio_asset_breakdown_20261026.csv`](../data/core_portfolio_asset_breakdown_20261026.csv): core-model PnL, additions, ticker contributions, realized/unrealized split, and current exposure.
- [`data/the_one_model_split_portfolios_v1_summary.json`](../data/the_one_model_split_portfolios_v1_summary.json) and [`data/the_one_model_split_portfolios_v1.csv`](../data/the_one_model_split_portfolios_v1.csv): all 32 TOM members and sidecar paths.
- [`data/the_one_model_energy_11u_sidecar_daily_v1.csv`](../data/the_one_model_energy_11u_sidecar_daily_v1.csv): BRENT/OIL 11U sidecar rows with TradingView marks.
- [`data/the_one_model_vs_winning_model_v1_summary.json`](../data/the_one_model_vs_winning_model_v1_summary.json): existing TWM_1M_FULL, TWM_1M_LIGHT, and TWM_1M_MAX.
- [TOM clean-sheet specification](../THE%20ONE%20MODEL%20%28TOM%29%20%E2%80%94%20Clean-Sheet%20Specification.md) defines TOM's `TOTAL`/`EACH` labels; [TWM chart-to-model specification](../TWM%20Chart-to-Model%20Series%20%E2%80%94%20Clean-Sheet%20Specification.md) defines TWM sizing boundaries.
- [TOM / TWM ROI Frontier — 2026-10-26](TOM-TWM%20ROI%20Frontier%20%E2%80%94%202026-10-26.md) documents the maximum historical single-ticker carve-out and the DXY-free full-model comparisons.
