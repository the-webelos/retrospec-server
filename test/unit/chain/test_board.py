
import unittest
from backend.retro.store.mem_store import MemStore
from backend.retro.chain.board import Board
from backend.retro.chain.node import ColumnHeaderNode, ContentNode, BoardNode
from backend.retro.chain.operations import SetOperation, IncrementOperation, DeleteOperation


class TestBoard(unittest.TestCase):
    def setUp(self):
        default_nodes = {"root": BoardNode("root", {"test": "RootContent"}, 1, None, {'column_a', 'column_b'}).to_dict(),
                         "column_a": ColumnHeaderNode("column_a", {"test": "ColumnA"}, 1, None, "root", "node_1").to_dict(),
                         "column_b": ColumnHeaderNode("column_b", {"test": "ColumnB"}, 1, None, "root", "node_5").to_dict(),
                         "node_1": ContentNode("node_1", {"test": "Node1"}, 1, None, "column_a", "node_2", "column_a").to_dict(),
                         "node_2": ContentNode("node_2", {"test": "Node2"}, 1, None, "node_1", "node_3", "column_a").to_dict(),
                         "node_3": ContentNode("node_3", {"test": "Node3"}, 1, None, "node_2", "node_4", "column_a").to_dict(),
                         "node_4": ContentNode("node_4", {"test": "Node4"}, 1, None, "node_3", None, "column_a").to_dict(),
                         "node_5": ContentNode("node_5", {"test": "Node5"}, 1, None, "column_b", "node_6", "column_b").to_dict(),
                         "node_6": ContentNode("node_6", {"test": "Node6"}, 1, None, "node_5", None, "column_b").to_dict()}
        self.store = MemStore(default_nodes)

    def test_populate_chain(self):
        chain = Board(self.store, 'root')

        self.assertEqual(9, len(chain.nodes()))

        self.assertEqual(BoardNode('root', content={"test": "RootContent"}, version=1, children={'column_a', 'column_b'}),
                         chain.get_node('root'))

        self.assertEqual(ColumnHeaderNode('column_a', content={"test": "ColumnA"}, version=1, parent="root", child="node_1"),
                         chain.get_node('column_a'))

        self.assertEqual(ContentNode('node_1', content={"test": "Node1"}, version=1, parent="column_a",
                                     child="node_2", column_header="column_a"),
                         chain.get_node('node_1'))

        self.assertEqual(ContentNode('node_2', content={"test": "Node2"}, version=1, parent="node_1",
                                     child="node_3", column_header="column_a"),
                         chain.get_node('node_2'))

        self.assertEqual(ContentNode('node_3', content={"test": "Node3"}, version=1, parent="node_2",
                                     child="node_4", column_header="column_a"),
                         chain.get_node('node_3'))

        self.assertEqual(ContentNode('node_4', content={"test": "Node4"}, version=1, parent="node_3",
                                     child=None, column_header="column_a"),
                         chain.get_node('node_4'))

        self.assertEqual(ColumnHeaderNode('column_b', content={"test": "ColumnB"}, version=1, parent="root", child="node_5"),
                         chain.get_node('column_b'))

        self.assertEqual(ContentNode('node_5', content={"test": "Node5"}, version=1, parent="column_b",
                                     child="node_6", column_header="column_b"),
                         chain.get_node('node_5'))

        self.assertEqual(ContentNode('node_6', content={"test": "Node6"}, version=1, parent="node_5",
                                     child=None, column_header="column_b"),
                         chain.get_node('node_6'))

    def test_add_node_to_root(self):
        chain = Board(self.store, 'root')

        node = chain.add_node('new_content', 'root')

        self.assertEqual({'column_a', 'column_b', node.id},
                         self.store.get_node('root').children)
        self.assertEqual(node.to_dict(),
                         self.store.get_node(node.id).to_dict())

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

    def test_move_node_new_column(self):
        chain = Board(self.store, 'root')

        nodes = chain.move_node("node_2", "node_5")

        self.assertEqual(5, len(nodes))
        self.assertEqual("node_5", self.store.get_node("node_2").parent)
        self.assertEqual("node_2", self.store.get_node("node_5").child)
        self.assertEqual("node_6", self.store.get_node("node_2").child)
        self.assertEqual("node_2", self.store.get_node("node_6").parent)
        self.assertEqual("node_3", self.store.get_node("node_1").child)
        self.assertEqual("node_1", self.store.get_node("node_3").parent)

    def test_move_node_swap_down(self):
        chain = Board(self.store, 'root')

        nodes = chain.move_node("node_1", "node_2")

        self.assertEqual(4, len(nodes))
        self.assertEqual("column_a", self.store.get_node("node_2").parent)
        self.assertEqual("node_1", self.store.get_node("node_2").child)

        self.assertEqual("node_2", self.store.get_node("node_1").parent)
        self.assertEqual("node_3", self.store.get_node("node_1").child)

        self.assertEqual("node_1", self.store.get_node("node_3").parent)
        self.assertEqual("node_4", self.store.get_node("node_3").child)

        self.assertEqual("node_2", self.store.get_node("column_a").child)

    def test_move_node_swap_up(self):
        chain = Board(self.store, 'root')

        nodes = chain.move_node("node_2", "column_a")

        self.assertEqual(4, len(nodes))
        self.assertEqual("column_a", self.store.get_node("node_2").parent)
        self.assertEqual("node_1", self.store.get_node("node_2").child)

        self.assertEqual("node_2", self.store.get_node("node_1").parent)
        self.assertEqual("node_3", self.store.get_node("node_1").child)

        self.assertEqual("node_1", self.store.get_node("node_3").parent)
        self.assertEqual("node_4", self.store.get_node("node_3").child)

        self.assertEqual("node_2", self.store.get_node("column_a").child)

    def test_edit_node_set_not_exists(self):
        chain = Board(self.store, 'root')

        op = SetOperation("foo", "bar")
        node = chain.edit_node("node_2", [op])
        self.assertEqual("bar", node.content.get("foo"))
        self.assertEqual("bar", self.store.get_node("node_2").content.get("foo"))

    def test_edit_node_set_exists(self):
        chain = Board(self.store, 'root')

        chain.edit_node("node_2", [SetOperation("foo", "bar")])
        node = chain.edit_node("node_2", [SetOperation("foo", "baz")])
        self.assertEqual("baz", node.content.get("foo"))
        self.assertEqual("baz", self.store.get_node("node_2").content.get("foo"))

    def test_edit_node_incr_not_exists(self):
        chain = Board(self.store, 'root')

        node = chain.edit_node("node_2", [IncrementOperation("foo", 1)])
        self.assertEqual(1, node.content.get("foo"))
        self.assertEqual(1, self.store.get_node("node_2").content.get("foo"))

    def test_edit_node_incr_exists(self):
        chain = Board(self.store, 'root')

        chain.edit_node("node_2", [IncrementOperation("foo", 1)])
        node = chain.edit_node("node_2", [IncrementOperation("foo", 4)])
        self.assertEqual(5, node.content.get("foo"))
        self.assertEqual(5, self.store.get_node("node_2").content.get("foo"))

    def test_edit_node_delete_not_exists(self):
        chain = Board(self.store, 'root')

        node = chain.edit_node("node_2", [DeleteOperation("foo")])
        self.assertTrue("foo" not in node.content)
        self.assertTrue("foo" not in self.store.get_node("node_2").content)

    def test_edit_node_delete_exists(self):
        chain = Board(self.store, 'root')

        chain.edit_node("node_2", [SetOperation("foo", "bar")])
        node = chain.edit_node("node_2", [DeleteOperation("foo")])
        self.assertTrue("foo" not in node.content)
        self.assertTrue("foo" not in self.store.get_node("node_2").content)

    def test_edit_node_multiple_ops(self):
        chain = Board(self.store, 'root')

        node = chain.edit_node("node_2", [SetOperation("foo", "bar"), SetOperation("baz", "boo")])
        self.assertEqual("bar", node.content['foo'])
        self.assertEqual("boo", node.content['baz'])

    def test_remove_node_column_header(self):
        chain = Board(self.store, 'root')

        chain.remove_node("column_a", True)

        self.assertEqual({"column_b"}, self.store.get_node("root").children)
        with self.assertRaises(KeyError):
            self.store.get_node("column_a")
        with self.assertRaises(KeyError):
            self.store.get_node("node_1")
        with self.assertRaises(KeyError):
            self.store.get_node("node_2")
        with self.assertRaises(KeyError):
            self.store.get_node("node_3")
        with self.assertRaises(KeyError):
            self.store.get_node("node_4")

    def test_remove_node(self):
        chain = Board(self.store, 'root')

        chain.remove_node("node_2", False)

        self.assertEqual("node_3", self.store.get_node("node_1").child)
        self.assertEqual("node_1", self.store.get_node("node_3").parent)

    def test_remove_node_cascade(self):
        chain = Board(self.store, 'root')

        chain.remove_node("node_2", True)

        self.assertEqual(None, self.store.get_node("node_1").child)
        with self.assertRaises(KeyError):
            self.store.get_node("node_2")
        with self.assertRaises(KeyError):
            self.store.get_node("node_3")
        with self.assertRaises(KeyError):
            self.store.get_node("node_4")
