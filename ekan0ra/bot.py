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
from .queue import Queue
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
        self.qs_queue = Queue()       
        self.load_links()
        self.logger = get_logger_instance()
        self.last_log_filename = self.logger.filename
        self.fpaste_url = None
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
                    datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
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
            APP_LOGGER.info('Uploading log to Fedora Paste server...')
            result = self.logger.pastebin_log(logger=APP_LOGGER)
            if result is not None:
                self.fpaste_url = result[1]
                APP_LOGGER.info('Upload was succesful.\n\tURL: %s',
                    self.fpaste_url)
            else:
                self.fpaste_url = None
                APP_LOGGER.warning('Upload failed!')
            self.logger.close()
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

        `channel` can either be an IRC channel or a user's nick.
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

    def show_queue_status(self, channel=None):
        """Show the users still in the question queue."""
        if channel is None:
            channel = self.channel
        self.describe(channel, 'Queue: %r' % self.qs_queue)

    def privmsg(self, hostmask, channel, msg):
        """Called when the bot receives a message."""
        # Message parsing could break the bot, let's `try/catch` this
        try:
            user = IRCUser(self, hostmask) # parse user object from given hostmask `user`
            msg = msg.strip()
            APP_LOGGER.info(
                'MESSAGE:\t%s\nSENDER:\t%s\nCHANNEL:\t%s', msg, user.nick, channel
            )

            # `channel == self.nickname`
            # determines if a message is a private message
            if self.islogging and not channel == self.nickname:
                # Don't log private messages with class log
                self.logger.log(
                    '<%{}s> %s'.format(self.config.CLASS_LOG_NICK_PADDING) % 
                    (user.nick, msg))

        
            # Is the message sender an admin?
            if user.is_admin():
            # process message from admin

                if msg.lower().startswith('.startclass') and \
                        channel == self.nickname:
                    if not self.islogging:
                        arg_pos = msg.find(' ')
                        if arg_pos >= 0:
                            topic = msg[arg_pos:].strip()
                        else:
                            topic = None
                        if self.startlogging(topic):
                            self.clearqueue()
                            self.say(
                                user.nick,
                                'Session logging started successfully!'
                            )
                            self.say(
                                self.channel, self.config.SESSION_START_MSG
                            ) 
                            if topic is not None:
                                self.say(self.channel, 'TOPIC: %s' % topic)
                            self.say(self.channel, 'Roll Call...')
                            self.log_issuer = user.nick
                        else:
                            self.say(user.nick, 'Logging failed to start!')
                    else:
                        self.say(
                            user.nick,
                            'Session logging already started by %s. No extra '
                                'logging started.' % self.log_issuer
                        )
                    
                elif msg.lower().endswith('.endclass') and \
                        channel == self.nickname:
                    if self.stoplogging():
                        self.say(
                            user.nick,
                            'Session logging terminated successfully!'
                        )
                        self.say(self.channel, self.config.SESSION_END_MSG)
                    else:
                        self.say(user.nick, 'Logging failed to terminate!')

                elif msg == '.clearqueue' and \
                        channel == self.nickname:
                    self.clearqueue()
                    self.say(self.channel, 'Queue is cleared.')

                elif msg == '.showqueue' and \
                        channel == self.nickname:
                    self.show_queue_status(user.nick)
                
                elif msg == '.next' and not self.islogging:
                    self.say(
                        channel,
                        '%s: No session is going on. No one is in queue.' %
                            user.nick
                    )

                elif msg == '.next' and self.islogging:
                    if self.qs_queue.has_next():
                        nick = self.qs_queue.pop_next()
                        msg = '%s: Please ask your question.' % nick
                        if self.qs_queue.has_next():
                            msg = '%s\n%s: You are next. Get ready with ' \
                                'your question.' % (
                                    msg, self.qs_queue.peek_next())
                        self.say(self.channel, msg)
                        if self.config.SHOW_QUEUE_STATUS_ENABLED:
                            self.show_queue_status(channel)
                    else:
                        self.say(self.channel, 'No one is in queue.')

                elif msg == '.masters' and \
                        channel == self.nickname:
                    self.say(
                        self.channel,
                        'My current masters are: %s' %
                            ', '.join(self.channel_admins_list)
                    )

                elif msg.startswith('.add') and \
                        channel == self.nickname:
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

                elif msg.startswith('.rm') and \
                        channel == self.nickname:
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
                        self.config.PINGALL_ENABLED and not \
                        channel == self.nickname:
                    self.pingmsg = msg.lower().lstrip('.pingall')
                    self.names(channel).addCallback(self.pingall)

                elif msg.startswith('.link') and self.config.LINKS_ENABLED and
                        channel == self.nickname:
                    self.links_for_key(msg, channel=user.nick)
            # end processing admin message


            # User wants to ask a question
            if msg == '!' and self.islogging and not \
                    channel == self.nickname:
                self.qs_queue.enqueue(user.nick)
                if self.config.SHOW_QUEUE_STATUS_ENABLED:
                    self.show_queue_status(channel)

            # User no longer wants to ask a question; remove them from queue
            elif msg in ('!-', '!!') and self.islogging and \
                    self.config.LEAVE_QUEUE_ENABLED and not \
                    channel == self.nickname:
                result = self.qs_queue.dequeue(user.nick)
                if result == True and \
                        self.config.SHOW_QUEUE_STATUS_ENABLED:
                    self.show_queue_status(channel)

            elif msg in ('!', '!-', '!!') and not self.islogging:
                self.say(
                    channel,
                    '%s: No session is going on, feel free to ask a '
                    'question. You do not have to type %s' % (user.nick, msg)
                )
            # end processing question indicator   

            elif msg == '.givemelogs' and self.config.GIVEMELOGS_ENABLED:
                if self.fpaste_url is None:
                    self.say(user.nick, 'Sorry, I do not have the last log.')
                    APP_LOGGER.warning('Could not find last class log!')
                else:
                    self.say(user.nick, 'View last class log here: %s' %
                        self.fpaste_url)
            
            elif msg == '.help':
                padding_width = \
                    max([len(command) for command in commands.keys()])
                for command in commands.keys():
                    self.say(
                        user.nick,
                        utils.get_help_text(command, padding=padding_width+1)
                    )      
        except:
            APP_LOGGER.error('Error parsing/processing received message!',
                exc_info=True)
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
    def links_for_key(self, msg, channel=None):
        """Parse `msg` and provide requested link (URL).

        Args:
            msg: Message to parse.
        """
        channel = self.channel if channel is None
        try:
            keyword = msg.split()[1]
            if not keyword:
                raise IndexError
        except IndexError:
            APP_LOGGER.error(
                'No keyword argument provided for `.link` command',
                exc_info=True)
            self.say(
                channel, '.link needs a keyword as argument. Check .help for details.'
            )
            return

        if keyword == 'reload':
            self.load_links()
        elif keyword in ['-l', 'help']:
            self.say(
                channel,
                'Valid options for `.link`:\t[%s]' %
                    str(', '.join(self.links_data.keys()))
            )
        else:
            self.say(
                channel,
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


