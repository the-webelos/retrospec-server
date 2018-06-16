from backend.retro.chain.exceptions import UnknownNodeTypeError

NODE_REGISTRY = {}


def register_node(cls):
    NODE_REGISTRY[cls.NODE_TYPE] = cls
    return cls


class Node(object):
    NODE_TYPE = 'Node'

    def __init__(self, node_id, content=None, version=1, orig_version=None):
        self.id = node_id
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

        return other.to_dict() == self.to_dict()

    def __hash__(self):
        return hash(((k, v) for k, v in self.to_dict()))

    def __copy__(self):
        return self.copy()

    def _dict_items(self):
        return {}

    def copy(self, **kwargs):
        new_node = self.__class__(self.id)
        new_node.__dict__.update(self.__dict__)
        new_node.__dict__.update(kwargs)

        return new_node

    def to_dict(self):
        d = {"type": self.NODE_TYPE, "id": self.id, "content": self.content, 'version': self.version,
             "orig_version": self.orig_version}
        d.update(self._dict_items())

        return d

    @staticmethod
    def from_dict(node_dict):
        cls = NODE_REGISTRY.get(node_dict["type"])
        if not cls:
            raise UnknownNodeTypeError("Unknown node type: %s" % node_dict['type'])

        return cls(node_dict["id"], **{k: v for k, v in node_dict.items() if k not in ("id", "type")})


@register_node
class BoardNode(Node):
    NODE_TYPE = 'Board'

    def __init__(self, node_id, content=None, version=1, orig_version=None, children=set()):
        super(BoardNode, self).__init__(node_id, content, version, orig_version)
        self.children = set(children)

    def neighbors(self):
        for child in self.children:
            yield child

    def remove_child(self, node_id):
        self.children.remove(node_id)

    def set_child(self, node_id):
        self.children.add(node_id)

    def _dict_items(self):
        return {"children": list(self.children)}


class ParentChildNode(Node):
    NODE_TYPE = 'ParentChild'

    def __init__(self, node_id, content=None, version=1, orig_version=None, parent=None, child=None):
        super(ParentChildNode, self).__init__(node_id, content, version, orig_version)
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

    def _dict_items(self):
        return {"parent": self.parent, "child": self.child}


@register_node
class ContentNode(ParentChildNode):
    NODE_TYPE = 'Content'

    def __init__(self, node_id, content=None, version=1, orig_version=None, parent=None, child=None, column_header=None):
        super(ContentNode, self).__init__(node_id, content, version, orig_version, parent, child)
        self.column_header = column_header

    def _dict_items(self):
        return {"parent": self.parent, "child": self.child, "column_header": self.column_header}


@register_node
class ColumnHeaderNode(ParentChildNode):
    NODE_TYPE = 'ColumnHeader'
