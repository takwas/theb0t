# stdlib imports
import os, sys
import unittest
import logging

# library imports
import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# local imports
from ekan0ra.logger import MessageLogger
from ekan0ra.logger import get_logger_instance


class LoggerTest(unittest.TestCase):

    def setUp(self):
        self.logger = get_logger_instance()
        #self.logger.create_new_log()

    def test_get_logger_instance(self):
        self.assertIsInstance(get_logger_instance(), MessageLogger)

    @mock.patch('ekan0ra.logger.logging.getLogger')
    def test_create_new_log(self, mock_getLogger):
        from datetime import datetime
        self.logger.create_new_log()
        self.assertTrue(mock_getLogger.called)


    # @mock.patch.object(MessageLogger, 'logger', auto_spec=True)
    # def test_log(self, mock_logging_info):
    #     print mock_logging_info
    #     assert True
    #     # self.logger.log('Random log message')
    #     # self.assertTrue(mock_logging_info.called)

    # def test_logger_name(self):
    #     self.assertRegexpMatches(self.logger.logger.name, 'classLogger_\w*')

    # def test_log_filename_pat(self):
    #     self.assertRegexpMatches(
    #         self.logger.filename, 'Logs-\d\d\d\d-\d\d-\d\d-\d\d-\d\d\.txt')

    def tearDown(self):
        logging.shutdown()


def main():
    unittest.main()


# if __name__ == '__main__':
#     unittest.main()