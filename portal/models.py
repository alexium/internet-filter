from flask_login import UserMixin
from .database import db


class User(db.Model, UserMixin):
  # default session duration is 5 mins
  session_duration = 5 * 60

  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(100), unique=True)
  password = db.Column(db.String(100))
  ip_addr = db.Column(db.String(100))
  session_expiration = db.Column(db.DateTime())
