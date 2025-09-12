from strategies.strategy import Strategy
class WickStrategy(Strategy):
    def on_candle_close(self, sym, tf):
        candles_df = self.fw.get_candles_df(sym, tf)
        sec_last = candles_df.iloc[-2]
        last = candles_df.iloc[-1]
        unit = self.fw.get_order_zone_unit_at(sym, tf, last['close'])

        # --- Ha már van trade, menedzseljük ---
        if self.fw.is_trade_open(sym, strategy=self):
            trade = self.fw.get_open_trades(sym, strategy=self)[0]

            # Ha a trade már BE-n van, kilépünk
            if trade.stop_loss == trade.entry_price:
                return

            # RR = 1 szint
            if trade.direction == 1:  # long
                if (last['close'] - trade.entry_price) >= (trade.entry_price - trade.stop_loss):
                    self.set_stop_loss(trade, trade.entry_price)
            else:  # short
                if (trade.entry_price - last['close']) >= (trade.stop_loss - trade.entry_price):
                    self.set_stop_loss(trade, trade.entry_price)
            return

        # --- LONG setup ---
        if self.fw.is_candle_bearish(sec_last) and self.fw.is_candle_bullish(last):
            long_wick = (last['open'] - last['low']) > (4 * unit)
            small_body = (last['close'] - last['open']) < (2 * unit)
            small_upper_wick = (last['high'] - last['close']) <= unit

            if long_wick and small_body and small_upper_wick:
                trade = self.fw.create_trade(
                    symbol=sym,
                    timeframe=tf,
                    direction=1,
                    strategy=self,
                    risk_pct=2,
                    entry_price=last['close'],
                    stop_loss=last['low'] - unit,  # low alatt
                    risk_reward=2
                )
                self.open_trade(trade)
                return

        # --- SHORT setup ---
        if self.fw.is_candle_bullish(sec_last) and self.fw.is_candle_bearish(last):
            long_wick = (last['high'] - last['open']) > (4 * unit)
            small_body = (last['open'] - last['close']) < (2 * unit)
            small_lower_wick = (last['close'] - last['low']) <= unit

            if long_wick and small_body and small_lower_wick:
                trade = self.fw.create_trade(
                    symbol=sym,
                    timeframe=tf,
                    direction=-1,
                    strategy=self,
                    risk_pct=2,
                    entry_price=last['close'],
                    stop_loss=last['high'] + unit,  # high fölött
                    risk_reward=2
                )
                self.open_trade(trade)
                return
    
    def on_ws_message(self, sym):
        pass
    
    def on_candles_restored(self, sym, tf):
        pass