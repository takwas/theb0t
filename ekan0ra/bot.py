
# standard library imports
import os
import sys
import time
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
app_console_handler = logging.StreamHandler(sys.stdout)
app_log_file_handler.setLevel('INFO')
app_console_handler.setLevel('DEBUG')
app_log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
app_log_file_handler.setFormatter(app_log_formatter)
app_console_handler.setFormatter(app_log_formatter)
application_logger.addHandler(app_log_file_handler)
application_logger.addHandler(app_console_handler)


class LogBot(irc.IRCClient):
    """A logging IRC bot."""

    def  __init__(self, config):
        application_logger.info('%r', config)
        application_logger.info('Creating bot...')
        self.config = config
        self.nickname = config.BOTNICK
        self.channel = config.CHANNEL
        # IRC users who can control this bot
        self.channel_admins_list = config.ADMINS
        self.qs_queue = QuestionQueue()
        self.links_reload()
        self.logger = get_logger_instance(self)
        application_logger.info('Logging bot finished initializing.')

    def clearqueue(self):
        self.qs_queue.clear()
        application_logger.info('Question queue cleared!')

    def connectionMade(self):
        application_logger.debug('Connection made!')
        irc.IRCClient.connectionMade(self)
        self.islogging = False
        self._namescallback = {}

    def startlogging(self, topic=None):
        # setup and begin logging a class session
        application_logger.info('About to start logging class session...')
        try:
            self.logger.create_new_log()
            self.logger.log("[## Class Started at %s ##]" %
                        time.asctime(time.localtime(time.time())))
            #user = User(self, user) # parse user object from given hostmask `user`
            #self.logger.log("<%s> %s" % (user.nick, msg)) # log the issuer of this command and the command (message)
            self.islogging = True
            application_logger.info('Class session logging started successfully!')
            if topic:
                irc.IRCClient.topic(self, topic)
        except:
            application_logger.error('Class session logging failed to start!', exc_info=True)
            return False
        return True

    def stoplogging(self):
        # end logging for a class session
        application_logger.info('About to stop logging class session...')
        try:
            if not self.logger:
                return
            #user = User(self, user) # parse user object from given hostmask `user`
            #self.logger.log("<%s> %s" % (user.nick, msg)) # log the issuer of this command and the command (message)
            self.logger.log("[## Class Ended at %s ##]" %
                            time.asctime(time.localtime(time.time())))
            #self.logger.close()
            #self.upload_logs(channel)
            self.last_log_filename = self.logger.filename
            self.islogging = False
            application_logger.info('Class session logging stopped successfully! Log saved at: %s', self.last_log_filename)
        except:
            application_logger.error('Class session logging failed to stop!', exc_info=True)
            return False
        return True

    def connectionLost(self, reason):
        """Called when bot looses connection to the server."""
        application_logger.warning('Connection lost! Will stop logging.\nReason: %s', reason)
        irc.IRCClient.connectionLost(self, reason)
        self.stoplogging()

    def signedOn(self):
        """Called when bot has succesfully signed on to server."""
        self.join(self.channel)
        application_logger.debug('Connected to server and joined channel: %s', self.channel)

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

    # Override say() so we can add logging to it
    def say(self, channel, msg, *args, **kwargs):
        """Send `msg` to `channel` (user/channel)."""
        application_logger.info('Bot said: %s\nIn channel: %s', msg, channel)
        irc.IRCClient.say(self, channel, msg, *args, **kwargs)

    def setTopic(self, topic):
        """Modify the topic of the channel."""
        topic = self.config.BASE_TOPIC + ' | ' + topic
        irc.IRCClient.topic(self, self.channel, topic)

    def resetTopic(self):
        """Reset the channel's topic to its default"""
        selfTopic(self, self.config.BASE_TOPIC)

    def privmsg(self, hostmask, channel, msg):
        """This will get called when the bot receives a message."""
        user = User(self, hostmask) # parse user object from given hostmask `user`
        msg = msg.strip()
        application_logger.info('Bot received message: %s\nFrom: %s\nIn channel: %s', msg, user.nick, channel)

        if self.islogging:
            self.logger.log('<%s> %s' % (user.nick, msg))

        # is the message sender an admin
        if user.is_admin():
            # process message from admin

            if channel == self.nickname:
            # Message is a private message from an admin
                if msg.lower().startswith('startclass'):
                    if not self.islogging:
                        topic = msg[msg.find(' '):].strip()
                        if self.startlogging(topic):
                            self.msg(user.nick, 'Session logging started successfully!')
                            self.say(self.channel, self.config.SESSION_START_MSG)
                            self.log_issuer = user
                        else:
                            self.msg(user.nick, 'Logging failed to start!')
                    else:
                        self.msg(user.nick,
                            'Session logging already started by %s. No extra logging started.' %self.log_issuer.nick)
                    
                if msg.lower().endswith('endclass'):
                    if self.stoplogging():
                        self.msg(user.nick, 'Session logging terminated successfully!')
                        self.say(self.channel, self.config.SESSION_END_MSG)
                    else:
                        self.msg(user.nick, 'Logging failed to terminate!')

            elif msg == 'clearqueue':
                self.clearqueue()
                self.say(self.channel, "Queue is cleared.")
            
            elif msg == 'next' and not self.islogging:
                self.say(self.channel, '%s: No session is going on. No one is in queue.' % user.nick)

            elif msg == 'next' and self.islogging:
                if self.qs_queue.has_next():
                    user = self.qs_queue.pop_next()
                    msg = "%s: Please ask your question." % user.nick
                    if self.qs_queue.has_next():
                        msg = "%s\n%s: You are next. Get ready with your question." % (msg, self.qs_queue.pop_next().nick)
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

        elif msg == '!' and not self.islogging:
            self.say(self.channel, '%s: no session is going on, feel free to ask a question. You do not have to type !' % user.nick)
        # end processing question indicator    

        elif msg == 'givemelogs':
            if not self.last_log_filename:
                self.msg(user.nick, 'Sorry, I do not have the last log.')
                application_logger.warning('Could not find last class log!')
            else:
                sys.argv = ['fpaste', self.last_log_filename]
                try:
                    short_url, url = fpaste.main()
                    application_logger.info('Class Log uploaded; and Fedora Paste returned:\n\tShort URL: %s\n\tLong URL: %s', short_url, url)
                    self.msg(user.nick, url)
                except:
                    self.msg(user.nick, 'Hit a 500! I have a crash on you.')
                    application_logger.error('Log uploading to Fedora failed!', exc_info=True)
        
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

    # IRC callbacks

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
        application_logger.info('Question queue cleared!')


# class Attendance(list):

#     def __init__(self):
#         self.mylist = list()
#     def addUser(self, user):
#         self.mylist.append(user)
#         time_in = datetime.datetime.now()
#         self.record[user.nick] = user, timein


class User(object):

    # 'hostmask' is of the form: username!ident@hostmask
    # Every user has access to the bot object
    def __init__(self, bot, user_hostmask):
        self.bot = bot
        self.hostmask = user_hostmask
        hostmask_pattern = re.compile(r'\w*![~\w]*@\w*')
        if hostmask_pattern.search(user_hostmask):
            self.nick, self.ident, self.mask = re.split('[!@]', user_hostmask) # split into nick, ident, mask
        else:
            raise InvalidUserError

    def __repr__(self):
        return 'User [Nick: %s; Ident: %s; Mask: %s]' %(self.nick, self.ident, self.mask)

    def is_admin(self):
        return self.nick in self.bot.channel_admins_list


class InvalidUserError(Exception):
    pass
