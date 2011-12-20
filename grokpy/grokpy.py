import threading

from connection import Connection
from project import Project
from stream import Stream
from field import Field

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
  
  
class ThreadRunner(threading.Thread):
  '''
  Make service requests in separate threads
  '''

  def __init__(self, queue):
    threading.Thread.__init__(self)
    # The queue from which we will pull tasks
    self.queue = queue

  def run(self):
    while True:
      serviceCall, params = self.queue.get()
      if params:
        result = serviceCall(*params)
      else:
        result = serviceCall()
      self.queue.task_done()