import unittest
from mock import Mock
from datetime import datetime

from grok_test_case import GrokTestCase
from grokpy.connection import Connection
from grokpy.exceptions import GrokError
from grokpy.model import Model
from grokpy.stream import Stream
from grokpy.client import Client

class StreamTestCase(GrokTestCase):

  def setUp(self):
    # Create a mock client
    self.client = Mock(spec=Client)
    self.client.c = Mock(spec=Connection)

    # Create our minimal streamDef
    self.streamDef = {'dataUrl':'http://example.com',
                      'url': 'http://example.com'}

    # Instantiate the stream
    self.s = Stream(self.client, self.streamDef)

  def testAddRecordsLowSplit(self):
    '''
    A low split number should throw an error.
    '''

    self.client.c.request.side_effect = GrokError("Boom!")

    # Make some dummy records
    records = []
    for i in range(50):
      records.append([0])

    self.assertRaises(GrokError, self.s.addRecords, records, 40)

  def testAddRecordsSmallRecordCount(self):
    '''
    Should pass without comment
    '''

    # Make some dummy records
    records = []
    for i in range(50):
      records.append([0])

    self.s.addRecords(records)

  def testAddRecordsLargeRecordCountBad(self):
    '''
    Should raise an error eventually
    '''

    self.client.c.request.side_effect = GrokError("Boom!")

    # Make some dummy records
    records = []
    for i in range(5000):
      records.append([0])

    self.assertRaises(GrokError, self.s.addRecords, records)

  def testAddRecordsLargeRecordCountGood(self):
    '''
    Should pass without comment
    '''

    # Make some dummy records
    records = []
    for i in range(5000):
      records.append([0])


    self.s.addRecords(records)

  def testDelete(self):
    '''
    No-op in unit test context
    '''

    self.s.delete()

  def testGetSpecDict(self):
    '''
    We should get back the same data we put in
    '''

    self.assertEqual(self.s.getSpecDict(), self.streamDef)

  def testAddRecordsWithPythonDatetimes(self):
    '''
    Records that include datetime objects should be silently converted to
    strings and passed on without error
    '''

    # Make some dummy records
    records = []
    for i in range(10):
      records.append([datetime.now(), 'foo', 14])

    self.s.addRecords(records)

if __name__ == '__main__':
  debug = 0
  if debug:
    single = unittest.TestSuite()
    single.addTest(StreamTestCase('testInstantiation'))
    unittest.TextTestRunner().run(single)
  else:
    unittest.main()
