'''
Base exceptions for the ntabeta Client Library
'''

class ntabetaError(Exception):
  pass

class AuthenticationError(ntabetaError):
  pass