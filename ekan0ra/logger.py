
# standard library imports
import time, sys
from datetime import datetime
import logging

class MessageLogger(object):
    """
    An independent logger class (because separation of application
    and protocol logic is a good thing).
    """
    def __init__(self):
        self.logger = None
        self.filename = None

    def create_new_log(self, filename=None, format_str=None):
        self.logger = logging.getLogger('classLogger_{}'.format(datetime.now().strftime("%Y-%m-%d-%H-%M")))
        self.filename = filename or 'Logs-{}.txt'.format(
            datetime.now().strftime("%Y-%m-%d-%H-%M")
        )
        #self.filename = self.bot.config.LOG_FILENAME_PREFIX.format(timestamp)
        file_handler = logging.FileHandler(self.filename)
        file_handler.setLevel('INFO')
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel('ERROR')

        log_formatter = logging.Formatter(format_str or '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        #log_formatter = logging.Formatter(self.bot.config.LOGGER_FORMAT)
        #file_handler.setFormatter(log_formatter)
        console_handler.setFormatter(log_formatter)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        self.logger.setLevel('INFO')

    def log(self, message):
        """Log `message` to a log file."""
        timestamp = time.strftime("%H:%M:%S", time.localtime(time.time()))
        log_msg =  ''.join(['[', timestamp, '] ', message])
        self.logger.info(log_msg)

    def close(self):
        self.logger.shutdown()


# Get logger instance
def get_logger_instance():
        return MessageLogger()