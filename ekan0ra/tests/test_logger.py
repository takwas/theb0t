# stdlib imports
import os, sys
import unittest
import logging

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# local imports
from ekan0ra.logger import MessageLogger
from ekan0ra.logger import get_logger_instance


class LoggerTest(unittest.TestCase):

    def setUp(self):
        self.logger = get_logger_instance()
        self.logger.create_new_log()

    def test_bot_is_logbot(self):
        self.assertIsInstance(self.logger, MessageLogger)

    def test_logger_name(self):
        self.assertRegexpMatches(self.logger.logger.name, 'classLogger_\w*')

    def test_log_filename_pat(self):
        self.assertRegexpMatches(
            self.logger.filename, 'Logs-\d\d\d\d-\d\d-\d\d-\d\d-\d\d\.txt')

    def tearDown(self):
        logging.shutdown()


def main():
    unittest.main()


# if __name__ == '__main__':
#     unittest.main()