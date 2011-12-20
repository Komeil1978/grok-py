
class Field(object):
  '''
  A complex object specification which allows Grok to properly interpret
  input data.
  '''

  def __init__(self,
               aggregationFunction = "first",
               formatString = None,
               dataType = "ENUMERATION",
               fieldRange = None,
               fieldSubset = None,
               flag = None,
               index = 0,
               name = "gym",
               useField = True):
    pass

  @staticmethod
  def getFieldFromJSON(jsonString):
    '''
    Accepts a JSON string and returns a Field object
    '''
    return Field()
