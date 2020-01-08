"""Auth-related endpoints for the portal service."""
# pylint: disable=no-member
import logging
import os
import subprocess
import time

from datetime import datetime
from flask import current_app
from flask import Blueprint
from flask import flash
from flask import redirect
from flask import request
from flask import url_for
from flask_login import current_user
from flask_login import login_user
from flask_login import logout_user
from flask_login import login_required
from werkzeug.security import check_password_hash
from .database import DB
from .database import User

AUTH = Blueprint('auth', __name__)
logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
LOG = logging.getLogger(__name__)

@AUTH.route('/logout')
@login_required
def logout():
  """Logout a user."""
  LOG.info('Logging out for %s', current_user.username)
  current_user.ip_addr = ''
  current_user.session_expiration = datetime.fromtimestamp(time.time() - 10)
  DB.session.commit()
  error_msg = update_router_config()
  if error_msg:
    flash('Error configuring router: ' + error_msg)
  logout_user()
  return redirect(url_for('main.index'))

@AUTH.route('/login', methods=['POST'])
def login_post():
  """Handle the login form."""
  username = request.form.get('username')
  password = request.form.get('password')
  remember = request.form.get('remember')
  user = User.query.filter_by(username=username).first()
  if user and check_password_hash(user.password, password):
    LOG.info('Login for %s', username)
    login_user(user, remember=remember)
    current_user.update_session()
    error_msg = update_router_config()
    if error_msg:
      flash('Error configuring router: ' + error_msg)
  else:
    flash('Please check your login details and try again.')
  return redirect(url_for('main.index'))

def update_router_config():
  """Run command to update the router configuration.

    Returns:
      None if update succeeded or error string if update failed.
    """
  cmd = ['ssh', '%s@%s' % (current_app.config['ROUTER_USER'],
                           current_app.config['ROUTER_IP']),
         'export FLASK_ENV=%s; %s' % (current_app.config['ENV'],
                                      current_app.config['ROUTER_CMD'])]
  try:
    LOG.debug('Running EdgeRouter script')
    proc = subprocess.run(cmd, capture_output=True, check=True)
    if proc.stdout or proc.stderr:
      error_msg = proc.stdout + b' ' + proc.stderr
      LOG.error(error_msg.decode('utf-8'))
      return error_msg.decode('utf-8')
  except subprocess.CalledProcessError as err:
    LOG.exception(err)
    return str(err)
  return None
