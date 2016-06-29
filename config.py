"""Configuration for the bot."""

# template string for building string 
# representations for config classes
running_mode = 'App running in {mode} mode.'


# Base configuration class that
# will be extended
class Config:

    pass


# Configuration used during
# the development of our bot
class DevConfig(Config):

    BOTNICK = 'sawkateca'
    ADMINS = ('acetakwas', )
    CHANNEL = '#test-my-bot'    # #test-my-bot is not a registered channel.
    LOG_FILENAME_PREFIX = 'Logs-{}.txt'
    LOGGER_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_PREFIX = '[{}]'

    SESSION_START_MSG = '----------SESSION STARTS----------'
    SESSION_END_MSG = '----------SESSION ENDS----------'



    def __repr__(self):

        return running_mode.format(mode='development')


# Configuration for testing the functionalities
# of our bot
class TestConfig(Config):

    BOTNICK = 'sawkat'

    DEFAULT_CHANNEL_ADMINS = ('acetakwas', )

    DEFAULT_CHANNELS = ('#botters-test', )


    def __repr__(self):

        return running_mode.format(mode='testing')


# Main configuration for when our bot is deployed on a server
class DeployConfig(Config):

    BOTNICK = 'batul' # The nick of the bot.

    DEFAULT_CHANNEL_ADMINS = ('kushal','sayan','mbuf','rtnpro','chandankumar','praveenkumar', ) # List of IRC nicks as masters.

    DEFAULT_CHANNELS = ('#dgplug', )
    

    def __repr__(self):

        return running_mode.format(mode='deploy')


config_modes = {
    'default' : DevConfig,
    'dev' : DevConfig,
    'deploy' : DeployConfig,
    'test' : TestConfig
}