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

def articles():
    article_ids = memcache.get("article_ids")
    duplicate_check = memcache.get("duplicate_check") # article_ids fra forrige scrape.


    #nytt forsøk, etter å ha skriblet på papir:
    if article_ids:
        if duplicate_check:
            for article in article_ids:
                if article in duplicate_check: # her kaller du en ny funksjon: hente artikler vha. id, og sjekke på tittel og url. skal jeg rett og slett lagre både tittel og url for hver artikkel? nei, det tar for stor plass, tror jeg. har bare en gig. kanskje ikke? jo, sats på det. lagre så lite som mulig.
                    db.delete(article)
                    article_ids.remove(article)
            memcache.set("duplicate_check",duplicate_check)
        else:
            memcache.add("duplicate_check",article_ids)
        memcache.set("article_ids", article_ids)
    elif duplicate_check:
        memcache.set("duplicate_check",duplicate_check)


# -------------------------------------


#     if duplicate_check:

# #        her bør du adde dupe check og art ids. og sjekken bør være om det finnes art ids, ikke dupe checks. 

#         duplicates = []
#         checked = []
#         for article_id in duplicate_check: # removes the last (newest) in list
#             article = Article.get_by_id(article_id)
#             if article.url in duplicates:
#                 db.delete(article)
#                 duplicate_check.remove(article.key().id())
#                 if article_ids:
#                     article_ids.remove(article.key().id())
#             else:
#                 duplicates.append(article.url)
#                 checked.append(article.title)
#                 duplicate_check.append(article.key().id())

#         duplicates = []
#         for title in checked:
#             if title in duplicates:
#                 db.delete(article)
#                 duplicate_check.remove(article.key().id())
#                 if article_ids:
#                     article_ids.remove(article.key().id())
#             else:
#                 duplicates.append(article.title)

#         memcache.set("duplicate_check", duplicate_check, 11000)
#         if article_ids:
#             memcache.set("article_ids", article_ids, 11000)

#     # articles = Article.all()
#     # duplicates = []
#     # for article in articles:
#     #     if article.content in duplicates: # probably never hits, because text is cleaned before new ones come in.
#     #         db.delete(article)
#     #     else:
#     #         duplicates.append(article.content)

def plagiarism(text): # later, more sophisticated dup check on the article content (text).
    pass
