import re


class User(object):
    """
    Represents a `User` object; contains info about user:
        nick,
        ident,
        mask
    """

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
        return 'User [Nick: %s; Ident: %s; Mask: %s]' % (self.nick, self.ident, self.mask)

    def is_admin(self):
        """Ask bot who created this `User` if they've made this `User` an admin."""
        return self.nick in self.bot.channel_admins_list


class InvalidUserError(Exception):
    pass
