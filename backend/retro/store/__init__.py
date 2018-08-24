from typing import NamedTuple, List
import uuid


class TransactionNodes(NamedTuple):
    reads: list = []
    updates: list = []
    deletes: list = []
    locks: list = []
    unlocks: list = []


class Group(NamedTuple):
    id: str
    name: str

    def to_dict(self):
        return {'id': self.id, 'name': self.name}


class Store(object):
    @staticmethod
    def next_node_id() -> str:
        return str(uuid.uuid4())

    @staticmethod
    def next_group_id() -> str:
        return str(uuid.uuid4())

    def transaction(self, board_id, func):
        raise NotImplementedError

    def create_board(self, board_node):
        raise NotImplementedError

    def get_node(self, node_id):
        raise NotImplementedError

    def get_group(self, group_id: str) -> Group:
        raise NotImplementedError

    def get_groups(self) -> List[Group]:
        raise NotImplementedError

    def remove_group(self, group_id: str) -> bool:
        raise NotImplementedError

    def upsert_group(self, group_id: str, group_name: str) -> Group:
        raise NotImplementedError

    def board_update_listener(self, board_id, message_cb=None):
        raise NotImplementedError

    def stop_listener(self, board_id):
        raise NotImplementedError
