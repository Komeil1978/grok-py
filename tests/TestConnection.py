import grokpy
import unittest

class ConnectionTestCase(unittest.TestCase):

  def setUp(self):
    self.mockKey = 'SeQ9AhK57vOeoySQn1EvwElhZV1X87AB'

  def testGoodConnection(self):
    '''
    Basic connection without errors
    '''
    connection = grokpy.Connection(self.mockKey)
    
  def testNoKey(self):
    '''
    If you pass no key and one can't be found there should be an error
    '''
    badURI = 'floomer'
    self.assertRaises(grokpy.AuthenticationError,
                      grokpy.Connection)
  
  def testBadKey(self):
    '''
    A key that doesn't look right should throw an error immediately
    '''
    badKey = 'foo'
    self.assertRaises(grokpy.AuthenticationError,
                      grokpy.Connection, badKey)
