import pandas as pd
from datetime import datetime
import os

class ExcelStore:
    def __init__(self, file_path):
        self.file_path = file_path
        if not os.path.exists(file_path):
            self._initialize_workbook()
        self._load_workbook()

    def _initialize_workbook(self):
        data = {
            'GameInfo': pd.DataFrame(columns=['GameID', 'StartDate', 'EndDate', 'StartingCash', 'MaxTrades']),
            'Players': pd.DataFrame(columns=['PlayerID', 'PlayerName', 'CashBalance']),
            'Portfolios': pd.DataFrame(columns=['PlayerID', 'StockSymbol', 'Quantity']),
            'Transactions': pd.DataFrame(columns=['TransactionID', 'PlayerID', 'StockSymbol', 'TradeType', 'Quantity', 'Price', 'TradeDate']),
            'MarketPrices': pd.DataFrame(columns=['StockSymbol', 'Price', 'RetrievedAt'])
        }
        with pd.ExcelWriter(self.file_path, engine='openpyxl') as writer:
            for sheet, df in data.items():
                df.to_excel(writer, sheet_name=sheet, index=False)

    def _load_workbook(self):
        self.workbook = pd.read_excel(self.file_path, sheet_name=None)

    def save(self):
        with pd.ExcelWriter(self.file_path, engine='openpyxl', mode='w') as writer:
            for sheet_name, df in self.workbook.items():
                df.to_excel(writer, sheet_name=sheet_name, index=False)

    def register_player(self, player_id, player_name, starting_cash):
        players = self.workbook['Players']
        if player_id not in players['PlayerID'].values:
            players.loc[len(players)] = [player_id, player_name, starting_cash]
            self.workbook['Players'] = players
            self.save()

    def get_cash_balance(self, player_id):
        players = self.workbook['Players']
        row = players[players['PlayerID'] == player_id]
        if row.empty:
            return 0.0
        return float(row.iloc[0]['CashBalance'])

    def get_held_shares(self, player_id, symbol):
        portfolios = self.workbook['Portfolios']
        row = portfolios[(portfolios['PlayerID'] == player_id) & (portfolios['StockSymbol'] == symbol)]
        if row.empty:
            return 0
        return int(row.iloc[0]['Quantity'])

    def log_transaction(self, player_id, symbol, trade_type, quantity, price):
        tx = self.workbook['Transactions']
        tx_id = len(tx) + 1
        tx.loc[len(tx)] = [tx_id, player_id, symbol, trade_type, quantity, price, datetime.now()]
        self.workbook['Transactions'] = tx
        self.save()

    def update_after_trades(self):
        players = self.workbook['Players']
        portfolios = self.workbook['Portfolios']
        tx = self.workbook['Transactions']

        portfolios = portfolios.groupby(['PlayerID', 'StockSymbol'], as_index=False)['Quantity'].sum()
        tx['Value'] = tx['Quantity'] * tx['Price']

        # Recalculate CashBalance per player
        tx['SignedValue'] = tx.apply(lambda x: -x['Value'] if x['TradeType'] == 'Buy' else x['Value'], axis=1)
        cash_balances = tx.groupby('PlayerID')['SignedValue'].sum().reset_index()

        for idx, row in cash_balances.iterrows():
            player_id = row['PlayerID']
            delta = row['SignedValue']
            players.loc[players['PlayerID'] == player_id, 'CashBalance'] += delta

        self.workbook['Players'] = players
        self.workbook['Portfolios'] = portfolios
        self.save()

    def get_player_portfolio(self, player_id):
        portfolios = self.workbook['Portfolios']
        market_prices = self.workbook.get('MarketPrices', pd.DataFrame(columns=['StockSymbol', 'Price']))

        holdings = portfolios[portfolios['PlayerID'] == player_id].copy()
        holdings = holdings.merge(market_prices, on='StockSymbol', how='left')
        holdings['Value'] = holdings['Quantity'] * holdings['Price']

        return holdings[['StockSymbol', 'Quantity', 'Price', 'Value']]

    def get_leaderboard(self):
        players = self.workbook['Players']
        portfolios = self.workbook['Portfolios']
        prices = self.workbook.get('MarketPrices', pd.DataFrame(columns=['StockSymbol', 'Price']))

        merged = portfolios.merge(prices, on='StockSymbol', how='left')
        merged['Value'] = merged['Quantity'] * merged['Price']
        port_vals = merged.groupby('PlayerID')['Value'].sum().reset_index(name='PortfolioValue')

        leaderboard = players.merge(port_vals, on='PlayerID', how='left')
        leaderboard['PortfolioValue'] = leaderboard['PortfolioValue'].fillna(0)
        leaderboard['NetWorth'] = leaderboard['CashBalance'] + leaderboard['PortfolioValue']
        return leaderboard[['PlayerID', 'PlayerName', 'CashBalance', 'PortfolioValue', 'NetWorth']].sort_values(by='NetWorth', ascending=False)

    def set_market_price(self, symbol, price):
        mp = self.workbook['MarketPrices']
        mp = mp[mp['StockSymbol'] != symbol]  # Remove old entry if exists
        mp.loc[len(mp)] = [symbol, price, datetime.now()]
        self.workbook['MarketPrices'] = mp
        self.save()
