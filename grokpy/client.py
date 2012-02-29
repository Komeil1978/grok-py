import threading
import httplib2

from connection import Connection
from user import User
from project import Project
from stream import Stream
from field import Field
from publicDataSource import PublicDataSource
from exceptions import GrokError, AuthenticationError

class Client(object):
  '''
  Top level object for interacting with the Grok Prediction Service.

  Contains:

  High Level Opertions
  Helper Methods
  '''

  def __init__(self, key = None, baseURL = None, connection = None):
    '''
    Key - Grok API Key
    baseURL - baseURL - Grok server request target
    connection - An instance of the grokpy.Connection class. Used mainly for
                 testing.
    '''

    # Create a connection to the API
    if not connection:
      if baseURL:
        self.c = Connection(key, baseURL)
      else:
        self.c = Connection(key)
    else:
      self.c = connection

    # Test the connection works and get the User info
    self.user = self.getUser()

  #############################################################################
  # High Level Operations

  def createModel(self, name = None):
    '''
    Create a model associated with this project
    '''

    print dir(self.user)
    url = self.user.modelsUrl
    requestDef = {'model': {'name':'My Model'}}

    result = self.c.request('POST', url, requestDef)

    return Model(result)

  def getModel(self, modelId):
    '''
    Returns the model corresponding to the given modelId
    '''
    if modelId == 'YOUR_MODEL_ID':
      raise GrokError('Please supply a valid Model Id')

    # Determine if this is a search or production model
    productionModels = [model['id'] for model in self._listProductionModels()]
    searchModels = [model['id'] for model in self._listSearchModels()]

    if modelId in productionModels and modelId in searchModels:
      raise GrokError('Ruh-ro, model id collision between prod and search.')
    elif modelId in productionModels:
      modelType = 'production'
    elif modelId in searchModels:
      modelType = 'search'
    else:
      raise GrokError('Model Id not found.')

    # Get the model definition and create a new Model object with that.
    service = modelType + 'ModelRead'
    idParam = modelType + 'ModelId'

    requestDef = {'service': service,
                  idParam: modelId}

    modelDef = self.c.request(requestDef, 'POST')

    return Model(self, modelDef = modelDef)

  def listModels(self):
    '''
    Returns a list of Models that exist in this project
    '''
    modelDescriptions = self._listSearchModels()

    modelDescriptions.extend(self._listProductionModels())

    if modelDescriptions:
      models = [Model(self, desc) for desc in modelDescriptions]
    else:
      models = []

    return models

  def stopAllModels(self, verbose = False):
    '''
    A convenience method to stop all models that have been promoted.

    This method can take many seconds to return depending on how many
    models are being stopped.
    '''

    productionModels = self._listProductionModels()

    stoppedModelIds = []
    for model in productionModels:
      if model['running']:
        id = model['id']
        stoppedModelIds.append(id)
        if verbose: print 'Stopping model: ' + str(id)
        requestDef = {'service': 'productionModelStop',
                      'productionModelId': id}
        self.c.request(requestDef)

    return stoppedModelIds

  def createStream(self):
    '''
    Returns an instance of the Stream object
    '''

    return Stream(self)

  #############################################################################
  # Private methods


  def _listProductionModels(self):
    '''
    Returns a list of all production models.
    '''

    requestDef = {'service': 'productionModelList',
                  'projectId': self.id,
                  'includeTotalCount': False}

    response = self.c.request(requestDef, 'POST')

    return response['productionModels']

  def _listSearchModels(self):
    '''
    Returns a list of all search models
    '''

    requestDef = {'service': 'searchModelList',
                  'projectId': self.id,
                  'includeTotalCount': False}

    response = self.c.request(requestDef, 'POST')

    return response['searchModels']

  def createProject(self, projectName):
    '''
    Creates a project through the Grok API
    '''

    # A dictionary describing the request
    requestDef = {
      'service': 'projectCreate',
      'name': projectName,
    }

    # Make the API request
    result = self.c.request(requestDef)

    # Use the results to instantiate a new Project object
    project = Project(self.c, result)

    return project

  def getProject(self, projectId):
    '''
    Returns a Project with the given id
    '''
    if projectId == 'YOUR_PROJECT_ID':
      raise GrokError('Please supply a valid Project Id')

    requestDef = {
      'service': 'projectRead',
      'projectId': projectId,
    }

    # Make the API request
    result = self.c.request(requestDef)

    # Use the results to instantiate a new Project object
    project = Project(self.c, result)

    return project

  def listProjects(self):
    '''
    Lists all the projects currently associated with this account
    '''
    requestDef = {'service': 'projectList'}

    projectDescriptions = self.c.request(requestDef)

    # Create objects out of the returned descriptions
    if projectDescriptions:
      projects = [Project(self.c, pDef) for pDef in projectDescriptions]
    else:
      projects = []

    return projects

  def listPublicDataSources(self):
    '''
    Lists all the public data sources registered with Grok
    '''
    requestDef = {'service': 'providerDefinitionList'}

    dataSourceDescriptions = self.c.request(requestDef)

    if dataSourceDescriptions:
      publicDataSources = [PublicDataSource(self.c, dsd) for dsd in
                           dataSourceDescriptions]
    else:
      publicDataSources = []

    return publicDataSources

  def getPublicDataSource(self, id):
    '''
    Looks up and returns a PDS by its code.
    '''
    pdsList = self.listPublicDataSources()

    for pds in pdsList:
      if pds.id == id:
        return pds
      else:
        continue

    # Code not found
    raise GrokError('A Public Data Source with id "%s" was not found.' % id)

  def getUser(self, userId = None):
    '''
    Retrieves the dict representation of a user from the list of users
    associated with the current API key.

    Returns a User object.
    '''
    url = '/users'
    rv = self.c.request('GET', url)

    # By default return the first user.
    if not userId:
      user = User(rv['users'][0])
      return user
    # Otherwise return the first user with a matching Id
    else:
      for userDict in rv['users']:
        if int(userDict['userId']) == userId:
          return User(userDict)

    # We didn't find the user
    raise GrokError('There were no users, or the userId you specified was not '
                    'found.')

  def about(self):
    '''
    Get current build and server information from API server
    '''
    requestDef = {'service': 'about'}

    return self.c.request(requestDef)

  #############################################################################
  # Helper Methods

  def alignPredictions(self, headers, resultRows):
    '''
    Puts prediction on the same row as the actual value for easy comparison in
    external tools like Excel.

    Example Transformation:

    RowID   ActualValue     PredictedValue
    0       3               5
    1       5               7
    2       7               9

    RowID   ActualValue     PredictedValue
    0       3
    1       5               5
    2       7               7
                            9
    '''

    # Find columns that contain predictions / metrics
    predictionIndexes = [headers.index(header)
                       for header in headers
                       if ('temporal_prediction' in header)
                       or ('temporal_metric' in header)]

    # Bump all predictions down one row
    columns = zip(*resultRows)
    for index in range(len(columns)):
      column = list(columns[index])
      if index in predictionIndexes:
        column.insert(0, '')
      else:
        column.append('')
      columns[index] = column
    resultRows = zip(*columns)

    return resultRows

