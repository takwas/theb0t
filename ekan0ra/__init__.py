def create_bot(config):

    from factory import LogBotFactory
    #log.startlogging(sys.stdout)

    # create factory protocol and application
    log_bot = LogBotFactory(config)

    return log_bot


def run_bot(bot, server=("irc.freenode.net", 6667, )):
    from twisted.internet import reactor#, protocol

    # connect factory to this host and port
    reactor.connectTCP(server[0], server[1], bot)

    # run bot
    reactor.run()
