# pages/3_Leaderboard.py
import streamlit as st
import pandas as pd
from utils.excel_store import ExcelGameStore

st.set_page_config(page_title="Leaderboard")

# ---------- Title ----------
st.title("🏆 Leaderboard")

# ---------- Load Game ----------
if "game_id" not in st.session_state:
    st.warning("Please load or create a game from the Home or Admin page.")
    st.stop()

store = ExcelGameStore(st.session_state["game_id"])
if not store.game_exists():
    st.error("Game file not found.")
    st.stop()

# ---------- Load Leaderboard ----------
leaderboard_df = store.read_sheet("Leaderboard")
if leaderboard_df.empty:
    st.info("Leaderboard is currently empty. Players must submit trades first.")
    st.stop()

# ---------- Sort & Display ----------
leaderboard_df = leaderboard_df.copy()
leaderboard_df["Rank"] = leaderboard_df["NetWorth"].rank(method="min", ascending=False).astype(int)
leaderboard_df = leaderboard_df.sort_values(by="NetWorth", ascending=False)

st.dataframe(
    leaderboard_df[["Rank", "Player", "Cash", "PortfolioValue", "NetWorth"]],
    use_container_width=True,
    hide_index=True
)

# ---------- Highlight Winner ----------
top_player = leaderboard_df.iloc[0]
st.success(f"🥇 Current Leader: **{top_player['Player']}** with Net Worth of **${top_player['NetWorth']:,.2f}**")

# ---------- Optional Chart ----------
with st.expander("📊 View Net Worth Chart"):
    st.bar_chart(data=leaderboard_df.set_index("Player")[["NetWorth"]])

