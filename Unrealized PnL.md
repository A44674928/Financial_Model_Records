# Unrealized PnL — Paper Trades Portfolio (*Fall (Arizona) [2026]*)

Mark-to-market **Unrealized Profit & Loss (PnL)** for trades from ***Fall (Arizona) [2026]* exclusively** (`America/Phoenix`, year-round **`MST` / `UTC-07:00`** without Daylight Saving Time) as of **Thursday, October 22, 2026** regular-session close (**4:00 PM EDT / 1:00 PM MST** for NYSE/NASDAQ equities; **official October 22 daily settlement** for ICE Brent and NYMEX WTI crude oil), assuming an equal **$10,000.00 initial notional (`1 unit`) per open position** (fractional quantity $Q = \$10{,}000 / P_{\text{entry}}$; excludes commissions, borrow fees, and overnight financing).

> **Master Unified Ledger — *Fall (Arizona) [2026]* Exclusively (`32` Symbols, Exact Fills + Realized & Short-Compounded Exits):** This document preserves the visual chart-only book from `Charts/`. For the complete error-corrected, standardized **`1 unit = $10,000.00`** *Fall (Arizona) [2026]* master ledger across all **32 symbols** (`trades/` & `trades.zip`, including realized `[TAKE PROFIT]` exits compounded with shorts, `INTC $115.11` Neutral → Short, same-day multi-post pairs, and restored `BRENT` / `OIL` / Oct 19 trades), see **[`Trades Zip PnL.md`](Trades%20Zip%20PnL.md)**.

---

## Executive Comparison Across Position Models

| Portfolio Model | Open Legs | Initial Notional | Mark Value (Oct 22) | Unrealized PnL ($) | Return (%) | Win / Loss | Net-Positive Tickers |
|---|---:|---:|---:|---:|---:|---|---|
| **1A. Triangle/Hazard Book + All 3 `SPCX` Charts** (`Oct 6 $173.77`, `Oct 9 $161.59`, `Oct 19 $147.96`) | **18** | **$180,000.00** | **$200,324.28** | **+$20,324.28** | **+11.29%** | **17 W / 1 L** | **7 of 7 (100% green)** |
| **1B. Triangle/Hazard Book + `SPCX` Arrow (`$176`) + `Oct 6` & `Oct 9`** | **18** | **$180,000.00** | **$201,882.90** | **+$21,882.90** | **+12.16%** | **17 W / 1 L** | **7 of 7 (100% green)** |
| **1C. Triangle/Hazard Book + All 4 `SPCX` Points** (`$176`, `$173.77`, `$161.59`, `$147.96`) | **19** | **$190,000.00** | **$212,099.85** | **+$22,099.85** | **+11.63%** | **18 W / 1 L** | **7 of 7 (100% green)** |
| *— Add 2 Unlisted `INTC` Chart `🟢L` (`Sep 4`, `Sep 16`) to 1A / 1B / 1C* | *20 / 20 / 21* | *$200k / $200k / $210k* | *$217,783.51 / $219,342.12 / $229,559.07* | ***+$17,783.51 / +$19,342.12 / +$19,559.07*** | ***+8.89% / +9.67% / +9.31%*** | *17–18 W / 3 L* | ***7 of 7 (100% green)*** |
| **2A. Published Charts Book (All 11 Charts: Oct 6 & Oct 9 `SPCX` + 9 Oct 19 Charts)** | **11** | **$110,000.00** | **$112,126.34** | **+$2,126.34** | **+1.93%** | **6 W / 5 L** | **4 of 9** |
| **2B. October 19 Snapshot Charts Only** (`Current Price Points.csv`) | **9** | **$90,000.00** | **$89,414.18** | **−$585.82** | **−0.65%** | 4 W / 5 L | 4 of 9 |

---

## 1. `SPCX` Multi-Leg Breakdown (GitHub Chart + Oct 6 & Oct 9 Legs)

Both newly provided `SPCX` screenshots have been archived alongside matching 🔴 **`y — Short`** labeled PNGs in [`Charts/SPCX/updates/`](Charts/SPCX/updates/) to pair with the October 19 `SPCX` chart already in [`Charts/SPCX/`](Charts/SPCX/):

