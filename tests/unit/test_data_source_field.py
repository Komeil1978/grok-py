import grokpy
import unittest

from grok_test_case import GrokTestCase
from grokpy.exceptions import GrokError

class DataSourceFieldTestCase(GrokTestCase):

  def setUp(self):

    self.f = grokpy.DataSourceField()

  def testGoodInstantiation(self):
    '''
    Basic object instantiation
    '''
    # Instantiate the Grok object
    f = grokpy.DataSourceField()

  def testIncompleteSettingsFail(self):
    '''
    If we haven't set all required values getSpec should raise an error
    '''
    self.assertRaises(GrokError, self.f.getSpec)

  def testSetName(self):
    '''
    Setting a name should work
    '''

    # Starts empty
    self.assertFalse(self.f.name)

    # Setting a very long name fails
    longName = ('This is a really long name, in fact one might say too long '
                'for something as simple as a field name. Who would have a '
                'name like this? Really it is insane. OMG this really has '
                'to be longer? Is that something that needs to be blah blah '
                'mumpty mumpty nurple nurple ting ting bang zap foo')
    self.assertRaises(GrokError, self.f.setName, longName)

    # Good set works
    name = 'foo'
    self.f.setName(name)
    self.assertEqual(self.f.name, name)

  def testSetType(self):
    '''
    Setting a type should work
    '''

    # Starts empty
    self.assertFalse(self.f.type)

    # Bad set fails
    self.assertRaises(GrokError, self.f.setType, 'foo')

    # Good set works
    dataType = grokpy.DataType.SCALAR
    self.f.setType(dataType)
    self.assertEqual(self.f.type, dataType)

  def testSetFlag(self):
    '''
    Setting a flag should work
    '''

    # Starts empty
    self.assertFalse(self.f.flag)

    # Bad set fails
    self.assertRaises(GrokError, self.f.setFlag, 'foo')

    # Good set succeeds
    flag = grokpy.DataFlag.TIMESTAMP
    self.f.setFlag(flag)
    self.assertEqual(self.f.flag, flag)

  def testSetAggregationFunction(self):
    '''
    Setting a function should work and catch various type mismatches
    '''

    # Test independance yay!
    f = grokpy.DataSourceField()

    # Starts empty
    self.assertFalse(f.aggregationFunction)

    # Early set fails
    self.assertRaises(GrokError,
                      f.setAggregationFunction, grokpy.AggregationFunction.SUM)

    # Set a valid type
    f.setType(grokpy.DataType.CATEGORY)

    # Mismatch with field type set fails
    self.assertRaises(GrokError,
                      f.setAggregationFunction, grokpy.AggregationFunction.SUM)

    # Good set succeeds
    aggFunc = grokpy.AggregationFunction.FIRST
    f.setAggregationFunction(aggFunc)
    self.assertEqual(f.aggregationFunction, aggFunc)

  def testSetMin(self):
    '''
    Setting min should work
    '''

    # Test independance yay!
    f = grokpy.DataSourceField()
    f.setType(grokpy.DataType.SCALAR)

    # Starts empty
    self.assertFalse(f.minValue)

    # Bad set fails
    self.assertRaises(GrokError, f.setMin, 'foo')

    # Good set works
    minValue = -33
    f.setMin(minValue)
    self.assertEqual(f.minValue, minValue)

  def testSetMax(self):
    '''
    Setting a max value should work
    '''
    # Test independance yay!
    f = grokpy.DataSourceField()
    f.setType(grokpy.DataType.SCALAR)

    # Starts empty
    self.assertFalse(f.maxValue)

    # Bad set fails
    self.assertRaises(GrokError, f.setMax, 'foo')

    # Good set works
    maxValue = 33.00009
    f.setMax(maxValue)
    self.assertEqual(f.maxValue, maxValue)

  def testGetSpec(self):
    '''
    Check the return value of a fully populated field spec
    '''
    # Test independance yay!
    f = grokpy.DataSourceField()
    name = 'Days of Joy'
    f.setName(name)
    dataType = grokpy.DataType.SCALAR
    f.setType(dataType)
    aggFunc = grokpy.AggregationFunction.SUM
    f.setAggregationFunction(aggFunc)
    minValue = -444
    maxValue = 444.2
    f.setMin(minValue)
    f.setMax(maxValue)

    expectedDict = {'max': maxValue,
                    'dataFormat': {'dataType': dataType},
                    'name': name,
                    'min': minValue,
                    'aggregationFunction': aggFunc}

    self.assertEqual(f.getSpec(), expectedDict)

if __name__ == '__main__':
  debug = 0
  if debug:
    single = unittest.TestSuite()
    single.addTest(ClientTestCase('testBadConnection'))
    unittest.TextTestRunner().run(single)
  else:
    unittest.main()
