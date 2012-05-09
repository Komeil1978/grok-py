import unittest
from mock import Mock

from grok_test_case import GrokTestCase
from grokpy.connection import Connection
from grokpy.project import Project
from grokpy.exceptions import GrokError
from grokpy.model import Model
from grokpy.stream import Stream
from grokpy.client import Client

class ProjectTestCase(GrokTestCase):

  def setUp(self):
    # Create a mock client
    self.client = Mock(spec=Client)
    self.client.c = Mock(spec=Connection)

    # Create our minimal projectDef
    self.projectId = 3354
    self.projectDef = {'id': self.projectId,
                       'name': 'Joyous Days',
                       'url': 'http://www.example.com',
                       'modelsUrl': 'http://www.example.com',
                       'streamsUrl': 'http://www.example.com'}

    # Instantiate the stream
    self.p = Project(self.client, self.projectDef)

  def testSetName(self):
    '''
    Calls the parent and updates the local objects name
    '''

    def rv(*args):
      return {'project': self.projectDef}

    # The function passed in will be called when request() is.
    self.client.c.request.side_effect = rv

    newName = 'globorous'
    self.p.setName(newName)

    self.assertEqual(self.p.name, newName)

  def testDelete(self):
    '''
    Calls the request method as expected
    '''

    self.p.delete()
    self.p.c.request.assert_any_call()

  def testCreateModel(self):
    '''
    Should make a call to the parent objects client.
    '''

    modelSpec = {}
    model = self.p.createModel(modelSpec)
    self.p.parentClient.createModel.assert_any_call()

  def testGetModel(self):
    '''
    Makes a call to the parent method
    '''
    self.p.getModel('id')

    self.p.parentClient.getModel.assert_any_call()

  def testListModels(self):
    '''
    Makes a call to the parent method
    '''
    self.p.listModels()

    self.p.parentClient.listModels.assert_any_call()

  def testDeleteAllModels(self):
    '''
    Makes a call to the parent method
    '''
    self.p.deleteAllModels()

    self.p.parentClient.deleteAllModels.assert_any_call()

  def testCreateStream(self):
    '''
    Should make a call to the parent objects client.
    '''

    modelSpec = {}
    model = self.p.createStream(modelSpec)
    self.p.parentClient.createStream.assert_any_call()

  def testGetStream(self):
    '''
    Makes a call to the parent method
    '''
    self.p.getStream('id')

    self.p.parentClient.getStream.assert_any_call()

  def testListStreams(self):
    '''
    Makes a call to the parent method
    '''
    self.p.listStreams()

    self.p.parentClient.listStreams.assert_any_call()

  def testDeleteAllStreams(self):
    '''
    Makes a call to the parent method
    '''
    self.p.deleteAllStreams()

    self.p.parentClient.deleteAllStreams.assert_any_call()

if __name__ == '__main__':
  debug = 0
  if debug:
    single = unittest.TestSuite()
    single.addTest(ProjectTestCase('testDeleteAllModels'))
    unittest.TextTestRunner().run(single)
  else:
    unittest.main()
