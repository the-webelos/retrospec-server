from flask import Flask
from retro.engine.board_engine import BoardEngine
from retro.engine.group_engine import GroupEngine
from retro.flask import retro_api_blueprint
from retro.flask import group_api_blueprint
from retro.utils.config import Config
from retro.utils.retro_logging import setup_basic_logging


def buildapp_from_config(cfg):
    setup_basic_logging()
    board_engine = BoardEngine(cfg)
    group_engine = GroupEngine(cfg)
    app = Flask(__name__, static_url_path='')
    app.register_blueprint(retro_api_blueprint.build_blueprint(board_engine))
    app.register_blueprint(group_api_blueprint.build_blueprint(group_engine))

    return app


app = buildapp_from_config(Config.from_env())


if __name__ == "__main__":
    cfg_ = Config.from_env()
    app.run(host=cfg_.retro_api_host, port=cfg_.retro_api_port, debug=True)
