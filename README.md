# Paper Trades — Repository Guide

This repository contains the Fall (Arizona) 2026 paper-trading ledger, model analysis, source records, and supporting research.

> **DEFAULT TRADINGVIEW BLOCK — effective October 20, 2026.** Post-cutoff TradingView inputs remain blocked for all active calculations except one user-authorized, versioned Oil mark-forward: existing aligned EOD marks through October 26, 2026, with trade events still cut off at October 19. This scoped exception does not authorize post-cutoff trade events, under-duress scenario positions, or updates to any other model. See the [TradingView policy](reports/TradingView%20Post-October%2019%20Block%20Policy.md), [Oil Portfolio update](reports/Oil%20Portfolio%20%E2%80%94%202026-10-26%20Update.md), and [exception index](data/tradingview_post_cutoff_exceptions_v1.csv).

The historical model comparison was built from the supplied TradingView benchmark through the **October 26, 2026** EOD close: 31 direct-price core symbols plus an integrated 1U/DAY/DXY index-return sleeve; BTC/ETH remain pending recalibration. Those post-cutoff inputs and dependent outputs are now policy exceptions, not current approved inputs. Four separate manual 10U LONG oil replenishment entries (two per ticker) are logged on Oct. 25: the $115.792 BRENT/$101.74 OIL lots use the user-recalled 17:20–17:25 MST window, modeled at a 17:22 MST midpoint, and the $114.80 BRENT/$101.00 OIL lots use an approximate 20:00 MST timestamp per the user's recollection. At 20:35 MST, additional Weekend Oil buys of 35U BRENT at $114.627 and 34U OIL at $100.74 are modeled simultaneously with closing the separate 10U SHORT lots. The 35U/34U LONG lots count toward weekly buy supply; the short closures do not. Against the 65U BRENT + 66U OIL existing all-core long exposure after the modeled short closes, they bring the total to 100U per ticker, 200U combined ($2,000,000 fixed-unit notional). These post-cutoff events are excluded from current PnL pending later EOD marks. The short exits override SAR only for the tagged shorts; prices/timing are hypothetical model assumptions, not verified executions. THE ONE MODEL adds the 10U/DAY DXY schedule to each of its 32 independent portfolios, for 11U/DAY combined DXY exposure; its 16 energy-inclusive portfolios use 11U/DAY per active BRENT and OIL ticker, matching that combined currency size. The 16 no-energy variants remain in the split. The 0.05U DXY schedule remains an alternative. Other strategy-comparison scopes are unchanged. Legacy whole-portfolio DXY/yield views are explicitly historical and retain their previous benchmark.

## Start here

