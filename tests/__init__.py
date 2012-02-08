import unittest

from TestClient import ClientTestCase
from TestConnection import ConnectionTestCase
from TestProject import ProjectTestCase

def all_tests():
    suite = unittest.TestSuite()

    # Add tests to run here
    suite.addTest(unittest.makeSuite(ClientTestCase))
    suite.addTest(unittest.makeSuite(ConnectionTestCase))
    suite.addTest(unittest.makeSuite(ProjectTestCase))

    return suite
