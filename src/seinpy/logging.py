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
    log_level = str(level.name).upper()
    log_levels = [level.value for level in LogLevels]

    if log_level not in log_levels:
        logging.basicConfig(level=LogLevels.error, format=LOG_FORMAT_DEFAULT)
        return

    if level == LogLevels.debug:
        logging.basicConfig(level=log_level, format=LOG_FORMAT_DEBUG)
    else:
        logging.basicConfig(level=log_level, format=LOG_FORMAT_DEFAULT)
