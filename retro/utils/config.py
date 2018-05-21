import os


class Config(object):
    def __init__(self):
        self.retro_api_host = "0.0.0.0"
        self.retro_api_port = 5123
        self.redis_host = None
        self.redis_port = None
        self.websocket_host = "0.0.0.0"
        self.websocket_port = 5124
        self.flask_secret = "secret!"
        self.template_config = None

    @staticmethod
    def from_env():
        cfg = Config()
        for k, v in os.environ.items():
            if hasattr(cfg, k.lower()):
                setattr(cfg, k.lower(), v)

        return cfg
