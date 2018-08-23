import sys
from datetime import datetime
from pprint import pprint
from pymongo import DESCENDING
from retro.chain.node import BoardNode
from retro.index.mongo_index import MongoIndex

SAMPLE_DATA = [
    {
        "id": "12345",
        "type": "Board",
        "creator": "jlorusso@website.com",
        "create_time": datetime.now(),
        "last_update_time": datetime.now(),
        "version": 2,
        "orig_version": 1,
        "children": ["14326", "45643"],
        "content": {
            "name": "board1",
            "owner": "someguy",
            "group": "404"
        },
    },
    {
        "id": "67890",
        "type": "Board",
        "name": "board2",
        "creator": "nmurdock@website.com",
        "create_time": datetime(1987, 7, 9),
        "last_update_time": datetime(1990, 7, 19),
        "version": 2,
        "orig_version": 1,
        "children": ["14326", "45643"],
        "content": {
            "name": "myboardthing",
            "owner": "dudeman",
            "group": "Nic Cage"
        }
    },
    {
        "id": "54321",
        "type": "Board",
        "name": "board3",
        "creator": "jhackett@website.com",
        "create_time": datetime.now(),
        "last_update_time": datetime.now(),
        "version": 2,
        "orig_version": 1,
        "children": ["14326", "45643"],
        "content": {
            "name": "myboardthing",
            "owner": "someguy",
            "group": "Nic Cage"
        },
    }
]

BOARD_NODES = [BoardNode.from_dict(data) for data in SAMPLE_DATA]


def populate_sample_data(index):
    for board_node in BOARD_NODES:
        index.create_board(board_node)


def main(argv):
    index = MongoIndex()
    print(f'Board exists = {index.has_board("12345")}')
    index.remove_all_boards()
    index.drop_indices()
    index.create_indices()
    populate_sample_data(index)

    board_node = BOARD_NODES[0]
    board_node.content["group"] = "Webelos"
    index.update_board(board_node)
    pprint(index.get_boards(filters={"content.name": "oArD"}, sort_key="name", sort_order=DESCENDING))


if __name__ == "__main__":
    main(sys.argv[1:])
