# pages/1_Trade_Submission.py
import streamlit as st
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
start_date = game_info["StartDate"]
end_date = game_info["EndDate"]

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
    holdings = store.read_sheet("Leaderboard")
    current_cash = holdings.loc[holdings["Player"] == player, "Cash"].values[0]
    
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
        store.append_trades(pd.DataFrame([trade_row]))
        st.success(f"✅ Trade submitted successfully at ${price} per share.")
