
# library imports
from twisted.internet import reactor#, protocol

# local imports
import utils


def create_bot(config, nick=None, channel=None):

    from factory import LogBotFactory
    #log.startlogging(sys.stdout)

    if nick is None:
        nick = config.BOTNICK

    if channel is None:
        channel = config.DEFAULT_CHANNELS[0]
    
    channel = utils.verify_channel(channel)

    # create factory protocol and application
    log_bot = LogBotFactory(nick=nick,  \
                            channel=channel,    \
                            channel_admins=list(    \
                                config.DEFAULT_CHANNEL_ADMINS)  \
                            )

    return log_bot



def run_bot(bot, server=("irc.freenode.net", 6667, )):

    # connect factory to this host and port
    reactor.connectTCP(server[0], server[1], bot)

    # run bot
    reactor.run()