#############################################################################
# Enums

class Aggregation(object):
  '''
  Enum-like class to specify valid aggregation strings
  '''
  RECORD = 'RECORD'
  SECONDS = 'SECONDS'
  MINUTES = 'MINUTES'
  MINUTES_15 = 'MINUTES_15'
  HOURS = 'HOURS'
  DAYS = 'DAYS'
  WEEKS = 'WEEKS'
  MONTHS = 'MONTHS'

class Status(object):
  '''
  Enum-like class to specify valid Swarm status strings
  '''
  RUNNING = 'RUNNING'
  CANCELED = 'CANCELED'
  COMPLETED = 'COMPLETED'

class GrokData(object):
  '''
  Enum-like class to specify valid Grok data type strings
  '''
  DATETIME = 'DATETIME' # a point in time.
  ENUMERATION = 'ENUMERATION' # a category.
  IP_ADDRESS = 'IP_ADDRESS' # an IP address (V4).
  LAT_LONG = 'LAT_LONG' # a latitude/longitude combination.
  SCALAR = 'SCALAR' # a numeric value.
  ZIP_CODE = 'ZIP_CODE' # a U.S. zip code. Aggregated with first or last.

class DataFlag(object):
  '''
  Enum-like class to specify valid data flag strings
  '''
  NONE = 'NONE'
  RESET = 'RESET'
  SEQUENCE = 'SEQUENCE'
  TIMESTAMP = 'TIMESTAMP'
