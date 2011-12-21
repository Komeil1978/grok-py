from model import Model

class Project(object):
  '''
  Object representing a Grok project
  '''
  
  def __init__(self, connection, projectDef):
    
    self.c = connection
    self.id = str(projectDef['id'])
    self.name = projectDef['name']
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
    
    return self.c.request(requestDef, 'POST')
    
  def configure(self, **kwargs):
    '''
    Set the streamConfiguration of the project
    '''
    
    desc = self.getDescription()
    
    for arg, value in kwargs.iteritems():
      desc['streamConfiguration'][arg] = value
    
    requestDef = {'service': 'projectUpdate',
                  'project': desc}
    
    return self.c.request(requestDef, 'POST')
    
  def createModel(self):
    '''
    Create a model associated with this project
    '''
    
    '''
    WARNING: HACK
    
    Due to the current object model we don't actually create the model until
    we associate a stream with the model
    '''
    
    return Model(self.c, self.projectDef)
    