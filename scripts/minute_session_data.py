"""Yahoo Finance 1-minute INTC close observations for the Sep 24 hazard-flip window.

Source: Yahoo Finance chart API, interval=1m, period1=1790269200,
period2=1790272800, retrieved 2026-10-23. Timestamps are bar opens; the
60 closes below cover bars opening 10:00–10:59 MST (close labels 10:01–11:00).
Yahoo's trailing regularMarketTime/zero-volume artifact is intentionally omitted.
"""

SYMBOL = "INTC"
SESSION_DATE = "2026-09-24"
WINDOW_START = "10:00"
WINDOW_END = "11:00"
BAR_SECONDS = 60
START_EPOCH = 1790269200
LOGGED_ENTRY_PRICE = 115.11

CLOSES_1M = [
    125.59, 125.79, 125.83, 125.94, 126.055, 126.19, 126.0558, 126.195,
    126.26, 126.0451, 125.89, 125.77, 125.64, 125.81, 125.765, 125.51,
    125.55, 125.50, 125.84, 125.70, 125.799, 125.74, 125.645, 125.745,
    125.545, 125.46, 125.375, 125.515, 125.61, 125.62, 125.71, 125.825,
    125.715, 125.5703, 125.3699, 125.42, 125.4767, 125.48, 125.305,
    125.37, 125.55, 125.4316, 125.42, 125.30, 125.19, 125.13, 125.21,
    125.35, 125.305, 125.42, 125.46, 125.29, 125.12, 125.08, 124.95,
    124.93, 125.15, 125.15, 125.17, 125.155,
]
