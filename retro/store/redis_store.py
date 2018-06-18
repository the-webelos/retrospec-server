import json
import logging
import redis
from datetime import timedelta
from redis import WatchError
from retro.chain.node import Node
from retro.events.event_processor_factory import EventProcessorFactory
from retro.store import Store
from retro.store.exceptions import NodeNotFoundError
from retro.websocket_server.websocket_message import BoardDeleteMessage, NodeLockMessage, NodeUnlockMessage, \
    NodeUpdateMessage, NodeDeleteMessage


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

        if not node_dict:
            raise NodeNotFoundError("Node with id '%s' not found in database.", node_id)

        return Node.from_dict(node_dict)

    def get_node_lock(self, node_id):
        return self.client.get(self._get_lock_key(node_id))

    def get_board_ids(self):
        return self.client.smembers(self.BOARD_SET_KEY)

    def create_board(self, board_node):
        with self.client.pipeline(True) as pipe:
            pipe.multi()

            pipe.sadd(self.BOARD_SET_KEY, board_node.id)
            pipe.hmset(board_node.id, self._get_node_map(board_node))
            pipe.publish(self._get_publish_channel(board_node.id),
                         NodeUpdateMessage(board_node.to_dict()).encode())

            pipe.execute()

    def remove_board(self, board_id):
        with self.client.pipeline(True) as pipe:
            pipe.multi()

            pipe.srem(self.BOARD_SET_KEY, board_id)
            pipe.publish(self._get_publish_channel(board_id),
                         BoardDeleteMessage(board_id).encode())
            pipe.execute()

    def update_listener(self, message_cb=lambda *x: True):
        board_update_channel = 'board_update|*'
        key_expiration_channel = '__key*__:expired'

        p = self.client.pubsub()
        p.psubscribe(board_update_channel)
        p.psubscribe(key_expiration_channel)

        for event in p.listen():
            try:
                _logger.debug("Update listener received event '%s'", event)
                if event['type'] == 'pmessage' and event['pattern']:
                    event_processor = EventProcessorFactory.get_event_processor(event, message_cb=message_cb)
                    if not event_processor.process():
                        break
            except:
                _logger.exception("Error during subscription processing.")

        p.punsubscribe(board_update_channel)
        p.punsubscribe(key_expiration_channel)
        _logger.info("Subscription terminated")

    @staticmethod
    def _get_lock_key(node_id):
        return "NODELOCK.%s" % node_id

    @staticmethod
    def _get_publish_channel(board_id):
        return 'board_update|%s' % board_id

    def transaction(self, board_id, func):
        with self.client.pipeline(True) as pipe:
            while True:
                try:
                    pipe.watch(board_id)

                    nodes = func(RedisStore(client=pipe))

                    board_version = json.loads(pipe.hget(board_id, 'version'))['value']

                    if nodes.updates or nodes.deletes or nodes.locks or nodes.unlocks:
                        # start transaction
                        pipe.multi()

                        # delete nodes
                        for node in nodes.deletes:
                            pipe.delete(node.id)

                        # publish deletes
                        if nodes.deletes:
                            pipe.publish(self._get_publish_channel(board_id),
                                         NodeDeleteMessage([node.to_dict() for node in nodes.deletes]).encode())

                        # Update nodes
                        for node in nodes.updates:
                            node.version = board_version + 1

                            # update orig version if needed
                            if node.orig_version is None:
                                node.orig_version = node.version

                            node_dict = self._get_node_map(node)

                            pipe.hmset(node.id, node_dict)

                        # publish updates
                        if nodes.updates:
                            pipe.publish(self._get_publish_channel(board_id),
                                         NodeUpdateMessage([node.to_dict() for node in nodes.updates]).encode())

                        # lock nodes
                        for node_id, lock_value in nodes.locks:
                            lock_key = self._get_lock_key(node_id)
                            pipe.setex(lock_key, timedelta(hours=1), lock_value)

                        # publish locks
                        if nodes.locks:
                            pipe.publish(self._get_publish_channel(board_id),
                                         NodeLockMessage([node_id for node_id, _ in nodes.locks]).encode())

                        # unlock nodes
                        for node_id in nodes.unlocks:
                            lock_key = self._get_lock_key(node_id)
                            pipe.delete(lock_key)

                        # publish unlocks
                        if nodes.unlocks:
                            pipe.publish(self._get_publish_channel(board_id),
                                         NodeUnlockMessage([node_id for node_id in nodes.unlocks]).encode())

                        # update board version
                        pipe.hset(board_id, 'version', json.dumps({'value': board_version + 1}))

                        pipe.execute()

                    return nodes
                except WatchError as err:
                    _logger.info("Transaction failed. Reason: %s" % repr(err))

    @staticmethod
    def _get_node_map(node):
        node_dict = node.to_dict()

        for k, v in node_dict.items():
            node_dict[k] = json.dumps({'value': v})

        return node_dict
