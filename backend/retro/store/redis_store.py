import json
import logging
import redis
from typing import List
from datetime import datetime, timedelta
from redis import WatchError
from retro.chain.node import Node, VERSION_KEY, LAST_UPDATE_TIME_KEY
from retro.events.event_processor_factory import EventProcessorFactory
from retro.store.store import Store, Group
from retro.store.exceptions import NodeNotFoundError
from retro.utils import unix_time_millis
from retro.websocket_server.websocket_message import BoardDeleteMessage, NodeLockMessage, NodeUnlockMessage, \
    NodeUpdateMessage, NodeDeleteMessage


_logger = logging.getLogger(__name__)


class RedisStore(Store):
    GROUP_HASH_KEY = 'groups'

    def __init__(self, index, host=None, port=None, client=None):
        super(RedisStore, self).__init__()
        self.client = client if client is not None else redis.StrictRedis(host=host,
                                                                          port=port,
                                                                          encoding='utf-8',
                                                                          decode_responses=True)
        self.index = index

    def get_node(self, node_id):
        return self._get_node(node_id)

    def get_node_lock(self, node_id):
        return self.client.get(self._get_lock_key(node_id))

    def create_board(self, board_node):
        with self.client.pipeline(True) as pipe:
            pipe.multi()
            pipe.hmset(board_node.id, self._get_node_map(board_node))
            pipe.publish(self._get_publish_channel(board_node.id),
                         NodeUpdateMessage(board_node.to_dict()).encode())

            pipe.execute()

        # Update index of board node
        self.index.create_board(board_node)

        return board_node

    def remove_board(self, board_id):
        self.index.remove_board(board_id)

        with self.client.pipeline(True) as pipe:
            pipe.multi()
            pipe.publish(self._get_publish_channel(board_id),
                         BoardDeleteMessage(board_id).encode())
            pipe.execute()

    def get_boards(self, filters=None, search_terms=None, start=0, count=20, sort_key=None, sort_order=None):
        return self.index.get_boards(filters=filters, search_terms=search_terms,
                                     start=start, count=count,
                                     sort_key=sort_key, sort_order=sort_order)

    def has_board(self, board_id):
        return self.index.has_board(board_id)

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

    def get_groups(self) -> List[Group]:
        groups = self.client.hgetall(self.GROUP_HASH_KEY)

        return [Group(k, v) for k, v in groups.items()]

    def get_group(self, group_id: str) -> Group:
        name = self.client.hget(self.GROUP_HASH_KEY, group_id)

        if not name:
            raise KeyError("Unknown group '%s'" % group_id)

        return Group(group_id, name)

    def upsert_group(self, group_id: str, name: str) -> Group:
        self.client.hset(self.GROUP_HASH_KEY, group_id, name)

        return Group(group_id, name)

    def remove_group(self, group_id: str) -> bool:
        return self.client.hdel(self.GROUP_HASH_KEY, group_id) > 0

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

                    nodes = func(RedisStore(self.index, client=pipe))

                    board_node = self._get_node(board_id, pipe=pipe)
                    board_node.version += 1
                    board_node.last_update_time = unix_time_millis(datetime.now())

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
                            node.version = board_node.version

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

                        # update board version and last_update_time
                        pipe.hmset(board_id, {
                            VERSION_KEY: json.dumps({'value': board_node.version}),
                            LAST_UPDATE_TIME_KEY: json.dumps({'value': board_node.last_update_time})
                        })

                        pipe.execute()

                        # Update the corresponding index for the board
                        self.index.update_board(board_node)

                    return nodes
                except WatchError as err:
                    _logger.info("Transaction failed. Reason: %s" % repr(err))

    @staticmethod
    def _get_node_map(node):
        node_dict = node.to_dict()

        for k, v in node_dict.items():
            node_dict[k] = json.dumps({'value': v})

        return node_dict

    def _get_node(self, node_id, pipe=None):
        node_dict = pipe.hgetall(node_id) if pipe else self.client.hgetall(node_id)
        for k, v in node_dict.items():
            node_dict[k] = json.loads(v)['value']

        if not node_dict:
            raise NodeNotFoundError("Node with id '%s' not found in database.", node_id)

        return Node.from_dict(node_dict)
