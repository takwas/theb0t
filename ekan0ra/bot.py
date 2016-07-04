
# standard library imports
import os
import sys
import time
from datetime import datetime
import json
import logging

# library imports
from twisted.words.protocols import irc
from twisted.internet import defer

# local imports
from user import IRCUser, InvalidUserError
from queue import QuestionQueue
from commands import commands
from logger import get_logger_instance
import fpaste
import utils


# globals
help_template = """{command} - {help_text}"""

application_logger = logging.getLogger('logbot_logger')

def create_app_logger(config):
    if not os.path.exists(config.APP_LOG_DIR):
        os.mkdir(config.APP_LOG_DIR)
    log_file_path = os.path.join(config.APP_LOG_DIR, config.APP_LOGGER_NAME)

    app_log_file_handler = logging.FileHandler(log_file_path)
    app_console_handler = logging.StreamHandler(sys.stdout)
    app_log_file_handler.setLevel('INFO')
    app_console_handler.setLevel('DEBUG')
    app_log_formatter = logging.Formatter(
        '%(name)s - %(levelname)s - %(message)s\n')
    app_log_file_handler.setFormatter(app_log_formatter)
    app_console_handler.setFormatter(app_log_formatter)
    application_logger.addHandler(app_log_file_handler)
    application_logger.addHandler(app_console_handler)
    application_logger.setLevel('DEBUG')


