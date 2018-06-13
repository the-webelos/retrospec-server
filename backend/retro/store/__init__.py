from typing import NamedTuple
import uuid


class TransactionNodes(NamedTuple):
    reads: list = []
    updates: list = []
    deletes: list = []
    locks: list = []
    unlocks: list = []


class Store(object):
    @staticmethod
    def next_node_id():
        return str(uuid.uuid4())

    def transaction(self, board_id, func):
        raise NotImplementedError

    def create_board(self, board_node):
        raise NotImplementedError

    def get_node(self, node_id):
        raise NotImplementedError

    def board_update_listener(self, board_id, message_cb=None):
        raise NotImplementedError

    def stop_listener(self, board_id):
        raise NotImplementedError
