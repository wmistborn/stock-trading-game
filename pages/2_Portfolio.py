# pages/2_Portfolio.py
import streamlit as st
import pandas as pd
from utils.excel_store import ExcelGameStore
from utils.price_utils import get_price_lookup

st.set_page_config(page_title="Player Portfolio")

# ---------- Page Title ----------
st.title("💼 View Portfolio")

# ---------- Load Game ----------
if "game_id" not in st.session_state:
    st.warning("Please load or create a game from the Home or Admin page.")
    st.stop()

store = ExcelGameStore(st.session_state["game_id"])
if not store.game_exists():
    st.error("Game file not found.")
    st.stop()

# ---------- Load Data ----------
holdings_df = store.read_sheet("PlayerHoldings")
leaderboard_df = store.read_sheet("Leaderboard")

if holdings_df.empty:
    st.info("No trades have been executed yet.")
    st.stop()

# ---------- Player Selector ----------
players = leaderboard_df["Player"].tolist()
selected_player = st.selectbox("Select a player to view holdings", players)

# ---------- Filter & Calculate ----------
player_holdings = holdings_df[holdings_df["Player"] == selected_player].copy()
symbols = player_holdings["StockSymbol"].tolist()

with st.spinner("🔄 Fetching live prices..."):
    price_lookup = get_price_lookup(symbols)

player_holdings["CurrentPrice"] = player_holdings["StockSymbol"].map(price_lookup)
player_holdings["TotalValue"] = player_holdings["Shares"] * player_holdings["CurrentPrice"]
player_holdings = player_holdings.round({"CurrentPrice": 2, "TotalValue": 2})

# ---------- Display Holdings ----------
st.subheader(f"📊 Holdings for {selected_player}")

if player_holdings.empty or player_holdings["Shares"].sum() == 0:
    st.info("No active holdings.")
else:
    st.dataframe(player_holdings[["StockSymbol", "Shares", "CurrentPrice", "TotalValue"]], use_container_width=True)

    total_value = player_holdings["TotalValue"].sum()
    st.metric(label="📈 Portfolio Value", value=f"${total_value:,.2f}")

# ---------- Optional: Update Sheet ----------
if st.button("📥 Save Updated Holdings & Value"):
    holdings_df.loc[holdings_df["Player"] == selected_player, "CurrentPrice"] = \
        holdings_df.loc[holdings_df["Player"] == selected_player, "StockSymbol"].map(price_lookup)

    holdings_df.loc[holdings_df["Player"] == selected_player, "TotalValue"] = \
        holdings_df.loc[holdings_df["Player"] == selected_player, "Shares"] * \
        holdings_df.loc[holdings_df["Player"] == selected_player, "StockSymbol"].map(price_lookup)

    leaderboard_df.loc[leaderboard_df["Player"] == selected_player, "PortfolioValue"] = total_value
    leaderboard_df["NetWorth"] = leaderboard_df["Cash"] + leaderboard_df["PortfolioValue"]
    leaderboard_df = leaderboard_df.round({"Cash": 2, "PortfolioValue": 2, "NetWorth": 2})

    store.update_holdings(holdings_df)
    store.update_leaderboard(leaderboard_df)
    st.success("Holdings and leaderboard updated successfully.")
