# pages/3_Leaderboard.py
import streamlit as st
import pandas as pd
from utils.excel_store import ExcelStore

# --- Load Game File ---
st.session_state.setdefault("workbook_path", "GameData.xlsx")
store = ExcelStore(st.session_state["workbook_path"])

st.title("🏆 Leaderboard")

try:
    leaderboard_df = store.get_leaderboard()
    st.dataframe(leaderboard_df, use_container_width=True)
except Exception as e:
    st.error(f"Unable to load leaderboard: {e}")
