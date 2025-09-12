symbols = [
        'BTC/USDT:USDT',
        'ETH/USDT:USDT'
    ]

symbols_backtest = [
    symbols[1]
]

symbol_map = {
    'XBTUSDTM': symbols[0],
    'ETHUSDTM': symbols[1]
}

timeframes_and_multipliers = {
    '1m': 1,
    '5m': 5,
    '15m': 15,
    '1h': 60,
    '4h': 240,
    '1d': 1440,
    '1w': 10080
}

min_timeframe_backtest = '5m'
max_timeframe_backtest = None