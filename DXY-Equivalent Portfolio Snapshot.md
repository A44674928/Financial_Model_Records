# Whole-Portfolio DXY View — FX Daily Data Needed

**The earlier DXY-equivalent snapshot was withdrawn. Its calculation was wrong:** it treated DXY as a separate $10,000 position and divided portfolio PnL by a fixed $1,000-per-point multiplier. Do not use the prior DXY totals.

The corrected view will use DXY as a **whole-portfolio numeraire**, not as an additional position. It will compare the portfolio's unrealized PnL in USD with the full account value expressed in DXY-equivalent units using the daily DXY close. The historical DXY log entry remains a reference mark; it will not add a standalone $10,000 DXY position to this comparison.

The supplied daily DXY series is preserved in `data/dxy_september_october_2026_daily_close.csv`. Per your direction, its Oct. 22 close of **102.22** is authoritative for this view and supersedes the earlier **101.616** terminal mark. Daily EUR/USD and JPY/USD closes are still needed to calculate those open positions' daily USD unrealized PnL as part of the whole portfolio. Please provide the daily closes from their entry dates through **Oct. 22, 2026**. The already-provided terminal FX marks are retained for reference; missing daily marks will not be silently interpolated.
