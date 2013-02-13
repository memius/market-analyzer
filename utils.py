from google.appengine.api import users
from google.appengine.ext import db

import re

class UserPrefs(db.Model):
    user_id = db.StringProperty()


def remove_duplicates(lst):
    non_duplicate_lst = []
    for elt in lst:
        if elt not in non_duplicate_lst and elt is not "None":
            non_duplicate_lst.append(elt)
    
    return non_duplicate_lst

#checks if the article contains natural language and actual semantic content, or just syntactic invocations:
def is_article(text):
    if text is "None" or text is "":
        return False

    # the most common non-personal bigrams:
    #non-prescence of these indicates a non-article.
    bigrams = ["in the","of the","to the","to be","all the","it is",\
                   "of a","and the","in a","with a","such a","with the",\
                   "is a","will not","is the","this is","by the","out of",\
                   "no more","for a"]
    ctr = 0
    for bigram in bigrams:
        if re.search(bigram,text):
            #print bigram
            ctr = ctr + 1
            #print "ctr in loop: ",ctr

    #print "ctr outside loop: ",ctr
    if ctr > 1:
        return True
    else:
        return False
    
