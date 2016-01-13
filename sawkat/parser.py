"""
    Parser for messages sent to bot.
"""


class ArgsParser(object):

    def __init__(self, cmd_delimiter=None):

        self.cmd_delimiter = cmd_delimiter if cmd_delimiter is not None \
            else ':'


    def parse_msg(self, msg):

        # strip message of leading and trailing whitespace chars
        msg = msg.strip()
        msg = msg +' '

        if msg.startswith(self.cmd_delimiter):

            # search for the first whitespace in the
            # message to extract the command
            cmd_width = msg.find(' ')
            cmd = msg[1:cmd_width]

            from utils import is_valid_cmd
            
            if is_valid_cmd(cmd):
                from commands import cmds
                func = cmds.get(cmd).get_action()
                return func(msg=msg[cmd_width:].strip())

            else:
                from actions import Response
                return Response("Invalid command!. Type ':help' for help")


    # method to add new command on the fly
    def add_action(self, cmd, action_callback,
                   cmd_help_text="No help available for this command."  \
                   ):
        
        from commands import cmds, Command

        # implement some cmd validator
        cmds[cmd] = Command(cmd=cmd, action_func=action_callback,
                            help_text=cmd_help_text)
