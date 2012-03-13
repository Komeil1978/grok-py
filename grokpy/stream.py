import os
import sys
import json
import math
import StringIO
import traceback

from field import Field

from exceptions import GrokError, AuthenticationError

class Stream(object):
  '''
  A Stream is the combination of data and the specification of those data
  that will be used by a model
  '''

  def __init__(self, parent, streamDef):

    # Give streams access to the parent client/project and its connection
    self.parent = parent
    self.c = self.parent.c

    # Take everything we're passed and make it an instance property.
    self.__dict__.update(streamDef)

  def addField(self, **kwargs):
    '''
    Add a field object to a stream
    '''
    newField = Field(**kwargs)

    self.streamDescription['fields'].append(newField.fieldDescription)

    return newField

  def addRecords(self, records, step = 5000):
    '''
    Appends records to the input cache of the given stream.
    '''

    # Where to POST the data
    url = self.dataUrl

    try:
      if len(records) > step:
        i = 0
        while i < len(records):
          requestDef = {"input": records[i:(i+step)]}
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

  def configure(self, filePath):
    '''
    Reads JSON from a given file and uses that to configure the stream
    '''
    pass

  def delete(self):
    '''
    Permanently deletes this stream.

    WARNING: There is currently no way to recover from this opperation.
    '''
    self.c.request('DELETE', self.url)

  def usePublicDataSource(self, publicDataSource):
    '''
    Takes a configured publicDataSource and attaches it to the stream
    '''

    # Check if there is configuration we need to complete
    if publicDataSource.locationFieldName:
      publicDataSource.description['configuration'] = \
      str(self._getFieldIndex(publicDataSource.locationFieldName))

    projDesc = self.parentProject.getDescription()
    projDesc['providers'].append(publicDataSource.description)

    requestDef = {'service': 'projectUpdate',
                  'project': projDesc}

    self.parentProject.projectDef = self.c.request(requestDef)

  #############################################################################
  # Private methods

  def _getFieldIndex(self, fieldName):
    '''
    Finds a field with a matching name and throws an error if there are more
    than one matches
    '''

    counter = 0
    index = 0
    for field in self.streamDescription['fields']:
      if field['name'] == fieldName:
        counter += 1
        index = field['index']

    if not counter:
      raise GrokError('Field not found: ' + fieldName)
    if counter > 1:
      raise GrokError('Duplicate Field Name: ' + fieldName + ' More than one '
                      'field with this name was found. Please use the '
                      'set*FieldIndex() methods directly.')


    return index

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
