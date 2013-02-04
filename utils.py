from google.appengine.api import users
from google.appengine.ext import db

class UserPrefs(db.Model):
    user_id = db.StringProperty()

















# taken from histopy project on github:

# usage:     
#for n in soup.html.body.findAll('ul')[n]:
#    s = remove_html_tags(str(n))     
def remove_html_tags(html):
    p = re.compile(r'<[^<]*?/?>')
    return p.sub('', html)

opener = urllib2.build_opener()
opener.addheaders = [('User-agent', 'Mozilla/5.0')]
def load_page():
    html = opener.open('http://en.wikipedia.org/wiki/').read()
    soup = BSoup(html)
    return soup
