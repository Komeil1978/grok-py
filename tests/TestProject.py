import unittest
from mock import Mock

from groktestcase import GrokTestCase
from grokpy.connection import Connection
from grokpy.project import Project
from grokpy.exceptions import GrokError
from grokpy.model import Model
from grokpy.stream import Stream

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

  def testSetName(self):
    '''
    Make a well formed call to the API and update the local objects name
    '''
    # Setup
    projectId = 3354
    projectDef = {'id': projectId,
                  'name': 'Joyous Days'}

    # Create our mock Connection class
    mock = Mock(spec=Connection)

    # Set up our return values
    returns = [projectDef, 'OK']
    def side_effects(*args):
       result = returns.pop(0)
       return result

    mock.request.side_effect = side_effects

    # Instantiate the project
    p = Project(mock, projectDef)

    # Make the call
    newName = 'Calypso'
    returnValue = p.setName(newName)

    # Check update request was made properly
    mock.request.assert_called_with({'project': {'id': 3354, 'name': 'Calypso'},
                                     'service': 'projectUpdate'},
                                     'POST')

    self.assertEqual(p.name, newName)

  def testCreateModel(self):
    '''
    Returns a model object
    '''
    # Setup
    projectId = 3354
    projectDef = {'id': projectId,
                  'name': 'Joyous Days'}

    # Create our mock Connection class
    mock = Mock(spec=Connection)

    # Instantiate the project
    p = Project(mock, projectDef)

    model = p.createModel()

    self.assertIsInstance(model, Model)

  def testGetModel(self):
    '''
    Handles default inputs, makes valid API calls
    '''
    # Setup
    projectId = 3354
    projectDef = {'id': projectId,
                  'name': 'Joyous Days'}

    # Create our mock Connection class
    mock = Mock(spec=Connection)

    # Set up our return values
    returns = [{'productionModels': []}, # Missing Model
              {'searchModels': []}, # Missing Model
              {'productionModels': [{'id': 32}]}, # Collision
              {'searchModels': [{'id': 32}]}, # Collision
              {'productionModels': [{'id': 32}]}, # Good Call (search)
              {'searchModels': [{'id': 15}]}, # Good Call (search)
              {'id': 15}, # Good Call (search)
              {'productionModels': [{'id': 32}]}, # Good Call (prod)
              {'searchModels': [{'id': 15}]}, # Good Call (prod)
              {'id': 32}, # Good Call (prod)
              ]
    def side_effects(*args):
       result = returns.pop(0)
       return result

    mock.request.side_effect = side_effects

    # Instantiate the project
    p = Project(mock, projectDef)

    # Default values check
    badId = 'YOUR_MODEL_ID'
    self.assertRaises(GrokError, p.getModel, badId)

    # Missing model
    self.assertRaisesRegexp(GrokError, 'Model Id not found.',
                            p.getModel, 'foo')

    # Collision
    self.assertRaisesRegexp(GrokError, 'Ruh-ro.*',
                            p.getModel, 32)

    # Good Call (search)
    modelId = 15
    model = p.getModel(modelId)

    self.assertIsInstance(model, Model)

    # Check request was made properly
    mock.request.assert_called_with({'searchModelId': modelId,
                                     'service': 'searchModelRead'}, 'POST')

    # Good Call (prod)
    modelId = 32
    model = p.getModel(modelId)

    self.assertIsInstance(model, Model)

    # Check request was made properly
    mock.request.assert_called_with({'productionModelId': modelId,
                                     'service': 'productionModelRead'}, 'POST')

  def testListModels(self):
    '''
    Should return a list of model objects
    '''
    # Setup
    projectId = 3354
    projectDef = {'id': projectId,
                  'name': 'Joyous Days'}

    # Create our mock Connection class
    mock = Mock(spec=Connection)

    # Instantiate the project
    p = Project(mock, projectDef)

    # Empty list

    # Override private methods used by this call
    def rv1(*args): return []
    def rv2(*args): return []
    p._listSearchModels = rv1
    p._listProductionModels = rv2

    models = p.listModels()

    self.assertEqual(models, [])

    # Small list

    # Override private methods used by this call
    def rv1(*args): return [{'id': 15}]
    def rv2(*args): return [{'id': 14, 'running': True}]
    p._listSearchModels = rv1
    p._listProductionModels = rv2

    models = p.listModels()

    # Make sure we get back models
    for model in models:
      self.assertIsInstance(model, Model)

    # Second model should be a production model
    self.assertEqual(models[1].type, 'production')

  def testStopAllModels(self):
    '''
    Should make a well formed request to the API for each running model
    '''
    # Setup
    projectId = 3354
    projectDef = {'id': projectId,
                  'name': 'Joyous Days'}

    # Create our mock Connection class
    mock = Mock(spec=Connection)

    # Instantiate the project
    p = Project(mock, projectDef)

    # Override private methods used by this call
    def rv(*args): return [{'id': 14, 'running': True},
                          {'id': 15, 'running': False}]
    p._listProductionModels = rv

    p.stopAllModels()

    mock.request.assert_called_once_with({'productionModelId': 14,
                                     'service': 'productionModelStop'})

  def testCreateStream(self):
    '''
    Should return a stream object
    '''
    # Setup
    projectId = 3354
    projectDef = {'id': projectId,
                  'name': 'Joyous Days'}

    # Create our mock Connection class
    mock = Mock(spec=Connection)

    # Instantiate the project
    p = Project(mock, projectDef)

    # Make the call, test the results
    stream = p.createStream()
    self.assertIsInstance(stream, Stream)
    self.assertEqual(stream.parentProject.id, str(projectId))


if __name__ == '__main__':
  debug = 0
  if debug:
    single = unittest.TestSuite()
    single.addTest(ProjectTestCase('testInstantiation'))
    unittest.TextTestRunner().run(single)
  else:
    unittest.main()
