from flask import Flask
import os
from retro.engine.board_engine import BoardEngine
from retro.flask import retro_api_blueprint
from retro.utils.config import Config


def buildapp_from_config(cfg):
    board_engine = BoardEngine(cfg)
    app = Flask(__name__, static_url_path='')
    app.register_blueprint(retro_api_blueprint.build_blueprint(board_engine))

    return app


app = buildapp_from_config(Config.from_env())

@app.route("/")
def main():
    return app.send_static_file('index.html')

@app.route('/<path:path>')
def static_file(path):
    return app.send_static_file(path)


if __name__ == "__main__":
    cfg_ = Config.from_env()
    app.run(host=cfg_.retro_api_host, port=cfg_.retro_api_port, debug=True)
