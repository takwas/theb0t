# standard library imports
import unittest

##########################
# TEMPORARY CODE         #
##########################
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
##########################
# END TEMPORARY CODE     #
##########################

# local imports
from sawkat.actions import *


class TestActions(unittest.TestCase):

    def test_do_help(self):

        self.assertEqual(do_help('paste'), 'some crap')
        self.assertEqual(do_help('past'), 'Showing help for command: <:paste>')

    
    def test_do_about(self):

        self.assertEqual(do_about('paste'), 'some crap')
        self.assertEqual(do_about('paste'), 'Showing help for command: <:paste>')

    
    def test_do_inbox(self):

        self.assertEqual(do_inbox('paste'), 'some crap')
        self.assertEqual(do_inbox('paste'), 'Showing help for command: <:paste>')

    
    def test_do_link(self):

        self.assertEqual(do_link('paste'), 'some crap')
        self.assertEqual(do_link('paste'), 'Showing help for command: <:paste>')

    
    def test_do_log(self):

        self.assertEqual(do_log('paste'), 'some crap')
        self.assertEqual(do_log('paste'), 'Showing help for command: <:paste>')


    def test_do_masters(self):

        self.assertEqual(do_masters('paste'), 'some crap')
        self.assertEqual(do_masters('paste'), 'Showing help for command: <:paste>')


    def test_do_paste(self):

        self.assertEqual(do_paste('paste'), 'some crap')
        self.assertEqual(do_paste('paste'), 'Showing help for command: <:paste>')

    
    def test_do_recall(self):

        self.assertEqual(do_recall('paste'), 'some crap')
        self.assertEqual(do_recall('paste'), 'Showing help for command: <:paste>')

    
    def test_do_resource(self):

        self.assertEqual(do_resource('paste'), 'some crap')
        self.assertEqual(do_resource('paste'), 'Showing help for command: <:paste>')

    
    def test_do_submit(self):

        self.assertEqual(do_submit('paste'), 'some crap')
        self.assertEqual(do_submit('paste'), 'Showing help for command: <:paste>')

    
    



if __name__ == '__main__':

    unittest.main()