from retro.store.mem_store import MemStore
from retro.store.redis_store import RedisStore


store = None


def timedelta_total_seconds(td):
    return (td.microseconds + (td.seconds + td.days * 86400) * 1000000) / 1000000


def get_store(cfg):
    global store
    if store:
        return store

    if cfg.redis_host:
        store = RedisStore(host=cfg.redis_host, port=int(cfg.redis_port))
    else:
        store = MemStore()

    return store
