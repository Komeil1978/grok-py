import unittest
from mock import Mock

from mock import Mock, patch

from grok_test_case import GrokTestCase
import grokpy.enum as grokenum

class EnumTestCase(GrokTestCase):
  

  def testAggregationFunction(self):
    self.assertEqual(grokenum.AggregationFunction.AVERAGE, 'mean')
    self.assertEqual(grokenum.AggregationFunction.SUM, 'sum')
    self.assertEqual(grokenum.AggregationFunction.FIRST, 'first')
    self.assertEqual(grokenum.AggregationFunction.LAST, 'last')
    self.assertEqual(grokenum.AggregationFunction.MAX, 'max')
    self.assertEqual(grokenum.AggregationFunction.MIN, 'min')


if __name__ == '__main__':
  debug = 0
  if debug:
    single = unittest.TestSuite()
    single.addTest(EnumTestCase('testInstantiation'))
    unittest.TextTestRunner().run(single)
  else:
    unittest.main()