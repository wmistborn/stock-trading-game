import pandas as pd
from openpyxl import load_workbook, Workbook
from datetime import datetime

class ExcelStore:
    def __init__(self, file_path):
        self.file_path = file_path

    def create_game_file(self):
        wb = Workbook()

        wb.create_sheet("GameInfo", 0)
        wb["GameInfo"].append(["GameID", "StartDate", "EndDate", "StartingCash", "MaxTradesPerDay"])

        wb.create_sheet("Players", 1)
        wb["Players"].append(["PlayerID", "PlayerName", "CashBalance"])

        wb.create_sheet("Transactions", 2)
        wb["Transactions"].append(["PlayerID", "StockSymbol", "TradeType", "Quantity", "Price", "TradeDate"])

        wb.create_sheet("Portfolios", 3)
        wb["Portfolios"].append(["PlayerID", "StockSymbol", "Quantity", "LatestPrice", "LastUpdated"])

        wb.save(self.file_path)

    def _read_sheet(self, sheet_name):
        return pd.read_excel(self.file_path, sheet_name=sheet_name)

    def _write_sheet(self, df, sheet_name):
        with pd.ExcelWriter(self.file_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=False)

    def register_player(self, player_id, player_name, starting_cash):
        df = self._read_sheet("Players")
        new_row = pd.DataFrame([[player_id, player_name, starting_cash]], columns=df.columns)
        df = pd.concat([df, new_row], ignore_index=True)
        self._write_sheet(df, "Players")

    def insert_trade(self, player_id, symbol, trade_type, quantity, price):
        df = self._read_sheet("Transactions")
        new_row = pd.DataFrame([[player_id, symbol, trade_type, quantity, price, datetime.now()]], columns=df.columns)
        df = pd.concat([df, new_row], ignore_index=True)
        self._write_sheet(df, "Transactions")

    def get_cash_balance(self, player_id):
        df = self._read_sheet("Players")
        row = df[df["PlayerID"] == player_id]
        return float(row["CashBalance"].values[0]) if not row.empty else 0.0

    def get_held_shares(self, player_id, symbol):
        df = self._read_sheet("Portfolios")
        row = df[(df["PlayerID"] == player_id) & (df["StockSymbol"] == symbol)]
        return int(row["Quantity"].values[0]) if not row.empty else 0

    def get_player_portfolio(self, player_id):
        df = self._read_sheet("Portfolios")
        df = df[df["PlayerID"] == player_id].copy()
        if df.empty:
            return pd.DataFrame(columns=["StockSymbol", "Shares", "Value"])
        df["Shares"] = df["Quantity"]
        df["Value"] = round(df["Quantity"] * df["LatestPrice"], 2)
        return df[["StockSymbol", "Shares", "Value"]]

    def get_leaderboard(self):
        players_df = self._read_sheet("Players")
        portfolios_df = self._read_sheet("Portfolios")

        portfolios_df["Value"] = portfolios_df["Quantity"] * portfolios_df["LatestPrice"]
        grouped = portfolios_df.groupby("PlayerID")["Value"].sum().reset_index()
        merged = players_df.merge(grouped, on="PlayerID", how="left").fillna(0)
        merged["NetWorth"] = merged["CashBalance"] + merged["Value"]
        return merged.sort_values("NetWorth", ascending=False)[["PlayerID", "PlayerName", "CashBalance", "Value", "NetWorth"]]

    def set_market_price(self, symbol, price):
        mp = self.workbook['MarketPrices']
        mp = mp[mp['StockSymbol'] != symbol]  # Remove old entry if exists
        mp.loc[len(mp)] = [symbol, price, datetime.now()]
        self.workbook['MarketPrices'] = mp
        self.save()
