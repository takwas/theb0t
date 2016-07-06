"""
    A bunch of utility functions for the program.
"""


# Returns a properly formatted channel name
# by making sure it begins with a '#'
def validate_channel(channel):
    assert type(channel) is str # defensive programming
    channel = '#' + channel.lstrip('#')

    return channel


# returns a list of valid link names
# def get_link_names(links_data):
#     return links_list.keys()