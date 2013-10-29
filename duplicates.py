# coding: utf-8

#checks for duplicates in the db, and removes them.

from google.appengine.ext import db

from models import Article, Company

def companies():
    companies = Company.all()
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
    articles = Article.all()
    duplicates = []
    checked = []
    for article in articles:
        if article.url in duplicates:
            db.delete(article)
        else:
            duplicates.append(article.url)
            checked.append(article)

    duplicates = []
    for article in checked:
        if article.title in duplicates: 
            db.delete(article)
        else:
            duplicates.append(article.title)

    # articles = Article.all()
    # duplicates = []
    # for article in articles:
    #     if article.content in duplicates: # probably never hits, because text is cleaned before new ones come in.
    #         db.delete(article)
    #     else:
    #         duplicates.append(article.content)

def plagiarism(text): # later, more sophisticated dup check on the article content (text).
    pass
