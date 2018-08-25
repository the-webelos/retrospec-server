import json
import logging
from datetime import datetime
from typing import Dict

from retro.chain.board import Board
from retro.chain.node import BoardNode, Node
from retro.store.exceptions import ExistingNodeError
from retro.store.store import Store
from retro.utils import unix_time_millis
from retro.utils.config import Config

_logger = logging.getLogger(__name__)


class BoardEngine(object):
    _default_template = {"id": "empty", "name": "Empty", "description": "Empty template with 0 columns", "columns": []}

    def __init__(self, config: Config, store: Store):
        self.config = config
        self.store = store
        self.templates = self._build_templates(self.config.template_config)

    def get_templates(self):
        return list(self.templates.values())

    def create_board(self, creator: str, template: str=None, content: Dict=None):
        if not content:
            content = {}

        template_def = self.templates[template] if template else {'columns': []}
        board_node = BoardNode(self.store.next_node_id(), content=content)

        # Not a huge fan of setting the time here, but it works for now
        now = unix_time_millis(datetime.now())
        board_node.create_time = now
        board_node.last_update_time = now
        board_node.creator = creator
        self.store.create_board(board_node)

        return self._generate_nodes_from_template(template_def, board_node.id, nodes=[board_node])

    def _generate_nodes_from_template(self, template_def: dict, board_id: str, nodes=None):
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

    def import_board(self, board_dict, child_dicts, copy=False, force=False):
        def _skip_node_transform(*_args, node):
            return node

        transform_func = _skip_node_transform
        board_node = Node.from_dict(board_dict)

        if copy:
            # If we're copying a board, we need to generate a new board_id, and update all the existing ids to
            # reference the new board.
            board_node.id = self.store.next_node_id()
            transform_func = self._copy_node_and_update_ids
            board_node = transform_func(board_node.id, board_node)

        # Create the board. This is done outside of the transaction because redis watches the board_node to ensure the
        # transaction can be executed without race conditions.
        if not force and self.has_board(board_node.id):
            raise ExistingNodeError("Board with id '%s' already exists." % board_node.id)

        self.store.create_board(board_node)
        board = Board(self.store, board_node.id)

        updated_nodes = board.import_nodes(child_dicts, transform_func=transform_func)

        return [self.store.get_node(board_node.id)] + updated_nodes

    def get_board(self, board_id):
        board = Board(self.store, board_id)

        return board.nodes()

    def has_board(self, board_id):
        return self.store.has_board(board_id)

    def delete_board(self, board_id):
        self.store.remove_board(board_id)

        board = Board(self.store, board_id)

        return board.delete()

    def get_boards(self, filters=None, search_terms=None, start=0, count=20, sort_key=None, sort_order=None):
        return self.store.get_boards(filters=filters, search_terms=search_terms,
                                     start=start, count=count,
                                     sort_key=sort_key, sort_order=sort_order)

    def get_node(self, board_id, node_id):
        board = Board(self.store, board_id)
        return board.get_node(node_id)

    def add_node(self, board_id: str, parent_id: str, content: dict=None):
        board = Board(self.store, board_id)

        return board.add_node(content or {}, parent_id)

    def move_node(self, board_id, node_id, new_parent_id):
        board = Board(self.store, board_id)
        return board.move_node(node_id, new_parent_id)

    def edit_node(self, board_id, node_id, operations, lock, unlock):
        board = Board(self.store, board_id)
        node = board.edit_node(node_id, operations, lock, unlock)

        return node

    def remove_node(self, board_id, node_id, cascade=False):
        board = Board(self.store, board_id)
        return board.remove_node(node_id, cascade)

    def update_listener(self, message_cb=lambda *x: True):
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

    @staticmethod
    def _copy_node_and_update_ids(board_id, node):
        def _get_updated_node_id(_node_id):
            parts = _node_id.partition("|")
            return "%s%s%s" % (board_id, parts[1], parts[2])

        new_node = node.copy(version=1, orig_version=None)
        new_node.id = _get_updated_node_id(new_node.id)

        if new_node.parent:
            new_node.parent = _get_updated_node_id(new_node.parent)
        if getattr(new_node, "child", None):
            new_node.child = _get_updated_node_id(new_node.child)
        if getattr(new_node, "children", None):
            new_node.children = {_get_updated_node_id(column_id) for column_id in new_node.children}
        if getattr(new_node, "column_header", None):
            new_node.column_header = _get_updated_node_id(new_node.column_header)

        return new_node
