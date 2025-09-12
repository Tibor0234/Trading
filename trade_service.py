from abc import ABC
import asyncio

class TradeService(ABC):
    def __init__(self):
        self.strategies = []

    def set_dependencies(self, engine, trade_manager, discord_bot):
        self.engine = engine
        self.trade_manager = trade_manager
        self.discord_bot = discord_bot

    def add_strategy(self, strategy):
        self.strategies.append(strategy)

    #for strategy framework
    def get_timeframes(self):
        return self.engine.timeframe_handler.timeframes
    
    #for strategy framework
    def get_ongoing_trades(self):
        return self.trade_manager.ongoing_trades
    
    #for strategy framework
    def get_account_manager(self):
        return self.trade_manager.account_manager

    #engine -> strategy
    def on_ws_message(self, sym):
        for strategy in self.strategies:
            strategy.on_ws_message(sym)

    #engine -> strategy
    def on_candle_close(self, sym, tf):
        for strategy in self.strategies:
            strategy.on_candle_close(sym, tf)

    #engine -> strategy
    def on_candles_restored(self, sym, tf):
        for strategy in self.strategies:
            strategy.on_candles_restored(sym, tf)

    #strategy -> trade_manager
    def on_trade_open(self, trade):
        self.trade_manager.add_ongoing_trade(trade)

    #strategy -> trade_manager
    def on_set_stop_loss(self, trade, sl):
        self.trade_manager.set_stop_loss(trade, sl)

    #strategy -> trade_manager
    def on_set_take_profit(self, trade, tp):
        self.trade_manager.set_take_profit(trade, tp)

    #strategy -> trade_manager
    def on_add_value(self, trade, value):
        self.trade_manager.add_value(trade, value)
    
    #strategy -> trade_manager
    def on_trade_close(self, trade, price):
        self.trade_manager.close_trade(trade, price)

    #trade_manager -> engine
    def on_trade_event(self, trade):
        html_path = self.engine.visualize_from_trade(trade)
        self.send_discord_trade_setup(html_path, 60)

    def send_discord_trade_result(self, html_path):
        self.discord_bot.send_trade_result(html_path)

    def send_discord_trade_setup(self, html_path, timeout):
        asyncio.run_coroutine_threadsafe(
            self.discord_bot.send_setup_dm(html_path, timeout),
            self.discord_bot.bot.loop
        )

    #discord_bot ->
    def on_discord_reaction(self, is_approved):
        if is_approved: print('trade elfogadva')
        else: print('trade elutasítva')

class TradeServiceLive(TradeService):
    #engine -> trade_manager
    def on_update_trades(self, symbol, price):
        self.trade_manager.update_ongoing_trades(symbol, price)

    #engine -> trade_manager
    def on_update_trades_restore(self, symbol, timeframe, cache_df):
        self.trade_manager.update_ongoing_trades_on_restore(self, symbol, timeframe, cache_df)

class TradeServiceBacktest(TradeService):
    #engine -> trade_manager
    def on_update_trades(self, symbol, timeframe, cache_df):
        self.trade_manager.update_ongoing_trades(symbol, timeframe, cache_df)