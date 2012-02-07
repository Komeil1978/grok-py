import grokpy
import unittest

from grokpy.connection import Connection
from grokpy.exceptions import AuthenticationError, GrokError

class ConnectionTestCase(unittest.TestCase):

  def setUp(self):
    self.mockKey = 'SeQ9AhK57vOeoySQn1EvwElhZV1X87AB'

  def testGoodConnection(self):
    '''
    Basic connection without errors
    '''
    connection = Connection(self.mockKey)

  def testBadKey(self):
    '''
    A key that doesn't look right should throw an error immediately
    '''
    badKey = 'foo'
    self.assertRaises(AuthenticationError,
                      Connection, badKey)

  def testNon200Response(self):
    '''
    If the HTTP response isn't 200 we should throw an error
    '''

    # Mock out HTTP Client
    class mockHTTPClient(object):
      def request(self, **kwargs):
        return {'status': 404}, 'mockContent'

    c = MockConnection(mockHTTPClient)

    # Define a minimal request
    requestDef = {'service': 'projectList'}

    self.assertRaises(GrokError, c.request, requestDef)

class MockConnection(Connection):
  '''
  Allows a test to override the http client that the standard connection uses.

  Think of it as adding dependency injection after the fact.
  '''

  def __init__(self, mockHTTPClient):
    self.mockHTTPClient = mockHTTPClient

    # Bring in all the parent class attributes
    Connection.__init__(self)

  def _getHTTPClient(self):
    return self.mockHTTPClient()


if __name__ == '__main__':
  debug = 0
  if debug:
    single = unittest.TestSuite()
    single.addTest(ConnectionTestCase('testGoodConnection'))
    unittest.TextTestRunner().run(single)
  else:
    unittest.main()
