import csv
import subprocess
import sys
import unittest
import zipfile
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_brent_119_exit as builder

REGISTER = ROOT / "data/brent_sold_119_20261030_v1.csv"
CHANGE_LOG = ROOT / "data/account_change_log_2026-10-30_v1.csv"
AUDIT_SHEET = ROOT / "data/oil_position_audit_sheet_v1.csv"
CLEAN_SHEET = ROOT / "data/november_2026_oil_clean_sheet_v1.csv"
PF_BALANCE = ROOT / "data/november_2026_plus_plus_experiment_balance_sheet_v1.csv"
LEDGER = ROOT / "trades/BRENT.txt"
REPORT = ROOT / "reports/BRENT Full Exit at $119 — 2026-10-30.md"
POLICY = ROOT / "reports/TradingView Post-October 19 Block Policy.md"

SALE = Decimal("119")
EXCEPTION = "USER_DIRECTED_POST_CUTOFF_EXIT_SCOPED_EXCEPTION_20261030"

# Per-book price-only realized PnL at $119, before costs.
EXPECTED_BOOK_PNL = {
    "Private Fund / TradingView Paper Trading": Decimal("2669676158.00"),
    "ATS locked $200 LONG foundation / $20B Units Experiment pool": Decimal("1898059402.97"),
    "THE WINNING MODEL — 50U transferred from the oil foundation": Decimal("17391.30"),
    "Core paper-trade ledger replay": Decimal("52827.16"),
    "Oil portfolio v2 / November 2026 Oil Clean Sheet": Decimal("35076.52"),
    "ATS and Manual Live Position Reconciliation": Decimal("32985.41"),
}

# Rows excluded from every book subtotal because they are scenario/sensitivity,
# legacy-baseline, or Under-Duress overlay rows the user scoped out.
SCENARIO_ROW_TYPES = {
    "UNDER_DURESS_RESTORED_LONG",
    "REINSTATED_NULLIFIED_SHORT_LIFECYCLE",
    "ATS_SCENARIO_RESIDUAL_LONG",
    "LEGACY_BASELINE_SHORT_EVENT",
    "REPORTED_LIQUIDATION_REFERENCE",
}


def rows(path):
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


class BrentFullExitRegisterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = rows(REGISTER)
        cls.by_id = {row["record_id"]: row for row in cls.rows}

    def test_register_covers_every_real_book_at_a_single_119_price(self):
        self.assertEqual(len(self.rows), 22)
        self.assertEqual(len(self.by_id), 22, "record IDs must be unique")
        for row in self.rows:
            self.assertEqual(row["ticker"], "BRENT")
            self.assertEqual(row["side"], "LONG")
            self.assertEqual(Decimal(row["sale_price_usd"]), SALE)
            self.assertEqual(row["sale_date"], "2026-10-30")
            self.assertTrue(row["position_state_after"].startswith("CLOSED — SOLD AT $119"))
            self.assertEqual(row["policy_label"], EXCEPTION)
            self.assertIn("not an independently verified brokerage fill",
                          row["execution_verification_status"])
            self.assertTrue(row["price_only_realized_pnl_usd"],
                            f"missing PnL on {row['record_id']}")
        self.assertEqual(set(EXPECTED_BOOK_PNL),
                         {row["book_or_model"] for row in self.rows})

    def test_per_book_price_only_pnl_matches_expected(self):
        totals = {}
        for row in self.rows:
            if row["book_subtotal_treatment"].startswith("WITHIN_BOOK_COMPONENT"):
                continue
            book = row["book_or_model"]
            totals[book] = totals.get(book, Decimal(0)) + Decimal(row["price_only_realized_pnl_usd"])
        self.assertEqual(set(totals), set(EXPECTED_BOOK_PNL))
        for book, expected in EXPECTED_BOOK_PNL.items():
            self.assertEqual(totals[book].quantize(Decimal("0.01")), expected, book)

    def test_pnl_formulas_are_correct_for_both_unit_conventions(self):
        for row in self.rows:
            entry = Decimal(row["entry_price_usd"])
            qty = Decimal(row["quantity"])
            if row["quantity_unit"].startswith("U ("):
                expected = qty * Decimal(10000) * (SALE / entry - Decimal(1))
                self.assertIn("(sale_price / entry_price - 1)", row["pnl_formula"])
            else:
                expected = qty * (SALE - entry)
                self.assertIn("quantity x (sale_price - entry_price)", row["pnl_formula"])
            self.assertEqual(
                Decimal(row["price_only_realized_pnl_usd"]),
                expected.quantize(Decimal("0.01")),
                row["record_id"],
            )

    def test_ats_foundation_ties_to_its_component_legs(self):
        combined = self.by_id["BRENT119-ATS-FOUNDATION"]
        residual = self.by_id["BRENT119-ATS-POOL-RESIDUAL"]
        supplemental = self.by_id["BRENT119-ATS-SUPPLEMENTAL"]
        self.assertTrue(combined["book_subtotal_treatment"].startswith("PRIMARY"))
        for leg in (residual, supplemental):
            self.assertTrue(leg["book_subtotal_treatment"].startswith("WITHIN_BOOK_COMPONENT"),
                            "component legs must be excluded from the subtotal")
        self.assertLess(
            abs(Decimal(combined["quantity"])
                - Decimal(residual["quantity"]) - Decimal(supplemental["quantity"])),
            Decimal("0.000001"))
        self.assertLessEqual(
            abs(Decimal(combined["price_only_realized_pnl_usd"])
                - Decimal(residual["price_only_realized_pnl_usd"])
                - Decimal(supplemental["price_only_realized_pnl_usd"])),
            Decimal("0.02"))
        self.assertEqual(combined["gross_basis_usd"], "19505877052.37")

    def test_core_ledger_closes_exactly_100_units_across_nine_lots(self):
        core = [r for r in self.rows if r["book_or_model"] == "Core paper-trade ledger replay"]
        self.assertEqual(len(core), 9)
        self.assertEqual(sum(Decimal(r["quantity"]) for r in core), Decimal("100"))
        self.assertEqual(sum(Decimal(r["gross_basis_usd"]) for r in core), Decimal("1000000.00"))
        # Lots already exited earlier must not be re-closed.
        entries = {(r["entry_date"], r["entry_price_usd"]) for r in core}
        self.assertNotIn(("2026-10-26", "115.51"), entries, "paired 50U lot was already sold at $117.409")
        self.assertNotIn(("2026-10-23", "117.00"), entries, "legacy trim/short are excluded")

    def test_private_fund_books_pnl_without_inferring_a_cash_basis(self):
        pf = self.by_id["BRENT119-PF-538566907"]
        self.assertEqual(pf["quantity"], "538566907")
        self.assertEqual(pf["entry_price_usd"], "114.043")
        self.assertEqual(pf["price_only_realized_pnl_usd"], "2669676158.00")
        self.assertEqual(pf["gross_basis_usd"], "",
                         "this source book deliberately infers no cash basis")
        self.assertEqual(pf["model_implied_gross_proceeds_usd"], "")
        self.assertEqual(Decimal(pf["quantity"]) * (SALE - Decimal("114.043")),
                         Decimal("2669676157.999"))

    def test_private_fund_exit_supersedes_the_voided_october_29_close(self):
        pf = self.by_id["BRENT119-PF-538566907"]
        self.assertEqual(pf["supersedes_record_id"], "PRIVATE_TV_BRENT_CLOSE_20261029")
        self.assertEqual(pf["superseded_close_price_evidence_usd"], "115.777")
        self.assertEqual(pf["superseded_close_pnl_evidence_usd"], "933875016.74")
        self.assertNotEqual(pf["price_only_realized_pnl_usd"], "933875016.74",
                            "the superseded screenshot PnL must not be booked")

    def test_cross_book_overlaps_are_flagged_and_never_summed(self):
        overlaps = [r for r in self.rows if r["overlap_flag"] != "NONE"]
        self.assertTrue(overlaps, "known overlaps must be flagged")
        for row in overlaps:
            combined = (row["additivity_rule"] + row["overlap_flag"] + row["notes"]).lower()
            self.assertTrue("do not" in combined or "not additive" in combined,
                            f"overlap row must warn against summing: {row['record_id']}")
        # The two 10U manual replenishments appear in both the core ledger and the
        # ATS/manual reconciliation.
        for price in ("115.792", "114.800"):
            matches = [r for r in self.rows
                       if Decimal(r["entry_price_usd"]) == Decimal(price)
                       and r["quantity_unit"].startswith("U (")]
            self.assertEqual(len(matches), 2, price)
            books = {m["book_or_model"] for m in matches}
            self.assertIn("Core paper-trade ledger replay", books)
            self.assertIn("ATS and Manual Live Position Reconciliation", books)

    def test_scenario_and_sensitivity_rows_are_excluded(self):
        # The user scoped this exit to REAL positions: the Under-Duress overlay and
        # the 10U/20U/30U/40U ATS sensitivities must not appear in the register.
        for row in self.rows:
            self.assertNotIn("Under-Duress", row["book_or_model"])
            self.assertNotIn("sensitivity", row["book_scope"].lower())
        joined = " ".join(row["record_id"] + row["lot_id"] for row in self.rows).upper()
        for forbidden in ("SENSITIVITY", "UNDER-DURESS", "SHORT-LIFECYCLE"):
            self.assertNotIn(forbidden, joined)

    def test_book_subtotals_sum_rounded_per_lot_values(self):
        """Ledger convention: each lot is booked at cents and subtotals sum those.

        Summing unrounded values instead differs by a few cents; the rounded
        per-lot sum is authoritative, matching Core Portfolio Asset Breakdown.md.
        """
        for book in ("Core paper-trade ledger replay",
                     "Oil portfolio v2 / November 2026 Oil Clean Sheet"):
            sel = [r for r in self.rows if r["book_or_model"] == book]
            rounded = sum(Decimal(r["price_only_realized_pnl_usd"]) for r in sel)
            unrounded = Decimal(0)
            for r in sel:
                entry, qty = Decimal(r["entry_price_usd"]), Decimal(r["quantity"])
                unrounded += (qty * Decimal(10000) * (SALE / entry - Decimal(1))
                              if r["quantity_unit"].startswith("U (") else qty * (SALE - entry))
            self.assertEqual(rounded.quantize(Decimal("0.01")), EXPECTED_BOOK_PNL[book], book)
            self.assertLessEqual(abs(rounded - unrounded), Decimal("0.05"),
                                 f"{book}: rounding drift exceeds a few cents")

    def test_builder_is_reproducible(self):
        before = REGISTER.read_bytes()
        subprocess.run([sys.executable, str(ROOT / "scripts/build_brent_119_exit.py")],
                       check=True, capture_output=True, cwd=ROOT)
        self.assertEqual(REGISTER.read_bytes(), before,
                         "the builder must regenerate the register byte-for-byte")


class BrentLedgerAndAuditSheetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ledger_text = LEDGER.read_text(encoding="utf-8")
        cls.audit = rows(AUDIT_SHEET)
        cls.brent_audit = [r for r in cls.audit if r["ticker"] == "BRENT"]

    def test_ledger_has_nine_lot_specific_119_exits(self):
        exits = [line for line in self.ledger_text.splitlines()
                 if line.startswith("2026-10-30") and "$119.00" in line]
        self.assertEqual(len(exits), 9)
        units = sum(Decimal(part.split()[0]) for line in exits
                    for part in [line.split("size: [")[1].split(" units")[0]])
        self.assertEqual(units, Decimal("100"))
        for line in exits:
            self.assertIn("USER-DIRECTED FULL BRENT EXIT AT $119", line)
            self.assertIn(EXCEPTION, line)
            self.assertIn("execution not independently verified", line)

    def test_trades_zip_stays_synchronized_with_the_ledger_tree(self):
        with zipfile.ZipFile(ROOT / "trades.zip") as archive:
            names = [n for n in archive.namelist() if not n.endswith("/")]
            for name in names:
                self.assertEqual(archive.read(name), (ROOT / name).read_bytes(),
                                 f"trades.zip is out of sync for {name}")
        self.assertIn("trades/BRENT.txt", names)

    def test_audit_sheet_closes_real_brent_rows_only(self):
        closed = [r for r in self.brent_audit
                  if r["position_state"].startswith("CLOSED — SOLD AT $119")]
        self.assertEqual(len(closed), 13)
        for row in closed:
            self.assertEqual(row["exit_date"], "2026-10-30")
            self.assertEqual(row["exit_price_usd"], "119.00")
            self.assertTrue(Decimal(row["realized_pnl_usd"]) > 0)
            self.assertIn(EXCEPTION, row["brent_119_exit_note"])

    def test_audit_sheet_leaves_scenario_rows_untouched(self):
        scenario = [r for r in self.brent_audit if r["row_type"] in SCENARIO_ROW_TYPES
                    and r["position_id"] != "PF-BRENT-CLOSE-20261029"]
        self.assertTrue(scenario)
        for row in scenario:
            self.assertNotEqual(row["exit_price_usd"], "119.00",
                                f"scenario row must not be closed: {row['position_id']}")
            self.assertNotEqual(row["exit_date"], "2026-10-30",
                                f"scenario row must not be dated to this exit: {row['position_id']}")
            note = row["brent_119_exit_note"]
            self.assertTrue(note.startswith("NOT AFFECTED") or note.startswith("SUPERSEDED REFERENCE"),
                            f"scenario row must explain its treatment: {row['position_id']}")
        sensitivities = [r for r in self.brent_audit
                         if "ATS exit sensitivity" in r["scenario_id"]]
        self.assertEqual(len(sensitivities), 4)
        for row in sensitivities:
            self.assertEqual(row["exit_price_usd"], "")

    def test_audit_sheet_non_brent_rows_are_untouched(self):
        for row in self.audit:
            if row["ticker"] != "BRENT":
                self.assertEqual(row["brent_119_exit_note"], "")
                self.assertNotEqual(row["exit_price_usd"], "119.00")

    def test_private_fund_void_is_lifted_in_the_audit_sheet(self):
        pf = next(r for r in self.brent_audit if r["position_id"] == "PF-BRENT-CLOSE-20261029")
        self.assertIn("LIFTED AND SUPERSEDED", pf["source_nullification_state"])
        self.assertIn("$115.777", pf["source_nullification_state"])
        self.assertEqual(pf["exit_price_usd"], "119.00")
        self.assertEqual(pf["realized_pnl_usd"], "2669676158.00")
        self.assertIn("USOIL close remained NULLIFIED AND VOIDED", pf["test_override_state"])


