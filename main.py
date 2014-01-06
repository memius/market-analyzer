# coding: utf-8

#only displays the finished products that scrape and bayesian have stored to db. and only at users' requests, NOT as cron jobs.

import jinja2, os, logging, pickle, webapp2, time, re

from bs4 import BeautifulSoup as bs
from google.appengine.api import users, urlfetch
from google.appengine.ext import db
from google.appengine.ext.webapp.util import login_required #must be webapp, not webapp2

import utils, crawl, sites, fetch, naive_bayes, scrape, duplicates, clean, analyze

from models import Article, Company, UserPrefs

# class UserPrefs(db.Model):
#     user_id = db.StringProperty()

logging.basicConfig(filename='logs/main.log', filemode='w', level=logging.DEBUG)

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class MainPage(webapp2.RequestHandler):

    def get(self): 
        #timeout = 0.2
        usr = users.get_current_user()
        if usr:
            user_id = usr.user_id()
            nickname = usr.nickname()
            email = usr.email()
            auth_url = users.create_logout_url(self.request.uri)
            auth_url_linktext = "Logout"
        else:
            user_id = "Empty user_id"
            nickname = "Empty nickname"
            email = "Empty email"
            auth_url = users.create_login_url(self.request.uri)
            auth_url_linktext = "Login"

        q = UserPrefs.all()
        q = q.filter("user_id =",user_id)
        try:
            [u] = q.fetch(1)
        except:
            u = UserPrefs()
            u.user_id = user_id
            u.nickname = nickname
            u.email = email
            u.put()

        # company = Company()
        # company.name = "Google Inc"
        # company.name_lower = "google inc"
        # company.ticker = "GOOG"
        # company.ticker_lower = "goog"
        # company.exchange = "NASDAQ"
        # company.put()
        # company = Company()
        # company.name = "Apple Inc"
        # company.name_lower = "apple inc"
        # company.ticker = "AAPL"
        # company.ticker_lower = "aapl"
        # company.exchange = "NASDAQ"
        # company.put()
        # company = Company()
        # company.name = "Facebook Inc"
        # company.name_lower = "facebook inc"
        # company.ticker = "FB"
        # company.ticker_lower = "fb"
        # company.exchange = "NASDAQ"
        # company.put()

        # u.companies = []
        # u.put()

        if u.companies == []:
            apple = Company.all().filter("name =","Apple Inc").get()
            u.companies.append(apple.key())
            google = Company.all().filter("name =","Google Inc").get()
            u.companies.append(google.key())
            facebook = Company.all().filter("name =","Facebook Inc").get()
            u.companies.append(facebook.key())
            u.put()

        company_names = []
        for company_key in u.companies:
            company = Company.get_by_id(company_key.id())
            # try: # in case there are zombie ids for that user:
            company_names.append(company.name)
            # except:
            #     continue

# #         # displaying all companies for debugging only:
        q = Company.all() #you'll need a 'more' button to display more than these 20
        companies = q.fetch(100) #fetch can't be async for now.

# #         ##############db.delete(companies) don't do this either!

# #         # you need a check here, to see what companies are already
# #         # user companies!
#         free_companies = ["Apple Inc", "Google Inc", "Facebook Inc"]

        # for company in companies:
        #     if company.ticker == "GE":
        #         # company.name = "International Business Machines Corp."
        #         # company.name_lower = "international business machines corp."
        #         # company.ticker = "IBM"
        #         # company.ticker_lower = "ibm"
        #         company.exchange = "NYSE"
        #         company.put()

#             if comp.name in free_companies and comp.key() not in u.companies:
#                 u.companies.append(comp.key())
# # #                comp.user = u #why can't this be usr? usr is a UserPrefs object, isn't it???? No, it's a in-built user object.


#                company.put()


#                 u.put()

