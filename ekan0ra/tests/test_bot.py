
# local imports
from bot import LogBot
from . import config


class LogBotTest(unittest.Test):

    bot = LogBot(config)

    def test_names(self):

        assert(bot.names)