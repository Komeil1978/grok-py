import unittest
from mock import Mock
from datetime import datetime

from mock import Mock, patch

from grok_test_case import GrokTestCase
from grokpy.connection import Connection
from grokpy.exceptions import GrokError
from grokpy.model import Model
from grokpy.stream import Stream
from grokpy.client import Client

class ModelTestCase(GrokTestCase):

  def setUp(self):
    # Create a mock client
    self.client = Mock(spec=Client)
    self.client.c = Mock(spec=Connection)

    # Create our minimal streamDef
    self.modelDef = {
      'dataUrl':'http://example.com',
      'url': 'http://example.com'
    }

    # Instantiate the stream
    self.m = Model(self.client, self.modelDef)


  @patch.object(Model, '_runCommand', spec=Model._runCommand)
  def testModelSetAnomalyAutoDetectThreshold(self, runCommandMock):

    self.m.setAnomalyAutoDetectThreshold('mockThreshold')
    runCommandMock.assert_called_once_with('setAutoDetectThreshold', 
      autoDetectThreshold='mockThreshold')
    runCommandMock.reset_mock()

    self.assertRaises(Exception, self.m.setAnomalyAutoDetectThreshold, 
      badParam='test')

    self.assertRaises(Exception, self.m.setAnomalyAutoDetectThreshold)


  @patch.object(Model, '_runCommand', spec=Model._runCommand)
  def testModelGetAnomalyAutoDetectThreshold(self, runCommandMock):

    self.m.getAnomalyAutoDetectThreshold()
    runCommandMock.assert_called_once_with('getAutoDetectThreshold')
    runCommandMock.reset_mock()

    self.assertRaises(Exception, self.m.getAnomalyAutoDetectThreshold, 
      badParam='test')


  @patch.object(Model, '_runCommand', spec=Model._runCommand)
  def testModelGetLabels(self, runCommandMock):

    self.m.getLabels()
    runCommandMock.assert_called_once_with('getLabels', 
      startRecordID=None,
      endRecordID=None)
    runCommandMock.reset_mock()

    self.m.getLabels(startRecordID=10)
    runCommandMock.assert_called_once_with('getLabels', 
      startRecordID=10,
      endRecordID=None)
    runCommandMock.reset_mock()

    self.m.getLabels(endRecordID=10)
    runCommandMock.assert_called_once_with('getLabels', 
      startRecordID=None, endRecordID=10)
    runCommandMock.reset_mock()

    self.assertRaises(Exception, self.m.addLabel, badParam='test')

  @patch.object(Model, '_runCommand', spec=Model._runCommand)
  def testModelAddLabels(self, runCommandMock):

    self.m.addLabel(startRecordID=10, endRecordID=15, labelName='test')
    runCommandMock.assert_called_once_with(
      'addLabel',
      startRecordID= 10,
      endRecordID= 15,
      labelName= 'test'
    )
    runCommandMock.reset_mock()

    self.assertRaises(Exception, self.m.addLabel, startRecordID=10)

    self.assertRaises(Exception, self.m.addLabel, badParam='test')


  @patch.object(Model, '_runCommand', spec=Model._runCommand)
  def testModelRemoveLabels(self, runCommandMock):

    self.m.removeLabels(startRecordID=10)
    runCommandMock.assert_called_once_with(
      'removeLabels',
      startRecordID= 10,
      endRecordID=None,
      labelFilter=None
    )
    runCommandMock.reset_mock()

    self.m.removeLabels(startRecordID=10, endRecordID=15)
    runCommandMock.assert_called_once_with(
      'removeLabels',
      startRecordID= 10,
      endRecordID= 15,
      labelFilter= None
    )
    runCommandMock.reset_mock()

    self.m.removeLabels(startRecordID=10, endRecordID=15, labelFilter='test')
    runCommandMock.assert_called_once_with(
      'removeLabels',
      startRecordID= 10,
      endRecordID= 15,
      labelFilter= 'test'
    )
    runCommandMock.reset_mock()

    self.assertRaises(Exception, self.m.removeLabels, badParam='test')

    
    
if __name__ == '__main__':
  debug = 0
  if debug:
    single = unittest.TestSuite()
    single.addTest(ModelTestCase('testInstantiation'))
    unittest.TextTestRunner().run(single)
  else:
    unittest.main()