import copy
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_whole_portfolio_dxy_view as dxy_view
from model_perf_core import SESSION_DATES, VARIANTS, all_series
from us10y_adjustment import apply_us10y_adjustment


def test_uploaded_daily_inputs_cover_all_model_sessions_and_terminal_marks():
    dxy = dxy_view.read_daily_column(dxy_view.DXY_FILE, "Date", "Close")
    fx = dxy_view.read_fx_daily()
    dxy_view.validate_terminal_marks(dxy, fx)

    assert len(SESSION_DATES) == 35
    assert dxy["2026-09-03"] == 98.95
    assert dxy["2026-10-22"] == 102.22
    assert fx["EURUSD"]["2026-10-22"] == 1.0728
    assert fx["JPYUSD"]["2026-10-22"] == 0.006734


def test_entry_date_fx_baselines_and_daily_marks_are_rebased_as_selected():
    _, fx, _, _, _, result = dxy_view.build_daily_series()
    eur_entry_index = SESSION_DATES.index("2026-09-15")
    jpy_first_session_index = SESSION_DATES.index("2026-09-08")
    for variant in VARIANTS:
        assert result[variant]["fx_eur_usd"][eur_entry_index] == 0
        jpy_first_session = dxy_view.UNIT * (
            fx["JPYUSD"]["2026-09-08"] / fx["JPYUSD"]["2026-09-07"] - 1
        )
        assert abs(result[variant]["fx_jpy_usd"][jpy_first_session_index] - jpy_first_session) < 1e-8
        eur_expected = dxy_view.UNIT * (1.0728 / fx["EURUSD"]["2026-09-15"] - 1)
        jpy_expected = dxy_view.UNIT * (0.006734 / fx["JPYUSD"]["2026-09-07"] - 1)
        assert abs(result[variant]["fx_eur_usd"][-1] - eur_expected) < 1e-8
        assert abs(result[variant]["fx_jpy_usd"][-1] - jpy_expected) < 1e-8


def test_whole_book_numeraire_uses_usd_account_value_over_dxy_not_a_dxy_lot():
    dxy, _, _, _, _, result = dxy_view.build_daily_series()
    terminal = SESSION_DATES.index("2026-10-22")
    start = 0
    for variant in VARIANTS:
        usd_value = result[variant]["usd_account_value"][terminal]
        dxy_value = result[variant]["dxy_equivalent_value"][terminal]
        expected = usd_value / dxy["2026-10-22"]
        assert abs(dxy_value - expected) < 1e-10
        assert abs(result[variant]["dxy_equivalent_value"][start] -
                   dxy_view.CAPITAL_BASIS_USD[variant] / dxy[SESSION_DATES[start]]) < 1e-10
        expected_return = (expected / result[variant]["dxy_equivalent_value"][start] - 1) * 100
        assert abs(result[variant]["dxy_return_pct"][terminal] - expected_return) < 1e-10


def test_us30y_holiday_mark_is_forward_filled_with_provenance_and_oct23_is_excluded():
    marks, sources = dxy_view.read_us30y_daily()
    assert marks["2026-10-12"] == 5.6
    assert sources["2026-10-12"] == "2026-10-09"
    assert SESSION_DATES[-1] == "2026-10-22"
    assert "2026-10-23" not in SESSION_DATES


def test_us10y_carry_preserves_established_core_model_basis():
    core, _ = all_series()
    expected = copy.deepcopy(core)
    expected_rows = apply_us10y_adjustment(expected, SESSION_DATES)
    _, cumulative = dxy_view.established_us10y_carry(core, expected_rows)
    for variant in VARIANTS:
        assert cumulative[variant] == expected[variant]["yield_adjustment"]


def test_exported_csvs_are_complete_and_oct22_values_reconcile():
    dxy, fx, us30y, source_dates, core, result = dxy_view.build_daily_series()
    dxy_view.write_daily_csv(dxy, fx, us30y, source_dates, core, result)
    dxy_view.write_summary_csv(result, fx, dxy)
    with dxy_view.DAILY_CSV.open(newline="", encoding="utf-8") as fh:
        daily_rows = list(csv.DictReader(fh))
    with dxy_view.SUMMARY_CSV.open(newline="", encoding="utf-8") as fh:
        summary_rows = list(csv.DictReader(fh))
    assert len(daily_rows) == len(VARIANTS) * len(SESSION_DATES)
    assert len(summary_rows) == len(VARIANTS)
    assert daily_rows[-1]["session_date"] == "2026-10-22"
    assert daily_rows[-1]["dxy_close"] == "102.22"
    assert daily_rows[-1]["jpyusd_daily_close"] == "0.006734"
    holiday = next(row for row in daily_rows if row["session_date"] == "2026-10-12")
    assert holiday["us30y_source_date"] == "2026-10-09"
