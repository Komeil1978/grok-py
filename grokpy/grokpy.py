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