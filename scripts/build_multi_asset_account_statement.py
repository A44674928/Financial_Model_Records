#!/usr/bin/env python3
"""Build a source-separated multi-asset statement register and Oct. 29 change log.

The output is a position/event register, not a reconciled brokerage statement.
It deliberately keeps model variants, source books, and audit-only records apart.
"""
from __future__ import annotations

import csv
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
REPORTS = ROOT / "reports"
STATEMENT_DATE = "2026-10-28"
LATEST_ALLOWED_MAIN_MARK = "2026-10-19"
OIL_MARK_DATE = "2026-10-26"
UNIT = 10_000.0
OIL_TICKERS = {"BRENT", "OIL", "CVX", "VLO", "XLE"}
BLOCKED_TICKERS = {"AAPL", "AMZN", "INTC", "META", "NVDA", "PLTR", "TSLA"}

STATEMENT_CSV = DATA / "multi_asset_account_statement_2026-10-28_v1.csv"
CHANGE_CSV = DATA / "account_change_log_2026-10-29_v1.csv"
STATEMENT_MD = REPORTS / "Multi-Asset Account Statement — 2026-10-28.md"
CHANGE_MD = REPORTS / "Account Change Log — 2026-10-29.md"

FIELDS = [
    "statement_as_of_date", "record_as_of_date", "row_category", "source_book_or_model",
    "source_row_type", "scenario_id", "variant", "ticker", "asset_class", "side_or_action", "quantity", "quantity_unit",
    "model_units", "entry_date_or_time", "entry_price_usd_or_quote", "mark_date_or_time",
    "mark_price_usd_or_quote", "gross_basis_usd", "market_value_or_notional_usd",
    "realized_pnl_usd", "unrealized_or_conditional_pnl_usd", "position_or_record_status",
    "source_nullification_state", "test_override_state", "additivity_rule", "policy_status",
    "source_record_id", "source_file", "notes",
]
CHANGE_FIELDS = [
    "change_date", "displayed_time", "timezone_status", "change_type", "source_book_or_model",
    "ticker", "side_or_action", "quantity", "quantity_unit", "entry_or_reference_price",
    "close_or_offer_value", "reported_transaction_pnl_usd", "source_reported_pnl_usd", "position_effect", "status",
    "source_record_id", "source_file", "notes",
]


def read_csv(path: Path):
    with path.open(newline="", encoding="utf-8-sig") as h:
        return list(csv.DictReader(h))


def blank_row(**values):
    row = {k: "" for k in FIELDS}
    row.update(values)
    row["statement_as_of_date"] = STATEMENT_DATE
    return row


def fmt(value):
    if value is None or value == "":
        return ""
    return f"{float(value):.2f}"


def add_screened_model_positions(rows):
    os.environ["PAPER_TRADES_INFLUENCER_AI_SCREEN"] = "1"
    os.environ.pop("PAPER_TRADES_AI_FUND_REPLAY", None)
    os.environ.pop("PAPER_TRADES_OIL_PORTFOLIO_REPLAY", None)
    sys.path.insert(0, str(ROOT / "scripts"))
    import model_perf_core as core

    events = core.parse_trades()
    day = core.SESSION_DATES[-1]
    assert day == LATEST_ALLOWED_MAIN_MARK, day
    for variant in core.VARIANTS:
        model = core.daily_series(variant, events)
        for lot in model["lots"]:
            if not lot["open"] or lot["sym"] in OIL_TICKERS:
                continue  # Oil is reported once, in its separate authorized book.
            ticker = lot["sym"]
            mark = core.PRICES[ticker][-1]
            qty = float(lot["qty"])
            basis = qty * UNIT
            direction = 1 if lot["side"] == "long" else -1
            pnl = direction * basis * (mark / float(lot["entry_px"]) - 1)
            market_value = basis * mark / float(lot["entry_px"])
            rows.append(blank_row(
                record_as_of_date=day,
                row_category="SCREENED_MAIN_MODEL_OPEN_LOT",
                source_book_or_model="Screened main paper-model replay; current screened view",
                variant=variant,
                ticker=ticker,
                asset_class="Direct-price model asset",
                side_or_action=lot["side"].upper(),
                quantity=f"{qty:g}",
                quantity_unit="U; $10,000 model notional per U (not shares/contracts)",
                model_units=f"{qty:g}",
                entry_date_or_time=lot["entry_date"],
                entry_price_usd_or_quote=fmt(lot["entry_px"]),
                mark_date_or_time=day,
                mark_price_usd_or_quote=fmt(mark),
                gross_basis_usd=fmt(basis),
                market_value_or_notional_usd=fmt(market_value),
                realized_pnl_usd="0.00",
                unrealized_or_conditional_pnl_usd=fmt(pnl),
                position_or_record_status="Model-open at 2026-10-19 cutoff; no later active mark or event applied",
                policy_status="SCREENED; OCT-20+ INPUTS EXCLUDED; OIL BOOK SEPARATED",
                source_record_id=f"{variant}-{lot['id']}",
                source_file=f"trades/{ticker}.txt",
                notes=("Paper-model lot only, not an account fill. The four variants are alternative model paths, "
                       "not additive holdings. Latest permitted non-Oil mark is 2026-10-19."),
            ))


