#!/usr/bin/env python
# standard library imports
import os
import sys

# library imports
from twisted.python import log

# local imports
import config as conf

# Get an object of the config in use,
# so we can access its __repr__ for logging
config = conf.config_modes.get(os.getenv('BOT_CONFIG', default='default'))()

if __name__ == '__main__':

    import ekan0ra
    from ekan0ra import create_bot, run_bot

    # initialize logging
    log.startLogging(sys.stdout)

    the_bot = create_bot(config=config)
    run_bot(the_bot)
