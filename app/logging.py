import logging

from pythonjsonlogger import jsonlogger


def configure_logging(log_level: str) -> None:
    root = logging.getLogger()
    root.setLevel(log_level)

    handler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter()

    handler.setFormatter(formatter)
    root.addHandler(handler)
