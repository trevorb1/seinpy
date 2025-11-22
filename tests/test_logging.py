import logging
from seinpy.logging import (
    configure_logging,
    LogLevels,
    LOG_FORMAT_DEFAULT,
    LOG_FORMAT_DEBUG,
)
import pytest


class TestLogLevels:
    def test_log_levels_enum_values(self):
        """Test that LogLevels enum has correct values."""
        assert LogLevels.debug.value == "DEBUG"
        assert LogLevels.info.value == "INFO"
        assert LogLevels.warning.value == "WARNING"
        assert LogLevels.error.value == "ERROR"
        assert LogLevels.critical.value == "CRITICAL"

    def test_log_levels_enum_names(self):
        """Test that LogLevels enum has correct names."""
        assert LogLevels.debug.name == "debug"
        assert LogLevels.info.name == "info"
        assert LogLevels.warning.name == "warning"
        assert LogLevels.error.name == "error"
        assert LogLevels.critical.name == "critical"


class TestConfigureLogging:
    test_data = [
        (LogLevels.debug, logging.DEBUG),
        (LogLevels.info, logging.INFO),
        (LogLevels.warning, logging.WARNING),
        (LogLevels.error, logging.ERROR),
        (LogLevels.critical, logging.CRITICAL),
    ]

    def setup_method(self):
        """Reset logging configuration before each test."""
        # Remove all handlers from root logger
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
        # Reset to default level
        logging.root.setLevel(logging.WARNING)

    def test_configure_logging_default_debug(self):
        """Test that configure_logging defaults to debug level with debug format."""
        configure_logging()

        root_logger = logging.getLogger()
        assert root_logger.level == logging.DEBUG

        # Check that the handler has the debug format
        handler = root_logger.handlers[0]
        assert handler.formatter._fmt == LOG_FORMAT_DEBUG

    @pytest.mark.parametrize(
        "level, expected_level",
        test_data,
        ids=["debug", "info", "warning", "error", "critical"],
    )
    def test_configure_logging_with_level(self, level, expected_level):
        """Test that configure_logging with debug level uses debug format."""
        configure_logging(level)

        root_logger = logging.getLogger()
        assert root_logger.level == expected_level

        handler = root_logger.handlers[0]
        assert (
            handler.formatter._fmt == LOG_FORMAT_DEBUG
            if level == LogLevels.debug
            else LOG_FORMAT_DEFAULT
        )

    def test_configure_logging_multiple_calls(self):
        """Test that configure_logging can be called multiple times."""
        configure_logging(LogLevels.info)
        assert logging.getLogger().level == logging.INFO

        configure_logging(LogLevels.debug)
        assert logging.getLogger().level == logging.DEBUG

        configure_logging(LogLevels.warning)
        assert logging.getLogger().level == logging.WARNING
