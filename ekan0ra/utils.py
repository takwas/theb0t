"""
    A bunch of utility functions for the program.
"""


# Verifies the name format for a channel
# Prepends it with a "#", if it doesn't
# already start with one
def verify_channel(channel):
    if channel and not channel.startswith('#'):
        channel = '#' + channel

    return channel


# returns a list of valid link names
def get_link_names(links_data):
    links_list = []
    for key, value in links_data.iteritems():
        links_list.append(key)

    return links_list