#!/usr/bin/env python
# coding: utf-8
# -*- coding: utf-8 -*-


# #started by cron-job. fetches articles from web, and stores them to db.

import urllib2, re, chardet

from bs4 import BeautifulSoup as bs
from google.appengine.api import urlfetch, memcache
from google.appengine.ext import db 

from models import Article, Company

def linkz(ticker): # the one for articles.
    url = "https://www.google.com/finance/company_news?q=NASDAQ%3A" + ticker + "&ei=jXT9UYDqMKT4wAPmUw"
    result = urlfetch.fetch(url)
    if result.status_code == 200:
        soup = bs(result.content)

        span_class = re.compile("^name$")
        spans = soup.find_all("span", {"class" : span_class})
        spans = set(spans) #removes duplicates
        links = []
        for span in spans:
            for link in span.find_all('a'):
                title = link.get_text()
                link = link.get("href")
                if link is not None:
                    links.append([title,link])
        return links
    else:
        return ["except in linkz"]

# def companies(exchange):
#     if exchange == 'Nasdaq':
#         url = "http://www.nasdaq.com/screening/companies-by-industry.aspx?exchange=NASDAQ"
#         result = urlfetch.fetch(url)
#         if result.status_code == 200:
#             soup = bs(result.content)
            
# #            res = re.compile("CompanyListResults")
#             table = soup.find("table", {"id" : "CompanyListResults"})
#             companies = []
#             for link in table.find_all("a", {"target" : "_blank"}):
#                 company_name = link.get_text()
#                 companies.append(company_name)

#             # DU ER HER, skal finne tittelen fra href'en for hvert selskap'.
#             # table id, company list results inneholder alle selskapene
#             # !href for each company - target=_blank ! dette kun for selskapene, ikke for de andre href'ene'.!
#             # for link in ...find_all('a', {"target" : "_blank"})
#             # title = link.get_text()
#         companies = ["google","facebook","general electric","hoover","daym","apple"]
#         return companies

def fetch(url):
#    headers = {'User-Agent' : "Mozilla/5.0 (Windows NT 6.0; WOW64) AppleWebKit/534.24 (KHTML, like Gecko) Chrome/11.0.696.16 Safari/534.24"}
    #request = urllib2.Request(url,None,headers)
    
#    html = urllib2.urlopen(request).read()
# #    headers = {'User-agent':'Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/3.6.12'}
# #    method = urlfetch.GET
    headers = {'User-Agent' : "Chrome/11.0.696.16"}
    result = urlfetch.fetch(url, headers)
    if result.status_code == 200:
        html = result.content
        result = chardet.detect(html)
        charenc = result['encoding'] #

        if result['confidence'] > 0.98:
            if charenc == "utf-8" or charenc == "UTF-8":
                try:
                    html = unicode(html, "utf-8")
                    return html
                except:
                    pass

            else:
                try:
                    html = html.decode(charenc)
                    html = unicode(html) # fjerne forrige avsnitt, og gjoer html = unicode(html, charenc)
                    return html
                except:                
                    pass

        else:
            soup = bs(html)
            try:
                content_type = repr(soup.find("meta", {"http-equiv" : "Content-Type"}))
                content = re.compile("text/html; charset=(?P<charset>.*?)\"")
                encoding = re.search(content, content_type).group("charset")
            except:
                try:
                    meta = soup.find("meta", charset=True)
                    content = re.compile("charset=(?P<charset>.*?)\"")
                    encoding = re.search(content, meta).group("charset")
                except:
                    encoding = None

            try:
                html = html.decode(encoding)
                html = unicode(html)
            except:
                html = None


#          # strings = soup.strings
#         tags = soup.find_all(True)
#         strings = []
#         for tag in tags:
#             strings.append(tag.get_text())
#         text = ''.join(strings)


# # #         soup = bs(result.content, "html5lib")
# #          unholy = re.compile("script|li|ul|img|object|input|meta|noscript|iframe|form|em|style")
# #          out = soup.find_all(unholy)
# #          # out = soup.meta
# #          for tag in out:
# #              try:
# #                  tag.extract()
# #              except:
# #                  continue
# #          text = soup.get_text()
# # #         text = soup.stripped_strings()
# # #         text = soup.findAll(text=True)

        # #text = text.encode('utf-8')
        # text = result.content.encode('utf-8')
        # text = text.decode('utf-8')
        # text = unicode(text)

# # def visible(element): nice filter to be used on text, need small adjustments:
# #     if element.parent.name in ['style', 'script', '[document]', 'head', 'title']:
# #         return False
# #     elif re.match('<!--.*-->', unicode(element)):
# #         return False
# #     return True

# # visible_texts = filter(visible, texts)

        # l = []
        # l.append('"""')
        # l.append(u"Content-Type: text/html")
        # l.append(u"\n")
        # l.append(text)
        # l.append('"""')
        # s = ''.join(l)

#         s = result.content
#          s = s.decode('latin1')
#          s = s.encode('utf-8')
# #         s = unicode(s,'utf-8') useless, just use the one above, which encodes to utf-8.

#     # else:
#     #     s = "different status code for result in fetch"
    
    return html

def process_links(company):
    links = linkz(company.ticker)

    old_titles = company.titles
    titles = [] 
    for [title,link] in links:
        titles.append(title)
    titles = [title for title in titles if title not in old_titles]

    if titles == []:
        # company.finished_scraping = True # denne slaar inn for tidlig, siden den kommer foer alle artiklene er tatt
        # company.put()
        return # from this subfunction

    link_ctr = 1
    for [title, link] in links: 
        if link_ctr > 200: 
            break # from this links loop
        elif title in titles:
            link_ctr += 1
            if link != None and link != "":
                html = fetch(link)
                if html != None:
                    article_object = Article()
                    article_object.title = title
                    titles.remove(title) # when finished, titles = []
                    article_object.html = html
                    article_object.url = link
                    article_object.company = company
                    article_object.put() 
                                
                    new_titles = old_titles + titles
                    company.titles = new_titles #this list should be shortened every now and then
                    company.put() 
                    
    return titles # to tell whether finished or not.


def scrape():

    # company = Company()
    # company.name = "IBM"
    # company.lower = "ibm"
    # company.ticker = "IBM"
    # company.exchange = "NASDAQ"
    # company.put()
    # company = Company()
    # company.name = "General Electric Company"
    # company.lower = "general electric company"
    # company.ticker = "GE"
    # company.exchange = "NASDAQ"
    # company.put()

    q = Company.all()
    q.order("-datetime") # or id? key().id()?

    chunk_size = 5
    companies = q.fetch(chunk_size)

    company_cursor = memcache.get("company_cursor")
    # if not company_cursor: NOT needed. if no cursor, it simply starts at the beginning.

    if company_cursor:
        companies.with_cursor(start_cursor = company_cursor)

#    all_companies_scraped = True
#    comp_ctr = 1
    for company in companies: 
#        if comp_ctr > 300:
#            break # done for now, come back later (by cron)
#        else:
            # if company.finished_scraping == True:
            #     continue # jump to next company
            # else:
        # comp_ctr += 1
        process_links(company)
#                titles = process_links(company)

                # if titles == []:
                #     company.finished_scraping = True

#                   all_companies_scraped = False NO!
#                else:
#                    company.finished_scraping = False

    # if all_companies_scraped:
    #     for company in companies:
    #         company.finished_scraping = False
    #         company.put()

        #some useless commet here

    if len(companies) == chunk_size: # if not, you are at the end, and you don't want a new cursor.
        company_cursor = companies.cursor() 
        memcache.set("company_cursor",company_cursor, 11000) # 10800 == 180 min.


