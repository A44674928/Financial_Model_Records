import csv
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports" / "Harshal's Private Fund — November 2026++ Experiment.md"
CSV_PATH = ROOT / "data" / "november_2026_plus_plus_experiment_balance_sheet_v1.csv"
ARCHIVE = ROOT / "Archive" / "November_2026_Experiment_Oil_Closes_2026-10-29"


def test_profit_only_balance_excludes_user_voided_oil_closes_and_keeps_source_values():
    text = REPORT.read_text(encoding="utf-8")
    with CSV_PATH.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    by_line = {row["balance_sheet_line"]: row for row in rows}
    opening = by_line["Prior profit-only carry-in"]
    brent = by_line["BRENT close order — nullified and voided per user instruction"]
    usoil = by_line["USOIL close order — nullified and voided per user instruction"]
    additions = by_line["Total new realized-PnL additions (nullified/voided oil closes)"]
    principal = by_line["Principal carried into experiment"]
    ending = by_line["Profit-only cash carry-forward subtotal"]
    lcid = by_line["LCID open position — market value snapshot"]
    lcid_buy = by_line["LCID filled buy order — unmarked lot"]
    ref_sum = by_line["Unreconciled simple sum: profit-only subtotal plus LCID market value"]

    assert opening["balance_sheet_name"] == "Harshal's Private Fund"
    assert opening["experiment"] == "November 2026++ Experiment"
    assert text.startswith("# Harshal's Private Fund")
    assert Decimal(opening["amount_usd"]) == Decimal("2396569687.95")
    assert Decimal(brent["amount_usd"]) == Decimal("0.00")
    assert Decimal(usoil["amount_usd"]) == Decimal("0.00")
    assert Decimal(brent["source_reported_pnl_usd"]) == Decimal("933875016.74")
    assert Decimal(usoil["source_reported_pnl_usd"]) == Decimal("1779605629.28")
    assert Decimal(additions["amount_usd"]) == Decimal("0.00")
    assert Decimal(additions["source_reported_pnl_usd"]) == Decimal("2713480646.02")
    assert Decimal(principal["amount_usd"]) == Decimal("0.00")
    assert Decimal(ending["amount_usd"]) == Decimal("2396569687.95")
    assert lcid["ticker"] == "LCID"
    assert lcid["action"] == "Open LONG per screenshot"
    assert lcid["quantity"] == "299401198.6"
    assert Decimal(lcid["cost_basis_usd"]) == Decimal("1000000003.32")
    assert Decimal(lcid["snapshot_price_usd"]) == Decimal("3.33")
    assert Decimal(lcid["market_value_usd"]) == Decimal("997005991.34")
    assert Decimal(lcid["unrealized_pnl_usd"]) == Decimal("-2994011.99")
    assert lcid["unrealized_pnl_pct"] == "-0.30%"
    assert Decimal(lcid_buy["amount_usd"]) == Decimal("999999999.98")
    assert lcid_buy["quantity"] == "301204819.27"
    assert lcid_buy["average_entry_price_usd"] == "3.32"
    assert lcid_buy["order_id"] == "3736492349"
    assert lcid_buy["as_of_date"] == "2026-10-29 11:05:57; timezone not shown"
    assert (ROOT / lcid_buy["source_artifact"]).is_file()
    assert Decimal(ref_sum["amount_usd"]) == Decimal("3393575679.29")
    assert ref_sum["classification"] == "Not a reconciled fund total"
    assert "No aggregate quantity or combined market value is inferred" in text
    assert (ROOT / lcid["source_artifact"]).is_file()
    assert "not recognized as realized" in text
    assert (Decimal(brent["quantity"]) * (Decimal(brent["close_price_usd"]) - Decimal(brent["average_entry_price_usd"]))).quantize(Decimal("0.01")) == Decimal(brent["source_reported_pnl_usd"])
    assert (Decimal(usoil["quantity"]) * (Decimal(usoil["close_price_usd"]) - Decimal(usoil["average_entry_price_usd"]))).quantize(Decimal("0.01")) == Decimal(usoil["source_reported_pnl_usd"])
    assert "nullified and voided" in text
    assert "earlier longs remain open" in text
    assert brent["quantity"] == "538566907"
    assert brent["average_entry_price_usd"] == "114.043000"
    assert brent["close_price_usd"] == "115.777"
    assert brent["as_of_date"] == "2026-10-29 10:41:44; timezone not shown"
    assert usoil["quantity"] == "601218118"
    assert usoil["average_entry_price_usd"] == "99.180000"
    assert usoil["close_price_usd"] == "102.14"
    assert usoil["as_of_date"] == "2026-10-29 10:41:38; timezone not shown"
    open_oil = [row for row in rows if row["ticker"] in {"BRENT", "USOIL"} and row["balance_sheet_line"].endswith("open after close nullification")]
    assert len(open_oil) == 2
    assert {(row["ticker"], row["quantity"], row["average_entry_price_usd"]) for row in open_oil} == {
        ("BRENT", "538566907", "114.043000"), ("USOIL", "601218118", "99.180000")
    }
    assert all(row["action"].startswith("LONG OPEN") and not row["snapshot_price_usd"] and not row["market_value_usd"] and not row["unrealized_pnl_usd"] for row in open_oil)
    assert all(Decimal(row["amount_usd"] or "0") == 0 for row in open_oil)
    assert "not independently audited brokerage executions" in text
    assert "$5,110,050,333.97" not in text
    assert "The current **$2,396,569,687.95** profit-only carry-forward" in text
    assert "does **not** carry forward principal" in text
    assert (ARCHIVE / "IMG_1218.png").is_file()
    assert (ARCHIVE / "IMG_1217.png").is_file()


def test_readme_links_profit_only_balance_sheet():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "Harshal%27s%20Private%20Fund" in readme
    assert REPORT.exists()
