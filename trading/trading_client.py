from config import kc_client

class TradingClient:
    def open_market_order(self, trade):
        """Piaci order nyitása leverage-gel, SL és TP az orderben"""
        side = 'buy' if trade.direction == 1 else 'sell'

        params = {
            'leverage': trade.leverage,
            'marginMode': 'isolated',
            'reduceOnly': False
        }

        # Ha van stop loss
        if trade.stop_loss:
            params['stopLoss'] = {
                'triggerPrice': trade.stop_loss,
                'triggerPriceType': 'last'
            }

        # Ha van take profit
        if trade.take_profit:
            params['takeProfit'] = {
                'triggerPrice': trade.take_profit,
                'triggerPriceType': 'last'
            }

        order = kc_client.create_order(
            symbol=trade.symbol,
            type='market',
            side=side,
            amount=trade.contracts,
            params=params
        )
        return order


    def open_limit_order(self, trade):
        """Limit order nyitása leverage-gel, SL és TP az orderben"""
        side = 'buy' if trade.direction == 1 else 'sell'

        params = {
            'leverage': trade.leverage,
            'marginMode': 'isolated',
            'reduceOnly': False
        }

        # SL / TP
        if trade.stop_loss:
            params['stopLoss'] = {
                'triggerPrice': trade.stop_loss,
                'triggerPriceType': 'last'
            }
        if trade.take_profit:
            params['takeProfit'] = {
                'triggerPrice': trade.take_profit,
                'triggerPriceType': 'last'
            }

        order = kc_client.create_order(
            symbol=trade.symbol,
            type='limit',
            side=side,
            amount=trade.contracts,
            price=trade.entry_price,
            params=params
        )
        return order

    def close_position(self, trade):
        """Pozíció zárása market orderrel (reduceOnly=True)"""
        close_side = 'sell' if trade.direction == 1 else 'buy'
        params = {
            'reduceOnly': True
        }

        order = kc_client.create_order(
            symbol=trade.symbol,
            type='market',
            side=close_side,
            amount=trade.contracts,
            params=params
        )
        return order