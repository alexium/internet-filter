import time

from datetime import datetime
from flask import Blueprint
from flask import render_template
from flask import request
from flask_login import login_required
from flask_login import current_user
from .database import db
from .models import User


main = Blueprint('main', __name__)

@main.route('/')
def index():
  if current_user.is_authenticated:
    current_user.ip_addr = request.remote_addr
    current_user.session_expiration = datetime.fromtimestamp(time.time() + User.session_duration)
    db.session.commit()
    return render_template('index.html', user=current_user)
  else:
    return render_template('index.html')

@main.route('/sessions')
def sessions():
  users = User.query.filter(User.session_expiration > datetime.now()).all()
  output = ""
  for user in users:
    output += '%s %s\n' % (user.username, user.ip_addr)
  return output
