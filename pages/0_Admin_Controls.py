# pages/0_Admin_Controls.py
import streamlit as st
from datetime import date
import random
import string
from utils.excel_store import ExcelGameStore
from utils.dividends import check_and_apply_dividends

st.set_page_config(page_title="Admin Controls")

# ---------- Title ----------
st.title("🛠️ Admin Controls — Create New Game")

# ---------- Helper: Generate Game ID ----------
def generate_game_id():
    return ''.join(random.choices(string.digits, k=4))

# ---------- New Game Form ----------
with st.form("create_game_form"):
    st.subheader("📋 Create a New Game")

    # Game details
    game_id = st.text_input("Game ID (leave blank to auto-generate)", value=generate_game_id())
    players_input = st.text_area("Player Names (one per line)", placeholder="Alice\nBob\nCharlie")
    starting_cash = st.number_input("Starting Cash", value=1000, min_value=100)
    max_trades = st.number_input("Max Trades per Day", value=3, min_value=1)
    start_date = st.date_input("Start Date", value=date.today())
    end_date = st.date_input("End Date")

    # Submit button
    submitted = st.form_submit_button("🚀 Create Game")

# ---------- Process Form Submission ----------
if submitted:
    players = [name.strip() for name in players_input.splitlines() if name.strip()]
    
    if not players:
        st.error("You must enter at least one player.")
    elif end_date < start_date:
        st.error("End date must be after start date.")
    else:
        store = ExcelGameStore(game_id)

        if store.game_exists():
            st.warning(f"A game with ID {game_id} already exists.")
        else:
            try:
                store.create_game_file(players, starting_cash, max_trades, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
                st.success(f"Game {game_id} created successfully!")

                # ✅ Set session state
                st.session_state["game_id"] = game_id
                st.session_state["file_path"] = store.get_path()

                st.info("Players can now go to the Trade Submission page to start building their portfolios.")
            except Exception as e:
                st.error(f"Error creating game: {e}")
# ---------- Dividend Payout Trigger ----------

st.subheader("💸 Game Maintenance")

if "game_id" in st.session_state:
    store = ExcelGameStore(st.session_state["game_id"])

    if store.game_exists():
        if st.button("📈 Apply Dividends"):
            events = check_and_apply_dividends(store)
            if events:
                st.success(f"{len(events)} dividend payouts applied.")
                st.dataframe(pd.DataFrame(events))
            else:
                st.info("No dividends scheduled for today.")
    else:
        st.warning("No existing game file found. Create or load a game to enable dividend payouts.")
else:
    st.info("Please load or create a game to enable dividend payouts.")