def add_oil_register(rows):
    oil_rows = read_csv(DATA / "oil_position_audit_sheet_v1.csv")
    for source in oil_rows:
        # Oct. 29 events belong in the change log, not the Oct. 28 opening statement.
        date_fields = (source.get("entry_date", ""), source.get("exit_date", ""), source.get("valuation_date", ""))
        if any(re.match(r"2026-10-29", value or "") for value in date_fields):
            continue
        if source.get("source_file", "").startswith("Archive/November_2026_Experiment_Oil_Closes_2026-10-29/"):
            continue  # Report the retained private-fund longs once in their own book section below.
        kind = source["row_type"]
        is_base = kind == "ACTIVE_OIL_MODEL_POSITION"
        row = blank_row(
            record_as_of_date=source.get("valuation_date") or OIL_MARK_DATE,
            row_category="OIL_V2_BASE_POSITION" if is_base else "OIL_AUDIT_SCENARIO_OR_REFERENCE",
            source_book_or_model=source.get("book_or_model", ""),
            source_row_type=source.get("row_type", ""),
            scenario_id=source.get("scenario_id", ""),
            source_nullification_state=source.get("source_nullification_state", ""),
            test_override_state=source.get("test_override_state", ""),
            additivity_rule=source.get("additivity_rule", ""),
            variant="Oil v2" if is_base else "",
            ticker=source.get("ticker", ""),
            asset_class="Oil, energy equity, or related scenario/reference",
            side_or_action=source.get("side", ""),
            quantity=source.get("quantity", ""),
            quantity_unit=source.get("quantity_unit", ""),
            model_units=source.get("u_equivalent", ""),
            entry_date_or_time=source.get("entry_date", ""),
            entry_price_usd_or_quote=source.get("entry_price_usd", ""),
            mark_date_or_time=source.get("valuation_date", ""),
            mark_price_usd_or_quote=source.get("valuation_mark_usd", ""),
            gross_basis_usd=source.get("gross_basis_usd", ""),
            market_value_or_notional_usd=source.get("market_value_usd", ""),
            realized_pnl_usd=source.get("realized_pnl_usd", ""),
            unrealized_or_conditional_pnl_usd=(source.get("conditional_unrealized_pnl_usd") or source.get("scenario_total_pnl_usd", "")),
            position_or_record_status=source.get("position_state", ""),
            policy_status=("USER_AUTHORIZED_SCOPED_OIL_V2; MARKS THROUGH 2026-10-26" if is_base
                           else "AUDIT-ONLY SCENARIO/REFERENCE; NOT AN ACTIVE OIL REPLAY POSITION"),
            source_record_id=source.get("source_record_id", ""),
            source_file=source.get("source_file", ""),
            notes=(source.get("audit_notes", "") + " " + source.get("additivity_rule", "")).strip(),
        )
        rows.append(row)


