# Standardized Paper-Trades Ledger — *Fall (Arizona) [2026]* (`1 Unit = $10,000.00`)

Complete mark-to-market ledger for [`trades/`](trades/) and [`trades.zip`](trades.zip) covering ***Fall (Arizona) [2026]* exclusively** (**32 symbols**, **77 standardized log lines** through `2026-10-19`; all timestamps recorded in Arizona year-round **`MST` / `UTC-07:00`** without Daylight Saving Time, where `06:30 MST = 09:30 EDT` U.S. regular-session open and `13:00 MST = 16:00 EDT` close), marked against **Thursday, October 22, 2026** closing prices (`1:00 PM MST` / `4:00 PM EDT`). These historical totals remain on the Oct. 22 basis; the active daily energy marks and sidecar source are documented separately in [`Model Performance Comparison.md`](Model%20Performance%20Comparison.md).

> **Historical snapshot warning (2026-10-25):** The tables below are a legacy ledger snapshot, marked to Oct. 22 and based on the older trade-log state; they do **not** include the integrated 50U Manual-Automatic BRENT and USOIL core entries, their modeled 10U target trims, or the separate Oct. 25 10U LONG manual replenishment entries in BRENT at $115.792 and USOIL at $101.74. The latter entries are after the current Oct. 23 mark cutoff and are excluded from current PnL pending subsequent EOD marks. See [`Model Performance Comparison.md`](Model%20Performance%20Comparison.md), [`Weekend Oil 50U Position Hypothetical.md`](Weekend%20Oil%2050U%20Position%20Hypothetical.md), and [`Oil Cost Basis Savings Model.md`](Oil%20Cost%20Basis%20Savings%20Model.md). Do not add this legacy snapshot to current model results or use its historical totals as current.

> **Oct 22 equity EOD recheck (Oct 23):** I rechecked all **26 stock symbols plus the XLE ETF** against Yahoo Finance daily chart closes for Oct 22. **26 of 27 matched** the prior ledger marks; `NET` was stale at `$306.60` and the source close was `$303.61`. The NET mark and dependent PnL have been corrected; symbol-by-symbol source URLs and deltas are in [`data/oct22_equity_eod_recheck.csv`](data/oct22_equity_eod_recheck.csv). This ledger's oil rows remain on their historical Oct. 22 proxy-based basis; the active exact daily marks are in the linked model comparison and sidecar source file.

> **Cohort Scope — *Fall (Arizona) [2026]* Exclusively:** These trades are ***Fall (Arizona) [2026]* exclusively** (`America/Phoenix`, `MST` — not a full-year 2026 calendar book; includes the Sep 3–posted `BTC` chart carrying an author-estimated `2026-08-01` entry alongside the 76 `2026-09-03` to `2026-10-19` lines). The pre-season `2024-08-19 PLTR @ $24.00` long entry has been separated into [`trades/2024/PLTR.txt`](trades/2024/PLTR.txt) (see standalone [`2024 Trades PnL.md`](reports/2024/2024%20Trades%20PnL.md)) so all tables, rankings, and return percentages below reflect ***Fall (Arizona) [2026]* exclusively** with zero multi-year skew.

### Standardization & Error-Fix Rules Applied
1. **Genericized Unit Size (`1 unit = $10,000.00`):** Every trade entry/exit is standardized in `units` (`1 unit = $10,000`, `2 units = $20,000` on `CAT` exit, `5 units = $50,000` on `INTC` and `META` exits).
2. **Full Exits Compounded with Shorts:** `CAT` (`$864.70`), `INTC` (`$127.11`), `META` (`$769.46`), `DIS` (`$104.23`), and `PLTR` (`$209.05`) explicitly log both the full exit and the compounded `[SHORT]` entry.
3. **`INTC $115.11` Neutral Flip → Short:** `2026-09-24 10:00 @ $115.11` in [`trades/INTC.txt`](trades/INTC.txt) is logged as **`[SHORT]`** (`1 unit = $10,000.00`) where direction changed to Neutral (`🟠` hazard marker).
4. **Same-Day Multi-Post Pairs:** Logged as distinct same-day `1 unit ($10,000)` trades (`AAPL` Sep 4, `INTC` Sep 16, `META` Sep 16, `CVX` Sep 17, `UPS` Oct 9).
5. **Restored Chart Tickers & Oct 19 Updates:** Includes `BRENT`, `OIL`, `ORCL`, `TSLA`, and the Oct 19 entries on `CAT`, `INTC`, `LMT`, `PLTR`, and `SPCX`.

---

## Executive Summary — *Fall (Arizona) [2026]* Portfolio (`1 Unit = $10,000.00` → Oct 22, 2026 Close)

### A. Unified *Fall (Arizona) [2026]* Ledger Through Oct 19 (All 32 Symbols)

