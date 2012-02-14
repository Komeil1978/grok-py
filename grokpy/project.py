import os
import csv
import StringIO
import traceback
import json

from model import Model
from stream import Stream
from joinFile import JoinFile

from exceptions import GrokError, AuthenticationError

class Project(object):
  '''
  Object representing a Grok project
  '''

  def __init__(self, connection, projectDef):

    self.c = connection
    try:
      self.id = projectDef['id']
      self.id = str(self.id)
      self.name = projectDef['name']
    except TypeError:
      raise GrokError('Instantiating a project expects a dictionary')
    self.projectDef = projectDef

  def getDescription(self):
    '''
    Get the current state of the project from Grok
    '''
    requestDef = {'service': 'projectRead',
                  'projectId': self.id}

    return self.c.request(requestDef)

  def delete(self):
    '''
    Permanently deletes the project, all its models, and data.
    '''
    requestDef = {'service': 'projectDelete',
                  'projectId': self.id}

    return self.c.request(requestDef)

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

  def createModel(self):
    '''
    Create a model associated with this project
    '''

    '''
    WARNING: HACK

    Due to the current object model we don't actually create the model until
    we start a swarm
    '''

    return Model(self)

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