def add_standalone_records(rows):
    # User-directed ALIUSD export position as of Oct. 28.
    a = read_csv(DATA / "aliusd_user_directed_position_v1.csv")[0]
    rows.append(blank_row(
        record_as_of_date="2026-10-28T17:41:25.410Z (export provenance)",
        row_category="USER_DIRECTED_POSITION_SNAPSHOT",
        source_book_or_model="Standalone ALIUSD user-directed paper scenario; account mapping not supplied",
        ticker="ALIUSD",
        asset_class="Aluminum / CFD-like platform instrument; contract convention unspecified",
        side_or_action=a["side"],
        quantity=a["raw_platform_quantity"],
        quantity_unit="raw platform quantity; multiplier/contract unit unknown",
        entry_date_or_time="Not supplied",
        entry_price_usd_or_quote=a["user_corrected_entry_price_usd"],
        mark_date_or_time="2026-10-28 export snapshot; not EOD",
        mark_price_usd_or_quote=a["source_csv_last_price_usd"],
        gross_basis_usd=a["recomputed_all_cash_entry_notional_usd"],
        market_value_or_notional_usd=a["source_csv_market_value_usd"],
        unrealized_or_conditional_pnl_usd=a["recomputed_conditional_mark_pnl_usd"],
        position_or_record_status="User-directed paper scenario; no verified brokerage fill; conditional export-snapshot arithmetic only",
        policy_status="SOURCE RECORD RETAINED; NOT A VERIFIED ACCOUNT POSITION OR EOD VALUATION",
        source_record_id=a["record_id"],
        source_file="data/aliusd_user_directed_position_v1.csv; Archive/ALIUSD_LONG_2026-10-28/",
        notes=("User corrected entry to $2,999.99; CSV quantity is authoritative. $3,070.60 is the export last-price snapshot. "
               "50x/margin fields are metadata only. No leverage, financing, account mapping, or contract multiplier inferred."),
    ))

    for record_id, ticker, quantity, entry, symbol, image in [
        ("PRIVATE_TV_BRENT_CLOSE_20261029_OPEN_LOT", "BRENT", "538566907", "114.043000", "BLACKBULL:BRENT", "IMG_1218.png"),
        ("PRIVATE_TV_USOIL_CLOSE_20261029_OPEN_LOT", "USOIL", "601218118", "99.180000", "TVC:USOIL", "IMG_1217.png"),
    ]:
        rows.append(blank_row(
            record_as_of_date="Prior to 2026-10-29; exact entry date/time not supplied",
            row_category="PRIVATE_FUND_OPEN_POSITION_RESTORED",
            source_book_or_model="Harshal's Private Fund / TradingView Paper Trading account label",
            ticker=ticker,
            asset_class="Oil-linked paper-trading long; account mapping to active Oil model unresolved",
            side_or_action="LONG OPEN",
            quantity=quantity,
            quantity_unit="platform-reported units; no instrument multiplier inferred",
            entry_date_or_time="Earlier entry; exact date/time not supplied",
            entry_price_usd_or_quote=entry,
            position_or_record_status="OPEN; October 29 close nullified and voided per user instruction; no valid current mark supplied",
            policy_status="USER-DIRECTED OPEN-LOT STATUS; PLATFORM VOID NOT INDEPENDENTLY CONFIRMED",
            source_record_id=record_id,
            source_file=f"Archive/November_2026_Experiment_Oil_Closes_2026-10-29/{image}",
            notes=f"Retain {ticker} long at reported earlier entry ${entry}. The October 29 screenshot close at {symbol} is nullified/voided per user direction; do not mark this lot closed or use the screenshot close price/PnL as a current valuation.",
        ))

    oil_sheet = read_csv(DATA / "oil_position_audit_sheet_v1.csv")
    for source in oil_sheet:
        if source["row_type"] != "PRIVATE_FUND_LCID_POSITION_REFERENCE":
            continue
        if re.match(r"2026-10-29", source.get("entry_date", "")):
            continue
        rows.append(blank_row(
            record_as_of_date="Capture date/time not supplied",
            row_category="PRIVATE_FUND_POSITION_SNAPSHOT",
            source_book_or_model="Harshal's Private Fund; account/ledger mapping unresolved",
            ticker="LCID",
            asset_class="Equity (NASDAQ:LCID)",
            side_or_action=source["side"],
            quantity=source["quantity"],
            quantity_unit=source["quantity_unit"],
            entry_date_or_time="Not supplied",
            entry_price_usd_or_quote=source["entry_price_usd"],
            mark_date_or_time="Screenshot capture time not supplied",
            mark_price_usd_or_quote=source["valuation_mark_usd"],
            gross_basis_usd=source["gross_basis_usd"],
            market_value_or_notional_usd=source["market_value_usd"],
            realized_pnl_usd="0.00",
            unrealized_or_conditional_pnl_usd=source["conditional_unrealized_pnl_usd"],
            position_or_record_status=source["position_state"],
            policy_status="SOURCE SNAPSHOT; DATE/ACCOUNT MAPPING UNRESOLVED",
            source_record_id=source["source_record_id"],
            source_file=source["source_file"],
            notes=source["audit_notes"],
        ))

    # User-directed small-caps LCID test lots after the general TradingView cutoff.
    for i, (day, price) in enumerate((("2026-10-20", "2.92"), ("2026-10-20", "3.01"),
                                      ("2026-10-21", "3.30"), ("2026-10-22", "3.43"),
                                      ("2026-10-23", "3.47")), 1):
        rows.append(blank_row(
            record_as_of_date=day,
            row_category="POST_CUTOFF_LCID_PILOT_LOT",
            source_book_or_model="Small Caps Buyout & Reorganization Test Pilot; model book unspecified",
            ticker="LCID",
            asset_class="Equity; modeled $10,000 unit",
            side_or_action="LONG",
            quantity="1",
            quantity_unit="U ($10,000 model notional); not share count",
            model_units="1",
            entry_date_or_time=day,
            entry_price_usd_or_quote=price,
            position_or_record_status="User-provided paper-model entry; active account/fill status not verified",
            policy_status="POST-CUTOFF RECORD; PRESERVED; NOT REPRICED OR ADDED TO ACTIVE MODEL",
            source_record_id=f"LCID-PILOT-{i}",
            source_file="trades/LCID.txt",
            notes="Oct. 20–23 entries postdate the standing TradingView cutoff; kept as source references only. No Oct. 28 mark is supplied here.",
        ))


