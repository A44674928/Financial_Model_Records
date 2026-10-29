import csv
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports" / "Harshal's Private Fund — November 2026++ Experiment.md"
CSV_PATH = ROOT / "data" / "november_2026_plus_plus_experiment_balance_sheet_v1.csv"


def test_profit_only_opening_balance_excludes_principal_and_preserves_provenance():
    text = REPORT.read_text(encoding="utf-8")
    with CSV_PATH.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    opening = next(row for row in rows if row["balance_sheet_line"] == "Profit-only opening cash balance")
    principal = next(row for row in rows if row["balance_sheet_line"] == "Principal carried into experiment")
    net_assets = next(row for row in rows if row["balance_sheet_line"] == "Net assets / opening balance")

    assert opening["balance_sheet_name"] == "Harshal's Private Fund"
    assert opening["experiment"] == "November 2026++ Experiment"
    assert text.startswith("# Harshal's Private Fund")
    assert Decimal(opening["amount_usd"]) == Decimal("2396569687.95")
    assert Decimal(principal["amount_usd"]) == Decimal("0.00")
    assert Decimal(net_assets["amount_usd"]) == Decimal("2396569687.95")
    assert "No principal" in text
    assert "not an independently reconciled fill-level realized-PnL figure" in text
    assert "higher endpoint" in text


def test_readme_links_profit_only_balance_sheet():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "November%202026%2B%2B%20Experiment" in readme
    assert REPORT.exists()
