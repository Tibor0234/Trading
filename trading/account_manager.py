from data.log_handler import log_event

class AccountManager:
    def __init__(self, account_balance):
        self.account_balance = account_balance
        self.withdrawed = 0
        self.total_trades = 0

    def set_trade_value(self, trade):
        risk_amount = self.account_balance * (trade.risk_pct / 100)
        price_diff = abs(trade.entry_price - trade.stop_loss)
        trade.value = risk_amount / (price_diff / trade.entry_price)

    def get_account_balance(self):
        return self.account_balance
    
    def update_account_balance(self, trade):
        profit = (trade.close_price - trade.entry_price) / trade.entry_price * trade.value * trade.direction
        fee = trade.value * (0.1 / 100)
        net_profit = profit - fee
        self.total_trades += 1
        sign = '+' if net_profit >= 0 else '-'
        log_event(f'Total trades: {self.total_trades}', f' Account balance: {round(self.account_balance, 2)} {sign} {round(abs(net_profit), 2)}')
        self.account_balance += net_profit

    def withdraw(self, amount):
        log_event(f'Account balance: {round(self.account_balance, 2)} - {round(amount, 2)}', f' Withdrawed value: {round(self.withdrawed, 2)} + {round(amount, 2)}')
        self.account_balance -= amount
        self.withdrawed += amount