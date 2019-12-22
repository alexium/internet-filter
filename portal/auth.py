"""Auth-related endpoints for the portal service."""
# pylint: disable=no-member
import time

from datetime import datetime
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


@AUTH.route('/logout')
@login_required
def logout():
  """Logout a user."""
  current_user.ip_addr = ''
  current_user.session_expiration = datetime.fromtimestamp(time.time() - 10)
  DB.session.commit()
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
    # login successful
    login_user(user, remember=remember)
  else:
    flash('Please check your login details and try again.')
  return redirect(url_for('main.index'))
