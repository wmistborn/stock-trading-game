# 0_Start_Page.py
import streamlit as st
import os
from datetime import datetime
import pandas as pd
from utils.excel_store import ExcelGameStore


games_dir = "games"

# Create the games directory if it doesn't exist
if not os.path.exists(games_dir):
    os.makedirs(games_dir)

# Now safely list files
available_games = [f.replace(".xlsx", "") for f in os.listdir(games_dir) if f.endswith(".xlsx")]

st.set_page_config(page_title="Start Page",)

# ---------- Title ----------
st.title("📈 Stock Trading Game")
st.markdown("""
Welcome to the Stock Trading Simulation!  
Compete with friends to build the most valuable portfolio over a set time period using real-time market data.
""")

# ---------- App Description ----------
with st.expander("📘 How the Game Works", expanded=False):
    st.markdown(
        """
        Compete with friends to build the most valuable portfolio over a set time period using real-time market data.
    
        1. **Admin** creates a game with a unique Game ID, players, rules, and time period.
        2. **Players** submit trades within the allowed limits (e.g., 3 trades/day).
        3. **Prices** are pulled from Yahoo Finance to simulate real trading.
        4. **Leaderboard** updates based on portfolio values + remaining cash.
        """
    )

# ---------- Show Existing Games ----------
st.subheader("📂 Current & Past Games")
folder = "games"
if os.path.exists(folder):
    game_files = [f.replace(".xlsx", "") for f in os.listdir(folder) if f.endswith(".xlsx")]
    if game_files:
        game_df = pd.DataFrame({"Game ID": sorted(game_files)})
        st.dataframe(game_df, use_container_width=True, hide_index=True)
    else:
        st.info("No games have been created yet.")
else:
    st.info("Game folder not found.")

# ---------- Load Game ID ----------
st.subheader("🎮 Load Existing Game")

# Scan the active_games directory
games_dir = "data/active_games"
available_games = [f.replace(".xlsx", "") for f in os.listdir(games_dir) if f.endswith(".xlsx")]

if not available_games:
    st.info("No active games found. Please create one using the Admin Controls.")
else:
    selected_game = st.selectbox("Select a Game ID", sorted(available_games))

    if st.button("🔓 Load Selected Game"):
        file_path = os.path.join(games_dir, f"{selected_game}.xlsx")
        if os.path.exists(file_path):
            st.session_state["game_id"] = selected_game
            st.session_state["file_path"] = file_path
            st.success(f"Game {selected_game} loaded! Use the menu to view or submit trades.")
        else:
            st.error("Selected file no longer exists.")

# ---------- Footer ----------
st.markdown("---")
st.caption("Built with ❤️ in Streamlit • Powered by yFinance • Managed via Excel")

