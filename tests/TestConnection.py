import grokpy
import unittest
import socket
import base64
import grokpy.requests as requests

from mock import Mock

from groktestcase import GrokTestCase
from grokpy.connection import Connection
from grokpy.exceptions import AuthenticationError, GrokError

class ConnectionTestCase(GrokTestCase):

  def setUp(self):
    self.mockKey = 'SeQ9AhK57vOeoySQn1EvwElhZV1X87AB'

    base64string = base64.encodestring(self.mockKey + ':').replace('\n', '')
    headers = {"Authorization": "Basic %s" % base64string,
                 "Content-Type": 'application/json; charset=UTF-8'}
    self.s = requests.session(headers=headers)

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

    self.assertEqual(c.baseURL, 'http://grok-api.numenta.com/version/1/')

    c2 = Connection(self.mockKey, 'http://www.example.com')

    self.assertEqual(c2.baseURL, 'http://www.example.com/version/1/')

  def testBadKey(self):
    '''
    A key that doesn't look right should throw an error immediately
    '''
    badKey = 'foo'
    self.assertRaises(AuthenticationError,
                      Connection, badKey)

  def testBasicRequest(self):
    '''
    Make sure we are building the HTTP request properly
    '''

    # Create our Mock HTTP Client
    mock = Mock(spec=self.h)

    # Define it's responses
    mock.request.return_value = ({'status': '200'}, '{"result": "success"}')

    # Make the request
    c = Connection(self.mockKey, httpClient = mock)
    requestDef = {'service': 'projectList'}
    c.request(requestDef)

    # Assert our Mock HTTP Client was called with expected values
    mock.request.assert_called_with(body = '{"version": "1", "service": "projectList"}',
                                    headers = {'content-type': 'application/json', 'API-Key': self.mockKey},
                                    uri = 'http://grok-api.numenta.com/version/1/',
                                    method = 'POST')

  def testBasicGETRequest(self):
    '''
    Make sure we are building GET requests properly
    '''

    # Create our Mock HTTP Client
    mock = Mock(spec=self.h)

    # Define it's responses
    mock.request.return_value = ({'status': '200'}, '{"result": "success"}')

    # Make the request
    c = Connection(self.mockKey, httpClient = mock)
    requestDef = {'service': 'projectList'}
    c.request(requestDef, 'GET')

    # Assert our Mock HTTP Client was called with expected values
    mock.request.assert_called_with(headers = {'API-Key': self.mockKey},
                                    uri = 'http://grok-api.numenta.com/version/1/service/projectList',
                                    method = 'GET')

  def testUnsupportedHTTPMethod(self):
    '''
    This version only allows GET and POST
    '''

    c = Connection(self.mockKey)

    requestDef = {'service': 'projectList'}

    self.assertRaises(GrokError, c.request, requestDef, 'PUT')

  def testHTTPRequestTimeOut(self):
    '''
    We should throw an error on socket timeouts
    '''

    # Create our Mock HTTP Client
    mock = Mock(spec=self.h)

    # Define a side effect
    mock.request.side_effect = socket.error('This request has timed out')

    c = Connection(self.mockKey, httpClient = mock)
    requestDef = {'service': 'projectList'}

    self.assertRaises(GrokError, c.request, requestDef)

  def testUnknownHTTPRequestError(self):
    '''
    We should catch and wrap all socket.error's and pass them back as
    GrokErrors
    '''

    # Create our Mock HTTP Client
    mock = Mock(spec=self.h)
    # Define a side effect
    mock.request.side_effect = socket.error('Foobar')

    c = Connection(self.mockKey, httpClient = mock)
    requestDef = {'service': 'projectList'}

    self.assertRaisesRegexp(GrokError, 'Foobar', c.request, requestDef)

  def testNon200Response(self):
    '''
    If the HTTP response isn't 200 we should throw an error
    '''

    # Create our Mock HTTP Client
    mock = Mock(spec=self.h)
    # Define it's responses
    mock.request.return_value = ({'status': '404'}, '{"result": "Error"}')

    # Make the request
    c = Connection(self.mockKey, httpClient = mock)
    requestDef = {'service': 'projectList'}

    # Assert an error is raised
    self.assertRaises(GrokError, c.request, requestDef)

  def testAPIError(self):
    '''
    We should handle error messages the API returns
    '''

    # Create our Mock HTTP Client
    mock = Mock(spec=self.h)
    # Define it's responses
    mock.request.return_value = ({'status': '200'}, '{"errors": "EC2 is dead"}')

    # Make the request
    c = Connection(self.mockKey, httpClient = mock)
    requestDef = {'service': 'projectList'}

    # Assert an error is raised
    self.assertRaisesRegexp(GrokError, 'EC2 is dead', c.request, requestDef)

  def testAPIInformationResponse(self):
    '''
    The API might not return a result or an error, but instead an information
    level response. This should be returned to the user.
    '''

    # Create our Mock HTTP Client
    mock = Mock(spec=self.h)
    # Define it's responses
    infoString = "EC2 is neat!"
    JSON = '{"information": ["'+infoString+'"]}'
    mock.request.return_value = ({'status': '200'}, JSON)

    # Make the request
    c = Connection(self.mockKey, httpClient = mock)
    requestDef = {'service': 'projectList'}

    self.assertEquals(c.request(requestDef), infoString)

  def testGarbageAPIResponse(self):
    '''
    Something has really gone wrong and we've returned crap
    '''

    # Create our Mock HTTP Client
    mock = Mock(spec=self.h)
    # Define it's responses
    mock.request.return_value = ({'status': '200'}, '{}')

    # Make the request
    c = Connection(self.mockKey, httpClient = mock)
    requestDef = {'service': 'projectList'}

    # Assert an error is raised
    self.assertRaisesRegexp(GrokError, 'Unexpected request response:{}', c.request, requestDef)

if __name__ == '__main__':
  debug = 0
  if debug:
    single = unittest.TestSuite()
    single.addTest(ConnectionTestCase('testGoodKey'))
    unittest.TextTestRunner().run(single)
  else:
    unittest.main()