| *Fall (Arizona) [2026]* Model Variant | Closed Units | Realized PnL ($) | Open Units | Unrealized PnL ($) | Total Units (Notional) | **Combined PnL ($)** | **Return (%)** | Unit Win / Flat / Loss |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| **Variant 1 — As-Logged Multi-Leg (`1u = $10k` Compounded Short)** | **14u** | **+$23,083.77** | **58u** | **+$20,229.95** | **72u ($720k)** | **+$43,313.72** | **+6.02%** | **50u W / 1u F / 21u L** |
| **Variant 2 — Automated SAR (`1u` Short Covered on Next Long)** | **19u** | **+$28,907.91** | **53u** | **+$11,567.12** | **72u ($720k)** | **+$40,475.03** | **+5.62%** | **51u W / 1u F / 20u L** |
| **Variant 3A — Matched-Stack Reversal (`Nu` Short Open: `2u CAT`, `5u INTC/META`)** | **14u** | **+$23,083.77** | **67u** | **+$41,454.99** | **81u ($810k)** | **+$64,538.76** | **+7.97%** | **59u W / 1u F / 21u L** |
| **Variant 3B — Matched-Stack SAR (`Nu` Short Covered on Next Long)** | **28u** | **+$40,074.61** | **53u** | **+$11,567.12** | **81u ($810k)** | **+$51,641.74** | **+6.38%** | **60u W / 1u F / 20u L** |

### B. Pre-Oct-19 *Fall (Arizona) [2026]* Cohort (`<= 2026-10-12`, 30 Symbols — Excluding the 9 Oct 19 Snapshot Trades)

| *Fall (Arizona) [2026]* Variant (`<= Oct 12`) | Closed Units | Realized PnL ($) | Open Units | Unrealized PnL ($) | Total Units (Notional) | **Combined PnL ($)** | **Return (%)** | Unit Win / Flat / Loss |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| **Variant 1 — As-Logged Multi-Leg (`1u` Compounded Short)** | **14u** | **+$23,083.77** | **49u** | **+$20,815.78** | **63u ($630k)** | **+$43,899.55** | **+6.97%** | **46u W / 1u F / 16u L** |
| **Variant 2 — Automated SAR (`1u` Short Covered on Next Long)** | **18u** | **+$27,345.29** | **45u** | **+$14,010.82** | **63u ($630k)** | **+$41,356.11** | **+6.56%** | **47u W / 1u F / 15u L** |
| **Variant 3A — Matched-Stack (`2u CAT`, `5u INTC/META` Open)** | **14u** | **+$23,083.77** | **58u** | **+$42,040.81** | **72u ($720k)** | **+$65,124.59** | **+9.05%** | **55u W / 1u F / 16u L** |
| **Variant 3B — Matched-Stack SAR (`2u CAT`, `5u INTC/META` Covered)** | **26u** | **+$36,949.37** | **46u** | **+$15,868.69** | **72u ($720k)** | **+$52,818.05** | **+7.34%** | **56u W / 1u F / 15u L** |

---

## Energy EOD Source Note — Current Marks Are Separate from This Oct. 22 Ledger

The approximate Oct. 23 quote comparison formerly shown here was a temporary working note and is withdrawn as a current valuation source. This ledger's existing historical tables remain marked to Oct. 22 and have not been recalculated.

The active core replay and the oil-desk sidecar use the same exact user-provided EOD rows in [`data/energy_provider_eod_marks_v1.csv`](data/energy_provider_eod_marks_v1.csv):

| Symbol | Active EOD source | Coverage | Sessions | Oct. 23 EOD mark |
|---|---|---|---:|---:|
| [`BRENT`](trades/BRENT.txt) | BlackBull Markets Brent Cash | Sep. 23–Oct. 23, 2026 | 23 | `$117.345` |
| [`OIL`](trades/OIL.txt) | TradingView `TVC:USOIL` | Sep. 10–Oct. 23, 2026 | 32 | `$103.45` |

Yahoo `BZ=F` / `CL=F` prices remain pre-entry context proxies only; the active model and sidecar do not use the former approximate quote pair.

## 1. *Fall (Arizona) [2026]* Realized PnL — Closed Exits & Stop-and-Reverse Covers (`1 Unit = $10,000.00`)

