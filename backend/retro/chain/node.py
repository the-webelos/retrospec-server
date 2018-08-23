from retro.chain.exceptions import UnknownNodeTypeError

NODE_ID_KEY = "id"
NODE_TYPE_KEY = "type"
CONTENT_KEY = "content"
VERSION_KEY = "version"
ORIG_VERSION_KEY = "orig_version"
CREATOR_KEY = "creator"
CREATE_TIME_KEY = "create_time"
LAST_UPDATE_TIME_KEY = "last_update_time"
CHILDREN_KEY = "children"
PARENT_KEY = "parent"
CHILD_KEY = "child"
COLUMN_HEADER_KEY = "column_header"

_NODE_REGISTRY = {}


def register_node(cls):
    _NODE_REGISTRY[cls.NODE_TYPE] = cls
    return cls


class Node(object):
    NODE_TYPE = 'Node'
    INDEX_FIELDS = []

    def __init__(self, node_id, content=None, version=1, orig_version=None,
                 creator=None, create_time=None, last_update_time=None, **kwargs):
        self.id = node_id
        self.content = content
        self.version = version
        self.orig_version = orig_version
        self.creator = creator
        self.create_time = create_time
        self.last_update_time = last_update_time
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
        d = {
            NODE_TYPE_KEY: self.NODE_TYPE,
            NODE_ID_KEY: self.id,
            CONTENT_KEY: self.content,
            VERSION_KEY: self.version,
            ORIG_VERSION_KEY: self.orig_version,
            CREATOR_KEY: self.creator,
            CREATE_TIME_KEY: self.create_time,
            LAST_UPDATE_TIME_KEY: self.last_update_time
        }
        d.update(self._dict_items())

        return d

    @staticmethod
    def from_dict(node_dict):
        cls = _NODE_REGISTRY.get(node_dict[NODE_TYPE_KEY])
        if not cls:
            raise UnknownNodeTypeError("Unknown node type: %s" % node_dict[NODE_TYPE_KEY])

        # Ignore id because we already passed it in, and ignore type because it's inferred by the class type
        return cls(node_dict[NODE_ID_KEY], **{k: v for k, v in node_dict.items()
                                              if k not in (NODE_ID_KEY, NODE_TYPE_KEY)})

    def to_index_dict(self):
        d = {}

        for field in self.INDEX_FIELDS:
            val = getattr(self, field)
            if val is not None:
                d[field] = val

        return d


@register_node
class BoardNode(Node):
    NODE_TYPE = 'Board'
    INDEX_FIELDS = [NODE_ID_KEY, CREATOR_KEY, CREATE_TIME_KEY, LAST_UPDATE_TIME_KEY, CONTENT_KEY]

    def __init__(self, node_id, children=set(), **kwargs):
        super(BoardNode, self).__init__(node_id, **kwargs)
        self.children = set(children)

    def neighbors(self):
        for child in self.children:
            yield child

    def remove_child(self, node_id):
        self.children.remove(node_id)

    def set_child(self, node_id):
        self.children.add(node_id)

    def _dict_items(self):
        return {CHILDREN_KEY: list(self.children)}


class ParentChildNode(Node):
    NODE_TYPE = 'ParentChild'

    def __init__(self, node_id, parent=None, child=None, **kwargs):
        super(ParentChildNode, self).__init__(node_id, **kwargs)
        self.parent = parent
        self.child = child

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
        return {PARENT_KEY: self.parent, CHILD_KEY: self.child}


@register_node
class ContentNode(ParentChildNode):
    NODE_TYPE = 'Content'

    def __init__(self, node_id, column_header=None, **kwargs):
        super(ContentNode, self).__init__(node_id, **kwargs)
        self.column_header = column_header

    def _dict_items(self):
        return {PARENT_KEY: self.parent, CHILD_KEY: self.child, COLUMN_HEADER_KEY: self.column_header}


@register_node
class ColumnHeaderNode(ParentChildNode):
    NODE_TYPE = 'ColumnHeader'
