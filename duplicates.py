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
    duplicate_check = memcache.get("duplicate_check")

    if duplicate_check:
        duplicates = []
        checked = []
        for article_id in duplicate_check: # removes the last (newest) in list
            article = Article.get_by_id(article_id)
            if article.url in duplicates:
                db.delete(article)
                duplicate_check.remove(article.key().id())
                if article_ids:
                    article_ids.remove(article.key().id())
            else:
                duplicates.append(article.url)
                checked.append(article)

        duplicates = []
        for article in checked:
            if article.title in duplicates:
                db.delete(article)
                duplicate_check.remove(article.key().id())
                if article_ids:
                    article_ids.remove(article.key().id())
            else:
                duplicates.append(article.title)

        memcache.set("duplicate_check", duplicate_check)
        if article_ids:
            memcache.set("article_ids", article_ids)

    # articles = Article.all()
    # duplicates = []
    # for article in articles:
    #     if article.content in duplicates: # probably never hits, because text is cleaned before new ones come in.
    #         db.delete(article)
    #     else:
    #         duplicates.append(article.content)

def plagiarism(text): # later, more sophisticated dup check on the article content (text).
    pass
