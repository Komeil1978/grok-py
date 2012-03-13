from model import Model
from stream import Stream
from exceptions import GrokError, AuthenticationError

class Project(object):
  '''
  Object representing a Grok project
  '''

  def __init__(self, parentClient, projectDef):

    # Give projects access to the parent client and its connection
    self.parentClient = parentClient
    self.c = self.parentClient.c

    # Take everything we're passed and make it an instance property.
    self.__dict__.update(projectDef)

  def getDescription(self):
    '''
    Returns the current state of the project from Grok
    '''
    requestDef = {'service': 'projectRead',
                  'projectId': self.id}

    return self.c.request(requestDef)

  def delete(self):
    '''
    Permanently deletes the project, all its models, and data.

    WARNING: There is currently no way to recover from this opperation.
    '''

    self.c.request('DELETE', self.url)

  def setName(self, newName):
    '''
    Rename the project
    '''
    # Get current description
    desc = self.getDescription()

    # Modify the dictionary
    desc['name'] = newName

    requestDef = {'service': 'projectUpdate',
                  'project': desc}

    response = self.c.request(requestDef, 'POST')

    # Update locals
    self.name = newName

    return response

  #############################################################################
  # Model Methods
  #
  # Thin wrappers for Model methods on the Client object.

  def createModel(self, spec):
    '''
    Return a new Model object. The model will be created under this project.
    '''

    return self.parentClient.createModel(spec,
                                         parent = self,
                                         url = self.modelsUrl)

  def getModel(self, modelId):
    '''
    Returns the model corresponding to the given modelId

    * modelId
    '''

    return self.parentClient.getModel(modelId, self.modelsUrl)

  def listModels(self):
    '''
    Returns a list of Models that exist in this project
    '''

    return self.parentClient.listModels(self.modelsUrl)

  def stopAllModels(self, verbose = False):
    '''
    Stops all running models in this project.
    '''

    return self.parentClient.stopAllModels(name, url = self.modelsUrl)

  #############################################################################
  # Stream Methods
  #
  # Thin wrappers for Stream methods on the Client object.

  def createStream(self, spec, name = None):
    '''
    Returns a new Stream object. The stream will be created under this project.
    '''

    return self.parentClient.createStream(spec,
                                          name,
                                          self,
                                          url = self.streamsUrl)

  def getStream(self, streamId):
    '''
    Returns a Stream object from the given streamId. Assumes the stream is part
    of this project.
    '''
    return self.parentClient.getStream(streamId, self.streamsUrl)

  def listStreams(self):
    '''
    Returns a list of streams associated with the current project
    '''
    return self.parentClient.listStreams(self.streamsUrl)

  def deleteAllStreams(self, verbose = False):
    '''
    Permanently deletes all streams associated with the current project

    WARNING: There is currently no way to recover from this opperation.
    '''
    self.parentClient.deleteAllStreams(self.streamsUrl, verbose)
