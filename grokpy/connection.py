import os
import json
import requests
import base64
import grokpy

from exceptions import GrokError, AuthenticationError

class Connection(object):
  '''
  Connection object for the Grok Prediction Service
  '''

  def __init__(self,
               key = None,
               baseURL = 'https://api.numenta.com/',
               session = None):
    '''
    key - Grok API Key
    baseURL - Grok server request target
    session - A requests lib Session instance. Useful for testing.
    '''

    # Search for API key in environment
    if not key or key == 'YOUR_KEY_HERE':
      key = self._find_key()
      if not key:
        raise AuthenticationError("""
          Please supply your API key.

          Method 1:
            Supply your credentials when you instantiate the connection.

            connection = %s(key='YOUR_KEY_HERE')

          Method 2:
          (More Secure)

            Add your credentials to your shell environment. From the command
            line:

            echo "export GROK_API_KEY=YOUR_KEY_HERE" >> ~/.bashrc
            source ~/.bashrc

            For either method please replace the dummy key value with your real
            key from your account page.

            http://grok.numenta.com/account""" % self.__class__.__name__)
    else:
      self._validateKey(key)

    # The API key we'll use to authenticate all HTTP calls.
    self.key = key
    if grokpy.DEBUG:
      print 'Using API Key'
      print key

    # The base path for all our HTTP calls
    if baseURL[-1] != '/':
      baseURL += '/'
    self.baseURL = baseURL + 'v2'

    # Require https
    if baseURL[:5] != 'https' and baseURL[:16] != 'http://localhost':
      raise GrokError('Please supply an HTTPS URL to override the default.')

    # The HTTP Client we'll use to make requests
    if not session:
      base64string = base64.encodestring(self.key + ':').replace('\n', '')
      agent = "Grok API Client - Python - Version %s" % grokpy.__version__
      headers = {"Authorization": "Basic %s" % base64string,
                 "Content-Type": 'application/json; charset=UTF-8',
                 "User-Agent": agent}
      session = requests.session(headers=headers)

    self.s = session

  def request(self, method, url, requestDef = None, params = None):
    '''
    Interface for all HTTP requests made to the Grok API
    '''

    if url[:4] != 'http':
      url = self.baseURL + url

    # JSON serialize the requestDef object
    requestDef = json.dumps(requestDef, ensure_ascii=False)

    if grokpy.DEBUG:
      print method
      print url
      print requestDef

    try:
      # Make the request, handle initial connection errors
      if method == 'GET':
        response = self.s.get(url, params = params)
      elif method == 'POST':
        response = self.s.post(url, requestDef)
      elif method == 'DELETE':
        response = self.s.delete(url)
      else:
        raise GrokError('Unsupported HTTP method: %s' % method)
    except ImportError:
      raise GrokError('The certifi module is required to use grokpy. Please '
                      'install it by running "sudo pip install certifi". If '
                      'you get an "unknown command" error. Please install pip '
                      'by running "sudo easy_install pip", then rerun the '
                      'first command.')

    if not response.ok:
      raise response.raise_for_status(response.text)

    # Load info from returned JSON strings
    content = json.loads(response.text)

    if grokpy.DEBUG >= 1:
      print content

    return content

  ###########################################################################
  # Private Methods

  def _find_key(self):
    '''
    Retrieve an API key from the user's shell environment
    '''
    try:
      key = os.environ["GROK_API_KEY"]
    except KeyError:
      return None

    return key

  def _validateKey(self, key):
    '''
    Makes sure that a given key conforms to the expected format
    '''

    if len(key) < 5:
      raise AuthenticationError('This key is too short, '
                                'please check it again: "' + key +'"')
    else:
      return 'OK'

  ###########################################################################
  # Debugging hooks
  #
  # See http://docs.python-requests.org/en/latest/user/advanced/#event-hooks

  def _printHeaders(self, args):
    '''
    Event hook to print the headers of a request. Pass this to the request
    method like this::

      requests.get('http://httpbin.org', hooks=dict(args=self._printHeaders))
    '''
    print args['headers']
