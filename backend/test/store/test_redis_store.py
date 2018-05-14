
import json
import redis
import unittest

from retro.store.redis_store import RedisStore
from retro.chain.node_chain import ColumnHeaderNode, ContentNode, RootNode
from helpers import get_redis_container, get_redis_config


class TestNodeChain(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.redis_container = get_redis_container()

    @classmethod
    def tearDownClass(cls):
        if cls.redis_container:
            cls.redis_container.stop()
            cls.redis_container.remove()

    def setUp(self):
        self.store = RedisStore(**get_redis_config(self.redis_container))
        self.store.create_board(RootNode(id='root', content="RootContent"))

    def tearDown(self):
        # remove all keys from redis
        self.store.client.flushall()

    def test_transaction(self):
        root = RootNode(id='root', content="RootContent", children=['column_a'])
        column = ColumnHeaderNode(id='column_a', order=0, content="ColumnA", parent="root", child=None)
        self.store.transaction('root', lambda x: ([root, column], []))

        self.assertEqual(self._get_node_dict_from_redis(root.id),
                         root.to_dict())
        self.assertEqual(self._get_node_dict_from_redis(column.id),
                         column.to_dict())

    def _get_node_dict_from_redis(self, node_id):
        config = get_redis_config(self.redis_container)
        config['encoding'] = 'utf-8'
        config['decode_responses'] = True

        r = redis.StrictRedis(**config)

        d = r.hgetall(node_id)
        for k, v in d.items():
            d[k] = json.loads(v)

        d['version'] = int(d.get('version', 1))

        return d