"""Legacy audit of the temporary approximate energy quote comparison.

This module is not imported by current model or sidecar builders. Current active
marks for both use the exact daily series in
`data/energy_provider_eod_marks_v1.csv`; Yahoo BZ=F/CL=F are pre-entry proxies
only. The older overlay data is retained solely for audit traceability and is
not a current valuation source.
"""

import csv
from decimal import Decimal, ROUND_HALF_UP
from html import escape
from pathlib import Path

from daily_closes import OCT23_EOD_SOURCES
from model_perf_core import PRICES, UNIT, build_lots, parse_trades

ROOT = Path(__file__).resolve().parents[1]
EOD_MARK_DATE = "2026-10-23"
LIVE_MARK_DATE = "2026-10-23"
LIVE_MARKS = {"BRENT": Decimal("115.72"), "OIL": Decimal("100.94")}
DISPLAY = {
    "BRENT": {
        "instrument": "BlackBull Brent Cash (trade log)",
        "price_source": "User-provided BlackBull Brent Cash daily EOD",
    },
    "OIL": {
        "instrument": "TradingView TVC:USOIL WTI CFD (trade index)",
        "price_source": "User-provided TradingView TVC:USOIL daily EOD",
    },
}
QUOTE_BASIS = "User-provided approximate quote; provider/time not specified"
_CENT = Decimal("0.01")


def _money(value):
    return Decimal(str(value)).quantize(_CENT, rounding=ROUND_HALF_UP)


def overlay_rows():
    """Calculate marked open PnL for the two energy books at both mark sets."""
    events = parse_trades()
    lots, realized = build_lots("V1", events)
    out = []
    for sym in ("BRENT", "OIL"):
        open_lots = [lot for lot in lots if lot["sym"] == sym and lot["open"]]
        realized_pnl = sum((r["pnl"] for r in realized if r["sym"] == sym), 0.0)
        eod_mark = Decimal(str(PRICES[sym][-1]))
        live_mark = LIVE_MARKS[sym]

        def mark_unrealized(mark):
            total = Decimal("0")
            for lot in open_lots:
                sign = Decimal("1") if lot["side"] == "long" else Decimal("-1")
                qty = Decimal(str(lot["qty"]))
                entry = Decimal(str(lot["entry_px"]))
                total += sign * qty * Decimal(str(UNIT)) * (mark / entry - 1)
            return total

        eod_unrealized = mark_unrealized(eod_mark)
        live_unrealized = mark_unrealized(live_mark)
        out.append({
            "symbol": sym,
            "trade_instrument": DISPLAY[sym]["instrument"],
            "historical_price_source_basis": DISPLAY[sym]["price_source"],
            "eod_source": OCT23_EOD_SOURCES[sym],
            "historical_mark_date": EOD_MARK_DATE,
            "historical_mark_usd": str(eod_mark),
            "historical_realized_pnl_usd": str(_money(realized_pnl)),
            "historical_unrealized_pnl_usd": str(_money(eod_unrealized)),
            "live_mark_date": LIVE_MARK_DATE,
            "live_mark_usd": str(live_mark),
            "live_quote_basis": QUOTE_BASIS,
            "live_realized_pnl_usd": str(_money(realized_pnl)),
            "live_unrealized_pnl_usd": str(_money(live_unrealized)),
            "change_from_historical_mark_usd": str(_money(live_unrealized - eod_unrealized)),
            "open_lots": str(len(open_lots)),
            "open_units": str(sum(lot["qty"] for lot in open_lots)),
        })
    return out


def write_overlay(path=None):
    path = Path(path) if path else ROOT / "data" / "energy_live_mark_overlay.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = overlay_rows()
    fields = list(rows[0])
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return path


def inject_html_overlay(html_path, rows=None, chart_path=None):
    """Add an idempotent energy quote/source card to the standalone Explorer."""
    rows = rows or overlay_rows()
    html_path = Path(html_path)
    chart_path = Path(chart_path) if chart_path else ROOT / "Charts" / "performance" / "14-energy-live-mark-overlay.png"
    chart_rel = chart_path.relative_to(ROOT).as_posix() if chart_path.is_absolute() else chart_path.as_posix()
    html = html_path.read_text(encoding="utf-8")
    card_id = '  <div class="card" id="energy-live-overlay">'
    if card_id in html:
        start = html.index(card_id)
        end = html.index("  </div>\n\n", start) + len("  </div>\n\n")
        html = html[:start] + html[end:]

    def pnl(value):
        value = float(value)
        sign = "+" if value >= 0 else "-"
        return f"{sign}${abs(value):,.2f}"

    def price(value):
        decimal = Decimal(str(value))
        places = max(2, -decimal.as_tuple().exponent)
        return f"${decimal:,.{places}f}"

    table_rows = []
    for row in rows:
        table_rows.append(
            "<tr>"
            f"<td><b>{row['symbol']}</b></td>"
            f"<td>{escape(row['eod_source'])}</td>"
            f"<td>{price(row['historical_mark_usd'])}</td>"
            f"<td>{pnl(row['historical_unrealized_pnl_usd'])}</td>"
            f"<td>{price(row['live_mark_usd'])}</td>"
            f"<td>{pnl(row['live_unrealized_pnl_usd'])}</td>"
            f"<td>{pnl(row['change_from_historical_mark_usd'])}</td>"
            "</tr>"
        )
    card = f'''{card_id}
    <h2>Energy EOD and approximate-quote comparison</h2>
    <p class="hint">The Oct 23 closes and all active-position dates use the exact user-provided BlackBull Brent Cash
       and TradingView <code>TVC:USOIL</code> EOD marks. Before each series begins (pre-entry context only),
       the historical arrays retain Yahoo <code>BZ=F</code>/<code>CL=F</code> proxies. The card compares the
       exact terminal marks with separate approximate user quotes whose provider/time were not specified.
       Approximate quotes are not mixed into portfolio totals.</p>
    <p><img src="{chart_rel}" alt="Oct 23 EOD and separate approximate energy quotes" style="max-width:100%;height:auto"></p>
    <div class="scroll"><table><thead><tr><th>Symbol</th><th>EOD source</th><th>Oct 23 EOD close</th>
      <th>EOD unrealized</th><th>Approx. quote</th><th>Approx. unrealized</th>
      <th>Change vs. EOD</th></tr></thead><tbody>{''.join(table_rows)}</tbody></table></div>
    <p class="hint"><a href="data/energy_live_mark_overlay.csv">Download mark/source audit (CSV)</a></p>
  </div>

'''
    marker = '  <div class="card">\n    <h2>Full session table</h2>'
    if marker not in html:
        raise ValueError("Explorer full-session card marker not found")
    html = html.replace(marker, card + marker, 1)
    html_path.write_text(html, encoding="utf-8")
    return html_path


if __name__ == "__main__":
    print(write_overlay().relative_to(ROOT))
    for row in overlay_rows():
        print(f"{row['symbol']}: {row['open_lots']} lots; "
              f"historical {row['historical_unrealized_pnl_usd']} -> "
              f"live estimate {row['live_unrealized_pnl_usd']} "
              f"(delta {row['change_from_historical_mark_usd']})")
