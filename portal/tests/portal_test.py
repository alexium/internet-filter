#!/usr/bin/python3
"""Unit tests for portal."""
import time
import unittest

from datetime import datetime
from flask_login import current_user
from portal import create_app
from portal import database
from portal.database import User


class TestPortal(unittest.TestCase):
  """Unit tests for portal."""

  def setUp(self):
    config = ({'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'})
    self.app = create_app(test_config=config)
    with self.app.app_context():
      database.init_db()

  def test_home(self):
    """Test home page."""
    with self.app.test_client() as client:
      response = client.get('/')
      self.assertEqual(200, response.status_code)

  def test_login_with_good_pw(self):
    """Tests login form with good password."""
    min_session_expiration = datetime.fromtimestamp(
      time.time() + User.SESSION_DURATION)
    with self.app.test_client() as client:
      client.post('/login', data={
        'username': 'test', 'password': 'test'}, follow_redirects=True)
      self.assertEqual(current_user.username, 'test')
      self.assertEqual(current_user.ip_addr, '127.0.0.1')
      self.assertTrue(current_user.is_authenticated)
      user = User.query.filter_by(username=current_user.username).first()
      self.assertLess(min_session_expiration, user.session_expiration)
      self.assertEqual('127.0.0.1', user.ip_addr)

  def test_login_with_bad_pw(self):
    """Tests login form with bad password."""
    with self.app.test_client() as client:
      client.post('/login', data={
        'username': 'test', 'password': 'bad'}, follow_redirects=True)
      self.assertFalse(current_user.is_authenticated)

  def test_sessions(self):
    """Tests the sessions endpoint."""
    with self.app.test_client() as client:
      response = client.get('/sessions')
      self.assertEqual(b'', response.data)
    with self.app.test_client() as client:
      client.post('/login', data={
        'username': 'test', 'password': 'test'}, follow_redirects=True)
    with self.app.test_client() as client:
      response = client.get('/sessions')
      self.assertEqual(b'test 127.0.0.1\n', response.data)
    with self.app.test_client() as client:
      client.post('/login', data={
        'username': 'foo', 'password': 'bar'}, follow_redirects=True)
    with self.app.test_client() as client:
      response = client.get('/sessions')
      self.assertEqual(b'test 127.0.0.1\nfoo 127.0.0.1\n', response.data)


if __name__ == '__main__':
  unittest.main()
