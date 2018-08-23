from retro.store.mem_store import MemStore
from retro.store.redis_store import RedisStore
from retro.index.mongo_index import MongoIndex

store = None
index = None


def timedelta_total_seconds(td):
    return (td.microseconds + (td.seconds + td.days * 86400) * 1000000) / 1000000


def unix_time_millis(dt):
    return int(dt.timestamp() * 1000)


def get_store(cfg):
    global store
    if store:
        return store

    if cfg.redis_host:
        store = RedisStore(host=cfg.redis_host, port=int(cfg.redis_port))
    else:
        store = MemStore()

    return store


def get_index(cfg):
    global index
    if index:
        return index

    index = MongoIndex(host=cfg.mongo_host, port=int(cfg.mongo_port))

    return index
