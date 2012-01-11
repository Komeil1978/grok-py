from grokpy.project import Project
import unittest

class MockConnection(object):
  
  def __init__(self):
    self.key = ''
    self.baseURL = 'http://example.com'
    
  def request(self, requestDef):
    '''
    Returns the same thing all the time
    '''
    
    return (200, 'foo')

class ProjectTestCase(unittest.TestCase):

  def setUp(self):
    self.c = MockConnection()
    self.projectName = 'Testing Time'

  def testCreateProject(self):
    '''
    Create a project without errors
    '''
    project = Project(self.c,
                      self.projectName)
        
    self.assertEquals(self.projectName, project.name)

