import math
import time
import pandas as pd
import threading
from abc import ABC, abstractmethod
from utils import timeframes_and_multipliers, symbols, symbols_backtest, min_timeframe_backtest, max_timeframe_backtest
from config import db_path_live, db_path_backtest, ws_endpoint, discord_bot_token
from data.db_handler import Database
from data.time_provider import TimeProvider
from data.api_client import fetch_data_limit, fetch_data_limit_since

from engine import EngineLive, EngineBacktest
from data.timeframe_handler import TimeframeHandlerLive, TimeframeHandlerBacktest
from data.timeframe import TimeframeLive, TimeframeBacktest
from data.candle import CandleLive, CandleBacktest
from analyzer.analyzer import Analyzer
from analyzer.swing_analyzer import SwingAnalyzer
from analyzer.ema_analyzer import EmaAnalyzer
from analyzer.trend_analyzer import TrendAnalyzer
from analyzer.trendline_analyzer import TrendlineAnalyzer
from analyzer.order_zone_analyzer import OrderZoneAnalyzer
from visualizer.visualizer import Visualizer
from visualizer.session_visualizer import SessionVisualizer
from visualizer.candlestick_visualizer import CandlestickVisualizer
from visualizer.ema_visualizer import EmaVisualizer
from visualizer.swing_visualizer import SwingVisualizer
from visualizer.trade_visualizer import TradeVisualizer
from visualizer.trend_visualizer import TrendVisualizer
from visualizer.order_zone_visualizer import OrderZoneVisualizer
from visualizer.trendline_visualizer import TrendlineVisualizer
from trading.trade_manager import TradeManagerLive, TradeManagerBacktest
from trading.account_manager import AccountManager
from data.ws_client_live import WsClientLive
from data.ws_client_backtest import WsClientBacktest
from trade_service import TradeServiceLive, TradeServiceBacktest
from discord_bot.discord_bot import DiscordBot

