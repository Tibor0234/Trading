import sqlite3 as sql
import pandas as pd

class Database:
    instance = None

    @staticmethod
    def init_database(db_path):
        Database.instance = Database(db_path)

    def __init__(self, db_path):
        self.conn = sql.connect(db_path, check_same_thread=False)

    def save_to_db_replace(self, df, symbol, timeframe):
        df.to_sql(f'{symbol}_{timeframe}', self.conn, if_exists='replace', index=False)

    def save_to_db_append(self, df, symbol, timeframe):
        df.to_sql(f'{symbol}_{timeframe}', self.conn, if_exists='append', index=False)

    def read_from_db_all(self, symbol, timeframe):
        query = f'SELECT * FROM "{symbol}_{timeframe}"'
        df = pd.read_sql_query(query, self.conn)
        df = df.sort_values(by='time')

        return df

    def read_from_db_limit(self, symbol, timeframe, limit):
        query = f'SELECT * FROM "{symbol}_{timeframe}" ORDER BY time DESC LIMIT {limit}'
        df = pd.read_sql_query(query, self.conn)
        df = df.sort_values(by='time')

        return df

    def read_from_db_limit_to(self, symbol, timeframe, limit, to):
        query = f'SELECT * FROM "{symbol}_{timeframe}" WHERE time < {to} ORDER BY time DESC LIMIT {limit}'
        df = pd.read_sql_query(query, self.conn)
        df = df.sort_values(by='time')
        
        return df