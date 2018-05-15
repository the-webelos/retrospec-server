from retro.chain.board import Board
from retro.chain.node import BoardNode
from retro.utils import get_store


class BoardEngine(object):
    def __init__(self, config, store=None):
        self.config = config
        self.store = store if store else get_store(config)

    def create_board(self, name):
        board_node = BoardNode(self.store.next_node_id(), content={"name": name})
        self.store.create_board(board_node)

        return board_node

    def get_all_boards(self):
        boards = {}
        for board_id in self.store.get_ids_by_type(BoardNode.NODE_TYPE):
            board_nodes = self.get_board(board_id)
            dict_nodes = [node.to_dict() for node in board_nodes.values()]
            boards[board_id] = dict_nodes

        return boards

    def get_board(self, board_id):
        board = Board(self.store, board_id)

        return board.nodes()

    def add_node(self, board_id, parent_id, content=None):
        board = Board(self.store, board_id)

        return board.add_node(content or {}, parent_id)

    def move_node(self, board_id, node_id, new_parent_id):
        board = Board(self.store, board_id)
        return board.move_node(node_id, new_parent_id)

    def edit_node(self, board_id, node_id, field, value, op):
        board = Board(self.store, board_id)
        return board.edit_node(node_id, field, value, op)

    def remove_node(self, board_id, node_id):
        board = Board(self.store, board_id)
        return board.remove_node(node_id)
