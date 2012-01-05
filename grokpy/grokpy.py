import threading

from connection import Connection
from project import Project
from stream import Stream
from field import Field
from exceptions import GrokError, AuthenticationError

class Grokpy(object):
  '''
  Top level object for interacting with the Grok Prediction Service.
  '''
  
  def __init__(self, key = None, baseURL = None):
    '''
    TODO: Make this into a singleton? Do we need to support multiple
    accounts in the same process?
    '''    
    # Create a connection to the API
    if baseURL:
      self.c = Connection(key, baseURL)
    else:
      self.c = Connection(key)
      
    # Minimal connection test
    self.testConnection()
  
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
  
  def listProjects(self):
    '''
    Lists all the projects currently associated with this account
    '''
    requestDef = {'service': 'projectList'}
    
    projectDescriptions = self.c.request(requestDef)
    
    # Create objects out of the returned descriptions
    projects = [Project(self.c, pDef) for pDef in projectDescriptions]
      
    return projects
  
  def testConnection(self):
    '''
    Makes a minimial service call to test the API connection
    '''
    
    requestDef = {'service': 'projectList'}
    
    self.c.request(requestDef)
  
  def alignPredictions(self, data):
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
    3                       9
    '''
    
    pass
    
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
  
