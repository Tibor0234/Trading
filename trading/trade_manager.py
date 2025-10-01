from abc import ABC, abstractmethod
from data.log_handler import log_event

class TradeManager(ABC):
    def __init__(self, trade_service, account_manager):
        self.ongoing_trades = []

        self.trade_service = trade_service
        self.account_manager = account_manager

    def set_trade_values(self, trade):
        return self.account_manager.set_trade_value(trade)

    def add_ongoing_trade(self, trade):
        if self.is_trade_invalid_abstract(trade):
            return False
        self.ongoing_trades.append(trade)
        html_path = self.trade_service.on_trade_event(trade)
        self.place_market_order_abstract(trade)
        log_event('A trade has been opened.', ' ' + html_path)
        return True

    def set_stop_loss(self, trade, sl):
        for open_trade in self.ongoing_trades:
            if open_trade == trade:
                open_trade.set_sl(sl)
                break

    def set_take_profit(self, trade, tp):
        for open_trade in self.ongoing_trades:
            if open_trade == trade:
                open_trade.set_tp(tp)
                break

    def add_value(self, trade, value):
        for open_trade in self.ongoing_trades:
            if open_trade == trade:
                open_trade.value += value
                break

    def close_trade(self, trade, price):
        for open_trade in self.ongoing_trades:
            if open_trade == trade:
                open_trade.close_trade(price)
                self._finalize_trade(open_trade)
                break

    def _update_trades_with_condition(self, condition_func):
        trades_to_remove = [t for t in self.ongoing_trades if condition_func(t)]

        for trade in trades_to_remove:
            self._finalize_trade(trade)
    
    def _finalize_trade(self, trade):
        self.ongoing_trades.remove(trade)
        html_path = self.trade_service.on_trade_event(trade)
        log_event('A trade has been closed.', ' ' + html_path)
        if trade.approved:
            result = self.account_manager.update_account_balance(trade)
            self.trade_service.on_trade_close(trade, result)
            self.close_position_abstract(trade)

    @abstractmethod
    def is_trade_invalid_abstract(self, trade):
        pass

    @abstractmethod
    def place_market_order_abstract(self, trade):
        pass

    @abstractmethod
    def close_position_abstract(self, trade):
        pass

class TradeManagerLive(TradeManager):
    def __init__(self, trade_service, account_manager, trading_client):
        super().__init__(trade_service, account_manager)
        self.trading_client = trading_client

    def is_trade_invalid_abstract(self, trade):
        return not trade.approved or any(t.symbol == trade.symbol for t in self.ongoing_trades)
    
    def place_market_order_abstract(self, trade):
        self.trading_client.open_market_order(trade)
    
    def close_position_abstract(self, trade):
        self.trading_client.close_position(trade)

    def update_ongoing_trades(self, sym, price):
        self._update_trades_with_condition(lambda t: t.symbol == sym and t.is_closed(price))

    def update_ongoing_trades_on_restore(self, sym, tf, cache_df):
        def condition(t):
            if t.symbol != sym or t.timeframe != tf:
                return False
            candles = cache_df[cache_df['time'] >= t.open_time]
            if candles.empty:
                return False
            high = max(candles['high'])
            low = min(candles['low'])
            return t.is_closed(high, low)
        self._update_trades_with_condition(condition)

class TradeManagerBacktest(TradeManager):
    def is_trade_invalid_abstract(self, trade):
        return False
    
    def place_market_order_abstract(self, trade):
        return
    
    def close_position_abstract(self, trade):
        return

    def update_ongoing_trades(self, sym, tf, cache_df):
        def condition(t):
            if t.symbol != sym or t.timeframe != tf:
                return False
            last_high = cache_df['high'].iloc[-1]
            last_low = cache_df['low'].iloc[-1]
            return t.is_closed(last_high, last_low)
        self._update_trades_with_condition(condition)