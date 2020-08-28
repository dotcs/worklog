import unittest
import sys
import logging

from worklog.utils.logger import configure_logger
import worklog.constants as wc


class TestLogging(unittest.TestCase):
    def test_configure_logger_name(self):
        logger = configure_logger()
        name = logger.name
        self.assertEqual(name, wc.DEFAULT_LOGGER_NAME)

    def test_configure_logger_handlers(self):
        logger = configure_logger()

        has_handlers = logger.hasHandlers()
        self.assertTrue(has_handlers)

        sys_handler = logger.handlers[0]
        self.assertEqual(sys_handler.stream, sys.stdout)

    def test_configure_logger_default_log_level(self):
        logger = configure_logger()
        log_level = logger.level
        self.assertEqual(log_level, logging.INFO)
