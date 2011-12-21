import os
import time

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
    
  def addStream(self, stream):
    '''
    Associates a stream with a model
    
    WARNING: HACK
    
    Due to the current object model this is actually where:
       - The project is configured server side
       - The model is created
       - Data is streamed to the model input cache
    '''
    # Store our Stream object for later use
    self.stream = stream
    
    # Configure project
    print 'CONFIGURING PROJECT'
    
    desc = {'streamConfiguration': {} }
    for arg, value in self.stream.description.iteritems():
      desc['streamConfiguration'][arg] = value
    
    self.projectDef.update(desc)

    requestDef = {'service': 'projectUpdate',
                  'project': self.projectDef}
    
    print self.c.request(requestDef, 'POST')
    
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
    
    print 'DONE'
    
    return 
  
  def startSwarm(self):
    '''
    Runs permutations on model parameters to find the optimal model
    characteristics for the given data.
    '''
    
    param = self.type + 'ModelId'
    
    requestDef = {'service': 'searchStart',
                  param: self.id}
    
    self.c.request(requestDef)
    
    return
  
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

  

    