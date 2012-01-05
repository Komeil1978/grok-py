import os
import time

from exceptions import GrokError, AuthenticationError

class Model(object):
  '''
  Object representing a Grok Model
  '''

  def __init__(self, connection, projectDef, modelDef = {}):
    # Our connection to the Grok API
    self.c = connection
    
    # The project this model belongs to
    self.projectDef = projectDef
    
    # The Id of this model
    self.id = None
    
    # The Stream this model will listen to
    self.stream = None
    
    # Whether this is a search or production model
    if 'running' in modelDef:
      self.type = 'production'
    else:
      self.type = 'search'
    
  def setStream(self, stream):
    '''
    Associates a stream with a model
    '''
    # Store our Stream object for later use
    self.stream = stream 
  
  def startSwarm(self):
    '''
    Runs permutations on model parameters to find the optimal model
    characteristics for the given data.
    '''
    
    # WARNING: HACK
    #
    # Due to the current object model this is actually where:
    #   - The project is configured server side
    #   - The model is created
    #   - Data is streamed to the model input cache
    print '<OBJECT MODEL WORKAROUND>'
 
    # Configure project
    print 'CONFIGURING PROJECT'
    
    for arg, value in self.stream.streamDescription.iteritems():
      self.projectDef['streamConfiguration'][arg] = value

    requestDef = {'service': 'projectUpdate',
                  'project': self.projectDef}
    
    self.c.request(requestDef, 'POST')
    
    # Create the model
    print 'CREATING MODEL'
    
    requestDef = {'service': 'searchModelCreate',
                  'projectId': self.projectDef['id']}
    
    modelDef = self.c.request(requestDef)
    
    self.id = modelDef['id']
    
    # Upload data held temporarily in Stream object
    print 'APPENDING DATA'
    service = self.type + 'ModelInputCacheAppend'
    param = self.type + 'ModelId'
    
    requestDef = {'service': service,
                  param: self.id,
                  'data': self.stream.records}
    
    self.c.request(requestDef)
    
    print '</WORKAROUND>'
    ########## END HACK
    
    param = self.type + 'ModelId'
    
    requestDef = {'service': 'searchStart',
                  param: self.id}
    
    self.c.request(requestDef)
    
    return
  
  def stopSwarm(self):
    '''
    Terminates a Swarm in progress
    '''
    param = self.type + 'ModelId'
    
    requestDef = {'service': 'searchCancel',
                  param: self.id}
    
    self.c.request(requestDef)
  
  def getSwarmProgress(self):
    '''
    Polls the server for progress of a running Swarm
    '''
    
    param = self.type + 'ModelId'
    
    requestDef = {'service': 'searchProgress',
                  param: self.id,
                  'stream': False}
    
    return self.c.request(requestDef)
    
  def getDescription(self):
    '''
    Get the current state of the model from Grok
    ''' 
    service = self.type + 'ModelRead'
    param = self.type + 'ModelId'
    
    requestDef = {'service': service,
                  param: self.id}
    
    return self.c.request(requestDef)
    
  def setName(self, newName):
    '''
    Rename the model
    '''
    # Get current description
    desc = self.getDescription()
    
    service = self.type + 'ModelUpdate'
    idParam = self.type + 'ModelId'
    
    requestDef = {'service': service,
                  idParam: self.id,
                  'name': newName,
                  'note': desc['note']}

    return self.c.request(requestDef)
  
  def setNote(self, newNote):
    '''
    Adds or updates a note to for this model
    '''
    # Get current description
    desc = self.getDescription()
    
    service = self.type + 'ModelUpdate'
    idParam = self.type + 'ModelId'
    
    requestDef = {'service': service,
                  idParam: self.id,
                  'name': desc['name'],
                  'note': newNote}
    
    return self.c.request(requestDef)
    
  def setLocationField(self, fieldName):
    '''
    Wrapper for setLocationFieldIndex()
    '''
    self.setLocationFieldIndex(self._getFieldIndex(fieldName))
  
  def setPredictionField(self, fieldName):
    '''
    Wrapper for setPredictionFieldIndex()
    '''
    self.setPredictionFieldIndex(self._getFieldIndex(fieldName))
  
  def setTemporalField(self, fieldName):
    '''
    Wrapper for setTemporalFieldIndex()
    '''
    self.setTemporalFieldIndex(self._getFieldIndex(fieldName))
    
  def setLocationFieldIndex(self, index):
    '''
    Which stream field provides geospatial data for the model
    '''
    self._checkIndex(index)
    
    self.projectDef['streamConfiguration']['locationFieldIndex'] = index

  def setPredictionFieldIndex(self, index):
    '''
    The stream field for which we are optimizing predictions.
    '''
    self._checkIndex(index)
    
    self.projectDef['streamConfiguration']['predictionFieldIndex'] = index
    
  def setTemporalFieldIndex(self, index):
    '''
    Which stream field provides temporal data for the model
    '''
    self._checkIndex(index)
    
    self.projectDef['streamConfiguration']['temporalFieldIndex'] = index
  
  def setTimeAggregation(self, aggregationType):
    '''
    How the model will aggregate data within the stream
    
    Valid Types:
    
    RECORD: no aggregation is done.
    SECONDS
    MINUTES
    15_MINUTES
    HOURS
    DAYS
    WEEKS
    MONTHS
    '''
    self.projectDef['streamConfiguration']['timeAggregation'] = aggregationType
    
  def getSwarmResults(self, startRow = -1, endRow = -1):
    '''
    Returns the data in the output cache of the best model found during
    a Grok Swarm
    
    The default start/end row values request all the data available.
    '''
    
    service = self.type + 'ModelOutputCacheData'
    idParam = self.type + 'ModelId'
    
    requestDef = {'service': service,
                  idParam: self.id,
                  'startRow': startRow,
                  'endRow': endRow}
    
    return self.c.request(requestDef)
  
  #############################################################################
  # Private methods
  
  def _getFieldIndex(self, fieldName):
    '''
    Finds a field with a matching name and throws an error if there are more
    than one matches
    '''
    
    counter = 0
    index = 0
    for field in self.stream.streamDescription['fields']:
      if field['name'] == fieldName:
        counter += 1
        index = field['index']
    
    if not counter:
      raise GrokError('Field not found: ' + fieldName)
    if counter > 1:
      raise GrokError('Duplicate Field Name: ' + fieldName + ' More than one '
                      'field with this name was found. Please use the '
                      'set*FieldIndex() methods directly.')
    
    return index
    
  def _checkIndex(self, index):
    '''
    Ensures that specified indexes are possible for the current stream
    '''
    
    if not self.stream:
      raise GrokError('Please configure and add a Stream to this model before '
                      'specifying how you want the model to use the stream')
    
    if not self.stream.streamDescription['fields']:
      raise GrokError('Please configure and add a stream to this model before'
                      'specifying which fields to use.')
    
    if index >= len(self.stream.streamDescription['fields']):
      raise IndexError('The specified index is out of range for the given '
                       'stream.')
    

  
    