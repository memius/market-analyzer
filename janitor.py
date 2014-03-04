#!/usr/bin/env python
# coding: utf-8
# -*- coding: utf-8 -*-

import clean, analyze, utils

from google.appengine.ext import db
from google.appengine.api import memcache

from models import Article


# hva med å bare hive inn alle article keys som "article_keys" i
# memcache. da vil jo alle artikler bli behandlet av de som henter
# article_keys.


# du må antakelig bruke cursor, og hente alle artiklene, men en av gangen, vha. cursor, og putte tittelen i titles, og sjekke om tittelen ligger i titles. titles lagres i memcache, og er sammenlignignsgrunnlag for dupe check. bare lag dupe checken først, og så lager vi after-clean og after-analyze etterpå. du bruker altså ikke så mye memory, siden du bare holder på med en artikkel av gangen, og titles legges i memcache, så den er tilgjengelig etter at du er ferdig med forrige artikkel. ganske enkelt, altså: titles = [], articles = Article.all(), cursor, for article in articles: hent tittel, sjekk om tittel i titles, dersom ja, db.delete(article), hvis ikke, legg article.title i titles og hopp til neste. bruk task queue, der du har 10 min. du får ikke lov til å bruke backends. da legger du inn f.eks. hvert tiende minutt, så sjekker den en artikkel hvert 10. min. det kommer til å ta lang tid. gjør det hvert 2. min, og se om det funker. kanskje med to artikler av gangen, kanskje 5 av gangen.


# en sjekk som sjekker company.titles opp mot faktisk lagrede
# titles. her tror jeg at det er mange titles i company.titles som
# aldri ble lagret.



def check(article):
    # # # specific article:
    # article = Article.get_by_id(640002)
    # db.delete(article)

    if article.clean and not utils.is_prose(article.text):
        clean.clean(article)
    if article.clean == False:
        clean.clean(article)
    if article.clean == None:
        clean.clean(article)
    if article.clean == True and article.sentiment == None:
        analyze.sentiment(article)
            #clean.clean(article)

    if article.analyzed and article.sentiment == None:
        analyze.sentiment(article)


#FORGET JANITOR FOR NOW; LET CLEAN AND ANALYZE DO THE JOB.
#FORGET JANITOR FOR NOW; LET CLEAN AND ANALYZE DO THE JOB.

def check_all():
    maintenance = memcache.get("maintenance")
    if maintenance:
        article = maintenance.pop() # last element is removed in place
        check(article)
        memcache.set("maintenance", maintenance)
    else:
        q = Article.all().filter("clean =", None) # now, it doesn't check those with clean == True!
        articles = q.fetch(8)
        memcache.add("articles", articles)
        


def clean_old_articles():
    q = Article.all()
    q.order("datetime")
    
    # cursor here, if fetch only a few
    clean_old_cursor = memcache.get("clean_old_cursor")
    if clean_old_cursor:
        q.with_cursor(start_cursor = clean_old_cursor)

    chunk_size = 2
    articles = q.fetch(chunk_size)

    for article in articles:
#        if article.sentiment == None:
#        if not article.clean:
        soup = bs(unicode(article.html))
        text = remove_outright(soup.get_text())
        sentences = sentencify(text)
        sentences = filter_sentences(sentences)
        sentences = junk(sentences)
            # strict(sentences)
        text = ''.join(sentences)        
            # if utils.is_prose(text):
        article.text = text
        article.clean = True
            # # else:
            # #     db.delete(article)
            # article.clean = True
        article.put()

    if len(articles) < chunk_size:
        memcache.delete("clean_old_cursor")

    if clean_old_cursor:
        memcache.set("clean_old_cursor", clean_old_cursor, 11000)
    else:
        memcache.add("clean_old_cursor", clean_old_cursor, 11000)




def all_sentiment_old_articles(): 
    q = Article.all()
    q.order("datetime")

#    memcache.delete("ana_old_cursor") #debug only

    ana_old_cursor = memcache.get("ana_old_cursor")
    if ana_old_cursor:
        q.with_cursor(start_cursor = ana_old_cursor)

    chunk_size = 8
    articles = q.fetch(chunk_size)

    for article in articles: 
        if not article.analyzed:
#        if article.clean and not article.sentiment:
            sentiment(article) 
#            article.sentiment = "sugar"


    if len(articles) < chunk_size:
        memcache.delete("ana_old_cursor")

    if ana_old_cursor:
        memcache.set("ana_old_cursor",ana_old_cursor, 11000)
    else:
        memcache.add("ana_old_cursor",ana_old_cursor, 11000)