def add_ai_fund_audit_rows(rows):
    # Preserve the former segregated AI Fund ledger as an excluded audit record set;
    # do not promote it to current holdings under the later influencer/AI screen.
    for source in read_csv(DATA / "harshal_priyavadan_patel_ai_fund_event_ledger_v2.csv"):
        rows.append(blank_row(
            record_as_of_date=source.get("Date", ""),
            row_category="AI_FUND_HISTORICAL_EVENT_AUDIT_ONLY",
            source_book_or_model="Historical segregated AI Fund v2 ledger; not current active book",
            source_row_type=source.get("Event", ""),
            scenario_id=source.get("Transfer_Basis", ""),
            ticker=source.get("Ticker", ""),
            asset_class="Historical model event; asset type follows ticker/source",
            side_or_action=f"{source.get('Event', '')} {source.get('Tag', '')}".strip(),
            quantity=source.get("Units", ""),
            quantity_unit="model units as logged; not brokerage quantity",
            entry_date_or_time=source.get("Date", ""),
            entry_price_usd_or_quote=source.get("Logged_Price", ""),
            position_or_record_status="Historical event only; does not establish a current open position",
            policy_status="EXCLUDED FROM ACTIVE MODEL UNDER 2026-10-29 TICKER/COMMENTARY SCREEN; SOURCE PRESERVED",
            source_record_id=source.get("Record_ID", ""),
            source_file=source.get("Source_File", ""),
            notes=(source.get("Original_Note", "") + " " + source.get("Marking_Status", "")).strip(),
        ))


def add_unpriced_source_records(rows):
    line_re = re.compile(
        r"^(?P<date>\d{4}-\d{2}-\d{2})\s+(?P<time>\d{2}:\d{2})\s+MST\s*\|\s*"
        r"SIMULATED PAPER\s+\[(?P<tag>[A-Za-z ]+?)\]\s*\|\s*"
        r"(?P<kind>entry|exit):\s*\[Market @ ~\$?(?P<px>[\d,]+\.?\d*%?)\]\s*\|\s*"
        r"size:\s*\[(?P<units>\d+(?:\.\d+)?)\s*units?[^\]]*\]\s*\|\s*"
        r"note:\s*\[(?P<note>.*)\]$"
    )
    symbols = {"BTC", "ETH", "DXY", "EURUSD", "JPYUSD", "US10Y", "US30Y"}
    for ticker in sorted(symbols):
        path = ROOT / "trades" / f"{ticker}.txt"
        if not path.exists():
            continue
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            m = line_re.match(line.strip())
            if not m or m["kind"] != "entry" or m["date"] > STATEMENT_DATE:
                continue
            note = m["note"]
            if ticker in BLOCKED_TICKERS or "commentary" in note.lower() or ticker == "DXY":
                policy = "SCREENED OUT OF ACTIVE MODEL; AUDIT REFERENCE ONLY"
            elif ticker in {"US10Y", "US30Y"}:
                policy = "YIELD-ONLY INPUT; NO BOND PRICE/QUANTITY CONVERSION"
            else:
                policy = "UNMODELED OR UNPRICED SOURCE ENTRY; OPEN STATUS NOT RECONCILED"
            rows.append(blank_row(
                record_as_of_date=m["date"],
                row_category="UNPRICED_OR_SCREENED_SOURCE_ENTRY",
                source_book_or_model="Unpriced/segregated historical source record",
                ticker=ticker,
                asset_class={"BTC": "Crypto", "ETH": "Crypto", "DXY": "Currency index", "EURUSD": "FX", "JPYUSD": "FX", "US10Y": "Treasury yield reference", "US30Y": "Treasury yield reference"}[ticker],
                side_or_action=m["tag"].upper(),
                quantity=m["units"],
                quantity_unit="U ($10,000 model notional) as source log states; not a brokerage quantity",
                model_units=m["units"],
                entry_date_or_time=f"{m['date']} {m['time']} MST",
                entry_price_usd_or_quote=m["px"],
                position_or_record_status="Historical paper-model source entry; current open/closed status not established",
                policy_status=policy,
                source_record_id=f"{ticker}-{lineno}",
                source_file=f"trades/{ticker}.txt",
                notes=note + " Yield quotes are not bond prices; no leverage/funding is inferred.",
            ))


