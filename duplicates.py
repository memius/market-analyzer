# coding: utf-8

#checks for duplicates in the db, and removes them.

import logging

from google.appengine.ext import db
from google.appengine.api import memcache

from models import Article, Company

logging.getLogger().setLevel(logging.DEBUG)

def companies():
    q = Company.all(keys_only=True)
    # q.order("datetime") no datetime on keys
    company_keys = q.fetch(1000)
    duplicates = []
    checked = []
    delete_ctr = 0
    for key in company_keys:
        company = Company.get_by_id(key.id())
        # logging.debug("company key id: %s", key.id())
        # logging.debug("company key name: %s", key.name())
        # logging.debug("company name: %s", company.name())

        # if company.name == "General Electric Company":
        #     company.exchange = "NYSE"
        #     company.put()
        #     # db.delete(company)

        #dev only:
#         #comp_list = ["GOOG","FB","AAPL","GE","TSLA"]
#         if company.exchange == "NYSE" and company.ticker != "GE":
        # if company.ticker == "IBM":
        #     db.delete(company)

        if company.name in duplicates:
            db.delete(company)
            delete_ctr += 1
        else:
            duplicates.append(company.name)
            checked.append(company)

    duplicates = []
    for company in checked:
        if company.ticker in duplicates:
            db.delete(company)
            delete_ctr += 1
        else:
            duplicates.append(company.ticker)

    logging.debug("deleted %s duplicate companies", delete_ctr)

# redundant because of titles check in scrape - and wrong, because it checks on keys, which are, of course, unique!
def articles():
    article_keys = memcache.get("article_keys")
    # logging.debug("dupe() article keys: %s", article_keys[:3])
    duplicate_check = memcache.get("duplicate_check") 

# dupe check skal inneholde:
#   i verste fall:
#     alle fra db - hente derfra hvis ingen dupe check
#   i beste fall:
#     de som ble skrapet forrige gang = article keys nå + dupe checks skal lagres som neste dupe check

    delete_ctr = 0
    if article_keys: # lagret av forrige scrape
        # logging.debug("article keys exist in dupes")
        if duplicate_check: # lagret av forrige duplicates
            for article_key in article_keys:
                article = Article.get_by_id(article_key.id())
                if article:
                    if article.title in duplicate_check:
                        db.delete(article)
                        article_keys.remove(article_key)
                        delete_ctr += 1
                    else:
                        duplicate_check.append(article.title)
            memcache.set("duplicate_check", duplicate_check)
            memcache.set("article_keys", article_keys)
        else:
            q = Article.all(keys_only=True)
            # q.order("datetime") no datetime on keys
            keys = q.fetch(500)
            duplicate_check = []
            for key in keys:
                article = Article.get_by_id(key.id())
                duplicate_check.append(article.title)

            for article_key in article_keys:

                # no, this doesn't work; the key.name() is different from the object.name() - you can make this a lot more efficient by using 'name' instead of 'title', because 'name' can be accessed directly from the key (key.name()) - you don't have to fetch the whole article! test this by logging a company name - they already have names.

                article = Article.get_by_id(key.id())
                if article:
                    if article.title in duplicate_check: 
                        db.delete(article)
                        article_keys.remove(article_key)
                        delete_ctr += 1
                    else:
                        duplicate_check.append(article.title)
            memcache.set("duplicate_check", article_keys)
            memcache.set("article_keys", article_keys)
    elif duplicate_check:
        # logging.debug("article keys do NOT exist in dupes")
        memcache.set("duplicate_check", duplicate_check)

    logging.debug("deleted %s duplicate articles", delete_ctr)

# not used right now: (use it in the run through all old articles routine that will use a larger instance)
def all_articles():
#    q = Article.all(keys_only=True) #fetching only the key, not the whole object.
# fetch only the titles, and use them for comparison
    q = Article.all() 
#    q = Article.all(projection=["title"]) funker ikke. feil med syntaks i doku.
    article_keys = q.fetch(10000) # this is just wrong! you are not fetching the keys here.
    duplicates = []
    for article_key in article_keys: # this is also just wrong - never dupe check on keys - they are all different!
        if article_key.title in duplicates:
            db.delete(article_key)
        else:
            duplicates.append(article_key.title)
    



# -------------------------------------


#     if duplicate_check:

# #        her bør du adde dupe check og art keys. og sjekken bør være om det finnes art keys, ikke dupe checks. 

#         duplicates = []
#         checked = []
#         for article_id in duplicate_check: # removes the last (newest) in list
#             article = Article.get_by_id(article_id)
#             if article.url in duplicates:
#                 db.delete(article)
#                 duplicate_check.remove(article.key().id())
#                 if article_keys:
#                     article_keys.remove(article.key().id())
#             else:
#                 duplicates.append(article.url)
#                 checked.append(article.title)
#                 duplicate_check.append(article.key().id())

#         duplicates = []
#         for title in checked:
#             if title in duplicates:
#                 db.delete(article)
#                 duplicate_check.remove(article.key().id())
#                 if article_keys:
#                     article_keys.remove(article.key().id())
#             else:
#                 duplicates.append(article.title)

#         memcache.set("duplicate_check", duplicate_check, 11000)
#         if article_keys:
#             memcache.set("article_keys", article_keys, 11000)

#     # articles = Article.all()
#     # duplicates = []
#     # for article in articles:
#     #     if article.content in duplicates: # probably never hits, because text is cleaned before new ones come in.
#     #         db.delete(article)
#     #     else:
#     #         duplicates.append(article.content)

def plagiarism(text): # later, more sophisticated dup check on the article content (text).
    pass
