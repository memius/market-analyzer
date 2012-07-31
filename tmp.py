import urllib2,re

from bs4 import BeautifulSoup

def gf():
    ticker = 'aapl'
    url = "https://www.google.com/finance/company_news?q=NASDAQ:" + ticker + "&start=10&num=10"
    html = urllib2.urlopen(url).read()
    soup = BeautifulSoup(html)
    div_id = re.compile("Article[0-9*]")
    divs = soup.find_all("div", {"id" : div_id})
    for div in divs:
        a = unicode(div.find('a', attrs={'href': re.compile("^http://")})) #matches first line starting with http://
        result = re.search("(http://.*?)\"",a)
        
        try:
            link = result.group(1)
            print 'the link: ',link
        except:
            link = "None"


the href i want, which corresponds to the title of each news item, is somehow above the 'article1' tag, or something like that.


gf()









# class MainPage(webapp2.RequestHandler):
#     def get(self):
#         guestbook_name=self.request.get('guestbook_name')
#         greetings_query = Greeting.all().ancestor(
#             guestbook_key(guestbook_name)).order('-date')
#         greetings = greetings_query.fetch(10)

#         if users.get_current_user():
#             url = users.create_logout_url(self.request.uri)
#             url_linktext = 'Logout'
#         else:
#             url = users.create_login_url(self.request.uri)
#             url_linktext = 'Login'

#         template_values = {
#             'greetings': greetings,
#             'url': url,
#             'url_linktext': url_linktext,
#         }

#         template = jinja_environment.get_template('index.html')
#         self.response.out.write(template.render(template_values))
