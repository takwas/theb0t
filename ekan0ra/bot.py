# -*- coding: utf-8 -*-
"""
    ekan0ra.bot
    ~~~~~~~~~~~

    This module implements the Twisted-framework-based bot object.

    :copyright: 
    :license:
"""
# standard Library imports
import json
import logging
import os
import sys
import time
from datetime import datetime

# third-party imports
from twisted.internet import defer
from twisted.words.protocols import irc

# local imports
import fpaste
import utils
from . import APP_LOGGER
from .commands import commands
from .logger import get_logger_instance
from .queue import QuestionQueue
from .user import IRCUser, InvalidUserError


class LogBot(irc.IRCClient):
    """A logging IRC bot.

    Implemented as an extension of `IRCClient` from the Twisted
    framework.

    Args:
        config: Configuration instance.

    Attributes:
        config: Bot configuration data.
        nickname: IRC nick of the bot.
        channel: IRC channel bot is connected to.
        channel_admins_list: List of IRC user-nicks that admins to the
            bot.
        qs_queue: A queue that stores IRC nicks of users who indicate
            that they have questions.
        logger: `MessageLogger` instance.
        last_log_filename: Keeps track of the filename of most recent
            class log.
    """

    def  __init__(self, config):
        APP_LOGGER.info('%r', config)
        APP_LOGGER.info('Creating bot...')
        self.config = config
        self.nickname = config.BOTNICK
        self.channel = config.CHANNEL
        self.channel_admins_list = list(config.ADMINS) # IRC users who can control this bot
        self.qs_queue = QuestionQueue()
        self.load_links()
        self.logger = get_logger_instance()
        self.last_log_filename = self.logger.filename
        APP_LOGGER.info('Logging bot finished initializing.')

    def add_admin(self, nick):
        """Add `nick` to the list of recognized admins.

        Args:
            nick: IRC nick of user to be added as admin.
        """
        self.channel_admins_list.append(nick)

    def remove_admin(self, nick):
        """Remove `nick` from the list (queue) of recognized admins.

        Args:
            nick: IRC nick of user to be added as admin.
        """
        self.channel_admins_list = filter(
            lambda x : x.lower() != nick.lower(),
            self.channel_admins_list            
        )

    def clearqueue(self):
        """Clear the list (queue) of users waiting to ask questions."""
        self.qs_queue.clear()
        APP_LOGGER.info('Question queue cleared!')

    def connectionMade(self):
        """Called when bot makes a connection to the server."""
        APP_LOGGER.debug('Connection made!')
        irc.IRCClient.connectionMade(self)
        self.islogging = False
        self._namescallback = {}

    def startlogging(self, topic=None):
        """Setup and begin logging a class session."""
        APP_LOGGER.info('About to start logging class session...')
        try:
            if not os.path.exists(self.config.CLASS_LOG_DIR):
                os.mkdir(self.config.CLASS_LOG_DIR)
            log_file_path = os.path.join(
                self.config.CLASS_LOG_DIR,
                self.config.CLASS_LOG_FILENAME_FORMAT_STR.format(
                    datetime.now().strftime('%Y-%m-%d-%H-%M')
                )
            )
            self.logger.create_new_log(
                log_file_path,
                self.config.CLASS_LOG_FORMAT_STR,
                self.config.CLASS_LOG_DATE_FORMAT_STR,
                self.config.CLASS_LOG_ROTATION_TIME,
                self.config.CLASS_LOG_ROTATION_INTERVAL,
                self.config.CLASS_LOG_BACKUP_COUNT)
            self.logger.log(
                '[## Class Started at %s ##]' % 
                    time.asctime(time.localtime(time.time()))
            )
            self.islogging = True
            APP_LOGGER.info(
                'Class session logging started successfully!'
            )
            if topic:
                self.setTopic(topic)
        except:
            APP_LOGGER.error(
                'Class session logging failed to start!', exc_info=True
            )
            return False
        return True

    def stoplogging(self):
        """End logging for a class session."""
        APP_LOGGER.info('About to stop logging class session...')
        try:
            if not self.logger:
                return
            self.logger.log(
                '[## Class Ended at %s ##]' %
                    time.asctime(time.localtime(time.time()))
            )
            self.logger.close()
            #self.upload_logs(channel)
            self.last_log_filename = self.logger.filename
            self.islogging = False
            APP_LOGGER.info(
                'Class session logging stopped successfully!\nLog saved '
                    'at: %s',
                self.last_log_filename
            )
            self.resetTopic()
        except:
            APP_LOGGER.error(
                'Class session logging failed to stop!', exc_info=True
            )
            return False
        return True

    def connectionLost(self, reason):
        """Called when bot looses connection to the server."""
        APP_LOGGER.warning('Connection lost!\nReason: %s', reason)
        irc.IRCClient.connectionLost(self, reason)
        if self.islogging:
            self.stoplogging()

    def signedOn(self):
        """Called when bot has succesfully signed on to server."""
        self.join(self.channel)
        APP_LOGGER.debug(
            'Connected to server and joined channel: %s', self.channel
        )

    def pingall(self, nicklist):
        """Called to ping all users with a message."""
        msg = ', '.join([nick for nick in nicklist if nick != self.nickname
                        and nick not in self.channel_admins_list])
        self.say(self.channel, msg)
        self.say(self.channel, self.pingmsg.lstrip())

    # To reload json file
    def load_links(self):
        """Load JSON file containing saved links."""
        try:
            link_file = open(self.config.LINKS_FILE)
            self.links_data = json.load(link_file)
            link_file.close()
            APP_LOGGER.info('Links file (re)loaded.')
        except:
            APP_LOGGER.error('Error reloading links file.',
                exc_info=True)

    # Override msg() so we can add logging to it
    def say(self, channel, msg, *args, **kwargs):
        """Send `msg` to `channel`.

        `channel` can either be a channel or a channel.
        """
        APP_LOGGER.info('\nCHANNEL:\t%s\nBOT MSG:\t%s', channel, msg)
        irc.IRCClient.msg(self, channel, msg, *args, **kwargs)

    def setTopic(self, topic):
        """Modify the topic of the channel.

        Appends `topic` to default topic set in configuration, and sets
        this as the channel's topic.

        Args:
            topic: The message to set as topic.
        """
        topic = self.config.BASE_TOPIC + ' | ' + topic
        APP_LOGGER.info('BOT ACTION (Topic Change):\n\t%s', topic)
        irc.IRCClient.topic(self, self.channel, topic)

    def resetTopic(self):
        """Reset the channel's topic to its default."""
        self.setTopic(self.config.BASE_TOPIC)

    def show_queue_status(self):
        """Show the users still in the question queue."""
        self.describe(self.channel, 'Queue: [%r]' % ', '.join(self.qs_queue))

    def privmsg(self, hostmask, channel, msg):
        """Called when the bot receives a message."""
        # Message parsing could break the bot, let's `try/catch` this
        try:
            user = IRCUser(self, hostmask) # parse user object from given hostmask `user`
            msg = msg.strip()
            APP_LOGGER.info(
                'MESSAGE:\t%s\nSENDER:\t%s\nCHANNEL:\t%s', msg, user.nick, channel
            )

            if self.islogging and not channel == self.nickname:
                # Don't log private messages with class log
                self.logger.log(
                    '<%{}s> %s'.format(self.config.CLASS_LOG_NICK_PADDING) % 
                    (user.nick, msg))

        
            # is the message sender an admin
            if user.is_admin():
            # process message from admin

                if channel == self.nickname:
                # Message is a private message from an admin
                    if msg.lower().startswith('.startclass'):
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
                                self.log_issuer = user.nick
                            else:
                                self.say(user.nick, 'Logging failed to start!')
                        else:
                            self.say(
                                user.nick,
                                'Session logging already started by %s. No extra '
                                    'logging started.' % self.log_issuer
                            )
                        
                    if msg.lower().endswith('.endclass'):
                        if self.stoplogging():
                            self.say(
                                user.nick,
                                'Session logging terminated successfully!'
                            )
                            self.say(self.channel, self.config.SESSION_END_MSG)
                        else:
                            self.say(user.nick, 'Logging failed to terminate!')

                elif msg == '.clearqueue':
                    self.clearqueue()
                    self.say(self.channel, 'Queue is cleared.')
                
                elif msg == '.next' and not self.islogging:
                    self.say(
                        self.channel,
                        '%s: No session is going on. No one is in queue.' %
                            user.nick
                    )

                elif msg == '.next' and self.islogging:
                    if self.qs_queue.has_next():
                        nick = self.qs_queue.pop_next()
                        msg = '%s: Please ask your question.' % nick
                        if self.qs_queue.has_next():
                            msg = '%s\n%s: You are next. Get ready with your ' \
                                'question.' % (msg, self.qs_queue.peek_next())
                        self.say(self.channel, msg)
                        if self.config.SHOW_QUEUE_STATUS_ENABLED:
                            self.show_queue_status()
                    else:
                        self.say(self.channel, 'No one is in queue.')

                elif msg == '.masters':
                    self.say(
                        self.channel,
                        'My current masters are: %s' %
                            ', '.join(self.channel_admins_list)
                    )

                elif msg.startswith('.add'):
                    try:
                        nick = msg.split()[1]
                        if nick in self.channel_admins_list:
                            self.say(
                                self.channel, '%s is already a master.' % nick)
                            APP_LOGGER.info('%s is already an admin.',
                                nick)
                        else:
                            self.add_admin(nick)
                            self.say(self.channel,'%s is a master now.' % nick)
                            APP_LOGGER.info('%s became an admin.', nick)
                    except Exception, err:
                        APP_LOGGER.error(
                            'Error adding admin!', exc_info=True
                        )

                elif msg.startswith('.rm'):
                    try:
                        nick = msg.split()[1]
                        self.remove_admin(nick)
                        self.say(self.channel, '%s removed from admin.' % nick)
                        APP_LOGGER.info('%s removed from admin.', nick)
                    except Exception, err:
                        APP_LOGGER.error(
                            'Error removing admin!', exc_info=True
                        )

                elif msg.lower().startswith('.pingall') and \
                        self.config.PINGALL_ENABLED:
                    self.pingmsg = msg.lower().lstrip('.pingall')
                    self.names(channel).addCallback(self.pingall)
            # end processing admin message


            # User wants to ask a question
            if msg == '!'  and self.islogging:
                self.qs_queue.enqueue(user.nick)
                if self.config.SHOW_QUEUE_STATUS_ENABLED:
                    self.show_queue_status()

            # User no longer wants to ask a question; remove them from queue
            elif msg in ('!-', '!!')  and self.islogging and \
                    self.config.LEAVE_QUEUE_ENABLED:
                result = self.qs_queue.dequeue(user.nick)
                if result == True and \
                        self.config.SHOW_QUEUE_STATUS_ENABLED:
                    self.show_queue_status()

            elif msg in ('!', '!-', '!!') and not self.islogging:
                self.say(
                    self.channel,
                    '%s: No session is going on, feel free to ask a question. '
                        'You do not have to type %s' % (user.nick, msg)
                )
            # end processing question indicator   

            elif msg == '.givemelogs' and self.config.GIVEMELOGS_ENABLED:
                if not self.last_log_filename:
                    self.say(user.nick, 'Sorry, I do not have the last log.')
                    APP_LOGGER.warning('Could not find last class log!')
                else:
                    sys.argv = ['fpaste', self.last_log_filename]
                    try:
                        short_url, url = fpaste.main()
                        APP_LOGGER.info(
                            'Class Log uploaded.\nFedora Paste URLs:\n\t1. Short:'
                                ' %s\n\t2. Long: %s', short_url, url
                        )
                        self.say(user.nick, url)
                    except:
                        self.say(user.nick, 'Hit a 500! I have a crash on you.')
                        APP_LOGGER.error(
                            'Log uploading to Fedora failed!', exc_info=True
                        )
            
            elif msg == '.help':
                padding_width = \
                    max([len(command) for command in commands.keys()])
                for command in commands.keys():
                    self.say(
                        user.nick,
                        utils.get_help_text(command, padding=padding_width+1)
                    )      

            elif msg.startswith('.link') and self.config.LINKS_ENABLED:
                self.links_for_key(msg)
        except:
            APP_LOGGER.error('Error parsing received message!', exc_info=True)
            self.say(self.channel, '500!')  # Quietly announce in channel.

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
        """Parse `msg` and and provide requested link (URL).

        Args:
            msg: Message to parse.
        """
        try:
            keyword = msg.split()[1]
            if not keyword:
                raise IndexError
        except IndexError:
            APP_LOGGER.error(
                'No keyword argument provided for `.link` command',
                exc_info=True)
            self.say(
                self.channel, '.link needs a keyword as argument. Check .help for details.'
            )
            return

        if keyword == 'reload':
            self.load_links()
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


