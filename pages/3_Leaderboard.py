# pages/3_Leaderboard.py
import streamlit as st
import pandas as pd
import altair as alt
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
top_net_worth = leaderboard_df["NetWorth"].max()
leaders = leaderboard_df[leaderboard_df["NetWorth"] == top_net_worth]["Player"].tolist()

if len(leaders) == 1:
    st.success(f"🥇 Current Leader: **{leaders[0]}** with Net Worth of **${top_net_worth:,.2f}**")
else:
    names = ", ".join(leaders)
    st.success(f"🥇 Tie for Leader: **{names}** with Net Worth of **${top_net_worth:,.2f}**")

# ---------- Stacked Net Worth Breakdown Chart ----------
with st.expander("📊 View Net Worth Breakdown (Stacked)"):

    holdings_df = store.read_sheet("PlayerHoldings")

    stock_values = (
        holdings_df.groupby(["Player", "StockSymbol"])["TotalValue"]
        .sum()
        .reset_index()
    )

    cash_df = leaderboard_df[["Player", "Cash"]].copy()
    cash_df["StockSymbol"] = "💵 Cash"
    cash_df.rename(columns={"Cash": "TotalValue"}, inplace=True)

    combined_df = pd.concat([stock_values, cash_df], ignore_index=True)
    combined_df["TotalValue"] = combined_df["TotalValue"].round(2)

    # Ensure Player order matches descending Net Worth
    player_order = leaderboard_df.sort_values(by="NetWorth", ascending=False)["Player"].tolist()

    chart = (
        alt.Chart(combined_df)
        .mark_bar()
        .encode(
            x=alt.X("Player:N", sort=player_order, title="Player"),
            y=alt.Y("sum(TotalValue):Q", title="Net Worth"),
            color=alt.Color("StockSymbol:N", title="Asset"),
            tooltip=["Player", "StockSymbol", "TotalValue"]
        )
        .properties(height=400)
    )

    st.altair_chart(chart, use_container_width=True)
