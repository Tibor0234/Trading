from abc import ABC, abstractmethod
from data.log_handler import log_event
from config import kc_client

class AccountManager(ABC):
    def __init__(self):
        self.total_trades = 0

    @abstractmethod
    def set_trade_value(self, trade):
        pass

    @abstractmethod
    def get_account_balance(self):
        pass
    
    @abstractmethod
    def update_account_balance(self, trade):
        pass

    @abstractmethod
    def withdraw(self, amount):
        pass

class AccountManagerLive(AccountManager):
    def __init__(self):
        super().__init__()

    def set_trade_value(self, trade):
        max_margin_pct = 0.35
        max_allowed_leverage = 10

        account_balance = self.get_account_balance()
        max_allowed_margin = account_balance * max_margin_pct

        price_diff = abs(trade.entry_price - trade.stop_loss)
        trade_value = account_balance * (trade.risk_pct / 100) / (price_diff / trade.entry_price)

        market = kc_client.market(trade.symbol)
        contract_size = market['contractSize']
        price = kc_client.fetch_ticker(trade.symbol)['last']
        contract_usd = contract_size * price

        contracts = int(trade_value / contract_usd)
        if contracts < 1:
            contracts = 1

        contract_value = contracts * contract_usd

        if contract_value <= max_allowed_margin:
            leverage = 1
            margin = contract_value
        else:
            leverage = contract_value / max_allowed_margin
            if leverage > max_allowed_leverage:
                return False
            margin = max_allowed_margin

        trade.value = trade_value
        trade.margin = margin
        trade.leverage = leverage
        trade.contracts = contracts

        return True

    def get_account_balance(self):
        return kc_client.fetch_balance()['USDT']['free']
    
    def update_account_balance(self, trade):
        profit = (trade.close_price - trade.entry_price) / trade.entry_price * trade.value * trade.direction
        self.total_trades += 1
        log_event(f'Total trades: {self.total_trades}', f' Profit: {round(abs(profit), 2)}')

        if profit > 0: return 1
        else: return 0

    def withdraw(self, amount):
        currency = 'USDT'
        transfer = kc_client.transfer(
            code=currency,
            amount=amount,
            fromAccount="futures",
            toAccount="spot"
        )
        log_event(f'{round(amount, 2)} USDT has been withdrawed to spot account.')

        return transfer

class AccountManagerBacktest(AccountManager):
    def __init__(self, account_balance):
        super().__init__()
        self.account_balance = account_balance
        self.withdrawed = 0

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

        if profit > 0: return 1
        else: return 0

    def withdraw(self, amount):
        log_event(f'Account balance: {round(self.account_balance, 2)} - {round(amount, 2)}', f' Withdrawed value: {round(self.withdrawed, 2)} + {round(amount, 2)}')
        self.account_balance -= amount
        self.withdrawed += amount