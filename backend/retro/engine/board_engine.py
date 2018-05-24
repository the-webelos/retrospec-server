import json
import logging

from retro.chain.board import Board
from retro.chain.node import BoardNode
from retro.utils import get_store

_logger = logging.getLogger(__name__)


class BoardEngine(object):
    _default_template = {"id": "empty", "name": "Empty", "description": "Empty template with 0 columns", "columns": []}

    def __init__(self, config, store=None):
        self.config = config
        self.store = store if store else get_store(config)

        self.config.template_config = "/home/jlorusso/dev/retrospec-server/backend/conf/templates.cfg"
        self.templates = self._build_templates(self.config.template_config)

    def get_templates(self):
        return list(self.templates.values())

    def create_board(self, name, template=None):
        template_def = self.templates[template] if template else {'columns': []}
        board_node = BoardNode(self.store.next_node_id(), content={"name": name})
        self.store.create_board(board_node)

        return self._generate_nodes_from_template(template_def, board_node.id, nodes=[board_node])

    def _generate_nodes_from_template(self, template_def, board_id, nodes=None):
        nodes = nodes or []

        def _add_node(_parent_id, content):
            n = self.add_node(board_id, _parent_id, content=content)
            nodes.append(n)
            return n.id

        for column_dict in template_def['columns']:
            # Allow users to provide column names as a list of strings if they want to.
            if isinstance(column_dict, str):
                column_dict = {"name": column_dict}
            parent_id = _add_node(board_id, {'name': column_dict.get("name")})
            for node_content in column_dict.get("nodes", []):
                parent_id = _add_node(parent_id, node_content)

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

    def get_boards(self, start=0, rows=20):
        boards = []
        for board_id in self.store.get_board_ids():
            boards.append(self.store.get_node(board_id))

        return boards

    def add_node(self, board_id, parent_id, content=None):
        board = Board(self.store, board_id)

        return board.add_node(content or {}, parent_id)

    def move_node(self, board_id, node_id, new_parent_id):
        board = Board(self.store, board_id)
        return board.move_node(node_id, new_parent_id)

    def edit_node(self, board_id, node_id, operations, lock, unlock):
        board = Board(self.store, board_id)
        return board.edit_node(node_id, operations, lock, unlock)

    def remove_node(self, board_id, node_id, cascade=False):
        board = Board(self.store, board_id)
        return board.remove_node(node_id, cascade)

    def update_listener(self, message_cb=lambda x: x):
        self.store.update_listener(message_cb=message_cb)

    def _build_templates(self, template_config):
        templates = {self._default_template['id']: self._default_template}

        if template_config:
            try:
                with open(template_config) as f:
                    for line in f:
                        line = line.strip(' ')
                        if line.startswith('#'):
                            continue

                        try:
                            template = json.loads(line)
                            templates[template['id']] = template
                        except:
                            _logger.warning("Unable to load template: %s", line)
            except:
                _logger.exception("Error parsing templates")

        return templates

