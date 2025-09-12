from strategies.strategy import Strategy

class TrendlineStrategy(Strategy):
    def __init__(self):
        super().__init__()
        self.swing_lows = {}
        self.swing_highs = {}
        self.support_trendlines = {}
        self.resistance_trendlines = {}

    def on_candle_close(self, sym, tf):
        candles_df = self.fw.get_candles_df(sym, tf)
        sec_last_candle = candles_df.iloc[-2]
        last_candle = candles_df.iloc[-1]
        if self.swing_lows.get(tf) is None or (self.fw.is_candle_bearish(sec_last_candle) and self.fw.is_candle_bullish(last_candle)):
            self.swing_lows[tf] = self.fw.get_swing_lows(sym, tf, candles_df)
            lows_3sl = self.fw.filter_swings(self.swing_lows[tf], min_sl=3)
            self.support_trendlines[tf] = self.fw.get_support_trendlines(sym, tf, lows_3sl)
        if self.swing_highs.get(tf) is None or (self.fw.is_candle_bullish(sec_last_candle) and self.fw.is_candle_bearish(last_candle)):
            self.swing_highs[tf] = self.fw.get_swing_highs(sym, tf, candles_df)
            highs_3sl = self.fw.filter_swings(self.swing_highs[tf], min_sl=3)
            self.resistance_trendlines[tf] = self.fw.get_resistance_trendlines(sym, tf, highs_3sl)
        
        if not self.fw.is_trade_open(sym, strategy=self):
            self.open_long(sym, tf)
            self.open_short(sym, tf)
        if self.fw.is_trade_open(sym, strategy=self):
            self.manage_long(sym, tf)
            self.manage_short(sym, tf)
    
    def open_long(self, sym, tf):
        trendline = self.fw.filter_trendlines(self.resistance_trendlines[tf], pos=-1)
        if trendline is None or trendline.touchpoints < 2 or trendline.slope < 13: return
        last_candle = self.fw.get_last_closed_candle(sym, tf)
        trendline_value = self.fw.get_trendline_value_at(trendline, last_candle['time'])
        unit = self.fw.get_trendline_unit_at(sym, tf, last_candle['close'])
        if last_candle['close'] > trendline_value + (3*unit):
            trade = self.fw.create_trade(
                symbol=sym,
                timeframe=tf,
                direction=1,
                strategy=self,
                risk_pct=2,
                entry_price=last_candle['close'],
                stop_loss=trendline_value - (5*unit),
                details={'resistance_trendlines_visual': [trendline]}
            )
            self.open_trade(trade)

    def manage_long(self, sym, tf):
        trades = self.fw.get_open_trades(sym, tf, strategy=self)
        if not trades: return
        trade = trades[0]
        if trade.direction != 1: return

        trendline = self.fw.filter_trendlines(self.support_trendlines[tf], pos=-1)
        if trendline is None: return
        last_candle = self.fw.get_last_closed_candle(sym, tf)
        unit = self.fw.get_trendline_unit_at(sym, tf, last_candle['close'])
        trendline_value = self.fw.get_trendline_value_at(trendline, last_candle['time'])
        trade.details['support_trendlines_visual'] = [trendline]
        self.set_stop_loss(trade, trendline_value - (3*unit))

    def open_short(self, sym, tf):
        trendline = self.fw.filter_trendlines(self.support_trendlines[tf], pos=-1)
        if trendline is None or trendline.touchpoints < 3 or trendline.slope < 13: return
        last_candle = self.fw.get_last_closed_candle(sym, tf)
        trendline_value = self.fw.get_trendline_value_at(trendline, last_candle['time'])
        unit = self.fw.get_trendline_unit_at(sym, tf, last_candle['close'])
        if last_candle['close'] < trendline_value - (3*unit):
            trade = self.fw.create_trade(
                symbol=sym,
                timeframe=tf,
                direction=-1,
                strategy=self,
                risk_pct=2,
                entry_price=last_candle['close'],
                stop_loss=trendline_value + (5*unit),
                details={'support_trendlines_visual': [trendline]}
            )
            self.open_trade(trade)

    def manage_short(self, sym, tf):
        trades = self.fw.get_open_trades(sym, tf, strategy=self)
        if not trades: return
        trade = trades[0]
        if trade.direction != -1: return

        trendline = self.fw.filter_trendlines(self.resistance_trendlines[tf], pos=-1)
        if trendline is None: return
        last_candle = self.fw.get_last_closed_candle(sym, tf)
        unit = self.fw.get_trendline_unit_at(sym, tf, last_candle['close'])
        trendline_value = self.fw.get_trendline_value_at(trendline, last_candle['time'])
        trade.details['resistance_trendlines_visual'] = [trendline]
        self.set_stop_loss(trade, trendline_value + (3*unit))
    
    def on_candles_restored(self, sym, tf):
        pass

    def on_ws_message(self, sym):
        pass