| # | Ticker | Side | Units (Notional) | Entry Timestamp | Exit Timestamp | Entry Price | Exit Price | Return (%) | Realized PnL ($) | Active In |
|---:|---|---|---|---|---|---:|---:|---:|---:|---|
| 1 | [**CAT**](trades/CAT.txt) | **LONG** | 1u ($10k) | 2026-09-03 06:30 | 2026-10-06 13:00 | $787.86 | $864.70 | **+9.75%** | **+$975.30** | V1, V2, V3 |
| 2 | [**CAT**](trades/CAT.txt) | **LONG** | 1u ($10k) | 2026-09-17 06:30 | 2026-10-06 13:00 | $785.41 | $864.70 | **+10.10%** | **+$1,009.54** | V1, V2, V3 |
| 3 | [**DIS**](trades/DIS.txt) | **LONG** | 1u ($10k) | 2026-09-03 06:30 | 2026-09-21 06:30 | $107.57 | $104.23 | **−3.10%** | **−$310.50** | V1, V2, V3 |
| 4 | [**INTC**](trades/INTC.txt) | **LONG** | 1u ($10k) | 2026-09-06 06:30 | 2026-09-22 13:00 | $95.80 | $127.11 | **+32.68%** | **+$3,268.27** | V1, V2, V3 |
| 5 | [**INTC**](trades/INTC.txt) | **LONG** | 1u ($10k) | 2026-09-10 06:30 | 2026-09-22 13:00 | $101.19 | $127.11 | **+25.62%** | **+$2,561.52** | V1, V2, V3 |
| 6 | [**INTC**](trades/INTC.txt) | **LONG** | 1u ($10k) | 2026-09-16 06:30 | 2026-09-22 13:00 | $102.25 | $127.11 | **+24.31%** | **+$2,431.30** | V1, V2, V3 |
| 7 | [**INTC**](trades/INTC.txt) | **LONG** | 1u ($10k) | 2026-09-16 06:30 | 2026-09-22 13:00 | $102.05 | $127.11 | **+24.56%** | **+$2,455.66** | V1, V2, V3 |
| 8 | [**INTC**](trades/INTC.txt) | **LONG** | 1u ($10k) | 2026-09-21 06:30 | 2026-09-22 13:00 | $124.14 | $127.11 | **+2.39%** | **+$239.25** | V1, V2, V3 |
| 9 | [**META**](trades/META.txt) | **LONG** | 1u ($10k) | 2026-09-03 06:30 | 2026-09-24 13:00 | $611.35 | $769.46 | **+25.86%** | **+$2,586.24** | V1, V2, V3 |
| 10 | [**META**](trades/META.txt) | **LONG** | 1u ($10k) | 2026-09-11 06:30 | 2026-09-24 13:00 | $648.03 | $769.46 | **+18.74%** | **+$1,873.83** | V1, V2, V3 |
| 11 | [**META**](trades/META.txt) | **LONG** | 1u ($10k) | 2026-09-16 06:30 | 2026-09-24 13:00 | $679.11 | $769.46 | **+13.30%** | **+$1,330.42** | V1, V2, V3 |
| 12 | [**META**](trades/META.txt) | **LONG** | 1u ($10k) | 2026-09-16 06:30 | 2026-09-24 13:00 | $679.24 | $769.46 | **+13.28%** | **+$1,328.25** | V1, V2, V3 |
| 13 | [**META**](trades/META.txt) | **LONG** | 1u ($10k) | 2026-09-21 06:30 | 2026-09-24 13:00 | $710.23 | $769.46 | **+8.34%** | **+$833.96** | V1, V2, V3 |
| 14 | [**PLTR**](trades/PLTR.txt) | **LONG** | 1u ($10k) | 2026-09-13 06:30 | 2026-10-09 06:30 | $167.23 | $209.05 | **+25.01%** | **+$2,500.75** | V1, V2, V3 |
| — | **Subtotal — Variant 1 & 3A Realized (`14 Units`)** | | **14u ($140k)** | | | | | **+16.49%** | **+$23,083.77** | **V1, V3A** |
| 15 | [**CAT**](trades/CAT.txt) | **SHORT *(SAR Cover)*** | 1u ($10k) | 2026-10-06 13:00 | 2026-10-19 06:30 | $864.70 | $729.58 | **+15.63%** | **+$1,562.62** *(V3B `2u`: **+$3,125.25**)* | V2, V3B |
| 16 | [**INTC**](trades/INTC.txt) | **SHORT *(SAR Cover)*** | 1u ($10k) | 2026-09-22 13:00 | 2026-09-28 06:30 | $127.11 | $104.70 | **+17.63%** | **+$1,763.04** *(V3B `5u`: **+$8,815.20**)* | V2, V3B |
| 17 | [**INTC**](trades/INTC.txt) | **SHORT *(SAR Cover)*** | 1u ($10k) | 2026-09-24 10:00 | 2026-09-28 06:30 | $115.11 | $104.70 | **+9.04%** | **+$904.35** | V2, V3B |
| 18 | [**META**](trades/META.txt) | **SHORT *(SAR Cover)*** | 1u ($10k) | 2026-09-24 13:00 | 2026-09-25 10:00 | $769.46 | $720.37 | **+6.38%** | **+$637.98** *(V3B `5u`: **+$3,189.90**)* | V2, V3B |
| 19 | [**PLTR**](trades/PLTR.txt) | **SHORT *(SAR Cover)*** | 1u ($10k) | 2026-09-03 06:30 | 2026-09-13 06:30 | $184.91 | $167.23 | **+9.56%** | **+$956.14** | V2, V3B |
| — | **Subtotal — Variant 2 Realized (`19 Units` incl. SAR Covers)** | | **19u ($190k)** | | | | | **+15.21%** | **+$28,907.91** | **V2** |
| — | **Subtotal — Variant 3B Realized (`28 Units` incl. Matched-Stack SAR Covers)** | | **28u ($280k)** | | | | | **+14.31%** | **+$40,074.61** | **V3B** |

---

## 2. *Fall (Arizona) [2026]* Symbol-by-Symbol Summary (All 32 Tickers — `1 Unit = $10,000.00`)

