from retro.index.mongo_index import MongoIndex
from .mem_store import MemStore
from .redis_store import RedisStore


def get_store(cfg):
    if cfg.redis_host:
        index = MongoIndex(host=cfg.mongo_host, port=int(cfg.mongo_port))
        store = RedisStore(index, host=cfg.redis_host, port=int(cfg.redis_port))
    else:
        store = MemStore()

    return store
