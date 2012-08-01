from google.appengine.api import users
from google.appengine.ext import db

class UserPrefs(db.Model):
    user_id = db.StringProperty()

