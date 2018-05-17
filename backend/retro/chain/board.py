from functools import partial
from retro.chain.node import ColumnHeaderNode, ContentNode


class Board(object):
    def __init__(self, store, board_id):
        self.store = store
        self.board_id = board_id

    def next_node_id(self):
        return "%s|%s" % (self.board_id, self.store.next_node_id())

    def nodes(self):
        nodes, _, _ = self.store.transaction(self.board_id, partial(self._collect_all))
        return nodes

    def delete(self):
        _, _, nodes = self.store.transaction(self.board_id, partial(self._delete_all))
        return nodes

    def get_node(self, node_id):
        return self.store.get_node(node_id)

    def add_node(self, node_content, parent_id):
        _, nodes, _ = self.store.transaction(self.board_id, partial(self._add_node, node_content, parent_id))
        return nodes[1]

    def move_node(self, node_id, new_parent_id):
        _, nodes, _ = self.store.transaction(self.board_id, partial(self._move_node, node_id, new_parent_id))
        return nodes[0]

    def edit_node(self, node_id, operation):
        _, nodes, _ = self.store.transaction(self.board_id, partial(self._edit_node, node_id, operation))

        return nodes[0]

    def remove_node(self, node_id, cascade):
        if cascade:
            _, _, nodes = self.store.transaction(self.board_id, partial(self._cascade_remove_nodes, node_id))
        else:
            _, _, nodes = self.store.transaction(self.board_id, partial(self._remove_node, node_id))

        return nodes

    def _add_node(self, node_content, parent_id, proxy):
        parent = proxy.get_node(parent_id)
        child = None
        new_node_id = self.next_node_id()

        if not parent.parent:
            # Parent is the top of the chain.  We will insert this as a new leaf node.
            node = ColumnHeaderNode(new_node_id, node_content, parent=parent_id)
            parent.set_child(node.id)
        else:
            if parent.child:
                child = proxy.get_node(parent.child)
            # we will insert this between parent and child nodes
            node = ContentNode(new_node_id, node_content, parent=parent_id, child=parent.child)

            parent.set_child(node.id)
            if child:
                child.parent = node.id

        update_nodes = [parent, node, child] if child else [parent, node]

        return [], update_nodes, []

    def _move_node(self, node_id, new_parent_id, proxy):
        node = proxy.get_node(node_id)
        new_parent = proxy.get_node(new_parent_id)
        old_parent = proxy.get_node(node.parent)
        old_child = proxy.get_node(node.child) if node.child else None

        new_child = proxy.get_node(new_parent.child) if new_parent.child else None

        # unlink our moving node from old parent
        old_parent.remove_child(node_id)
        if old_child:
            # unlink old child from our moving node
            node.remove_child(old_child.id)
            old_parent.set_child(old_child.id)
            old_child.parent = old_parent.id

        new_parent.child = node_id
        node.parent = new_parent.id
        if new_child:
            node.set_child(new_child.id)
            new_child.parent = node_id

        nodes = [node, new_parent, new_child, old_parent, old_child]
        return [], [node for node in nodes if node is not None], []

    def _remove_node(self, node_id, proxy):
        node = proxy.get_node(node_id)
        parent = proxy.get_node(node.parent)
        child = proxy.get_node(node.child) if node.child else None

        parent.remove_child(node_id)
        if child:
            parent.set_child(child.id)
            child.parent = parent.id

        update_nodes = [parent, child] if child else [parent]
        return [], update_nodes, [node]

    def _cascade_remove_node(self, node_id, proxy):
        nodes = self._collect_nodes(proxy, node_id)

        parent = proxy.get_node(nodes[node_id].parent)

        parent.remove_child(node_id)

        return [], [parent], nodes

    def _edit_node(self, node_id, operation, proxy):
        node = proxy.get_node(node_id)
        operation.execute(node)

        return [], [node], []

    def _collect_all(self, proxy):
        return self._collect_nodes(proxy, self.board_id).values(), [], []

    def _delete_all(self, proxy):
        return [], [], self._collect_nodes(proxy, self.board_id).values()

    def _collect_nodes(self, proxy, root_id, parent_id=None):
        collected = {}
        top = proxy.get_node(root_id)
        collected[top.id] = top

        for node_id in top.neighbors():
            if node_id != parent_id:
                collected.update(self._collect_nodes(proxy, node_id, root_id))

        return collected