def add_post_cutoff_trade_audit_rows(rows):
    os.environ["PAPER_TRADES_INFLUENCER_AI_SCREEN"] = "0"
    line_re = re.compile(
        r"^(?P<date>\d{4}-\d{2}-\d{2})\s+(?P<time>\d{2}:\d{2})\s+MST\s*\|\s*"
        r"SIMULATED PAPER\s+\[(?P<tag>[A-Za-z ]+?)\]\s*\|\s*"
        r"(?P<kind>entry|exit):\s*\[Market @ ~\$?(?P<px>[\d,]+\.?\d*%?)\]\s*\|\s*"
        r"size:\s*\[(?P<units>\d+(?:\.\d+)?)\s*units?[^\]]*\]\s*\|\s*"
        r"note:\s*\[(?P<note>.*)\]$"
    )
    for path in sorted((ROOT / "trades").glob("*.txt")):
        ticker = path.stem.upper()
        if ticker == "INDEX" or ticker in OIL_TICKERS or ticker in {"LCID", "ALIUSD", "BTC", "ETH", "DXY", "EURUSD", "JPYUSD", "US10Y", "US30Y"}:
            continue
        for lineno, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            m = line_re.match(raw.strip())
            if not m or not ("2026-10-20" <= m["date"] <= STATEMENT_DATE):
                continue
            blocked = ticker in BLOCKED_TICKERS
            rows.append(blank_row(
                record_as_of_date=m["date"],
                row_category="POST_CUTOFF_LEDGER_EVENT_AUDIT_ONLY",
                source_book_or_model="Trade log; account/model mapping not supplied",
                ticker=ticker,
                asset_class="Paper-model source event",
                side_or_action=f"{m['kind'].upper()} {m['tag'].upper()}",
                quantity=m["units"],
                quantity_unit="U/model units from source log; not brokerage quantity",
                model_units=m["units"],
                entry_date_or_time=f"{m['date']} {m['time']} MST",
                entry_price_usd_or_quote=m["px"],
                position_or_record_status="Audit-only event; not treated as an active account position in this statement",
                policy_status=("BLOCKED TICKER; PRESERVED; NOT ACTIVE" if blocked else
                               "POST-2026-10-19 RECORD; PRESERVED; NOT ACTIVE IN GENERAL REPLAY"),
                source_record_id=f"{ticker}-{lineno}",
                source_file=str(path.relative_to(ROOT)),
                notes=m["note"],
            ))


def change(**values):
    row = {k: "" for k in CHANGE_FIELDS}
    row.update(values)
    return row


