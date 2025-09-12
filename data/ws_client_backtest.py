import threading
import traceback
from data.db_handler import Database
from utils import timeframes_and_multipliers, min_timeframe_backtest
from data.log_handler import log_event
from data.time_provider import TimeProvider
import pandas as pd

class WsClientBacktest:
    def __init__(self, symbol, callback):
        self.symbol = symbol
        self.callback = callback
        self.min_tf_mp = timeframes_and_multipliers.get(min_timeframe_backtest)

    def run_simulation(self, cursor, end_time):
        thread = threading.Thread(target=self.simulate_ws, args=(cursor, end_time))
        thread.daemon = True
        thread.start()

    def simulate_ws(self, cursor, end_time):
        TimeProvider.instance.set_time(cursor)
        log_event('Backtest process has been started.')
        print('A backtest folyamat elindult.')

        step = 200
        try:
            cursor += (self.min_tf_mp * 60) * (step * 2)

            if end_time:
                end_time = end_time + 1
            else:
                end_time = Database.instance.read_from_db_limit(self.symbol, min_timeframe_backtest, 1)['time'].iloc[0] + 1

            while cursor < end_time:
                print(pd.to_datetime(cursor, unit='s'))
                candles = Database.instance.read_from_db_limit_to(self.symbol, min_timeframe_backtest, step, cursor)
                if candles.empty:
                    cursor += (self.min_tf_mp * 60 * step)
                    continue

                last_candle = None
                for _, candle in candles.iterrows():
                    if last_candle is not None and candle.equals(last_candle):
                        continue
                    last_candle = candle

                    time = candle['time']
                    open = candle['open']
                    high = candle['high']
                    low = candle['low']
                    close = candle['close']
                    volume = candle['volume']

                    TimeProvider.instance.set_time(time)
                    self.callback(self.symbol, time, open, high, low, close, volume)

                cursor = time + (self.min_tf_mp * 60 * step)

            log_event('Backtest process has been finished.')
            print('A backtest folyamat befejeződött.')
        except Exception as e:
            self.on_error(e)

    def on_error(self, error):
        traceback_string = ''.join(traceback.format_exception(type(error), error, error.__traceback__))
        log_event("Ws exception.", traceback_string)