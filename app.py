# app.py
import streamlit as st
import os
from datetime import datetime

st.set_page_config(page_title="Stock Trading Game", layout="centered")

# ---------- Title & Introduction ----------
st.title("📈 Stock Trading Game")
st.markdown("""
Welcome to the Stock Trading Simulation!  
Compete with friends to build the most valuable portfolio over a set time period using real-time market data.
""")

# ---------- App Description ----------
with st.expander("📘 How the Game Works", expanded=False):
    st.markdown("""
    1. **Admin** creates a game with a unique Game ID, players, rules, and time period.
    2. **Players** submit trades within the allowed limits (e.g., 3 trades/day).
    3. **Prices** are pulled from Yahoo Finance to simulate real trading.
    4. **Leaderboard** updates based on portfolio values + remaining cash.

    ---
    """)
    st.markdown("Each game is saved as a separate Excel file for full transparency and traceability.")

# ---------- Load Game ID ----------
st.subheader("🎮 Load Existing Game")

game_id = st.text_input("Enter Game ID:", placeholder="e.g., 4073")
if st.button("Load Game"):
    file_path = f"data/active_games/{game_id}.xlsx"
    if os.path.exists(file_path):
        st.success(f"Game {game_id} loaded! Use the navigation menu to start trading.")
        st.session_state["game_id"] = game_id
        st.session_state["file_path"] = file_path
    else:
        st.error("Game not found. Please check the Game ID or contact the admin.")

# ---------- Footer ----------
st.markdown("---")
st.caption("Built with ❤️ in Streamlit • Powered by yFinance • Managed via Excel")

