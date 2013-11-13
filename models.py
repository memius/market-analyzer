# coding: utf-8


from google.appengine.api import users
from google.appengine.ext import db

class Counter(db.Model):
    ctr = db.IntegerProperty()

class Token(db.Model):
    word = db.StringProperty()
    prob = db.FloatProperty()
    pos_freq = db.IntegerProperty()
    neg_freq = db.IntegerProperty()

class UserPrefs(db.Model):
    user_id = db.StringProperty()
    nickname = db.StringProperty()
    email = db.StringProperty()
    companies = db.ListProperty(db.Key)
    # obj = db.UserProperty()
    # name = db.StringProperty()
    # companies is an implied property - see Company class.

class Company(db.Model):
    name = db.StringProperty() #show this in the web app
    name_lower = db.StringProperty() 
    ticker = db.StringProperty() #show only this in the android app
    ticker_lower = db.StringProperty() 
    exchange = db.StringProperty()
    datetime = db.DateTimeProperty(auto_now_add=True)
    price = db.FloatProperty()
    movement = db.BooleanProperty()  #whether it went up or down since yesterday. if no value -> no movement.
#    articles = db.ReferenceProperty(Article) #not needed: do this: articles = company.articles.get()
    titles = db.StringListProperty()
    finished_scraping = db.BooleanProperty(False)
#    user = db.ReferenceProperty(UserPrefs, collection_name = "companies")
#    recommendation = db.StringProperty() #'buy', 'hold' or 'sell'
#    confidence = db.FloatProperty() #a number from 0.0 to 1.0
#    user = db.ReferenceProperty(User, collection_name = "companies")

    @property
    def user(self):
        return UserPrefs.gql("WHERE companies = :1", self.key()) 

class Article(db.Model):
    title = db.StringProperty()
#    soup = db.BlobProperty()
    html = db.TextProperty()
    text = db.TextProperty()
    datetime = db.DateTimeProperty(auto_now_add=True)
#    companies = db.ListProperty(db.Key) #the companies for which the article is relevant
    url = db.StringProperty()
    sentiment = db.ByteStringProperty() #negative, positive, neutral
    title_sentiment = db.ByteStringProperty() # why is this not simply a stringproperty?
    prob = db.FloatProperty()
    title_prob = db.FloatProperty()
    mod = db.FloatProperty() # modification to next probability calculation
#    normalized = db.TextProperty()
    clean = db.BooleanProperty(False) 
    analyzed = db.BooleanProperty(False) 
    company = db.ReferenceProperty(Company, collection_name = "articles")

def tokens_key(tokens_name=None):
  return db.Key.from_path('Tokens', tokens_name or 'default_tokens')

def companies_key(companies_name=None):
  """Constructs a Datastore key for a Companies entity with companies_name."""
  return db.Key.from_path('Companies', companies_name or 'default_companies')

def articles_key(articles_name=None):
  return db.Key.from_path('Articles', articles_name or 'default_articles')
