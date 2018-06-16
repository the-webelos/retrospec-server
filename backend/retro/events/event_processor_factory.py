from backend.retro.events.exceptions import UnknownEventError
from backend.retro.store.exceptions import NodeParseError
from backend.retro.websocket_server.websocket_message import WebsocketMessage, NodeUnlockMessage


class EventProcessorFactory(object):
    """
    The responsibility of this factory is to take a redis event, and return an appropriate EventProcessor that will be
    used to handle that event. In many cases, this means decoding and turning it into an instance of WebsocketMessage
    that the passed in message_cb can consume and emit.
    """
    @staticmethod
    def get_event_processor(event, message_cb=lambda *x: True):
        processor = None
        channel = event['channel']

        if channel.endswith('__:expired'):
            if event['data'].startswith('NODELOCK.'):
                processor = ExpiredLockProcessor(event, message_cb)
        elif channel.startswith('board_update|'):
            processor = BoardUpdateProcessor(event, message_cb)

        if not processor:
            raise UnknownEventError("No known processor for event '%s'." % event)

        return processor


class EventProcessorBase(object):
    def __init__(self, event, message_cb):
        self.event = event
        self.message_cb = message_cb

    def process(self):
        raise NotImplementedError("Subclass must implement process method!")


class ExpiredLockProcessor(EventProcessorBase):
    def __init__(self, *args, **kwargs):
        super(ExpiredLockProcessor, self).__init__(*args, **kwargs)

    def process(self):
        return self.message_cb(*self.__parse_key_expired_event())

    def __parse_key_expired_event(self):
        # Because this event was published by redis instead of our API, event['data'] is not a serialized instance of
        # WebsocketMessage, and therefore we cannot simply call WebsocketMessage.decode(). Instead, we create a new
        # NodeUnlockMessage using the data inside the redis event, which in this case will be the NODELOCK key that was
        # deleted.
        node_id = self.event['data'].partition('NODELOCK.')[2]
        if node_id:
            # If the node_id does not contain a '|', that means it's either a board id or just bad data. We don't have
            # board locking implemented in the UI, but if we ever wanted it, this code should just work. The split won't
            # find a '|' in that case, so the resulting board_id will be equal to the node_id. We don't really care if
            # it's bad data because if the board_id doesn't exist, then no boards will be negatively impacted.
            board_id = node_id.split('|')[0]
            message = NodeUnlockMessage([node_id])
            return message, board_id
        else:
            raise NodeParseError("Error parsing node lock expiration event '%s'." % self.event.get('data'))


class BoardUpdateProcessor(EventProcessorBase):
    def __init__(self, *args, **kwargs):
        super(BoardUpdateProcessor, self).__init__(*args, **kwargs)

    def process(self):
        # Decode the previously serialized WebsocketMessage from event['data'] and pass it to the message_cb to be
        # emitted.
        board_id = self.event['channel'].partition('|')[2]
        return self.message_cb(WebsocketMessage.decode(self.event['data']), board_id)
