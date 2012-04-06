import grokpy

from grokpy.exceptions import GrokError

class ModelSpecification(object):
  '''
  This is a client level object that is useful for building Model
  Specifications in an object oriented way. (As opposed to writing the JSON
  or Dict directly).
  '''

  def __init__(self):

    # What is the name of this model
    self.name = ''

    # What stream should this model listen to
    self.streamId = None

    # What aggregation will this model use
    self.aggInt = None

  def setName(self, name):
    '''
    Updates the local name.
    '''
    self.name = name

  def setPredictedField(self, predictedField):
    '''
    Sets the field the model will attempt to predict. Swarm will evaluate
    models based on the models ability to predict this field.

    * predictedField - String. A field name as it appears in the stream
      specification.
    '''

    self.predictedField = predictedField

  def setStream(self, streamId):
    '''
    Sets which stream the model will listen to.

    * streamId - String. A 36 unique id for a Stream. OR grokpy.Stream object
      from which a stream id will be extracted.
    '''

    if isinstance(streamId, grokpy.Stream):
      self.streamId = streamId.id
    elif len(streamId) == 36:
      self.streamId = streamId
    else:
      raise GrokError('This does not appear to be a properly formatted stream '
                      'id.')

  def setAggregationInterval(self, aggInt):
    '''
    Defines the interval Grok will use to aggregate incoming records over.

    * aggInt - Dict. Example::

      interval = {'hours': 1,
                  'minutes': 15}

      modelSpec.setAggregationInterval(interval)
    '''
    self.dataSources.append(dataSource)

  def getSpec(self):
    '''
    Returns an assembled dict from the current state of the specification
    '''

    if not self.name:
      raise GrokError('Please set a name for this model')

    if not self.streamId:
      raise GrokError('Please set a stream id for this model spec.')

    returnSpec = {"name": self.name,
                  "predictedField": self.predictedField,
                  "streamId": self.streamId}

    if self.aggInt:
      returnSpec['aggregation'] = {}
      returnSpec['aggregation']['interval'] = self.aggInt

    return returnSpec
