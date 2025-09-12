from abc import ABC, abstractmethod

class Engine(ABC):
    def __init__(self, trade_service, visualizer):
        self.visualizer = visualizer
        self.trade_service = trade_service

    def set_dependencies(self, timeframe_handler):
        self.timeframe_handler = timeframe_handler

    def on_candle_close(self, sym, tf, cache_df):
        timeframe = self.timeframe_handler.timeframes[sym][tf]
        self.update_on_candle_close_abstract(sym, tf, cache_df)

        self.trade_service.on_candle_close(sym, tf)

    def on_restore(self, sym, tf, cache_df):
        timeframe = self.timeframe_handler.timeframes[sym][tf]

        self.trade_service.on_update_trades_restore(sym, tf, cache_df)
        self.trade_service.on_candles_restored(sym, tf)

    def visualize_from_input(self, sym, tf):
        if sym in self.timeframe_handler.timeframes.keys():
            symbol_key = sym
        else:
            complete_symbol = f'{sym.upper()}/USDT:USDT'
            if complete_symbol in self.timeframe_handler.timeframes.keys():
                symbol_key = complete_symbol
            else:
                print('Nincs ilyen symbol.')
                return
        if tf not in self.timeframe_handler.timeframes[symbol_key].keys():
            print('Nincs ilyen timeframe.')
            return

        timeframe = self.timeframe_handler.timeframes[symbol_key][tf]
        self.visualizer.visualize_from_input(timeframe)

    def visualize_from_trade(self, trade):
        self.visualizer.visualize_from_trade(trade)

    @abstractmethod
    def update_on_candle_close_abstract(self, sym, tf, cache_df):
        pass

class EngineLive(Engine):
    def ws_message_handler(self, symbol, time, price, size):
        self.timeframe_handler.update_timeframes(symbol, time, price, size)
        self.trade_service.on_update_trades(symbol, price)
        self.trade_service.on_ws_message(symbol)

    def update_on_candle_close_abstract(self, sym, tf, cache_df):
        pass

class EngineBacktest(Engine):
    def ws_message_handler(self, symbol, time, open, high, low, close, volume):
        self.timeframe_handler.update_timeframes(symbol, time, open, high, low, close, volume)
        self.trade_service.on_ws_message(symbol)

    def update_on_candle_close_abstract(self, sym, tf, cache_df):
        self.trade_service.on_update_trades(sym, tf, cache_df)