import logging


def setup_basic_logging(filename=None, level=logging.INFO, fmt=None):
    if not fmt:
        fmt = "%(asctime)s [%(levelname)s] %(name)s - %(message)s"
    logging.basicConfig(filename=filename, level=level, format=fmt)
