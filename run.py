#!/usr/bin/env python

# standard library imports
import os

# local imports
import config as conf


# set the configuration mode that will be
# used for running the program
config = conf.config_modes.get(os.getenv('BOT_CONFIG', default='default'))


def get_args_parser():
    """A helper function for creating command line arguments"""

    # standard library imports
    import argparse


    parser = argparse.ArgumentParser()

    parser.add_argument('-s', '--stealth',  \
                        help='run this client in quiet mode',
                        action='store_true' \
                        )
    parser.add_argument('--nick', help='a server nick for this client')
    parser.add_argument('--pwd', help='a password for a registered nick')
    parser.add_argument('--channels', \
                        help='a list of channels for this client to join'   \
                        )

    return parser


# runs the program
if __name__ == '__main__':

    # local imports
    from ekan0ra import create_bot, run_bot
   

    # get the command-line arguments parser
    args_parser = get_args_parser()
    args = args_parser.parse_args()
    
    channels = args.channels.split() if args.channels else None

    the_bot = create_bot(config, nick=args.nick, pwd=args.pwd or os.environ['IRC_PWD'], channels=channels)

    run_bot(the_bot)

