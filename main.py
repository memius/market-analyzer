#from google.appengine.api import urlfetch
#import string

#btw: the u' in front means the string is unicode.



# import logging

# import fetch, crawl

# logging.basicConfig(filename='main.log', filemode='w', level=logging.DEBUG)

# print '' #needed to get anything printed on screen




# #debugging only:
# urls = crawl.links("http://news.google.com")

# logging.debug('urls: %s END urls',urls)

# # for url in urls:
# # #    url = unicode(url,'utf-8',errors='replace')
# # #    url = url.encode('utf-8')
# #     print ''
# #     print url

# # #debugging only:
# # urls = [urls[11],urls[12]]
# # print 'urls[0]: ',urls[0]

# for url in urls:
# #     #print 'link: ', link
# #     #url = link['href']
#     try:
#         doc_title, keywords, title, img_txt, intro, text = fetch.article(url)
#         print 'doc_title: ', doc_title
#         print 'keywords: ', keywords
#         print 'title: ', title
#         print 'img_txt: ', img_txt
#         print 'intro: ', intro
#         print 'text: ', text
#     except:
#         print 'no content'



# for aa kunne bruke python 2.7:



import webapp2, cgi, urllib, jinja2, os, logging, itertools

from google.appengine.api import users
from google.appengine.ext import db

import utils, crawl, sites, fetch

logging.basicConfig(filename='main.log', filemode='w', level=logging.DEBUG)

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))


# grandparent
# class User(db.Model): avoid this - grandparents costs a lot of writes to the db.
#     nick = db.StringProperty()
#     companies = 

class Article(db.Model):
    content = db.TextProperty()
    datetime = db.DateTimeProperty(auto_now_add=True)
    companies = db.ListProperty(db.Key) #the companies for which the article is relevant
    url = db.StringProperty()

#parent
class Company(db.Model):
    name = db.StringProperty() #show this in the web app
    ticker = db.StringProperty() #show only this in the android app
    exchange = db.StringProperty()
    price = db.FloatProperty()
    movement = db.BooleanProperty()  #whether it went up or down since yesterday. if no value -> no movement.
    articles = db.ReferenceProperty(Article) #not needed: do this: articles = company.article_set.get()
    recommendation = db.StringProperty() #'buy', 'hold' or 'sell'
    confidence = db.FloatProperty() #a number from 0.0 to 1.0

    @property
    def articles(self):
        return Article.gql("WHERE companies = :1", self.key()) #the articles that are relevant for the company

def companies_key(companies_name=None):
  """Constructs a Datastore key for a Companies entity with companies_name."""
  return db.Key.from_path('Companies', companies_name or 'default_companies')

def articles_key(articles_name=None):
  return db.Key.from_path('Articles', articles_name or 'default_articles')




class MainPage(webapp2.RequestHandler):
    def get(self): #handles get requests from the intarwebs
        user = users.get_current_user()
        if user:
            query = db.GqlQuery("SELECT * FROM UserPrefs WHERE userid = :1", user.user_id())
            user_id = query.get() #not used for now. used for filtering which companies to show, etc.
            url = users.create_logout_url(self.request.uri)
            url_linktext = "Logout"
        else:
            user_id = "None" 
            url = users.create_login_url(self.request.uri)
            url_linktext = "Login"

        # stores one company to the db:
        # company = Company(parent=companies_key())
        # company.name = "Samsung"
        # company.ticker = "005930"
        # company.exchange = "KRX"
        # company.put()

        companies = Company.all().ancestor(companies_key())
        #companies = companies.fetch(60)
        #db.delete(companies) #removes all entries from db


# #        articles = []
#         for company in companies:
#             links = sites.gf(company.ticker)
#             for link in links:
#                 if link is not "None":
#                     article = Article(parent = articles_key())  #must have an if not already exists here
#                     content = fetch.article(link) # list of strings
#                     text = ' '.join(content)
#                     # text = ""
#                     # for sentence in content:
#                     #     text = sentence + text # maybe + " " +
#                     article.content = text
#                     article.url = link
#                     article.companies.append(company.key())
#                     article.put()

# #                    articles.append(article.content)

        articles = Article.all().ancestor(companies_key())

        template_values = {
            'user' : user,
            'url' : url,
            'url_linktext' : url_linktext,
            'companies' : companies,
            'articles': articles
            }

        template = jinja_environment.get_template('index.html')
        self.response.out.write(template.render(template_values))

app = webapp2.WSGIApplication([('/', MainPage)], debug=True) #remove debug in production
