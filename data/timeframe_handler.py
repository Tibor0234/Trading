from abc import ABC

class TimeframeHandler(ABC):
    def __init__(self, timeframes_dict):
        self.timeframes = timeframes_dict

class TimeframeHandlerLive(TimeframeHandler):
    def update_timeframes(self, symbol, time, price, size):
        symbol_timeframes = self.timeframes.get(symbol)
        
        #standard update
        for tf, timeframe in symbol_timeframes.items():
            timeframe.candle.update_candle(time, price, size)

        #adatvesztés ellenőrzés
        if symbol_timeframes['1m'].is_data_lost():
            for tf, timeframe in symbol_timeframes.items():
                timeframe.restore_data()

        #gyertya zárás
        for tf, timeframe in symbol_timeframes.items():
            if timeframe.is_candle_closed():
                timeframe.close_candle()

class TimeframeHandlerBacktest(TimeframeHandler):
    def update_timeframes(self, symbol, time, open, high, low, close, volume):
        symbol_timeframes = self.timeframes.get(symbol)

        #standard update
        for tf, timeframe in symbol_timeframes.items():
            timeframe.candle.update_candle(time, open, high, low, close, volume)

        #gyertya zárás
        for tf, timeframe in symbol_timeframes.items():
            if timeframe.is_candle_closed():
                timeframe.close_candle()