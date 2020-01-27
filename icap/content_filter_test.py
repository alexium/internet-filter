#!/usr/bin/python3
"""Unit tests for content filter."""
import unittest

from content_filter import Filter


class TestContentFilter(unittest.TestCase):
  """Unit tests for Icap server."""


  def test_content_filter(self):
    """Test content filter."""
    whitelist = '\n\nfoo.com  \n foo.bar.com  # blah blah  \n'
    content_filter = Filter(whitelist)
    self.assertFalse(content_filter.allowed('baz.com'))
    self.assertTrue(content_filter.allowed('foo.com'))
    self.assertTrue(content_filter.allowed('bar.foo.com'))
    self.assertTrue(content_filter.allowed('foo.bar.com'))
    self.assertFalse(content_filter.allowed('bar.com'))


if __name__ == '__main__':
  unittest.main()
