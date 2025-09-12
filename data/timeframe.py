import time
import pandas as pd
from abc import ABC, abstractmethod
from data.db_handler import Database
from data.api_client import fetch_data_limit
from data.log_handler import log_event

class Timeframe(ABC):
    def __init__(self, sym, tf, timestamp, candle, candles_to_cache, callback_on_close, callback_on_restore, analyzer):
        self.symbol = sym
        self.timeframe = tf
        self.timestamp = timestamp
        self.candle = candle
        self.cache_df = candles_to_cache
        self.callback_on_close = callback_on_close
        self.callback_on_restore = callback_on_restore
        self.analyzer = analyzer

    def is_candle_closed(self):
        expected_close_time = self.candle.open_time + self.timestamp
        if self.candle.time >= expected_close_time:
            return True
        return False

    def close_candle(self):
        closed_candle_df = self.candle.convert_to_df()
        self.save_to_db_abstract(closed_candle_df)

        self.candle.init_new_candle(self.timestamp)
        self.update_cache(closed_candle_df)
        self.callback_on_close(self.symbol, self.timeframe, self.cache_df)

    def update_cache(self, candles_df):
        self.cache_df = pd.concat([self.cache_df, candles_df], ignore_index=True)

        if len(self.cache_df) > 399:
            self.cache_df = self.cache_df.iloc[-399:]

    @abstractmethod
    def save_to_db_abstract(self, closed_candle_df):
        pass
        
class TimeframeLive(Timeframe):
    def is_data_lost(self):
        expected_close_time = self.candle.open_time + self.timestamp
        if self.candle.time >= expected_close_time + self.timestamp:
            return True
        return False
    
    def restore_data(self):
        now = int(time.time())
        limit = int((now - self.candle.open_time) // self.timestamp) + 1

        restored_candles_df = fetch_data_limit(self.symbol, self.timeframe, limit)

        if len(restored_candles_df) > 1:
            candles_to_save = restored_candles_df.iloc[:-1]
            filtered_candles_to_save = candles_to_save[~candles_to_save['time'].isin(self.cache_df['time'])]
            self.save_to_db_abstract(filtered_candles_to_save, self.symbol, self.timeframe)
            self.update_cache(filtered_candles_to_save)

            self.callback_on_restore(self.symbol, self.timeframe, self.cache_df)

        last_candle_df = restored_candles_df.iloc[[-1]]
        self.candle.convert_from_df(last_candle_df)

        if self.timeframe == '1m':
            log_event(f'{len(restored_candles_df)} minutes have been restored on {self.symbol}')

    def save_to_db_abstract(self, closed_candle_df):
        Database.instance.save_to_db_append(closed_candle_df, self.symbol, self.timeframe)

class TimeframeBacktest(Timeframe):
    def save_to_db_abstract(self, closed_candle_df):
        pass