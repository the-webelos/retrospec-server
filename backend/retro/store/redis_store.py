import json
import logging
import redis
from redis import WatchError
from retro.store import Store

_logger = logging.getLogger(__name__)


class RedisStore(Store):
    BOARD_SET_KEY = 'boards'

    def __init__(self, host=None, port=None, client=None):
        super(RedisStore, self).__init__()
        self.client = client if client is not None else redis.StrictRedis(host=host,
                                                                          port=port,
                                                                          encoding='utf-8',
                                                                          decode_responses=True)

    def get_node(self, node_id):
        node_dict = self.client.hgetall(node_id)
        for k, v in node_dict.items():
            node_dict[k] = json.loads(v)['value']

        return self.node_from_dict(node_dict)

    def create_board(self, board_node):
        with self.client.pipeline(True) as pipe:
            pipe.multi()

            pipe.sadd(self.BOARD_SET_KEY, board_node.id)
            pipe.publish(self.BOARD_SET_KEY, json.dumps({"event_type": "board_create", "event_data": board_node.id}))
            pipe.hmset(board_node.id, self._get_node_map(board_node))
            pipe.publish(board_node.id, json.dumps({"event_type": "node_update", "event_data": board_node.to_dict()}))

            pipe.execute()

    def get_board_ids(self):
        return self.client.smembers(self.BOARD_SET_KEY)

    def remove_board(self, board_id):
        with self.client.pipeline(True) as pipe:
            pipe.multi()

            pipe.srem(self.BOARD_SET_KEY, board_id)
            pipe.publish(self.BOARD_SET_KEY, json.dumps({"event_type": "board_del", "event_data": board_id}))

            pipe.execute()

    def board_update_listener(self, board_id, message_cb=lambda *x: True):
        p = self.client.pubsub()
        channel = '%s*' % board_id
        p.psubscribe(channel)

        for event in p.listen():
            try:
                _logger.debug("Board listener received event '%s'", event)
                if event['type'] == 'pmessage' and event['pattern'] is not None:
                    if not message_cb(event, board_id):
                        break
            except:
                _logger.exception("Error during subscription processing.")

        p.unsubscribe(channel)
        _logger.info("Subscription to channel '%s' terminated" % channel)

    def stop_listener(self, board_id):
        self.client.publish('%s' % board_id, json.dumps({'event_type': 'lonely_board', 'event_data': board_id}))

    def transaction(self, board_id, func):
        with self.client.pipeline(True) as pipe:
            while True:
                try:
                    pipe.watch(board_id)

                    board_version = json.loads(pipe.hget(board_id, 'version'))['value']

                    read_nodes, update_nodes, remove_nodes = func(RedisStore(client=pipe))

                    if update_nodes or remove_nodes:
                        # start transaction
                        pipe.multi()

                        for node in update_nodes:
                            node.version = board_version + 1

                            # update orig version if needed
                            if node.orig_version is None:
                                node.orig_version = node.version

                            node_dict = self._get_node_map(node)

                            pipe.hmset(node.id, node_dict)

                        if update_nodes:
                            pipe.publish(board_id,
                                         json.dumps({"event_type": "node_update",
                                                     "event_data": [node.to_dict() for node in update_nodes]}))

                        for node in remove_nodes:
                            pipe.delete(node.id)

                        if remove_nodes:
                            pipe.publish(board_id, json.dumps({"event_type": "node_del",
                                                               "event_data": [node.to_dict() for node in remove_nodes]}))

                        pipe.hset(board_id, 'version', json.dumps({'value': board_version + 1}))

                        pipe.execute()

                    return read_nodes, update_nodes, remove_nodes
                except WatchError:
                    _logger.info("Transaction failed")

    @staticmethod
    def _get_node_map(node):
        node_dict = node.to_dict()

        for k, v in node_dict.items():
            node_dict[k] = json.dumps({'value': v})

        return node_dict
