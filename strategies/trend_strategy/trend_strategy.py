from strategies.strategy import Strategy

class TrendStrategy(Strategy):
    def __init__(self):
        super().__init__()
        self.base_account_balance = None

    def on_candle_close(self, sym, tf):
        account_balance = self.fw.get_account_balance()
        if self.base_account_balance is None:
            self.base_account_balance = account_balance
        elif account_balance > self.base_account_balance * 1.1:
            self.fw.withdraw(account_balance - self.base_account_balance)

        self.open_long(sym, tf)
        self.manage_long(sym, tf)

    def open_long(self, sym, tf):
        if tf != '15m': return
        if self.fw.is_trade_open(sym, strategy=self): return

        candles_df = self.fw.get_cache_df(sym, tf)
        candles_df_before = candles_df.iloc[:-1]
        last_candle = self.fw.get_last_closed_candle(sym, tf)

        lows = self.fw.get_swing_lows(sym, tf, candles_df, min_sl=2)
        highs = self.fw.get_swing_highs(sym, tf, candles_df, min_sl=2)
        is_uptrend = self.fw.is_uptrend(sym, tf, lows, highs)
        
        lows_before = self.fw.get_swing_lows(sym, tf, candles_df_before, min_sl=2, save=False)
        highs_before = self.fw.get_swing_highs(sym, tf, candles_df_before, min_sl=2, save=False)
        is_uptrend_before = self.fw.is_uptrend(sym, tf, lows_before, highs_before, save=False)

        if is_uptrend and not is_uptrend_before:
            sec_last_low = self.fw.get_swing_lows(sym, tf, pos=-2)
            trade = self.fw.create_trade(
                symbol=sym,
                timeframe=tf,
                direction=1,
                strategy=self,
                risk_pct=2,
                entry_price=last_candle['close'],
                stop_loss=sec_last_low['low']
            )
            self.open_trade(trade)

    def manage_long(self, sym, tf):
        if tf != '15m': return
        if not self.fw.is_trade_open(sym, strategy=self): return

        trade = self.fw.get_open_trades(sym, tf, strategy=self, direction=1)[0]

        candles_df = self.fw.get_cache_df(sym, tf)
        lows = self.fw.get_swing_lows(sym, tf, candles_df, min_sl=2)
        highs = self.fw.get_swing_highs(sym, tf, candles_df, min_sl=2)
        last_candle = self.fw.get_last_closed_candle(sym, tf)
        if not self.fw.is_uptrend(sym, tf, lows, highs):
            self.close_trade(trade, last_candle['close'])
        
        sec_last_low = self.fw.get_swing_lows(sym, tf, pos=-2)

        stop_loss = sec_last_low['low']
        self.set_stop_loss(trade, stop_loss)

    def on_ws_message(self, sym):
        pass
    
    def on_candles_restored(self, sym, tf):
        pass