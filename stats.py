# coding: utf-8


import logging, datetime

from google.appengine.api import memcache
from google.appengine.ext import db

from models import Article, Company

logging.getLogger().setLevel(logging.DEBUG)


def count_recent_stats():
    # if old_flag:
    #     q = Article.all(keys_only=True)
    #     article_keys = q.fetch(10000)
    # else:
    article_keys = memcache.get("article_keys")
    # logging.debug("clean() article keys: %s", article_keys[:3])
    # logging.debug("in clean")
    stats_ctr = 0
    if article_keys:
        # pos_ctr = 0
        # neg_ctr = 0

        companies = []
        logging.debug("article keys exist in stats")
        for article_key in article_keys:
            article = Article.get_by_id(article_key.id())
            if article != None and article.sentiment != "neutral":
                company = article.company # expensive, but ok for now - optimize later

                logging.debug("datetime.datetime.now(): %s", datetime.datetime.now())
                logging.debug("article.datetime: %s", article.datetime)
                if datetime.datetime.now() - article.datetime < datetime.timedelta(hours = 24):
                    if company.pos_ctr_day == None:
                        company.pos_ctr_day = 0
                    if company.neg_ctr_day == None:
                        company.neg_ctr_day = 0
                    if article.sentiment == 'positive':
                        company.pos_ctr_day += 1
                    elif article.sentiment == 'negative':
                        company.neg_ctr_day += 1

                elif True:
                    if company.pos_ctr_week == None:
                        company.pos_ctr_week = 0
                    if company.neg_ctr_week == None:
                        company.neg_ctr_week = 0
                    if article.sentiment == 'positive':
                        company.pos_ctr_week += 1
                    elif article.sentiment == 'negative':
                        company.neg_ctr_week += 1

                elif True:
                    if company.pos_ctr_month == None:
                        company.pos_ctr_month = 0
                    if company.neg_ctr_month == None:
                        company.neg_ctr_month = 0
                    if article.sentiment == 'positive':
                        company.pos_ctr_month += 1
                    elif article.sentiment == 'negative':
                        company.neg_ctr_month += 1


                company.put() # expensive to do this once for each article, but ok, because few articles each time.
                    
                # company = article.company # this is extremely expensive, but ok for now.
                # old_pos_ctr = company.pos_ctr
                # if old_pos_ctr == None:
                #     old_pos_ctr = 0
                # new_pos_ctr = old_pos_ctr + 1 # NOT pos_ctr, which counts for ALL the articles.
                # company.pos_ctr = new_pos_ctr

                # old_neg_ctr = company.neg_ctr
                # if old_neg_ctr == None:
                #     old_neg_ctr = 0
                # new_neg_ctr = old_neg_ctr + 1
                # company.neg_ctr = new_neg_ctr

                company.put()

        stats_ctr += 1
        # cleaning.remove(article) not needed, because pop removes it for us.
        memcache.set("article_keys", article_keys)
        # logging.debug("article keys set")

    logging.debug("counted stats for %s articles", stats_ctr)

    
def count_all_stats():
    q = Company.all()
    companies = q.fetch(10000)
    for company in companies:
        company.pos_ctr = 0
        company.neg_ctr = 0
        articles = company.articles
        for article in articles:
            if article.sentiment == "positive":
                company.pos_ctr += 1
            elif article.sentiment == "negative":
                company.neg_ctr += 1

        company.put()