#         q = article_objects = Article.all() # should be articles = company.articlestod
#         q = q.order("-datetime")
#         q = q.filter("clean =",True)
#         article_objects = q.fetch(100)
# #        article_objects = q # debug only
#         ####db.delete(article_objects) stop doing this - delete attributes instead, run scripts to add new attributes
        keys_names = zip(u.companies,company_names)

        template_values = {
            'keys_names' : keys_names,
            'companies' : companies, #debug only
            'user' : u,
            'auth_url' : auth_url,
            'auth_url_linktext' : auth_url_linktext,
            }

        template = jinja_environment.get_template('index.html')
        self.response.out.write(template.render(template_values))

class CompanyClickHandler(webapp2.RequestHandler):
    def get(self,company_id): # apparently, it must be company_id, not something else.
        # r = self.request
        # company = re.compile("company/(?P<company>.*?)HTTP")
        # company = re.search(company,unicode(r)).group("company")
        company = Company.get_by_id(int(company_id))
        articles = [article for article in company.articles if article.clean]
        # articles = [article for article in company.articles]
        [pos_rat,neg_rat] = utils.sentiment_count(articles)

        # for article in articles:
        #     article.analyzed = True
        #     article.put()

        # company.name = "Microsoft Corporation"
        # company.name_lower = "microsoft corporation"
        # company.ticker = "GE"
        # company.ticker_lower = "ge"
        # company.exchange = "NYSE"
        # company.put()
         
        template_values = {
            'id' : company_id,
            'pos_rat' : pos_rat,
            'neg_rat' : neg_rat,
            'name' : company.name,
            'exchange' : company.exchange,
            'articles' : articles,
            'tot_articles' : company.articles.count(),
            'num_of_articles' : len(articles) 
            }

        template = jinja_environment.get_template('company.html')
        self.response.out.write(template.render(template_values))

class ArticleClickHandler(webapp2.RequestHandler):
    def get(self,article_id): 
        article = Article.get_by_id(int(article_id))

        template_values = {
            'id' : article.key().id(),
            'sentiment' : article.sentiment,
            'title' : article.title,
            'text' : article.text
            }

        template = jinja_environment.get_template('article.html')
        self.response.out.write(template.render(template_values))


# you need some robustness here: the user can type inc, Inc, Inc., inc.,
# Incorporated, Corp, corp, etc. i need to be able to handle all of
# them. maybe normalize the input?
class FindCompanyHandler(webapp2.RequestHandler):
    def post(self):
        
        template_values = {}

        template = jinja_environment.get_template('find_company.html')
        self.response.out.write(template.render(template_values))
        
    def get(self): # get() identical to post() has to be here because of the redirect from /subscribe.
        
        template_values = {}

        template = jinja_environment.get_template('find_company.html')
        self.response.out.write(template.render(template_values))

class FoundCompanyHandler(webapp2.RequestHandler):
    def post(self):
        name_ticker = self.request.get('name_ticker')

        q = Company.all().filter("name_lower =",name_ticker.lower()) 
        company = q.get()
        if company != None:
            name = company.name
            exchange = company.exchange
            ticker = company.ticker
        
        if company == None:
            q = Company.all().filter("ticker_lower =",name_ticker.lower())
            company = q.get()
            if company != None:
                name = company.name
                exchange = company.exchange
                ticker = company.ticker

        if company == None:
            url = "https://www.google.com/finance?q=" + name_ticker + "&ei=uxJjUpDELYqrwAPHWA"

            result = urlfetch.fetch(url)
            if result.status_code == 200:
                soup = bs(result.content)

                title = soup.title.get_text()

                name = re.compile("(?P<name>.*?):")
                exchange = re.compile(": (?P<exchange>.*?):")
                ticker = re.compile(":.*?:(?P<ticker>.*?) quotes & news")

                exchange = re.search(exchange,title).group("exchange")
                name = re.search(name, title).group("name")
                ticker = re.search(ticker, title).group("ticker")

                # check here to see if what the user typed in actually gave a result on google finance.

                company = Company()
                company.name = name
                company.name_lower = name.lower()
                company.exchange = exchange.lower()
                company.ticker = ticker
                company.ticker_lower = ticker.lower()
                company.put()

        company_id = company.key().id() # use name instead of id - it's better for the api.
        template_values = {
            'name' : name,
            'id' : company_id,
            'exchange' : exchange,
            'ticker' : ticker
            }

        template = jinja_environment.get_template('found_company.html')
        self.response.out.write(template.render(template_values))


        # self.redirect("company/" + str(company_id))

            # else:
            #     pass #some error message, and redirect back to text input.

