import logging
import redis
from retro.websocket_server import namespace


_logger = logging.getLogger(__name__)


def subscribe_board(board_id, socketio):
    client = redis.StrictRedis(host='localhost', port=6379, encoding='utf-8', decode_responses=True)
    p = client.pubsub()
    channel = '%s*' % board_id
    p.psubscribe(channel)

    for event in p.listen():
        if event['data'] == 'UNSUBSCRIBE':
            p.unsubscribe(channel)
            _logger.info("Unsubscribed from channel '%s'.", channel)
            break
        elif event['type'] == 'pmessage':
            data = {"data": event["data"], "count": 1}
            socketio.emit("my_response", data, namespace=namespace, room=board_id)
            print("%s" % event['data'])

    print("Subscription to channel '%s' terminated" % channel)