- [TradingView PaperTrading Block Policy](reports/TradingView%20Post-October%2019%20Block%20Policy.md) — strict all-source cutoff from 2026-10-20, legacy exception index, and no-recompute rule.
- [Model Performance Comparison](Model%20Performance%20Comparison.md) — historical four-model daily and intraday comparison; its post-cutoff TradingView-derived inputs are flagged pending review.
- [Core Portfolio Asset Breakdown](Core%20Portfolio%20Asset%20Breakdown.md) — open long/short exposures, asset concentration, and PnL by ticker across the four core variants.
- [THE ONE MODEL vs THE WINNING MODEL](THE%20ONE%20MODEL%20vs%20THE%20WINNING%20MODEL.md) — equal-gross comparison of the 32-portfolio aggregate and its ex-post top terminal-PnL constituent.
- [TWM Chart-to-Model Series — Clean-Sheet Specification](TWM%20Chart-to-Model%20Series%20%E2%80%94%20Clean-Sheet%20Specification.md) — private-chart intake, TWM_1M/TWM_20B boundaries, and optional accumulator rules.
- [THE ONE MODEL — Winning Model and Contender Specification](THE%20ONE%20MODEL%20%E2%80%94%20Winning%20Model%20and%20Contender%20Specification.md) — current champion, all 32 candidates, and how future models such as V4 can contend.
- [THE ONE MODEL (TOM) — Clean-Sheet Specification](THE%20ONE%20MODEL%20%28TOM%29%20%E2%80%94%20Clean-Sheet%20Specification.md) — TOM construction, winner rules, and aggregate vs per-constituent $1K/$10K sizing.
- [TOM / TWM 1K–10K ROI Design Sheet — 2026-10-26](reports/TOM-TWM%201K-10K%20ROI%20Design%20Sheet%20%E2%80%94%202026-10-26.md) — $1K/$10K projections for V3A core-only, DXY-free, LMT-only, BRENT-only, TWM, and TOM aggregate/per-member designs.
- [Weightless Randomized Demo Portfolios — 2026-10-26](reports/Weightless%20Randomized%20Demo%20Portfolios%20%E2%80%94%202026-10-26.md) — fixed-seed equal-dollar mixed compositions, daily aggregate paths, and a composition-agnostic accounting demonstration (not a profitability forecast).
- [Oil Portfolio Update — 2026-10-26](reports/Oil%20Portfolio%20%E2%80%94%202026-10-26%20Update.md) — user-authorized Oil-only mark-forward to the latest complete aligned EOD marks; active trade-event cutoff remains 2026-10-19, and Oct. 27–29 marks are still needed for a current-date valuation.
- [Oil Position Audit Sheet](data/oil_position_audit_sheet_v1.csv) — one row per known Oil-related core/ATS/manual/private position or scenario record. Grouping provisionally uses small <=1U ($10,000 standard model notional) and large >1U; reinstated short sensitivities remain hypothetical and non-additive.
- [Multi-Asset Account Statement — 2026-10-28](reports/Multi-Asset%20Account%20Statement%20%E2%80%94%202026-10-28.md) and [register CSV](data/multi_asset_account_statement_2026-10-28_v1.csv) — source-separated holdings, model lots, snapshots and audit-only records; not a reconciled account total.
- [Account Change Log — 2026-10-29](reports/Account%20Change%20Log%20%E2%80%94%202026-10-29.md) and [CSV](data/account_change_log_2026-10-29_v1.csv) — screenshot-reported transactions, the LCID buy and hypothetical offer reference, and model/policy changes.
- [$200 Oil Foundation & U-Sized Opportunity Capitalization Strategy — Briefing](reports/%24200%20Oil%20Foundation%20%26%20U-Sized%20Opportunity%20Capitalization%20Strategy%20%E2%80%94%20Briefing.md) — historical strategy design and user-reported ATS exit/dissolution.
- [Harshal's Private Fund — November 2026++ Experiment](reports/Harshal%27s%20Private%20Fund%20%E2%80%94%20November%202026%2B%2B%20Experiment.md) — preserved historical profit-only balance and position schedule; separate under-duress replay overlays the two Oct. 29 oil closes as voided.
- [$20B Paper Portfolio — Units Experiment](Units%20Experiment%20Pool%20Allocation.md) — original pool bridge, restored supplemental $20B BRENT/OIL order, 50U/50U transfer to THE WINNING MODEL, and combined lot sizing.
- [Monero Realized-Profit EOM Conversion Overlay — 2026-10-26](reports/Monero%20Realized-Profit%20EOM%20Conversion%20Overlay%20%E2%80%94%202026-10-26.md) — 1% of monthly aggregate net realized PnL is reserved for Kraken XMR/USD conversion only when a supplied TradingView EOM mark exists.
- [ALIUSD User-Directed LONG Position](reports/ALIUSD%20User-Directed%20LONG%20Position.md) — CSV-sized 15,546,506-unit LONG at corrected $2,999.99 basis; leverage is bookkeeping only; source artifacts archived; excluded from historical core replay.
- [Model Performance Explorer](Model%20Performance%20Explorer.html) — interactive view of model results.
- [Model Calculation Guide](Model%20Calculation%20Guide.md) — plain-language unit sizing, daily position handling, reversal logic, and PnL formulas.
- [ATS and Manual Live Position Reconciliation](ATS%20and%20Manual%20Live%20Position%20Reconciliation.md) — preserved user-reported ATS liquidation and prior zero-position report.
- [Under-Duress Oil Sale Void Replay](reports/Under-Duress%20Oil%20Sale%20Void%20Replay.md) — separate, non-destructive scenario overlay that voids listed oil closes, restores documented/model-equivalent positions, and tags hypothetical LCID consideration as unallocated scenario funding.
- [Under-Duress Audit / Rollback Log](reports/Under-Duress%20Audit%20Rollback%20Log.md) — user-reported public-portfolio ATS manual-review rationale and public/private scope boundary.
- [Oil Cost Basis Savings Model](Oil%20Cost%20Basis%20Savings%20Model.md) — realized target-trim and modeled SHORT-exit PnL credited once to the effective basis of the residual and replenishment lots, mapped across all 32 portfolios.
- [Trades Zip PnL](Trades%20Zip%20PnL.md) — master historical PnL report; see its scope note for reconciliation status.
- [TradingView Energy and Currency Desk Sidecars](TradingView%20Energy%20and%20Currency%20Desk%20Sidecars.md) — standard 10U energy and DXY sizing schedules; the THE ONE MODEL uses a derived 11U/DAY energy tranche per active ticker, while its 1U/DAY core DXY sleeve plus 10U/DAY add-on gives 11U/day combined currency exposure.
- [Crypto Sidecar — Pending TradingView Recalibration](Crypto%20Sidecar%20%E2%80%94%20Pending%20TradingView%20Recalibration.md) — BTC/ETH excluded until source calibration.
- [Small Caps pilot](Small%20Caps%20%5BBuyout%20%26%20Reorganization%20Offering%20Test%20Pilot%5D.md) — LCID test basket and current-date $4.2B hypothetical market-cap-level buyout terms.
- [Corporate Takeover Defense — Legal Limits](reports/Corporate%20Takeover%20Defense%20%E2%80%94%20Legal%20Limits.md) — educational U.S./Delaware overview of poison pills, duress, fiduciary duties, and scorched-earth tactics.
- [Strategy and Sidecar Comparison](Strategy%20and%20Sidecar%20Comparison.md) — standard variants, $500 and shared/variant-specific 1U/EOD models, 10U TradingView energy sidecar, and composites.
- [Oil Chart Set — 2026-10-28](reports/Oil%20Chart%20Set%20%E2%80%94%202026-10-28.md) — four archived TradingView daily charts, grouped into a USOIL recent view and BRENT recent, close, and broader-2026 views; screenshots are not treated as fills or EOD marks.
- [Chart Archive Review](Chart%20Archive%20Review.md), [Triangle Signals](Triangle%20Signals.md), and [Unrealized PnL](Unrealized%20PnL.md) — source reconciliation and focused trade views.

## Repository layout

- `trades/` — standardized symbol ledgers; `trades/2024/` holds the separate 2024 cohort; its [standalone PnL report](reports/2024/2024%20Trades%20PnL.md) is organized under `reports/`.
- `trades.zip` — synchronized archive of the `trades/` tree.
- `Charts/` — original and labeled chart images, plus generated performance charts.
- `Archive/` — source screenshot archives and duplicate captures.
- `reports/` — historical standalone reports, including the 2024 trade report.
- `data/` — user-provided input series, audit tables, and generated model exports. Historical TradingView benchmark files and post-cutoff exceptions are preserved beside the [exception index](data/tradingview_post_cutoff_exceptions_v1.csv); they are not approved for active use pending review. Five provisional XRH0 carry-forwards remain separately flagged; BTC/ETH remain outside the core. Legacy close sets are preserved for historical audits only.
- `scripts/` — TradingView import/alignment tools, source-date policy gate, exception indexer, historical core replay, and model builders. Post-cutoff TradingView import and benchmark rebuilds are blocked by default; other TV-dependent rebuilds are paused by policy until review. `build_oil_desk_hypothetical.py` is retained for the historical superseded schedule only.
- `tests/` — regression tests for the ledgers, marks, model calculations, and generated outputs.
- `research/` — topical research reports and working notes, grouped by subject.
- `references/` — standalone reference documents, including the supplied ledger PDF.

## Rebuilds

**Default TradingView-dependent imports and model/report rebuilds remain paused** under the October 20 cutoff. A single user-authorized, isolated Oil v2 mark-forward uses the existing aligned EOD marks through October 26, while keeping active trade events capped at October 19 and excluding all later trade-log, ATS-scenario, and under-duress positions. This is not a general policy waiver. The repository has no complete five-symbol EOD marks for October 27–29, so the v2 report is not an October 29 valuation. Do not run other TradingView imports, benchmarks, sidecars, portfolio, oil, or PnL rebuilds without a separate explicit review and authorization.

To reproduce only this scoped update:

```bash
PAPER_TRADES_OIL_PORTFOLIO_VERSION=2 python3 scripts/build_oil_portfolio.py
```

The exception inventory can be refreshed without changing trade/PnL values:

```bash
python3 scripts/build_tradingview_post_cutoff_exceptions.py
```

The pinned historical importers and benchmark builder reject post-cutoff TradingView inputs by default. The `--preserve-flagged-legacy` override is for archival/test reproduction only; it marks those rows as exceptions and does not make them eligible for active use. See [TradingView PaperTrading Block Policy](reports/TradingView%20Post-October%2019%20Block%20Policy.md).

Some chart-generation and test dependencies (for example, Matplotlib and Pillow) may need to be installed in the local environment first.
