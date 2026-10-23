# Whole-Portfolio DXY View — Daily Data Needed

**The earlier DXY-equivalent snapshot was withdrawn. Its calculation was wrong:** it treated DXY as a separate $10,000 position and divided portfolio PnL by a fixed $1,000-per-point multiplier. Do not use the prior DXY totals.

The corrected view will use DXY as a **whole-portfolio numeraire**, not as an additional position. The comparison will show portfolio unrealized PnL in USD and the same account value expressed in DXY-equivalent units using the DXY index close as the conversion basis. The historical DXY log entry remains a reference mark; it will not add a standalone $10,000 position to this comparison.

The workspace has user-provided Oct. 22 terminal marks for DXY, EUR/USD, and JPY/USD, plus daily US30Y yields. It does not yet contain the daily DXY, EUR/USD, and JPY/USD closes required for the selected daily graph and full-portfolio daily PnL path. Please provide closes from **Sep. 3–Oct. 22, 2026** (or from each position's entry date through Oct. 22) in a CSV with date and close columns. Once supplied, the graph can compare USD unrealized PnL against the whole portfolio's DXY-denominated value without treating DXY as a separate trade.
