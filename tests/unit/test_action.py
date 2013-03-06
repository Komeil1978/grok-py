import unittest
from mock import Mock

from grok_test_case import GrokTestCase
from grokpy.connection import Connection
from grokpy.action import Action
from grokpy.exceptions import GrokError
from grokpy.project import Project
from grokpy.client import Client

class ActionTestCase(GrokTestCase):

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

    # Instantiate the project
    self.p = Project(self.client, self.projectDef)

    # Create our minimal actionDef
    self.actionDef = {'description': 'I did things!',
                      'url': 'http://www.example.com'}

    # Instantiate the action
    self.a = Action(self.p, self.actionDef)

  def testDelete(self):
    '''
    Calls the request method as expected
    '''

    self.a.delete()
    self.a.c.request.assert_any_call()

  def testGetSpecDict(self):
    '''
    Should return the same dictionary passed in.
    '''

    self.assertEqual(self.a.getSpecDict(), self.actionDef)


if __name__ == '__main__':
  debug = 0
  if debug:
    single = unittest.TestSuite()
    single.addTest(ActionTestCase('testDeleteAllModels'))
    unittest.TextTestRunner().run(single)
  else:
    unittest.main()
