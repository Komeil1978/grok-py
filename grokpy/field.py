import inspect
import json


class Field(object):
  '''
  A complex object specification which allows Grok to properly interpret
  input data.
  '''

  def __init__(self, descDict):
    # Create a dictionary describing this field
    self.description = descDict

  @staticmethod
  def getFieldFromJSON(jsonString):
    '''
    Accepts a JSON string and returns a Field object
    '''
    
    description = json.loads(jsonString)
    
    return Field(**description)
