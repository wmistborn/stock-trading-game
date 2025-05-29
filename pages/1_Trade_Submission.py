# pages/1_Trade_Submission.py
import streamlit as st
import pandas as pd
import yfinance as yf
from utils.db_utils import insert_trade, get_cash_balance, get_held_shares

st.title("💼 Trade Submission")
st.markdown("""
Use this form to submit your trades. You can enter multiple trades in one batch. Prices can be fetched live via Yahoo Finance.
""")

# --- Player Info ---
player_id = st.text_input("🔑 Enter Your Player ID")

# --- Fetch Market Price ---
def fetch_live_price(symbol):
    try:
        return yf.Ticker(symbol).info['regularMarketPrice']
    except:
        return None

# --- Trade Table Editor ---
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
        cash = get_cash_balance(player_id)
        total_cost = 0

        for _, row in trades.iterrows():
            symbol = row['StockSymbol'].upper()
            trade_type = row['TradeType']
            qty = int(row['Quantity'])
            use_market = row['UseMarketPrice']
            price = float(row['Price'])

            if use_market:
                price = fetch_live_price(symbol) or 0

            cost = round(price * qty, 2)

            # Validation logic
            if trade_type == 'Buy':
                if total_cost + cost > cash:
                    validated.append((symbol, "❌ Not enough cash"))
                    continue
                total_cost += cost
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
                price = fetch_live_price(symbol) or 0

            insert_trade(player_id, symbol, trade_type, qty, price)

        st.success("Trades submitted successfully!")
else:
    st.info("Please enter your Player ID above to continue.")
