import json
import logging
import redis
from redis import WatchError
from retro.store import Store

_logger = logging.getLogger(__name__)


class RedisStore(Store):
    def __init__(self, host=None, port=None, client=None):
        super(RedisStore, self).__init__()
        self.client = client or redis.StrictRedis(host=host, port=port, encoding='utf-8', decode_responses=True)

    def get_node(self, node_id):
        node_dict = self.client.hgetall(node_id)
        for k, v in node_dict.items():
            node_dict[k] = json.loads(v)

        return self.node_from_dict(self.client.hgetall(node_id))

    def create_board(self, board_node):
        self.client.hmset(board_node.id, board_node.to_dict())

    def transaction(self, board_id, func):
        with self.client.pipeline(True) as pipe:
            while True:
                try:
                    pipe.watch(board_id)

                    board_version = int(pipe.hget(board_id, 'version'))

                    update_nodes, remove_nodes = func(RedisStore(client=pipe))

                    # start transaction
                    pipe.multi()

                    for node in update_nodes:
                        node.version = board_version + 1
                        node_dict = node.to_dict()

                        for k,v in node_dict.items():
                            node_dict[k] = json.dumps(v)

                        pipe.hmset(node.id, node_dict)

                        pipe.hset(board_id, 'version', board_version + 1)

                    for node in remove_nodes:
                        pipe.delete(node.id)

                    pipe.execute()

                    return update_nodes
                except WatchError:
                    _logger.info("Transaction failed")
