# pages/2_Portfolio.py
import streamlit as st
from utils.db_utils import get_player_portfolio, get_cash_balance
from utils.price_utils import get_latest_price

st.title("📊 My Portfolio")
st.markdown("View your current holdings and overall portfolio value.")

# --- Player ID Input ---
player_id = st.text_input("🔑 Enter Your Player ID")

if player_id:
    portfolio_df = get_player_portfolio(player_id)
    cash = get_cash_balance(player_id)

    if portfolio_df.empty:
        st.info("You currently do not hold any stocks.")
    else:
        st.markdown("### 📦 Stock Holdings")
        
        # Optional: fetch latest prices again just to verify display (not strictly needed if stored already)
        total_portfolio_value = portfolio_df["Value"].sum()
        net_worth = round(total_portfolio_value + cash, 2)

        st.dataframe(portfolio_df.style.format({"Shares": "{:.0f}", "Value": "${:,.2f}"}))

        st.markdown("---")
        st.metric(label="💰 Cash Balance", value=f"${cash:,.2f}")
        st.metric(label="📈 Portfolio Value", value=f"${total_portfolio_value:,.2f}")
        st.metric(label="🧮 Net Worth", value=f"${net_worth:,.2f}")
else:
    st.info("Please enter your Player ID to view your portfolio.")

