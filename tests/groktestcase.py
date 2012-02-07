import unittest
import re

class GrokTestCase(unittest.TestCase):
  '''
  Extend the functionality of unittest with a few of the assertions
  from unittest2 / python2.7
  '''

  def assertRaisesRegexp(self, expected_exception, expected_regexp,
                       callable_obj=None, *args, **kwargs):
    """Asserts that the message in a raised exception matches a regexp.

    Args:
        expected_exception: Exception class expected to be raised.
        expected_regexp: Regexp (re pattern object or string) expected
                to be found in error message.
        callable_obj: Function to be called.
        args: Extra args.
        kwargs: Extra kwargs.
    """
    if callable_obj is None:
        return _AssertRaisesContext(expected_exception, self, expected_regexp)
    try:
        callable_obj(*args, **kwargs)
    except expected_exception, exc_value:
        if isinstance(expected_regexp, basestring):
            expected_regexp = re.compile(expected_regexp)
        if not expected_regexp.search(str(exc_value)):
            raise self.failureException('"%s" does not match "%s"' %
                     (expected_regexp.pattern, str(exc_value)))
    else:
        if hasattr(expected_exception, '__name__'):
            excName = expected_exception.__name__
        else:
            excName = str(expected_exception)
        raise self.failureException, "%s not raised" % excName

  def assertIsInstance(self, obj, cls, msg=None):
    """Same as self.assertTrue(isinstance(obj, cls)), with a nicer
    default message."""
    if not isinstance(obj, cls):
        standardMsg = '%s is not an instance of %r' % (safe_repr(obj), cls)
        self.fail(self._formatMessage(msg, standardMsg))

class _AssertRaisesContext(object):
    """A context manager used to implement TestCase.assertRaises* methods."""

    def __init__(self, expected, test_case, expected_regexp=None):
        self.expected = expected
        self.failureException = test_case.failureException
        self.expected_regexp = expected_regexp

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb):
        if exc_type is None:
            try:
                exc_name = self.expected.__name__
            except AttributeError:
                exc_name = str(self.expected)
            raise self.failureException(
                "%s not raised" % (exc_name,))
        if not issubclass(exc_type, self.expected):
            # let unexpected exceptions pass through
            return False
        self.exception = exc_value # store for later retrieval
        if self.expected_regexp is None:
            return True

        expected_regexp = self.expected_regexp
        if isinstance(expected_regexp, basestring):
            expected_regexp = re.compile(expected_regexp)
        if not expected_regexp.search(str(exc_value)):
            raise self.failureException('"%s" does not match "%s"' %
                     (expected_regexp.pattern, str(exc_value)))
        return True
