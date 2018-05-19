import eventlet
eventlet.monkey_patch()

import logging
import json
from threading import Lock
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room, close_room, disconnect
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
def error_handler(ex):
    _logger.error(ex)


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

    # If room is empty, close it down
    if is_room_empty(board_id):
        _logger.debug("Room '%s' is empty after unsubscribe", board_id)
        close(board_id)

    emit('unsubscribe_response', {'board_id': board_id})


def close(board_id):
    _logger.debug("Closing room %s", board_id)

    close_room(board_id)


@socketio.on('disconnect_request', namespace=namespace)
def disconnect_request():
    _logger.debug("Disconnect request received from client.")
    emit('disconnect_response', {'data': 'Disconnected!'})
    disconnect()
    _logger.debug("Disconnect successful")


@socketio.on('my_ping', namespace=namespace)
def ping_pong():
    emit('my_pong')


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
    # If sid is the last client in any rooms, terminate the subscription and close the room. socketio will take care of
    # the room close for us, but we need to stop the redis listener ourselves.
    sid = request.sid
    sid_rooms = socketio.server.manager.get_rooms(sid, namespace=namespace)
    _logger.debug("Disconnecting sid '%s'. ROOMS=[%s]", sid, sid_rooms)
    for room in sid_rooms:
        if is_room_empty(room, ignore_sids=[sid]):
            _logger.debug("Room '%s' is empty after '%s' disconnect", sid, room)
            close(room)

    _logger.debug('Client disconnected %s\n  ROOMS=%s', sid, sid_rooms)


def message_cb(message, board_id):
    should_keep_listening = True
    event = json.loads(message['data'])
    event_type = event.get('event_type')

    _logger.debug("Processing '%s' event", event_type)

    if event_type in ('node_update', 'node_del'):
        socketio.emit(event_type, {"nodes": event['event_data']}, namespace=namespace, room=board_id)
    elif event_type in ('node_lock', 'node_unlock'):
        socketio.emit(event_type, {"node_id": event['event_data']}, namespace=namespace, room=board_id)
    elif event_type == 'board_create':
        # nothing for websocket to do
        pass
    else:
        _logger.warning("Unknown event type for %s: %s", board_id, event_type)

    return should_keep_listening


def is_room_empty(room, ignore_sids=()):
    try:
        participants = [p for p in socketio.server.manager.get_participants(namespace, room) if p not in ignore_sids]
        _logger.debug("The following sids are still in room '%s': %s. NOTE: The following sids were ignored: %s",
                      room, participants, ignore_sids)
        # Check if anyone is still in the room
        room_empty = bool(participants)
    except KeyError:
        # This will raise a KeyError if there are no participants in the room
        room_empty = True

    return room_empty


if __name__ == "__main__":
    cfg_ = Config.from_env()
    socketio.run(app, host=cfg_.websocket_host, port=cfg_.websocket_port, debug=False)
