import csv
import hashlib
import sys
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from model_perf_core import PRICES, UNMODELED_SYMBOLS, parse_trades  # noqa: E402


def test_user_directed_aliusd_position_is_recorded_without_inventing_trade_timing():
    with (ROOT / "data/aliusd_user_directed_position_v1.csv").open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 1
    row = rows[0]
    assert (row["ticker"], row["side"]) == ("ALIUSD", "LONG")
    assert row["raw_platform_quantity"] == "15546506"
    assert row["initial_user_notional_usd"] == "20000000000.00"
    assert row["user_corrected_entry_price_usd"] == "2999.99"
    assert row["recomputed_all_cash_entry_notional_usd"] == "46639362534.94"
    assert row["source_csv_avg_fill_price_usd"] == "3008.70"
    assert row["source_csv_last_price_usd"] == "3070.60"
    assert row["recomputed_conditional_mark_pnl_usd"] == "1097738788.66"
    assert row["source_csv_reported_leverage"] == "50x" and row["leverage_used"] == "false"
    assert (row["position_date"], row["position_time"]) == ("not supplied", "not supplied")
    assert row["source_chart_created_at"] == "2026-10-28 10:20 UTC-7"
    assert row["chart_snapshot_price_usd"] == "3066.10"
    assert "not verified EOD account PnL" in row["valuation_status"]


def test_aliusd_is_preserved_but_excluded_from_core_model_until_marks_exist():
    assert "ALIUSD" in UNMODELED_SYMBOLS
    assert "ALIUSD" not in PRICES
    assert not any(event["sym"] == "ALIUSD" for event in parse_trades())
    trade_record = (ROOT / "trades/ALIUSD.txt").read_text(encoding="utf-8")
    assert "position/order date and time were not supplied" in trade_record
    assert "not an entry/order time" in trade_record
    assert "No ALIUSD EOD series" in trade_record and "position trade date is supplied" in trade_record
    with ZipFile(ROOT / "trades.zip") as archive:
        assert archive.read("trades/ALIUSD.txt") == (ROOT / "trades/ALIUSD.txt").read_bytes()
        assert archive.read("trades/index.txt") == (ROOT / "trades/index.txt").read_bytes()


def test_archived_aliusd_chart_is_preserved_and_identified_as_unverified_context():
    image = ROOT / "Archive/ALIUSD_LONG_2026-10-28/ALUMINUM_2026-10-28_10-20-33.png"
    assert image.is_file()
    assert hashlib.sha256(image.read_bytes()).hexdigest() == "90ac1a6855268b81291e00c2706c9a246eaa955e2829ed04fa557e470d414526"
    source_csv = ROOT / "Archive/ALIUSD_LONG_2026-10-28/paper-trading-positions-2026-10-28T17_41_25.410Z.csv"
    assert hashlib.sha256(source_csv.read_bytes()).hexdigest() == "eb6b800911916d4e989231ef6cc39dd6a3681e50be9c7b2068c2dabae9e67576"
    report = (ROOT / "reports/ALIUSD User-Directed LONG Position.md").read_text(encoding="utf-8")
    assert "$46,639,362,534.94" in report
    assert "$2,999.99" in report
    assert "$1,097,738,788.66" in report
    assert "supersedes the earlier $20B notional sizing" in report
    assert "bookkeeping fields only" in report and "no leverage, borrowing, or financing" in report
    assert "position-entry date/time" in report
    assert "not used for the conditional calculation above" in report
    assert "no funding source or combined account total is inferred" in report
