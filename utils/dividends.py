#dividends.py
import yfinance as yf
import pandas as pd
from datetime import datetime

def check_and_apply_dividends(store):
    holdings = store.read_sheet("PlayerHoldings")
    leaderboard = store.read_sheet("Leaderboard")

    today = pd.Timestamp(datetime.now().date())

    # Prepare list of unique stocks
    unique_symbols = holdings["StockSymbol"].unique()
    dividend_events = []

    for symbol in unique_symbols:
        try:
            ticker = yf.Ticker(symbol)
            cal = ticker.dividends
            if cal.empty:
                continue

            # Filter for today
            recent_divs = cal[cal.index.date == today.date()]
            if recent_divs.empty:
                continue

            dividend_per_share = recent_divs[-1]
            players_holding = holdings[holdings["StockSymbol"] == symbol]

            for _, row in players_holding.iterrows():
                player = row["Player"]
                shares = row["Shares"]
                total = round(shares * dividend_per_share, 2)

                # Add to leaderboard cash
                leaderboard.loc[leaderboard["Player"] == player, "Cash"] += total

                dividend_events.append({
                    "Date": today,
                    "Player": player,
                    "StockSymbol": symbol,
                    "Shares": shares,
                    "DividendPerShare": dividend_per_share,
                    "TotalDividend": total
                })

        except Exception as e:
            print(f"Error checking dividend for {symbol}: {e}")

    # Save updated cash balances
    store.update_leaderboard(leaderboard)

    # Log dividend events
    if dividend_events:
        div_df = pd.DataFrame(dividend_events)
        try:
            prev_divs = store.read_sheet("Dividends")
            combined = pd.concat([prev_divs, div_df], ignore_index=True)
        except:
            combined = div_df
        store.write_sheet("Dividends", combined)

    return dividend_events
