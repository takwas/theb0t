
# local imports
from bot import LogBot
from . import config


class LogBotTest(unittest.Test):

    bot = LogBot(config.DEFAULT_CHANNEL_ADMINS[0])

    def test_names(self):

        assert(bot.names)