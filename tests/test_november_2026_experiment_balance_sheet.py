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
    ending = by_line["Profit-only cash carry-forward subtotal"]
    lcid = by_line["LCID open position — market value snapshot"]
    ref_sum = by_line["Unreconciled simple sum: profit-only subtotal plus LCID market value"]

    assert opening["balance_sheet_name"] == "Harshal's Private Fund"
    assert opening["experiment"] == "November 2026++ Experiment"
    assert text.startswith("# Harshal's Private Fund")
    assert Decimal(opening["amount_usd"]) == Decimal("2396569687.95")
    assert Decimal(brent["amount_usd"]) == Decimal("933875016.74")
    assert Decimal(usoil["amount_usd"]) == Decimal("1779605629.28")
    assert Decimal(additions["amount_usd"]) == Decimal("2713480646.02")
    assert Decimal(principal["amount_usd"]) == Decimal("0.00")
    assert Decimal(ending["amount_usd"]) == Decimal("5110050333.97")
    assert lcid["ticker"] == "LCID"
    assert lcid["action"] == "Open LONG per screenshot"
    assert lcid["quantity"] == "299401198.6"
    assert Decimal(lcid["cost_basis_usd"]) == Decimal("1000000003.32")
    assert Decimal(lcid["snapshot_price_usd"]) == Decimal("3.33")
    assert Decimal(lcid["market_value_usd"]) == Decimal("997005991.34")
    assert Decimal(lcid["unrealized_pnl_usd"]) == Decimal("-2994011.99")
    assert lcid["unrealized_pnl_pct"] == "-0.30%"
    assert Decimal(ref_sum["amount_usd"]) == Decimal("6107056325.31")
    assert ref_sum["classification"] == "Not a reconciled fund total"
    assert (ROOT / lcid["source_artifact"]).is_file()
    assert "not added to the profit-only cash subtotal" in text
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
    assert "the **$5,110,050,333.97** profit-only subtotal combines that selected prior estimate" in text
    assert "does **not** carry forward principal" in text
    assert (ARCHIVE / "IMG_1218.png").is_file()
    assert (ARCHIVE / "IMG_1217.png").is_file()


def test_readme_links_profit_only_balance_sheet():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "Harshal%27s%20Private%20Fund" in readme
    assert REPORT.exists()
