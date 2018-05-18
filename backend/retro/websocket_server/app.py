import eventlet
eventlet.monkey_patch()

import logging
import json
from threading import Lock
from flask import Flask, render_template, session, request
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, disconnect
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
    setup_basic_logging()
    logging.getLogger("socketio").setLevel(logging.WARNING)
    logging.getLogger("engineio").setLevel(logging.WARNING)

    _app = Flask(__name__)
    _app.config['SECRET_KEY'] = cfg.flask_secret
    _socket_io = SocketIO(_app, async_mode=async_mode)

    return _app, _socket_io


cfg_ = Config.from_env()
app, socketio = buildapp_from_config(cfg_)
board_engine = BoardEngine(cfg_)
thread_lock = Lock()


@app.route('/')
def index():
    return render_template('index.html', async_mode=socketio.async_mode)


@socketio.on_error(namespace=namespace)
def error_handler(ex):
    _logger.error(ex)


@socketio.on('subscribe', namespace=namespace)
def subscribe(message):
    board_id = message.get("board_id")
    if not board_id:
        raise ValueError("No board provided!")

    # Ensure board exists before we create a room for it
#    if not board_engine.has_board(board_id):
#        raise ValueError("Board '%s' does not exist!" % board_id)

    with thread_lock:
        # If there's not already a redis subscription to this board, create one
        if board_id not in socketio.server.manager.rooms.get(namespace, {}):
            socketio.start_background_task(board_engine.subscribe_board, board_id, message_cb)

        join_room(board_id)

    _logger.info("Subscribed to board '%s'. [USER=%s]" % (board_id, request.sid))
    emit('subscribe_response',
         {'board_id': board_id})


@socketio.on('unsubscribe', namespace=namespace)
def unsubscribe(message):
    board_id = message['board_id']
    leave_room(board_id)

    try:
        # Check if anyone is still in the room
        room_empty = False if list(socketio.server.manager.get_participants(namespace, board_id)) else True
    except KeyError:
        # This will raise a KeyError if there are no participants in the room
        room_empty = True

    # If room is empty, close it down
    if room_empty:
        close(message)

    emit('unsubscribe_response',
         {'board_id': board_id})


def close(message):
    board_id = message['board_id']

    # The room is being closed so we don't need the redis subscription anymore
    with thread_lock:
        board_engine.unsubscribe_board(board_id)

    close_room(board_id)


@socketio.on('disconnect_request', namespace=namespace)
def disconnect_request():
    emit('disconnect_response', {'data': 'Disconnected!'})
    disconnect()


@socketio.on('my_ping', namespace=namespace)
def ping_pong():
    emit('my_pong')


@socketio.on('connect', namespace=namespace)
def test_connect():
    emit('connect_response', {'data': 'Connected'})


@socketio.on('disconnect', namespace=namespace)
def test_disconnect():
    # get rooms for sid
    _logger.info('Client disconnected %s', request.sid)


def message_cb(message, board_id):
    should_keep_listening = True
    event = json.loads(message['data'])
    event_type = event.get('event_type')

    if event_type in ('node_update', 'node_del'):
        socketio.emit(event_type, {"nodes": event['event_data']}, namespace=namespace, room=board_id)
    elif event_type == 'lonely_board' or event_type == 'board_del':
        should_keep_listening = False
    elif event_type == 'board_create':
        # nothing for websocket to do
        pass
    else:
        _logger.warning("Unknown event type for %s: %s", board_id, event_type)

    return should_keep_listening


if __name__ == "__main__":
    cfg_ = Config.from_env()
    socketio.run(app, host=cfg_.websocket_host, port=cfg_.websocket_port, debug=False)
