from client import Client
from connection import Connection
from model import Model
from model_specification import ModelSpecification
from project import Project
from enum import (Aggregation,
                  SwarmSize,
                  SwarmStatus,
                  DataType,
                  DataFlag,
                  AggregationFunction,
                  PredictionType,
                  DataSourceType,
                  PublicDataSources,
                  WeatherDataType,
                  StockDataTypes,
                  HolidayLocale)
from stream import Stream
from stream_specification import StreamSpecification
from local_data_source import LocalDataSource
from weather_data_source import WeatherDataSource
from events_data_source import EventsDataSource
from stocks_data_source import StocksDataSource
from data_source_field import DataSourceField

from exceptions import (AuthenticationError,
                        GrokError)

# Debug variable
DEBUG = False

__version__ = '0.2.2'

__all__ = ['Client', 'Connection', 'Model', 'Project', 'Stream',
           'StreamSpecification', 'LocalDataSource', 'WeatherDataSource',
           'DataSourceField']
