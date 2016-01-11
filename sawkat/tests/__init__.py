"""
    Testing module for our bot. ;)
"""


# local imports
# THIS FAILS!!!
#from sawkat import config as conf


#config = conf.config_modes.get('test')


#!/usr/bin/env python
"""Module to run the tests"""


# standard library imports
#import unittest


# THIS FAILS!!!
#from sawkat.tests import test_utils


if __name__ == '__main__':
    
    # THIS IS THE FIX I HAVE FOR NOW; ADDING THE PATH
    import sys, os
    for path in sys.path:
        print path
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    
    print
    print
    for path in sys.path:
        print path
    import sawkat
    from sawkat.tests import test_utils
    
    #unittest.main()