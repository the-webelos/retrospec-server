import os


class Config(object):
    def __init__(self):
        self.retro_api_host = "0.0.0.0"
        self.retro_api_port = 8880
        self.redis_host = None
        self.redis_port = None
        self.mongo_host = None
        self.mongo_port = None
        self.websocket_host = "0.0.0.0"
        self.websocket_port = 4215
        self.flask_secret = "secret!"
        self.template_config = None

    @staticmethod
    def from_env():
        cfg = Config()
        for k, v in os.environ.items():
            if hasattr(cfg, k.lower()):
                setattr(cfg, k.lower(), v)

        return cfg
