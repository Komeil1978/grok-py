import os

class Stream(object):
  '''
  A stream defines the characteristics of data being sent into Grok
  
  It is composed of fields and stream options such as:
      Aggregation
      Joining to Data Files
      Joining to Public Data
  '''

  def __init__(self):
    pass

  def addField(self, field):
    '''
    Add a field object to a stream
    '''
    pass

  def useAggregation(self):
    '''
    If a DATETIME field is present you can aggregate any of your other
    fields over time
    '''
    pass

  def joinPublicData(self):
    '''
    Select which public data sources to join into this stream on the server
    '''
    pass

  def joinDataFile(self):
    '''
    Specifies a local CSV to upload and join into this stream during
    Swam and prediction
    '''
    pass