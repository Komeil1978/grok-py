import grokpy
import unittest
import socket
import grokpy.requests

from mock import Mock

from grok_test_case import GrokTestCase
from grokpy.connection import Connection
from grokpy.client import Client
from grokpy.project import Project
from grokpy.publicDataSource import PublicDataSource
from grokpy.exceptions import AuthenticationError, GrokError

class ClientTestCase(GrokTestCase):

  def setUp(self):
    self.mockKey = 'SeQ9AhK57vOeoySQn1EvwElhZV1X87AB'

  def testGoodInstantiation(self):
    '''
    Basic object instantiation with mocks
    '''

    # Create our mock Connection class
    mock = Mock(spec=Connection)

    # Instantiate the Grok object
    g = Client(key = self.mockKey, connection = mock)

  def testBadConnection(self):
    '''
    A Grok Client should test its connection when instantiated
    '''

    # Create our mock Connection class
    mock = Mock(spec=Connection)
    mock.request.side_effect = GrokError('Bad connection!')

    # Assert error raised
    self.assertRaises(GrokError, Client, key = self.mockKey, connection = mock)

  def testCreateProject(self):
    '''
    Creating a project should make a well formatted call to the API
    '''
    # Inputs
    projectName = 'Foo'

    # Create our mock Connection class
    mock = Mock(spec=Connection)
    mock.request.return_value = {'name': projectName, 'id': 23887}

    # Create our client
    g = Client(key = self.mockKey, connection = mock)

    # Make the call
    returnValue = g.createProject(projectName)

    mock.request.assert_called_with({'service': 'projectCreate',
                                     'name': projectName})

    self.assertIsInstance(returnValue, Project)

  def testGetProject(self):
    '''
    Errors should be raised if called with default values
    Project should be returned
    '''
    # Inputs
    badId = 'YOUR_PROJECT_ID'
    goodId = 23887
    projectName = 'Foo'

    # Create our mock Connection class
    mock = Mock(spec=Connection)
    mock.request.return_value = {'name': projectName, 'id': goodId}

    # Create our client
    g = Client(key = self.mockKey, connection = mock)

    # Make the call that should error
    self.assertRaises(GrokError, g.getProject, badId)

    # Make the good call
    returnValue = g.getProject(goodId)

    mock.request.assert_called_with({'service': 'projectRead',
                                     'projectId': goodId})

    self.assertIsInstance(returnValue, Project)

  def testListProjects(self):
    '''
    Should make a well formatted call and return a list of Project instances
    '''

    # Create our mock Connection class
    mock = Mock(spec=Connection)
    mock.request.return_value = [{'name': 'project1', 'id': 1},
                                 {'name': 'project2', 'id': 2}]

    # Create our client
    g = Client(key = self.mockKey, connection = mock)

    # Make the call
    projects = g.listProjects()

    mock.request.assert_called_with({'service': 'projectList'})

    self.assertIsInstance(projects, type([]))

    for project in projects:
      self.assertIsInstance(project, Project)

  def testListPublicDataSources(self):
    '''
    Should make a well formatted call and return a list of
    PublicDatasource instances
    '''

    # Create our mock Connection class
    mock = Mock(spec=Connection)
    mock.request.return_value = [{'id': 'Twitter'},
                                 {'id': 'Weather'}]

    # Create our client
    g = Client(key = self.mockKey, connection = mock)

    # Make the call
    publicDataSources = g.listPublicDataSources()

    mock.request.assert_called_with({'service': 'providerDefinitionList'})

    self.assertIsInstance(publicDataSources, type([]))

    for publicDataSource in publicDataSources:
      self.assertIsInstance(publicDataSource, PublicDataSource)

  def testGetPublicDataSource(self):
    '''
    We should raise an error if a bad id is given, otherwise we should
    return an instance of PublicDataSource
    '''

    # Create our mock Connection class
    mock = Mock(spec=Connection)
    # getPublicDataSource() internally calls listPublicDataSources()
    mock.request.return_value = [{'id': 'Twitter'},
                                 {'id': 'Weather'}]

    # Create our client
    g = Client(key = self.mockKey, connection = mock)

    # Make the bad call
    self.assertRaises(GrokError, g.getPublicDataSource, 'Flrum')

    # Make the good call
    source = g.getPublicDataSource('Twitter')

    mock.request.assert_called_with({'service': 'providerDefinitionList'})

    self.assertIsInstance(source, PublicDataSource)

  def testAbout(self):
    '''
    We should make a properly formatted call
    '''

    # Create our mock Connection class
    mock = Mock(spec=Connection)
    rvString = "Version 1"
    mock.request.return_value = "Version 1"

    # Create our client
    g = Client(key = self.mockKey, connection = mock)

    # Make the good call
    self.assertEqual(g.about(), rvString)

    mock.request.assert_called_with({'service': 'about'})

  def testAlignPredictions(self):
    '''
    Return properly aligned resultRows
    '''

    # Create a client
    g = Client(key = self.mockKey, connection = Mock(spec=Connection))

    inputHeaders = ['rowId',
                    'input:value',
                    'temporal_prediction:value',
                    'temporal_metric:grok_score']

    inputRows = [['0', '1', '2', '10'],
                 ['1', '2', '3', '10']]

    expectedOut = [('0', '1', '', ''),
                    ('1', '2', '2', '10'),
                    ('', '', '3', '10')]

    self.assertEqual(g.alignPredictions(inputHeaders, inputRows), expectedOut)

if __name__ == '__main__':
  debug = 0
  if debug:
    single = unittest.TestSuite()
    single.addTest(ClientTestCase('testBadConnection'))
    unittest.TextTestRunner().run(single)
  else:
    unittest.main()