| `SPCX` Leg / Chart | Date & Interval | Signal / Side | Entry Price | Oct 22 Mark | Implied Units ($10k) | Move ($/sh) | Return (%) | Unrealized PnL ($) | Labeled Chart |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| **`"SPCX"`** *(Added Leg 1)* | Tue Oct 6, 2026 · `1D` | 🔴 **y — Short** | $173.77 | $144.75 | 57.5473 sh | +$29.02 | **+16.70%** | **+$1,670.02** | [View labeled chart](Charts/SPCX/updates/SPCX-2026-10-06-labeled.png) |
| **`"SPCX UPDATE: SUCCESS!"`** *(Added Leg 2)* | Fri Oct 9, 2026 · `15m` | 🔴 **y — Short** | $161.59 | $144.75 | 61.8850 sh | +$16.84 | **+10.42%** | **+$1,042.14** | [View labeled chart](Charts/SPCX/updates/SPCX-2026-10-09-labeled.png) |
| **`"SPCX: TARGET IDENTIFIED"`** *(GitHub Chart Price)* | Mon Oct 19, 2026 · `1W` | 🔴 **y — Short** | $147.96 | $144.75 | 67.5858 sh | +$3.21 | **+2.17%** | **+$216.95** | [View labeled chart](Charts/SPCX/SPCX-2026-10-19-labeled.png) |
| **Red `⬇` Arrow on GitHub / Oct 9 Chart** *(15m High `$176.42`)* | Wk Sep 28 / Oct 6 Peak | 🔴 **y — Short** | $176.00 | $144.75 | 56.8182 sh | +$31.25 | **+17.76%** | **+$1,775.57** | [View labeled chart](Charts/SPCX/SPCX-2026-10-19-labeled.png) |

### `SPCX` Subtotals ($10,000 per Leg → Oct 22 Close `$144.75`)

| `SPCX` Roll-Up Basis | Legs | Initial Notional | Net Units Held | Avg Entry | Mark Value (Oct 22) | Unrealized PnL ($) | Return (%) |
|---|---:|---:|---:|---:|---:|---:|---:|
| **Added 2 Legs Only** (`Oct 6 $173.77` + `Oct 9 $161.59`) | 2 | $20,000.00 | −119.4324 sh | $167.46 | $22,712.17 | **+$2,712.17** | **+13.56%** |
| **3 Published `SPCX` Charts** (`Oct 6 $173.77` + `Oct 9 $161.59` + `Oct 19 $147.96`) | **3** | **$30,000.00** | **−187.0182 sh** | **$160.41** | **$32,929.12** | **+$2,929.12** | **+9.76%** |
| **GitHub Red Arrow + 2 Added Legs** (`Wk Sep 28 $176` + `Oct 6 $173.77` + `Oct 9 $161.59`) | **3** | **$30,000.00** | **−176.2505 sh** | **$170.21** | **$34,487.74** | **+$4,487.74** | **+14.96%** |
| **All 4 `SPCX` Points Combined** (`$176` + `$173.77` + `$161.59` + `$147.96`) | **4** | **$40,000.00** | **−243.8364 sh** | **$164.05** | **$44,704.69** | **+$4,704.69** | **+11.76%** |

> **Relationship between the `$176` red arrow and the `Oct 6 ($173.77)` chart:** On the [Oct 6 1D screenshot](Charts/SPCX/updates/SPCX-2026-10-06-short.jpeg), no red arrow had been drawn yet when `SPCX` was posted short at **`$173.77`**. On the [Oct 9 15m update](Charts/SPCX/updates/SPCX-2026-10-09-short-update.jpeg) (`$161.59`), the red `⬇` arrow appears directly at the **Oct 6 intraday peak (`High $176.42`)** inside the green consolidation box — the same peak read off the weekly log axis in [`Triangle Signals.md`](Triangle%20Signals.md) as `Wk Sep 28 ≈ $176`. Counting the three published `SPCX` charts (`$173.77`, `$161.59`, `$147.96`) avoids double-counting the Oct 6 entry while including the `Oct 19 ($147.96)` GitHub chart; all three roll-up conventions are reported in full below.

---

## 2. All-Signals Unclosed Portfolio Ledger

### Scorecard by Signal Group & Asset Class

*(Shown for **Model 1A**: 15 other recorded triangle/hazard legs + the **3 Published `SPCX` Charts** [`$173.77`, `$161.59`, `$147.96`] = 18 legs, and **Model 1C**: adding the `$176.00` red-arrow point as a 19th leg.)*

