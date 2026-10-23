"""Separate approximate live energy marks from the Oct 22 historical backtest.

The mark inputs are user-provided on 2026-10-23; the quote provider and exact
observation time were not supplied. Historical daily series still use Yahoo
BZ=F (Brent futures) and CL=F (WTI futures), which are proxies rather than the
exact BRENT Cash / TVC:USOIL instruments named in the trade metadata.
"""

import csv
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

from model_perf_core import PRICES, UNIT, build_lots, parse_trades

ROOT = Path(__file__).resolve().parents[1]
LIVE_MARK_DATE = "2026-10-23"
LIVE_MARKS = {"BRENT": Decimal("115.72"), "OIL": Decimal("100.94")}
DISPLAY = {
    "BRENT": {
        "instrument": "Brent Cash / ICE Brent (trade log)",
        "history_proxy": "Yahoo BZ=F Brent futures",
    },
    "OIL": {
        "instrument": "TVC:USOIL WTI CFD (trade index)",
        "history_proxy": "Yahoo CL=F WTI futures",
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
        prior_mark = Decimal(str(PRICES[sym][-1]))
        live_mark = LIVE_MARKS[sym]

        def mark_unrealized(mark):
            total = Decimal("0")
            for lot in open_lots:
                sign = Decimal("1") if lot["side"] == "long" else Decimal("-1")
                qty = Decimal(str(lot["qty"]))
                entry = Decimal(str(lot["entry_px"]))
                total += sign * qty * Decimal(str(UNIT)) * (mark / entry - 1)
            return total

        prior_unrealized = mark_unrealized(prior_mark)
        live_unrealized = mark_unrealized(live_mark)
        out.append({
            "symbol": sym,
            "trade_instrument": DISPLAY[sym]["instrument"],
            "historical_price_proxy": DISPLAY[sym]["history_proxy"],
            "historical_mark_date": "2026-10-22",
            "historical_mark_usd": str(prior_mark),
            "historical_realized_pnl_usd": str(_money(realized_pnl)),
            "historical_unrealized_pnl_usd": str(_money(prior_unrealized)),
            "live_mark_date": LIVE_MARK_DATE,
            "live_mark_usd": str(live_mark),
            "live_quote_basis": QUOTE_BASIS,
            "live_realized_pnl_usd": str(_money(realized_pnl)),
            "live_unrealized_pnl_usd": str(_money(live_unrealized)),
            "change_from_historical_mark_usd": str(_money(live_unrealized - prior_unrealized)),
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
        writer = csv.DictWriter(f, fieldnames=fields)
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

    table_rows = []
    for row in rows:
        table_rows.append(
            "<tr>"
            f"<td><b>{row['symbol']}</b></td>"
            f"<td>${float(row['historical_mark_usd']):,.2f}</td>"
            f"<td>{pnl(row['historical_unrealized_pnl_usd'])}</td>"
            f"<td>${float(row['live_mark_usd']):,.2f}</td>"
            f"<td>{pnl(row['live_unrealized_pnl_usd'])}</td>"
            f"<td>{pnl(row['change_from_historical_mark_usd'])}</td>"
            "</tr>"
        )
    card = f'''{card_id}
    <h2>Energy quote reconciliation — indicative Oct 23 marks</h2>
    <p class="hint">Historical comparison remains at Oct 22. It uses Yahoo
       <code>BZ=F</code>/<code>CL=F</code> futures proxies; the trade metadata names Brent
       Cash / ICE Brent and <code>TVC:USOIL</code>. User-supplied live quotes are approximate;
       provider and timestamp were not specified. These two live marks are not mixed into
       the Oct 22 portfolio totals.</p>
    <p><img src="{chart_rel}" alt="Separate historical and approximate live energy mark comparison" style="max-width:100%;height:auto"></p>
    <div class="scroll"><table><thead><tr><th>Symbol</th><th>Oct 22 mark</th>
      <th>Oct 22 unrealized</th><th>Approx. live mark</th><th>Live unrealized</th>
      <th>Change</th></tr></thead><tbody>{''.join(table_rows)}</tbody></table></div>
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
