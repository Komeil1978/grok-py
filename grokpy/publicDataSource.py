from exceptions import GrokError, AuthenticationError

class PublicDataSource(object):
  '''
  Object describing a public data source
  '''

  def __init__(self, connection, description):

    self.c = connection

    self.__dict__.update(description)
