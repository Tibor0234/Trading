from config import kc_client

class TradingClient:
    def place_order(self, symbol, type, side, amount, leverage):
        order = kc_client.create_order(
            symbol = symbol,
            type = type,
            side = side,
            amount = amount,
            params= {
                'leverage': leverage
            }
        )
        return order

    def close_position(self, symbol, side):
        order = kc_client.close_position(
            symbol=symbol,
            side=side
        )
        return order