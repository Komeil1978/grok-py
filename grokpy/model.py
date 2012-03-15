import os
import time
import httplib
import json
import warnings

from exceptions import GrokError, AuthenticationError, NotYetImplementedError
from streaming import StreamListener, Stream
from swarm import Swarm

VERBOSITY = 0

class Model(object):
  '''
  Object representing a Grok Model.

  * parent - **Either** a `Client` or `Project`.
  * modelDef - A dict, usually returned from a model creation or get action.
    Usually includes:

    * id
    * name
    * streamId
    * swarmsUrl
    * url
  '''

  def __init__(self, parent, modelDef):

    # Give streams access to the parent client/project and its connection
    self.parent = parent
    self.c = self.parent.c

    # Take everything we're passed and make it an instance property.
    self.__dict__.update(modelDef)

    # Prepare to have a swarm associated with the model
    self.swarm = None

  def delete(self):
    '''
    Permanently deletes the model

    .. warning:: There is currently no way to recover from this opperation.
    '''
    self.c.request('DELETE', self.url)

  #############################################################################
  # Model Configuration

  def setName(self, newName):
    '''
    Renames the model.

    * newName - String
    '''

    raise NotYetImplementedError()

    # Get the current model state
    url = self.url
    modelDef = self.c.request('GET', url)['model']

    # Update the definition
    modelDef['name'] = newName

    # Update remote state
    self.c.request('POST', url, {'model': modelDef})

    # Update local state
    self.name = newName

  def setNote(self, newNote):
    '''
    Adds or updates a note for this model.

    * newNote - A String describing this model.
    '''

    raise NotYetImplementedError

    # Get the current model state
    url = self.url
    modelDef = self.c.request('GET', url)['model']

    # Update the definition
    modelDef['note'] = newNote

    # Update remote state
    self.c.request('POST', url, {'model': modelDef})

    # Update local state
    self.note = newNote

  #############################################################################
  # Model states

  def promote(self):
    '''
    Puts the model into a production ready mode.

    .. note: This may take several seconds.
    '''
    pass
  
  def start(self):
    '''
    Starts up a model, readying it to receive new data from a stream
    '''
    raise NotYetImplementedError()

  def disableLearning(self, retries = 3):
    '''
    Puts the model into a predictions only state where it will not learn from
    new data.

    * retries - If this method is called immediately after model promotion it may
              fail. By default we will retry a few times.
    '''
    raise NotYetImplementedError()

  def enableLearning(self):
    '''
    New records will be integrated into the models future predictions.
    '''
    raise NotYetImplementedError()

  #############################################################################
  # Stream

  def getStream(self):
    '''
    Returns the Stream that this model is associated with.
    '''
    return self.parent.getStream(self.streamId)

  #############################################################################
  # Swarms

  def startSwarm(self, size = None):
    '''
    Runs permutations on model parameters to find the optimal model
    characteristics for the given data.

    * size - A value from grokpy.SwarmSize. Initially, small, medium, or large.
      the default is medium. Small is only good for testing, whereas large can
      take a very long time.
    '''

    if self.swarm and self.swarm.getState() in ['Starting', 'Running']:
      raise GrokError('This model is already swarming.')

    url = self.swarmsUrl
    requestDef = {}
    if size:
      requestDef.update({'options': {"size": size}})

    result = self.c.request('POST', url, requestDef)

    # Save the swarm object
    self.swarm = Swarm(self, result['swarm'])

    return result

  def stopSwarm(self):
    '''
    Terminates a Swarm in progress
    '''
    raise NotYetImplementedError()

  def getSwarmState(self):
    '''
    Returns the current state of a swarm.

    TODO: Check this works when you get a model that's already created and swarming
    '''

    if not self.swarm:
      raise GrokError('There is no swarm associated with this model.')

    return self.swarm.getState()

  def getModelOutput(self):
    '''
    Returns the data in the output cache of the best model found during Swarm.
    '''
    result = self.c.request('GET', self.dataUrl)['output']

    headers = result['names']
    data = result['data']

    return headers, data

  #############################################################################
  # Basic Interaction - Live/On/Production Models

  def getMultiStepPredictions(self, buffer, timesteps):
    '''
    .. warning:: Experimental.

    Gets predictions for the next N timesteps

    * buffer - A set of actual values to send in to prime predictions. This buffer
             should be sent in with each call and updated as new actual values
             are measured.
    * timesteps - The number of steps into the future to predict.


    Example::

      --TIMESTEP 1 --
      buffer = [[0],
                [1],
                [2],
                [0],
                [1],
                [2]]

      Call:
        model.getMultiStepPredictions(buffer, 3)
      Return:
        3 rows of predictions, which are then converted back to input format

        results = [[.01],
                   [1.01],
                   [2.01]]

      --TIMESTEP 2 --
      buffer = [[0],
                [1],
                [2],
                [0],
                [1],
                [2],
                [0]] # Note the extra actual value we have now

      Call:
        model.getMultiStepPredictions(buffer, 3)
      Return:
        3 rows of predictions, which are then converted back to input format

        results = [[1.01],
                   [2.01],
                   [.01]] # Predictions are now one more timestep in the future
    '''

    # Send in our buffer
    self.sendRecords(buffer)

    # Get the last prediction
    bufferLen = len(buffer)

    if self.outputCachePointer == 0:
      headers, resultRows = self.monitorPredictions(bufferLen - 1)
    else:
      start = self.outputCachePointer + bufferLen
      headers, resultRows = self.monitorPredictions(start)

    # Collect predictions
    results = []
    for i in range(timesteps):
      latestPrediction = resultRows[-1]
      # store the row id
      latestId = int(latestPrediction[0])
      self.outputCachePointer = latestId
      # add that prediction to the list
      results.append(latestPrediction)
      # convert that prediction back into a row
      tempRecord = self._predictionToInput(headers, latestPrediction)
      # send that new row in
      self.sendRecords([tempRecord])
      # get the latest prediction
      response = self.getPredictions((latestId + 1), -1)
      resultRows = response['rows']

    return headers, results

  #############################################################################
  # Private methods

  def _predictionToInput(self, headers, prediction):
    '''
    Converts predictions back into inputs for multi-step prediction

    * headers - The column names for each prediction
    * prediction - A list of inputs, predictions, and metrics
    '''

    if not len(headers) == len(prediction):
      raise GrokError('Headers and predictions do not match up. ' +
                      str(headers) + ' ' + str(prediction))

    # Match up headers and values
    zipped = dict(zip(headers, prediction))
    input = {}
    for name, value in zipped.iteritems():
      # Extract only relevant values. Preds will overwrite if they exist.
      if 'input' in name or 'temporal_prediction' in name:
        prefix, field = name.split(':')
        input[field] = value

    return input.values()
