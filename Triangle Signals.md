# Triangle Signals — October 19, 2026 screenshots

Dates and prices of the recorded **green**, **orange** and **red** triangle annotations on the charts in
`Archive/October 19th 2026.zip` (10 screenshots, 9 unique — see `Charts/`).

- **Triangle dates** are read from each chart's own time axis, converted to trading sessions.
- **Triangle prices** are read from each chart's price scale (the levels are logarithmic), at the point of the triangle.
  Expect roughly ±1 % precision, ±1 session on daily charts, ±1 week on the weekly chart.
- **Current prices below** are transcribed from the numeric screenshot labels, not estimated from the axes.

## Price-point key

| Color / symbol | Label | Meaning |
|---|---|---|
| 🟢 **x** | **Long** | Green marks a long point. |
| 🔴 **y** | **Short** | Red marks a short point. |
| 🟠 **z** | **Hazard** | Orange marks a warning, not a long or short entry. |

The letters are lowercase. Annotated chart copies show the letter in its actual color, beside a ring
around the latest plotted price point. Each copy also includes the full key and its displayed price
in a footer; the original JPEGs and ZIP are unchanged.

## Current price points — October 19, 2026 screenshots

**“Current” means the price displayed in the screenshot, not a live market quote.** Each x/y label
follows that screenshot's existing **LONG/SHORT badge**, not the latest historical triangle or the
day's price change. No screenshot explicitly marks its current price as a warning, so no new current
**z — Hazard** signal is inferred. Existing orange triangle entries below are labeled **z — Hazard**.

<!-- current-prices:start -->
| Ticker | Chart | Current displayed price (USD) | Label | Annotated chart |
|---|---|---|---|---|
| **BRENT** | 1D | **$111.025** | 🟢 **x — Long** | [View labeled chart](Charts/BRENT/BRENT-2026-10-19-labeled.png) |
| **CAT** | 1D | **$729.58** | 🟢 **x — Long** | [View labeled chart](Charts/CAT/CAT-2026-10-19-labeled.png) |
| **INTC** | 1D | **$94.865** | 🟢 **x — Long** | [View labeled chart](Charts/INTC/INTC-2026-10-19-labeled.png) |
| **LMT** | 1D | **$548.23** | 🟢 **x — Long** | [View labeled chart](Charts/LMT/LMT-2026-10-19-labeled.png) |
| **OIL** | 1D | **$98.74** | 🟢 **x — Long** | [View labeled chart](Charts/OIL/OIL-2026-10-19-labeled.png) |
| **ORCL** | 1D | **$128.23** | 🟢 **x — Long** | [View labeled chart](Charts/ORCL/ORCL-2026-10-19-labeled.png) |
| **PLTR** | 1D | **$194.15** | 🔴 **y — Short** | [View labeled chart](Charts/PLTR/PLTR-2026-10-19-labeled.png) |
| **SPCX** | 1W | **$147.96** | 🔴 **y — Short** | [View labeled chart](Charts/SPCX/SPCX-2026-10-19-labeled.png) |
| **TSLA** | 1W | **$368.06** | 🔴 **y — Short** | [View labeled chart](Charts/TSLA/TSLA-2026-10-19-labeled.png) |
<!-- current-prices:end -->

Source values, capture times (local, as named in the files), and marker placement coordinates are in
[Current Price Points.csv](Current%20Price%20Points.csv). Prices are in the displayed USD units;
OIL is quoted in USD per barrel. Projected candles, targets, and support/resistance levels are **not**
used as current prices — in particular, SPCX uses **$147.96**, not its future target near $45.

## Green triangles — x · Long

| Ticker | Chart | Date | Price (level marked) | Point label | Bias on chart |
|---|---|---|---|---|---|
| **PLTR** | Palantir · 1D | Fri **Sep 11, 2026** | **≈ $166** | 🟢 **x — Long** | SHORT |
| **LMT** | Lockheed Martin · 1D | Wed **Oct 7, 2026** | **≈ $502** | 🟢 **x — Long** | LONG |
| **LMT** | Lockheed Martin · 1D | Mon **Oct 12, 2026** | **≈ $496** | 🟢 **x — Long** | LONG |
| **OIL** | WTI Crude CFD · 1D | Thu **Oct 8, 2026** | **≈ $90.6** | 🟢 **x — Long** | LONG |
| **BRENT** | Brent Crude · 1D | Wed **Sep 23, 2026** | **≈ $102.5** | 🟢 **x — Long** | LONG |
| **BRENT** | Brent Crude · 1D | Fri **Oct 9, 2026** | **≈ $106.5** | 🟢 **x — Long** | LONG |
| **CAT** | Caterpillar · 1D | Mon **Sep 14, 2026** | **≈ $780** | 🟢 **x — Long** | LONG |

The historical point label and the chart's overall bias are separate: PLTR's old green point is
**x — Long**, while its current price gets **y — Short** from the screenshot's SHORT badge.
The original triangle shapes are preserved in both the source and annotated images.

