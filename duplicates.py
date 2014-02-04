# coding: utf-8

#checks for duplicates in the db, and removes them.

from google.appengine.ext import db
from google.appengine.api import memcache

from models import Article, Company

def companies():
    q = Company.all()
    q.order("datetime")
    companies = q.fetch(1000)
    duplicates = []
    checked = []
    for company in companies:

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
        else:
            duplicates.append(company.name)
            checked.append(company)

    duplicates = []
    for company in checked:
        if company.ticker in duplicates:
            db.delete(company)
        else:
            duplicates.append(company.ticker)


# redundant because of titles check in scrape - and wrong, because it checks on keys, which are, of course, unique!
def articles():
    article_keys = memcache.get("article_keys")
    duplicate_check = memcache.get("duplicate_check") 

# dupe check skal inneholde:
#   i verste fall:
#     alle fra db - hente derfra hvis ingen dupe check
#   i beste fall:
#     de som ble skrapet forrige gang = article keys nå + dupe checks skal lagres som neste dupe check

    if article_keys != None: # lagret av forrige scrape
        if duplicate_check != None: # lagret av forrige duplicates
            for article_key in article_keys:
                if article_key in duplicate_check:
                    db.delete(article_key)
#                    article_keys.remove(article_key)
                else:
                    duplicate_check.append(article_key)
            memcache.set("duplicate_check", duplicate_check)
        else:
            duplicate_check = Article.all(keys_only=True) #fetching only the key, not the whole object.
            for article_key in article_keys:
                if article_key in duplicate_check:
                    db.delete(article_key)
#                    article_keys.remove(article_key)
                else:
                    duplicate_check.append(article_key)
            memcache.add("duplicate_check", article_keys)
    elif duplicate_check:
        memcache.set("duplicate_check", duplicate_check)


# not used right now: (use it in the run through all old articles routine that will use a larger instance)
def all_articles():
#    q = Article.all(keys_only=True) #fetching only the key, not the whole object.
# fetch only the titles, and use them for comparison
    q = Article.all() 
#    q = Article.all(projection=["title"]) funker ikke. feil med syntaks i doku.
    article_keys = q.fetch(10000)
    duplicates = []
    for article_key in article_keys:
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
