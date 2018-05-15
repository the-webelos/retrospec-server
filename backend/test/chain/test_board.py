
import unittest
from retro.store.mem_store import MemStore
from retro.chain.board import Board
from retro.chain.node import ColumnHeaderNode, ContentNode, BoardNode


class TestBoard(unittest.TestCase):
    def setUp(self):
        default_nodes = {"root": BoardNode("root", {"test": "RootContent"}, 1, {'column_a', 'column_b'}).to_dict(),
                         "column_a": ColumnHeaderNode("column_a", {"test": "ColumnA"}, 1, 0, "root", "node_1").to_dict(),
                         "column_b": ColumnHeaderNode("column_b", {"test": "ColumnB"}, 1, 1, "root", "node_5").to_dict(),
                         "node_1": ContentNode("node_1", {"test": "Node1"}, 1, "column_a", "node_2").to_dict(),
                         "node_2": ContentNode("node_2", {"test": "Node2"}, 1, "node_1", "node_3").to_dict(),
                         "node_3": ContentNode("node_3", {"test": "Node3"}, 1, "node_2", "node_4").to_dict(),
                         "node_4": ContentNode("node_4", {"test": "Node4"}, 1, "node_3").to_dict(),
                         "node_5": ContentNode("node_5", {"test": "Node5"}, 1, "column_b", "node_6").to_dict(),
                         "node_6": ContentNode("node_6", {"test": "Node6"}, 1, "node_5").to_dict()}
        self.store = MemStore(default_nodes)

    def test_populate_chain(self):
        chain = Board(self.store, 'root')

        self.assertEqual(9, len(chain.nodes()))

        self.assertEqual(BoardNode(id='root', content={"test": "RootContent"}, version=1, children={'column_a', 'column_b'}),
                         chain.get_node('root'))

        self.assertEqual(ColumnHeaderNode(id='column_a', order=0, content={"test": "ColumnA"}, version=1, parent="root", child="node_1"),
                         chain.get_node('column_a'))

        self.assertEqual(ContentNode(id='node_1', content={"test": "Node1"}, version=1, parent="column_a", child="node_2"),
                         chain.get_node('node_1'))

        self.assertEqual(ContentNode(id='node_2', content={"test": "Node2"}, version=1, parent="node_1", child="node_3"),
                         chain.get_node('node_2'))

        self.assertEqual(ContentNode(id='node_3', content={"test": "Node3"}, version=1, parent="node_2", child="node_4"),
                         chain.get_node('node_3'))

        self.assertEqual(ContentNode(id='node_4', content={"test": "Node4"}, version=1, parent="node_3", child=None),
                         chain.get_node('node_4'))

        self.assertEqual(ColumnHeaderNode(id='column_b', order=1, content={"test": "ColumnB"}, version=1, parent="root", child="node_5"),
                         chain.get_node('column_b'))

        self.assertEqual(ContentNode(id='node_5', content={"test": "Node5"}, version=1, parent="column_b", child="node_6"),
                         chain.get_node('node_5'))

        self.assertEqual(ContentNode(id='node_6', content={"test": "Node6"}, version=1, parent="node_5", child=None),
                         chain.get_node('node_6'))

    def test_add_node_to_root(self):
        chain = Board(self.store, 'root')

        node = chain.add_node('new_content', 'root')

        self.assertEqual({'column_a', 'column_b', node.id},
                         self.store.get_node('root').children)
        self.assertEqual(node,
                         self.store.get_node(node.id))

    def test_add_node_to_column_end(self):
        chain = Board(self.store, 'root')

        node = chain.add_node('new_content', 'node_4')

        self.assertEqual(node.id,
                         self.store.get_node('node_4').child)
        self.assertEqual('node_4',
                         node.parent)

    def test_add_node_between_nodes(self):
        chain = Board(self.store, 'root')

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
        chain = Board(self.store, 'root')

        node = chain.move_node("node_2", "node_5")

        self.assertEqual("node_5", self.store.get_node("node_2").parent)
        self.assertEqual("node_2", self.store.get_node("node_5").child)
        self.assertEqual("node_6", self.store.get_node("node_2").child)
        self.assertEqual("node_2", self.store.get_node("node_6").parent)
        self.assertEqual("node_3", self.store.get_node("node_1").child)
        self.assertEqual("node_1", self.store.get_node("node_3").parent)

    def test_edit_node_set_not_exists(self):
        chain = Board(self.store, 'root')

        node = chain.edit_node("node_2", "foo", "bar", "SET")
        self.assertEqual("bar", node.content.get("foo"))
        self.assertEqual("bar", self.store.get_node("node_2").content.get("foo"))

    def test_edit_node_set_exists(self):
        chain = Board(self.store, 'root')

        chain.edit_node("node_2", "foo", "bar", "SET")
        node = chain.edit_node("node_2", "foo", "baz", "SET")
        self.assertEqual("baz", node.content.get("foo"))
        self.assertEqual("baz", self.store.get_node("node_2").content.get("foo"))

    def test_edit_node_incr_not_exists(self):
        chain = Board(self.store, 'root')

        node = chain.edit_node("node_2", "foo", 1, "INCR")
        self.assertEqual(1, node.content.get("foo"))
        self.assertEqual(1, self.store.get_node("node_2").content.get("foo"))

    def test_edit_node_incr_exists(self):
        chain = Board(self.store, 'root')

        chain.edit_node("node_2", "foo", 1, "SET")
        node = chain.edit_node("node_2", "foo", 4, "INCR")
        self.assertEqual(5, node.content.get("foo"))
        self.assertEqual(5, self.store.get_node("node_2").content.get("foo"))

    def test_edit_node_delete_not_exists(self):
        chain = Board(self.store, 'root')

        node = chain.edit_node("node_2", "foo", None, "DELETE")
        self.assertTrue("foo" not in node.content)
        self.assertTrue("foo" not in self.store.get_node("node_2").content)

    def test_edit_node_delete_exists(self):
        chain = Board(self.store, 'root')

        chain.edit_node("node_2", "foo", "bar", "SET")
        node = chain.edit_node("node_2", "foo", None, "DELETE")
        self.assertTrue("foo" not in node.content)
        self.assertTrue("foo" not in self.store.get_node("node_2").content)

    def test_remove_node(self):
        chain = Board(self.store, 'root')

        chain.remove_node("node_2")

        self.assertEqual("node_3", self.store.get_node("node_1").child)
        self.assertEqual("node_1", self.store.get_node("node_3").parent)
