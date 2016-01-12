
"""
    List of actions:

        do_help
        do_about
        do_inbox
        do_link
        do_log
        do_masters
        do_paste
        do_recall
        do_resource
        do_submit
"""

# standard library imports
import re

# local imports
import utils


def do_help(msg=None):

    if msg is None:

        def format_cmds():
            """
                Inner helper function.

                This should give an output of the form:
                    :help, :about, :inbox, :link, :log, :masters, :paste, :whatdidimiss, :resource, :submit
            """
            
            from commands import cmds

            ':' + ', :'.join(sorted(cmds.keys()))


        return \
            """
                Showing general help.

                List of commands:
                    {cmds}

                For help on a command, type:
                    :help [command]

                E.g :help paste

            """.format(cmds=format_cmds())

    elif utils.is_valid_cmd(msg):
        
        from commands import cmds

        return cmds.get(msg.get_help_text())
        #'Showing help for command: <:{cmd}>'.format(cmd=msg)

    else:

        return "No help for {cmd}. Type ':help' for list of commands.".format(cmd=msg)


def do_about(msg):

    """
        Byte Bit Bot  :)
    """
    pass


def do_inbox(msg):

    pass


def do_link(msg):

    pass


def do_log(msg):

    pass


def do_masters(msg):

    pass


def do_paste(msg):

    pass


def do_recall(msg):

    pass


def do_resource(msg):

    pass


def do_submit(msg):

    pass