from abc import ABC, abstractmethod
from strategies.strategy_framework import StrategyFramework

class Strategy(ABC):
    def init_strategy(self, trade_service, framework : StrategyFramework):
        self.trade_service = trade_service
        self.fw = framework
    
    #from engine
    @abstractmethod
    def on_candle_close(self, sym, tf):
        pass

    @abstractmethod
    def on_candles_restored(self, sym, tf):
        pass

    @abstractmethod
    def on_ws_message(self, sym):
        pass

    #to trade manager
    def open_trade(self, trade, check = False):
        self.trade_service.on_trade_open(trade)

    def set_stop_loss(self, trade, sl):
        self.trade_service.on_set_stop_loss(trade, sl)

    def set_take_profit(self, trade, tp):
        self.trade_service.on_set_take_profit(trade, tp)

    def add_value(self, trade, value):
        self.trade_service.on_add_value(trade, value)
    
    def close_trade(self, trade, price):
        self.trade_service.on_trade_close(trade, price)