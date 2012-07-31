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



import webapp2, cgi, urllib, jinja2, os

from google.appengine.api import users
from google.appengine.ext import db

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))


class Article(db.Model):
    content = db.StringProperty(multiline=True)
    datetime = db.DateTimeProperty()
    companies = db.ListProperty(db.Key) #the companies for which the article is relevant

#parent
class Company(db.Model):
    name = db.StringProperty() #show this in the web app
    ticker = db.StringProperty() #show only this in the android app
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


class MainPage(webapp2.RequestHandler):
    def get(self): #handles get requests from the intarwebs
        user = users.get_current_user()
        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = "Logout"
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = "Login"

        #companies_name = self.request.get('companies_name') from tutorial
        companies_name="sinsen" #debugging only
        companies_ticker = "arb"
        

        # company = Company(parent = companies_key('statoil'))
        # company.name = "statoil"
        # company.ticker = "stl"
        # company.put()

        #printing the companies: (some duplicated definitions here:)
        
        #fetching from db. returns empty
        # several_companies = db.GqlQuery("SELECT * "
        #                         "FROM Company "
        #                         "WHERE ANCESTOR IS :1 "
        #                         "ORDER BY date DESC LIMIT 10",
        #                         companies_key(companies_name)) #try to get entire list of companies rather than one

        # several_companies = Company.gql("WHERE ANCESTOR IS :1 LIMIT 10",
        #                      companies_key(companies_name))
        # self.response.out.write('several comps: %s' % several_companies)

        companies_query = Company.all().ancestor(
            companies_key(companies_name))
        companies = companies_query.fetch(2)


        # for one_company in several_companies:
        #     #one_company.ticker = 'stl'
        #     self.response.out.write('starting')
        #     if one_company.ticker:
        #         self.response.out.write(
        #             '<b>%s</b> ticker:' % one_company.ticker)
        #     else:
        #         self.response.out.write('name:')
        #         self.response.out.write('<blockquote>%s</blockquote>' %
        #                                 cgi.escape(one_company.name))
        #     self.response.out.write('ending')



      #   self.response.out.write("""
      #       %s, %s
      #   </body>
      # </html>""" % (companies_ticker,companies_name))

        template_values = {
            'companies' : companies,
            'url' : url,
            'url_linktext' : url_linktext,
            }

        template = jinja_environment.get_template('index.html')
        self.response.out.write(template.render(template_values))

class Companies(webapp2.RequestHandler):
  def post(self):
      #some comment on this line
      #companies_name = self.request.get('companies_name') from tutorial
      companies_name = "apple" #debugging only
      one_company = Company(parent=companies_key(companies_name))
      one_company.ticker = "msft" #debugging only
      #one_company.ticker = self.request.get('ticker')
      one_company.name = "Microsoft"
      #one_company.name = self.request.get('name')

      one_company.put()
      self.redirect('/?' + urllib.urlencode({'companies_name': companies_name}))


app = webapp2.WSGIApplication([('/', MainPage),
                               ('/comp', Companies)], debug=True) #remove debug in production
