import os
import time

class Model(object):
  '''
  Object representing a Grok Model
  '''

  def __init__(self, connection, modelDef):
    # Our connection to the Grok API
    self.c = connection
    # UID for this model
    self.id = modelDef['id']
    # Whether this is a search or production model
    if 'running' in modelDef:
      self.type = 'production'
    else:
      self.type = 'search'
    # If this model has requested an upload store the id here
    self.uploadId = None
  
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
    Rename the project
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
    
  def upload(self, filePath):
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
    service = self.type + 'ModelInputCacheUpload'
    idParam = self.type + 'ModelId'
    
    ## These will be sent as URL params
    requestDef = {'service': service,
                  idParam: self.id,
                  'uploadId': uploadId,
                  'filename': filename}
    ## File content will be alone in the body
    body = fh.read()
    
    headers = {'content-type':'text/csv', 'content-length': str(size)}
    
    numRows = self.c.request(requestDef, 'POST', body, headers)
    
    # Clean up
    fh.close()
    
  def monitorUpload(self, updateDelay = 1000):
    '''
    Opens a connection to Grok and listens for updates on the progress of
    an upload
    
    updateDelay - ms delay between updates. Range: 500 -> 10000
    '''
    attempts = 0
    while True:
      if attempts >= 10:
        raise GrokError('No uploadId found. Upload progress cannot be monitored'
                        'Please call model.upload() before monitorUpload()')
      elif not self.uploadId:
        attempts += 1
        time.sleep(.5)
        continue
      else:
        requestDef = {'service': 'fileUploadProgress',
                      'uploadId': self.uploadId,
                      'updateDelay': updateDelay}
        self.c.request(requestDef)
  
  def swarm(self):
    '''
    Runs permutations on model parameters to find the optimal model
    characteristics for the given data.
    '''
    
    idParam = self.type + 'ModelId'
    
    requestDef = {'service': 'searchStart',
                  idParam: self.id}
    
    self.c.request(requestDef)
    