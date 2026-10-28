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
    assert row["notional_usd"] == "20000000000.00"
    assert row["user_specified_entry_price_usd"] == "3000.00"
    assert row["price_divided_notional_equivalent"] == "6666666.66666667"
    assert (row["position_date"], row["position_time"]) == ("not supplied", "not supplied")
    assert row["source_chart_created_at"] == "2026-10-28 10:20 UTC-7"
    assert row["displayed_chart_price_usd"] == "3066.10"
    assert "not EOD valuation" in row["displayed_price_use"]


def test_aliusd_is_preserved_but_excluded_from_core_model_until_marks_exist():
    assert "ALIUSD" in UNMODELED_SYMBOLS
    assert "ALIUSD" not in PRICES
    assert not any(event["sym"] == "ALIUSD" for event in parse_trades())
    trade_record = (ROOT / "trades/ALIUSD.txt").read_text(encoding="utf-8")
    assert "position/order date and time were not supplied" in trade_record
    assert "not an entry/order time" in trade_record
    assert "no ALIUSD EOD series or trade date" in trade_record
    with ZipFile(ROOT / "trades.zip") as archive:
        assert archive.read("trades/ALIUSD.txt") == (ROOT / "trades/ALIUSD.txt").read_bytes()
        assert archive.read("trades/index.txt") == (ROOT / "trades/index.txt").read_bytes()


def test_archived_aliusd_chart_is_preserved_and_identified_as_unverified_context():
    image = ROOT / "Archive/ALIUSD_LONG_2026-10-28/ALUMINUM_2026-10-28_10-20-33.png"
    assert image.is_file()
    assert hashlib.sha256(image.read_bytes()).hexdigest() == "90ac1a6855268b81291e00c2706c9a246eaa955e2829ed04fa557e470d414526"
    report = (ROOT / "reports/ALIUSD User-Directed LONG Position.md").read_text(encoding="utf-8")
    assert "$20,000,000,000.00" in report
    assert "$3,000.00" in report
    assert "position's entry/order time" in report and "source chart only" in report
    assert "not as a verified EOD close" in report
    assert "no funding source or combined account total is inferred" in report
