'''
A set of Enum-like classes to specifiy the strings expected by the API
in a straight forward and self-documenting fashion.
'''

class Aggregation(object):

  RECORD = 'record'
  SECONDS = 'seconds'
  MINUTES = 'minutes'
  MINUTES_15 = 'minutes15'
  HOURS = 'hours'
  DAYS = 'days'
  WEEKS = 'weeks'
  MONTHS = 'months'

class SwarmSize(object):

  SMALL = 'small'
  MEDIUM = 'medium' # Default
  LARGE = 'large'

class SwarmStatus(object):

  STARTING = 'starting'
  RUNNING = 'running'
  CANCELED = 'canceled'
  COMPLETED = 'completed'

class DataType(object):

  DATETIME = 'DATETIME' # a point in time.
  ENUMERATION = 'ENUMERATION' # a category.
  IP_ADDRESS = 'IP_ADDRESS' # an IP address (V4).
  LAT_LONG = 'LAT_LONG' # a latitude/longitude combination.
  SCALAR = 'SCALAR' # a numeric value.
  ZIP_CODE = 'ZIP_CODE' # a U.S. zip code. Aggregated with first or last.

class DataFlag(object):

  NONE = 'NONE'
  RESET = 'RESET'
  SEQUENCE = 'SEQUENCE'
  TIMESTAMP = 'TIMESTAMP'
