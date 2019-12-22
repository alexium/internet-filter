"""Endpoints for non-auth stuff."""
# pylint: disable=no-member
import time

from datetime import datetime
from flask import Blueprint
from flask import render_template
from flask import Response
from flask import request
from flask_login import current_user
from .database import DB
from .database import User


MAIN = Blueprint('main', __name__)

@MAIN.route('/')
def index():
  """Home page for the portal."""
  if current_user.is_authenticated:
    current_user.ip_addr = request.remote_addr
    current_user.session_expiration = datetime.fromtimestamp(
      time.time() + User.SESSION_DURATION)
    DB.session.commit()
    return render_template('index.html', user=current_user)
  return render_template('index.html')

@MAIN.route('/sessions')
def sessions():
  """Show users with current sessions."""
  users = User.query.filter(User.session_expiration > datetime.now()).all()
  output = ""
  for user in users:
    output += '%s %s\n' % (user.username, user.ip_addr)
  return Response(output, 'text/plain')
