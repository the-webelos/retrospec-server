#if __name__ == "__main__":
#    import gevent.monkey
#    gevent.monkey.patch_all()
#    import psycogreen.gevent
#    psycogreen.gevent.patch_psycopg()
#    import sys
#    sys.path.insert(0, "../../")


from flask import Flask
from retro.flask import api_blueprint
from retro.store.mem_store import MemStore
from retro.utils.config import Config


def buildapp_from_config(cfg):
    nodes = {}
    store = MemStore(nodes)
    app = Flask(__name__)
    app.register_blueprint(api_blueprint.build_blueprint(store))

    return app


if __name__ == "__main__":
    cfg_ = Config()
    app_ = buildapp_from_config(cfg_)
    app_.run(host=cfg_.RetroApiHost, port=cfg_.RetroApiPort, debug=True)
