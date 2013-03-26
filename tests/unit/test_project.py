import unittest
from mock import Mock

from grok_test_case import GrokTestCase
from grokpy.connection import Connection
from grokpy.project import Project
from grokpy.exceptions import GrokError
from grokpy.model import Model
from grokpy.stream import Stream
from grokpy.action import Action
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
                       'streamsUrl': 'http://www.example.com',
                       'actionsUrl': 'http://www.example.com'}

    # Instantiate the project
    self.p = Project(self.client, self.projectDef)

  ####################
  # Project Top Level

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

  ###################
  # Models

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

  #################
  # Streams

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

  ################
  # Actions

  def testCreateAction(self):
    '''
    Creating a action should make a well formatted call to the API
    '''

    # Update the response for the next request
    description = "I did things!"
    response = {"action": {
                  "description": "I did things!",
                  "id": "dbbfc567-c409-4e7a-b06f-941f752e2f55",
                  "url": "http://www.example.com"
                }}

    self.p.c.request.return_value = response

    # Make the call
    returnValue = self.p.createAction(description)

    self.p.c.request.assert_called_with('POST',
                                        self.p.actionsUrl,
                                        {'action': {'description': description}})

    self.assertIsInstance(returnValue, Action)

  def testGetAction(self):
    '''
    Not Implemented - Error should be raised
    '''

    actionId = 'foo'

    self.assertRaises(NotImplementedError, self.p.getAction, actionId)

  def testListActions(self):
    '''
    Should make a well formatted call and return a list of Action instances
    '''

    # Update the response for the next request
    response = {'actions': [{'description': 'Stuff Done', 'id': 1},
                            {'description': 'More things!', 'id': 2}]}
    self.p.c.request.return_value = response

    # Make the call
    actions = self.p.listActions()

    self.p.c.request.assert_called_with('GET', self.p.actionsUrl)

    self.assertIsInstance(actions, type([]))

    for action in actions:
      self.assertIsInstance(action, Action)

  def testDeleteAllActions(self):
    '''
    Not Implemented - Error should be raised
    '''

    self.assertRaises(NotImplementedError, self.p.deleteAllActions)

if __name__ == '__main__':
  debug = 0
  if debug:
    single = unittest.TestSuite()
    single.addTest(ProjectTestCase('testDeleteAllActions'))
    unittest.TextTestRunner().run(single)
  else:
    unittest.main()
