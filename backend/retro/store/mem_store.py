import threading

from retro.store import Store


class MemStore(Store):
    def __init__(self, nodes):
        self.nodes = nodes
        self.lock = threading.RLock()

    def get_node(self, node_id):
        with self.lock:
            node_dict = self.nodes[node_id].copy()
            node_dict['id'] = node_id

            return self.node_from_dict(node_dict)

    def create_board(self, board_node):
        self.nodes[board_node.id] = board_node.to_dict()

    def transaction(self, board_id, func):
        with self.lock:
            board_version = self.nodes[board_id]['version']

            update_nodes, remove_nodes = func(self)

            for node in update_nodes:
                node.version = board_version + 1
                node_dict = node.to_dict()

                self.nodes[node.id] = node_dict

                self.nodes[board_id]['version'] = board_version + 1

            for node in remove_nodes:
                del self.nodes[node.id]

            return update_nodes
