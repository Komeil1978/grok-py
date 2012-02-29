import os
import urllib2
import httplib2
import json
import socket
import requests
import base64

from exceptions import GrokError, AuthenticationError

VERBOSITY = 1

class Connection(object):
  '''
  Connection object for the Grok Prediction Service
  '''

  def __init__(self, key = None, baseURL = 'http://api.grok.numenta.com/', session = None):
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

    # The base path for all our HTTP calls
    self.baseURL = baseURL + 'v1'

    # The HTTP Client we'll use to make requests
    if not session:
      base64string = base64.encodestring(self.key + ':').replace('\n', '')
      headers = {"Authorization": "Basic %s" % base64string,
                 "Content-Type": 'application/json; charset=UTF-8'}
      session = requests.session(headers=headers)

    self.s = session

  def request(self, method, url, requestDef = None):
    '''
    Interface for all HTTP requests made to the Grok API
    '''

    print method
    print url
    if url[:4] != 'http':
      url = self.baseURL + url
    print url

    # JSON serialize the requestDef object
    requestDef = json.dumps(requestDef, ensure_ascii=False)
    print requestDef

    # Make the request, handle initial connection errors
    if method == 'GET':
      response = self.s.get(url)
    elif method == 'POST':
      response = self.s.post(url, requestDef)
    elif method == 'PUT':
      response = self.s.put(url)
    elif method == 'DELETE':
      response = self.s.delete(url)
    else:
      raise GrokError('Unrecognised HTTP method: %s' % method)

    # Handle HTTP errors
    if response.status_code != 200:
      print response.headers
      raise GrokError(response)

    # Load info from returned JSON strings
    content = json.loads(response.text)

    if VERBOSITY >= 1:
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

  def _handleGrokErrors(self, errors):
    '''
    Deal with known error codes from the Grok services
    '''
    raise GrokError(errors)

  def _requestDefToURL(self, requestDef):
    '''
    Takes in a requestDef dict and returns a uri appropriate for GET or
    for POST with body
    '''
    uriList = []
    for key, value in requestDef.iteritems():
      uriList.append(key)
      uriList.append(urllib2.quote(value))
    uriSuffix = '/'.join(uriList)
    uri = self.baseURL + uriSuffix

    return uri