class Factory(ABC):
    @staticmethod
    def calculate_tolerance(mp, min_tol, max_tol, min_mp = timeframes_and_multipliers.get('1m'), max_mp = timeframes_and_multipliers.get('1w')):
        b = math.log(max_tol / min_tol) / math.log(max_mp / min_mp)
        a = min_tol / (min_mp ** b)
        tolerance = a * (mp ** b)
        return tolerance
    
    @staticmethod
    def timeframes_dict_builder():
        timeframes_dict = {}
        for sym in symbols:
            timeframes_dict[sym] = {}
        return timeframes_dict
    
    def timeframe_handler_builder(self, params, callback_on_close, callback_on_restore):
        timeframes_dict = self.timeframes_dict_builder()

        min_timeframe_mp = timeframes_and_multipliers.get(min_timeframe_backtest)
        max_timeframe_mp = timeframes_and_multipliers.get(max_timeframe_backtest)
        for tf, mp in timeframes_and_multipliers.items():
            if self.invalid_timeframe_abstract(mp, min_timeframe_mp, max_timeframe_mp):
                continue

            for sym in symbols:
                if not self.valid_symbol_abstract(sym):
                    continue
                
                timestamp = mp * 60

                #Adatok beolvasása
                historical_df = self.get_historical_data_abstract(sym, tf, 400, timestamp, start_time=params['bt_start_time'])

                candle_df = historical_df.iloc[[-1]]
                candles_to_save = historical_df.iloc[:-1]
                candles_to_cache = candles_to_save.tail(399)

                self.save_to_database_abstract(candles_to_save, sym, tf)

                #Paméterek számolása
                if sym == symbols[0]:
                    tolerance = self.calculate_tolerance(mp, params['btc_tolerance_min'], params['btc_tolerance_max'])
                elif sym == symbols[1]:
                    tolerance = self.calculate_tolerance(mp, params['eth_tolerance_min'], params['eth_tolerance_max'])
                trendline_tolerance = tolerance * params['trendline_tolerance_mp']
                order_zone_tolerance = tolerance * params['order_zone_tolerance_mp']
                                
                #Timeframe objektum függőségei
                swing_analyzer = SwingAnalyzer()
                trendline_analyzer = TrendlineAnalyzer(tolerance=trendline_tolerance, timestamp=timestamp)
                order_zone_analyzer = OrderZoneAnalyzer(tolerance=order_zone_tolerance)
                trend_analyzer = TrendAnalyzer()
                ema_analyzer = EmaAnalyzer()
                analyzer = Analyzer(swing_analyzer=swing_analyzer,
                                    trendline_analyzer=trendline_analyzer,
                                    order_zone_analyzer=order_zone_analyzer,
                                    trend_analyzer=trend_analyzer,
                                    ema_analyzer=ema_analyzer
                                    )

                candle = self.create_candle_abstract(candle_df)
                timeframe = self.create_timeframe_abstract(sym, tf, timestamp, candle, candles_to_cache, callback_on_close, callback_on_restore, analyzer)

                timeframes_dict[sym][tf] = timeframe

        return timeframes_dict
        
    def program_builder(self, factory_params):
        trade_service = self.create_trade_service_abstract()

        self.create_time_provider_abstract(factory_params['bt_start_time'])

        #Visualizer
        candlestick_visualizer = CandlestickVisualizer()
        trade_visualizer = TradeVisualizer()
        swing_visualizer = SwingVisualizer()
        trendline_visualizer = TrendlineVisualizer()
        order_zone_visualizer = OrderZoneVisualizer()
        trend_visualizer = TrendVisualizer()
        ema_visualizer = EmaVisualizer()
        session_visualizer = SessionVisualizer()

        visualizer = Visualizer(candlestick_visualizer=candlestick_visualizer,
                                trade_visualizer=trade_visualizer,
                                swing_visualizer=swing_visualizer,
                                trendline_visualizer=trendline_visualizer,
                                order_zone_visualizer = order_zone_visualizer,
                                trend_visualizer=trend_visualizer,
                                ema_visualizer=ema_visualizer,
                                session_visualizer=session_visualizer
                                )

        engine = self.create_engine_abstract(trade_service, visualizer)
        self.create_database_abstract()
        
        #Timeframe handler
        tf_callback_on_close = engine.on_candle_close
        tf_callback_on_restore = engine.on_restore
        timeframes_dict = self.timeframe_handler_builder(factory_params, tf_callback_on_close, tf_callback_on_restore)
        timeframe_handler = self.create_timeframe_handler_abstract(timeframes_dict)

        engine.set_dependencies(timeframe_handler)
        
        #Trade manager
        account_manager = AccountManager(factory_params['bt_account_balance'])
        trade_manager = self.create_trade_manager_abstract(trade_service, account_manager)

        #Websocket
        ws_callback_func = engine.ws_message_handler
        websocket_client = self.create_websocket_client_abstract(ws_callback_func)

        #Discord bot
        discord_bot = DiscordBot(discord_bot_token, trade_service.on_discord_reaction)
        discord_thread = threading.Thread(target=discord_bot.run_bot, daemon=True)
        discord_thread.start()

        trade_service.set_dependencies(engine, trade_manager, discord_bot)

        return trade_service, websocket_client

    @abstractmethod
    def invalid_timeframe_abstract(self, mp, min_timeframe_mp, max_timeframe_mp):
        pass

    @abstractmethod
    def create_trade_service_abstract(self):
        pass

    @abstractmethod
    def create_time_provider_abstract(self, ts):
        pass

    @abstractmethod
    def create_database_abstract(self):
        pass

    @abstractmethod
    def create_candle_abstract(self, candle_df):
        pass

    @abstractmethod
    def get_historical_data_abstract(self, sym, tf, limit, ts, start_time):
        pass
    
    @abstractmethod
    def create_websocket_client_abstract(self, callback):
        pass
    
    @abstractmethod
    def create_engine_abstract(self, trade_service, visualizer):
        pass
    
    @abstractmethod
    def create_timeframe_handler_abstract(self, timeframes_dict):
        pass
    
    @abstractmethod
    def create_timeframe_abstract(self, sym, tf, timestamp, candle, candles_to_cache, callback_on_close, callback_on_restore, analyzer):
        pass
    
    @abstractmethod
    def create_trade_manager_abstract(self, trade_service, account_manager):
        pass
    
    @abstractmethod
    def valid_symbol_abstract(self, sym):
        pass
    
    @abstractmethod
    def save_to_database_abstract(self, candles_to_save, sym, tf):
        pass

