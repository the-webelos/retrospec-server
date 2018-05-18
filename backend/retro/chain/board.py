from functools import partial
from retro.chain.node import ColumnHeaderNode, ContentNode
from retro.store import TransactionNodes
from retro.store.exceptions import NodeLockedError, UnlockFailureError


class Board(object):
    def __init__(self, store, board_id):
        self.store = store
        self.board_id = board_id

    def next_node_id(self):
        return "%s|%s" % (self.board_id, self.store.next_node_id())

    def nodes(self):
        nodes = self.store.transaction(self.board_id, partial(self._collect_all))
        return nodes.reads

    def delete(self):
        nodes = self.store.transaction(self.board_id, partial(self._delete_all))
        return nodes.deletes

    def get_node(self, node_id):
        return self.store.get_node(node_id)

    def add_node(self, node_content, parent_id):
        nodes = self.store.transaction(self.board_id, partial(self._add_node, node_content, parent_id))
        return nodes.updates[1]

    def move_node(self, node_id, new_parent_id):
        nodes = self.store.transaction(self.board_id, partial(self._move_node, node_id, new_parent_id))
        return nodes.updates

    def edit_node(self, node_id, operation, lock=None, unlock=None):
        nodes = self.store.transaction(self.board_id, partial(self._edit_node, node_id, operation, lock, unlock))

        return nodes.updates[0]

    def remove_node(self, node_id, cascade):
        if cascade:
            nodes = self.store.transaction(self.board_id, partial(self._cascade_remove_nodes, node_id))
        else:
            nodes = self.store.transaction(self.board_id, partial(self._remove_node, node_id))

        return nodes.deletes

    def _add_node(self, node_content, parent_id, proxy):
        parent = proxy.get_node(parent_id)
        child = None
        new_node_id = self.next_node_id()

        column_header_parent = self._find_first_parent(proxy, parent_id, ColumnHeaderNode.NODE_TYPE)

        if column_header_parent:
            if parent.child:
                child = proxy.get_node(parent.child)
            # we will insert this between parent and child nodes
            node = ContentNode(new_node_id, node_content, parent=parent_id, child=parent.child,
                               column_header=column_header_parent.id)

            parent.set_child(node.id)
            if child:
                child.parent = node.id
        else:
            # Parent is the top of the chain.  We will insert this as a new leaf node.
            node = ColumnHeaderNode(new_node_id, node_content, parent=parent_id)
            parent.set_child(node.id)

        update_nodes = [parent, node, child] if child else [parent, node]

        return TransactionNodes(updates=update_nodes)

    def _move_node(self, node_id, new_parent_id, proxy):
        # A -> B -> C -> D
        #  move node_id B new_parent_id C
        # A new child C
        # B new parent C, new child D
        # C new parent A, new child B}
        # D new parent B
        #
        # OR
        #
        # A -> B -> C -> D -> E
        #  move node_id B new_parent_id D
        # A new child C
        # B new parent D, new child E
        # C new parent A
        # D new child B
        # E new parent B
        #
        # OR
        #
        # A -> B -> C -> D
        #  move node_id C new_parent_id A
        # A new child C
        # B new parent C, new child D
        # C new parent A, new child B}
        # D new parent B

        node = proxy.get_node(node_id)
        old_parent = proxy.get_node(node.parent)
        old_child = proxy.get_node(node.child) if node.child else None
        new_parent = proxy.get_node(new_parent_id)
        new_child = proxy.get_node(new_parent.child) if new_parent.child else None

        if old_parent == new_child:
            old_parent = new_child

        if new_parent == old_child:
            new_parent = old_child

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

        nodes = set([node, new_parent, new_child, old_parent, old_child])
        return TransactionNodes(updates=[node for node in nodes if node is not None])

    def _remove_node(self, node_id, proxy):
        node = proxy.get_node(node_id)
        parent = proxy.get_node(node.parent)
        child = proxy.get_node(node.child) if node.child else None

        parent.remove_child(node_id)
        if child:
            parent.set_child(child.id)
            child.parent = parent.id

        update_nodes = [parent, child] if child else [parent]
        return TransactionNodes(updates=update_nodes, deletes=[node])

    def _cascade_remove_nodes(self, node_id, proxy):
        node = proxy.get_node(node_id)
        parent = proxy.get_node(node.parent)
        parent.remove_child(node_id)

        nodes = self._collect_nodes(proxy, node_id, parent.id)

        return TransactionNodes(updates=[parent], deletes=nodes.values())

    def _edit_node(self, node_id, operation, lock, unlock, proxy):
        node = proxy.get_node(node_id)
        node_lock = proxy.get_node_lock(node_id)
        lock_nodes = []
        unlock_nodes = []

        if node_lock:
            # node is locked
            if unlock:
                # we are trying to unlock the locked node
                if node_lock != unlock:
                    raise UnlockFailureError("Failed to unlock node '%s': %s != %s", node_id, unlock, node_lock)
                unlock_nodes.append(node_id)
            else:
                raise NodeLockedError("Cannot edit locked node '%s'!" % node_id)
        elif lock:
            # node is unlocked and we want to lock it
            lock_nodes.append((node_id, lock))

        # apply operation (SET, INCR, etc) to node
        operation.execute(node)

        return TransactionNodes(updates=[node], locks=lock_nodes, unlocks=unlock_nodes)

    def _collect_all(self, proxy):
        return TransactionNodes(reads=self._collect_nodes(proxy, self.board_id).values())

    def _delete_all(self, proxy):
        return TransactionNodes(deletes=self._collect_nodes(proxy, self.board_id).values())

    def _collect_nodes(self, proxy, root_id, parent_id=None):
        collected = {}
        top = proxy.get_node(root_id)
        collected[top.id] = top

        for node_id in top.neighbors():
            if node_id != parent_id:
                collected.update(self._collect_nodes(proxy, node_id, root_id))

        return collected

    def _find_first_parent(self, proxy, node_id, node_type):
        node = proxy.get_node(node_id)

        if node.NODE_TYPE == node_type:
            return node

        if node.parent:
            return self._find_first_parent(proxy, node.parent, node_type)
        else:
            return None
