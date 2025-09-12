import pandas as pd
from abc import ABC

class Candle(ABC):
    def __init__(self, candle_df):
        self.convert_from_df(candle_df)
        self.is_new_candle = False

    def init_new_candle(self, timestamp):
        self.open_time = self.open_time + timestamp
        self.time = self.open_time
        self.open = self.close
        self.high = self.close
        self.low = self.close
        self.close = self.close
        self.volume = 0
        self.is_new_candle = True

    def convert_to_series(self):
        candle_dict = {
            'time': self.open_time,
            'open': self.open,
            'high': self.high,
            'low': self.low,
            'close': self.close,
            'volume': self.volume
        }
        return pd.Series(candle_dict)
    
    def convert_to_df(self):
        return pd.DataFrame([self.convert_to_series()])
    
    def convert_from_df(self, candle_df):
        self.time = candle_df['time'].item()
        self.open = candle_df['open'].item()
        self.high = candle_df['high'].item()
        self.low = candle_df['low'].item()
        self.close = candle_df['close'].item()
        self.volume = candle_df['volume'].item()
        self.open_time = candle_df['time'].item()

class CandleLive(Candle):
    def update_candle(self, time, price, size):
        if self.is_new_candle:
            self.time = time
            self.open = price
            self.high = price
            self.low = price
            self.close = price
            self.volume = size
            self.is_new_candle = False
        else:
            self.time = time
            self.high = max(self.high, price)
            self.low = min(self.low, price)
            self.close = price
            self.volume += size

class CandleBacktest(Candle):
    def update_candle(self, time, open, high, low, close, volume):
        if self.is_new_candle:
            self.time = time
            self.open = open
            self.high = high
            self.low = low
            self.close = close
            self.volume = volume
            self.is_new_candle = False
        else:
            self.time = time
            self.high = max(self.high, high)
            self.low = min(self.low, low)
            self.close = close
            self.volume += volume