| Breakdown | Legs (1A / 1C) | Initial Notional (1A / 1C) | Mark Value (1A / 1C) | Unrealized PnL ($) (1A / 1C) | Return (%) (1A / 1C) | Win / Loss |
|---|---|---|---|---|---|---|
| 🟢 **Green `▲` Longs (`Triangle Signals.md`)** | 7 | $70,000.00 | $77,135.79 | **+$7,135.79** | **+10.19%** | 6 W / 1 L |
| 🔴 **Red `▼` Shorts (`PLTR` + `SPCX` ×3 / ×4)** | 4 / 5 | $40k / $50k | $43,631.01 / $55,406.58 | **+$3,631.01 / +$5,406.58** | **+9.08% / +10.81%** | **4–5 W / 0 L** |
| 🟠 **Orange Hazard Openings (`5 🟠L` + `2 🟠S`)** | 7 | $70,000.00 | $79,557.47 | **+$9,557.47** | **+13.65%** | **7 W / 0 L** |
| *— All Long Legs (`7 🟢L` + `5 🟠L`)* | *12* | *$120,000.00* | *$132,120.63* | ***+$12,120.63*** | ***+10.10%*** | *11 W / 1 L* |
| *— All Short Legs (`4–5 🔴S` + `2 🟠S`)* | *6 / 7* | *$60k / $70k* | *$68,203.65 / $79,979.21* | ***+$8,203.65 / +$9,979.21*** | ***+13.67% / +14.26%*** | ***6–7 W / 0 L*** |
| *— Energy / Commodities (`BRENT` ×3, `OIL` ×3)* | *6* | *$60,000.00* | *$65,389.50* | ***+$5,389.50*** | ***+8.98%*** | *6 W / 0 L* |
| *— US Equities (`LMT` ×4, `SPCX` ×3/×4, `PLTR` ×2, `CAT` ×2, `INTC`)* | *12 / 13* | *$120k / $130k* | *$134,934.77 / $146,710.34* | ***+$14,934.77 / +$16,710.34*** | ***+12.45% / +12.85%*** | *11–12 W / 1 L* |
| **Total — Model 1A (`3` `SPCX` Charts) / Model 1C (`4` `SPCX` Points)** | **18 / 19** | **$180k / $190k** | **$200,324.28 / $212,099.85** | **+$20,324.28 / +$22,099.85** | **+11.29% / +11.63%** | **17–18 W / 1 L** |
| **Total — Model 1B (`$176` Arrow + `Oct 6` & `Oct 9` `SPCX`)** | **18** | **$180,000.00** | **$201,882.90** | **+$21,882.90** | **+12.16%** | **17 W / 1 L** |

### Ticker-by-Ticker Roll-Up (Chronological Position Sequence)

| Ticker | Chronological Signal Sequence | Legs | Gross Notional | Net Units Held | Avg Entry | Oct 22 Mark | Unrealized PnL ($) | Return (%) |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| **LMT** | Oct 7 🟢L ($502) → Oct 9 🟠L ($514) → Oct 12 🟢L ($496) → Oct 19 🟠L* ($548) | 4 | $40,000.00 | +77.7850 sh | $514.24 | $589.91 | **+$5,886.17** | **+14.72%** |
| **SPCX** *(3 charts)* | Oct 6 🔴S ($173.77) → Oct 9 🔴S ($161.59) → Oct 19 🔴S ($147.96) | 3 | $30,000.00 | −187.0182 sh | $160.41 | $144.75 | **+$2,929.12** | **+9.76%** |
| **SPCX** *(arrow + 2 / all 4)* | *Wk Sep 28 🔴S ($176) + Oct 6 ($173.77) + Oct 9 ($161.59) [+ Oct 19 ($147.96)]* | *3 / 4* | *$30k / $40k* | *−176.2505 / −243.8364 sh* | *$170.21 / $164.05* | *$144.75* | ***+$4,487.74 / +$4,704.69*** | ***+14.96% / +11.76%*** |
| **OIL** | Sep 22 🟠L ($90.2) → Sep 29 🟠L ($89.3) → Oct 8 🟢L ($90.6) | 3 | $30,000.00 | +333.2221 bbl | $90.03 | $99.47 | **+$3,145.60** | **+10.49%** |
| **INTC** *(recorded)* | Sep 28 🟠S ($117) | 1 | $10,000.00 | −85.4701 sh | $117.00 | $85.49 | **+$2,693.16** | **+26.93%** |
| **PLTR** | Sep 11 🟢L ($166) → Oct 9 🔴S ($211) | 2 | $20,000.00 | +12.8476 sh | *(box)* | $196.19 | **+$2,520.57** | **+12.60%** |
| **BRENT** | Sep 23 🟢L ($102.5) → Oct 2 🟠L ($107.0) → Oct 9 🟢L ($106.5) | 3 | $30,000.00 | +284.9156 bbl | $105.29 | $113.17 | **+$2,243.90** | **+7.48%** |
| **CAT** | Sep 14 🟢L ($780) → Oct 6 🟠S ($867) | 2 | $20,000.00 | +1.2865 sh | *(flipped)* | $704.05 | **+$905.75** | **+4.53%** |
| **INTC** *(all 3 chart)* | *Sep 4 🟢L ($95.4) → Sep 16 🟢L ($100.6) → Sep 28 🟠S ($117)* | *3* | *$30,000.00* | *+118.7553 sh* | *(flipped)* | *$85.49* | ***+$152.39*** | ***+0.51%*** |

