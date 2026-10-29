import csv
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports" / "Harshal's Private Fund — November 2026++ Experiment.md"
CSV_PATH = ROOT / "data" / "november_2026_plus_plus_experiment_balance_sheet_v1.csv"
ARCHIVE = ROOT / "Archive" / "November_2026_Experiment_Oil_Closes_2026-10-29"


def test_profit_only_balance_adds_screenshot_reported_close_pnl():
    text = REPORT.read_text(encoding="utf-8")
    with CSV_PATH.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    by_line = {row["balance_sheet_line"]: row for row in rows}
    opening = by_line["Prior profit-only carry-in"]
    brent = by_line["BRENT realized PnL added"]
    usoil = by_line["USOIL realized PnL added"]
    additions = by_line["Total new realized-PnL additions"]
    principal = by_line["Principal carried into experiment"]
    ending = by_line["Ending profit-only experiment balance"]

    assert opening["balance_sheet_name"] == "Harshal's Private Fund"
    assert opening["experiment"] == "November 2026++ Experiment"
    assert text.startswith("# Harshal's Private Fund")
    assert Decimal(opening["amount_usd"]) == Decimal("2396569687.95")
    assert Decimal(brent["amount_usd"]) == Decimal("933875016.74")
    assert Decimal(usoil["amount_usd"]) == Decimal("1779605629.28")
    assert Decimal(additions["amount_usd"]) == Decimal("2713480646.02")
    assert Decimal(principal["amount_usd"]) == Decimal("0.00")
    assert Decimal(ending["amount_usd"]) == Decimal("5110050333.97")
    assert (Decimal(brent["quantity"]) * (Decimal(brent["close_price_usd"]) - Decimal(brent["average_entry_price_usd"]))).quantize(Decimal("0.01")) == Decimal(brent["amount_usd"])
    assert Decimal(usoil["quantity"]) * (Decimal(usoil["close_price_usd"]) - Decimal(usoil["average_entry_price_usd"])) == Decimal(usoil["amount_usd"])
    assert "mapping to the separate earlier locked-foundation estimate is unspecified" in text
    assert brent["quantity"] == "538566907"
    assert brent["average_entry_price_usd"] == "114.043000"
    assert brent["close_price_usd"] == "115.777"
    assert brent["as_of_date"] == "2026-10-29 10:41:44; timezone not shown"
    assert usoil["quantity"] == "601218118"
    assert usoil["average_entry_price_usd"] == "99.180000"
    assert usoil["close_price_usd"] == "102.14"
    assert usoil["as_of_date"] == "2026-10-29 10:41:38; timezone not shown"
    assert "not independently audited brokerage executions" in text
    assert "$5,110,050,333.97" in text
    assert "ending figure combines that selected prior estimate" in text
    assert "does **not** carry forward principal" in text
    assert (ARCHIVE / "IMG_1218.png").is_file()
    assert (ARCHIVE / "IMG_1217.png").is_file()


def test_readme_links_profit_only_balance_sheet():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "Harshal%27s%20Private%20Fund" in readme
    assert REPORT.exists()
