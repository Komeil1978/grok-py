import grokpy

from grokpy.exceptions import GrokError

class StreamSpecification(object):
  '''
  This is a client level object that is useful for building Stream
  Specifications in an object oriented way. (As opposed to writing the JSON
  directly). By adding dataSources you can add both local and public data
  to your stream.
  '''

  def __init__(self):

    # What is the name of this stream
    self.name = ''

    # What data sources are in this stream
    self.dataSources = []

  def setName(self, name):
    '''
    Updates the local name.
    '''
    self.name = name

  def addDataSource(self, dataSource):
    '''
    Adds the data source to the local list of data sources for later assembly
    into a descriptive dict.
    '''
    self.dataSources.append(dataSource)

  def getSpec(self):
    '''
    Returns an assembled dict from the current state of the specification
    '''

    if self.name == '':
      raise GrokError('Please set a name for this stream')

    if self.dataSources == []:
      raise GrokError('Please add at least one dataSource to this '
                      'specification.')

    returnSpec = {"name": self.name,
                 "dataSources": []}

    for dataSource in self.dataSources:
      returnSpec['dataSources'].append(dataSource.getSpec())

    return returnSpec
