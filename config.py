"""Configuration for the bot."""

import os

# template string for building string 
# representations for config classes
running_mode = 'App running in {mode} mode. With configs:\n{configs}'

def get_admins(default_admins):
    admins = os.getenv('LOGBOT_ADMINS', None)
    if admins is not None:
        admins = admins.split()
    else:
        admins = default_admins
    return admins


# Base configuration class that
# will be extended
class Config:
    LOG_FILENAME = 'Logs-{}.txt'
    CLASS_LOGGER_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_PREFIX = '[{}]'

    SESSION_START_MSG = '----------SESSION STARTS----------'
    SESSION_END_MSG = '----------SESSION ENDS----------'

    BASE_TOPIC = "Welcome to Linux User's Group of Durgapur | Mailing list at http://lists.dgplug.org/listinfo.cgi/users-dgplug.org | Old classes https://www.dgplug.org/irclogs/ | https://docs.python.org/3/tutorial/ | https://dgplug.org/summertraining16/"

# Configuration used during
# the development of our bot
class DevConfig(Config):

    BOTNICK = os.getenv('LOGBOT_NICK', 'sawkateca')
    CHANNEL = os.getenv('LOGBOT_CHANNEL', '#test-my-bot') # #test-my-bot is not a registered channel.
    ADMINS = get_admins(('acetakwas', ))

    def __repr__(self):
        data = self.__class__.__dict__.copy()
        #data['mode'] = 'development'
        data.pop('__doc__', None)
        data.pop('__repr__', None)
        data.pop('__module__', None)
        return running_mode.format(mode='development', configs=data)


# Configuration for testing the functionalities
# of our bot
class TestConfig(Config):

    BOTNICK = os.getenv('LOGBOT_NICK', 'sawkat')
    CHANNEL = os.getenv('LOGBOT_CHANNEL', '#botters-test')
    ADMINS = get_admins(('acetakwas', ))

    def __repr__(self):
        data = self.__class__.__dict__.copy()
        #data['mode'] = 'testing'
        data.pop('__doc__', None)
        data.pop('__repr__', None)
        data.pop('__module__', None)
        return running_mode.format(mode='testing', configs=data)
    

# Main configuration for when our bot is deployed on a server
class DeployConfig(Config):

    BOTNICK = os.getenv('LOGBOT_NICK', 'batul') # The nick of the bot.
    CHANNEL = os.getenv('LOGBOT_CHANNEL', '#dgplug')
    ADMINS = get_admins(('kushal','sayan','mbuf','rtnpro','chandankumar','praveenkumar', )) # List of IRC nicks as masters.

    def __repr__(self):
        data = self.__class__.__dict__.copy()
        #data['mode'] = 'deploy'
        data.pop('__doc__', None)
        data.pop('__repr__', None)
        data.pop('__module__', None)
        return running_mode.format(mode='deploy', configs=data)


config_modes = {
    'default' : DevConfig,
    'dev' : DevConfig,
    'deploy' : DeployConfig,
    'test' : TestConfig
}