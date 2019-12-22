"""Initializes the development database.

See https://flask.palletsprojects.com/en/1.1.x/tutorial/database/"""
import click

from flask_sqlalchemy import SQLAlchemy
from flask.cli import with_appcontext
from werkzeug.security import generate_password_hash


db = SQLAlchemy()

def init_db():
  db.create_all()
  from .models import User
  new_user = User(
    username='test', password=generate_password_hash('test', method='sha256'))
  db.session.add(new_user)
  db.session.commit()

@click.command('init-db')
@with_appcontext
def init_db_command():
    init_db()
    click.echo('Initialized the database.')
