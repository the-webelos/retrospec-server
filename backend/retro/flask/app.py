#if __name__ == "__main__":
#    import gevent.monkey
#    gevent.monkey.patch_all()
#    import psycogreen.gevent
#    psycogreen.gevent.patch_psycopg()
#    import sys
#    sys.path.insert(0, "../../")


from flask import Flask

from retro.engine.board_engine import BoardEngine
from retro.flask import retro_api_blueprint
from retro.store.mem_store import MemStore
from retro.utils.config import Config


def config_from_env():
    return {}


def buildapp_from_config(cfg):
    nodes = {}
    store = MemStore(nodes)
    board_engine = BoardEngine(cfg, store=store)
    app = Flask(__name__)
    app.register_blueprint(retro_api_blueprint.build_blueprint(board_engine))

    return app


app = buildapp_from_config(config_from_env())


if __name__ == "__main__":
    cfg_ = Config()
    app.run(host=cfg_.RetroApiHost, port=cfg_.RetroApiPort, debug=True)
