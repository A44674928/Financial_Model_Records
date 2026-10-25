# TradingView benchmark import status — 2026-10-24

> **Historical Part A-only checkpoint — superseded by the Part B import and full recalculation.** This note records the intermediate state before the second user-supplied archive was available. Its Part A coverage gate and “no comparison calculated yet” status are not current. The active 31-symbol core, separate DXY sidecar, crypto pending page, and current source manifest are linked in [`Model Performance Comparison.md`](../../Model%20Performance%20Comparison.md), [`TradingView Energy and Currency Desk Sidecars.md`](../../TradingView%20Energy%20and%20Currency%20Desk%20Sidecars.md), and [`data/tradingview_benchmark_coverage_20261024.csv`](../../data/tradingview_benchmark_coverage_20261024.csv).

## Source and processing

The user-specified archive is preserved byte-for-byte at [`data/benchmark_tradingview_price_lists_source_20261024.zip`](../../data/benchmark_tradingview_price_lists_source_20261024.zip). It was downloaded from [`Financial_Model_Records/PART A PRICE LISTS TRADING VIEW.zip`](https://github.com/A44674928/Financial_Model_Records/blob/main/PART%20A%20PRICE%20LISTS%20TRADING%20VIEW.zip), from repository commit `22540a55b08214460bb6cd7e64d8174c1ee1e1c2`; its SHA-256 is `1f283d0f7bf09edf8462a2115ec5c0c42be4f4c6a7491ffdb90d7b6060aa5f3e`.

[`scripts/import_tradingview_price_lists.py`](../../scripts/import_tradingview_price_lists.py) converts only ticker-specific RTF files into [`data/tradingview_benchmark_price_lists_20261024.csv`](../../data/tradingview_benchmark_price_lists_20261024.csv), with dates, closes, original RTF filenames, source links, and archive hash. The 571 parsed daily observations include all 36 active comparison sessions for each supplied ticker, plus the extra source dates. The September 7 Brent observation is retained in the raw normalized CSV but lies outside the common U.S. equity comparison calendar. `USOIL` maps to the model's internal `OIL` symbol. The generic `TICKER PRICE LIST (EXAMPLE).rtf` and macOS metadata are excluded; the GEV file is identified by its filename because its RTF body heading says `TICKER`.

## Coverage gate

The current comparison universe contains 33 directly priced symbols. The archive has complete 36-session coverage for **15** ticker-specific symbols:

`BRENT`, `CAT`, `GEV`, `HD`, `INTC`, `LCID`, `LMT`, `LULU`, `META`, `OIL` (from the `USOIL` file), `ORCL`, `PLTR`, `SPCX`, `TSLA`, and `VLO`.

The remaining **18** symbols have no ticker-specific list in this archive and are deliberately not substituted from Yahoo Finance or earlier project data:

`AAPL`, `AMZN`, `BTC`, `CVX`, `DIS`, `ETH`, `LLY`, `NET`, `NFLX`, `NVDA`, `PEP`, `RIVN`, `TMO`, `UPS`, `V`, `WMT`, `XLE`, and `XRH0`.

| Supplied ticker | Oct. 23 close | Supplied ticker | Oct. 23 close | Supplied ticker | Oct. 23 close |
|---|---:|---|---:|---|---:|
| BRENT | $117.345 | CAT | $687.00 | GEV | $815.00 |
| HD | $319.83 | INTC | $86.96 | LCID | $3.52 |
| LMT | $604.18 | LULU | $99.01 | META | $642.62 |
| OIL (USOIL file) | $103.45 | ORCL | $126.16 | PLTR | $196.75 |
| SPCX | $147.49 | TSLA | $372.22 | VLO | $419.28 |

See [`data/tradingview_benchmark_coverage_20261024.csv`](../../data/tradingview_benchmark_coverage_20261024.csv) and [`data/tradingview_benchmark_source_manifest_20261024.json`](../../data/tradingview_benchmark_source_manifest_20261024.json) for the machine-readable record.

**No new complete model comparison has been calculated yet.** A full core, fixed-$500/EOD, 1U/EOD, sidecar, DXY/yield, and 32-portfolio comparison must wait until all 18 missing lists are supplied. In accordance with the user's exclusive-benchmark instruction, no model may mix the 15 new TradingView histories with legacy Yahoo/previous-project prices for the other symbols. The archive also does not contain the separate DXY, EURUSD, JPYUSD, US10Y, or US30Y series used in supplementary numeraire/yield views; those views need their benchmark inputs confirmed or supplied before a strict all-comparison refresh. One prior energy-sidecar mark is specifically inconsistent with the new file: BRENT on 2026-09-28 was 103.676 in the prior energy input but is 102.676 in this TradingView list. The new user-supplied list is the benchmark; the prior sidecar output has not yet been recalculated.

A possible fill source in the same GitHub repository, [`data/multi_source_tv_yahoo_selection_1pct_v1.csv`](https://github.com/A44674928/Financial_Model_Records/blob/main/data/multi_source_tv_yahoo_selection_1pct_v1.csv), was checked against the 571 supplied ticker/date observations. It has rows for the missing tickers, but it matches only **2/571 exactly** and **14/571 within 1%**; median relative difference is **35.16%**. It is therefore rejected as a matching benchmark and must not fill the blanks. Existing reports remain retained for audit/history but are explicitly marked as legacy and not the requested updated benchmark.
