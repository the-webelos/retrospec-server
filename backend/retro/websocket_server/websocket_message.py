import json
import logging
from backend.retro.websocket_server.exceptions import UnknownMessageType

_logger = logging.getLogger(__name__)


def _ensure_iterable(data):
    try:
        iter(data)
    except TypeError:
        data = [data]

    return data


class WebsocketMessage(object):
    """
    Base class for defining a WebsocketMessage. NOTE subclasses MUST define a class level 'type' variable. Among other
    things, _TYPE_MAP relies on that being statically defined at a class level.
    """
    type = None

    def __init__(self, data):
        self._raw_data = data

    @property
    def data(self):
        return self._raw_data

    def encode(self):
        return json.dumps(self.to_dict())

    @staticmethod
    def decode(message):
        message_dict = json.loads(message)
        message_type = message_dict.get("type")

        try:
            return _TYPE_MAP[message_type](message_dict.get("data"))
        except KeyError as err:
            raise UnknownMessageType("Error decoding websocket message. '%s' is not a known message type." %
                                     message_type) from err

    def to_dict(self):
        return {"type": self.type,
                "data": self._raw_data}


class BoardDeleteMessage(WebsocketMessage):
    type = "board_del"

    def __init__(self, board_id):
        super(BoardDeleteMessage, self).__init__(board_id)

    @property
    def data(self):
        return {"board_id": self._raw_data}


class NodeUpdateMessage(WebsocketMessage):
    type = "node_update"

    def __init__(self, nodes):
        super(NodeUpdateMessage, self).__init__(nodes)

    @property
    def data(self):
        return {"nodes": _ensure_iterable(self._raw_data)}


class NodeDeleteMessage(WebsocketMessage):
    type = "node_del"

    def __init__(self, nodes):
        super(NodeDeleteMessage, self).__init__(nodes)

    @property
    def data(self):
        return {"nodes": _ensure_iterable(self._raw_data)}


class NodeLockMessage(WebsocketMessage):
    type = "node_lock"

    def __init__(self, node_ids):
        super(NodeLockMessage, self).__init__(node_ids)

    @property
    def data(self):
        return {"node_id": _ensure_iterable(self._raw_data)}


class NodeUnlockMessage(WebsocketMessage):
    type = "node_unlock"

    def __init__(self, node_ids):
        super(NodeUnlockMessage, self).__init__(node_ids)

    @property
    def data(self):
        return {"node_id": _ensure_iterable(self._raw_data)}


_TYPE_MAP = {cls.type: cls for cls in WebsocketMessage.__subclasses__()}
