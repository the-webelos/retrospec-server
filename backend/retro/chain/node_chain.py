import uuid
from functools import partial


class Node(object):
    NODE_TYPE = 'Node'

    def __init__(self, id, content=None, version=1):
        self.id = id
        self.content = content
        self.version = version
        self.parent = None

    def neighbors(self):
        raise NotImplementedError

    def __str__(self):
        return "%s|%s|%s" % (self.id, self.content, self.version)

    def __eq__(self, other):
        if not isinstance(other, Node):
            return False

        return other.id == self.id and other.content == self.content and self.version == other.version

    def _dict_items(self):
        return {}

    def to_dict(self):
        d = {"type": self.NODE_TYPE, "id": self.id, "content": self.content, 'version': self.version}
        d.update(self._dict_items())

        return d


class RootNode(Node):
    NODE_TYPE = 'Root'

    def __init__(self, id, content=None, version=1, children=list()):
        super(RootNode, self).__init__(id, content, version)
        self.children = children

    def neighbors(self):
        for child in self.children:
            yield child

    def __eq__(self, other):
        if not isinstance(other, RootNode):
            return False

        return other.id == self.id and other.content == self.content and other.children == self.children

    def _dict_items(self):
        return {"children": self.children}


class ContentNode(Node):
    NODE_TYPE = 'Content'

    def __init__(self, id, content=None, version=1, parent=None, child=None):
        super(ContentNode, self).__init__(id, content, version)
        self.parent=parent
        self.child=child

    def neighbors(self):
        if self.parent:
            yield self.parent
        if self.child:
            yield self.child

    def __eq__(self, other):
        if not isinstance(other, ContentNode):
            return False

        return other.id == self.id and other.content == self.content and other.version == self.version \
                and other.parent == self.parent and other.child == self.child

    def _dict_items(self):
        return {"parent": self.parent, "child": self.child}


class ColumnHeaderNode(ContentNode):
    NODE_TYPE = 'ColumnHeader'

    def __init__(self, id, content=None, version=1, order=None, parent=None, child=None):
        super(ColumnHeaderNode, self).__init__(id, content, version, parent, child)
        self.order = order

    def __eq__(self, other):
        if not isinstance(other, ColumnHeaderNode):
            return False

        return other.id == self.id and other.content == self.content and other.version == self.version \
                and other.parent == self.parent and other.child == self.child and other.order == self.order

    def _dict_items(self):
        return {"parent": self.parent, "child": self.child, "order": self.order}


class NodeChain(object):
    def __init__(self, store, board_id=None):
        self.store = store
        if not board_id:
            self.board_id = self.store.next_node_id()
            self.store.create_board(RootNode(self.board_id, content=""))
        self.board_id = board_id

    def nodes(self):
        return self._collect_nodes(self.board_id)

    def get_node(self, node_id):
        return self.store.get_node(node_id)

    def add_node(self, node_content, parent_id):
        nodes = self.store.transaction(self.board_id, partial(self._add_node, node_content, parent_id))
        return nodes[1]

    def move_node(self, node_id, new_parent_id):
        nodes = self.store.transaction(self.board_id, partial(self._move_node, node_id, new_parent_id))
        return nodes[0]

    def remove_node(self, node_id):
        nodes = self.store.transaction(self.board_id, )
    def _add_node(self, node_content, parent_id, proxy):
        parent = proxy.get_node(parent_id)
        child = None

        if not parent.parent:
            # Parent is the top of the chain.  We will insert this as a new leaf node.
            node = ColumnHeaderNode(uuid.uuid4(), node_content, 1, parent_id)
            parent.children.append(node.id)
        else:
            if parent.child:
                child = proxy.get_node(parent.child)
            # we will insert this between parent and child nodes
            node = ContentNode(uuid.uuid4(), node_content, 1, parent_id, parent.child)

            parent.child = node.id
            if child:
                child.parent = node.id

        return [parent, node, child] if child else [parent, node]

    def _move_node(self, node_id, new_parent_id, proxy):
        node = proxy.get_node(node_id)
        new_parent = proxy.get_node(new_parent_id)
        old_parent = proxy.get_node(node.parent)
        old_child = proxy.get_node(node.child) if node.child else None

        new_child = proxy.get_node(new_parent.child) if new_parent.child else None

        if old_child:
            old_parent.child = old_child.id
            old_child.parent = old_parent.id
        else:
            old_parent.child = None

        new_parent.child = node_id
        node.parent = new_parent.id
        if new_child:
            node.child = new_child.id
            new_child.parent = node_id
        else:
            node.child = None

        nodes = [node, new_parent, new_child, old_parent, old_child]
        return [node for node in nodes if node is not None]

    def _collect_nodes(self, root_id, parent_id=None):
        collected = {}
        top = self.store.get_node(root_id)
        collected[top.id] = top

        for node_id in top.neighbors():
            if node_id != parent_id:
                collected.update(self._collect_nodes(node_id, root_id))

        return collected