## Orange triangles — z · Hazard

| Ticker | Chart | Date | Price (level marked) | Point label | Bias on chart |
|---|---|---|---|---|---|
| **LMT** | Lockheed Martin · 1D | Fri **Oct 9, 2026** | **≈ $514** | 🟠 **z — Hazard** | LONG |
| **LMT** | Lockheed Martin · 1D | Fri **Oct 19, 2026** | **≈ $548** | 🟠 **z — Pending Hazard** | LONG |
| **OIL** | WTI Crude CFD · 1D | Tue **Sep 22, 2026** | **≈ $90.2** | 🟠 **z — Hazard** | LONG |
| **OIL** | WTI Crude CFD · 1D | Tue **Sep 29, 2026** | **≈ $89.3** | 🟠 **z — Hazard** | LONG |
| **BRENT** | Brent Crude · 1D | Fri **Oct 2, 2026** | **≈ $107.0** | 🟠 **z — Hazard** | LONG |
| **CAT** | Caterpillar · 1D | Tue **Oct 6, 2026** | **≈ $867** | 🟠 **z — Hazard** | LONG |
| **INTC** | Intel · 1D | Mon **Sep 28, 2026** | **≈ $117** | 🟠 **z — Hazard** | LONG |

Orange triangle/dot annotations are **Hazard** warning points under this key, even when the
screenshot has an overall LONG badge. They are not relabeled as long entries.

## Red triangles — y · Short

| Ticker | Chart | Date | Price (level marked) | Point label | Bias on chart |
|---|---|---|---|---|---|
| **PLTR** | Palantir · 1D | Fri **Oct 9, 2026** | **≈ $211** (high ≈ $215) | 🔴 **y — Short** | SHORT |
| **SPCX** | SpaceX · **1W** | week of Mon **Sep 28, 2026** | **≈ $176** | 🔴 **y — Short** | SHORT |

Red triangle annotations use **y — Short** under this key.

## Charts with no recorded triangles

These charts still receive a **current-price** label from their original LONG/SHORT badge.

| Ticker | Chart | Current-price label | Screenshot |
|---|---|---|---|
| **TSLA** | Tesla · 1W (weekly range levels only) | 🔴 **y — Short** | `Charts/TSLA/` |
| **ORCL** | Oracle · 1D (Fibonacci envelope levels only) | 🟢 **x — Long** | `Charts/ORCL/` |

## Original screenshot → ticker map

| File | Ticker | Captured (local) | Recorded triangles |
|---|---|---|---|
| `Charts/PLTR/PLTR 2026-10-19 21.45.17.jpeg` | PLTR | 9:45:17 PM | 1 green, 1 red |
| `Charts/LMT/LMT 2026-10-19 21.45.30.jpeg` | LMT | 9:45:30 PM | 2 green, 1 orange |
| `Charts/SPCX/SPCX 2026-10-19 21.45.39.jpeg` | SPCX | 9:45:39 PM | 1 red (weekly) |
| `Charts/TSLA/TSLA 2026-10-19 21.45.50.jpeg` | TSLA | 9:45:50 PM | none |
| `Charts/OIL/OIL 2026-10-19 21.46.00.jpeg` | OIL (WTI) | 9:46:00 PM | 2 orange, 1 green |
| `Charts/BRENT/BRENT 2026-10-19 21.46.08.jpeg` | BRENT | 9:46:08 PM | 2 green, 1 orange |
| `Charts/CAT/CAT 2026-10-19 21.46.16.jpeg` | CAT | 9:46:16 PM | 1 green, 1 orange |
| `Charts/INTC/INTC 2026-10-19 21.46.26.jpeg` | INTC | 9:46:26 PM | 1 orange |
| `Charts/ORCL/ORCL 2026-10-19 21.46.46.jpeg` | ORCL | 9:46:46 PM | none |

`Archive/duplicates/OIL 2026-10-19 21.46.00 (duplicate).jpeg` is a byte-identical copy of the OIL screenshot,
so it is stored once under `Charts/OIL/` and the spare copy is kept in `Archive/duplicates/`.

## Reproduce the labels

The CSV is the source of truth for the **current-price** table and annotated PNGs. The historical
triangle dates/prices above are the earlier approximate readings; this labeling update does not
recalculate them or turn them into current signals.

Requires Python 3.9+, Pillow, and DejaVu Sans regular/bold fonts. From the repository root:

```sh
python3 -m pip install -r scripts/requirements.txt
python3 scripts/label_current_prices.py
python3 -m unittest discover -s tests -v
```

On systems with fonts elsewhere, pass `--font-dir /path/to/dejavu` to the labeling script.
It writes separate `Charts/<TICKER>/<TICKER>-2026-10-19-labeled.png` files and updates only the
current-price table in this report. It does not alter the source screenshots or archive.
