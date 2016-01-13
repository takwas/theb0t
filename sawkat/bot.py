
# standard library imports
import time, sys, os
import datetime
import json

# library imports
from twisted.words.protocols import irc
from twisted.internet import defer

# local imports
from commands import cmds
from logger import MessageLogger
from parser import ArgsParser
import fpaste
import utils


# globals
help_template = """
{command} - {help_text}
"""


class LogBot(irc.IRCClient):
    """A logging IRC bot."""

    def  __init__(self, nick, channels, channel_admins, pwd=None):
        self.nickname = nick
        self.password = pwd
        self.channels = channels
        self.channel = channels[0]
        self.channel_admins_list = channel_admins
        self.qs_queue = Queue()
        #self.links_reload()
        self.logger = None
        self.sourceURL = "http://github.com/takwas/theb0t"
        self.parser = ArgsParser()
        self.stealth = False


    def clearqueue(self):
        self.qs_queue = []

    def connectionMade(self):
        irc.IRCClient.connectionMade(self)
        self.islogging = False
        self._namescallback = {}

    def startlogging(self, user, msg):

        pass
        
    def stoplogging(self, channel):
        if not self.logger:
            return
        self.logger.log("[## Class Ended at %s ##]" %
                        time.asctime(time.localtime(time.time())))
        self.logger.close()
        #self.upload_logs(channel)
        self.islogging = False

    def connectionLost(self, reason):
        irc.IRCClient.connectionLost(self, reason)
        self.islogging = False

    def signedOn(self):
        """Called when bot has succesfully signed on to server."""
        for channel in self.channels:
            self.join(channel)

    def pingall(self, nicklist):
        """Called to ping all with a message"""
        msg = ', '.join([nick for nick in nicklist if nick != self.nickname and nick not in self.channel_admins_list])
        self.msg(self.channel, msg)
        self.msg(self.channel, self.pingmsg.lstrip())


    def privmsg(self, user, channel, msg):
        """This will get called when the bot receives a message."""
        user = user.split('!', 1)[0]
        
        msg = msg.strip()

        user_is_admin = user in self.channel_admins_list

        # check if it is a private message to me
        if channel == self.nickname:
            room = user
            response = self.parser.parse_msg(msg)

        # or a message directed at me from the channel
        elif msg.startswith(self.nickname):
            room = channel
            response = self.parser.parse_msg(msg[msg.find(' ')+1:])

        print response.get_response()
        if not self.stealth:
            for line in response.get_response():
                self.msg(room, line)

        # if self.islogging:
        #     self.logger.log("<%s> %s" % (user, msg))


        # if msg == '!'  and self.islogging:
        #     self.qs_queue.append(user)

        # if msg == '!' and not self.islogging:
        #     self.msg(self.channel, '%s: no session is going on, feel free to ask a question. You do not have to type !' % user)
        #     return

        # if msg == 'givemelogs':
        #     import sys
        #     sys.argv = ['fpaste', self.filename]

        #     try:
        #         short_url, url = fpaste.main()
        #         self.msg(user, url)
        #     except:
        #         self.msg(user, '500: I have a crash on you')
        
        # if msg == 'clearqueue' and user_is_admin:
        #     self.clearqueue()
        #     self.msg(self.channel, "Queue is cleared.")

        # if msg == 'next' and user_is_admin:
        #     if len(self.qs_queue) > 0:
        #         name = self.qs_queue.pop(0)
        #         msg = "%s: please ask your question." % name
        #         if len(self.qs_queue) > 0:
        #             msg = "%s. %s you are next. Get ready with your question." % (msg, self.qs_queue[0])
        #         self.msg(self.channel, msg)
        #     else:
        #         self.msg(self.channel, "No one is in queue.")
        # if msg == 'masters' and user_is_admin:
        #     self.msg(self.channel, "My current masters are: %s" % ",".join(self.channel_admins_list))
        # if msg.startswith('add:') and user_is_admin:
        #     try:
        #         name = msg.split()[1]
        #         print name
        #         self.channel_admins_list.append(name)
        #         self.msg(self.channel,'%s is a master now.' % name)
        #     except Exception, err:
        #         print err
        # if msg.startswith('rm:') and user_is_admin:
        #     try:
        #         name = msg.split()[1]
        #         self.channel_admins_list = filter(lambda x: x != name, self.channel_admins_list)
        #     except Exception, err:
        #         print err

        # if msg == 'help':
        #     for command, help_txt in commands.iteritems():
        #         self.msg(user, help_template.format(command=command,
        #                                             help_text=help_txt))

        # if channel == self.nickname:

        #     if msg.lower().endswith('startclass') and user_is_admin:
        #         self.startlogging(user, msg)
        #         self.msg(user, 'Session logging started successfully')
        #         #self.msg(self.channel, '----------SESSION STARTS----------')
        #         self.msg(user, '----------SESSION STARTS----------')

        #     if msg.lower().endswith('endclass') and user_is_admin:
        #         self.msg(self.channel, '----------SESSION ENDS----------')
        #         self.stoplogging(channel)
        #         self.msg(user, 'Session logging terminated successfully')

        # if msg.lower().startswith('pingall:') and user_is_admin:
        #     self.pingmsg = msg.lower().lstrip('pingall:')
        #     self.names(channel).addCallback(self.pingall)

        # if msg == '.link help' or msg == '.link help' or msg == '.link -l':
        #     link_names = str(utils.get_link_names(self.links_data))
            
        #     self.msg(self.channel, link_names)      
            

        # if msg.startswith('.link '):
        #     self.links_for_key(msg)

    def action(self, user, channel, msg):
        """This will get called when the bot sees someone do an action."""
        user = user.split('!', 1)[0]
        if self.islogging:
            self.logger.log("* %s %s" % (user, msg))

    # irc callbacks

    def irc_NICK(self, prefix, params):
        """Called when an IRC user changes their nickname."""
        old_nick = prefix.split('!')[0]
        new_nick = params[0]
        if self.islogging:
            self.logger.log("%s is now known as %s" % (old_nick, new_nick))


    # For fun, override the method that determines how a nickname is changed on
    # collisions. The default method appends an underscore.
    def alterCollidedNick(self, nickname):
        """
        Generate an altered version of a nickname that caused a collision in an
        effort to create an unused related name for subsequent registration.
        """
        return nickname + '^'

    def names(self, channel):
        channel = channel.lower()
        d = defer.Deferred()
        if channel not in self._namescallback:
            self._namescallback[channel] = ([], [])

        self._namescallback[channel][0].append(d)
        self.sendLine("NAMES %s" % channel)
        return d

    def irc_RPL_NAMREPLY(self, prefix, params):
        channel = params[2].lower()
        nicklist = params[3].split(' ')

        if channel not in self._namescallback:
            return

        n = self._namescallback[channel][1]
        n += nicklist

    # Function to return requested links
    def links_for_key(self, msg):
        keyword = msg.split()[1]
        if not keyword:
            self.msg(self.channel, '.link need a keyword. Check help for details')

        if keyword == 'reload':
            self.links_reload()
        else:
            self.msg(self.channel,
                     str(self.links_data.get(str(keyword), "Keyword does not exist! Type [.link help] or [.link -l] to see valid keywords")))

    def irc_RPL_ENDOFNAMES(self, prefix, params):
        channel = params[1].lower()
        if channel not in self._namescallback:
            return

        callbacks, namelist = self._namescallback[channel]

        for cb in callbacks:
            cb.callback(namelist)

        del self._namescallback[channel]






class Queue(object):

    def __init__(self):
        self.queue = []        


    def enqueue(self, item):
        self.queue.append(item)


    def dequeue(self, index):
        """
            Does not return removed queue item"""
        self.pop(index)

    def pop(self, index=None):

        try:
        
            index = len(self.queue)-1 if index is None else index
            return self.queue.pop(index)
        
        except IndexError("Pop index out of queue range!"):
            return None
                


    def is_empty(self):
        return len(self.queue) <= 0
