import websocket
from websocket import create_connection
from retro.utils.config import Config


try:
    import thread
except ImportError:
    import _thread as thread
import time


def on_message(ws, message):
    print(message)


def on_error(ws, error):
    print(error)


def on_close(ws):
    print("### closed ###")


def on_open(ws):
    def run(*args):
        for i in range(3):
            time.sleep(1)
            ws.send("Hello %d" % i)

        time.sleep(1)
        ws.close()
        print("Thread terminating...")

    thread.start_new_thread(run, ())


if __name__ == "__main__":
    cfg = Config()
    url = "ws://%s:%s/" % (cfg.websocket_host, cfg.websocket_port)
    #websocket.enableTrace(True)
    #ws_server = websocket.WebSocketApp(url, on_message=on_message, on_error=on_error, on_close=on_close)
    #ws_server.on_open = on_open
    #ws_server.run_forever(http_proxy_host=cfg.websocket_host, http_proxy_port=cfg.websocket_port)
    #time.sleep(1)

    ws_ = create_connection(url)
    ws_.send("Hello world!")
    result = ws_.recv()
    print("Received '%s'" % result)
    ws_.close()
    #ws_ = websocket.WebSocket()
    #ws_.connect("ws://%s:%s/websocket" % (cfg.websocket_host, cfg.websocket_port))
