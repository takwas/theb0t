
# library imports
from twisted.internet import reactor, protocol

# local imports
from bot import LogBot
#import utils

class LogBotFactory(protocol.ClientFactory):
    """A factory for LogBots.

    A new protocol instance will be created each time we connect to the server.
    """

    def __init__(self, nick, channel, channel_admins):
        self.nick = nick
        self.channel = channel
        self.channel_admins = channel_admins


    def buildProtocol(self, addr):
        p = LogBot(nick=self.nick,  \
                   channel=self.channel,    \
                   channel_admins=self.channel_admins   \
                   )
        p.factory = self
        return p

    def clientConnectionLost(self, connector, reason):
        """If we get disconnected, reconnect to server."""
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print "connection failed:", reason
        reactor.stop()