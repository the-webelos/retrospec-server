import threading

from retro.store import Store


class MemStore(Store):
    def __init__(self, nodes=None):
        super(MemStore, self).__init__()
        self.nodes = nodes if nodes else {}
        self.boards = set()
        self.lock = threading.RLock()

    def get_node(self, node_id):
        with self.lock:
            node_dict = self.nodes[node_id].copy()
            node_dict['id'] = node_id

            return self.node_from_dict(node_dict)

    def create_board(self, board_node):
        self.boards.add(board_node.id)
        self.nodes[board_node.id] = board_node.to_dict()

    def remove_board(self, board_id):
        self.boards.remove(board_id)

    def get_board_ids(self):
        return self.boards

    def get_ids_by_type(self, node_type):
        board_ids = []
        for node_id, node in self.nodes.items():
            if node.get("type") == node_type:
                board_ids.append(node_id)

        return board_ids

    def transaction(self, board_id, func):
        with self.lock:
            board_version = self.nodes[board_id]['version']

            read_nodes, update_nodes, remove_nodes = func(self)

            for node in update_nodes:
                node.version = board_version + 1

                #update orig version if needed
                if node.orig_version is None:
                    node.orig_version = node.version

                node_dict = node.to_dict()

                self.nodes[node.id] = node_dict

                self.nodes[board_id]['version'] = board_version + 1

            for node in remove_nodes:
                del self.nodes[node.id]

            return read_nodes, update_nodes, remove_nodes
