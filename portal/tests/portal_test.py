#!/usr/bin/python3
"""Unit tests for portal."""

import unittest

from portal import create_app
from portal import database


class TestPortal(unittest.TestCase):
  """Unit tests for portal."""

  def setUp(self):
    config = ({ 'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:' })
    app = create_app(test_config=config)
    with app.app_context():
      database.init_db()
    

  def testPortal(self):
    print("foo")


if __name__ == '__main__':
  unittest.main()
