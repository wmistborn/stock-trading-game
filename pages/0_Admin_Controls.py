# pages/0_Admin_Controls.py
import streamlit as st
import pandas as pd
import os
from utils.excel_store import ExcelStore
from datetime import datetime

st.set_page_config(page_title="Admin Controls", page_icon="🛠️")
st.title("🛠️ Admin Control Center")
st.markdown("Create and configure a new game.")

# --- Create New Game ---
st.subheader("🎮 Start a New Game")
game_id = st.text_input("Game ID (4-digit code)", max_chars=4)
start_date = st.date_input("Game Start Date", datetime.today())
end_date = st.date_input("Game End Date")
starting_cash = st.number_input("Starting Cash Per Player ($)", min_value=0.0, value=1000.0)
max_trades_per_day = st.number_input("Max Trades Per Day", min_value=1, value=5)

# --- Register Players ---
st.markdown("### 👥 Register Players")
player_input = st.text_area("Enter Player IDs and Names (one per line, format: ID,Name)")

if st.button("🚀 Launch New Game"):
    if not game_id or not player_input.strip():
        st.error("Please enter a Game ID and register at least one player.")
    else:
        # --- Parse Player Entries ---
        players = []
        for line in player_input.strip().split("\n"):
            try:
                pid, name = [x.strip() for x in line.split(",")]
                players.append({"PlayerID": pid, "PlayerName": name, "CashBalance": starting_cash})
            except:
                st.warning(f"Invalid format: {line}")

        # --- Initialize Excel Store ---
        file_name = f"Game_{game_id}.xlsx"
        store = ExcelStore(file_name)
        store.create_game_file()
        store.write_game_info(game_id, start_date, end_date, starting_cash, max_trades_per_day)
        store.write_players(players)

        st.success(f"New game {game_id} created and saved to {file_name}!")
        st.session_state["current_game"] = file_name

# --- Load Existing Game ---
st.subheader("📂 Load Existing Game")
existing_games = [f for f in os.listdir(".") if f.startswith("Game_") and f.endswith(".xlsx")]
selected_game = st.selectbox("Select a Game File", existing_games)

if st.button("📥 Load Game"):
    st.session_state["current_game"] = selected_game
    st.success(f"Game {selected_game} loaded.")
