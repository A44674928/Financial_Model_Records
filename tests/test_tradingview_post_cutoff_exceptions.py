import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_tradingview_post_cutoff_exceptions as exceptions  # noqa: E402


def test_existing_post_cutoff_tradingview_artifacts_are_flagged_not_recomputed():
    rows = exceptions.build()
    by_artifact = {row["artifact"]: row for row in rows}
    assert len(rows) == 109
    assert sum(int(row["post_cutoff_record_count"]) for row in rows) == 1145
    assert "data/tradingview_benchmark_session_marks_20261026.csv" in by_artifact
    session_marks = by_artifact["data/tradingview_benchmark_session_marks_20261026.csv"]
    assert session_marks["first_post_cutoff_date"] == "2026-10-20"
    assert session_marks["last_post_cutoff_date"] == "2026-10-26"
    assert session_marks["policy_status"] == "EXISTING_EXCEPTION_FLAGGED; PRESERVED; NOT_RECOMPUTED"
    assert "Archive/November_2026_Experiment_Oil_Closes_2026-10-29/IMG_1217.png" in by_artifact
    assert "trades/OIL.txt" in by_artifact

    with (ROOT / "data/tradingview_post_cutoff_exceptions_v1.csv").open(newline="", encoding="utf-8") as handle:
        persisted = list(csv.DictReader(handle))
    assert len(persisted) == len(rows)
    by_artifact = {row["artifact"]: row for row in persisted}
    assert by_artifact["data/tradingview_benchmark_session_marks_20261026.csv"]["policy_status"] == "EXISTING_EXCEPTION_FLAGGED; PRESERVED; NOT_RECOMPUTED"
    assert by_artifact["reports/Oil Portfolio — 2026-10-26 Update.md"]["policy_status"].startswith("USER_AUTHORIZED_SCOPED_OIL_V2")
    assert by_artifact["data/oil_position_audit_sheet_v1.csv"]["policy_status"] == "USER_AUTHORIZED_OIL_AUDIT_SHEET; SCENARIOS LABELED; NOT NETTED"
    assert by_artifact["reports/Multi-Asset Account Statement — 2026-10-28.md"]["policy_status"] == "USER_AUTHORIZED_MULTI_ASSET_REGISTER; SOURCE_BOOKS_SEPARATED; NO_NET_TOTAL"
    assert by_artifact["reports/Account Change Log — 2026-10-29.md"]["policy_status"] == "USER_AUTHORIZED_OCT29_CHANGE_LOG; TRANSACTIONS_AND_CONTROLS_SEPARATED"
    assert all(row["policy_status"] in {
        "EXISTING_EXCEPTION_FLAGGED; PRESERVED; NOT_RECOMPUTED",
        "USER_AUTHORIZED_SCOPED_OIL_V2; MARKS_THROUGH_2026-10-26; NO_POST_CUTOFF_TRADE_EVENTS",
        "USER_AUTHORIZED_OIL_AUDIT_SHEET; SCENARIOS LABELED; NOT NETTED",
        "USER_AUTHORIZED_MULTI_ASSET_REGISTER; SOURCE_BOOKS_SEPARATED; NO_NET_TOTAL",
        "USER_AUTHORIZED_OCT29_CHANGE_LOG; TRANSACTIONS_AND_CONTROLS_SEPARATED",
    } for row in persisted)
    policy = (ROOT / "reports" / "TradingView Post-October 19 Block Policy.md").read_text()
    assert "**107 artifact/record groups**" in policy
    assert "**1,142 rows" in policy


def test_active_benchmark_rebuild_is_blocked_by_post_cutoff_inputs():
    sys.path.insert(0, str(ROOT / "scripts"))
    import build_tradingview_benchmark as benchmark  # noqa: E402

    try:
        benchmark.build()
    except ValueError as exc:
        assert "Refusing to rebuild active TradingView benchmark" in str(exc)
    else:
        raise AssertionError("post-cutoff TradingView data must block the default benchmark rebuild")
