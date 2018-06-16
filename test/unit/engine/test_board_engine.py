import unittest
from backend.retro.chain.node import Node, BoardNode, ContentNode
from backend.retro.engine.board_engine import BoardEngine
from backend.retro.store.exceptions import ExistingNodeError
from backend.retro.store.mem_store import MemStore
from backend.retro.utils.config import Config


class TestBoardEngine(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestBoardEngine, self).__init__(*args, **kwargs)

        self.config = Config()
        self.store = MemStore()
        self.board_json = {
            "board_node": {
                "type": "Board",
                "id": "712d9667-3816-435e-92f0-4c18d12d7f6c",
                "content": {
                    "name": "2018-May-9 Retrospective | NICOLAS CAGE"
                },
                "version": 488,
                "orig_version": 2,
                "children": ["712d9667-3816-435e-92f0-4c18d12d7f6c|10122d74-44a2-4a90-9d0a-1b2ee6454307",
                             "712d9667-3816-435e-92f0-4c18d12d7f6c|3ecbe0b3-582c-49f4-9bf0-e88eeea5faf7",
                             "712d9667-3816-435e-92f0-4c18d12d7f6c|4f553013-67e1-483e-be62-de1633e6f694"]
            },
            "child_nodes": [{
                "type": "ColumnHeader",
                "id": "712d9667-3816-435e-92f0-4c18d12d7f6c|10122d74-44a2-4a90-9d0a-1b2ee6454307",
                "content": {
                    "name": "What could have gone better?"
                },
                "version": 112,
                "orig_version": 3,
                "parent": "712d9667-3816-435e-92f0-4c18d12d7f6c",
                "child": "712d9667-3816-435e-92f0-4c18d12d7f6c|5db41e80-d186-48cd-bd78-a8b1457ca59f"
            }, {
                "type": "Content",
                "id": "712d9667-3816-435e-92f0-4c18d12d7f6c|5db41e80-d186-48cd-bd78-a8b1457ca59f",
                "content": {
                    "text": "Less meetings please",
                    "votes": 0
                },
                "version": 112,
                "orig_version": 112,
                "parent": "712d9667-3816-435e-92f0-4c18d12d7f6c|10122d74-44a2-4a90-9d0a-1b2ee6454307",
                "child": "712d9667-3816-435e-92f0-4c18d12d7f6c|07a5a54e-0bc2-4bef-a28d-cd58355ee8ec",
                "column_header": "712d9667-3816-435e-92f0-4c18d12d7f6c|10122d74-44a2-4a90-9d0a-1b2ee6454307"
            }, {
                "type": "Content",
                "id": "712d9667-3816-435e-92f0-4c18d12d7f6c|07a5a54e-0bc2-4bef-a28d-cd58355ee8ec",
                "content": {
                    "text": "Support distractions",
                    "votes": 0
                },
                "version": 112,
                "orig_version": 15,
                "parent": "712d9667-3816-435e-92f0-4c18d12d7f6c|5db41e80-d186-48cd-bd78-a8b1457ca59f",
                "child": "712d9667-3816-435e-92f0-4c18d12d7f6c|b3009f02-1970-4d09-a70a-44e3ec0dc43d",
                "column_header": "712d9667-3816-435e-92f0-4c18d12d7f6c|10122d74-44a2-4a90-9d0a-1b2ee6454307"
            }, {
                "type": "Content",
                "id": "712d9667-3816-435e-92f0-4c18d12d7f6c|b3009f02-1970-4d09-a70a-44e3ec0dc43d",
                "content": {
                    "text": "Less production issues",
                    "votes": 0
                },
                "version": 101,
                "orig_version": 10,
                "parent": "712d9667-3816-435e-92f0-4c18d12d7f6c|07a5a54e-0bc2-4bef-a28d-cd58355ee8ec",
                "child": "712d9667-3816-435e-92f0-4c18d12d7f6c|feada774-49ff-4bae-b561-0729060c99dc",
                "column_header": "712d9667-3816-435e-92f0-4c18d12d7f6c|10122d74-44a2-4a90-9d0a-1b2ee6454307"
            }, {
                "type": "Content",
                "id": "712d9667-3816-435e-92f0-4c18d12d7f6c|feada774-49ff-4bae-b561-0729060c99dc",
                "content": {
                    "text": "IT ticket for jumpbox ssh was \"blocked\" for a week, no description as to why",
                    "votes": 0
                },
                "version": 101,
                "orig_version": 9,
                "parent": "712d9667-3816-435e-92f0-4c18d12d7f6c|b3009f02-1970-4d09-a70a-44e3ec0dc43d",
                "child": "712d9667-3816-435e-92f0-4c18d12d7f6c|f2df9df8-5572-42f2-9249-8dca7ea44c24",
                "column_header": "712d9667-3816-435e-92f0-4c18d12d7f6c|10122d74-44a2-4a90-9d0a-1b2ee6454307"
            }, {
                "type": "Content",
                "id": "712d9667-3816-435e-92f0-4c18d12d7f6c|f2df9df8-5572-42f2-9249-8dca7ea44c24",
                "content": {
                    "text": "Research planning",
                    "votes": 0
                },
                "version": 101,
                "orig_version": 16,
                "parent": "712d9667-3816-435e-92f0-4c18d12d7f6c|feada774-49ff-4bae-b561-0729060c99dc",
                "child": None,
                "column_header": "712d9667-3816-435e-92f0-4c18d12d7f6c|10122d74-44a2-4a90-9d0a-1b2ee6454307"
            }, {
                "type": "ColumnHeader",
                "id": "712d9667-3816-435e-92f0-4c18d12d7f6c|3ecbe0b3-582c-49f4-9bf0-e88eeea5faf7",
                "content": {
                    "name": "How can we improve?"
                },
                "version": 429,
                "orig_version": 4,
                "parent": "712d9667-3816-435e-92f0-4c18d12d7f6c",
                "child": "712d9667-3816-435e-92f0-4c18d12d7f6c|0687a95a-7c46-4532-8d6f-3ee117f4087c"
            }, {
                "type": "Content",
                "id": "712d9667-3816-435e-92f0-4c18d12d7f6c|0687a95a-7c46-4532-8d6f-3ee117f4087c",
                "content": {
                    "text": "Team lunch",
                    "votes": 5
                },
                "version": 434,
                "orig_version": 429,
                "parent": "712d9667-3816-435e-92f0-4c18d12d7f6c|3ecbe0b3-582c-49f4-9bf0-e88eeea5faf7",
                "child": "712d9667-3816-435e-92f0-4c18d12d7f6c|a9e40ab6-649a-43a5-bca9-632aef1000c9",
                "column_header": "712d9667-3816-435e-92f0-4c18d12d7f6c|3ecbe0b3-582c-49f4-9bf0-e88eeea5faf7"
            }, {
                "type": "Content",
                "id": "712d9667-3816-435e-92f0-4c18d12d7f6c|a9e40ab6-649a-43a5-bca9-632aef1000c9",
                "content": {
                    "text": "We cannot - we are perfect",
                    "votes": 1
                },
                "version": 488,
                "orig_version": 428,
                "parent": "712d9667-3816-435e-92f0-4c18d12d7f6c|0687a95a-7c46-4532-8d6f-3ee117f4087c",
                "child": "712d9667-3816-435e-92f0-4c18d12d7f6c|5e329634-506e-41a4-8e98-844a3d26fd48",
                "column_header": "712d9667-3816-435e-92f0-4c18d12d7f6c|3ecbe0b3-582c-49f4-9bf0-e88eeea5faf7"
            }, {
                "type": "Content",
                "id": "712d9667-3816-435e-92f0-4c18d12d7f6c|5e329634-506e-41a4-8e98-844a3d26fd48",
                "content": {
                    "text": "Set up a clear vision with Kate for her summer project",
                    "votes": 1
                },
                "version": 428,
                "orig_version": 38,
                "parent": "712d9667-3816-435e-92f0-4c18d12d7f6c|a9e40ab6-649a-43a5-bca9-632aef1000c9",
                "child": "712d9667-3816-435e-92f0-4c18d12d7f6c|ef79b7e9-d3c6-4135-a737-dcbe26cab30f",
                "column_header": "712d9667-3816-435e-92f0-4c18d12d7f6c|3ecbe0b3-582c-49f4-9bf0-e88eeea5faf7"
            }, {
                "type": "Content",
                "id": "712d9667-3816-435e-92f0-4c18d12d7f6c|ef79b7e9-d3c6-4135-a737-dcbe26cab30f",
                "content": {
                    "text": "more dog lovers on the team - less cat lovers. ",
                    "votes": 2
                },
                "version": 487,
                "orig_version": 7,
                "parent": "712d9667-3816-435e-92f0-4c18d12d7f6c|5e329634-506e-41a4-8e98-844a3d26fd48",
                "child": None,
                "column_header": "712d9667-3816-435e-92f0-4c18d12d7f6c|3ecbe0b3-582c-49f4-9bf0-e88eeea5faf7"
            }, {
                "type": "ColumnHeader",
                "id": "712d9667-3816-435e-92f0-4c18d12d7f6c|4f553013-67e1-483e-be62-de1633e6f694",
                "content": {
                    "name": "What went well?"
                },
                "version": 108,
                "orig_version": 2,
                "parent": "712d9667-3816-435e-92f0-4c18d12d7f6c",
                "child": "712d9667-3816-435e-92f0-4c18d12d7f6c|9ca42ac6-2211-46f4-80dc-d4a1097d5d20"
            }, {
                "type": "Content",
                "id": "712d9667-3816-435e-92f0-4c18d12d7f6c|9ca42ac6-2211-46f4-80dc-d4a1097d5d20",
                "content": {
                    "text": "Content discussions",
                    "votes": 0
                },
                "version": 108,
                "orig_version": 108,
                "parent": "712d9667-3816-435e-92f0-4c18d12d7f6c|4f553013-67e1-483e-be62-de1633e6f694",
                "child": "712d9667-3816-435e-92f0-4c18d12d7f6c|d3f3ef6b-df36-418c-9171-f3e25373d816",
                "column_header": "712d9667-3816-435e-92f0-4c18d12d7f6c|4f553013-67e1-483e-be62-de1633e6f694"
            }, {
                "type": "Content",
                "id": "712d9667-3816-435e-92f0-4c18d12d7f6c|d3f3ef6b-df36-418c-9171-f3e25373d816",
                "content": {
                    "text": "Ifrit Onboarding",
                    "votes": 1
                },
                "version": 109,
                "orig_version": 95,
                "parent": "712d9667-3816-435e-92f0-4c18d12d7f6c|9ca42ac6-2211-46f4-80dc-d4a1097d5d20",
                "child": "712d9667-3816-435e-92f0-4c18d12d7f6c|1d070fb4-e77a-45ff-aad5-1d3546295725",
                "column_header": "712d9667-3816-435e-92f0-4c18d12d7f6c|4f553013-67e1-483e-be62-de1633e6f694"
            }, {
                "type": "Content",
                "id": "712d9667-3816-435e-92f0-4c18d12d7f6c|1d070fb4-e77a-45ff-aad5-1d3546295725",
                "content": {
                    "text": "customer beta calls",
                    "votes": 17
                },
                "version": 415,
                "orig_version": 18,
                "parent": "712d9667-3816-435e-92f0-4c18d12d7f6c|d3f3ef6b-df36-418c-9171-f3e25373d816",
                "child": "712d9667-3816-435e-92f0-4c18d12d7f6c|61bde310-d576-4a21-9df9-525090255f06",
                "column_header": "712d9667-3816-435e-92f0-4c18d12d7f6c|4f553013-67e1-483e-be62-de1633e6f694"
            }, {
                "type": "Content",
                "id": "712d9667-3816-435e-92f0-4c18d12d7f6c|61bde310-d576-4a21-9df9-525090255f06",
                "content": {
                    "text": "Lots of good collaboration on feeds",
                    "votes": 1
                },
                "version": 418,
                "orig_version": 8,
                "parent": "712d9667-3816-435e-92f0-4c18d12d7f6c|1d070fb4-e77a-45ff-aad5-1d3546295725",
                "child": "712d9667-3816-435e-92f0-4c18d12d7f6c|3becc494-65fa-4db4-bcd6-77d7db3c9284",
                "column_header": "712d9667-3816-435e-92f0-4c18d12d7f6c|4f553013-67e1-483e-be62-de1633e6f694"
            }, {
                "type": "Content",
                "id": "712d9667-3816-435e-92f0-4c18d12d7f6c|3becc494-65fa-4db4-bcd6-77d7db3c9284",
                "content": {
                    "text": "Progress in discussions with Heisenberg",
                    "votes": 0
                },
                "version": 106,
                "orig_version": 19,
                "parent": "712d9667-3816-435e-92f0-4c18d12d7f6c|61bde310-d576-4a21-9df9-525090255f06",
                "child": "712d9667-3816-435e-92f0-4c18d12d7f6c|2264b880-9521-49a4-b5a0-b7dbe5604afc",
                "column_header": "712d9667-3816-435e-92f0-4c18d12d7f6c|4f553013-67e1-483e-be62-de1633e6f694"
            }, {
                "type": "Content",
                "id": "712d9667-3816-435e-92f0-4c18d12d7f6c|2264b880-9521-49a4-b5a0-b7dbe5604afc",
                "content": {
                    "text": "Query API is tested much better",
                    "votes": 2
                },
                "version": 425,
                "orig_version": 14,
                "parent": "712d9667-3816-435e-92f0-4c18d12d7f6c|3becc494-65fa-4db4-bcd6-77d7db3c9284",
                "child": "712d9667-3816-435e-92f0-4c18d12d7f6c|2e027ac8-0fad-4b93-be91-a79f10ae16a3",
                "column_header": "712d9667-3816-435e-92f0-4c18d12d7f6c|4f553013-67e1-483e-be62-de1633e6f694"
            }, {
                "type": "Content",
                "id": "712d9667-3816-435e-92f0-4c18d12d7f6c|2e027ac8-0fad-4b93-be91-a79f10ae16a3",
                "content": {
                    "text": "We have an intern!",
                    "votes": 0
                },
                "version": 105,
                "orig_version": 17,
                "parent": "712d9667-3816-435e-92f0-4c18d12d7f6c|2264b880-9521-49a4-b5a0-b7dbe5604afc",
                "child": "712d9667-3816-435e-92f0-4c18d12d7f6c|571a21e3-36c8-4d7c-9871-5f10087be2b9",
                "column_header": "712d9667-3816-435e-92f0-4c18d12d7f6c|4f553013-67e1-483e-be62-de1633e6f694"
            }, {
                "type": "Content",
                "id": "712d9667-3816-435e-92f0-4c18d12d7f6c|571a21e3-36c8-4d7c-9871-5f10087be2b9",
                "content": {
                    "text": "Generally finished tasks planned",
                    "votes": 0,
                    "blur": False
                },
                "version": 427,
                "orig_version": 12,
                "parent": "712d9667-3816-435e-92f0-4c18d12d7f6c|2e027ac8-0fad-4b93-be91-a79f10ae16a3",
                "child": "712d9667-3816-435e-92f0-4c18d12d7f6c|94ffbefc-20d9-492f-95f9-c7953565d5a9",
                "column_header": "712d9667-3816-435e-92f0-4c18d12d7f6c|4f553013-67e1-483e-be62-de1633e6f694"
            }, {
                "type": "Content",
                "id": "712d9667-3816-435e-92f0-4c18d12d7f6c|94ffbefc-20d9-492f-95f9-c7953565d5a9",
                "content": {
                    "text": "Lot of collaboration on wireframes, lot of people getting involved",
                    "votes": 0
                },
                "version": 103,
                "orig_version": 13,
                "parent": "712d9667-3816-435e-92f0-4c18d12d7f6c|571a21e3-36c8-4d7c-9871-5f10087be2b9",
                "child": None,
                "column_header": "712d9667-3816-435e-92f0-4c18d12d7f6c|4f553013-67e1-483e-be62-de1633e6f694"
            }]
        }

        self.board_node = Node.from_dict(self.board_json.get("board_node"))
        self.child_nodes = [Node.from_dict(node_dict) for node_dict in self.board_json.get("child_nodes")]

    def test_import_board(self):
        board_engine = BoardEngine(self.config, store=self.store)
        board_node, child_nodes = self.board_json.get("board_node"), self.board_json.get("child_nodes")

        expected_nodes = [board_node] + child_nodes
        created_nodes = board_engine.import_board(board_node, child_nodes, copy=False)

        self._test_import_board(expected_nodes, created_nodes)

    def test_import_board_with_existing_data(self):
        store = MemStore(nodes={node.id: node for node in self.child_nodes})
        store.create_board(self.board_node)
        board_engine = BoardEngine(self.config, store=store)
        with self.assertRaises(ExistingNodeError):
            board_engine.import_board(self.board_json.get("board_node"), self.board_json.get("child_nodes"))

    def test_import_board_with_existing_data_force(self):
        store = MemStore(nodes={node.id: node for node in self.child_nodes})
        store.create_board(self.board_node)
        board_engine = BoardEngine(self.config, store=store)

        board_node, child_nodes = self.board_json.get("board_node"), self.board_json.get("child_nodes")
        expected_nodes = [board_node] + child_nodes
        created_nodes = board_engine.import_board(board_node, child_nodes, force=True)

        self._test_import_board(expected_nodes, created_nodes)

    def test_import_board_with_copy(self):
        board_engine = BoardEngine(self.config, store=self.store)
        board_node, child_nodes = self.board_json.get("board_node"), self.board_json.get("child_nodes")

        expected_nodes = [board_node] + child_nodes
        created_nodes = board_engine.import_board(board_node, child_nodes, copy=True)
        orig_board_id = board_node["id"]
        new_board_id = created_nodes[0].id

        self.assertEqual(len(expected_nodes), len(created_nodes))
        self.assertNotEqual(orig_board_id, new_board_id)

        for i, node in enumerate(created_nodes):
            expected_node = Node.from_dict(expected_nodes[i])

            self.assertTrue(node.id.startswith(new_board_id))
            self.assertEqual(expected_node.NODE_TYPE, node.NODE_TYPE)
            self.assertEqual(expected_node.content, node.content)
            self.assertEqual(node.version, 2)

            if node.NODE_TYPE == BoardNode.NODE_TYPE:
                self.assertEqual(len(expected_node.children), len(node.children))
                for child in node.children:
                    self.assertTrue(child.startswith(new_board_id))
            else:
                self.assertTrue(node.parent.startswith(new_board_id))
                if expected_node.child is None:
                    self.assertIsNone(node.child)
                else:
                    self.assertTrue(node.child.startswith(new_board_id))

                if node.NODE_TYPE == ContentNode:
                    self.assertTrue(node.column_header.startswith(new_board_id))

    def _test_import_board(self, expected_nodes, created_nodes):
        self.assertEqual(len(expected_nodes), len(created_nodes))
        for i, node in enumerate(created_nodes):
            expected_node = Node.from_dict(expected_nodes[i])

            self.assertEqual(expected_node.id, node.id)
            self.assertEqual(expected_node.NODE_TYPE, node.NODE_TYPE)
            self.assertEqual(expected_node.content, node.content)
            self.assertEqual(expected_node.parent, node.parent)
            self.assertEqual(489, node.version)

            if node.NODE_TYPE == BoardNode.NODE_TYPE:
                self.assertSetEqual(expected_node.children, node.children)
            else:
                self.assertEqual(expected_node.child, node.child)
                if node.NODE_TYPE == ContentNode:
                    self.assertEqual(expected_node.column_header, node.column_header)
