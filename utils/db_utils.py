# utils/db_utils.py
import pyodbc
import pandas as pd
from datetime import datetime

# --- SQL Connection ---
def get_connection():
    return pyodbc.connect(
        r"DRIVER={SQL Server};SERVER=WBrocat_2\TESTSERVER;DATABASE=TEST_2;Trusted_Connection=yes;"
    )

# --- Insert Trade ---
def insert_trade(player_id, symbol, trade_type, quantity, price):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO Transactions (PlayerID, StockSymbol, TradeType, Quantity, Price, TradeDate)
        VALUES (?, ?, ?, ?, ?, ?)
    """, player_id, symbol, trade_type, quantity, price, datetime.now())
    conn.commit()
    conn.close()

# --- Get Cash Balance ---
def get_cash_balance(player_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT CashBalance FROM PlayerSummaries WHERE PlayerID = ?
    """, player_id)
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else 0.0

# --- Get Held Shares ---
def get_held_shares(player_id, symbol):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT SUM(CASE WHEN TradeType = 'Buy' THEN Quantity ELSE -Quantity END) AS SharesHeld
        FROM Transactions WHERE PlayerID = ? AND StockSymbol = ?
    """, player_id, symbol)
    row = cursor.fetchone()
    conn.close()
    return row[0] if row and row[0] else 0

# --- Get Portfolio ---
def get_player_portfolio(player_id):
    conn = get_connection()
    query = """
        SELECT t.StockSymbol,
               SUM(CASE WHEN t.TradeType = 'Buy' THEN t.Quantity ELSE -t.Quantity END) AS Shares,
               ROUND(SUM((CASE WHEN t.TradeType = 'Buy' THEN t.Quantity ELSE -t.Quantity END) * t.Price), 2) AS Value
        FROM Transactions t
        WHERE t.PlayerID = ?
        GROUP BY t.StockSymbol
        HAVING SUM(CASE WHEN t.TradeType = 'Buy' THEN t.Quantity ELSE -t.Quantity END) > 0
    """
    df = pd.read_sql(query, conn, params=[player_id])
    conn.close()
    return df

# --- Get Leaderboard ---
def get_leaderboard_data():
    conn = get_connection()
    query = """
        SELECT PlayerID,
               PlayerName,
               CashBalance,
               PortfolioValue,
               (CashBalance + PortfolioValue) AS NetWorth
        FROM PlayerSummaries
        ORDER BY NetWorth DESC
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df
