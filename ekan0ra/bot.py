
# standard library imports
import time, sys, os
import datetime
import json
import re
import logging

# library imports
from twisted.words.protocols import irc
from twisted.internet import defer

# local imports
#from ekan0ra import config
from commands import commands
from logger import get_logger_instance
import fpaste
import utils


# globals
help_template = """
{command} - {help_text}
"""

application_logger = logging.getLogger('application_logger')
app_log_file_handler = logging.FileHandler('.application_log.log')
app_log_file_handler.setLevel('DEBUG')
application_logger.addHandler(app_log_file_handler)


class LogBot(irc.IRCClient):
    """A logging IRC bot."""

    def  __init__(self, config):
        self.config = config
        self.nickname = config.BOTNICK
        self.channel = config.CHANNEL
        # IRC users who can control this bot
        self.channel_admins_list = config.ADMINS
        self.qs_queue = QuestionQueue()
        self.links_reload()
        self.logger = get_logger_instance(self)

    def clearqueue(self):
        self.qs_queue.clear()

    def connectionMade(self):
        irc.IRCClient.connectionMade(self)
        self.islogging = False
        self._namescallback = {}

    def startlogging(self, user, msg):
        try:
            # setup and begin logging a class session
            self.logger.create_new_log()
            self.logger.log("[## Class Started at %s ##]" %
                        time.asctime(time.localtime(time.time())))
            #user = User(self, user) # parse user object from given hostmask `user`
            self.logger.log("<%s> %s" % (user.nick, msg)) # log the issuer of this command and the command (message)
            self.islogging = True
            self.log_issuer = user
        except:
            return False
        return True

    def stoplogging(self, channel):
        try:
            # end logging for a class session
            if not self.logger:
                return
            #user = User(self, user) # parse user object from given hostmask `user`
            self.logger.log("<%s> %s" % (user.nick, msg)) # log the issuer of this command and the command (message)
            self.logger.log("[## Class Ended at %s ##]" %
                            time.asctime(time.localtime(time.time())))
            self.logger.close()
            #self.upload_logs(channel)
            self.islogging = False
        except:
            return False
        return True

    def connectionLost(self, reason):
        irc.IRCClient.connectionLost(self, reason)
        self.islogging = False

    def signedOn(self):
        """Called when bot has succesfully signed on to server."""
        self.join(self.channel)

    def pingall(self, nicklist):
        """Called to ping all with a message"""
        msg = ', '.join([nick for nick in nicklist if nick != self.nickname and nick not in self.channel_admins_list])
        self.say(self.channel, msg)
        self.say(self.channel, self.pingmsg.lstrip())

    # To reload json file
    def links_reload(self):
        link_file = open('links.json')
        self.links_data = json.load(link_file)
        link_file.close()


    # IRC callbacks

    def privmsg(self, hostmask, channel, msg):
        """This will get called when the bot receives a message."""
        user = User(self, hostmask) # parse user object from given hostmask `user`
        msg = msg.strip()

        if self.islogging:
            self.logger.log('<%s> %s' % (user.nick, msg))

        # is the message sender an admin
        if user.is_admin():
            # process message from admin

            if channel == self.nickname:
            # Message is a private message from an admin
                if msg.lower().endswith('startclass'):
                    if not self.islogging:
                        if self.startlogging(user, msg):
                            self.msg(user.nick, 'Session logging started successfully!')
                            self.say(self.channel, self.config.SESSION_START_MSG)
                        else:
                            self.msg(user.nick, 'Logging failed to start!')
                    else:
                        self.msg(user.nick,
                            'Session logging already started by %s. No extra logging started.' %self.log_issuer.nick)
                    
                if msg.lower().endswith('endclass'):
                    if stoplogging(user, msg):
                        self.msg(user.nick, 'Session logging terminated successfully!')
                        self.say(self.channel, self.config.SESSION_END_MSG)
                    else:
                        self.msg(user.nick, 'Logging failed to terminate!')

            elif msg == 'clearqueue':
                self.clearqueue()
                self.say(self.channel, "Queue is cleared.")
            
            elif msg == 'next':
                if self.qs_queue.has_next():
                    print 'Queue-pop: %r' %self.qs_queue # DEBUG
                    user = self.qs_queue.pop_next()
                    print 'User: %r' %user # DEBUG
                    msg = "%s: please ask your question." % user.nick
                    if self.qs_queue.has_next():
                        msg = "%s. %s you are next. Get ready with your question." % (msg, self.qs_queue.pop_next().nick)
                    self.say(self.channel, msg)
                else:
                    self.say(self.channel, "No one is in queue.")

            elif msg == 'masters':
                self.say(self.channel, "My current masters are: %s" % ",".join(self.channel_admins_list))

            elif msg.startswith('add:'):
                try:
                    nick = msg.split()[1]
                    print nick # DEBUG
                    # is nick valid
                    self.channel_admins_list.append(nick)
                    self.say(self.channel,'%s is a master now.' % name)
                except Exception, err:
                    print err # DEBUG

            elif msg.startswith('rm:'):
                try:
                    nick = msg.split()[1]
                    self.channel_admins_list = filter(lambda x: x.lower() != nick.lower(), self.channel_admins_list)
                except Exception, err:
                    print err

            elif msg.lower().startswith('pingall:'):
                self.pingmsg = msg.lower().lstrip('pingall:')
                self.names(channel).addCallback(self.pingall)
            # end processing admin message


        # User wants to ask a question
        if msg == '!'  and self.islogging:
            self.qs_queue.append(user)
            print 'Queue-append: %r' %self.qs_queue # DEBUG

        elif msg == '!' and not self.islogging:
            self.say(self.channel, '%s: no session is going on, feel free to ask a question. You do not have to type !' % user.nick)
        # end processing question indicator    

        elif msg == 'givemelogs':
            sys.argv = ['fpaste', self.filename]
            try:
                short_url, url = fpaste.main()
                self.msg(user.nick, url)
            except:
                self.msg(user.nick, 'Hit a 500! I have a crash on you.')
        
        elif msg == 'help':
            for command, help_txt in commands.iteritems():
                self.msg(
                    user,
                    help_template.format(
                        command=command, help_text=help_txt
                    )
                )      

        elif msg.startswith('.link '):
            self.links_for_key(msg)

    def action(self, hostmask, channel, msg):
        """This will get called when the bot sees someone do an action."""
        user = User(self, hostmask) # parse user object from given hostmask `user`
        if self.islogging:
            self.logger.log("* %s %s" % (user.nick, msg))

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
        Generate an altered version of a nickname that caused a
        collision in an effort to create an unused related name for
        subsequent registration.
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
            self.say(self.channel, '.link need a keyword. Check help for details')

        if keyword == 'reload':
            self.links_reload()
        else:
            self.say(self.channel,
                     str(self.links_data.get(str(keyword), "Keyword does not exist! Type [.link help] or [.link -l] to see valid keywords")))

    def irc_RPL_ENDOFNAMES(self, prefix, params):
        channel = params[1].lower()
        if channel not in self._namescallback:
            return

        callbacks, namelist = self._namescallback[channel]

        for cb in callbacks:
            cb.callback(namelist)

        del self._namescallback[channel]


class QuestionQueue(list):

    def has_next(self):
        return len(self) > 0

    def next(self):
        if self.has_next():
            return self[0]
        else:
            return None

    def pop_next(self):
        if self.has_next():
            return self.pop(0)
        else:
            return None

    def clear(self):
        self.__delslice__(0, len(self))


class User(object):

    # 'hostmask' is of the form: username!ident@hostmask
    # Every user has access to the bot object
    def __init__(self, bot, user_hostmask):
        self.bot = bot
        self.hostmask = user_hostmask
        hostmask_pattern = re.compile(r'\w*![~\w]*@\w*')
        if hostmask_pattern.search(user_hostmask):
            self.nick, ident, self.mask = re.split('[!@]', user_hostmask) # split into nick, ident, mask
        else:
            raise InvalidUserError

    def is_admin(self):
        return self.nick in self.bot.channel_admins_list


class InvalidUserError(Exception):
    pass
