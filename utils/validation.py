def validate_trade(trade, current_cash, max_trades_today, trades_today_count, price_lookup):
    errors = []

    # Check ticker validity
    if trade["StockSymbol"] not in price_lookup:
        errors.append("Invalid ticker symbol.")

    # Check action
    if trade["Action"] not in ["BUY", "SELL"]:
        errors.append("Invalid trade action.")

    # Check positive share amount
    if trade["Shares"] <= 0:
        errors.append("Shares must be greater than 0.")

    # Check trade limit
    if trades_today_count >= max_trades_today:
        errors.append("Daily trade limit exceeded.")

    # Check sufficient cash (BUY only)
    if trade["Action"] == "BUY":
        symbol = trade["StockSymbol"]
        price = price_lookup.get(symbol, 0)
        total_cost = price * trade["Shares"]
        if total_cost > current_cash:
            errors.append("Insufficient cash to complete trade.")

    return errors
