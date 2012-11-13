import grokpy
import unittest
import socket
import json
import grokpy.requests

from mock import Mock

from grok_test_case import GrokTestCase
from grokpy.connection import Connection
from grokpy.client import Client
from grokpy.project import Project
from grokpy.exceptions import AuthenticationError, GrokError

class ClientTestCase(GrokTestCase):

  def setUp(self):
    self.mockKey = 'SeQ9AhK57vOeoySQn1EvwElhZV1X87AB'
    self.mockConnection = Mock(spec = Connection)

    # The first request will always be to getUser(). So set this up now.
    self.projectsUrl = "https://api.numenta.com/v2/users/0a0acdd4-d293-11e1-bb05-123138107980/projects"
    self.apiKey = "API_KEY"
    self.streamsUrl = "https://api.numenta.com/v2/users/0a0acdd4-d293-11e1-bb05-123138107980/streams"
    self.firstName = "Api"
    self.url = "https://api.numenta.com/v2/users/0a0acdd4-d293-11e1-bb05-123138107980"
    self.lastName = "DocUser"
    # id is reserved as part of unittest
    self._id = "0a0acdd4-d293-11e1-bb05-123138107980"
    self.modelsUrl = "https://api.numenta.com/v2/users/0a0acdd4-d293-11e1-bb05-123138107980/models"
    self.usageUrl = "https://api.numenta.com/v2/users/0a0acdd4-d293-11e1-bb05-123138107980/usage"
    self.tier = 2
    self.email = "apidocs@numenta.com"

    self.getUserResponse = {'users': [{
                      "projectsUrl": self.projectsUrl,
                      "apiKey": self.apiKey,
                      "streamsUrl": self.streamsUrl,
                      "firstName": self.firstName,
                      "url": self.url,
                      "lastName": self.lastName,
                      "id": self._id,
                      "modelsUrl": self.modelsUrl,
                      "usageUrl": self.usageUrl,
                      "tier": self.tier,
                      "email": self.email
                    }]}

    self.mockConnection.request.return_value = self.getUserResponse

  def testGoodInstantiation(self):
    '''
    Basic object instantiation with mocks
    '''

    # Instantiate the Grok object
    grok = Client(key = self.mockKey, connection = self.mockConnection)

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

    # Create our client
    grok = Client(key = self.mockKey, connection = self.mockConnection)

    # Update the response for the next request
    response = {"project": {
                  "name": "API Doc project for retrieval",
                  "id": "dbbfc567-c409-4e7a-b06f-941f752e2f55",
                }}

    self.mockConnection.request.return_value = response

    # Make the call
    projectName = 'Foo'
    returnValue = grok.createProject(projectName)

    self.mockConnection.request.assert_called_with('POST',
                                                   self.projectsUrl,
                                                   {'project': {'name': projectName}})

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

    # Create our client
    grok = Client(key = self.mockKey, connection = self.mockConnection)

    # Update our mock's repsonse for the next request
    response = {'project': {'name': projectName, 'id': goodId}}
    self.mockConnection.request.return_value = response

    # Make the call that should error
    self.assertRaises(GrokError, grok.getProject, badId)

    # Make the good call
    returnValue = grok.getProject(goodId)

    expectedUrl = self.projectsUrl + '/' + str(goodId)
    self.mockConnection.request.assert_called_with('GET', expectedUrl)

    self.assertIsInstance(returnValue, Project)

  def testListProjects(self):
    '''
    Should make a well formatted call and return a list of Project instances
    '''

    # Create our client
    grok = Client(key = self.mockKey, connection = self.mockConnection)

    # Update our mock's repsonse for the next request
    response = {'projects': [{'name': 'project1', 'id': 1}, {'name': 'project2', 'id': 2}]}
    self.mockConnection.request.return_value = response

    # Make the call
    projects = grok.listProjects()

    self.mockConnection.request.assert_called_with('GET', self.projectsUrl,
                                                   params = {'all': True})

    self.assertIsInstance(projects, type([]))

    for project in projects:
      self.assertIsInstance(project, Project)

if __name__ == '__main__':
  debug = 0
  if debug:
    single = unittest.TestSuite()
    single.addTest(ClientTestCase('testListProjects'))
    unittest.TextTestRunner().run(single)
  else:
    unittest.main()
