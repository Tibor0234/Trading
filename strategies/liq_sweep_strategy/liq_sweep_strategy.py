from strategies.strategy import Strategy

class LiqSweepStrategy(Strategy):
    def __init__(self):
        super().__init__()
        self.swing_lows = {}
        self.swing_highs = {}
        self.demand_zones = {}
        self.supply_zones = {}

    def on_candle_close(self, sym, tf):
        if self.fw.is_trade_open(sym, strategy=self):
            return
            trade = self.fw.get_open_trades(sym, strategy=self)[0]
            if trade.stop_loss == trade.entry_price: return
            last_candle = self.fw.get_last_closed_candle(sym, tf)
            if abs(last_candle['close'] - trade.entry_price) >= abs(trade.entry_price - trade.stop_loss):
                self.set_stop_loss(trade, trade.entry_price)
            return

        candles_df = self.fw.get_candles_df(sym, tf)[:-2]
        sec_last_candle = candles_df.iloc[-2]
        last_candle = candles_df.iloc[-1]
        if self.swing_lows.get(tf) is None or (self.fw.is_candle_bearish(sec_last_candle) and self.fw.is_candle_bullish(last_candle)):
            self.swing_lows[tf] = self.fw.get_swing_lows(sym, tf, candles_df)
            lows_4sl = self.fw.filter_swings(self.swing_lows[tf], min_sl=4)
            self.demand_zones[tf] = self.fw.get_demand_zones(sym, tf, lows_4sl)
        if self.swing_highs.get(tf) is None or (self.fw.is_candle_bullish(sec_last_candle) and self.fw.is_candle_bearish(last_candle)):
            self.swing_highs[tf] = self.fw.get_swing_highs(sym, tf, candles_df)
            highs_4sl = self.fw.filter_swings(self.swing_highs[tf], min_sl=4)
            self.supply_zones[tf] = self.fw.get_supply_zones(sym, tf, highs_4sl)

        self.from_equal_highs(sym, tf)
        self.from_equal_lows(sym, tf)

    def from_equal_highs(self, sym, tf):
        last_candle = self.fw.get_last_closed_candle(sym, tf)
        unit = self.fw.get_order_zone_unit_at(sym, tf, last_candle['close'])
        if not self.fw.is_candle_bearish(last_candle): return
        sec_last_candle = self.fw.get_candles_df(sym, tf, pos=-2)
        valid_supply_zones = [z for z in self.supply_zones[tf] if sec_last_candle['open'] < self.fw.get_order_zone_prec_high(z) and
                                                        sec_last_candle['close'] < self.fw.get_order_zone_prec_high(z) and
                                                        sec_last_candle['high'] > z.zone_high]
        if not valid_supply_zones: return
        zone = valid_supply_zones[0]
        unit = self.fw.get_order_zone_unit_at(sym, tf, zone.zone_high)
        trade = self.fw.create_trade(
            symbol=sym,
            timeframe=tf,
            direction=-1,
            strategy=self,
            risk_pct=2,
            entry_price=last_candle['close'],
            stop_loss=zone.zone_high + (2*unit),
            risk_reward=1.5,
            details={'supply_zones_visual': [zone]}
        )
        self.open_trade(trade)

    def from_equal_lows(self, sym, tf):
        last_candle = self.fw.get_last_closed_candle(sym, tf)
        unit = self.fw.get_order_zone_unit_at(sym, tf, last_candle['close'])
        if not self.fw.is_candle_bullish(last_candle): return
        sec_last_candle = self.fw.get_candles_df(sym, tf, pos=-2)
        valid_demand_zones = [z for z in self.demand_zones[tf] if sec_last_candle['open'] > self.fw.get_order_zone_prec_low(z)
                                                        and sec_last_candle['close'] > self.fw.get_order_zone_prec_low(z)
                                                        and sec_last_candle['low'] < z.zone_low]
        if not valid_demand_zones: return
        zone = valid_demand_zones[0]
        trade = self.fw.create_trade(
            symbol=sym,
            timeframe=tf,
            direction=1,
            strategy=self,
            risk_pct=2,
            entry_price=last_candle['close'],
            stop_loss=zone.zone_low - (2 * unit),
            risk_reward=1.5,
            details={'demand_zones_visual': [zone]}
        )
        self.open_trade(trade)

    def from_liq_pools(self, sym, tf):
        if self.fw.is_trade_open(sym, strategy=self): return
        candles_df = self.fw.get_candles_df(sym, tf)
        candles_before = candles_df[:-1]
        highs = self.fw.get_swing_highs(sym, tf, candles_before)
        highs_4sl = self.fw.filter_swings(highs, min_sl=4)
        liq_highs = self.fw.get_high_liquidity_pools(highs_4sl).iloc[:-1]
        last_candle = self.fw.get_last_closed_candle(sym, tf)
        valid_liq_highs = liq_highs[
            (last_candle['close'] < liq_highs['high']) &
            (last_candle['open'] < liq_highs['high']) &
            (last_candle['high'] > liq_highs['high'])]
        if valid_liq_highs.empty or len(valid_liq_highs) > 1: return
        liq_high = valid_liq_highs.iloc[0]
        unit = self.fw.get_order_zone_unit_at(sym, tf, liq_high['high'])
        trade = self.fw.create_trade(
            symbol=sym,
            timeframe=tf,
            direction=-1,
            strategy=self,
            risk_pct=2,
            entry_price=last_candle['close'],
            stop_loss=liq_high['high'] + (2*unit),
            risk_reward=1.5,
            details={'swing_highs_visual': liq_highs}
        )
        self.open_trade(trade)

    def on_candles_restored(self, sym, tf):
        pass

    def on_ws_message(self, sym):
        pass