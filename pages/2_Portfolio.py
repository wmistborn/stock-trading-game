# pages/2_Portfolio.py
import streamlit as st
import pandas as pd
from utils.db_utils import get_player_portfolio, get_cash_balance

st.title("📊 Player Portfolio")

# --- Player Info ---
player_id = st.text_input("🔑 Enter Your Player ID")

if player_id:
    cash = get_cash_balance(player_id)
    st.metric("💰 Current Cash Balance", f"${cash:,.2f}")

    portfolio = get_player_portfolio(player_id)

    if not portfolio.empty:
        st.markdown("### 📦 Holdings")
        st.dataframe(portfolio, use_container_width=True)

        # Show total portfolio value
        portfolio_value = portfolio['Value'].sum()
        total_value = portfolio_value + cash

        st.markdown(f"**📈 Portfolio Value:** ${portfolio_value:,.2f}")
        st.markdown(f"**💼 Total Net Worth:** ${total_value:,.2f}")
    else:
        st.info("No holdings found for this player.")
else:
    st.info("Please enter your Player ID above to view your portfolio.")
