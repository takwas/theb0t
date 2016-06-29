
# library imports
from twisted.internet import reactor, protocol

# local imports
from bot import LogBot
#import utils

class LogBotFactory(protocol.ClientFactory):
    """A factory for LogBots.

    A new protocol instance will be created each time we connect to the server.
    """

    def __init__(self, config): # nick, channel, channel_admins):
        self.config = config
        self.channel = self.config.CHANNEL
        self.nickname = self.config.BOTNICK
        self.channel_admins_list = self.config.ADMINS

    def buildProtocol(self, addr):
        bot = LogBot(self.config)
        bot.factory = self
        return bot

    def clientConnectionLost(self, connector, reason):
        """If we get disconnected, reconnect to server."""
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print "connection failed:", reason
        reactor.stop()