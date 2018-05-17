import json
import logging
import redis
from retro.websocket_server import namespace

_logger = logging.getLogger(__name__)


def subscribe_board(board_id, socketio):
    client = redis.StrictRedis(host='localhost', port=6379, encoding='utf-8', decode_responses=True)
    p = client.pubsub()
    channel = '%s*' % board_id
    p.psubscribe(channel)

    for item in p.listen():
        try:
            _logger.warning("%s", item)
            if item['type'] == 'pmessage' and item['pattern'] is not None:
                event = json.loads(item['data'])
                event_type = event.get('event_type')
                if event_type in ('node_update', 'node_del'):
                    socketio.emit(event_type, event['event_data'], namespace=namespace, room=board_id)
                elif event_type == 'board_unsubscribe' or event_type == 'board_del':
                    p.unsubscribe(channel)
                elif event_type == 'board_create':
                    # nothing for websocket to do
                    pass
                else:
                    _logger.warning("Unknown event type for %s: %s", board_id, event_type)
        except:
            _logger.exception("Error during subscription processing.")

    print("Subscription to channel '%s' terminated" % channel)
