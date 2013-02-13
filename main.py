# coding: utf-8

import cgi, urllib, jinja2, os, logging, itertools, pickle, webapp2, httplib2

from google.appengine.api import users
from google.appengine.api import memcache
from google.appengine.ext import db
#from google.appengine.ext import webapp2 see above
from apiclient.discovery import build
from google.appengine.ext.webapp.util import login_required #must be webapp, not webapp2
from oauth2client.appengine import StorageByKeyName
from oauth2client.appengine import CredentialsModel
from oauth2client.client import OAuth2WebServerFlow

import utils, crawl, sites, fetch

SCOPE = ('https://www.googleapis.com/auth/devstorage.read_write ' +
         'https://www.googleapis.com/auth/prediction')
USER_AGENT = 'try-prediction/1.0' #shouldn't it be 1.4?
#SECRETS_FILE = 'json/client_secrets.json'
ID_FILE = 'static/txt/id.txt'
SECRETS_FILE = 'static/txt/secret.txt'
DEFAULT_MODEL = 'Language Detection'

logging.basicConfig(filename='logs/main.log', filemode='w', level=logging.DEBUG)

#service = build('prediction', 'v1.4', http=http)

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))


# grandparent
# class User(db.Model): avoid this - grandparents costs a lot of writes to the db.
#     nick = db.StringProperty()
#     companies = 

class Article(db.Model):
    #content = db.TextProperty()
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
    def get(self): 
        user = users.get_current_user()
        if user:
            query = db.GqlQuery("SELECT * FROM UserPrefs WHERE userid = :1", user.user_id())
            user_id = query.get() #not used for now. used for filtering which companies to show, etc.
            auth_url = users.create_logout_url(self.request.uri)
            auth_url_linktext = "Logout"
        else:
            user_id = "None" 
            auth_url = users.create_login_url(self.request.uri)
            auth_url_linktext = "Login"

        # # stores one company to the db:
        # company = Company(parent=companies_key())
        # company.name = "Microsoft"
        # company.ticker = "MSFT"
        # company.exchange = "NASDAQ"
        # company.put()

        companies = Company.all().ancestor(companies_key())
        #companies = companies.fetch(60)
        #db.delete(companies) #removes all entries from db

# #       adds articles to the db, relevant to 'companies'.
# #        particles = []
#         for company in companies:
#             links = sites.gf(company.ticker)
#             links =  utils.remove_duplicates(links)
#             for link in links:
#                 if link is not "None":
#                     logging.debug('type(link): %s END type(link)', type(link))
#                     article = Article(parent = articles_key())  #must have an if not already exists here

#                     text = fetch.article(link) # should return one long unicode string. does it?
# #                    particles.append(text) #NOT needed (articles is fetched from db just below)
#                     logging.debug('type(text): %s END type(text)', type(text))

#                     #text = text.encode('utf-8')
#                     #text = unicode(text)
#                     #text = link
#                     #text = str(text)
#                     # for sentence in content:
#                     #     text = sentence + text # maybe + " " +
#                     article.content = text
#                     article.url = link
#                     article.companies.append(company.key())
#                     article.put()

        articles = Article.all().ancestor(articles_key())
        texts = []
        for article in articles:
#            text = article
            text = article.content #url
            #recommendation = crm.classify(text) #this must be put to company.recommendation
            #content.append(recommendation)
            texts.append(text)
#           texts.append(article)

##        db.delete(articles) #removes all article entries from db

        template_values = {
            'user' : user,
            'auth_url' : auth_url,
            'auth_url_linktext' : auth_url_linktext,
            'companies' : companies,
            'articles': texts
            }

        template = jinja_environment.get_template('index.html')
        self.response.out.write(template.render(template_values))