### Complete Leg-by-Leg Ledger ($10,000 per Position → Oct 22 Close)

| # | Ticker | Date | Signal | Side | Entry | Oct 22 Mark | Implied Units | Trade Move ($/unit) | Return (%) | Unrealized PnL ($) |
|---:|---|---|---|---|---:|---:|---:|---:|---:|---:|
| 1 | [**INTC**](Charts/INTC/INTC-2026-10-19-labeled.png) | Mon Sep 28, 2026 | 🟠S Hazard Flip | **SHORT** | $117.00 | $85.49 | 85.4701 sh | +$31.51 | **+26.93%** | **+$2,693.16** |
| 2 | [**LMT**](Charts/LMT/LMT-2026-10-19-labeled.png) | Mon Oct 12, 2026 | 🟢L Long | **LONG** | $496.00 | $589.91 | 20.1613 sh | +$93.91 | **+18.93%** | **+$1,893.35** |
| 3 | [**CAT**](Charts/CAT/CAT-2026-10-19-labeled.png) | Tue Oct 6, 2026 | 🟠S Hazard Flip | **SHORT** | $867.00 | $704.05 | 11.5340 sh | +$162.95 | **+18.79%** | **+$1,879.47** |
| 4 | [**PLTR**](Charts/PLTR/PLTR-2026-10-19-labeled.png) | Fri Sep 11, 2026 | 🟢L Long | **LONG** | $166.00 | $196.19 | 60.2410 sh | +$30.19 | **+18.19%** | **+$1,818.67** |
| 5 | [**LMT**](Charts/LMT/LMT-2026-10-19-labeled.png) | Wed Oct 7, 2026 | 🟢L Long | **LONG** | $502.00 | $589.91 | 19.9203 sh | +$87.91 | **+17.51%** | **+$1,751.20** |
| 6 | [**SPCX**](Charts/SPCX/updates/SPCX-2026-10-06-labeled.png) | Tue Oct 6, 2026 | 🔴S Short *(1D)* | **SHORT** | $173.77 | $144.75 | 57.5473 sh | +$29.02 | **+16.70%** | **+$1,670.02** |
| 7 | [**LMT**](Charts/LMT/LMT-2026-10-19-labeled.png) | Fri Oct 9, 2026 | 🟠L Hazard Long | **LONG** | $514.00 | $589.91 | 19.4553 sh | +$75.91 | **+14.77%** | **+$1,476.85** |
| 8 | [**OIL**](Charts/OIL/OIL-2026-10-19-labeled.png) | Tue Sep 29, 2026 | 🟠L Hazard Long | **LONG** | $89.30 | $99.47 | 111.9821 bbl | +$10.17 | **+11.39%** | **+$1,138.86** |
| 9 | [**SPCX**](Charts/SPCX/updates/SPCX-2026-10-09-labeled.png) | Fri Oct 9, 2026 | 🔴S Short *(15m)* | **SHORT** | $161.59 | $144.75 | 61.8850 sh | +$16.84 | **+10.42%** | **+$1,042.14** |
| 10 | [**BRENT**](Charts/BRENT/BRENT-2026-10-19-labeled.png) | Wed Sep 23, 2026 | 🟢L Long | **LONG** | $102.50 | $113.17 | 97.5610 bbl | +$10.67 | **+10.41%** | **+$1,040.98** |
| 11 | [**OIL**](Charts/OIL/OIL-2026-10-19-labeled.png) | Tue Sep 22, 2026 | 🟠L Hazard Long | **LONG** | $90.20 | $99.47 | 110.8647 bbl | +$9.27 | **+10.28%** | **+$1,027.72** |
| 12 | [**OIL**](Charts/OIL/OIL-2026-10-19-labeled.png) | Thu Oct 8, 2026 | 🟢L Long | **LONG** | $90.60 | $99.47 | 110.3753 bbl | +$8.87 | **+9.79%** | **+$979.03** |
| 13 | [**LMT**](Charts/LMT/LMT-2026-10-19-labeled.png) | Oct 19, 2026 | 🟠L* Pending Long | **LONG** | $548.00 | $589.91 | 18.2482 sh | +$41.91 | **+7.65%** | **+$764.78** |
| 14 | [**PLTR**](Charts/PLTR/PLTR-2026-10-19-labeled.png) | Fri Oct 9, 2026 | 🔴S Short | **SHORT** | $211.00 | $196.19 | 47.3934 sh | +$14.81 | **+7.02%** | **+$701.90** |
| 15 | [**BRENT**](Charts/BRENT/BRENT-2026-10-19-labeled.png) | Fri Oct 9, 2026 | 🟢L Long | **LONG** | $106.50 | $113.17 | 93.8967 bbl | +$6.67 | **+6.26%** | **+$626.29** |
| 16 | [**BRENT**](Charts/BRENT/BRENT-2026-10-19-labeled.png) | Fri Oct 2, 2026 | 🟠L Hazard Long | **LONG** | $107.00 | $113.17 | 93.4579 bbl | +$6.17 | **+5.77%** | **+$576.64** |
| 17 | [**SPCX**](Charts/SPCX/SPCX-2026-10-19-labeled.png) | Mon Oct 19, 2026 | 🔴S Short *(1W GitHub)* | **SHORT** | $147.96 | $144.75 | 67.5858 sh | +$3.21 | **+2.17%** | **+$216.95** |
| 18 | [**CAT**](Charts/CAT/CAT-2026-10-19-labeled.png) | Mon Sep 14, 2026 | 🟢L Long | **LONG** | $780.00 | $704.05 | 12.8205 sh | −$75.95 | **−9.74%** | **−$973.72** |
| — | **Subtotal — Model 1A (18 Legs: 3 `SPCX` Charts)** | | **12L / 6S** | | **$180,000.00** | **$200,324.28** | | | **+11.29%** | **+$20,324.28** |
| 19 | [**SPCX***](Charts/SPCX/SPCX-2026-10-19-labeled.png) | Wk Sep 28, 2026 | 🔴S Short *(arrow)* | **SHORT** | $176.00 | $144.75 | 56.8182 sh | +$31.25 | **+17.76%** | **+$1,775.57** |
| — | **Subtotal — Model 1C (19 Legs: All 4 `SPCX` Points)** | | **12L / 7S** | | **$190,000.00** | **$212,099.85** | | | **+11.63%** | **+$22,099.85** |
| 20 | [**INTC***](Charts/INTC/INTC%202026-10-19%2021.46.26.jpeg) | Fri Sep 4, 2026 | 🟢L *(chart)* | **LONG** | $95.40 | $85.49 | 104.8218 sh | −$9.91 | **−10.39%** | **−$1,038.78** |
| 21 | [**INTC***](Charts/INTC/INTC%202026-10-19%2021.46.26.jpeg) | Wed Sep 16, 2026 | 🟢L *(chart)* | **LONG** | $100.60 | $85.49 | 99.4036 sh | −$15.11 | **−15.02%** | **−$1,501.99** |
| — | **Total — All 21 Visual + Chart Legs** | | **14L / 7S** | | **$210,000.00** | **$229,559.07** | | | **+9.31%** | **+$19,559.07** |

