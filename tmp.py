# coding: utf-8

import urllib2,re

from bs4 import BeautifulSoup

def gf(ticker):
    url = "https://www.google.com/finance/company_news?q=NASDAQ:" + ticker + "&start=10&num=10"
    html = urllib2.urlopen(url).read()
    soup = BeautifulSoup(html)
    #div_id = re.compile("Article[0-9*]")
    #divs = soup.find_all("div", {"id" : div_id})
    div_class = re.compile("^g-section.*")
    divs = soup.find_all("div", {"class" : div_class})
    for div in divs:
        a = unicode(div.find('a', attrs={'href': re.compile("^http://")})) 
        link_regex = re.search("(http://.*?)\"",a)
        
        try:
            link = link_regex.group(1)

        except:
            link = "None"

        print 'the link: ',link





gf('aapl')









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
