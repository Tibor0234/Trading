import ccxt
import os
from dotenv import load_dotenv

load_dotenv()

exchange = ccxt.kucoinfutures()

api_key = os.getenv('API_KEY')
api_secret = os.getenv('API_SECRET')
api_passphrase = os.getenv('API_PASSPHRASE')

authentification = {
    "apiKey": api_key,
    "secret": api_secret,
    "password": api_passphrase
}

kc_client = ccxt.kucoinfutures(authentification)

ws_endpoint = 'https://api-futures.kucoin.com/api/v1/bullet-public'

root = r"F:\SATradingBOT"

activity_log_path = os.path.join(root, "activity_log.csv")
chart_log_path = os.path.join(root, "chart_log")

db_path_live = os.path.join(root, "trading.db")
db_path_backtest = os.path.join(root, "candles_for_backtest", "backtest.db")

discord_bot_token = os.getenv('DISCORD_BOT_TOKEN')