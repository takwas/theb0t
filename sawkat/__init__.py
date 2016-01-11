import tests


def create_bot(config, nick=None, pwd=None, channels=None):
    
    # standard library imports
    import sys

    # library imports
    from twisted.python import log

    # local imports
    import utils
    from factory import LogBotFactory


    if nick is None:
        nick = config.BOTNICK

    if channels is None:
        channels = list(config.DEFAULT_CHANNELS)
    
    for i in range(len(channels)):
        channels[i] = utils.verify_channel(channels[i])

    
    # initialize logging
    log.startLogging(sys.stdout)

    # create factory protocol and application
    log_bot = LogBotFactory(nick=nick,  \
                            pwd=pwd,    \
                            channels=channels,    \
                            channel_admins=list(    \
                                config.DEFAULT_CHANNEL_ADMINS)  \
                            )

    return log_bot



def run_bot(bot, server=("irc.freenode.net", 6667, )):

    # library imports
    from twisted.internet import reactor#, protocol


    # connect factory to this host and port
    reactor.connectTCP(server[0], server[1], bot)

    # run bot
    reactor.run()
