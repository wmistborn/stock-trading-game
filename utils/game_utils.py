# utils/game_utils.py
import pyodbc
from datetime import datetime

# --- SQL Connection ---
def get_connection():
    return pyodbc.connect(
        r"DRIVER={SQL Server};SERVER=WBrocat_2\TESTSERVER;DATABASE=TEST_2;Trusted_Connection=yes;"
    )

# --- Initialize a New Game ---
def start_new_game(game_id, start_date, end_date, starting_cash):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO GameInfo (GameID, StartDate, EndDate, StartingCash, CreatedAt)
        VALUES (?, ?, ?, ?, ?)
    """, game_id, start_date, end_date, starting_cash, datetime.now())
    conn.commit()
    conn.close()

# --- Register New Player ---
def register_player(player_id, player_name, game_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        DECLARE @StartingCash DECIMAL(18,2);
        SELECT @StartingCash = StartingCash FROM GameInfo WHERE GameID = ?;

        INSERT INTO Players (PlayerID, PlayerName, GameID, CreatedAt)
        VALUES (?, ?, ?, ?);

        INSERT INTO PlayerSummaries (PlayerID, GameID, CashBalance, PortfolioValue)
        VALUES (?, ?, @StartingCash, 0);
    """, game_id, player_id, player_name, game_id, datetime.now(), player_id, game_id)
    conn.commit()
    conn.close()
