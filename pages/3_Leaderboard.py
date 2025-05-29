# pages/3_Leaderboard.py
import streamlit as st
from utils.db_utils import get_leaderboard_data

st.title("🏆 Leaderboard")
st.markdown("See how players rank based on total net worth (cash + portfolio value).")

# --- Fetch Leaderboard Data ---
df = get_leaderboard_data()

if df.empty:
    st.info("Leaderboard is currently empty. No trades or players found.")
else:
    df.index += 1  # To show rank starting at 1
    df.rename(columns={
        "PlayerName": "👤 Player",
        "CashBalance": "💰 Cash",
        "PortfolioValue": "📦 Portfolio",
        "NetWorth": "💎 Net Worth"
    }, inplace=True)

    st.dataframe(
        df.style.format({
            "💰 Cash": "${:,.2f}",
            "📦 Portfolio": "${:,.2f}",
            "💎 Net Worth": "${:,.2f}"
        }),
        use_container_width=True
    )
