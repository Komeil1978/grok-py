import grokpy
import unittest

from grok_test_case import GrokTestCase
from grokpy.exceptions import GrokError

class EventsDataSourceTestCase(GrokTestCase):

  def setUp(self):
    '''
    Run before each test
    '''

    self.e = grokpy.EventsDataSource()

  def testIncompleteSettingsFail(self):
    '''
    If we haven't set all required values getSpec should raise an error
    '''

    # No events
    self.assertRaises(GrokError, self.e.getSpec)

  def testAddEventType(self):
    '''
    Adding an event type should work
    '''

    # Starts empty
    self.assertFalse(self.e.fields)

    # Bad set fails
    self.assertRaises(GrokError, self.e.addEventType, 'GARBAGE')

    # Good set works
    eType = grokpy.HolidayLocale.CA_HOLIDAYS
    self.e.addEventType(eType)
    self.assertEqual(len(self.e.fields), 1)

  def testGetSpec(self):
    '''
    Check the return value of a fully populated field spec
    '''

    # Add type
    eType = grokpy.HolidayLocale.CA_HOLIDAYS
    self.e.addEventType(eType)

    expectedDict = {'dataSourceType': 'public',
                    'name': 'events',
                    'fields': [{'dataFormat': {'dataType': 'CATEGORY'},
                                'name': 'CA-HOLIDAYS'}]}

    self.assertEqual(self.e.getSpec(), expectedDict)


if __name__ == '__main__':
  debug = 0
  if debug:
    single = unittest.TestSuite()
    single.addTest(EventsDataSourceTestCase('testAddDataType'))
    unittest.TextTestRunner().run(single)
  else:
    unittest.main()