| Ticker | Oct 22 Mark | *Fall [2026]* Units (`Closed / Open`) | **Var 1 Realized** | **Var 1 Unrealized** | **Var 1 Total PnL** *(1u Short)* | **Var 2 Total PnL** *(SAR)* | **Var 3A Total PnL** *(Matched Nu Short)* |
|---|---:|---|---:|---:|---:|---:|---:|
| [**AAPL**](trades/AAPL.txt) | $348.22 | 0C / 4L | $0.00 | +$1,591.79 | **+$1,591.79** | **+$1,591.79** | **+$1,591.79** |
| [**AMZN**](trades/AMZN.txt) | $250.38 | 0C / 1L | $0.00 | −$317.12 | **−$317.12** | **−$317.12** | **−$317.12** |
| [**BRENT**](trades/BRENT.txt) | $113.17 | 0C / 4L | $0.00 | +$2,437.10 | **+$2,437.10** | **+$2,437.10** | **+$2,437.10** |
| [**BTC**](trades/BTC.txt) | $81,263.73 | 0C / 2L | $0.00 | +$2,920.54 | **+$2,920.54** | **+$2,920.54** | **+$2,920.54** |
| [**CAT**](trades/CAT.txt) | $704.05 | 2C / 1L+1S | +$1,984.84 | +$1,507.94 | **+$3,492.78** | **+$3,197.53** | **+$5,350.65** |
| [**CVX**](trades/CVX.txt) | $226.68 | 0C / 2L | $0.00 | +$1,511.24 | **+$1,511.24** | **+$1,511.24** | **+$1,511.24** |
| [**DIS**](trades/DIS.txt) | $113.13 | 1C / 1S | −$310.50 | −$853.88 | **−$1,164.38** | **−$1,164.38** | **−$1,164.38** |
| [**ETH**](trades/ETH.txt) | $2,381.38 | 0C / 1L | $0.00 | −$190.39 | **−$190.39** | **−$190.39** | **−$190.39** |
| [**GEV**](trades/GEV.txt) | $827.42 | 0C / 1L | $0.00 | −$1,779.81 | **−$1,779.81** | **−$1,779.81** | **−$1,779.81** |
| [**HD**](trades/HD.txt) | $327.73 | 0C / 1L | $0.00 | +$668.64 | **+$668.64** | **+$668.64** | **+$668.64** |
| [**INTC**](trades/INTC.txt) | $85.49 | 5C / 3L+2S | +$10,955.99 | +$188.67 | **+$11,144.66** | **+$7,964.53** | **+$24,241.98** |
| [**LLY**](trades/LLY.txt) | $1,306.69 | 0C / 1L | $0.00 | +$1,080.50 | **+$1,080.50** | **+$1,080.50** | **+$1,080.50** |
| [**LMT**](trades/LMT.txt) | $589.91 | 0C / 4L | $0.00 | +$5,880.21 | **+$5,880.21** | **+$5,880.21** | **+$5,880.21** |
| [**LULU**](trades/LULU.txt) | $104.06 | 0C / 1L | $0.00 | +$844.10 | **+$844.10** | **+$844.10** | **+$844.10** |
| [**META**](trades/META.txt) | $648.85 | 5C / 2L+1S | +$7,952.70 | −$401.02 | **+$7,551.68** | **+$6,622.19** | **+$13,821.53** |
| [**NET**](trades/NET.txt) | $303.61 | 0C / 1L | $0.00 | −$871.34 | **−$871.34** | **−$871.34** | **−$871.34** |
| [**NFLX**](trades/NFLX.txt) | $67.05 | 0C / 1L | $0.00 | −$1.49 | **−$1.49** | **−$1.49** | **−$1.49** |
| [**NVDA**](trades/NVDA.txt) | $212.21 | 0C / 1L | $0.00 | −$757.00 | **−$757.00** | **−$757.00** | **−$757.00** |
| [**OIL**](trades/OIL.txt) | $99.47 | 0C / 4L | $0.00 | +$3,219.53 | **+$3,219.53** | **+$3,219.53** | **+$3,219.53** |
| [**ORCL**](trades/ORCL.txt) | $125.54 | 0C / 1L | $0.00 | −$209.78 | **−$209.78** | **−$209.78** | **−$209.78** |
| [**PEP**](trades/PEP.txt) | $138.83 | 0C / 1L | $0.00 | +$817.36 | **+$817.36** | **+$817.36** | **+$817.36** |
| [**PLTR**](trades/PLTR.txt) | $196.19 | 1C / 3S | +$2,500.75 | −$99.94 | **+$2,400.81** | **+$3,966.98** | **+$2,400.81** |
| [**RIVN**](trades/RIVN.txt) | $12.06 | 0C / 1L | $0.00 | −$1,566.43 | **−$1,566.43** | **−$1,566.43** | **−$1,566.43** |
| [**SPCX**](trades/SPCX.txt) | $144.75 | 0C / 3S | $0.00 | +$2,929.12 | **+$2,929.12** | **+$2,929.12** | **+$2,929.12** |
| [**TMO**](trades/TMO.txt) | $676.54 | 0C / 1L | $0.00 | +$204.38 | **+$204.38** | **+$204.38** | **+$204.38** |
| [**TSLA**](trades/TSLA.txt) | $374.58 | 0C / 1S | $0.00 | −$177.15 | **−$177.15** | **−$177.15** | **−$177.15** |
| [**UPS**](trades/UPS.txt) | $101.52 | 0C / 2S | $0.00 | −$1,519.99 | **−$1,519.99** | **−$1,519.99** | **−$1,519.99** |
| [**V**](trades/V.txt) | $414.34 | 0C / 1L | $0.00 | +$749.51 | **+$749.51** | **+$749.51** | **+$749.51** |
| [**VLO**](trades/VLO.txt) | $426.28 | 0C / 1L | $0.00 | +$51.40 | **+$51.40** | **+$51.40** | **+$51.40** |
| [**WMT**](trades/WMT.txt) | $121.12 | 0C / 1L | $0.00 | +$1,617.11 | **+$1,617.11** | **+$1,617.11** | **+$1,617.11** |
| [**XLE**](trades/XLE.txt) | $67.57 | 0C / 1L | $0.00 | +$756.13 | **+$756.13** | **+$756.13** | **+$756.13** |
| [**XRH0**](trades/XRH0.txt) | $790.00 | 0C / 1L | $0.00 | $0.00 | **$0.00** | **$0.00** | **$0.00** |
| **Total — *Fall (Arizona) [2026]* Portfolio (32 Tickers)** | | **14C / 58O (72u)** | **+$23,083.77** | **+$20,229.95** | **+$43,313.72** | **+$40,475.03** | **+$64,538.76** |

