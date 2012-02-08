import unittest
import httplib2
from mock import Mock

from groktestcase import GrokTestCase
from grokpy.connection import Connection
from grokpy.project import Project
from grokpy.exceptions import AuthenticationError, GrokError

class ProjectTestCase(GrokTestCase):

  def setUp(self):
    self.mockKey = 'SeQ9AhK57vOeoySQn1EvwElhZV1X87AB'

  def testInstantiation(self):
    '''
    Basic object instantiation with mocks
    '''

    # Create our mock Connection class
    mock = Mock(spec=Connection)

    projectDef = {'id': 1980,
                  'name': 'Joyous Days'}

    # Instantiate the project
    p = Project(mock, projectDef)

    self.assertEqual(p.id, '1980')
    self.assertEqual(p.name, 'Joyous Days')

    # Passing anything in beside a dict should fail
    projectDef2 = []
    self.assertRaises(GrokError, Project, mock, projectDef2)

  def testGetDescription(self):
    '''
    Make a well formatted call to the API
    '''
    # Create our mock Connection class
    mock = Mock(spec=Connection)
    mock.request.return_value = 'Foo'

    # Instantiate the project
    projectId = '1980'
    projectDef = {'id': projectId,
                  'name': 'Joyous Days'}
    p = Project(mock, projectDef)

    # Make the call
    returnValue = p.getDescription()

    mock.request.assert_called_with({'service': 'projectRead',
                                     'projectId': projectId})

    self.assertEqual(returnValue, 'Foo')

  def testDelete(self):
    '''
    Make a well formatted call to the API
    '''
    # Create our mock Connection class
    mock = Mock(spec=Connection)
    mock.request.return_value = 'Foo'

    # Instantiate the project
    projectId = '1980'
    projectDef = {'id': projectId,
                  'name': 'Joyous Days'}
    p = Project(mock, projectDef)

    # Make the call
    returnValue = p.delete()

    mock.request.assert_called_with({'service': 'projectDelete',
                                     'projectId': projectId})

    self.assertEqual(returnValue, 'Foo')

if __name__ == '__main__':
  debug = 0
  if debug:
    single = unittest.TestSuite()
    single.addTest(ProjectTestCase('testInstantiation'))
    unittest.TextTestRunner().run(single)
  else:
    unittest.main()
