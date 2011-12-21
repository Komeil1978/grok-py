from field import Field

class Stream(object):
  '''
  A Stream is the combination of data and the specification of those data
  that will be used by a model
  '''

  def __init__(self):
    # Our stream description
    self.description = {'fields': []}
    
    # Our local data store
    self.records = None
    
  def setLocationFieldIndex(self, index):
    self.description['locationFieldIndex'] = index

  def setPredictionFieldIndex(self, index):
    self.description['predictionFieldIndex'] = index
    
  def setTemporalFieldIndex(self, index):
    self.description['temporalFieldIndex'] = index
  
  def setTimeAggregation(self, aggregationType):
    self.description['timeAggregation'] = aggregationType
  
  def addField(self, descDict):
    '''
    Add a field object to a stream
    '''
    newField = Field(descDict)
    
    self.description['fields'].append(newField.description)
    
    return newField
    
  def addRecords(self, records):
    '''
    Appends records to the input cache of the given stream.
    
    WARNING: HACK
    
    Due to the current object model we actually send the records in the
    model.addStream() method.
    '''
    
    self.records = records
    
    return len(self.records)
