import unittest
from mock import Mock

from grok_test_case import GrokTestCase
from grokpy.connection import Connection
from grokpy.project import Project
from grokpy.exceptions import GrokError
from grokpy.model import Model
from grokpy.stream import Stream

class StreamTestCase(GrokTestCase):

  def setUp(self):
    self.mockKey = 'SeQ9AhK57vOeoySQn1EvwElhZV1X87AB'

  def testInstantiation(self):
    '''
    Basic object instantiation with mocks
    '''

    # Create our mock Project class
    proj = Mock(spec=Project)
    conn = Mock(spec=Connection)

    projId = '5344'
    proj.id = projId
    proj.c = conn

    # Instantiate the stream
    s = Stream(proj)

    self.assertEqual(s.parentProject.id, projId)

if __name__ == '__main__':
  debug = 0
  if debug:
    single = unittest.TestSuite()
    single.addTest(StreamTestCase('testInstantiation'))
    unittest.TextTestRunner().run(single)
  else:
    unittest.main()
