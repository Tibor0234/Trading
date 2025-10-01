from abc import ABC
from datetime import datetime, timezone, time as dtime
from zoneinfo import ZoneInfo
from trading.trade import Trade
import pandas as pd

class StrategyFramework(ABC):
    def __init__(self, trade_service):
        self.timeframes = trade_service.get_timeframes()
        self.ongoing_trades = trade_service.get_ongoing_trades()
        self.account_manager = trade_service.get_account_manager()

    #trade manager methods
    def create_trade(self, timeframe_obj, direction, strategy, risk_pct, entry_price,
                stop_loss, take_profit = None, risk_reward = None, details = {}):
        return Trade(
            timeframe_obj=timeframe_obj,
            direction=direction,
            strategy=strategy,
            risk_pct=risk_pct,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            risk_reward=risk_reward,
            details=details
        )

    def is_trade_open(self, sym = None, tf = None, strategy = None, direction = None):
        return any(
        (sym is None or trade.symbol == sym) and
        (tf is None or trade.timeframe == tf) and
        (direction is None or trade.direction == direction) and
        (strategy is None or trade.strategy == strategy)
        for trade in self.ongoing_trades
    )
    
    def get_open_trades(self, sym = None, tf = None, strategy = None, direction = None):
        return [
        trade for trade in self.ongoing_trades
        if (sym is None or trade.symbol == sym) and
           (tf is None or trade.timeframe == tf) and
           (direction is None or trade.direction == direction) and
           (strategy is None or trade.strategy == strategy)
    ]
    
    #account manager methods
    def withdraw(self, amount):
        self.account_manager.withdraw(amount)

    def get_account_balance(self):
        return self.account_manager.get_account_balance()

    #timeframe and candle methods
    def get_timeframe_obj(self, sym, tf):
        return self.timeframes[sym][tf]

    def get_candles_df(self, sym, tf, since=None, to=None, pos=None):
        df = self.timeframes[sym][tf].cache_df
        df = df[df['time'] >= since] if since is not None else df
        df = df[df['time'] <= to] if to is not None else df
        try: return df.iloc[pos] if pos is not None else df
        except: return None
    
    def get_candles_df_with_open_candle(self, sym, tf, since=None):
        return pd.concat([self.get_candles_df(sym, tf, since), self.timeframes[sym][tf].candle.convert_to_df()], ignore_index=True)

    def get_last_closed_candle(self, sym, tf):
        return self.get_candles_df(sym, tf, pos=-1)
    
    def get_open_candle(self, sym, tf):
        return self.timeframes[sym][tf].candle.convert_to_series()
    
    def get_current_price(self, sym, tf):
        return self.timeframes[sym][tf].candle.close
    
    def is_all_candles_bullish(self, candles):
        return (candles['close'] > candles['open']).all()
    
    def is_all_candles_bearish(self, candles):
        return (candles['open'] > candles['close']).all()
    
    def is_candle_bullish(self, candle):
        return self.is_all_candles_bullish(candle)
    
    def is_candle_bearish(self, candle):
        return self.is_all_candles_bearish(candle)
    
    def get_higher_timeframes(self, sym, tf):
        return [t.timeframe for t in sorted(
            (t for t in self.timeframes[sym].values()
            if t.timestamp > self.timeframes[sym][tf].timestamp),
            key=lambda x: x.timestamp)]
    
    def get_higher_timeframe(self, sym, tf):
        higher_timeframes = self.get_higher_timeframes(sym, tf)
        return higher_timeframes[0] if higher_timeframes else None

    #indicators
    def get_ema(self, sym, tf, length, candles_df, pos=None):
        ema_obj = self.timeframes[sym][tf].analyzer.ema_analyzer.get_ema(length, candles_df)
        try: return ema_obj.values[pos] if pos is not None else ema_obj.values
        except IndexError: return None

    #structures
    def get_swing_lows(self, sym, tf, candles_df):
        return self.timeframes[sym][tf].analyzer.swing_analyzer.get_swing_lows(candles_df)
    
    def get_swing_highs(self, sym, tf, candles_df):
        return self.timeframes[sym][tf].analyzer.swing_analyzer.get_swing_highs(candles_df)
    
    def get_support_trendlines(self, sym, tf, swing_lows):
        return self.timeframes[sym][tf].analyzer.trendline_analyzer.get_support_trendlines(swing_lows)
    
    def get_resistance_trendlines(self, sym, tf, swing_highs):
        return self.timeframes[sym][tf].analyzer.trendline_analyzer.get_resistance_trendlines(swing_highs)
    
    def get_demand_zones(self, sym, tf, swing_lows):
        return self.timeframes[sym][tf].analyzer.order_zone_analyzer.get_demand_zones(swing_lows)
    
    def get_supply_zones(self, sym, tf, swing_highs):
        return self.timeframes[sym][tf].analyzer.order_zone_analyzer.get_supply_zones(swing_highs)
    
    def get_current_trend(self, sym, tf, swing_lows, swing_highs):
        return self.timeframes[sym][tf].analyzer.trend_analyzer.get_current_trend(swing_lows, swing_highs)
    
    #structure filters
    def filter_swings(self, swings, min_sl=None, max_sl=None, pos=None):
        swings = swings[swings['swing_length'] >= min_sl] if min_sl is not None else swings
        swings = swings[swings['swing_length'] <= max_sl] if max_sl is not None else swings
        try: return swings.iloc[pos] if pos is not None else swings
        except IndexError: return None

    def filter_trendlines(self, trendlines, min_tp=None, max_tp=None, min_sp=None, max_sp=None, pos=None):
        trendlines = [t for t in trendlines if (min_tp is None or t.touchpoints >= min_tp) and (max_tp is None or t.touchpoints <= max_tp)
                    and (min_sp is None or t.slope >= min_sp) and (max_sp is None or t.slope <= max_sp)]
        try: return trendlines[pos] if pos is not None else trendlines
        except IndexError: return None

    def filter_order_zones(self, order_zones, min_tp=None, max_tp=None, pos=None):
        zones = [z for z in order_zones if (min_tp is None or z.touchpoints >= min_tp) and (max_tp is None or z.touchpoints <= max_tp)]
        try: return zones[pos] if pos is not None else zones
        except IndexError: return None

    def is_uptrend(self, current_trend):
        return current_trend.direction == 1
    
    def is_downtrend(self, current_trend):
        return current_trend.direction == -1
    
    #swing methods
    def get_high_liquidity_pools(self, swing_highs):
        filtered, max_high = [], None
        for i in range(len(swing_highs)-1, -1, -1):
            if max_high is None or swing_highs.iloc[i]['high'] > max_high:
                filtered.append(swing_highs.iloc[i])
                max_high = swing_highs.iloc[i]['high']
        return pd.DataFrame(filtered[::-1])

    def get_low_liquidity_pools(self, swing_lows):
        filtered, min_low = [], None
        for i in range(len(swing_lows)-1, -1, -1):
            if min_low is None or swing_lows.iloc[i]['low'] < min_low:
                filtered.append(swing_lows.iloc[i])
                min_low = swing_lows.iloc[i]['low']
        return pd.DataFrame(filtered.reverse())

    #trendline methods
    def get_trendline_unit_at(self, sym, tf, price):
        tolerance = self.timeframes[sym][tf].analyzer.trendline_analyzer.tolerance
        tol_high = price * (1 + tolerance)
        return (tol_high - price)
    
    def get_trendline_value_at(self, trendline, time):
        return trendline.get_y_on_line(time)
    
    def get_trendline_tolerance_low(self, trendline, price):
        return trendline.get_tolerance_low(price)
    
    def get_trendline_tolerance_high(self, trendline, price):
        return trendline.get_tolerance_high(price)

    #order zone methods
    def get_order_zone_unit_at(self, sym, tf, price):
        tolerance = self.timeframes[sym][tf].analyzer.order_zone_analyzer.tolerance
        tol_high = price * (1 + tolerance)
        return (tol_high - price)
    
    def get_order_zone_prec_low(self, order_zone):
        return order_zone.get_zone_low_prec()

    def get_order_zone_prec_high(self, order_zone):
        return order_zone.get_zone_high_prec()

    #time filters
    def get_hour_from_ts(self, time):
        return datetime.fromtimestamp(time, tz=timezone.utc).hour
    
    def get_minute_from_ts(self, time):
        return datetime.fromtimestamp(time, tz=timezone.utc).minute
    
    def is_weekday(self, time):
        dt = datetime.fromtimestamp(time, tz=timezone.utc)
        return dt.isoweekday() < 6
    
    #session filters
    def is_new_york_open(self, ts):
        dt_utc = datetime.fromtimestamp(ts, tz=ZoneInfo("UTC"))
        ny_time = dt_utc.astimezone(ZoneInfo("America/New_York"))
        session_start = dtime(9, 30)
        session_end = dtime(16, 0)
        return session_start <= ny_time.time() <= session_end and ny_time.isoweekday() < 6

    def is_london_open(self, ts):
        dt_utc = datetime.fromtimestamp(ts, tz=ZoneInfo("UTC"))
        london_time = dt_utc.astimezone(ZoneInfo("Europe/London"))
        session_start = dtime(8, 0)
        session_end = dtime(16, 30)
        return session_start <= london_time.time() <= session_end and london_time.isoweekday() < 6

    def is_tokyo_open(self, ts):
        dt_utc = datetime.fromtimestamp(ts, tz=ZoneInfo("UTC"))
        tokyo_time = dt_utc.astimezone(ZoneInfo("Asia/Tokyo"))
        session_start = dtime(9, 0)
        session_end = dtime(15, 0)
        return session_start <= tokyo_time.time() <= session_end and tokyo_time.isoweekday() < 6
    
    #session opens
    def get_new_york_open(self, ts):
        ny_time = datetime.fromtimestamp(ts, tz=ZoneInfo("America/New_York"))
        session_start = dtime(9, 30)
        return datetime.combine(ny_time.date(), session_start, tzinfo=ZoneInfo("America/New_York")).timestamp()

    def get_london_open(self, ts):
        london_time = datetime.fromtimestamp(ts, tz=ZoneInfo("Europe/London"))
        session_start = dtime(8, 0)
        return datetime.combine(london_time.date(), session_start, tzinfo=ZoneInfo("Europe/London")).timestamp()

    def get_tokyo_open(self, ts):
        tokyo_time = datetime.fromtimestamp(ts, tz=ZoneInfo("Asia/Tokyo"))
        session_start = dtime(9, 0)
        return datetime.combine(tokyo_time.date(), session_start, tzinfo=ZoneInfo("Asia/Tokyo")).timestamp()