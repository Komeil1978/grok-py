import os
import sys
import json
import math
import StringIO
import traceback
import grokpy

from exceptions import GrokError, AuthenticationError

class Stream(object):
  '''
  A Stream is the combination of data and the specification of those data
  that will be used by a model
  '''

<<<<<<< HEAD
  def __init__(self, parent, streamDef):

    # Give streams access to the parent client/project and its connection
    self.parent = parent
    self.c = self.parent.c
=======
  def __init__(self, parentProject):

    # Our connection to the Grok API
    self.c = parentProject.c

    # Our stream description
    self.streamDescription = {'fields': []}

    # HACK: Our local data store
    # In API v2 this should go away
    self.records = None

    self.parentProject = parentProject
>>>>>>> 0ff1eeda9d2ffc932ff73f6bf70f2f4b94fd1d73

    # Take everything we're passed and make it an instance property.
    self.__dict__.update(streamDef)

  def addRecords(self, records, step = 5000):
    '''
    Appends records to the input cache of the given stream.
<<<<<<< HEAD
    '''

    # Where to POST the data
    url = self.dataUrl
=======

    WARNING: HACK

    Due to the current object model we actually send the records in the
    model.startSwarm() method, using the _addRecords() method below.
    '''

    if not self.streamDescription['fields']:
      raise GrokError('No fields found. Please configure your stream before '
                      'adding records.')
    self.records = records

    return len(self.records)

  def _addRecords(self, modelId, service, param, step = 5000):
    '''
    WARNING: HACK

    This is the method that actually sends records.
    It is called during model.startSwarm()

    We will start out trying to send a max of 5k records at a time. This can
    fail if the records are very wide. If it fails we will halve the number
    of records we try to send until they fit into a single request.
    '''

    if not self.records:
      raise GrokError('There are no records to send. Please make sure you have '
                      'previously added records to the stream using the '
                      'stream.addRecords() method')

    try:
      if len(self.records) > step:
        i = 0
        while i < len(self.records):
          requestDef = {'service': service,
                      param: modelId,
                      'data': self.records[i:(i+step)]}

          self.c.request(requestDef)
          i += step

      else:
        requestDef = {'service': service,
                      param: modelId,
                      'data': self.records}

        self.c.request(requestDef)
    except GrokError:
      # Break recursion if this just isn't going to work
      if step < 100: raise
      # Try sending half as many records.
      step = int(math.floor(step / 2))
      self._addRecords(modelId, service, param, step)

  def configure(self, filePath):
    '''
    Reads JSON from a given file and uses that to configure the stream
    '''
    fileHandle = open(filePath, 'rU')
>>>>>>> 0ff1eeda9d2ffc932ff73f6bf70f2f4b94fd1d73

    try:
      if len(records) > step:
        i = 0
        while i < len(records):
          requestDef = {"input": records[i:(i+step)]}
          if grokpy.DEBUG:
            print len(requestDef['input'])
          self.c.request('POST', url, requestDef)
          i += step
      # If it's small enough send everything
      else:
        requestDef = {"input": records}
        self.c.request('POST', url, requestDef)
    except GrokError:
      # Break recursion if this just isn't going to work
      if step < 100: raise
      # Try sending half as many records.
      step = int(math.floor(step / 2))
      self.addRecords(records, step)

  def delete(self):
    '''
    Permanently deletes this stream.

    WARNING: There is currently no way to recover from this opperation.
    '''
    self.c.request('DELETE', self.url)

  #############################################################################
  # Private methods

  def _safe_dict(self, d):
    '''
    Recursively clone json structure with UTF-8 dictionary keys

    From: http://www.gossamer-threads.com/lists/python/python/684379
    '''
    if isinstance(d, dict):
      return dict([(k.encode('utf-8'), self._safe_dict(v)) for k,v in d.iteritems()])
    elif isinstance(d, list):
      return [self._safe_dict(x) for x in d]
    else:
      return d
