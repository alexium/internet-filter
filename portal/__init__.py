import os

from flask import Flask
from flask_login import LoginManager

def create_app(test_config=None):
  app = Flask(__name__, instance_relative_config=True)
  load_config(app, test_config)
  register_blueprints(app)
  from .database import db
  db.init_app(app)
  from .database import init_db_command
  app.cli.add_command(init_db_command)
  setup_login_manager(app)
  return app

def setup_login_manager(app):
  login_manager = LoginManager()
  from .models import User
  @login_manager.user_loader
  def load_user(user_id):
    return User.query.get(int(user_id))
  login_manager.login_view = 'auth.login'
  login_manager.init_app(app)
  
def register_blueprints(app):
  from .auth import auth as auth_blueprint
  app.register_blueprint(auth_blueprint)
  from .main import main as main_blueprint
  app.register_blueprint(main_blueprint)

def load_config(app, test_config):
  app.config.from_mapping(
    SQLALCHEMY_TRACK_MODIFICATIONS = False,
    SQLALCHEMY_DATABASE_URI = 'sqlite:///dev.db',
    SECRET_KEY = 'dev')
  if test_config:
    app.config.from_mapping(test_config)
  if app.config['ENV'] == 'production':
    app.config.from_pyfile('prod.cfg', silent=True)
  try:
    os.makedirs(app.instance_path)
  except OSError:
    pass
