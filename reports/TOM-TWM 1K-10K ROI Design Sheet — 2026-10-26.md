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

- [`data/model_performance_summary.json`](../data/model_performance_summary.json), [`data/model_performance_daily.csv`](../data/model_performance_daily.csv), [`data/model_performance_tickers.csv`](../data/model_performance_tickers.csv): core-model PnL, additions, and ticker contributions.
- [`data/the_one_model_split_portfolios_v1_summary.json`](../data/the_one_model_split_portfolios_v1_summary.json) and [`data/the_one_model_split_portfolios_v1.csv`](../data/the_one_model_split_portfolios_v1.csv): all 32 TOM members and sidecar paths.
- [`data/the_one_model_energy_11u_sidecar_daily_v1.csv`](../data/the_one_model_energy_11u_sidecar_daily_v1.csv): BRENT/OIL 11U sidecar rows with TradingView marks.
- [`data/the_one_model_vs_winning_model_v1_summary.json`](../data/the_one_model_vs_winning_model_v1_summary.json): existing TWM_1M_FULL, TWM_1M_LIGHT, and TWM_1M_MAX.
- [TOM clean-sheet specification](../THE%20ONE%20MODEL%20%28TOM%29%20%E2%80%94%20Clean-Sheet%20Specification.md) defines TOM's `TOTAL`/`EACH` labels; [TWM chart-to-model specification](../TWM%20Chart-to-Model%20Series%20%E2%80%94%20Clean-Sheet%20Specification.md) defines TWM sizing boundaries.
- [TOM / TWM ROI Frontier — 2026-10-26](TOM-TWM%20ROI%20Frontier%20%E2%80%94%202026-10-26.md) documents the maximum historical single-ticker carve-out and the DXY-free full-model comparisons.
