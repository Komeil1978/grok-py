import unittest
import grokpy.requests as requests
import json

from mock import Mock, patch, sentinel

from grok_test_case import GrokTestCase
import grokpy
from grokpy.connection import Connection
from grokpy.exceptions import AuthenticationError, GrokError

class ConnectionTestCase(GrokTestCase):

  def setUp(self):
    self.mockKey = 'g1gCaM3PLRze6wuCtqSqQb5l41k06h3r'
    self.mockSession = Mock(spec = requests.session())
    self.mockResponse = Mock(spec = requests.Response())

  def testGoodKey(self):
    '''
    This key should pass validity checks.
    '''
    c = Connection(self.mockKey)

    self.assertEqual(c.key, self.mockKey)

  def testBaseURL(self):
    '''
    Verify expected base URL and one we pass in
    '''
    c = Connection(self.mockKey)

    self.assertEqual(c.baseURL, 'https://api.numenta.com/v2')

    c2 = Connection(self.mockKey, 'https://www.example.com')

    self.assertEqual(c2.baseURL, 'https://www.example.com/v2')

  def testHTTPSRequirement(self):
    '''
    Passing in an http url should raise a GrokError
    '''

    self.assertRaises(GrokError,
                      Connection,
                      self.mockKey,
                      'http://www.example.com')

  def testBadKey(self):
    '''
    A key that doesn't look right should throw an error immediately
    '''
    badKey = 'foo'
    self.assertRaises(AuthenticationError,
                      Connection,
                      badKey)

  def testMissingKey(self):
    '''
    If you've left the default and haven't set a ENV key we should throw an
    error
    '''
    mockKey = 'YOUR_KEY_HERE'

    # Monkey patch the connection class. A dev running these tests will
    # probably have a key in their environment. We want this check to fail.
    def mp(self):
      return None

    Connection._find_key = mp

    self.assertRaises(AuthenticationError, Connection, mockKey)

  def testRequestGET(self):
    '''
    Make sure a basic GET returns code as expected
    '''

    # Define responses
    response = {'users': 'idanforth@numenta.com'}
    responseJSON = json.dumps(response)
    self.mockResponse.text = responseJSON
    self.mockSession.get.return_value = self.mockResponse

    # Make the request
    c = Connection(self.mockKey, session = self.mockSession)
    rv = c.request('GET', '/users')

    # Make sure we get out what we put in
    self.assertEqual(rv, response)

  def testRequestPOST(self):
    '''
    Make sure a basic POST returns as expected
    '''

    # Define responses
    response = {'model': {}}
    responseJSON = json.dumps(response)
    self.mockResponse.text = responseJSON
    self.mockSession.post.return_value = self.mockResponse

    # Make the request
    requestDef = {'model': 'modelSpec'}
    c = Connection(self.mockKey, session = self.mockSession)
    rv = c.request('POST', '/models', requestDef)

    # Make sure we get out what we put in
    self.assertEqual(rv, response)

  def testRequestDELETE(self):
    '''
    Make sure basic DELETE returns properly
    '''

    # Define responses
    response = {'ok': True}
    responseJSON = json.dumps(response)
    self.mockResponse.text = responseJSON
    self.mockSession.delete.return_value = self.mockResponse

    # Make the request
    c = Connection(self.mockKey, session = self.mockSession)
    rv = c.request('DELETE', '/model/foo')

    # Make sure we get out what we put in
    self.assertEqual(rv, response)

  def testRequestPUT(self):
    '''
    PUT Should raise a Grok error as we don't use it today
    '''
    # Make the request
    c = Connection(self.mockKey, session = self.mockSession)
    self.assertRaises(GrokError,
                      c.request,
                      'PUT',
                      '/models')

  def testMissingCertifi(self):
    '''
    If the certifi module isn't present we should raise a GrokError
    '''

    self.mockSession.get.side_effect = ImportError('Missing module')

    c = Connection(self.mockKey, session = self.mockSession)
    self.assertRaises(GrokError, c.request, 'GET', '/users')

  def testResponseStatusNotOK(self):
    '''
    If the status of the response is not 'ok' as determined by the requests lib
    we should forward on the underlying error
    '''

    response = {'error': 'Monkeys! Everywhere!'}
    responseJSON = json.dumps(response)
    self.mockResponse.text = responseJSON
    self.mockResponse.ok = False
    self.mockResponse.raise_for_status = Exception
    self.mockSession.get.return_value = self.mockResponse

    # Check we get the correct error text out
    c = Connection(self.mockKey, session = self.mockSession)
    self.assertRaisesRegexp(Exception, responseJSON, c.request, 'GET', '/users')

  def testNewRequestSessionCreatedWithUserSpecifiedHeaders(self):
    '''
    User can optionally specify headers to be sent along with all requests
    coming from a particular Connection object.
    '''

    mockSessionFunction = Mock(return_value=sentinel.some_object)

    with patch.object(grokpy.connection.requests, 'session', mockSessionFunction):
      grokpy.connection.Connection(self.mockKey,
        'https://www.example.com',
        # sending no session so one is created so we can test the headers it gets
        session = None,
        headers = {'x-test-header': 'header val'})

    sessionArgs = mockSessionFunction.call_args[1]
    self.assertIsInstance(sessionArgs, dict, 'session must be send headers dict')
    headers = sessionArgs['headers']
    self.assertIsInstance(headers, dict, 'session headers object must be a dict')
    self.assertTrue('x-test-header' in headers, 'headers object missing user-specified header')
    self.assertEqual('header val', headers['x-test-header'], 'bad custom header value')

if __name__ == '__main__':
  debug = 0
  if debug:
    single = unittest.TestSuite()
    single.addTest(ConnectionTestCase('testRequestPUT'))
    unittest.TextTestRunner().run(single)
  else:
    unittest.main()
