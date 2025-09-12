import threading
import time
import json
import traceback
import requests
import websocket
from data.log_handler import log_event
from data.time_provider import TimeProvider
from utils import symbol_map

class WsClientLive:
    def __init__(self, ws_endpoint, callback):
        self.ws_endpoint = ws_endpoint
        self.connected = False
        self.connected_lock = threading.Lock()
        self.ws_thread = None
        self.reconnect_thread = None
        self.callback = callback

    def set_connected(self, value):
        with self.connected_lock:
            self.connected = value

    def is_connected(self):
        with self.connected_lock:
            return self.connected

    def get_public_ws_endpoint(self):
        response = requests.post(self.ws_endpoint)
        data = response.json()
        if data['code'] == '200000':
            endpoint = data['data']['instanceServers'][0]['endpoint']
            token = data['data']['token']
            return endpoint, token
        else:
            #print("Hiba endpoint vagy token lekérésekor:", data)
            return None, None

    def on_message(self, ws, message):
        data = json.loads(message)

        if data.get("type") != "message" or "data" not in data:
            #print('⚠️ Nem "message" típusú vagy nincs "data":', data.get("type"), data)
            return

        trade_data = data["data"]
        
        symbol = trade_data["symbol"]
        time_ = int(trade_data["ts"] / 1_000_000_000)
        price = float(trade_data["price"])
        size = float(trade_data["size"])
        side = trade_data["side"]
        
        mapped_symbol = symbol_map.get(symbol)
        TimeProvider.instance.set_time(time_)
        self.callback(mapped_symbol, time_, price, size)

    def on_error(self, ws, error):
        traceback_string = ''.join(traceback.format_exception(type(error), error, error.__traceback__))
        log_event("Ws exception.", traceback_string)

    def on_close(self, ws, close_status_code, close_msg):
        log_event("Ws connection lost.")
        self.set_connected(False)
        self.reconnect()

    def on_open(self, ws):
        log_event("Ws connected.")
        subscribe_msg = {
            "id": "1",
            "type": "subscribe",
            "topic": "/contractMarket/execution:XBTUSDTM,ETHUSDTM",
            "response": True
        }
        ws.send(json.dumps(subscribe_msg))
        self.set_connected(True)

    def start_ws_thread(self, endpoint, token):
        if self.ws_thread is None or not self.ws_thread.is_alive():
            url = f'{endpoint}?token={token}'

            def run_ws():
                def wrapped_on_message(ws, message):
                    self.on_message(ws, message)

                ws = websocket.WebSocketApp(
                    url,
                    on_open=self.on_open,
                    on_message=wrapped_on_message,
                    on_error=self.on_error,
                    on_close=self.on_close
                )
                ws.run_forever(ping_interval=18, ping_timeout=10)

            self.ws_thread = threading.Thread(target=run_ws)
            self.ws_thread.daemon = True
            self.ws_thread.start()
            #print('Websocket szál elindítva.')
        else:
            #print("Websocket szál már fut, nem indítok újabbat")
            pass

    def reconnect(self):
        if self.reconnect_thread is None or not self.reconnect_thread.is_alive():
            self.reconnect_thread = threading.Thread(target=self.run_reconnect)
            self.reconnect_thread.daemon = True
            self.reconnect_thread.start()
        else:
            pass
            #print("Reconnect szál már fut, nem indítok újabbat")

    def run_reconnect(self):
        retry_delay = 15  # másodpercenként próbálkozunk
        while not self.is_connected():
            try:
                endpoint, token = self.get_public_ws_endpoint()
                if endpoint and token:
                    self.start_ws_thread(endpoint, token)
                    time.sleep(10)
            except Exception as e:
                #print("Nem sikerült lekérni az endpointot vagy tokent.")
                time.sleep(retry_delay)

            if not self.is_connected():
                #print("Csatlakozás sikertelen.")
                time.sleep(retry_delay)