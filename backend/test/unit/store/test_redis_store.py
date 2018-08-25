
from functools import partial
import unittest

from retro.store.store import TransactionNodes
from retro.store.redis_store import RedisStore
from retro.chain.node import ColumnHeaderNode, BoardNode
from test.helpers import get_redis_container, get_redis_config


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
        self.store.create_board(BoardNode('root', content={"name": "test board"}))

    def tearDown(self):
        # remove all keys from redis
        self.store.client.flushall()

    def test_transaction(self):
        node, parent = self.store.transaction('root', partial(self._transaction, {"foo": "ColumnA"}, "root")).updates

        root = self.store.get_node('root')

        self.assertEqual({node.id}, root.children)
        self.assertEqual(2, root.version)

        self.assertEqual(parent.to_dict(), root.to_dict())

        self.assertEqual('root',
                         self.store.get_node(node.id).parent)
        self.assertEqual({"foo": "ColumnA"},
                         self.store.get_node(node.id).content)

    def test_get_node(self):
        node = self.store.get_node('root')

        self.assertEqual({'name': 'test board'}, node.content)
        self.assertEqual('root', node.id)
        self.assertEqual(1, node.version)

    def _transaction(self, node_content, parent_id, proxy):
        parent = proxy.get_node(parent_id)

        node = ColumnHeaderNode(proxy.next_node_id(), node_content, parent=parent_id)
        parent.set_child(node.id)

        return TransactionNodes(updates=[node, parent])
