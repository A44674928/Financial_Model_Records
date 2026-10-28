import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "Archive/Oil_Chart_Set_2026-10-28"


def test_three_oil_chart_sources_are_archived_and_hash_preserved():
    expected = {
        "USOIL/USOIL_2026-10-28_11-04-08.png": "3447efb8a0a634400b61f28123814a76f63502473e6440cf0bde84d435a966fd",
        "BRENT/BRENT_2026-10-28_11-05-21.png": "e229b2fe61aa90b6911efca634dbc213d2e01c5a889206124ce87f65ceb44395",
        "BRENT/BRENT_2026-10-28_11-05-00.png": "46604b7cda54f9da119ca764394bf6d6a5d2e30e10d7623f0a66df919df3870c",
        "BRENT/BRENT_2026-10-28_11-12-12.png": "3e3a01abc755bceace092bf5fad699d35f903e79bf6706749eedfb5bc8ff6f12",
    }
    for relative_path, digest in expected.items():
        image = ARCHIVE / relative_path
        assert image.is_file()
        assert hashlib.sha256(image.read_bytes()).hexdigest() == digest


def test_gallery_preserves_chart_context_without_inventing_positions_or_eod_marks():
    gallery = (ROOT / "reports/Oil Chart Set — 2026-10-28.md").read_text(encoding="utf-8")
    assert "USOIL / WTI — recent daily view" in gallery
    assert "BRENT — recent daily view" in gallery
    assert "BRENT — late-September to late-October close view" in gallery
    assert "BRENT — broader 2026 daily view" in gallery
    assert "four user-supplied daily charts" in gallery
    assert "$117.108000" in gallery and "11:12 UTC−7" in gallery
    assert "$102.780000" in gallery
    assert "$117.087000" in gallery and "$117.108000" in gallery
    assert "not supplied EOD closes" in gallery
    assert "No position direction, entry, or trade is inferred" in gallery
    assert "does not change existing BRENT/OIL position sizes" in gallery
