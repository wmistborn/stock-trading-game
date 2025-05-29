# app.py
import streamlit as st
from datetime import datetime

# --- Page Config ---
st.set_page_config(
    page_title="Stock Trading Game Hub",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Main Header ---
st.title("📈 Stock Trading Game Dashboard")
st.markdown("""
Welcome to the **Stock Trading Game** – a fun and competitive platform where you manage a virtual stock portfolio!

📌 Use the sidebar to navigate:
- 💼 Submit trades
- 📊 View your portfolio
- 🏆 Check the leaderboard

Admins can manage game setup, pricing updates, and resets via SQL backend.
""")

# --- Game Info Section (Optional) ---
st.subheader("🎮 Game Overview")
st.markdown("""
- 💰 Each player starts with a fixed cash balance.
- 📈 Buy and sell stocks using real market data.
- ⏳ Your goal: maximize your portfolio value by the end of the game window.
- ✅ Trades are validated in real time.
""")

# --- Footer ---
st.markdown("""
---
📅 **{0}**  
🔧 Built with Streamlit | Game by Wills & ChatGPT
""".format(datetime.today().strftime("%B %d, %Y")))
