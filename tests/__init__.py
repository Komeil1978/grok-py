import unittest

from TestClient import ClientTestCase
from TestConnection import ConnectionTestCase
from TestProject import ProjectTestCase
from TestStream import StreamTestCase

def all_tests():
    suite = unittest.TestSuite()

    # Add tests to run here
    suite.addTest(unittest.makeSuite(ClientTestCase))
    suite.addTest(unittest.makeSuite(ConnectionTestCase))
    suite.addTest(unittest.makeSuite(ProjectTestCase))
    suite.addTest(unittest.makeSuite(StreamTestCase))

    return suite
