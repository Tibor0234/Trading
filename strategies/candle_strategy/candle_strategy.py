from strategies.strategy import Strategy

class CandleStrategy(Strategy):
    def on_candle_close(self, sym, tf):
        if tf != '1m' or self.fw.is_trade_open(): return
        last_candle = self.fw.get_last_closed_candle(sym, tf)
        unit = self.fw.get_order_zone_unit_at(sym, tf, last_candle['close'])
        if self.fw.is_candle_bullish(last_candle):
            trade = self.fw.create_trade(
                timeframe_obj=self.fw.get_timeframe_obj(sym, tf),
                direction=1,
                strategy=self,
                risk_pct=1,
                entry_price=last_candle['close'],
                stop_loss=last_candle['close'] - (10 * unit),
                risk_reward=1
            )
        else:
            trade = self.fw.create_trade(
                timeframe_obj=self.fw.get_timeframe_obj(sym, tf),
                direction=-1,
                strategy=self,
                risk_pct=1,
                entry_price=last_candle['close'],
                stop_loss=last_candle['close'] + (10 * unit),
                risk_reward=1
            )
        self.open_trade(trade)
    
    def on_candles_restored(self, sym, tf):
        pass
    
    def on_ws_message(self, sym):
        pass