class LogBot(irc.IRCClient):
    """A logging IRC bot."""

    def  __init__(self, config):
        create_app_logger(config)
        application_logger.info('%r', config)
        application_logger.info('Creating bot...')
        self.config = config
        self.nickname = config.BOTNICK
        self.channel = config.CHANNEL
        self.channel_admins_list = list(config.ADMINS) # IRC users who can control this bot
        self.qs_queue = QuestionQueue()
        self.links_reload()
        self.logger = get_logger_instance()
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
            if not os.path.exists(self.config.CLASS_LOG_DIR):
                os.mkdir(self.config.CLASS_LOG_DIR)
            log_file_path = os.path.join(
                self.config.CLASS_LOG_DIR,
                self.config.LOG_FILENAME.format(
                    datetime.now().strftime('%Y-%m-%d-%H-%M')
                )
            )
            self.logger.create_new_log(
                log_file_path, self.config.CLASS_LOGGER_FORMAT)
            self.logger.log(
                '[## Class Started at %s ##]' % 
                    time.asctime(time.localtime(time.time()))
            )
            self.islogging = True
            application_logger.info(
                'Class session logging started successfully!'
            )
            if topic:
                self.setTopic(topic)
        except:
            application_logger.error(
                'Class session logging failed to start!', exc_info=True
            )
            return False
        return True

    def stoplogging(self):
        # end logging for a class session
        application_logger.info('About to stop logging class session...')
        try:
            if not self.logger:
                return
            self.logger.log(
                '[## Class Ended at %s ##]' %
                    time.asctime(time.localtime(time.time()))
            )
            #self.logger.close()
            #self.upload_logs(channel)
            self.last_log_filename = self.logger.filename
            self.islogging = False
            application_logger.info(
                'Class session logging stopped successfully!\nLog saved '
                    'at: %s',
                self.last_log_filename
            )
            self.resetTopic()
        except:
            application_logger.error(
                'Class session logging failed to stop!', exc_info=True
            )
            return False
        return True

    def connectionLost(self, reason):
        """Called when bot looses connection to the server."""
        application_logger.warning(
            'Connection lost! Will stop logging.\nReason: %s', reason
        )
        irc.IRCClient.connectionLost(self, reason)
        if self.islogging:
            self.stoplogging()

    def signedOn(self):
        """Called when bot has succesfully signed on to server."""
        self.join(self.channel)
        application_logger.debug(
            'Connected to server and joined channel: %s', self.channel
        )

    def pingall(self, nicklist):
        """Called to ping all with a message"""
        msg = ', '.join([nick for nick in nicklist if nick != self.nickname
                        and nick not in self.channel_admins_list])
        self.say(self.channel, msg)
        self.say(self.channel, self.pingmsg.lstrip())

    # To reload json file
    def links_reload(self):
        try:
            link_file = open(self.config.LINKS_FILE)
            self.links_data = json.load(link_file)
            link_file.close()
            application_logger.info('Links file reloaded.')
        except:
            application_logger.error('Error reloading links file.',
                exc_info=True)

    # Override msg() so we can add logging to it
    def say(self, channel, msg, *args, **kwargs):
        """Send `msg` to `channel` (user/channel)."""
        application_logger.info('Bot said: %s\nIn channel: %s', msg, channel)
        irc.IRCClient.msg(self, channel, msg, *args, **kwargs)

    def setTopic(self, topic):
        """Modify the topic of the channel."""
        topic = self.config.BASE_TOPIC + ' | ' + topic
        application_logger.info('Bot changed channel topic to: %s', topic)
        irc.IRCClient.topic(self, self.channel, topic)

    def resetTopic(self):
        """Reset the channel's topic to its default"""
        self.setTopic(self.config.BASE_TOPIC)

    def privmsg(self, hostmask, channel, msg):
        """This will get called when the bot receives a message."""
        user = IRCUser(self, hostmask) # parse user object from given hostmask `user`
        msg = msg.strip()
        application_logger.info(
            '\nMessage:\t%s\nFrom:\t%s\nChannel:\t%s', msg, user.nick, channel
        )

        if self.islogging and not channel == self.nickname:
            # Don't log private messages with class log
            self.logger.log('<%s> %s' % (user.nick, msg))

        # is the message sender an admin
        if user.is_admin():
        # process message from admin

            if channel == self.nickname:
            # Message is a private message from an admin
                if msg.lower().startswith('startclass'):
                    if not self.islogging:
                        arg_pos = msg.find(' ')
                        if arg_pos >= 0:
                            topic = msg[arg_pos:].strip()
                        else:
                            topic = None
                        if self.startlogging(topic):
                            self.say(
                                user.nick,
                                'Session logging started successfully!'
                            )
                            self.say(
                                self.channel, self.config.SESSION_START_MSG
                            )
                            self.log_issuer = user
                        else:
                            self.say(user.nick, 'Logging failed to start!')
                    else:
                        self.say(
                            user.nick,
                            'Session logging already started by %s. No extra '
                                'logging started.' % self.log_issuer.nick
                        )
                    
                if msg.lower().endswith('endclass'):
                    if self.stoplogging():
                        self.say(
                            user.nick,
                            'Session logging terminated successfully!'
                        )
                        self.say(self.channel, self.config.SESSION_END_MSG)
                    else:
                        self.say(user.nick, 'Logging failed to terminate!')

            elif msg == 'clearqueue':
                self.clearqueue()
                self.say(self.channel, 'Queue is cleared.')
            
            elif msg == 'next' and not self.islogging:
                self.say(
                    self.channel,
                    '%s: No session is going on. No one is in queue.' %
                        user.nick
                )

            elif msg == 'next' and self.islogging:
                if self.qs_queue.has_next():
                    nick = self.qs_queue.pop_next()
                    msg = '%s: Please ask your question.' % nick
                    if self.qs_queue.has_next():
                        msg = '%s\n%s: You are next. Get ready with your ' \
                            'question.' % (msg, self.qs_queue.peek_next())
                    self.say(self.channel, msg)
                else:
                    self.say(self.channel, 'No one is in queue.')

            elif msg == 'masters':
                self.say(
                    self.channel,
                    'My current masters are: %s' %
                        ','.join(self.channel_admins_list)
                )

            elif msg.startswith('add:'):
                try:
                    nick = msg.split()[1]
                    print nick # DEBUG
                    # is nick valid
                    if nick in self.channel_admins_list:
                        self.say(
                            self.channel, '%s is already a master.' % nick)
                        application_logger.info('%s is already an admin.',
                            nick)
                    else:
                        self.channel_admins_list.append(nick)
                        self.say(self.channel,'%s is a master now.' % nick)
                        application_logger.info('%s became an admin.', nick)
                except Exception, err:
                    application_logger.error(
                        'Error adding admin!', exc_info=True
                    )

            elif msg.startswith('rm:'):
                try:
                    nick = msg.split()[1]
                    self.channel_admins_list = filter(
                        lambda x: x.lower() != nick.lower(),
                        self.channel_admins_list
                    )
                    self.say(self.channel, '%s removed from admin.' % nick)
                    application_logger.info('%s removed from admin.', nick)
                except Exception, err:
                    application_logger.error(
                        'Error removing admin!', exc_info=True
                    )

            elif msg.lower().startswith('pingall:'):
                self.pingmsg = msg.lower().lstrip('pingall:')
                self.names(channel).addCallback(self.pingall)
        # end processing admin message


        # User wants to ask a question
        if msg == '!'  and self.islogging:
            self.qs_queue.enqueue(user.nick)

        # User no longer wants to ask a question; remove them from queue
        elif msg in ('!-', '!!')  and self.islogging:
            self.qs_queue.dequeue(user.nick)

        elif msg in ('!', '!-', '!!') and not self.islogging:
            self.say(
                self.channel,
                '%s: No session is going on, feel free to ask a question. '
                    'You do not have to type %s' % (user.nick, msg)
            )
        # end processing question indicator   

        elif msg == 'givemelogs':
            if not self.last_log_filename:
                self.say(user.nick, 'Sorry, I do not have the last log.')
                application_logger.warning('Could not find last class log!')
            else:
                sys.argv = ['fpaste', self.last_log_filename]
                try:
                    short_url, url = fpaste.main()
                    application_logger.info(
                        'Class Log uploaded; and Fedora Paste returned:\n\t'
                            'Short URL: %s\n\tLong URL: %s', short_url, url
                    )
                    self.say(user.nick, url)
                except:
                    self.say(user.nick, 'Hit a 500! I have a crash on you.')
                    application_logger.error(
                        'Log uploading to Fedora failed!', exc_info=True
                    )
        
        elif msg == 'help':
            for command, help_txt in commands.iteritems():
                self.say(
                    user,
                    help_template.format(
                        command=command, help_text=help_txt
                    )
                )      

        elif msg.split()[0] == '.link':
            self.links_for_key(msg)

    def action(self, hostmask, channel, msg):
        """This will get called when the bot sees someone do an action."""
        user = IRCUser(self, hostmask) # parse user object from given hostmask `user`
        if self.islogging:
            self.logger.log('* %s %s' % (user.nick, msg))

    # IRC callbacks

    def irc_NICK(self, prefix, params):
        """Called when an IRC user changes their nickname."""
        old_nick = prefix.split('!')[0]
        new_nick = params[0]
        if self.islogging:
            self.logger.log('%s is now known as %s' % (old_nick, new_nick))

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
        self.sendLine('NAMES %s' % channel)
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
        try:
            keyword = msg.split()[1]
            if not keyword:
                raise IndexError
        except IndexError:
            application_logger.error(
                'No keyword argument provided for `.link` command',
                exc_info=True)
            self.say(
                self.channel, '.link needs a keyword as argument. Check help for details.'
            )
            return

        if keyword == 'reload':
            self.links_reload()
        elif keyword in ['-l', 'help']:
            self.say(
                self.channel,
                'Valid options for `.link`:\t[%s]' %
                    str(', '.join(self.links_data.keys()))
            )
        else:
            self.say(
                self.channel,
                str(
                    self.links_data.get(
                        str(keyword),
                        'Keyword "%s" does not exist! Type [.link help] or '
                            '[.link -l] to see valid keywords' % keyword
                    )
                )
            )

    def irc_RPL_ENDOFNAMES(self, prefix, params):
        channel = params[1].lower()
        if channel not in self._namescallback:
            return

        callbacks, namelist = self._namescallback[channel]

        for cb in callbacks:
            cb.callback(namelist)

        del self._namescallback[channel]