class FactoryLive(Factory):
    def invalid_timeframe_abstract(self, mp, min_timeframe_mp, max_timeframe_mp):
        return False

    def create_trade_service_abstract(self):
        return TradeServiceLive()
    
    def create_time_provider_abstract(self, ts):
        return TimeProvider.init_time_provider(int(time.time()))

    def create_database_abstract(self):
        return Database.init_database(db_path_live)

    def create_candle_abstract(self, candle_df):
        return CandleLive(candle_df)
    
    def get_historical_data_abstract(self, sym, tf, limit, ts, start_time):
        df_now = fetch_data_limit(sym, tf, limit/2)

        since = df_now['time'].iloc[0] - (limit/2 * ts)
        df_since = fetch_data_limit_since(sym, tf, limit/2, since)

        df = pd.concat([df_since, df_now]).drop_duplicates(ignore_index=True)
        return df
    
    def create_websocket_client_abstract(self, callback):
        return WsClientLive(ws_endpoint, callback)
    
    def create_engine_abstract(self, trade_service, visualizer):
        return EngineLive(trade_service, visualizer)
    
    def create_timeframe_handler_abstract(self, timeframes_dict):
        return TimeframeHandlerLive(timeframes_dict)
    
    def create_timeframe_abstract(self, sym, tf, timestamp, candle, candles_to_cache, callback_on_close, callback_on_restore, analyzer):
        return TimeframeLive(sym, tf, timestamp, candle, candles_to_cache, callback_on_close, callback_on_restore, analyzer)
    
    def create_trade_manager_abstract(self, trade_service, account_manager):
        return TradeManagerLive(trade_service, account_manager)
    
    def valid_symbol_abstract(self, sym):
        return True
    
    def save_to_database_abstract(self, candles_to_save, sym, tf):
        Database.instance.save_to_db_replace(candles_to_save, sym, tf)
    
class FactoryBacktest(Factory):
    def invalid_timeframe_abstract(self, mp, min_timeframe_mp, max_timeframe_mp):
        return (min_timeframe_mp is not None and mp < min_timeframe_mp) or (max_timeframe_mp is not None and mp > max_timeframe_mp)

    def create_trade_service_abstract(self):
        return TradeServiceBacktest()
    
    def create_time_provider_abstract(self, ts):
        return TimeProvider.init_time_provider(ts)

    def create_database_abstract(self):
        return Database.init_database(db_path_backtest)

    def create_candle_abstract(self, candle_df):
        return CandleBacktest(candle_df)
    
    def get_historical_data_abstract(self, sym, tf, limit, ts, start_time):
        return Database.instance.read_from_db_limit_to(sym, tf, limit, start_time)
    
    def create_websocket_client_abstract(self, callback):
        return WsClientBacktest(symbols_backtest[0], callback)
    
    def create_engine_abstract(self, trade_service, visualizer):
        return EngineBacktest(trade_service, visualizer)
    
    def create_timeframe_handler_abstract(self, timeframes_dict):
        return TimeframeHandlerBacktest(timeframes_dict)
    
    def create_timeframe_abstract(self, sym, tf, timestamp, candle, candles_to_cache, callback_on_close, callback_on_restore, analyzer):
        return TimeframeBacktest(sym, tf, timestamp, candle, candles_to_cache, callback_on_close, callback_on_restore, analyzer)
    
    def create_trade_manager_abstract(self, trade_service, account_manager):
        return TradeManagerBacktest(trade_service, account_manager)
    
    def valid_symbol_abstract(self, sym):
        return sym in symbols_backtest
    
    def save_to_database_abstract(self, candles_to_save, sym, tf):
        pass