class SubscribeHandler(webapp2.RequestHandler):
     def post(self):
        response = self.request.get("response")
        company_id = self.request.get("key")
        if response == "Subscribe":
            company = Company.get_by_id(int(company_id)) # may need to be cast to int, or even str.
            
            user = users.get_current_user()
            user_id = user.user_id()
            q = UserPrefs.all()
            u = q.filter("user_id =",user_id).get()

            u.companies.append(company.key())
            u.put()
            # company.user = u
            # company.put()

            self.redirect("company/" + str(company_id))
            # later, we charge the user for this. (don't charge if the company is one of the free ones.)
        elif response == "Cancel":
            self.redirect("/find_company")
#            self.redirect("/subscribe")

class UnsubscribeHandler(webapp2.RequestHandler):
     def post(self):
        response = self.request.get("response")
        company_id = self.request.get("key")
        if response == "Unsubscribe":
            company = Company.get_by_id(int(company_id)) 
            
            user = users.get_current_user()
            user_id = user.user_id()
            q = UserPrefs.all()
            u = q.filter("user_id =",user_id).get()

            u.companies.remove(company.key())
            u.put()
            # company.user = None # change it to 'remove user from company.users'.
            # company.put()
            # and stop charging the user.

            self.redirect("/")

class CorrectionHandler(webapp2.RequestHandler):
    def post(self):
        self.response.write(
            'You clicked:%sEND for article:%sEND' % (self.request.get('sentiment'), self.request.get('key') )
            )
        article_object_key = self.request.get("key")
        article_object = Article.get_by_id(int(article_object_key)) #could be made async, i think.
        # article__key = db.Key('Article', self.request.get('id'))
        self.response.write(" article object: %s END article object" % str(article_object))
        # self.response.write(article_object.content)
        s = self.request.get('sentiment')
        article_object.sentiment = str(s) # must be str, not unicode
        article_object.title_sentiment = str(s) 
        
        if s == "positive":
            article_object.mod = 0.9
        if s == "negative":
            article_object.mod = -0.9

        article_object.put()
        self.redirect("article/" + str(article_object_key))

class ScrapeHandler(webapp2.RequestHandler):
    def get(self):
        scrape.scrape()
        # self.response.write(c)
        self.response.write('you have scraped some articles')
        # self.redirect("/")

class DuplicateHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('you have removed duplicates')
        duplicates.companies()
        duplicates.articles()

class CleanHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('you have cleaned some text')
        clean.clean()

class CleanOldHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('you have cleaned some old articles')
        clean.clean_old_articles()

class AnalyzeHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write("you have analyzed all articles")
        analyze.all_sentiment()

class AnalyzeOldHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write("you have analyzed old articles")
        analyze.all_sentiment_old_articles()

class CheckHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write("checked")
        ctrs = utils.check()

        template_values = {
            'ctrs' : ctrs,
            }

        template = jinja_environment.get_template('check.html')
        self.response.out.write(template.render(template_values))

app = webapp2.WSGIApplication([
#        ('/auth_return', AuthHandler),
        ('/correction', CorrectionHandler),
        ('/company/(.*)', CompanyClickHandler),
        ('/article/(.*)', ArticleClickHandler),
        ('/find_company',FindCompanyHandler),
        ('/found_company',FoundCompanyHandler),
        ('/subscribe', SubscribeHandler),
        ('/unsubscribe', UnsubscribeHandler),
        ('/scrape', ScrapeHandler),
        ('/dupes', DuplicateHandler),
        ('/clean', CleanHandler),
        ('/clean_old_articles', CleanOldHandler),
        ('/analyze', AnalyzeHandler),
        ('/analyze_old_articles', AnalyzeOldHandler),
        ('/check', CheckHandler),
        ('/.*', MainPage),
        ], debug=True) #remove debug in production