def build_change_rows():
    result = []
    # Screenshot close evidence is retained, but the close is nullified/voided and the original long remains open.
    for record_id, ticker, symbol, time, qty, entry, close, pnl, image in [
        ("PRIVATE_TV_BRENT_CLOSE_20261029", "BRENT", "BLACKBULL:BRENT", "10:41:44", "538566907", "114.043000", "115.777", "933875016.74", "IMG_1218.png"),
        ("PRIVATE_TV_USOIL_CLOSE_20261029", "USOIL", "TVC:USOIL", "10:41:38", "601218118", "99.180000", "102.14", "1779605629.28", "IMG_1217.png"),
    ]:
        result.append(change(
            change_date="2026-10-29", displayed_time="Not supplied", timezone_status=f"Void time not supplied; source screenshot time {time} with no timezone",
            change_type="OIL CLOSE NULLIFIED AND VOIDED PER USER INSTRUCTION", source_book_or_model="Harshal's Private Fund / TradingView Paper Trading account label",
            ticker=ticker, side_or_action="NULLIFY / VOID CLOSE; KEEP LONG OPEN", quantity=qty, quantity_unit="platform-reported units",
            entry_or_reference_price=entry, close_or_offer_value=close,
            reported_transaction_pnl_usd="0.00", source_reported_pnl_usd=pnl,
            position_effect="Do not record a close; retain the earlier long as open at its stated entry price. No realized PnL or current mark inferred; mapping to other Oil/model lots remains unestablished.",
            status="Close nullified/voided per user instruction; screenshot still displays close/PnL; platform status not independently confirmed",
            source_record_id=record_id,
            source_file=f"Archive/November_2026_Experiment_Oil_Closes_2026-10-29/{image}",
            notes=f"Platform symbol {symbol}. Source screenshot time {time} (timezone not shown) and displayed PnL ${float(pnl):,.2f} are preserved as voided-source evidence only. Do not use the screenshot close price as a mark or book the displayed PnL. The existing long remains open at entry ${entry}; entry date/time not supplied.",
        ))
        result.append(change(
            change_date="2026-10-29", displayed_time="Not supplied", timezone_status="Date only; original entry time not supplied",
            change_type="EARLIER OIL LONG RETAINED OPEN", source_book_or_model="Harshal's Private Fund / TradingView Paper Trading account label",
            ticker=ticker, side_or_action="LONG OPEN; NO EXIT", quantity=qty, quantity_unit="platform-reported units",
            entry_or_reference_price=entry, reported_transaction_pnl_usd="0.00", source_reported_pnl_usd="",
            position_effect="Carry the earlier long forward as open; exact entry date/time and account mapping are not supplied. No mark or market value assigned.",
            status="User-directed open-position treatment after the October 29 close was nullified/voided",
            source_record_id=f"{record_id}_OPEN_LOT", source_file=f"Archive/November_2026_Experiment_Oil_Closes_2026-10-29/{image}",
            notes=f"Opening entry price ${entry} and quantity {qty} preserved from the screenshot's average entry and units. The close price ${close} is not applied as a mark; no current valuation supplied.",
        ))
    result.append(change(
        change_date="2026-10-29", displayed_time="11:05:57", timezone_status="Timezone not shown",
        change_type="FILLED BUY ORDER", source_book_or_model="Harshal's Private Fund report; selected account truncates as SWITCH_TO_LCI...",
        ticker="LCID", side_or_action="BUY MARKET", quantity="301204819.27", quantity_unit="screenshot-reported shares",
        entry_or_reference_price="3.32", close_or_offer_value="999999999.98", reported_transaction_pnl_usd="0.00",
        position_effect="Add a distinct purchased lot; not a sell/close; no post-fill mark, funding source, or account mapping to earlier LCID screenshot supplied",
        status="Filled per user-provided TradingView Paper Trading screenshot; not audited execution",
        source_record_id="3736492349", source_file="Archive/Private_Fund_LCID_Position/IMG_1225.png",
        notes="Displayed 1x/margin fields are transcription only; no financing inferred. Value is purchase consideration, not realized PnL.",
    ))
    result.append(change(
        change_date="2026-10-29", displayed_time="Not supplied", timezone_status="Date supplied; no time supplied",
        change_type="HYPOTHETICAL LCID OFFER REFERENCE", source_book_or_model="User-directed hypothetical takeover/offer reference",
        ticker="LCID", side_or_action="HYPOTHETICAL MARKET-CAP OFFER", quantity="", quantity_unit="Not supplied",
        entry_or_reference_price="", close_or_offer_value="1310000000.00 USD market capitalization (user-supplied)",
        reported_transaction_pnl_usd="",
        position_effect="No position, order, or actual bid created; do not calculate per-share price or exchange ratio",
        status="Hypothetical; market-cap figure not independently verified",
        source_record_id="LCID_HYPOTHETICAL_OFFER_20261029", source_file="User instruction; reports/Under-Duress Oil Sale Void Replay.md",
        notes="Recorded as a current-date market-cap reference regardless of share count, as instructed; not an actual offer or completed transaction.",
    ))
    result.append(change(
        change_date="2026-10-29", displayed_time="Not supplied", timezone_status="Date only",
        change_type="MODEL/POLICY CONTROL", source_book_or_model="Influencer and AI source/ticker screen",
        ticker="MULTI-ASSET", side_or_action="RETROACTIVE SCREEN AND REPLAY",
        position_effect="Affected model events in AAPL, AMZN, INTC, META, NVDA, PLTR, TSLA and all third-party commentary excluded; records preserved; separate screened replay created",
        status="Control change; not a trade or cash movement",
        source_record_id="INFLUENCER_AI_SCREEN_20261029", source_file="reports/Influencer and AI Source Block Policy.md",
        notes="Screened replay ends 2026-10-19 under standing TradingView cutoff; no general post-cutoff mark authorization.",
    ))
    result.append(change(
        change_date="2026-10-29", displayed_time="Not supplied", timezone_status="Date only",
        change_type="MODEL MARK-FORWARD CONTROL", source_book_or_model="Separate Oil portfolio v2",
        ticker="BRENT; OIL; CVX; VLO; XLE", side_or_action="MARK FORWARD ONLY",
        position_effect="Existing Oil positions through 2026-10-19 re-marked using aligned EOD marks through 2026-10-26; no later trade events added",
        status="User-authorized scoped replay; not a 2026-10-29 valuation",
        source_record_id="OIL_V2_MARK_FORWARD_20261029", source_file="reports/Oil Portfolio — 2026-10-26 Update.md",
        notes="Oil v1 remains preserved. Post-cutoff trade-event cutoff remains 2026-10-19; no Oct. 27–29 aligned marks available.",
    ))
    result.append(change(
        change_date="2026-10-29", displayed_time="Not supplied", timezone_status="Date only",
        change_type="AUDIT SCENARIO STATUS CHANGE", source_book_or_model="Oil position audit test sheet",
        ticker="BRENT; OIL", side_or_action="RESTORE SHORT LIFECYCLES AS UN-NULLIFIED FOR TEST",
        quantity="8 lifecycle scenarios", quantity_unit="Alternative sensitivities; not additive",
        position_effect="Audit representation only; original source nullification history retained; no source book or active replay changed",
        status="Scenario-only; not evidence of brokerage positions or executions",
        source_record_id="OIL_SHORT_LIFECYCLE_AUDIT_TEST_20261029", source_file="data/oil_position_audit_sheet_v1.csv",
        notes="Restored test display includes 10U/20U/30U/40U scenario sizes for BRENT and OIL; source records remain unchanged.",
    ))
    return result


