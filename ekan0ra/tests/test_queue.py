# stdlib imports
import os, sys
import unittest
import random

# library imports
import mock


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# local imports
from ekan0ra.queue import QuestionQueue


class QueueTest(unittest.TestCase):

    @mock.patch('ekan0ra.bot.create_app_logger') # Fake creation of app logger
    def setUp(self, mock_create_app_logger):
        self.qq = QuestionQueue()
        self.assertListEqual([], self.qq) # Ensure queue is initially empty
    
    def test_enqueue(self):
        self.qq.enqueue(1) # Add item to queue
        self.assertListEqual([1], self.qq)

    def test_dequeue(self):
        items = list(set(range(5))) # unique set of items
        # Add items to queue
        for i in items:
            self.qq.enqueue(items[i]) 

        item = random.choice(items)
        self.qq.dequeue(item) # Remove random item from queue
        self.assertNotIn(item, self.qq) # confirm dequeue

    def test_has_next(self):
        # Being initially empty, queue should have no next item
        self.assertFalse(self.qq.has_next())
        
        # Add item to queue and check that queue now has a next item
        self.qq.enqueue(1)
        self.assertTrue(self.qq)
        self.assertTrue(self.qq.has_next())

    def tearDown(self):
        del self.qq
    

def main():
    unittest.main()


if __name__ == '__main__':
    unittest.main()