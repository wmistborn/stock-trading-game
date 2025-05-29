# utils/game_utils.py
import pandas as pd

def initialize_portfolio(players, starting_cash):
    """Create an empty holdings DataFrame for all players."""
    data = []
    for player in players:
        data.append({"Player": player, "Cash": starting_cash, "PortfolioValue": 0.0})
    return pd.DataFrame(data)

def update_portfolio(holdings_df, transactions_df, price_lookup):
    """Update portfolio values and cash balances."""
    holdings = holdings_df.copy()
    for player in holdings["Player"]:
        player_trades = transactions_df[transactions_df["Player"] == player]
        player_holdings = {}

        cash = holdings.loc[holdings["Player"] == player, "Cash"].values[0]
        for _, row in player_trades.iterrows():
            symbol = row["StockSymbol"]
            shares = row["Shares"]
            price = price_lookup.get(symbol, 0)
            total_cost = shares * price
            if row["Action"] == "BUY":
                cash -= total_cost
                player_holdings[symbol] = player_holdings.get(symbol, 0) + shares
            elif row["Action"] == "SELL":
                cash += total_cost
                player_holdings[symbol] = player_holdings.get(symbol, 0) - shares

        portfolio_value = sum(price_lookup.get(sym, 0) * qty for sym, qty in player_holdings.items())
        holdings.loc[holdings["Player"] == player, "PortfolioValue"] = round(portfolio_value, 2)
        holdings.loc[holdings["Player"] == player, "Cash"] = round(cash, 2)

    return holdings
