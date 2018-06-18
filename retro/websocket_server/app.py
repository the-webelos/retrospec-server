import eventlet
eventlet.monkey_patch()

import logging
from threading import Lock
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room, disconnect
from retro.engine.board_engine import BoardEngine
from retro.utils.config import Config
from retro.utils.retro_logging import setup_basic_logging
from retro.websocket_server import namespace

_logger = logging.getLogger(__name__)


def buildapp_from_config(cfg):
    # Set this variable to "threading", "eventlet" or "gevent" to test the
    # different async modes, or leave it set to None for the application to choose
    # the best option based on installed packages.
    async_mode = "eventlet"
    setup_basic_logging(level=logging.DEBUG)
    logging.getLogger("socketio").setLevel(logging.WARNING)
    logging.getLogger("engineio").setLevel(logging.WARNING)

    _app = Flask(__name__)
    _app.config['SECRET_KEY'] = cfg.flask_secret
    _socket_io = SocketIO(_app, async_mode=async_mode)

    return _app, _socket_io


cfg_ = Config.from_env()
app, socketio = buildapp_from_config(cfg_)
board_engine = BoardEngine(cfg_)
thread = None
thread_lock = Lock()


@app.route('/')
def index():
    return render_template('index.html', async_mode=socketio.async_mode)


@socketio.on_error(namespace=namespace)
def error_handler(_ex):
    _logger.exception("Unhandled exception from websocket server.")


@socketio.on('connect', namespace=namespace)
def test_connect():
    global thread

    with thread_lock:
        if thread is None:
            _logger.debug("Starting update listener thread...")
            thread = socketio.start_background_task(board_engine.update_listener, message_cb)

    emit('connect_response', {'data': 'Connected'})
    _logger.debug("Connection successful for sid '%s'!", request.sid)


@socketio.on('disconnect', namespace=namespace)
def test_disconnect():
    _logger.debug("Client '%s' successfully disconnected", request.sid)


@socketio.on('disconnect_request', namespace=namespace)
def disconnect_request():
    _logger.debug("Disconnect request received from client '%s'.", request.sid)
    emit('disconnect_response', {'data': 'Disconnected!'})
    disconnect()


@socketio.on('subscribe', namespace=namespace)
def subscribe(message):
    board_id = message.get("board_id")
    if not board_id:
        raise ValueError("No board provided!")

    # Ensure board exists before we create a room for it
    #if not board_engine.has_board(board_id):
    #    raise ValueError("Board '%s' does not exist!" % board_id)

    join_room(board_id)

    _logger.debug("Subscribed to board '%s'. [USER=%s]\n  ROOMS=%s" %
                  (board_id, request.sid, socketio.server.manager.get_rooms(request.sid, namespace)))
    emit('subscribe_response', {'board_id': board_id})


@socketio.on('unsubscribe', namespace=namespace)
def unsubscribe(message):
    board_id = message['board_id']
    _logger.debug("Unsubscribing from board '%s'...", board_id)
    leave_room(board_id)
    emit('unsubscribe_response', {'board_id': board_id})


@socketio.on('my_ping', namespace=namespace)
def ping_pong():
    emit('my_pong')


def message_cb(message, board_id):
    should_keep_listening = True
    _logger.debug("Processing '%s' event for board '%s'. Event data: '%s'.", message.type, board_id, message.data)
    socketio.emit(message.type, message.data, namespace=namespace, room=board_id)

    return should_keep_listening


if __name__ == "__main__":
    cfg_ = Config.from_env()
    socketio.run(app, host=cfg_.websocket_host, port=cfg_.websocket_port, debug=False)
