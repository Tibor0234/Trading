import pandas as pd
from config import exchange

def fetch_data_limit(symbol, timeframe, limit):
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=int(limit))
    df = pd.DataFrame(ohlcv, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
    df['time'] = df['time'] / 1000
    return df

def fetch_data_limit_since(symbol, timeframe, limit, since):
    since = since * 1000
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=int(limit), since=int(since))
    df = pd.DataFrame(ohlcv, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
    df['time'] = df['time'] / 1000
    return df