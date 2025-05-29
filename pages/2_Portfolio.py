# pages/2_Portfolio.py
import streamlit as st
import pandas as pd
from utils.excel_store import ExcelStore

# --- Load Game File ---
st.session_state.setdefault("workbook_path", "GameData.xlsx")
store = ExcelStore(st.session_state["workbook_path"])

st.title("📊 Portfolio Viewer")

# --- Player ID Input ---
player_id = st.text_input("Enter Your Player ID")

if player_id:
    try:
        # Retrieve portfolio and cash balance
        portfolio_df = store.get_player_portfolio(player_id)
        cash = store.get_cash_balance(player_id)

        st.subheader("💼 Current Holdings")
        if not portfolio_df.empty:
            st.dataframe(portfolio_df, use_container_width=True)
        else:
            st.info("No current holdings.")

        st.subheader("💵 Cash Balance")
        st.write(f"${cash:,.2f}")

        st.subheader("📈 Total Portfolio Value")
        total_value = cash + portfolio_df["Value"].sum()
        st.write(f"${total_value:,.2f}")

    except Exception as e:
        st.error(f"Error loading portfolio: {e}")
else:
    st.info("Please enter your Player ID above to view your portfolio.")
