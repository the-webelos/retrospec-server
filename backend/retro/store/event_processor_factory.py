import json
from retro.store.exceptions import UnknownEventError


class EventProcessorFactory(object):
    @staticmethod
    def get_event_processor(event, message_cb=lambda x: True):
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
        board_id = self.__parse_key_expired_event()
        return self.message_cb(self.event, board_id)

    def __parse_key_expired_event(self):
        node_ids = self.event['data'].partition('NODELOCK.')[2].split('|')
        if len(node_ids) == 2:
            board_id, node_id = node_ids
            self.event['data'] = json.dumps({'event_type': 'node_unlock',
                                             'event_data': [node_id]})
            return board_id
        else:
            raise Exception("Error parsing node lock expiration event '%s'." % self.event['data'])


class BoardUpdateProcessor(EventProcessorBase):
    def __init__(self, *args, **kwargs):
        super(BoardUpdateProcessor, self).__init__(*args, **kwargs)

    def process(self):
        board_id = self.event['channel'].partition('|')[2]
        return self.message_cb(self.event, board_id)
