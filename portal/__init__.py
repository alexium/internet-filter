"""Create the flask app for the portal."""
import logging
import os

from flask import Flask
from flask_login import LoginManager

logging.basicConfig(level=os.environ.get('LOGLEVEL', 'INFO'))
LOG = logging.getLogger(__name__)

def create_app(test_config=None):
  """Create the flask app for the portal."""
  app = Flask(__name__, instance_relative_config=True)
  _load_config(app, test_config)
  _register_blueprints(app)
  from .database import DB
  DB.init_app(app)
  from .database import init_db_command
  app.cli.add_command(init_db_command)
  _setup_login_manager(app)
  return app

def _setup_login_manager(app):
  login_manager = LoginManager()
  from .database import User
  @login_manager.user_loader
  def load_user(user_id): # pylint: disable=unused-variable
    return User.query.get(int(user_id))
  login_manager.login_view = 'auth.login'
  login_manager.init_app(app)

def _register_blueprints(app):
  from .auth import AUTH as auth_blueprint
  app.register_blueprint(auth_blueprint)
  from .main import MAIN as main_blueprint
  app.register_blueprint(main_blueprint)

def _load_config(app, test_config):
  db_uri = 'sqlite:///' + os.path.join(app.instance_path, 'dev.db')
  app.config.from_mapping(
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    SQLALCHEMY_DATABASE_URI=db_uri,
    SECRET_KEY='dev',
    ROUTER_USER='ubnt',
    ROUTER_IP='192.168.3.1',
    ROUTER_CMD='/config/scripts/edgerouter.sh'
  )
  if test_config:
    app.config.from_mapping(test_config)
  elif app.config['ENV'] == 'production':
    LOG.info('Using production config')
    app.config.from_pyfile('prod.cfg', silent=True)
  try:
    os.makedirs(app.instance_path)
  except OSError:
    pass
