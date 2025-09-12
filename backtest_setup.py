import pandas as pd
from data.db_handler import Database
from config import db_path_backtest
from utils import symbols
from config import root

symbol = symbols[1]

eth_candles_path = root + r'\candles_for_backtest\ETHUSD_1m_KuCoin.csv'
df = pd.read_csv(eth_candles_path)

df_1m = df[['Open time', 'Open', 'High', 'Low', 'Close', 'Volume']].copy()
df_1m.columns = ['time', 'open', 'high', 'low', 'close', 'volume']
df_1m['time'] = pd.to_datetime(df_1m['time'])
df_1m.set_index('time', inplace=True)

df_5m = df_1m.resample('5min').agg({
    'open': 'first',
    'high': 'max',
    'low': 'min',
    'close': 'last',
    'volume': 'sum'
})

df_15m = df_5m.resample('15min').agg({
    'open': 'first',
    'high': 'max',
    'low': 'min',
    'close': 'last',
    'volume': 'sum'
})

df_1h = df_15m.resample('1h').agg({
    'open': 'first',
    'high': 'max',
    'low': 'min',
    'close': 'last',
    'volume': 'sum'
})

df_4h = df_1h.resample('4h').agg({
    'open': 'first',
    'high': 'max',
    'low': 'min',
    'close': 'last',
    'volume': 'sum'
})

df_1d = df_4h.resample('1D').agg({
    'open': 'first',
    'high': 'max',
    'low': 'min',
    'close': 'last',
    'volume': 'sum'
})

df_1w = df_1d.resample('1W').agg({
    'open': 'first',
    'high': 'max',
    'low': 'min',
    'close': 'last',
    'volume': 'sum'
})

for df_ in [df_1m, df_5m, df_15m, df_1h, df_4h, df_1d, df_1w]:
    df_.index = df_.index.astype('int64') // 10**9
    df_.index.name = 'time'
    df_.reset_index(inplace=True)

Database.init_database(db_path_backtest)

Database.instance.save_to_db_replace(df_1m, symbol, '1m')
Database.instance.save_to_db_replace(df_5m, symbol, '5m')
Database.instance.save_to_db_replace(df_15m, symbol, '15m')
Database.instance.save_to_db_replace(df_1h, symbol, '1h')
Database.instance.save_to_db_replace(df_4h, symbol, '4h')
Database.instance.save_to_db_replace(df_1d, symbol, '1d')
Database.instance.save_to_db_replace(df_1w, symbol, '1w')

print(f'{symbol} gyertyák betöltve backtest adatbázisba.')