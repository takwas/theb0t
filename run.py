#!/usr/bin/env python
# standard library imports
import os
import sys

# library imports
from twisted.python import log

# local imports
import config as conf


config = conf.config_modes.get(os.getenv('BOT_CONFIG', default='default'))


if __name__ == '__main__':

    import ekan0ra
    from ekan0ra import create_bot, run_bot

    # initialize logging
    log.startLogging(sys.stdout)

    from sys import argv
    if len(argv) > 1:
        the_bot = create_bot(config=config, channel=argv[1])
    else:
        the_bot = create_bot(config=config)

    run_bot(the_bot)
