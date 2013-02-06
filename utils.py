from google.appengine.api import users
from google.appengine.ext import db

class UserPrefs(db.Model):
    user_id = db.StringProperty()


def remove_duplicates(lst):
    non_duplicate_lst = []
    for elt in lst:
        if elt not in non_duplicate_lst and elt is not "None":
            non_duplicate_lst.append(elt)
    
    return non_duplicate_lst
