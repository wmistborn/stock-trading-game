# pages/1_Trade_Submission.py
import streamlit as st
import pandas as pd
from utils.excel_store import ExcelStore
from utils.price_utils import get_price
from datetime import datetime
import os

st.set_page_config(page_title="Trade Submission", page_icon="💼")
st.title("💼 Trade Submission")

if "current_game" not in st.session_state:
    st.warning("Please load a game from the Admin Control page.")
    st.stop()

file_name = st.session_state["current_game"]
store = ExcelStore(file_name)

player_id = st.text_input("🔑 Enter Your Player ID")

# --- Trade Table Entry ---
def trade_form():
    st.markdown("### 📋 Trade Entry Table")
    trade_data = pd.DataFrame(
        [{"StockSymbol": "", "TradeType": "Buy", "Quantity": 0, "UseMarketPrice": True, "Price": 0.0}]
    )
    edited_df = st.data_editor(
        trade_data,
        num_rows="dynamic",
        use_container_width=True,
        key="trade_editor"
    )
    return edited_df

if player_id:
    trades = trade_form()
    st.markdown("---")

    if st.button("✅ Preview and Validate"):
        validated = []
        cash = store.get_cash_balance(player_id)
        total_cost = 0

        for _, row in trades.iterrows():
            symbol = row['StockSymbol'].upper()
            trade_type = row['TradeType']
            qty = int(row['Quantity'])
            use_market = row['UseMarketPrice']
            price = float(row['Price'])

            if use_market:
                price = get_price(symbol) or 0

            cost = round(price * qty, 2)

            if trade_type == 'Buy':
                if total_cost + cost > cash:
                    validated.append((symbol, "❌ Not enough cash"))
                    continue
                total_cost += cost
                validated.append((symbol, f"✅ Buy - ${cost:.2f}"))
            elif trade_type == 'Sell':
                held = store.get_held_shares(player_id, symbol)
                if qty > held:
                    validated.append((symbol, f"❌ Only holding {held} shares"))
                    continue
                validated.append((symbol, f"✅ Sell - ${cost:.2f}"))

        st.markdown("### 🧾 Validation Results")
        for sym, msg in validated:
            st.write(f"{sym}: {msg}")

    if st.button("🚀 Submit Valid Trades"):
        for _, row in trades.iterrows():
            symbol = row['StockSymbol'].upper()
            trade_type = row['TradeType']
            qty = int(row['Quantity'])
            price = float(row['Price'])

            if row['UseMarketPrice']:
                price = get_price(symbol) or 0

            store.log_transaction(player_id, symbol, trade_type, qty, price)

        store.update_after_trades()
        st.success("Trades submitted successfully!")
else:
    st.info("Please enter your Player ID above to continue.")