def write_csv(path, rows, fields):
    with path.open("w", newline="", encoding="utf-8") as h:
        writer = csv.DictWriter(h, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def build():
    rows = []
    add_screened_model_positions(rows)
    add_oil_register(rows)
    add_standalone_records(rows)
    add_ai_fund_audit_rows(rows)
    add_unpriced_source_records(rows)
    add_post_cutoff_trade_audit_rows(rows)
    rows.sort(key=lambda r: (r["row_category"], r["source_book_or_model"], r["variant"], r["ticker"], r["entry_date_or_time"], r["source_record_id"]))
    changes = build_change_rows()
    changes.sort(key=lambda r: (r["change_date"], r["displayed_time"] if re.fullmatch(r"\d{2}:\d{2}:\d{2}", r["displayed_time"]) else "99:99:99", r["change_type"]))
    write_csv(STATEMENT_CSV, rows, FIELDS)
    write_csv(CHANGE_CSV, changes, CHANGE_FIELDS)

    categories = {}
    for row in rows:
        categories[row["row_category"]] = categories.get(row["row_category"], 0) + 1
    lines = [
        "# Multi-Asset Account Statement — October 28, 2026",
        "",
        "> **Source-separated position and event register, not a reconciled brokerage statement.** No single account map, funded cash balance, or verified execution ledger is available across these source books.",
        "",
        "## Statement basis and boundary",
        "",
        "This statement gathers the repository's identified multi-asset holdings, modeled lots, user-directed snapshots, and audit references dated October 28 or earlier. The source evidence has differing as-of dates. The latest permitted non-Oil main-model mark is **October 19** under the standing TradingView cutoff; the separately authorized Oil v2 mark-forward uses aligned EOD marks through **October 26**, with trade events still cut off at October 19. The ALIUSD export is a source snapshot from October 28, not an EOD mark. The older Private Fund LCID screenshot has no capture timestamp.",
        "",
        "The CSV is intentionally a **register**, not a portfolio valuation. It keeps separate source books, alternative model variants, and audit-only scenarios on separate rows. It does not add their notionals, market values, profit estimates, or PnL into an account total. The four core-model variants are alternative paths, not additive holdings.",
        "",
        "## Row coverage",
        "",
        f"The register contains **{len(rows)} rows**. By category: " + "; ".join(f"{k}: {v}" for k, v in sorted(categories.items())) + ".",
        "",
        "- **Screened main model:** open paper-model lots through October 19 across four alternative variants. Blocked tickers and commentary-derived records are not represented as active; after-cutoff trade-log events are separately retained as audit-only rows.",
        "- **Oil:** the active Oil v2 pre-cutoff lots are shown at October 26 marks; ATS/manual, under-duress, legacy, and liquidation references remain separately labeled and non-additive. The two separate-book Private Fund longs are retained open at their earlier reported entries ($114.043 BRENT; $99.18 USOIL); entry dates and current marks are unknown. Their October 29 close records are nullified/voided in the change log, not treated as exits.",
        "- **ALIUSD:** user-directed long from an October 28 platform export, with the user-corrected $2,999.99 entry and $3,070.60 export snapshot. The raw quantity is preserved; contract multiplier and account mapping are unknown. Its conditional $46,639,362,534.94 gross basis and $1,097,738,788.66 snapshot price-only change are arithmetic references, not funded capital or verified account PnL; platform 50×/margin fields are not applied.",
        "- **LCID:** an older open-long screenshot is retained with its capture date unknown. Five Oct. 20–23 Small Caps pilot units are separate model rows and remain post-cutoff audit-only; they are not combined with the large screenshot position.",
        "- **AI Fund history:** the prior segregated AI Fund v2 event ledger is included row-by-row as historical audit data, not as active holdings; its blocked-ticker/commentary events remain excluded under the October 29 screen.",
        "- **Unpriced / screened source records:** BTC, ETH, FX, DXY, and Treasury-yield references are retained with their source status. Yield quotes are not bond prices; no quantity, duration, FX conversion, or current mark is invented.",
        "",
        "## Reconciliation limitations",
        "",
        "The historical screened replay is a paper model, not an account custody record. Oil is separately modeled and appears in separate Oil rows; older combined model rows are not netted against it. The older AI Fund ledger contains records for policy-blocked tickers/commentary and is not treated as a current active portfolio after the October 29 screen. The Private Fund's prior profit-only carry-in is a selected model estimate, not verified cash, and is not represented as an asset or added to any position value.",
        "",
        "No inferred leverage, financing, cash, or funding source is included. TradingView Paper Trading screenshots and model outputs are not independently audited brokerage executions. The $1.31B LCID market-cap reference is hypothetical and belongs in the October 29 change log, not this October 28 statement.",
        "",
        "## Files",
        "",
        "- Machine-readable register: [`data/multi_asset_account_statement_2026-10-28_v1.csv`](../data/multi_asset_account_statement_2026-10-28_v1.csv).",
        "- October 29 changes: [change log report](Account%20Change%20Log%20%E2%80%94%202026-10-29.md) and [CSV](../data/account_change_log_2026-10-29_v1.csv).",
        "- Supporting source records: [Oil v2 update](Oil%20Portfolio%20%E2%80%94%202026-10-26%20Update.md), [ALIUSD position note](ALIUSD%20User-Directed%20LONG%20Position.md), [Private Fund balance sheet](Harshal's%20Private%20Fund%20%E2%80%94%20November%202026++%20Experiment.md), and [screened replay](Influencer%20and%20AI%20Screened%20Replay%20%E2%80%94%202026-10-29.md).",
        "",
    ]
    STATEMENT_MD.write_text("\n".join(lines), encoding="utf-8")

    change_lines = [
        "# Account Change Log — October 29, 2026",
        "",
        "> Chronological source log. Transaction times are used only where shown; no timezone is inferred. Model/policy changes are distinguished from transactions.",
        "",
        "## Reported activity and recorded changes",
        "",
        "| Time (as shown) | Book / type | Instrument | Recorded change | Recognized amount / source display |",
        "|---|---|---|---|---|",
        "| 10:41:38 screenshot time; void time not supplied | Separate Private Fund / close nullification | USOIL | Close-long record **nullified and voided**; retain 601,218,118-unit long open at $99.18 entry | $0.00 realized; screenshot close $102.14 / +$1,779,605,629.28 preserved only as voided-source evidence; no mark assigned |",
        "| 10:41:44 screenshot time; void time not supplied | Separate Private Fund / close nullification | BRENT | Close-long record **nullified and voided**; retain 538,566,907-unit long open at $114.043 entry | $0.00 realized; screenshot close $115.777 / +$933,875,016.74 preserved only as voided-source evidence; no mark assigned |",
        "| 11:05:57; timezone not shown | Private Fund report / filled order | LCID | Buy market, 301,204,819.27 shares at $3.32; order 3736492349 | $999,999,999.98 purchase value; distinct lot, not realized PnL |",
        "| Date only | User-directed hypothetical offer reference | LCID | Record the hypothetical offer at the supplied current market capitalization | $1.31B user-supplied; not independently verified; no per-share price or exchange ratio calculated |",
        "| Date only | Model/policy control | Multi-asset | Retroactive influencer/AI screen applied; listed tickers and third-party commentary excluded from active replay | Historical records preserved; not a trade or cash movement |",
        "| Date only | Model/policy control | Oil | Authorized Oil v2 mark-forward through October 26 while retaining October 19 trade-event cutoff | Not an October 29 valuation; no later trade events used |",
        "| Date only | Audit scenario | BRENT / OIL | Eight short lifecycle scenarios represented as un-nullified for audit testing | Scenario-only; source history unchanged; not active account positions |",
        "",
        "## Interpretation and controls",
        "",
        "- The source screenshots display two Private Fund / TradingView Paper Trading long closes. Per the user's clarification, both closes are **nullified and voided**; retain the earlier longs open at $114.043 (BRENT) and $99.18 (USOIL), using the reported quantities. Entry dates/times and account mapping remain unknown. The screenshot close prices are not used as marks, and **$0.00 is recognized as realized PnL**. Platform void status is not independently confirmed; the screenshots remain preserved as source evidence.",
        "- The LCID order is a **buy**, not a sell or close. Its account selector is truncated, no post-fill mark or funding source is supplied, and it is not netted with the older LCID screenshot position.",
        "- The LCID $1.31B market-cap figure is the user's hypothetical reference as of October 29. It is not an actual bid, agreed consideration, completed transaction, per-share value, or exchange ratio.",
        "- The Oil v2 mark-forward and AI/ticker screen are control/replay changes, not transactions. The under-duress short restoration changes the audit-test representation only; source records and active Oil v2 remain unchanged.",
        "- No cross-book realized PnL, cash, NAV, or account total is calculated. No financing or leverage is inferred.",
        "",
        "## Machine-readable log",
        "",
        "[`data/account_change_log_2026-10-29_v1.csv`](../data/account_change_log_2026-10-29_v1.csv) contains the source IDs, files, timestamps, quantities, prices, amounts, and status notes.",
        "",
    ]
    CHANGE_MD.write_text("\n".join(change_lines), encoding="utf-8")
    print(f"Wrote {len(rows)} statement register rows and {len(changes)} change-log rows.")
    print("Statement categories:", categories)


if __name__ == "__main__":
    build()
