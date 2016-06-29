
# standard library imports
import time
from datetime import datetime
import logging

class MessageLogger(object):
    """
    An independent logger class (because separation of application
    and protocol logic is a good thing).
    """
    def __init__(self, bot):

        self.logger = logging.getLogger('classLogger')
        self.bot = bot

    def create_new_log(self):
        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d-%H-%M")
        log_file_handler = logging.FileHandler(self.bot.config.LOG_FILENAME_PREFIX.format(timestamp))
        log_file_handler.setLevel(logging.INFO)
        log_console_handler = logging.StreamHandler()
        log_console_handler.setLevel(logging.ERROR)
        log_formatter = self.bot.config.LOGGER_FORMAT
        log_file_handler.setFormatter(log_formatter)
        log_console_handler.setFormatter(log_formatter)

        self.logger.addHandler(log_file_handler)
        self.logger.addHandler(log_console_handler)

    def log(self, message):
        """Log `message` to a log file."""
        timestamp = time.strftime("%H:%M:%S", time.localtime(time.time()))
        self.logger.info(' '.join([self.bot.config.LOG_PREFIX.format(timestamp), message]))


# Get logger instance
def get_logger_instance(bot):
    return MessageLogger(bot)