class DependentBookTests(unittest.TestCase):
    def test_november_clean_sheet_closes_both_oil_symbols(self):
        sheet = rows(CLEAN_SHEET)
        brent = next(r for r in sheet if r["ticker"].startswith("BRENT"))
        usoil = next(r for r in sheet if r["ticker"].startswith("USOIL"))
        self.assertTrue(brent["position_status"].startswith("CLOSED — SOLD AT $119"))
        self.assertEqual(brent["user_directed_exit_price_usd"], "119.00")
        self.assertEqual(brent["private_fund_exit_price_only_realized_pnl_usd"], "2669676158.00")
        self.assertEqual(brent["ats_foundation_exit_price_only_realized_pnl_usd"], "1898059402.97")
        self.assertEqual(brent["oil_v2_exit_price_only_realized_pnl_usd_per_variant"], "35076.52")
        self.assertEqual(brent["exit_policy_label"], EXCEPTION)
        # The subsequent separate USOIL instruction closes its lot too.
        self.assertTrue(usoil["position_status"].startswith("CLOSED — SOLD AT $104.50"))
        self.assertEqual(usoil["user_directed_exit_price_usd"], "104.50")
        self.assertEqual(usoil["private_fund_exit_price_only_realized_pnl_usd"], "3198480387.76")

    def test_private_fund_balance_books_both_exits(self):
        sheet = rows(PF_BALANCE)
        subtotal = next(r for r in sheet
                        if r["balance_sheet_line"].startswith("Profit-only cash carry-forward subtotal"))
        self.assertEqual(Decimal(subtotal["amount_usd"]), Decimal("8264726233.71"))
        additions = next(r for r in sheet
                         if r["balance_sheet_line"].startswith("Total new realized-PnL additions"))
        self.assertEqual(Decimal(additions["amount_usd"]), Decimal("5868156545.76"))
        carry_in = next(r for r in sheet if r["balance_sheet_line"] == "Prior profit-only carry-in")
        self.assertEqual(Decimal(carry_in["amount_usd"]) + Decimal(additions["amount_usd"]),
                         Decimal(subtotal["amount_usd"]))
        unreconciled = next(r for r in sheet
                            if r["balance_sheet_line"].startswith("Unreconciled simple sum"))
        self.assertEqual(Decimal(unreconciled["amount_usd"]), Decimal("9261732225.05"))

        brent_close = next(r for r in sheet if r["ticker"] == "BRENT"
                           and r["balance_sheet_line"].startswith("BRENT close order"))
        self.assertEqual(brent_close["close_price_usd"], "119.00")
        self.assertEqual(Decimal(brent_close["amount_usd"]), Decimal("2669676158.00"))
        self.assertEqual(brent_close["source_reported_pnl_usd"], "933875016.74",
                         "the superseded screenshot PnL must remain visible as evidence")

        # USOIL is now independently closed under a later instruction.
        usoil = [r for r in sheet if r["ticker"] == "USOIL"]
        self.assertEqual(len(usoil), 2)
        close = next(r for r in usoil if r["balance_sheet_line"].startswith("USOIL close order"))
        self.assertEqual(close["amount_usd"], "3198480387.76")
        self.assertEqual(close["close_price_usd"], "104.50")
        self.assertEqual(close["source_reported_pnl_usd"], "1779605629.28")

    def test_brent_change_log_supersedes_the_void(self):
        log = [row for row in rows(CHANGE_LOG) if row["ticker"] == "BRENT"]
        self.assertTrue(log)
        for row in log:
            self.assertEqual(row["ticker"], "BRENT")
            self.assertEqual(row["change_date"], "2026-10-30")
        superseded = next(r for r in log
                          if r["change_type"].startswith("OIL CLOSE SUPERSEDED"))
        self.assertEqual(superseded["close_or_offer_value"], "119.00")
        self.assertEqual(superseded["reported_transaction_pnl_usd"], "2669676158.00")
        self.assertEqual(superseded["source_reported_pnl_usd"], "933875016.74")
        policy_row = next(r for r in log if r["change_type"] == "MODEL/POLICY CONTROL")
        self.assertEqual(policy_row["source_record_id"], EXCEPTION)

    def test_user_reported_ats_decision_note(self):
        register = rows(REGISTER)
        foundation = next(r for r in register if r["record_id"] == "BRENT119-ATS-FOUNDATION")
        log = next(r for r in rows(CHANGE_LOG)
                   if r["source_record_id"] == "ATS-FOUNDATION-BRENT-SOLD-119-20261030")
        for note in (foundation["notes"], log["notes"], REPORT.read_text(encoding="utf-8")):
            self.assertIn("price check at $119", note)
            self.assertIn("on its own", note)
            self.assertIn("not independently verified", note)

    def test_scoped_exception_and_report_are_recorded(self):
        policy_text = POLICY.read_text(encoding="utf-8")
        self.assertIn(EXCEPTION, policy_text)
        self.assertIn("BRENT full exit at $119 (October 30, 2026)", policy_text)
        self.assertIn("does **not** authorize", policy_text)
        report_text = REPORT.read_text(encoding="utf-8")
        for value in ("$2,669,676,158.00", "$1,898,059,402.97", "$52,827.16",
                      "$35,076.52", "$32,985.41", "$17,391.30"):
            self.assertIn(value, report_text)
        self.assertIn("price-only", report_text.lower())
        self.assertIn("not verified as interchangeable", report_text)

    def test_under_duress_overlay_csvs_are_not_rewritten(self):
        for name in ("data/under_duress_oil_restored_positions_v1.csv",
                     "data/under_duress_oil_void_events_v1.csv"):
            path = ROOT / name
            self.assertTrue(path.exists(), name)
            text = path.read_text(encoding="utf-8")
            self.assertNotIn("119.00", text,
                             f"{name} must be preserved unchanged as the earlier baseline")

    def test_index_event_count_matches_the_ledger_tree(self):
        index = (ROOT / "trades/index.txt").read_text(encoding="utf-8")
        self.assertIn("145 standardized log events currently recorded", index)
        dated = 0
        for path in sorted((ROOT / "trades").glob("*.txt")):
            if path.name == "index.txt":
                continue
            for line in path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line and not line.startswith("#") and line[:4].isdigit():
                    dated += 1
        self.assertEqual(dated, 145)


if __name__ == "__main__":
    unittest.main()
