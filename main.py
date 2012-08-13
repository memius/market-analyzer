# coding: utf-8

import webapp2, cgi, urllib, jinja2, os, logging, itertools

from google.appengine.api import users
from google.appengine.ext import db
from apiclient.discovery import build

import utils, crawl, sites, fetch


logging.basicConfig(filename='main.log', filemode='w', level=logging.DEBUG)

service = build('prediction', 'v1.4', http=http)

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
        # company.name = "Apple"
        # company.ticker = "AAPL"
        # company.exchange = "NASDAQ"
        # company.put()

        companies = Company.all().ancestor(companies_key())
        #companies = companies.fetch(60)
        #db.delete(companies) #removes all entries from db


# #       adds articles to the db, relevant to 'companies'.
# #        articles = []
#         for company in companies:
#             links = sites.gf(company.ticker)
#             for link in links:
#                 if link is not "None":
#                     article = Article(parent = articles_key())  #must have an if not already exists here
#                     content = fetch.article(link) # list of strings
#                     text = ' '.join(content)
#                     text = text.decode('utf-8')
#                     text = unicode(text)
#                     # text = ""
#                     # for sentence in content:
#                     #     text = sentence + text # maybe + " " +
#                     article.content = text
#                     article.url = link
#                     article.companies.append(company.key())
#                     article.put()
# #                    articles.append(article.content)


        articles = Article.all().ancestor(articles_key())
        content = []
        for article in articles:
            text = article.url
            #recommendation = crm.classify(text) #this must be put to company.recommendation
            #content.append(recommendation)
            content.append(text)

        #db.delete(articles) #removes all entries from db

        template_values = {
            'user' : user,
            'url' : url,
            'url_linktext' : url_linktext,
            'companies' : companies,
            'articles': content
            }

        template = jinja_environment.get_template('index.html')
        self.response.out.write(template.render(template_values))

app = webapp2.WSGIApplication([('/', MainPage)], debug=True) #remove debug in production
