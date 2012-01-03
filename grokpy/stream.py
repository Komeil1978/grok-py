from field import Field

class Stream(object):
  '''
  A Stream is the combination of data and the specification of those data
  that will be used by a model
  '''

  def __init__(self):
    # Our stream description
    self.streamDescription = {'fields': []}
    
    # Our local data store
    self.records = None
    
  def setLocationFieldIndex(self, index):
    self.streamDescription['locationFieldIndex'] = index

  def setPredictionFieldIndex(self, index):
    self.streamDescription['predictionFieldIndex'] = index
    
  def setTemporalFieldIndex(self, index):
    self.streamDescription['temporalFieldIndex'] = index
  
  def setTimeAggregation(self, aggregationType):
    self.streamDescription['timeAggregation'] = aggregationType
  
  def addField(self, **kwargs):
    '''
    Add a field object to a stream
    '''
    newField = Field(**kwargs)

    self.streamDescription['fields'].append(newField.fieldDescription)
    
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
