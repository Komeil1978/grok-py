from field import Field

class Stream(object):
  '''
  A stream defines the characteristics of data being sent into Grok
  
  It is composed of fields and stream options such as:
      Aggregation
      Joining to Data Files
      Joining to Public Data
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
    
  def addFieldFromJSON(self, jsonString):
    '''
    Add a field using a JSON object as the definition for this field
    '''
    return Field.getFieldFromJSON(jsonString)
  
  def addRecords(self, records):
    '''
    Appends records to the input cache of the given stream. In the current
    object model this is the input cache of a specific model, so we
    won't do the upload until we call startSwarm() on the model.
    '''
    
    self.records = records
    
    return len(self.records)
    
  def upload(self, filePath, model):
    '''
    Uploads data from a given file to this model
    '''
    
    # Make sure we can open the given file
    _, filename = os.path.split(filePath)
    size = os.path.getsize(filePath)
    fh = open(filePath, 'r')
    
    # Get a handle for our upload
    requestDef = {'service': 'fileUploadInit'}
    uploadId = self.c.request(requestDef)
    
    # Store this locally
    self.uploadId = uploadId
    
    # Send the file contents
    service = model.type + 'ModelInputCacheUpload'
    idParam = model.type + 'ModelId'
    
    ## These will be sent as URL params
    requestDef = {'service': service,
                  idParam: model.id,
                  'uploadId': uploadId,
                  'filename': filename}
    ## File content will be alone in the body
    body = fh.read()
    
    headers = {'content-type':'text/csv', 'content-length': str(size)}
    
    numRows = self.c.request(requestDef, 'POST', body, headers)
    
    # Clean up
    fh.close()