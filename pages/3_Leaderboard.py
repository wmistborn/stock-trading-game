# pages/3_Leaderboard.py
import streamlit as st
import pandas as pd
from utils.db_utils import get_leaderboard_data

st.title("🏆 Leaderboard")
st.markdown("""
View the current rankings of all players based on total net worth.
""")

# --- Retrieve Leaderboard ---
leaderboard = get_leaderboard_data()

if not leaderboard.empty:
    st.dataframe(leaderboard, use_container_width=True, height=500)
else:
    st.info("Leaderboard data is not available.")
