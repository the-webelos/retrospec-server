import logging


def setup_basic_logging(filename=None, level=logging.INFO, fmt=None):
    if not fmt:
        fmt = "%(asctime)s [%(levelname)s] %(name)s - %(message)s"

    handlers = [logging.StreamHandler()]
    if filename:
        handlers.append(logging.FileHandler(filename))

    logging.basicConfig(level=level, format=fmt, handlers=handlers)
