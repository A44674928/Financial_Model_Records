# Chart Archive Review — 2026-10-23 Screenshot ZIP

Source: `Before the October 19th TradingView moderator's bitch fit.zip` (85 JPEGs), reconciled with `trades/*.txt` and `trades/index.txt`. Numbered image references correspond to `.cache/chart_review/images/001.jpeg`–`085.jpeg`; capture-name mapping is in `.cache/chart_review/manifest.txt`.

## Changes Applied from Your Review

- Added distinct $10,000-unit LONG entries for META Sep 8 (`013`, `$616.67`), TVC:USOIL Sep 10 (`014`, `$97.32`), and TVC:USOIL Sep 24 (`046`, `$93.74`).
- Recorded the badge-marked DXY LONG (`007`, chart quote `99.087`), EUR/USD LONG (`019`, `1.15388`), and the user-confirmed JPY/USD LONG (`012`, `0.010160`) as $10,000 positions. The EUR/USD and JPY/USD positions are partial currency exposures against the broad LONG DXY basket. Also recorded US10Y LONG Sep 10 (`015`, `4.865%`), US30Y SHORT Sep 15 (`021`, `5.35%`), and a distinct US10Y LONG Sep 24 (`045`, `5.208%`), each $10,000.
- Corrected the AAPL Sep 4 second-post entry in `trades/AAPL.txt` from `$336.64` to the screenshot quote `$320.98` (`010`).
- Corrected log dates to the dates shown on the post screenshots: NFLX (`059`) and INTC (`060`) to Oct 3; UPS's hidden second short (`074`) to Oct 10; and PLTR's “share sellers paradise” exit/short pair (`076`) to Oct 10. The two UPS posts remain separate positions; the PLTR exit and compounded short remain paired events for the same position.
- Kept the BRENT Oct 9 `$106.50` lot as-is; screenshot `075` is its Oct 10 update, not an additional position.
- For screenshot `061`, recorded a $10,000 BRENT LONG on Oct 4 at the visible chart quote `$106.446`, plus a separate $10,000 CVX LONG on Oct 5 at the user-provided market-open price `$206.83` (the Oct 4 post caption says `CVX`, although its visible chart is Brent Cash).
- Preserved all 77 original event lines; added eleven confirmed chart positions, including JPY/USD LONG on Sep 7. The 2026 trade logs now contain 88 event lines. `trades.zip` was synchronized with the updated text logs and index.

## Scope / Modeling Note

The model comparison was subsequently regenerated for the 32 symbols with configured daily price series. It uses 82 modeled events out of 88 total log events; six DXY, EUR/USD, JPY/USD, and Treasury-yield events remain outside that valuation universe. The separate master `Trades Zip PnL.md` has not been recalculated and will not currently reconcile to the refreshed model comparison.

The requested US10Y adjustment is still pending its daily yield series. The agreed calculation is an annualized daily spread carry on deployed notional: `(US10Y yield − 4.865%) / 365`, with above-baseline yield contributing positive adjustment. The local data only contains selected chart points, not a complete daily series.
