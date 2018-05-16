import threading

import redis

client = redis.StrictRedis(host='localhost', port=6379, encoding='utf-8', decode_responses=True)

def subscribe_board(board_id):
    p = client.pubsub()
    p.psubscribe('%s*' % board_id)

    for event in p.listen():
        if event['type'] == 'pmessage':
            print("%s" % event['data'])


def subscribe_boards():
    p = client.pubsub()
    p.subscribe('boards')

    for event in p.listen():
        print("NEW BOARD: %s" % event)
        # {'type': 'subscribe', 'pattern': None, 'channel': 'boards', 'data': 1}
        if event['type'] == 'message':
            threading.Thread(target=subscribe_board, args=(event['data'],)).start()


if __name__ == "__main__":
    subscribe_boards()
