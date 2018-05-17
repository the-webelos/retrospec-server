import json
import logging

from retro.chain.board import Board
from retro.chain.node import BoardNode
from retro.utils import get_store

_logger = logging.getLogger(__name__)


class BoardEngine(object):
    def __init__(self, config, store=None):
        self.config = config
        self.store = store if store else get_store(config)

        self.templates = self._build_templates(self.config.template_config)

    def create_board(self, name, template=None):
        board_node = BoardNode(self.store.next_node_id(), content={"name": name})
        self.store.create_board(board_node)

        nodes = [board_node]
        template_def = self.templates[template] if template else {'columns': []}

        for column in template_def['columns']:
            nodes.append(self.add_node(board_node.id, board_node.id, {'name': column}))

        return nodes

    def get_board(self, board_id):
        board = Board(self.store, board_id)

        return board.nodes()

    def has_board(self, board_id):
        return board_id in self.store.get_board_ids()

    def delete_board(self, board_id):
        self.store.remove_board(board_id)

        board = Board(self.store, board_id)

        return board.delete()

    def get_boards(self):
        boards = []
        for id in self.store.get_board_ids():
            boards.append(self.store.get_node(id))

        return boards

    def add_node(self, board_id, parent_id, content=None):
        board = Board(self.store, board_id)

        return board.add_node(content or {}, parent_id)

    def move_node(self, board_id, node_id, new_parent_id):
        board = Board(self.store, board_id)
        return board.move_node(node_id, new_parent_id)

    def edit_node(self, board_id, node_id, operation):
        board = Board(self.store, board_id)
        return board.edit_node(node_id, operation)

    def remove_node(self, board_id, node_id, cascade=False):
        board = Board(self.store, board_id)
        return board.remove_node(node_id, cascade)

    def subscribe_board(self, board_id, message_cb=lambda x: x):
        self.store.board_update_listener(board_id, message_cb=message_cb)

    def unsubscribe_board(self, board_id):
        self.store.stop_listener(board_id)

    def _build_templates(self, template_config):
        templates = {}
        try:
            with open(template_config) as f:
                for line in f:
                    line = line.strip(' ')
                    if line.startswith('#'):
                        continue

                    parts = line.partition('=')
                    try:
                        templates[parts[0]] = json.loads(parts[2])
                    except:
                        pass
        except:
            _logger.exception("Error parsing templates")

        return templates

