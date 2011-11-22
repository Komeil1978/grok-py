import os
import urllib2
import json

from ntabeta.exceptions import (ntabetaError,
                                AuthenticationError)

class Client(object):
  '''
  Client for the ntabeta Prediction Service
  
  This class wraps services provided by the ntabeta API
  '''
  
  def __init__(self, key = None,
               baseURL = 'http://107.22.77.223:1961/version/1/'):
    '''
    Instantiate a ntabeta client
    '''
    
    # Search for API key in environment
    if not key:
      key = find_key()
      if not key:
        raise AuthenticationError("""
          Please supply your API key.
          
          Method 1:
            Supply your credentials when you instantiate the client.
            
            client = %s(key='D23984KJHKJH')

          Method 2:
          (More Secure)

            Add your credentials to your shell environment. From the command
            line:

            echo "export ntabeta_API_KEY=D23984KJHKJH" >> ~/.bashrc
            source ~/.bashrc
  
            For either method please replace the dummy key value with your real
            key from your account page.

            http://ntabeta.numenta.com/account""" % self.__class__.__name__)
        
    # The API we'll use to authenticate all HTTP calls.
    self.key = key
    
    # The base path for all our HTTP calls
    self.baseURL = baseURL + 'apiKey/' + self.key + '/'
    
  def request(self, path, method = None):
    '''
    Make a call directly to the ntabeta API and print the returned JSON
    '''
    uri = self.baseURL + path
    
    rv = urllib2.urlopen(uri)
    
    pyResults = json.loads(rv.read())
    
    return pyResults['result']
    
  #############################################################################
  # API Services
  
  def availableServices(self):
    '''
    Returns a list of the ntabeta Services
    '''
    return self.request('')
  
  def cachePurge(self):
    pass
  
  def dataUploadInit(self):
    pass
  
  def dataUploadProgres(self):
    pass
  
  def dataUpload(self):
    pass
  
  def fileUpload(self):
    pass
  
  def inputCacheAppend(self):
    pass
  
  def inputCacheData(self):
    pass
  
  '''
  MODELS
  '''
  
  def modelCopy(self):
    pass
  
  def modelCreate(self):
    pass
  
  def modelDelete(self):
    pass
  
  def modelList(self):
    pass
  
  def modelPredictions(self):
    pass
  
  def modelRead(self):
    pass
  
  def modelUpdate(self):
    pass
  
  '''
  PROJECTS
  '''
  
  def projectCreate(self):
    pass
  
  def projectDelete(self):
    pass
  
  def projectList(self):
    pass
  
  def projectRead(self):
    pass
  
  def projectUpdate(self):
    pass
  
  '''
  PROVIDERS
  '''
  
  def providerFileDelete(self):
    pass
  
  def providerFileList(self):
    pass
  
  def providerFileUpload(self):
    pass
  
  def providerList(self):
    '''
    Get a list of available data providers and the specification for using them
    as part of a search
    '''
    
    self.request('service/providerList')
  
  '''
  SEARCH
  '''
  
  def searchCancel(self):
    pass
  
  def searchData(self):
    pass
  
  def searchList(self):
    pass
  
  def searchProgress(self):
    pass
  
  def searchResult(self):
    pass
  
  def searchStart(self):
    pass
        
def find_key():
  '''
  Retrieve an API key from the user's shell environment
  '''
  try:
    key = os.environ["ntabeta_API_KEY"]
  except KeyError:
    return None
  
  return key