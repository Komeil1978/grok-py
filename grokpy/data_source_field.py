import grokpy

from grokpy.exceptions import GrokError

class DataSourceField(object):
  '''
  A local object used to build up a stream specification
  '''

  def __init__(self):

    # Default empty values
    self.name = None

    self.type = None

    self.flag = None

  def setName(self, name):
    '''
    Updates the local name of this field

    * name - A short string describing this field.
    '''
    self.name = name

  def setType(self, type):
    '''
    Updates the local type of this field

    * type - A grokpy.DataType enum value
    '''

    self.type = type

  def setFlag(self, flag):
    '''
    Optional - Sets a flag locally for this field.

    * flag - A grokpy.DataFlag enum value
    '''

    self.flag = flag

  def getSpec(self):
    '''
    Returns the constructed dict representation of this field
    '''

    if not self.name or not self.type:
      raise GrokError('Please set both a name and a type for this field')

    returnSpec = {"name": self.name,
                  "dataFormat": {"dataType": self.type}}

    if self.flag:
      returnSpec['flag'] = self.flag


    return returnSpec
