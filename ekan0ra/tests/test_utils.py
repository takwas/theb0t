# standard library imports
import unittest

# local imports
from tests import config
from ekan0ra import create_bot

class UtilsTest(unittest.TestCase):

    def setup():
        
        bot = create_bot(config=config)
        
    def test_verify_channel():
        self.assertEqual(verify_channel("#chan"), "chan")

#    def test_get_link_names(links_data):