# definert på api console, og kan tilsynelatende ikke endres (burde være localhost:8080):
# redirect url:
# urn:ietf:wg:oauth:2.0:oob
# http://localhost

        try:
            # Read server-side OAuth 2.0 credentials from datastore and
            # raise an exception if credentials not found.
      
            credentials = StorageByKeyName(CredentialsModel, USER_AGENT, 
                                           'credentials').locked_get()
            if not credentials or credentials.invalid:
                # if not user:
                #     self.redirect("/reset") redirects to Reset class
                
                #raise Exception('missing OAuth 2.0 credentials')
#                secrets = parse_json_file(SECRETS_FILE)
                client_id = open(ID_FILE, 'r').read().strip()
                client_secret = open(SECRETS_FILE, 'r').read().strip()

#                client_id = secrets['installed']['client_id']
#                client_secret = secrets['installed']['client_secret']

                flow = OAuth2WebServerFlow(client_id=client_id,
                                           client_secret=client_secret,
                                           scope=SCOPE,
                                           user_agent=USER_AGENT,
                                           access_type = 'offline',
                                           approval_prompt='force')
                callback = self.request.relative_url('/auth_return') #redirects to AuthHandler class
                authorize_url = flow.step1_get_authorize_url(callback)
                # Save flow object in memcache for later retrieval on OAuth callback,
                # and redirect this session to Google's OAuth 2.0 authorization site.
                logging.info('saving flow for user ' + user.user_id())
                memcache.set(user.user_id(), pickle.dumps(flow))
                self.redirect(authorize_url)


            # Authorize HTTP session with server credentials and obtain  
            # access to prediction API client library.
            http = credentials.authorize(httplib2.Http())
            service = build('prediction', 'v1.4', http=http)
            papi = service.trainedmodels()
    
            # Read and parse JSON model description data.
            #models = parse_json_file(MODELS_FILE)

            # Get reference to user's selected model.
            #model_name = self.request.get('model')
            #model = 'Language Detection'
            model = 'languages'

            # # Build prediction data (csvInstance) dynamically based on form input.
            # vals = []
            # for field in model['fields']:
            #     label = field['label']
            # val = str(self.request.get(label))
            # vals.append(val)
            # body = {'input' : {'csvInstance' : vals }}
            # logging.info('model:' + model_name + ' body:' + str(body))
            vals = ['these','are','some','words','that','i','have','said']

            # Make a prediction and return JSON results to Javascript client.
            ret = papi.predict(id=model, body=vals).execute()
            self.response.out.write("yabbadabbadoo")
            self.response.out.write(json.dumps(ret))

        except Exception, err:
            # Capture any API errors here and pass response from API back to
            # Javascript client embedded in a special error indication tag.
            err_str = str(err)
            # if err_str[0:len(ERR_TAG)] != ERR_TAG:
            #     err_str = ERR_TAG + err_str + ERR_END
            self.response.out.write(err_str)



class AuthHandler(webapp2.RequestHandler):
  '''This class fields OAuth 2.0 web callback for the "Try Prediction" app.'''

  @login_required
  def get(self):
    user = users.get_current_user()

    # Retrieve flow object from memcache.
    logging.info('retrieving flow for user ' + user.user_id())
    flow = pickle.loads(memcache.get(user.user_id()))
    if flow:
      # Extract newly acquired server credentials, store creds
      # in datatore for future retrieval and redirect session
      # back to app's main page.
      credentials = flow.step2_exchange(self.request.params)
      StorageByKeyName(CredentialsModel, USER_AGENT,
                       'credentials').locked_put(credentials)
      self.redirect('/')
    else:
      raise('unable to obtain OAuth 2.0 credentials')

class Reset(webapp2.RequestHandler):
  '''This class processes requests to reset the server's OAuth 2.0 
     credentials. It should only be executed by the application
     administrator per the app.yaml configuration file.'''

  @login_required
  def get(self):
    # Store empty credentials in the datastore and redirect to main page.
    StorageByKeyName(CredentialsModel, USER_AGENT,
                     'credentials').locked_put(None)
    self.redirect('/')


app = webapp2.WSGIApplication([
        ('/', MainPage),
        ('/auth_return', AuthHandler),
        ], debug=True) #remove debug in production

