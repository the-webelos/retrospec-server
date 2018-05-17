import eventlet
eventlet.monkey_patch()

import logging
import json
import redis
from threading import Lock
from flask import Flask, render_template, session, request
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect
from retro.engine.board_engine import BoardEngine
from retro.utils.config import Config
from retro.websocket_server import namespace
from retro.websocket_server.redis_listener import subscribe_board


_logger = logging.getLogger(__name__)


def buildapp_from_config(cfg):
    # Set this variable to "threading", "eventlet" or "gevent" to test the
    # different async modes, or leave it set to None for the application to choose
    # the best option based on installed packages.
    async_mode = "eventlet"

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
def join(message):
    board_id = message.get("board_id")
    if not board_id:
        raise ValueError("No board provided!")

    # Ensure board exists before we create a room for it
#    if not board_engine.has_board(board_id):
#        raise ValueError("Board '%s' does not exist!" % board_id)

    with thread_lock:
        # If there's not already a redis subscription to this board, create one
        if board_id not in socketio.server.manager.rooms.get(namespace, {}):
            socketio.start_background_task(subscribe_board, board_id, socketio)

        join_room(board_id)

    emit('subscribe_response',
         {'board_id': board_id})


@socketio.on('unsubscribe', namespace=namespace)
def leave(message):
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
        client = redis.StrictRedis(host='localhost', port=6379, encoding='utf-8', decode_responses=True)
        client.publish('%s' % board_id, json.dumps({'event_type': 'unsubscribe', 'event_data': board_id}))

    close_room(board_id)


@socketio.on('disconnect_request', namespace=namespace)
def disconnect_request():
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': 'Disconnected!', 'count': session['receive_count']})
    disconnect()


@socketio.on('my_ping', namespace=namespace)
def ping_pong():
    emit('my_pong')


@socketio.on('disconnect', namespace=namespace)
def test_disconnect():
    # get rooms for sid
    print('Client disconnected', request.sid)


if __name__ == "__main__":
    cfg_ = Config.from_env()
    socketio.run(app, host=cfg_.websocket_host, port=cfg_.websocket_port, debug=False)
