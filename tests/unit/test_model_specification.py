import unittest
from mock import Mock
from datetime import datetime

import grokpy
from grok_test_case import GrokTestCase

class ModelSpecificationTestCase(GrokTestCase):

  def setUp(self):
    grokpy.DEBUG = True
    # Create a mock client
    self.client = Mock(spec=grokpy.Client)
    self.client.c = Mock(spec=grokpy.Connection)

    self.name = "Test Name"
    self.predicted_field = "Predicted Field"
    self.streamId = "1234-1234-1234-1234-1234-1234-123456"

  def testModelSpec(self):
    '''
    A low split number should throw an error.
    '''

    def rv(*args):
      return args

    # The function passed in will be called when request() is.
    self.client.c.request.side_effect = rv

    modelSpec = grokpy.ModelSpecification()
    modelSpec.setName(self.name)
    modelSpec.setPredictedField(self.predicted_field)
    modelSpec.setStream(self.streamId)
    
    modelSpecDict = modelSpec.getSpec()

    self.assertTrue('modelType' in modelSpecDict)
    self.assertTrue('name' in modelSpecDict)
    self.assertTrue('predictedField' in modelSpecDict)
    self.assertTrue('streamId' in modelSpecDict)
    self.assertTrue('predictionSteps' in modelSpecDict)

    self.assertEqual(modelSpecDict['modelType'], grokpy.ModelType.PREDICTOR)
    self.assertEqual(modelSpecDict['name'], self.name)
    self.assertEqual(modelSpecDict['predictedField'], self.predicted_field)
    self.assertEqual(modelSpecDict['streamId'], self.streamId)
    self.assertEqual(modelSpecDict['predictionSteps'], [1])


  def testModelSpecTypes(self):
    '''
    A low split number should throw an error.
    '''

    def rv(*args):
      return args

    # The function passed in will be called when request() is.
    self.client.c.request.side_effect = rv

    modelSpec = grokpy.ModelSpecification()
    modelSpec.setName(self.name)
    modelSpec.setPredictedField(self.predicted_field)
    modelSpec.setStream(self.streamId)

    # Test Detector
    modelSpec.setType(grokpy.ModelType.ANOMALY)
    modelSpecDict = modelSpec.getSpec()
    self.assertTrue('modelType' in modelSpecDict)
    self.assertEqual(modelSpecDict['modelType'], grokpy.ModelType.ANOMALY)

    # Test Predictor
    modelSpec.setType(grokpy.ModelType.PREDICTOR)
    modelSpecDict = modelSpec.getSpec()
    self.assertTrue('modelType' in modelSpecDict)
    self.assertEqual(modelSpecDict['modelType'], grokpy.ModelType.PREDICTOR)

    

if __name__ == '__main__':
  debug = 0
  if debug:
    single = unittest.TestSuite()
    unittest.TextTestRunner().run(single)
  else:
    unittest.main()