---

## 3. Same-Day Multi-Post Trade Pairs (`2 Units = $20,000.00` per Pair)

| Ticker | Date | Trade 1 (`1u = $10k`) | Trade 2 (`1u = $10k`) | Status | Pair PnL (`2u = $20k`) |
|---|---|---|---|---|---:|
| [**AAPL**](trades/AAPL.txt) | `2026-09-04` | `LONG @ $328.21` (`+$609.67`) | `LONG @ $336.64` (`+$343.99`) | Open Long (`2u`) | **+$953.66** |
| [**INTC**](trades/INTC.txt) | `2026-09-16` | `LONG @ $102.25` (`+$2,431.30`) | `LONG @ $102.05` (`+$2,455.66`) | Closed @ `$127.11` (`2u`) | **+$4,886.95** |
| [**META**](trades/META.txt) | `2026-09-16` | `LONG @ $679.11` (`+$1,330.42`) | `LONG @ $679.24` (`+$1,328.25`) | Closed @ `$769.46` (`2u`) | **+$2,658.67** |
| [**CVX**](trades/CVX.txt) | `2026-09-17` | `LONG @ $210.83` (`+$751.79`) | `LONG @ $210.68` (`+$759.45`) | Open Long (`2u`) | **+$1,511.24** |
| [**UPS**](trades/UPS.txt) | `2026-10-09` | `SHORT @ $94.13` (`−$785.08`) | `SHORT @ $94.57` (`−$734.91`) | Open Short (`2u`) | **−$1,519.99** |

---

## 4. *Fall (Arizona) [2026]* Open Positions Ledger (`58 Open Units` in Variant 1 → Oct 22, 2026 Close)

Ranked across open positions from ***Fall (Arizona) [2026]* exclusively** (`1 Unit = $10,000.00`) as of the October 22, 2026 close:

