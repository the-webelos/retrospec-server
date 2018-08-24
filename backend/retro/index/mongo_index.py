import locale
import re
from pymongo import collation, MongoClient, ASCENDING, DESCENDING
from retro.chain.node import CREATE_TIME_KEY, NODE_ID_KEY
from retro.index import Index
from .exceptions import InvalidSortOrder

_MONGO_ID_KEY = "_id"
_COLLATION = collation.Collation(locale.getdefaultlocale()[0] or "en_US")
SORT_ORDER_MAP = {"asc": ASCENDING, "desc": DESCENDING}


# TODO Track creator on node creation
# TODO Update last_update_time on node edit
# TODO Create a storage manager that abstracts the index so clients don't have to update both store and index.
# TODO   May also want to move the time declarations in there

class MongoIndex(Index):
    def __init__(self, host=None, port=None, client=None):
        super(MongoIndex, self).__init__()
        # pass connect=False to avoid race condition when MongoClient is started through uwsgi (pre-fork)
        self.__client = client if client is not None else MongoClient(host=host, port=port, connect=False)

        db = self.__client.retrospec
        self._boards_collection = db.boards

    def create_indices(self):
        self._boards_collection.create_index([("content.name", DESCENDING)])

    def drop_indices(self):
        self._boards_collection.drop_indexes()

    def has_board(self, board_id):
        return self._boards_collection.find({NODE_ID_KEY: board_id}, {_MONGO_ID_KEY: True}).limit(1).count() > 0

    def get_boards(self, filters=None, search_terms=None, start=0, count=20, sort_key=None, sort_order=None):
        q_sort_key = sort_key or CREATE_TIME_KEY
        q_sort_order = self._coerce_sort_order(sort_order or ASCENDING)
        q_search_terms = {k: re.compile(v, re.IGNORECASE) for k, v in (search_terms or {}).items()}
        q_filters = {**q_search_terms, **(filters or {})}

        return [
            board for board in self._boards_collection
                                   .find(q_filters, {_MONGO_ID_KEY: False})
                                   .skip(start)
                                   .limit(count)
                                   .sort(q_sort_key, q_sort_order)
                                   .collation(_COLLATION)
        ]

    def create_board(self, board_node):
        self._boards_collection.insert_one(board_node.to_index_dict())

    def update_board(self, board_node):
        self._boards_collection.update_one(
            {NODE_ID_KEY: board_node.id},
            {"$set": board_node.to_index_dict()},
            upsert=True
        )

    def remove_board(self, board_id):
        self._boards_collection.delete_one({NODE_ID_KEY: board_id})

    def remove_all_boards(self):
        self._boards_collection.remove({})

    @staticmethod
    def _coerce_sort_order(sort_order):
        if isinstance(sort_order, int):
            return sort_order

        try:
            return SORT_ORDER_MAP[sort_order.lower()]
        except Exception:
            raise InvalidSortOrder(f"Sort order '{sort_order}' is not valid. Must be one of {SORT_ORDER_MAP.keys()}.")
