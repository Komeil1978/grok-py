import grokpy
import unittest

from grok_test_case import GrokTestCase
from grokpy.exceptions import GrokError

class StocksDataSourceTestCase(GrokTestCase):

  def setUp(self):
    '''
    Run before each test
    '''

    self.s = grokpy.StocksDataSource()

  def testGoodInstantiation(self):
    '''
    Basic object instantiation
    '''
    # Instantiate the Grok object
    s = grokpy.StocksDataSource()

  def testIncompleteSettingsFail(self):
    '''
    If we haven't set all required values getSpec should raise an error
    '''

    # Neither stocks nor data types
    self.assertRaises(GrokError, self.s.getSpec)

    # Without datatype
    self.s.addSymbol('AAPL')
    self.assertRaises(GrokError, self.s.getSpec)

    # Without stocks
    s2 = grokpy.StocksDataSource()
    s2.addDataType(grokpy.StockDataTypes.OPEN_PRICE)
    self.assertRaises(GrokError, s2.getSpec)

  def testAddSymbol(self):
    '''
    Adding a single symbol should work
    '''

    # Starts empty
    self.assertFalse(self.s.symbols)

    # Bad set fails
    self.assertRaises(GrokError, self.s.addSymbol, 'MUCH_TOO_LONG')

    # Good set works
    symbol = 'MSFT'
    self.s.addSymbol(symbol)
    self.assertEqual(len(self.s.symbols), 1)
    self.assertEqual(self.s.symbols[0], symbol)

  def testAddSymbols(self):
    '''
    Adding multiple symbols at once should work
    '''

    # Starts empty
    self.assertFalse(self.s.symbols)

    # Good set works
    symbols = ['MSFT','AAPL','GE']
    self.s.addSymbols(symbols)
    self.assertEqual(len(self.s.symbols), 3)
    self.assertEqual(self.s.symbols, symbols)

  def testAddDataType(self):
    '''
    Adding a data type should work, invalid types should throw errors
    '''

    # Valid types
    type1 = grokpy.StockDataTypes.OPEN_PRICE
    type2 = grokpy.StockDataTypes.HIGH_PRICE
    types = [type1, type2]
    self.s.addDataType(type1)
    self.s.addDataType(type2)

    self.assertEqual(len(self.s.dataTypes), 2)
    self.assertEqual(self.s.dataTypes, types)

    # Invalid type
    s2 = grokpy.StocksDataSource()
    self.assertRaises(GrokError, s2.addDataType, 'FROOOMBAR!!!!')

  def testGetSpec(self):
    '''
    Check the return value of a fully populated field spec
    '''

    # Add symbols
    symbols = ['MSFT','AAPL','GE']
    self.s.addSymbols(symbols)

    # Add types
    type1 = grokpy.StockDataTypes.OPEN_PRICE
    type2 = grokpy.StockDataTypes.HIGH_PRICE
    self.s.addDataType(type1)
    self.s.addDataType(type2)

    expectedDict = {'dataSourceType': 'public',
                    'name': 'stocks',
                    'fields': [{'dataFormat': {'dataType': 'SCALAR'},
                                'name': 'MSFT-OpenPrice'},
                               {'dataFormat': {'dataType': 'SCALAR'},
                                'name': 'MSFT-HighPrice'},
                               {'dataFormat': {'dataType': 'SCALAR'},
                                'name': 'AAPL-OpenPrice'},
                               {'dataFormat': {'dataType': 'SCALAR'},
                                'name': 'AAPL-HighPrice'},
                               {'dataFormat': {'dataType': 'SCALAR'},
                                'name': 'GE-OpenPrice'},
                               {'dataFormat': {'dataType': 'SCALAR'},
                                'name': 'GE-HighPrice'}]}

    self.assertEqual(self.s.getSpec(), expectedDict)

    # Calling this again shouldn't change the spec
    self.assertEqual(self.s.getSpec(), expectedDict)

if __name__ == '__main__':
  debug = 0
  if debug:
    single = unittest.TestSuite()
    single.addTest(StocksDataSourceTestCase('testAddDataType'))
    unittest.TextTestRunner().run(single)
  else:
    unittest.main()
