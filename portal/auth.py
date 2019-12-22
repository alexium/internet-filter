import time

from datetime import datetime
from flask import Blueprint
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_login import current_user
from flask_login import login_user
from flask_login import logout_user
from flask_login import login_required
from werkzeug.security import check_password_hash
from .database import db
from .models import User

auth = Blueprint('auth', __name__)


@auth.route('/logout')
@login_required
def logout():
  current_user.ip_addr = ''
  current_user.session_expiration = datetime.fromtimestamp(time.time() - 10)
  db.session.commit()
  logout_user()
  return redirect(url_for('main.index'))

@auth.route('/login', methods=['POST'])
def login_post():
  username = request.form.get('username')
  password = request.form.get('password')
  remember = True if request.form.get('remember') else False
  user = User.query.filter_by(username=username).first()

  if not user or not check_password_hash(user.password, password): 
    flash('Please check your login details and try again.')
    return redirect(url_for('main.index'))

  # login successful
  login_user(user, remember=remember)
  return redirect(url_for('main.index'))
