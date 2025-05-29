from utils.db_utils import get_connection

# --- Update Player's Cash Balance ---
def update_cash_balance(player_id, amount_delta):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE Players
            SET CashBalance = CashBalance + ?
            WHERE PlayerID = ?
        """, amount_delta, player_id)
        conn.commit()
    except Exception as e:
        print(f"[ERROR] Updating cash balance: {e}")
    finally:
        conn.close()

# --- Update Portfolio Holdings ---
def update_portfolio(player_id, symbol, quantity_delta):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Check if the record exists
        cursor.execute("""
            SELECT Quantity FROM Portfolios WHERE PlayerID = ? AND StockSymbol = ?
        """, player_id, symbol)
        row = cursor.fetchone()

        if row:
            new_qty = row[0] + quantity_delta
            if new_qty > 0:
                # Update existing row
                cursor.execute("""
                    UPDATE Portfolios SET Quantity = ? WHERE PlayerID = ? AND StockSymbol = ?
                """, new_qty, player_id, symbol)
            else:
                # Delete if shares drop to 0 or below
                cursor.execute("""
                    DELETE FROM Portfolios WHERE PlayerID = ? AND StockSymbol = ?
                """, player_id, symbol)
        else:
            # Insert new row
            cursor.execute("""
                INSERT INTO Portfolios (PlayerID, StockSymbol, Quantity)
                VALUES (?, ?, ?)
            """, player_id, symbol, quantity_delta)

        conn.commit()
    except Exception as e:
        print(f"[ERROR] Updating portfolio: {e}")
    finally:
        conn.close()
