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

