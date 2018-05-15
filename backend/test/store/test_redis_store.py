
import json
import redis
import unittest

from retro.store.redis_store import RedisStore
from retro.chain.node import ColumnHeaderNode, ContentNode, BoardNode
from helpers import get_redis_container, get_redis_config


class TestRedisStore(unittest.TestCase):
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
        self.store.create_board(BoardNode(id='root', content={"name": "test board"}))

    def tearDown(self):
        # remove all keys from redis
        self.store.client.flushall()

    def test_transaction(self):
        root = BoardNode(id='root', content="RootContent", children=['column_a'])
        column = ColumnHeaderNode(id='column_a', content="ColumnA", parent="root", child=None)
        self.store.transaction('root', lambda x: ([root, column], []))

        self.assertEqual(self.store.get_node('root').to_dict(),
                         root.to_dict())
        self.assertEqual(self.store.get_node('column_a').to_dict(),
                         column.to_dict())

    def test_get_node(self):
        node = self.store.get_node('root')

        self.assertEqual({'name': 'test board'}, node.content)
        self.assertEqual('root', node.id)
        self.assertEqual(1, node.version)
