# -*- coding: utf-8 -*-
"""
    ekan0ra.utils
    ~~~~~~~~~~~~~

    A bunch of utility functions for the program.

    :copyright: 
    :license:
"""
# local imports
from .commands import commands


# Returns a properly formatted channel name
# by making sure it begins with a '#'
def validate_channel(channel):
    assert type(channel) is str # defensive programming
    channel = '#' + channel.lstrip('#')
    return channel


# returns a list of valid link names
# def get_link_names(links_data):
#     return links_list.keys()


def get_help_text(command, padding=15):
    """Retrieve and format help text for `command`."""
    help_text = commands.get(command, None)
    if help_text is None:
        return ''
    return ' %-{padding}s|  {help_text}'.format(
        padding=padding,
        help_text=help_text) % command