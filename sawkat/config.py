"""Configuration for the bot."""

# template string for building string 
# representations for config classes
running_mode = 'App running in {mode} mode.'


# Base configuration class that
# will be extended
class Config:

    LINKS_FILE = os.path.join(os.path.abspath(os.curdir), 'links.json')


# Configuration used during
# the development of our bot
class DevConfig(Config):

    # standard library imports
    import os


    BOTNICK = 'sawkat'

    DEFAULT_CHANNEL_ADMINS = ('acetakwas', )

    DEFAULT_CHANNELS = ('#test-my-bot', '#test-bot', '#botters', )    # #test-my-bot is not a registered channel.

    


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