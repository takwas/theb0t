#!/usr/bin/env python
"""Module to run the tests"""


# standard library imports
#import unittest


# THIS FAILS!!!
#from sawkat.tests import test_utils


if __name__ == '__main__':
    
    # THIS IS THE FIX I HAVE FOR NOW; ADDING THE PATH
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    
    import sawkat
    from sawkat.tests import test_utils
    
    #unittest.main()