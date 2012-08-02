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
    links = []
    for div in divs:
        a = unicode(div.find('a', attrs={'href': re.compile("^http://")})) 
        link_regex = re.search("(http://.*?)\"",a)
        
        try:
            link = link_regex.group(1)

        except:
            link = "None"

        #print 'the link: ',link
        links.append(link)

    return links





#gf('aapl')



 
