#!/usr/bin/env python
# coding: utf-8
# -*- coding: utf-8 -*-


# see if this works without any more configuration. you probably have to define a task queue request first, though. or maybe a call to _ah_start or whatever it was from cron will do the trick?

# it has to be a dynamic backend, because only they can be started by a http request. residents must be started manually.


from models import Article

# this is for testing backends. put something in the db, say a new
# company. if that works, update every ten minutes or so, to change
# the company entry. if that works, you can try to start scrape.py
# this way - or one of the others, if that doesn't work on the first
# try.
def test():
    # # create a new company, then update it, then do scrape/dupes/clean or analyze.
    # company = Company()
    # company.name = "Advanced Micro Devices, Inc"
    # company.name_lower = "advanced micro devices, inc"
    # company.ticker = "AMD"
    # company.ticker_lower = "amd"
    # company.exchange = "NYSE"
    # company.put()

    # company = Company()
    # company.name = "Goldman Sachs Group Inc"
    # company.name_lower = "goldman sachs group inc"
    # company.ticker = "GS"
    # company.ticker_lower = "gs"
    # company.exchange = "NYSE"
    # company.put()

    q = Article.all()
    q.order("datetime")
    articles = q.fetch(1)

    for article in articles:
        article.title_sentiment = "foobar"
        article.put()
