from data.log_handler import clear_chart_log_dir, init_log_file, log_event
from factory import FactoryLive, FactoryBacktest
from strategies.strategy_framework import StrategyFramework
from strategies.liq_sweep_strategy.liq_sweep_strategy import LiqSweepStrategy
from strategies.trendline_strategy.trendline_strategy import TrendlineStrategy
from strategies.trend_strategy.trend_strategy import TrendStrategy
from strategies.wick_strategy.wick_strategy import WickStrategy

#Settings------------------------------------------------------------

live = False

strategies = [
    #WickStrategy()
    #LiqSweepStrategy(),
    TrendlineStrategy()
    #TrendStrategy()
]

backtest_start_time = 1687651200
backtest_end_time = None

factory_params = {
    'btc_tolerance_min': 0.00015,
    'btc_tolerance_max': 0.035,
    'eth_tolerance_min': 0.0004,
    'eth_tolerance_max': 0.025,
    'trendline_tolerance_mp': 1.1,
    'order_zone_tolerance_mp': 1.35,
    'bt_start_time': backtest_start_time,
    'bt_account_balance': 1_000
}

#---------------------------------------------------------------------

clear_chart_log_dir()
init_log_file()

if live:
    factory = FactoryLive()
else:
    factory = FactoryBacktest()

trade_service, ws_client = factory.program_builder(factory_params)

framework = StrategyFramework(trade_service)
for strategy in strategies:
    strategy.init_strategy(trade_service, framework)
    trade_service.add_strategy(strategy)

if live:
    endpoint, token = ws_client.get_public_ws_endpoint()
    ws_client.start_ws_thread(endpoint, token)

    log_event('The program has been started.')
    print('A program elindult. Diagram megelenítéséhez írd be a kívánt szimbólumot és időkeretet. (pl. btc1m)')
else:
    ws_client.run_simulation(cursor=backtest_start_time, end_time=backtest_end_time)

#Loop------------------------------------------------------------------
while True:
    item = input()
    symbol = item[:3]
    timeframe = item[3:]
    trade_service.engine.visualize_from_input(symbol, timeframe)