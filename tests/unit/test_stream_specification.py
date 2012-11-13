import grokpy
import unittest

from grok_test_case import GrokTestCase
from grokpy.exceptions import GrokError

class StreamSpecTestCase(GrokTestCase):

  def setUp(self):
    '''
    Run before each test
    '''
    self.s = grokpy.StreamSpecification()

  def testIncompleteSettingsFail(self):
    '''
    If we haven't set all required values getSpec should raise an error
    '''

    # Name but no data sources
    s2 = grokpy.StreamSpecification()
    s2.setName('I think its time for some FANCY!')
    self.assertRaises(GrokError, s2.getSpec)

    # Data sources but no name
    s3 = grokpy.StreamSpecification()
    stocks = grokpy.StocksDataSource()
    stocks.addSymbol('AAPL')
    stocks.addDataType(grokpy.StockDataTypes.OPEN_PRICE)
    s3.addDataSource(stocks)
    self.assertRaises(GrokError, s3.getSpec)

  def testAddDataSource(self):
    '''
    Adding an event type should work
    '''

    # Starts empty
    self.assertFalse(self.s.dataSources)

    # Adding an object that is not a data source should fail
    self.assertRaises(GrokError, self.s.addDataSource, 'foobar')

    # Adding a good data source succeeds
    stocks = grokpy.StocksDataSource()
    stocks.addSymbol('AAPL')
    stocks.addDataType(grokpy.StockDataTypes.OPEN_PRICE)

    self.s.addDataSource(stocks)
    self.assertEqual(len(self.s.dataSources), 1)
    self.assertEqual(type(self.s.dataSources[0]), type(stocks))

  def testGetSpec(self):
    '''
    Check the return value of a fully populated field spec
    '''

    # Give this spec a name
    name = 'Lord all mighty, so purple.'
    self.s.setName(name)

    # Add a good data source
    stocks = grokpy.StocksDataSource()
    stocks.addSymbol('AAPL')
    stocks.addDataType(grokpy.StockDataTypes.OPEN_PRICE)

    self.s.addDataSource(stocks)

    expectedDict = {'name': name,
                    'dataSources': [{'dataSourceType': 'public',
                                     'name': 'stocks',
                                     'fields': [{'dataFormat':
                                                {'dataType': 'SCALAR'},
                                                'name': 'AAPL-OpenPrice'}]}]}

    self.assertEqual(self.s.getSpec(), expectedDict)


if __name__ == '__main__':
  debug = 0
  if debug:
    single = unittest.TestSuite()
    single.addTest(StreamSpecTestCase('testGetSpec'))
    unittest.TextTestRunner().run(single)
  else:
    unittest.main()
