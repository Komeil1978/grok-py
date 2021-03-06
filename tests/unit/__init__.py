import unittest

from test_client import ClientTestCase
from test_connection import ConnectionTestCase
from test_project import ProjectTestCase
from test_stream import StreamTestCase
from test_data_source_field import DataSourceFieldTestCase
from test_stocks_data_source import StocksDataSourceTestCase
from test_events_data_source import EventsDataSourceTestCase
from test_stream_specification import StreamSpecTestCase

def all_tests():
    suite = unittest.TestSuite()

    # Add tests to run here
    suite.addTest(unittest.makeSuite(ClientTestCase))
    suite.addTest(unittest.makeSuite(ConnectionTestCase))
    suite.addTest(unittest.makeSuite(ProjectTestCase))
    suite.addTest(unittest.makeSuite(StreamTestCase))
    suite.addTest(unittest.makeSuite(DataSourceFieldTestCase))
    suite.addTest(unittest.makeSuite(StocksDataSourceTestCase))
    suite.addTest(unittest.makeSuite(EventsDataSourceTestCase))
    suite.addTest(unittest.makeSuite(StreamSpecTestCase))

    return suite
