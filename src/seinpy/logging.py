import logging
from enum import Enum

LOG_FORMAT_DEFAULT = "%(asctime)s:%(levelname)s:%(name)s:%(message)s"
LOG_FORMAT_DEBUG = "%(levelname)s:%(message)s:%(pathname)s:%(funcName)s:%(lineno)d"


class LogLevels(Enum):
    debug = "DEBUG"
    info = "INFO"
    warning = "WARNING"
    error = "ERROR"
    critical = "CRITICAL"


def configure_logging(level: LogLevels = LogLevels.debug) -> None:
    level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }

    log_level = level_map.get(level.value, logging.WARNING)

    if level == LogLevels.debug:
        logging.basicConfig(level=log_level, format=LOG_FORMAT_DEBUG, force=True)
    else:
        logging.basicConfig(level=log_level, format=LOG_FORMAT_DEFAULT, force=True)
