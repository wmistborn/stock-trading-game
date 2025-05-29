# pages/1_Trade_Submission.py
import streamlit as st
import pandas as pd
from utils.db_utils import insert_trade, get_cash_balance, get_held_shares
from utils.db_update import update_cash_balance, update_portfolio
from utils.price_utils import get_latest_price

st.title("💼 Trade Submission")
st.markdown("""
Use this form to submit your trades. You can enter multiple trades in one batch. Prices are fetched live from Yahoo Finance.
""")

# --- Player ID Input ---
player_id = st.text_input("🔑 Enter Your Player ID")

# --- Trade Entry Table ---
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

# --- Main Logic ---
if player_id:
    trades = trade_form()
    st.markdown("---")

    if st.button("✅ Preview and Validate"):
        validated = []
        cash = get_cash_balance(player_id)
        running_total = 0

        for _, row in trades.iterrows():
            symbol = row['StockSymbol'].upper()
            trade_type = row['TradeType']
            qty = int(row['Quantity'])
            price = float(row['Price'])

            if row['UseMarketPrice']:
                price = get_latest_price(symbol) or 0

            cost = round(price * qty, 2)

            if trade_type == 'Buy':
                if running_total + cost > cash:
                    validated.append((symbol, "❌ Not enough cash"))
                    continue
                running_total += cost
                validated.append((symbol, f"✅ Buy - ${cost:.2f}"))

            elif trade_type == 'Sell':
                held = get_held_shares(player_id, symbol)
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
                price = get_latest_price(symbol) or 0

            total_cost = round(price * qty, 2)

            # Update database
            insert_trade(player_id, symbol, trade_type, qty, price)

            # Update portfolio and cash
            if trade_type == "Buy":
                update_cash_balance(player_id, -total_cost)
                update_portfolio(player_id, symbol, qty)
            elif trade_type == "Sell":
                update_cash_balance(player_id, total_cost)
                update_portfolio(player_id, symbol, -qty)

        st.success("✅ Trades submitted and balances updated!")
else:
    st.info("Please enter your Player ID above to continue.")
