# standard library imports
#import unittest

# THIS IS THE FIX I HAVE FOR NOW; ADDING THE PATH
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# local imports
from tests import config
from sawkat import create_bot
print "IMPORTED"

# class UtilsTest(unittest.TestCase):

#     def setup():
        
#         bot = create_bot(config=config)
        
#     def test_verify_channel():
#         self.assertEqual(verify_channel("#chan"), "chan")

# #    def test_get_link_names(links_data):




if __name__ == '__main__':

    # THIS IS THE FIX I HAVE FOR NOW; ADDING THE PATH
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

    unittest.main()