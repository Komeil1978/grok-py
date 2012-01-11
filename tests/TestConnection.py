import grokpy
import unittest

from grokpy.connection import Connection
from grokpy.exceptions import AuthenticationError

class ConnectionTestCase(unittest.TestCase):

  def setUp(self):
    self.mockKey = 'SeQ9AhK57vOeoySQn1EvwElhZV1X87AB'

  def testGoodConnection(self):
    '''
    Basic connection without errors
    '''
    connection = Connection(self.mockKey)
    
  def testNoKey(self):
    '''
    If you pass no key and one can't be found there should be an error
    '''
    self.assertRaises(AuthenticationError,
                      Connection)
  
  def testBadKey(self):
    '''
    A key that doesn't look right should throw an error immediately
    '''
    badKey = 'foo'
    self.assertRaises(AuthenticationError,
                      Connection, badKey)
    
if __name__ == '__main__':
  debug = 0
  if debug:
    single = unittest.TestSuite()
    single.addTest(ConnectionTestCase('testGoodConnection'))
    unittest.TextTestRunner().run(single)
  else:
    unittest.main()
