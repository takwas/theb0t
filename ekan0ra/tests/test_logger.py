import os, sys
path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print path
# local imports
from ekan0ra.bot import LogBot
from ekan0ra.logger import getLogger
from . import config


class LoggerTest(unittest.TestCase):

    def setUp(self):
        self.bot = LogBot(config)

    def test_bot_is_logbot(self):
        self.assertIsInstance(bot, LogBot)


if __name__ == '__main__':
    import os
    import sys
    path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print path
    sys.path.insert(0, path)
    unittest.main()