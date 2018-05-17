class Node(object):
    NODE_TYPE = 'Node'

    def __init__(self, id, content=None, version=1, orig_version=None):
        self.id = id
        self.content = content
        self.version = version
        self.orig_version = orig_version
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
        d = {"type": self.NODE_TYPE, "id": self.id, "content": self.content, 'version': self.version,
             "orig_version": self.orig_version}
        d.update(self._dict_items())

        return d


class BoardNode(Node):
    NODE_TYPE = 'Board'

    def __init__(self, id, content=None, version=1, orig_version=None, children=set()):
        super(BoardNode, self).__init__(id, content, version, orig_version)
        self.children = set(children)

    def neighbors(self):
        for child in self.children:
            yield child

    def remove_child(self, node_id):
        self.children.remove(node_id)

    def set_child(self, node_id):
        self.children.add(node_id)

    def __eq__(self, other):
        if not isinstance(other, BoardNode):
            return False

        return other.id == self.id and other.content == self.content and other.children == self.children

    def _dict_items(self):
        return {"children": list(self.children)}


class ParentChildNode(Node):
    NODE_TYPE = 'ParentChild'

    def __init__(self, id, content=None, version=1, orig_version=None, parent=None, child=None):
        super(ParentChildNode, self).__init__(id, content, version, orig_version)
        self.parent=parent
        self.child=child

    def remove_child(self, node_id):
        if self.child == node_id:
            self.child = None

    def set_child(self, node_id):
        self.child = node_id

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


class ContentNode(ParentChildNode):
    NODE_TYPE = 'Content'

    def __init__(self, id, content=None, version=1, orig_version=None, parent=None, child=None, column_header=None):
        super(ContentNode, self).__init__(id, content, version, orig_version, parent, child)
        self.column_header = column_header

    def __eq__(self, other):
        if not isinstance(other, ContentNode):
            return False

        return other.id == self.id and other.content == self.content and other.version == self.version \
                and other.parent == self.parent and other.child == self.child \
                and other.column_header == self.column_header

    def _dict_items(self):
        return {"parent": self.parent, "child": self.child, "column_header": self.column_header}


class ColumnHeaderNode(ParentChildNode):
    NODE_TYPE = 'ColumnHeader'

    def __eq__(self, other):
        if not isinstance(other, ColumnHeaderNode):
            return False

        return other.id == self.id and other.content == self.content and other.version == self.version \
               and other.parent == self.parent and other.child == self.child

