#!/usr/bin/env python
"""Module to run the tests"""


# standard library imports
#import unittest


# THIS FAILS!!!
from sawkat.tests import test_utils


if __name__ == '__main__':
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    import sawkat
    pass
    #unittest.main()