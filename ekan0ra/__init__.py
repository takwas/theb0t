
# library imports
from twisted.internet import reactor#, protocol

# local imports
from run import config


def create_bot(channel=None):

    from factory import LogBotFactory
    #log.startlogging(sys.stdout)

    if channel is None:
        channel = config.DEFAULT_CHANNELS[0]
    
    channel = verify_channel(channel)

    # create factory protocol and application
    log_bot = LogBotFactory(channel)

    return log_bot


def verify_channel(channel):

    if channel:

        if not channel.startswith('#'):
            channel = '#' + channel

    else:
        pass

    return channel


def run_bot(bot, server=("irc.freenode.net", 6667, )):

    # connect factory to this host and port
    reactor.connectTCP(server[0], server[1], bot)

    # run bot
    reactor.run()
