import configparser
import logging
import os

_logger = logging.getLogger(__name__)


class InvalidRetroHomeError(Exception):
    pass


class Config(object):
    RETRO_HOME = os.environ.get("RETRO_HOME", "")
    if not (RETRO_HOME and os.path.exists(RETRO_HOME)):
        raise InvalidRetroHomeError("Environment variable RETRO_HOME must be set to the root directory for this "
                                    "application")

    CFG_DIR = os.path.join(RETRO_HOME, "conf")
    RETRO_CONF = os.path.join(CFG_DIR, "retro.conf")
    INTERPOLATION_VARS = {"retro_home": RETRO_HOME,
                          "cfg_dir": CFG_DIR}

    def __init__(self):
        self._parser = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())

        self.retro_api_host = "0.0.0.0"
        self.retro_api_port = 5123
        self.redis_host = "redis"
        self.redis_port = 6379
        self.websocket_host = "0.0.0.0"
        self.websocket_port = 5124
        self.flask_secret = "secret!"
        self.template_config = os.path.join(self.CFG_DIR, "templates.cfg")

    @staticmethod
    def from_env():
        cfg = Config()
        for k, v in os.environ.items():
            if hasattr(cfg, k.lower()):
                setattr(cfg, k.lower(), v)

        return cfg

    def load(self, path=RETRO_CONF):
        # Initialize the parser with interpolation variables and config defaults
        self._parser.read_dict({configparser.DEFAULTSECT: self.INTERPOLATION_VARS})
        self._parser.read_dict({configparser.DEFAULTSECT: self.to_dict()})

        # Load the config file
        if path is not None:
            if not self._parser.read(path):
                _logger.warning("Unable to load config from path '%s'.", path)

        # Initialize each previously loaded parser value into this config. ConfigParser loads all values as strings, so
        # we need to convert to the correct type.
        for section_name, section in self._parser.items():
            for k in section.keys():
                try:
                    converted_val = self._get_type_converter(type(getattr(self, k)))(section_name, k)
                    setattr(self, k, converted_val)
                except AttributeError:
                    if k.lower() not in self.INTERPOLATION_VARS:
                        _logger.warning("Ignoring unknown config option '%s' in section '%s'.", k, section_name)

        return self

    def write(self, path):
        with open(path, "w") as f:
            # Don't write the interpolation variables to the config.
            for option in self.INTERPOLATION_VARS.keys():
                self._parser.remove_option(configparser.DEFAULTSECT, option)
            self._parser.write(f)

        # Reload the previously deleted interpolation variables.
        self._parser.read_dict({configparser.DEFAULTSECT: self.INTERPOLATION_VARS})

    def _get_type_converter(self, conversion_type):
        if conversion_type == bool:
            return self._parser.getboolean
        elif conversion_type == int:
            return self._parser.getint
        elif conversion_type == float:
            return self._parser.getfloat
        elif conversion_type == type(None):
            def none_converter(sect_name, key):
                v = self._parser.get(sect_name, key)
                return None if v == "None" else v
            return none_converter
        else:
            return self._parser.get

    def to_dict(self):
        return {k: v for k, v in vars(self).items() if not k.startswith("_")}
