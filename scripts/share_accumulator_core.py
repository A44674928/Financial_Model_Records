"""Profit-funded, next-mark share/model-unit accumulator for TWM_1M_MAX."""
from collections import defaultdict


ENERGY_TICKERS = frozenset({"BRENT", "OIL"})


def run_share_accumulator(session_dates, price_marks, realized_events, scale_factor, unit_value=10_000.0):
    """Replay a realized-PnL-funded overlay without changing its source portfolio.

    Equities are represented as fractional shares bought at the next supplied
    mark. BRENT/OIL are represented as model-U equivalents: one U starts with
    ``unit_value`` dollars of notional and its mark-to-market follows the
    TradingView price ratio from its purchase mark. Negative realized PnL sells
    accumulated lots at the next supplied mark; any uncovered amount remains a
    loss debit and offsets future realized profits before another purchase.

    ``price_marks`` maps ticker to ``{session_date: positive TradingView mark}``.
    Events contain ticker, date, and unscaled realized PnL. Same-ticker events
    closing on one date are netted before scheduling the next-mark transaction.
    """
    dates = list(session_dates)
    if not dates or len(dates) != len(set(dates)):
        raise ValueError("Session dates must be non-empty and unique")
    date_to_index = {day: index for index, day in enumerate(dates)}
    scale = float(scale_factor)
    if scale <= 0 or unit_value <= 0:
        raise ValueError("Scale factor and model unit value must be positive")

    normalized_marks = {}
    for ticker, marks in price_marks.items():
        cleaned = {}
        for day, price in marks.items():
            if day not in date_to_index:
                continue
            price = float(price)
            if price <= 0:
                raise ValueError(f"Non-positive supplied mark for {ticker} on {day}")
            cleaned[day] = price
        normalized_marks[ticker.upper()] = cleaned

    realized_by_day = defaultdict(float)
    ticker_set = set()
    for event in realized_events:
        ticker = str(event["ticker"]).strip().upper()
        day = str(event["date"])
        if day not in date_to_index:
            raise ValueError(f"Realized event is outside the session calendar: {ticker} {day}")
        if ticker not in normalized_marks:
            raise ValueError(f"No supplied TradingView mark series for realized ticker {ticker}")
        pnl = float(event["pnl"])
        realized_by_day[(ticker, day)] += pnl
        ticker_set.add(ticker)

    # Include the energy unit trackers even when the current replay has no
    # realized BRENT/OIL closes, so their zero state is explicit in outputs.
    ticker_set.update(ticker for ticker in ENERGY_TICKERS if ticker in normalized_marks)
    tickers = sorted(ticker_set)
    mark_indices = {
        ticker: {date_to_index[day]: price for day, price in normalized_marks[ticker].items()}
        for ticker in tickers
    }
    next_mark_index = {}
    for ticker in tickers:
        indices = sorted(mark_indices[ticker])
        for event_index in range(len(dates)):
            next_mark_index[(ticker, event_index)] = next(
                (mark_index for mark_index in indices if mark_index > event_index), None
            )

    scheduled = defaultdict(float)
    no_future_mark = defaultdict(float)
    for (ticker, day), pnl in realized_by_day.items():
        event_index = date_to_index[day]
        due_index = next_mark_index[(ticker, event_index)]
        scaled_pnl = pnl * scale
        if due_index is None:
            no_future_mark[ticker] += scaled_pnl
        else:
            scheduled[(ticker, due_index)] += scaled_pnl

    lots = {ticker: [] for ticker in tickers}
    loss_debit = defaultdict(float)
    cumulative_realized_overlay_pnl = defaultdict(float)
    daily_rows = []

    for index, day in enumerate(dates):
        for ticker in tickers:
            due_cash = scheduled.get((ticker, index), 0.0)
            mark = mark_indices[ticker].get(index)
            if due_cash and mark is None:
                raise ValueError(f"Scheduled transaction lacks a supplied mark: {ticker} {day}")
            purchase_cash = 0.0
            sale_proceeds = 0.0
            amount_bought = 0.0
            amount_sold = 0.0
            realized_overlay_today = 0.0
            if due_cash:
                balance = due_cash - loss_debit[ticker]
                if balance > 1e-10:
                    purchase_cash = balance
                    if ticker in ENERGY_TICKERS:
                        amount_bought = balance / unit_value
                        lots[ticker].append({"amount": amount_bought, "basis": balance, "entry": mark})
                    else:
                        amount_bought = balance / mark
                        lots[ticker].append({"amount": amount_bought, "basis": balance, "entry": mark})
                    loss_debit[ticker] = 0.0
                elif balance < -1e-10:
                    loss_to_cover = -balance
                    holdings_value = sum(
                        lot["amount"] * unit_value * mark / lot["entry"]
                        if ticker in ENERGY_TICKERS else lot["amount"] * mark
                        for lot in lots[ticker]
                    )
                    sale_proceeds = min(loss_to_cover, holdings_value)
                    if holdings_value > 0 and sale_proceeds > 0:
                        fraction_sold = sale_proceeds / holdings_value
                        for lot in lots[ticker]:
                            value = (lot["amount"] * unit_value * mark / lot["entry"]
                                     if ticker in ENERGY_TICKERS else lot["amount"] * mark)
                            value_sold = value * fraction_sold
                            basis_sold = lot["basis"] * fraction_sold
                            amount_sold += lot["amount"] * fraction_sold
                            lot["amount"] *= 1.0 - fraction_sold
                            lot["basis"] *= 1.0 - fraction_sold
                            realized_overlay_today += value_sold - basis_sold
                        lots[ticker] = [lot for lot in lots[ticker] if lot["amount"] > 1e-12]
                    loss_debit[ticker] = max(0.0, loss_to_cover - sale_proceeds)
                    cumulative_realized_overlay_pnl[ticker] += realized_overlay_today
                else:
                    # Exact offset: realized profit fully clears prior loss debit.
                    loss_debit[ticker] = 0.0

            mark = mark if mark is not None else _latest_mark(mark_indices[ticker], index)
            held_amount = sum(lot["amount"] for lot in lots[ticker])
            basis = sum(lot["basis"] for lot in lots[ticker])
            market_value = 0.0
            if mark is not None:
                market_value = sum(
                    lot["amount"] * unit_value * mark / lot["entry"]
                    if ticker in ENERGY_TICKERS else lot["amount"] * mark
                    for lot in lots[ticker]
                )
            unrealized = market_value - basis
            raw_realized = realized_by_day.get((ticker, day), 0.0)
            pending = sum(
                amount * scale for (event_ticker, event_day), amount in realized_by_day.items()
                if event_ticker == ticker and date_to_index[event_day] >= index
            )
            daily_rows.append({
                "date": day,
                "ticker": ticker,
                "asset_tracker_type": "model_U_equivalent" if ticker in ENERGY_TICKERS else "fractional_share",
                "tradingview_eod_mark": "" if mark is None else f"{mark:.8f}",
                "base_realized_pnl_usd": f"{raw_realized:.8f}",
                "scaled_realized_pnl_usd": f"{raw_realized * scale:.8f}",
                "next_mark_purchase_cash_usd": f"{purchase_cash:.8f}",
                "next_mark_sale_proceeds_usd": f"{sale_proceeds:.8f}",
                "amount_bought": f"{amount_bought:.10f}",
                "amount_sold": f"{amount_sold:.10f}",
                "shares_or_model_units_held": f"{held_amount:.10f}",
                "accumulator_cost_basis_usd": f"{basis:.8f}",
                "accumulator_market_value_usd": f"{market_value:.8f}",
                "accumulator_unrealized_pnl_usd": f"{unrealized:.8f}",
                "accumulator_realized_pnl_usd": f"{cumulative_realized_overlay_pnl[ticker]:.8f}",
                "accumulator_net_pnl_usd": f"{cumulative_realized_overlay_pnl[ticker] + unrealized:.8f}",
                "unfunded_loss_carry_usd": f"{loss_debit[ticker]:.8f}",
                "realized_pnl_pending_next_mark_usd": f"{pending:.8f}",
            })

    terminal = []
    for ticker in tickers:
        last_mark = _latest_mark(mark_indices[ticker], len(dates) - 1)
        held_amount = sum(lot["amount"] for lot in lots[ticker])
        basis = sum(lot["basis"] for lot in lots[ticker])
        market_value = sum(
            lot["amount"] * unit_value * last_mark / lot["entry"]
            if ticker in ENERGY_TICKERS else lot["amount"] * last_mark
            for lot in lots[ticker]
        ) if last_mark is not None else 0.0
        unrealized = market_value - basis
        realized_pnl = cumulative_realized_overlay_pnl[ticker]
        terminal.append({
            "ticker": ticker,
            "asset_tracker_type": "model_U_equivalent" if ticker in ENERGY_TICKERS else "fractional_share",
            "last_supplied_mark_date": dates[max(mark_indices[ticker])] if mark_indices[ticker] else "",
            "last_supplied_mark": "" if last_mark is None else f"{last_mark:.8f}",
            "base_realized_pnl_usd": f"{sum(pnl for (sym, _), pnl in realized_by_day.items() if sym == ticker):.8f}",
            "scaled_realized_pnl_usd": f"{sum(pnl for (sym, _), pnl in realized_by_day.items() if sym == ticker) * scale:.8f}",
            "shares_or_model_units_held": f"{held_amount:.10f}",
            "accumulator_cost_basis_usd": f"{basis:.8f}",
            "accumulator_market_value_usd": f"{market_value:.8f}",
            "accumulator_unrealized_pnl_usd": f"{unrealized:.8f}",
            "accumulator_realized_pnl_usd": f"{realized_pnl:.8f}",
            "accumulator_net_pnl_usd": f"{realized_pnl + unrealized:.8f}",
            "unfunded_loss_carry_usd": f"{loss_debit[ticker]:.8f}",
            "realized_pnl_without_future_mark_usd": f"{no_future_mark[ticker]:.8f}",
        })
    return daily_rows, terminal


def _latest_mark(mark_by_index, index):
    available = [i for i in mark_by_index if i <= index]
    return mark_by_index[max(available)] if available else None
