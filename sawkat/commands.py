"""
    Commands recognisable by our bot.
"""


# local imports
import actions


# commands = [
#     ('!', 'Queue yourself to ask a question during a session'),
#     ('givemelogs', 'Give you a fpaste link with the latest log'),
#     ('clearqueue', 'Clear the ask question queue'),
#     ('next', 'ping the person in the queue to ask question'),
#     ('masters', 'returns the list of all the masters'),
#     ('add:[nick]', 'adds the nick to masters list'),
#     ('rm:[nick]', 'removes the nick from masters list'),
#     ('startclass', 'start logging the class'),
#     ('endclass', 'ends logging the class'),
#     ('pingall:[message]', 'pings the message to all'),
#     ('help', 'list all the commands'),
#     ('.link [portal]', 'Returns the link of the portal')
# ]


# commands = {
#     '!' : 'Queue yourself to ask a question during a session',
#     'givemelogs' : 'Give you a fpaste link with the latest log',
#     'clearqueue' : 'Clear the ask question queue',
#     'next' : 'ping the person in the queue to ask question',
#     'masters' : 'returns the list of all the masters',
#     'add:[nick]' : 'adds the nick to masters list',
#     'rm:[nick]' : 'removes the nick from masters list',
#     'startclass' : 'start logging the class',
#     'endclass' : 'ends logging the class',
#     'pingall:[message]' : 'pings the message to all',
#     'help' : 'list all the commands',
#     '.link [portal]' : 'Returns the link of the portal'
# }


class Command(object):

    def __init__(self, cmd, action_func, help_text):

        self.cmd = cmd
        self.action_func = action_func
        self.help_text = help_text


    def get_help_text(self):

        return self.help_text



    def get_action(self):

        return self.action_func




cmds = {
    'help' : Command(cmd='help', action_func=actions.do_help,
        help_text=   \
"""
Usage:

    U1:\t:help
        Show general help.

    U2:\t:help <command>
        Show help for specified <command>. Use USG1 for a
        list of valid commands.
"""
        ),
    'about' : Command(cmd='about', action_func=actions.do_about,
        help_text=   \
"""
Usage:

    U1:\t:about
        Show 'about' information for this client.
"""
        ),
    'inbox' : Command(cmd='inbox', action_func=actions.do_inbox,
        help_text=   \
"""
Usage:

    U1:\t:inbox
        Show help for this command.

    U2:\t:inbox status
        Show status of inbox. See if there are any unread messages.
"""
        ),
    'link' : Command(cmd='link', action_func=actions.do_link,
        help_text=   \
"""
Usage:

    U1:\t:link
        Show help for this command.

    U2:\t:link list
        Show a list of available link titles.

    U3:\t:link <link_title>
        Show URL for <link_title>.
"""
        ),
    'log' : Command(cmd='log', action_func=actions.do_log,
        help_text=   \
"""
Usage:

    U1:\t:log
        Show help for this command.
"""
),
    'masters' : Command(cmd='masters', action_func=actions.do_masters,
        help_text=   \
"""
Usage:

    U1:\t:masters
        Show help for this command.
"""
        ),
    'paste' : Command(cmd='paste', action_func=actions.do_paste,
        help_text=   \
"""
Usage:

    U1:\t:paste
        Show help for this command.
"""
        ),
    'whatdidimiss' : Command(cmd='recall', action_func=actions.do_recall,
        help_text=   \
"""
Usage:

    U1:\t:recall
        Show help for this command.
"""
        ),
    'resource' : Command(cmd='resource', action_func=actions.do_resource,
        help_text=   \
"""
Usage:

    U1:\t:resource
        Show help for this command.
"""
        ),
    'submit' : Command(cmd='submit', action_func=actions.do_submit,
        help_text=   \
"""
Usage:

    U1:\t:submit
        Show help for this command.
"""
        )
}