| # | Ticker | Entry Timestamp | Action | Side | Units | Entry Price | Oct 22 Mark | Implied Qty | Move ($/sh) | Return (%) | Unrealized PnL ($) | SAR / Stack Note |
|---:|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | [**INTC**](trades/INTC.txt) | 2026-09-22 13:00 | `SHORT (Compounded)` | **SHORT** | 1u | $127.11 | $85.49 | 78.6720 | +$41.62 | **+32.74%** | **+$3,274.33** | Covered @ $104.70 in V2; `5u` = **+$16,371.65** in V3A |
| 2 | [**INTC**](trades/INTC.txt) | 2026-09-24 10:00 | `SHORT (Neutral Flip)` | **SHORT** | 1u | $115.11 | $85.49 | 86.8734 | +$29.62 | **+25.73%** | **+$2,573.19** | Covered @ $104.70 in V2 (`+$904.35` R) |
| 3 | [**BTC**](trades/BTC.txt) | 2026-08-01 06:30 | `LONG` | **LONG** | 1u | $65,000.00 | $81,263.73 | 0.1538 | +$16,263.73 | **+25.02%** | **+$2,502.11** | V1, V2, V3 *(Sep 3 Fall post; est. Aug 1 entry)* |
| 4 | [**CAT**](trades/CAT.txt) | 2026-10-06 13:00 | `SHORT (Compounded)` | **SHORT** | 1u | $864.70 | $704.05 | 11.5647 | +$160.65 | **+18.58%** | **+$1,857.87** | Covered @ $729.58 in V2; `2u` = **+$3,715.74** in V3A |
| 5 | [**LMT**](trades/LMT.txt) | 2026-10-08 06:30 | `LONG` | **LONG** | 1u | $499.22 | $589.91 | 20.0312 | +$90.69 | **+18.17%** | **+$1,816.63** | V1, V2, V3 |
| 6 | [**LMT**](trades/LMT.txt) | 2026-10-03 06:30 | `LONG` | **LONG** | 1u | $505.41 | $589.91 | 19.7859 | +$84.50 | **+16.72%** | **+$1,671.91** | V1, V2, V3 |
| 7 | [**SPCX**](trades/SPCX.txt) | 2026-10-06 06:30 | `SHORT` | **SHORT** | 1u | $173.77 | $144.75 | 57.5473 | +$29.02 | **+16.70%** | **+$1,670.02** | V1, V2, V3 |
| 8 | [**LMT**](trades/LMT.txt) | 2026-10-06 06:30 | `LONG` | **LONG** | 1u | $507.17 | $589.91 | 19.7173 | +$82.74 | **+16.31%** | **+$1,631.41** | V1, V2, V3 |
| 9 | [**WMT**](trades/WMT.txt) | 2026-10-03 06:30 | `LONG` | **LONG** | 1u | $104.26 | $121.12 | 95.9141 | +$16.86 | **+16.17%** | **+$1,617.11** | V1, V2, V3 |
| 10 | [**META**](trades/META.txt) | 2026-09-24 13:00 | `SHORT (Compounded)` | **SHORT** | 1u | $769.46 | $648.85 | 12.9961 | +$120.61 | **+15.67%** | **+$1,567.46** | Covered @ $720.37 in V2; `5u` = **+$7,837.31** in V3A |
| 11 | [**OIL**](trades/OIL.txt) | 2026-09-29 06:30 | `LONG` | **LONG** | 1u | $89.30 | $99.47 | 111.9821 | +$10.17 | **+11.39%** | **+$1,138.86** | V1, V2, V3 |
| 12 | [**LLY**](trades/LLY.txt) | 2026-10-12 06:30 | `LONG` | **LONG** | 1u | $1,179.27 | $1,306.69 | 8.4798 | +$127.42 | **+10.80%** | **+$1,080.50** | V1, V2, V3 |
| 13 | [**SPCX**](trades/SPCX.txt) | 2026-10-09 06:30 | `SHORT` | **SHORT** | 1u | $161.59 | $144.75 | 61.8850 | +$16.84 | **+10.42%** | **+$1,042.14** | V1, V2, V3 |
| 14 | [**BRENT**](trades/BRENT.txt) | 2026-09-23 06:30 | `LONG` | **LONG** | 1u | $102.50 | $113.17 | 97.5610 | +$10.67 | **+10.41%** | **+$1,040.98** | V1, V2, V3 |
| 15 | [**OIL**](trades/OIL.txt) | 2026-09-22 06:30 | `LONG` | **LONG** | 1u | $90.20 | $99.47 | 110.8647 | +$9.27 | **+10.28%** | **+$1,027.72** | V1, V2, V3 |
| 16 | [**OIL**](trades/OIL.txt) | 2026-10-08 06:30 | `LONG` | **LONG** | 1u | $90.60 | $99.47 | 110.3753 | +$8.87 | **+9.79%** | **+$979.03** | V1, V2, V3 |
| 17 | [**LULU**](trades/LULU.txt) | 2026-09-17 06:30 | `LONG` | **LONG** | 1u | $95.96 | $104.06 | 104.2101 | +$8.10 | **+8.44%** | **+$844.10** | V1, V2, V3 |
| 18 | [**PEP**](trades/PEP.txt) | 2026-10-09 06:30 | `LONG` | **LONG** | 1u | $128.34 | $138.83 | 77.9180 | +$10.49 | **+8.17%** | **+$817.36** | V1, V2, V3 |
| 19 | [**LMT**](trades/LMT.txt) | 2026-10-19 06:30 | `LONG` | **LONG** | 1u | $548.23 | $589.91 | 18.2405 | +$41.68 | **+7.60%** | **+$760.26** | Oct 19 chart addition |
| 20 | [**CVX**](trades/CVX.txt) | 2026-09-17 06:30 | `LONG` | **LONG** | 1u | $210.68 | $226.68 | 47.4654 | +$16.00 | **+7.59%** | **+$759.45** | V1, V2, V3 |
| 21 | [**XLE**](trades/XLE.txt) | 2026-10-03 06:30 | `LONG` | **LONG** | 1u | $62.82 | $67.57 | 159.1850 | +$4.75 | **+7.56%** | **+$756.13** | V1, V2, V3 |
| 22 | [**CVX**](trades/CVX.txt) | 2026-09-17 06:30 | `LONG` | **LONG** | 1u | $210.83 | $226.68 | 47.4316 | +$15.85 | **+7.52%** | **+$751.79** | V1, V2, V3 |
| 23 | [**V**](trades/V.txt) | 2026-10-12 06:30 | `LONG` | **LONG** | 1u | $385.45 | $414.34 | 25.9437 | +$28.89 | **+7.50%** | **+$749.51** | V1, V2, V3 |
| 24 | [**HD**](trades/HD.txt) | 2026-09-16 06:30 | `LONG` | **LONG** | 1u | $307.19 | $327.73 | 32.5531 | +$20.54 | **+6.69%** | **+$668.64** | V1, V2, V3 |
| 25 | [**BRENT**](trades/BRENT.txt) | 2026-10-09 06:30 | `LONG` | **LONG** | 1u | $106.50 | $113.17 | 93.8967 | +$6.67 | **+6.26%** | **+$626.29** | V1, V2, V3 |
| 26 | [**PLTR**](trades/PLTR.txt) | 2026-10-09 06:30 | `SHORT (Logged w/ Exit)` | **SHORT** | 1u | $209.05 | $196.19 | 47.8354 | +$12.86 | **+6.15%** | **+$615.16** | V1, V2, V3 |
| 27 | [**AAPL**](trades/AAPL.txt) | 2026-09-04 06:30 | `LONG` | **LONG** | 1u | $328.21 | $348.22 | 30.4683 | +$20.01 | **+6.10%** | **+$609.67** | V1, V2, V3 |
| 28 | [**BRENT**](trades/BRENT.txt) | 2026-10-02 06:30 | `LONG` | **LONG** | 1u | $107.00 | $113.17 | 93.4579 | +$6.17 | **+5.77%** | **+$576.64** | V1, V2, V3 |
| 29 | [**BTC**](trades/BTC.txt) | 2026-09-03 06:30 | `LONG` | **LONG** | 1u | $78,000.00 | $81,263.73 | 0.1282 | +$3,263.73 | **+4.18%** | **+$418.43** | V1, V2, V3 |
| 30 | [**AAPL**](trades/AAPL.txt) | 2026-09-24 06:30 | `LONG` | **LONG** | 1u | $335.92 | $348.22 | 29.7690 | +$12.30 | **+3.66%** | **+$366.16** | V1, V2, V3 |
| 31 | [**AAPL**](trades/AAPL.txt) | 2026-09-04 06:30 | `LONG` | **LONG** | 1u | $336.64 | $348.22 | 29.7053 | +$11.58 | **+3.44%** | **+$343.99** | V1, V2, V3 |
| 32 | [**AAPL**](trades/AAPL.txt) | 2026-09-21 06:30 | `LONG` | **LONG** | 1u | $339.00 | $348.22 | 29.4985 | +$9.22 | **+2.72%** | **+$271.98** | V1, V2, V3 |
| 33 | [**SPCX**](trades/SPCX.txt) | 2026-10-19 06:30 | `SHORT` | **SHORT** | 1u | $147.96 | $144.75 | 67.5858 | +$3.21 | **+2.17%** | **+$216.95** | Oct 19 chart addition |
| 34 | [**TMO**](trades/TMO.txt) | 2026-10-06 06:30 | `LONG` | **LONG** | 1u | $662.99 | $676.54 | 15.0832 | +$13.55 | **+2.04%** | **+$204.38** | V1, V2, V3 |
| 35 | [**BRENT**](trades/BRENT.txt) | 2026-10-19 06:30 | `LONG` | **LONG** | 1u | $111.025 | $113.17 | 90.0698 | +$2.145 | **+1.93%** | **+$193.20** | Oct 19 chart addition |
| 36 | [**OIL**](trades/OIL.txt) | 2026-10-19 06:30 | `LONG` | **LONG** | 1u | $98.74 | $99.47 | 101.2761 | +$0.73 | **+0.74%** | **+$73.93** | Oct 19 chart addition |
| 37 | [**VLO**](trades/VLO.txt) | 2026-10-08 06:30 | `LONG` | **LONG** | 1u | $424.10 | $426.28 | 23.5793 | +$2.18 | **+0.51%** | **+$51.40** | V1, V2, V3 |
| 38 | [**XRH0**](trades/XRH0.txt) | 2026-09-03 06:30 | `LONG` | **LONG** | 1u | $790.00 | $790.00 | 12.6582 | $0.00 | **0.00%** | **$0.00** | V1, V2, V3 |
| 39 | [**NFLX**](trades/NFLX.txt) | 2026-10-04 06:30 | `LONG` | **LONG** | 1u | $67.06 | $67.05 | 149.1202 | −$0.01 | **−0.01%** | **−$1.49** | V1, V2, V3 |
| 40 | [**PLTR**](trades/PLTR.txt) | 2026-10-19 06:30 | `SHORT` | **SHORT** | 1u | $194.15 | $196.19 | 51.5066 | −$2.04 | **−1.05%** | **−$105.07** | Oct 19 chart addition |
| 41 | [**TSLA**](trades/TSLA.txt) | 2026-10-19 06:30 | `SHORT` | **SHORT** | 1u | $368.06 | $374.58 | 27.1695 | −$6.52 | **−1.77%** | **−$177.15** | Oct 19 chart addition |
| 42 | [**ETH**](trades/ETH.txt) | 2026-09-03 06:30 | `LONG` | **LONG** | 1u | $2,427.60 | $2,381.38 | 4.1193 | −$46.22 | **−1.90%** | **−$190.39** | V1, V2, V3 |
| 43 | [**ORCL**](trades/ORCL.txt) | 2026-10-19 06:30 | `LONG` | **LONG** | 1u | $128.23 | $125.54 | 77.9849 | −$2.69 | **−2.10%** | **−$209.78** | Oct 19 chart addition |
| 44 | [**AMZN**](trades/AMZN.txt) | 2026-09-21 06:30 | `LONG` | **LONG** | 1u | $258.58 | $250.38 | 38.6728 | −$8.20 | **−3.17%** | **−$317.12** | V1, V2, V3 |
| 45 | [**CAT**](trades/CAT.txt) | 2026-10-19 06:30 | `LONG` | **LONG** | 1u | $729.58 | $704.05 | 13.7065 | −$25.53 | **−3.50%** | **−$349.93** | Oct 19 chart addition |
| 46 | [**PLTR**](trades/PLTR.txt) | 2026-09-03 06:30 | `SHORT` | **SHORT** | 1u | $184.91 | $196.19 | 54.0804 | −$11.28 | **−6.10%** | **−$610.03** | Covered @ $167.23 in V2 (`+$956.14` R) |
| 47 | [**UPS**](trades/UPS.txt) | 2026-10-09 06:30 | `SHORT` | **SHORT** | 1u | $94.57 | $101.52 | 105.7418 | −$6.95 | **−7.35%** | **−$734.91** | V1, V2, V3 |
| 48 | [**NVDA**](trades/NVDA.txt) | 2026-09-03 06:30 | `LONG` | **LONG** | 1u | $229.59 | $212.21 | 43.5559 | −$17.38 | **−7.57%** | **−$757.00** | V1, V2, V3 |
| 51 | [**NET**](trades/NET.txt) | 2026-09-17 06:30 | `LONG` | **LONG** | 1u | $332.59 | $303.61 | 30.0670 | −$28.98 | **−8.71%** | **−$871.34** | V1, V2, V3 |
| 49 | [**UPS**](trades/UPS.txt) | 2026-10-09 06:30 | `SHORT` | **SHORT** | 1u | $94.13 | $101.52 | 106.2361 | −$7.39 | **−7.85%** | **−$785.08** | V1, V2, V3 |
| 50 | [**DIS**](trades/DIS.txt) | 2026-09-21 06:30 | `SHORT` | **SHORT** | 1u | $104.23 | $113.13 | 95.9417 | −$8.90 | **−8.54%** | **−$853.88** | V1, V2, V3 |
| 52 | [**META**](trades/META.txt) | 2026-10-09 06:30 | `LONG` | **LONG** | 1u | $719.00 | $648.85 | 13.9082 | −$70.15 | **−9.76%** | **−$975.66** | V1, V2, V3 |
| 53 | [**INTC**](trades/INTC.txt) | 2026-10-19 06:30 | `LONG` | **LONG** | 1u | $94.865 | $85.49 | 105.4130 | −$9.375 | **−9.88%** | **−$988.25** | Oct 19 chart addition |
| 54 | [**META**](trades/META.txt) | 2026-09-25 10:00 | `REBUY` | **LONG** | 1u | $720.37 | $648.85 | 13.8818 | −$71.52 | **−9.93%** | **−$992.82** | V1, V2, V3 |
| 55 | [**RIVN**](trades/RIVN.txt) | 2026-10-03 06:30 | `LONG` | **LONG** | 1u | $14.30 | $12.06 | 699.3007 | −$2.24 | **−15.66%** | **−$1,566.43** | V1, V2, V3 |
| 56 | [**GEV**](trades/GEV.txt) | 2026-10-09 06:30 | `LONG` | **LONG** | 1u | $1,006.57 | $827.42 | 9.9347 | −$179.15 | **−17.80%** | **−$1,779.81** | V1, V2, V3 |
| 57 | [**INTC**](trades/INTC.txt) | 2026-09-28 06:30 | `LONG` | **LONG** | 1u | $104.70 | $85.49 | 95.5110 | −$19.21 | **−18.35%** | **−$1,834.77** | V1, V2, V3 |
| 58 | [**INTC**](trades/INTC.txt) | 2026-10-04 06:30 | `LONG` | **LONG** | 1u | $119.33 | $85.49 | 83.8012 | −$33.84 | **−28.36%** | **−$2,835.83** | V1, V2, V3 |
| — | **Total — *Fall (Arizona) [2026]* Open Units (`58 Units`)** | | | | **58u ($580k)** | | | | | **+3.49%** | **+$20,229.95** | *V2 (`53u`): `+$11,567.12`; V3A (`67u`): `+$41,454.99`* |

---

## 5. Standardized Unit Valuation Formula

For any *Fall (Arizona) [2026]* position of $U_i$ standardized units ($1\text{ unit} = \$10{,}000.00$, initial notional $N_{0,i} = U_i \times \$10{,}000.00$), entry price $P_{0,i}$, and exit or October 22, 2026 closing mark $P_{1,i}$:

$$Q_i = \frac{U_i \times \$10{,}000.00}{P_{0,i}}, \qquad \Delta P_i = \begin{cases} P_{1,i} - P_{0,i} & \text{if LONG} \\ P_{0,i} - P_{1,i} & \text{if SHORT} \end{cases}, \qquad \text{PnL}_i (\$) = Q_i \times \Delta P_i = U_i \times \$10{,}000.00 \times \frac{\Delta P_i}{P_{0,i}}$$

---

## 6. Model Performance Comparison

The four portfolio-model variants above (**V1 · V2 · V3A · V3B**) are compared
**day by day** across the same `35` *Fall (Arizona) [2026]* sessions in
**[`Model Performance Comparison.md`](Model%20Performance%20Comparison.md)**, with an
interactive explorer at
**[`Model Performance Explorer.html`](Model%20Performance%20Explorer.html)** and
machine-readable series in [`data/`](data/).
