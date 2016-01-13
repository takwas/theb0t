
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


class Response(object):

    def __init__(self, messages=[]):

        if messages is not None and isinstance(messages, str):

            self.messages = messages.split('\n')
        
        else:
            self.messages = messages


    def add_message(self, msg):

        self.messages.append(msg)


    def get_response(self):

        return self.messages


def do_help(msg=None):

    if msg is None or msg=='' or msg==' ':

        def format_cmds():
            """
                Inner helper function.

                This should give an output of the form:
                    :help, :about, :inbox, :link, :log, :masters, :paste, :whatdidimiss, :resource, :submit
            """

            from commands import cmds

            return ':' + ', :'.join(sorted(cmds.keys()))


        return \
            Response(
"""
Showing general help.

List of commands:
    {cmds}

For help on a command, type:
    :help [command]

E.g :help paste

""".format(cmds=format_cmds())
            )

    elif utils.is_valid_cmd(msg):
        
        from commands import cmds

        return Response(cmds.get(msg).get_help_text())
        #'Showing help for command: <:{cmd}>'.format(cmd=msg)

    else:

        return Response(
                "No help for '{cmd}'.\nType ':help' (without the quotes) for a list of commands.".format(cmd=msg)
                )


def do_about(msg):

    return Response(
"""
Byte Bit Bot  :)
Name: Sawkat
Source Factory: http://github.com/takwas/theb0t/
""")


def do_inbox(msg):

    pass


def do_link(msg):

    pass


def do_log(msg):

    now = datetime.datetime.now()
    filename = "logs/Logs-%s.txt"%now.strftime("%Y-%m-%d-%H-%M")
    logger = MessageLogger(open(self.filename, "a"))

    logger.log("[## Class Started at %s ##]" %
                time.asctime(time.localtime(time.time())))
    user = user.split('!', 1)[0]
    self.logger.log("<%s> %s" % (user, msg))
    self.islogging = True



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