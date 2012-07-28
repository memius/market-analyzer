#etter at du har faatt dette til aa virke begynner du aa bruke scrapy, som virker robust og lett aa bruke, men litt mer verbose enn dette her:


#ose_news() kan salvages til en slags crawler som foelger alle hrefs paa et domene:

#-you have a short, editable dict that contains the sites you want to crawl (db.no, vg.no, etc.).
#-you deliver one of these at a time to the crawler, and the crawler crawls that domain, following all non-followed links.
#-thus, you need a db of followed links, so you can check every link against that, and not follow it if it's in the db.
#-you also need a db of links to follow, which is generated and used by the crawler.
#-the crawler also generates a db of leafs to return to fetch.
from bs4 import BeautifulSoup

import re, logging, urllib2

import papers

from replace_characters import replace_characters

logging.basicConfig(filename='crawl.log', filemode='w', level=logging.DEBUG)

def sites():
    all_urls = []
    for url in papers.names.values():
        logging.debug('trying url: %s', url)
        urls = links(url) #use deferred here, i think.
        all_urls.extend(urls) #puts urls in all_urls
        #store returned links to db
        logging.info('added leaf urls to db')

    return all_urls

def links(url):

    followed = [] #this needs to be a persistent db, to be used next time you crawl.
    urls = [] #regenerated each time.

    html = urllib2.urlopen(url).read()
    soup = BeautifulSoup(html)

    #follows all the links (soup('a')) on the front page once.
    links = soup.findAll('a', attrs={'href': re.compile("^http://")})
    for link in links:
        url = link['href']
#        url = replace_characters(url) causes error
        url = url.encode('utf-8')
#        url = url.replace()
        urls.append(url)

    return urls


# stuff from weekend codes:
# # Open some site, let's pick a random one, the first that pops in mind:
# r = br.open('http://google.com')
# html = r.read()

# # Show the source
# print html
# # or
# print br.response().read()

# # Show the html title
# print br.title()

# # Show the response headers
# print r.info()
# # or
# print br.response().info()

# # Show the available forms
# for f in br.forms():
#     print f

# # Select the first (index zero) form
# br.select_form(nr=0)

# # Let's search
# br.form['q']='weekend codes'
# br.submit()
# print br.response().read()

# # Looking at some results in link format
# for l in br.links(url_regex='stockrt'):
#     print l

# # Testing presence of link (if the link is not found you would have to
# # handle a LinkNotFoundError exception)
# br.find_link(text='Weekend codes')

# # Actually clicking the link
# req = br.click_link(text='Weekend codes')
# br.open(req)
# print br.response().read()
# print br.geturl()

# # Back
# br.back()
# print br.response().read()
# print br.geturl()


# page = urllib2.urlopen("http://www.linkpages.com")
# soup = BeautifulSoup(page)
# for link in soup.findAll('a', attrs={'href': re.compile("^http://")}):
#     print link
