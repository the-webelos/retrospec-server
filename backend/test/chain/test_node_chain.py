
import unittest
from retro.store.mem_store import MemStore
from retro.chain.node_chain import ColumnHeaderNode, ContentNode, RootNode, NodeChain


class TestNodeChain(unittest.TestCase):
    def setUp(self):
        default_nodes = {"root": RootNode("root", "RootContent", 1, {'column_a', 'column_b'}).to_dict(),
                         "column_a": ColumnHeaderNode("column_a", "ColumnA", 1, 0, "root", "node_1").to_dict(),
                         "column_b": ColumnHeaderNode("column_b", "ColumnB", 1, 1, "root", "node_5").to_dict(),
                         "node_1": ContentNode("node_1", "Node1", 1, "column_a", "node_2").to_dict(),
                         "node_2": ContentNode("node_2", "Node2", 1, "node_1", "node_3").to_dict(),
                         "node_3": ContentNode("node_3", "Node3", 1, "node_2", "node_4").to_dict(),
                         "node_4": ContentNode("node_4", "Node4", 1, "node_3").to_dict(),
                         "node_5": ContentNode("node_5", "Node5", 1, "column_b", "node_6").to_dict(),
                         "node_6": ContentNode("node_6", "Node6", 1, "node_5").to_dict()}
        self.store = MemStore(default_nodes)

    def test_populate_chain(self):
        chain = NodeChain(self.store, 'root')

        self.assertEqual(9, len(chain.nodes()))

        self.assertEqual(RootNode(id='root', content="RootContent", version=1, children={'column_a', 'column_b'}),
                         chain.get_node('root'))

        self.assertEqual(ColumnHeaderNode(id='column_a', order=0, content="ColumnA", version=1, parent="root", child="node_1"),
                         chain.get_node('column_a'))

        self.assertEqual(ContentNode(id='node_1', content="Node1", version=1, parent="column_a", child="node_2"),
                         chain.get_node('node_1'))

        self.assertEqual(ContentNode(id='node_2', content="Node2", version=1, parent="node_1", child="node_3"),
                         chain.get_node('node_2'))

        self.assertEqual(ContentNode(id='node_3', content="Node3", version=1, parent="node_2", child="node_4"),
                         chain.get_node('node_3'))

        self.assertEqual(ContentNode(id='node_4', content="Node4", version=1, parent="node_3", child=None),
                         chain.get_node('node_4'))

        self.assertEqual(ColumnHeaderNode(id='column_b', order=1, content="ColumnB", version=1, parent="root", child="node_5"),
                         chain.get_node('column_b'))

        self.assertEqual(ContentNode(id='node_5', content="Node5", version=1, parent="column_b", child="node_6"),
                         chain.get_node('node_5'))

        self.assertEqual(ContentNode(id='node_6', content="Node6", version=1, parent="node_5", child=None),
                         chain.get_node('node_6'))

    def test_add_node_to_root(self):
        chain = NodeChain(self.store, 'root')

        node = chain.add_node('new_content', 'root')

        self.assertEqual({'column_a', 'column_b', node.id},
                         self.store.get_node('root').children)
        self.assertEqual(node,
                         self.store.get_node(node.id))

    def test_add_node_to_column_end(self):
        chain = NodeChain(self.store, 'root')

        node = chain.add_node('new_content', 'node_4')

        self.assertEqual(node.id,
                         self.store.get_node('node_4').child)
        self.assertEqual('node_4',
                         node.parent)

    def test_add_node_between_nodes(self):
        chain = NodeChain(self.store, 'root')

        node = chain.add_node('new_content', 'node_1')

        self.assertEqual(node.id,
                         self.store.get_node('node_1').child)
        self.assertEqual('node_1',
                         node.parent)
        self.assertEqual('node_2',
                         node.child)
        self.assertEqual(node.id,
                         self.store.get_node('node_2').parent)

    def test_move_node(self):
        chain = NodeChain(self.store, 'root')

        node = chain.move_node("node_2", "node_5")

        self.assertEqual("node_5", self.store.get_node("node_2").parent)
        self.assertEqual("node_2", self.store.get_node("node_5").child)
        self.assertEqual("node_6", self.store.get_node("node_2").child)
        self.assertEqual("node_2", self.store.get_node("node_6").parent)
        self.assertEqual("node_3", self.store.get_node("node_1").child)
        self.assertEqual("node_1", self.store.get_node("node_3").parent)

    def test_remove_node(self):
        chain = NodeChain(self.store, 'root')

        chain.remove_node("node_2")

        self.assertEqual("node_3", self.store.get_node("node_1").child)
        self.assertEqual("node_1", self.store.get_node("node_3").parent)