---

## 3. Published Charts Book (All 11 Charts: Oct 6 & Oct 9 `SPCX` + 9 Oct 19 Charts)

Combining the two earlier `SPCX` `↘ SHORT` screenshots (`Oct 6 @ $173.77` and `Oct 9 @ $161.59`) with the nine October 19 charts in [`Current Price Points.csv`](Current%20Price%20Points.csv) (including the October 19 `SPCX @ $147.96` GitHub chart) flips the Published Charts Book **from `−$585.82` (−0.65%) into profit at `+$2,126.34` (+1.93% on $110,000.00)**:

| Ticker | Idea Date / Chart | Signal / Side | Entry Price | Mark Price (Oct 22) | Implied Units ($10k) | Trade PnL ($/unit) | Return (%) | Unrealized PnL ($) | Position Value ($) |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| [**BRENT**](Charts/BRENT/BRENT-2026-10-19-labeled.png) | Oct 19 · 1D | 🟢 **x — Long** | $111.025 | $113.17 | 90.0698 bbl | +$2.145 | **+1.93%** | **+$193.20** | $10,193.20 |
| [**CAT**](Charts/CAT/CAT-2026-10-19-labeled.png) | Oct 19 · 1D | 🟢 **x — Long** | $729.58 | $704.05 | 13.7065 sh | −$25.53 | **−3.50%** | **−$349.93** | $9,650.07 |
| [**INTC**](Charts/INTC/INTC-2026-10-19-labeled.png) | Oct 19 · 1D | 🟢 **x — Long** | $94.865 | $85.49 | 105.4130 sh | −$9.375 | **−9.88%** | **−$988.25** | $9,011.75 |
| [**LMT**](Charts/LMT/LMT-2026-10-19-labeled.png) | Oct 19 · 1D | 🟢 **x — Long** | $548.23 | $589.91 | 18.2405 sh | +$41.68 | **+7.60%** | **+$760.26** | $10,760.26 |
| [**OIL**](Charts/OIL/OIL-2026-10-19-labeled.png) | Oct 19 · 1D | 🟢 **x — Long** | $98.74 | $99.47 | 101.2761 bbl | +$0.73 | **+0.74%** | **+$73.93** | $10,073.93 |
| [**ORCL**](Charts/ORCL/ORCL-2026-10-19-labeled.png) | Oct 19 · 1D | 🟢 **x — Long** | $128.23 | $125.54 | 77.9849 sh | −$2.69 | **−2.10%** | **−$209.78** | $9,790.22 |
| [**PLTR**](Charts/PLTR/PLTR-2026-10-19-labeled.png) | Oct 19 · 1D | 🔴 **y — Short** | $194.15 | $196.19 | 51.5066 sh | −$2.04 | **−1.05%** | **−$105.07** | $9,894.93 |
| [**SPCX** *(Oct 6)*](Charts/SPCX/updates/SPCX-2026-10-06-labeled.png) | Oct 6 · 1D | 🔴 **y — Short** | $173.77 | $144.75 | 57.5473 sh | +$29.02 | **+16.70%** | **+$1,670.02** | $11,670.02 |
| [**SPCX** *(Oct 9)*](Charts/SPCX/updates/SPCX-2026-10-09-labeled.png) | Oct 9 · 15m | 🔴 **y — Short** | $161.59 | $144.75 | 61.8850 sh | +$16.84 | **+10.42%** | **+$1,042.14** | $11,042.14 |
| [**SPCX** *(Oct 19)*](Charts/SPCX/SPCX-2026-10-19-labeled.png) | Oct 19 · 1W | 🔴 **y — Short** | $147.96 | $144.75 | 67.5858 sh | +$3.21 | **+2.17%** | **+$216.95** | $10,216.95 |
| [**TSLA**](Charts/TSLA/TSLA-2026-10-19-labeled.png) | Oct 19 · 1W | 🔴 **y — Short** | $368.06 | $374.58 | 27.1695 sh | −$6.52 | **−1.77%** | **−$177.15** | $9,822.85 |
| **Total (11 Charts)** | | **6 Long / 5 Short** | **$110,000.00** | **$112,126.34** | | | **+1.93%** | **+$2,126.34** | **$112,126.34** |

*(Oct 19 snapshot-only subtotal without the two earlier `SPCX` charts: `$90,000.00` initial → `$89,414.18` mark = **−$585.82** / **−0.65%**.)*

---

## 4. Calculation Methodology

For each open leg $i$ with initial notional $N_0 = \$10{,}000.00$, entry price $P_{0,i}$, and October 22 mark price $P_{1,i}$:

$$\text{Implied Units } (Q_i) = \frac{\$10{,}000.00}{P_{0,i}}, \qquad \Delta P_i = \begin{cases} P_{1,i} - P_{0,i} & \text{if } \text{LONG } (\text{L}) \\ P_{0,i} - P_{1,i} & \text{if } \text{SHORT } (\text{S}) \end{cases}$$

$$\text{Return } (\%) = \frac{\Delta P_i}{P_{0,i}} \times 100\%, \qquad \text{Unrealized PnL } (\$) = Q_i \times \Delta P_i = \$10{,}000.00 \times \frac{\Delta P_i}{P_{0,i}}$$
