# stdlib imports
import os, sys
import unittest
import random

# library imports
import mock


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# local imports
from ekan0ra.bot import LogBot
from ekan0ra.user import IRCUser, InvalidUserError
from config import config_modes


config = config_modes.get('test')


class BotCommandsTest(unittest.TestCase):

    @mock.patch('ekan0ra.bot.create_app_logger') # Fake creation of app logger
    @mock.patch.object(LogBot, 'links_reload', auto_spec=True) # Fake links data load
    @mock.patch('ekan0ra.bot.get_logger_instance') # Fake logger creation
    @mock.patch('ekan0ra.bot.irc.IRCClient')
    def setUp(
            self, mock_irc_IRCClient, mock_get_logger_instance,
            mock_links_reload, mock_create_app_logger):
        ####TODO: Add more valid hostmask patterns to test
        self.validhostmasks = [
            'sawkateca!~sawkateca@41.203.71.181',
            '29cb47b5!29cb47b5@gateway/web/freenode/ip.41.203.71.181',
            'acetakwas!~acetakwas@41.203.71.181'
        ]
        ####TODO: Add more invalid hostmask patterns to test
        self.invalidhostmasks = [
            '~sawkateca@41.203.71.181',
            '29cb47b5@gateway/web/freenode/ip.41.203.71.181',
            '~acetakwas@41.203.71.181'
        ]


        self.assertFalse(
            mock_create_app_logger.called,
            'Create app logger was called too early')
        self.assertFalse(
            mock_links_reload.called,
            'Reload links was called too early')
        self.assertFalse(
            mock_get_logger_instance.called,
            'Get logger instance was called too early')
        self.bot = LogBot(config)
        self.bot.connectionMade()
        self.bot.islogging = True # Fake logging
        
        mock_irc_IRCClient.connectionMade.assert_called_with(self.bot)
        mock_create_app_logger.assert_called_with(config)

    @mock.patch('ekan0ra.bot.irc.IRCClient')
    @mock.patch.object(LogBot, 'describe', auto_spec=True) # Fake links data load
    def test_question_queue(self, mock_describe, mock_irc_IRCClient):
        self.assertListEqual([], self.bot.qs_queue)
        hostmask = self.validhostmasks[0]
        self.bot.privmsg(hostmask, self.bot.channel, '!')
        assert(mock_describe.called)
        self.assertIn(IRCUser(self.bot, hostmask).nick, self.bot.qs_queue)
        self.bot.privmsg(hostmask, self.bot.channel, '!!')
        assert(mock_describe.called)
        self.assertListEqual([], self.bot.qs_queue)
        self.bot.privmsg(hostmask, self.bot.channel, '!')
        assert(mock_describe.called)
        self.assertIn(IRCUser(self.bot, hostmask).nick, self.bot.qs_queue)
        self.bot.privmsg(hostmask, self.bot.channel, '!-')
        assert(mock_describe.called)
        self.assertListEqual([], self.bot.qs_queue)


    # def test_hostmask_parsing(self):
    #     for hostmask in self.invalidhostmasks:
    #         self.assertRaises(InvalidUserError, IRCUser, self.bot, hostmask)
    #     for hostmask in self.validhostmasks:
    #         self.assertIsInstance(IRCUser(self.bot, hostmask), IRCUser, msg='Could not parse: %s' %hostmask)

    # def test_default_admins_works(self):
    #     self.assertEquals(list(config.ADMINS), self.bot.channel_admins_list)

    # def test_not_admin_by_default(self):
    #     nick = random.choice(self.validhostmasks)
    #     self.user = IRCUser(self.bot, nick)
    #     self.assertIsInstance(self.user, IRCUser)
    #     # New user should not be an admin by default
    #     # unless listed as a default admin in config
    #     if nick not in config.ADMINS:
    #         self.assertFalse(self.user.is_admin())
    #         self.bot.channel_admins_list.append(self.user.nick)
    #         self.assertTrue(self.user.is_admin())
    #     else:
    #         self.assertTrue(self.user.is_admin())

        

    # def tearDown(self):
    #     self.bot.stoplogging()
    #     self.bot.quit()


def main():
    unittest.main()


if __name__ == '__main__':
    unittest.main()