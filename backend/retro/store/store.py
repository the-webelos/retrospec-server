import uuid
from typing import NamedTuple, List, Dict, Callable
from retro.chain.node import Node, BoardNode


class TransactionNodes(NamedTuple):
    reads: list = []
    updates: list = []
    deletes: list = []
    locks: list = []
    unlocks: list = []


class Group(NamedTuple):
    id: str
    name: str

    def to_dict(self) -> Dict:
        return {'id': self.id, 'name': self.name}


class Store(object):
    @staticmethod
    def next_node_id() -> str:
        return str(uuid.uuid4())

    @staticmethod
    def next_group_id() -> str:
        return str(uuid.uuid4())

    def transaction(self, board_id: str, func: Callable) -> List[Node]:
        raise NotImplementedError

    def create_board(self, board_node: BoardNode) -> None:
        raise NotImplementedError

    def remove_board(self, board_id: str) -> None:
        raise NotImplementedError

    def get_boards(self, filters: Dict=None, search_terms: Dict=None,
                   start: int=0, count: int=20,
                   sort_key: str=None, sort_order: str=None) -> List[Dict]:
        raise NotImplementedError

    def has_board(self, board_id: str) -> bool:
        raise NotImplementedError

    def get_node(self, node_id: str) -> Node:
        raise NotImplementedError

    def get_group(self, group_id: str) -> Group:
        raise NotImplementedError

    def get_groups(self) -> List[Group]:
        raise NotImplementedError

    def remove_group(self, group_id: str) -> bool:
        raise NotImplementedError

    def upsert_group(self, group_id: str, group_name: str) -> Group:
        raise NotImplementedError

    def update_listener(self, message_cb: Callable=None) -> None:
        raise NotImplementedError
