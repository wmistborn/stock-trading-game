# pages/2_Trade_Submission.py
import streamlit as st
import pandas as pd
from datetime import datetime
from utils.excel_store import ExcelGameStore
from utils.price_utils import get_current_price
from utils.validation import validate_trade

st.set_page_config(page_title="Submit Trade")

# ---------- Page Header ----------
st.title("📤 Trade Submission")

# ---------- Load Game Info ----------
if "game_id" not in st.session_state:
    st.warning("Please load or create a game from the Home or Admin page.")
    st.stop()

store = ExcelGameStore(st.session_state["game_id"])
if not store.game_exists():
    st.error("Game file not found. Please go back to the Admin page and re-create the game.")
    st.stop()

game_info = store.load_game_info()
players = game_info["Players"]
max_trades = game_info["MaxTradesPerDay"]
start_date = game_info["StartDate"].date()
end_date = game_info["EndDate"].date()

# ---------- Trade Submission Form ----------
with st.form("trade_form"):
    st.subheader("🧾 Enter a Trade")
    player = st.selectbox("Player", players)
    stock = st.text_input("Stock Symbol (e.g., AAPL)", max_chars=10).upper()
    action = st.radio("Action", ["BUY", "SELL"])
    shares = st.number_input("Number of Shares", min_value=1, value=1)
    submit = st.form_submit_button("Submit Trade")

# ---------- Trade Validation ----------
if submit:
    today = datetime.now().date()
    if today < start_date or today > end_date:
        st.error(f"Trade rejected: today is outside the game window ({start_date} to {end_date}).")
        st.stop()

    price = get_current_price(stock)
    if not price:
        st.error("Unable to fetch price. Please check the ticker symbol.")
        st.stop()

    # Get player cash and today’s trade count
    leaderboard = store.read_sheet("Leaderboard")
    player_row = leaderboard[leaderboard["Player"] == player]
    if player_row.empty:
        st.error(f"Player '{player}' not found in Leaderboard. Has the game been initialized?")
        st.stop()

    current_cash = player_row["Cash"].values[0]
    
    all_trades = store.read_sheet("TradeQueue")
    trades_today = all_trades[
        (all_trades["Player"] == player) &
        (pd.to_datetime(all_trades["RequestedAt"]).dt.date == today)
    ]
    
    trade_data = {
        "Player": player,
        "StockSymbol": stock,
        "Action": action,
        "Shares": shares
    }

    errors = validate_trade(
        trade=trade_data,
        current_cash=current_cash,
        max_trades_today=max_trades,
        trades_today_count=len(trades_today),
        price_lookup={stock: price}
    )

    if errors:
        st.error("Trade Rejected:")
        for err in errors:
            st.markdown(f"- ❌ {err}")
    else:
        trade_row = {
            "TradeID": len(all_trades) + 1,
            "Player": player,
            "StockSymbol": stock,
            "Action": action,
            "Shares": shares,
            "RequestedAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Status": "Valid",
            "Notes": ""
        }
        # Append Valid Trades
        store.append_trades(pd.DataFrame([trade_row]))
        
        # 🔄 Update cash in Leaderboard
        leaderboard = store.read_sheet("Leaderboard")
        current_row = leaderboard[leaderboard["Player"] == player].index[0]

        trade_value = shares * price
        if action == "BUY":
            leaderboard.loc[current_row, "Cash"] -= trade_value
        elif action == "SELL":
            leaderboard.loc[current_row, "Cash"] += trade_value

        leaderboard.loc[current_row, "Cash"] = round(leaderboard.loc[current_row, "Cash"], 2)
        leaderboard["NetWorth"] = leaderboard["Cash"] + leaderboard["PortfolioValue"]
        leaderboard["NetWorth"] = leaderboard["NetWorth"].round(2)

        store.update_leaderboard(leaderboard)

        st.success(f"✅ Trade submitted successfully at ${price:.2f} per share.")
        st.info(f"💰 {player}'s cash balance updated to ${leaderboard.loc[current_row, 'Cash']:.2f}")

        # 🔁 Update PlayerHoldings
        holdings = store.read_sheet("PlayerHoldings")
        row_mask = (holdings["Player"] == player) & (holdings["StockSymbol"] == stock)

        if action == "BUY":
            if row_mask.any():
                holdings.loc[row_mask, "Shares"] += shares
            else:
                new_row = {
                    "Player": player,
                    "StockSymbol": stock,
                    "Shares": shares,
                    "CurrentPrice": price,
                    "TotalValue": round(shares * price, 2)
                }
                holdings = pd.concat([holdings, pd.DataFrame([new_row])], ignore_index=True)

        elif action == "SELL":
            if row_mask.any():
                current_shares = holdings.loc[row_mask, "Shares"].values[0]
                updated_shares = current_shares - shares
                if updated_shares > 0:
                    holdings.loc[row_mask, "Shares"] = updated_shares
                else:
                    holdings = holdings[~row_mask]  # remove row if no shares left

# 🔁 Update prices and total values
        holdings.loc[holdings["Player"] == player, "CurrentPrice"] = \
            holdings.loc[holdings["Player"] == player, "StockSymbol"].map(lambda sym: get_current_price(sym))

        holdings["TotalValue"] = holdings["Shares"] * holdings["CurrentPrice"]
        holdings = holdings.round({"TotalValue": 2, "CurrentPrice": 2})

# 🔁 Recalculate PortfolioValue
        portfolio_value = holdings[holdings["Player"] == player]["TotalValue"].sum()
        leaderboard.loc[current_row, "PortfolioValue"] = portfolio_value
        leaderboard.loc[current_row, "NetWorth"] = leaderboard.loc[current_row, "Cash"] + portfolio_value
        leaderboard = leaderboard.round(2)

# 🔁 Save updates
        store.update_holdings(holdings)
        store.update_leaderboard(leaderboard)
        
