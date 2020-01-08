"""Database models for the portal."""
# pylint: disable=no-member
import time
from datetime import datetime

import click
from flask import request
from flask.cli import with_appcontext
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash

DB = SQLAlchemy()


class User(DB.Model, UserMixin):
  """Schema for the user table."""

  # default session duration is 5 mins
  SESSION_DURATION = 5 * 60

  id = DB.Column(DB.Integer, primary_key=True)
  username = DB.Column(DB.String(100), unique=True)
  password = DB.Column(DB.String(100))
  ip_addr = DB.Column(DB.String(100))
  session_expiration = DB.Column(DB.DateTime())

  def update_session(self):
    """Write session expiration and IP address to the DB."""
    self.ip_addr = request.remote_addr or \
      request.environ['HTTP_X_FORWARDED_FOR']
    self.session_expiration = datetime.fromtimestamp(
      time.time() + User.SESSION_DURATION)
    DB.session.commit()


def init_db():
  """Initialize the DB when using in test or dev environments."""
  DB.create_all()
  new_user1 = User(
    username='test', password=generate_password_hash('test', method='sha256'))
  DB.session.add(new_user1)
  new_user2 = User(
    username='foo', password=generate_password_hash('bar', method='sha256'))
  DB.session.add(new_user2)
  DB.session.commit()

@click.command('init-db')
@with_appcontext
def init_db_command():
  """Command line way to initialize the DB."""
  init_db()
  click.echo('Initialized the database.')
