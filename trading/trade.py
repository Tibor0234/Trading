class Trade():
    id = 0

    def __init__(self, timeframe_obj, direction, risk_pct, strategy, entry_price,
                stop_loss, take_profit = None, risk_reward = None, details = {}):
        self.id = Trade.id
        Trade.id += 1
                
        #essential
        self.timeframe_obj = timeframe_obj
        self.symbol = timeframe_obj.symbol
        self.timeframe = timeframe_obj.timeframe
        self.direction = direction
        self.risk_pct = risk_pct
        self.strategy = strategy
        self.entry_price = entry_price
        self.stop_loss = stop_loss

        #optional
        self.take_profit = None
        self.risk_reward = None
        self.details = details

        #later
        self.value = None
        self.margin = None
        self.leverage = None
        self.contracts = None
        self.visual_open_time = None

        if stop_loss is not None:
            self.set_sl(stop_loss)
        if take_profit is not None:
            self.set_tp(take_profit)
        if risk_reward is not None:
            self.set_rr(risk_reward)

        #final
        self.close_price = None

        self.approved = False
        self.setup_msg_id = None

    def set_sl(self, sl):
        self.stop_loss = sl
        if self.take_profit is not None:
            self.update_rr_from_sl_tp()
        elif self.risk_reward is not None:
            self.update_tp_from_sl_rr()

    def set_tp(self, tp):
        self.take_profit = tp
        if self.stop_loss is not None:
            self.update_rr_from_sl_tp()
        elif self.risk_reward is not None:
            self.update_sl_from_tp_rr()

    def set_rr(self, rr):
        self.risk_reward = rr
        if self.stop_loss is not None and self.take_profit is None:
            self.update_tp_from_sl_rr()
        elif self.take_profit is not None and self.stop_loss is None:
            self.update_sl_from_tp_rr()

    def update_rr_from_sl_tp(self):
        if self.stop_loss is None or self.take_profit is None:
            return

        risk = abs(self.entry_price - self.stop_loss)
        reward = abs(self.take_profit - self.entry_price)
        if risk != 0:
            self.risk_reward = reward / risk
        else:
            self.risk_reward = None

    def update_tp_from_sl_rr(self):
        if self.stop_loss is None or self.risk_reward is None:
            return

        risk = abs(self.entry_price - self.stop_loss)
        if risk == 0:
            return
        
        if self.direction == 1:
            self.take_profit = self.entry_price + risk * self.risk_reward
        elif self.direction == -1:
            self.take_profit = self.entry_price - risk * self.risk_reward

    def update_sl_from_tp_rr(self):
        if self.take_profit is None or self.risk_reward == 0 or self.risk_reward is None:
            return
        
        reward = abs(self.take_profit - self.entry_price)
        risk = reward / self.risk_reward
        if self.direction == 1:
            self.stop_loss = self.entry_price - risk
        elif self.direction == -1:
            self.stop_loss = self.entry_price + risk

    def is_closed(self, high_price, low_price = None):
        if low_price is None:
            low_price = high_price

        if self.direction == 1:
            if self.take_profit is not None and high_price >= self.take_profit:
                self.close_price = self.take_profit
            elif self.stop_loss is not None and low_price <= self.stop_loss:
                self.close_price = self.stop_loss
        else:
            if self.take_profit is not None and low_price <= self.take_profit:
                self.close_price = self.take_profit
            elif self.stop_loss is not None and high_price >= self.stop_loss:
                self.close_price = self.stop_loss

        if self.close_price is not None:
            return True
        return False
    
    def close_trade(self, price):
        self.close_price = price