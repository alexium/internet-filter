"""Database models for the portal."""
# pylint: disable=no-member
import click

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
