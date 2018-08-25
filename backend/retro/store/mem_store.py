import threading

from typing import List
from retro.chain.node import Node
from retro.store.store import Store, Group


class MemStore(Store):
    def __init__(self, nodes=None):
        super(MemStore, self).__init__()
        self.nodes = nodes if nodes else {}
        self.boards = set()
        self.groups = dict()
        self.lock = threading.RLock()
        self.node_locks = dict()

    def get_node(self, node_id):
        with self.lock:
            node_dict = self.nodes[node_id].copy()
            node_dict['id'] = node_id

            return Node.from_dict(node_dict)

    def get_node_lock(self, node_id):
        return self.node_locks.get(node_id)

    def create_board(self, board_node):
        self.boards.add(board_node.id)
        self.nodes[board_node.id] = board_node.to_dict()

    def remove_board(self, board_id):
        self.boards.remove(board_id)

    def get_ids_by_type(self, node_type):
        board_ids = []
        for node_id, node in self.nodes.items():
            if node.get("type") == node_type:
                board_ids.append(node_id)

        return board_ids

    def get_groups(self) -> List[Group]:
        return [Group(k, v) for k, v in self.groups.items()]

    def get_group(self, group_id: str) -> Group:
        name = self.groups.get(group_id)

        if not name:
            raise KeyError("Unknown group '%s'" % group_id)

        return Group(group_id, name)

    def upsert_group(self, group_id, name) -> Group:
        self.groups[group_id] = name

        return Group(group_id, name)

    def remove_group(self, group_id) -> bool:
        return self.groups.pop(group_id, None) is not None

    def board_update_listener(self, board_id, message_cb=lambda *x: True):
        pass

    def stop_listener(self, board_id):
        pass

    def transaction(self, board_id, func):
        with self.lock:
            nodes = func(self)

            board_version = self.nodes[board_id]['version']

            if nodes.updates or nodes.deletes or nodes.locks or nodes.unlocks:
                for node in nodes.deletes:
                    del self.nodes[node.id]

                for node in nodes.updates:
                    node.version = board_version + 1

                    # update orig version if needed
                    if node.orig_version is None:
                        node.orig_version = node.version

                    node_dict = node.to_dict()

                    self.nodes[node.id] = node_dict

                for node_id, lock_val in nodes.locks:
                    self.node_locks[node_id] = lock_val

                for node_id in nodes.unlocks:
                    self.node_locks.pop(node_id, None)

                # update board version
                self.nodes[board_id]['version'] += 1

            return nodes
