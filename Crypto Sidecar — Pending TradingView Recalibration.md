# Crypto Sidecar — Pending TradingView Recalibration

> **Status: excluded from the core package.** BTC and ETH are intentionally isolated from all current core model calculations because their supplied historical marks have not yet been recalibrated to the user-provided TradingView benchmark. No substitute, Yahoo, legacy, or inferred prices are used here.

## Why this sidecar is pending

The TradingView benchmark currently includes 31 direct-price core symbols and a separate DXY index-mark series used for the integrated 1U/DAY/DXY currency sleeve. BTC and ETH are not present in the supplied Part A/Part B price lists used for the interim core. Until compatible TradingView price lists are supplied and aligned to the common session calendar, this page reports **no crypto mark-to-market PnL, return, or performance comparison**.

The original simulated-paper entries remain in [`trades/BTC.txt`](trades/BTC.txt) and [`trades/ETH.txt`](trades/ETH.txt) as source records only. Their logged entry details do not make the crypto positions part of the active benchmark or establish a valid current valuation.

## Sizing scenarios to apply after recalibration

Once source-calibrated BTC and ETH TradingView marks are available, the sidecar will report these as three independent hypothetical sizing alternatives:

| Scenario | Notional per 1U definition |
|---|---:|
| 0.05U | $500 |
| 1U | $10,000 |
| 10U | $100,000 |

These alternatives will not be stacked. No scenario PnL is calculated until the underlying price histories and missing-session treatment are verified.

## Source and scope controls

- Core exclusion is enforced in [`scripts/model_perf_core.py`](scripts/model_perf_core.py); neither BTC nor ETH is a member of the core price universe.
- The current benchmark coverage and source manifest are [`data/tradingview_benchmark_coverage_20261024.csv`](data/tradingview_benchmark_coverage_20261024.csv) and [`data/tradingview_benchmark_source_manifest_20261024.json`](data/tradingview_benchmark_source_manifest_20261024.json).
- The current core model report is [`Model Performance Comparison.md`](Model%20Performance%20Comparison.md).
- The integrated 1U/DAY/DXY sleeve and the separate energy/DXY sizing alternatives are documented in [`TradingView Energy and Currency Desk Sidecars.md`](TradingView%20Energy%20and%20Currency%20Desk%20Sidecars.md); none include crypto.

**Recalibration trigger:** add only user-provided TradingView BTC/ETH lists, preserve their provenance and coverage, align them to the benchmark sessions under an explicitly approved gap policy, then regenerate the isolated 0.05U/1U/10U sidecar. Until then, BTC/ETH remain pending and excluded.
