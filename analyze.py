#!/usr/bin/env python
# coding: utf-8
# -*- coding: utf-8 -*-

import utils, naive_bayes

from google.appengine.api import memcache

from models import Article

# naar hvert selskap faar noen hundre artikler kan man begynne aa beregne
# probs paa kun selskapets artikler - da vil antakelig accuracyen gaa
# opp. nye selskaper, og selskper med faa artikler kan bruke hele
# korpusen som grunnlag. dette loeses vha. en enkel sjekk i begynnelsen
# av analyze, som ser paa stoerrelsen av det spesifikke korpuset.
def sentiment(article_object):

    values = memcache.get("values")
    if values: 
        [text, pos_freq, neg_freq, pos_size, neg_size, \
                                    title, pos_title_freq, neg_title_freq, pos_title_size, neg_title_size] = values
    else:

        q = Article.all()
        q.order("datetime")
        article_objects = q.fetch(1000)
        

    # finding sizes and frequencies:
        positive_article_texts = [""]
        negative_article_texts = [""]

        pos_titles = [""]
        neg_titles = [""]

    # if article_objects = []:
    #     article_objects = Article.all() 

        for article in article_objects:
            sentiment = article.sentiment

            if sentiment == "positive":
                positive_article_texts.append(article.text)
            elif sentiment == "negative":
                negative_article_texts.append(article.text)

            title_sentiment = article.title_sentiment

            if title_sentiment == "positive":
                pos_titles.append(article.title)
            elif title_sentiment == "negative":
                neg_titles.append(article.title)

        pos_size = len(positive_article_texts)
        neg_size = len(negative_article_texts)

        pos_title_size = len(pos_titles)
        neg_title_size = len(neg_titles)


    # finding token frequencies for the whole corpus:
        pos_text = ' '.join(map(unicode, positive_article_texts)) # possibly undesirable hack
        neg_text = ' '.join(map(unicode, negative_article_texts))

        pos_title = ' '.join(map(unicode, pos_titles))
        neg_title = ' '.join(map(unicode, neg_titles))
        
        pos_freq = naive_bayes.count_tokens(pos_text)
        neg_freq = naive_bayes.count_tokens(neg_text)

        pos_title_freq = naive_bayes.count_tokens(pos_title)
        neg_title_freq = naive_bayes.count_tokens(neg_title)

    # finding sentiment for one incoming article:
    # norm = article_object.normalized
        text = utils.string_normalize(article_object.text)
        title = utils.string_normalize(article_object.title)

        memcache.add("values", [text, pos_freq, neg_freq, pos_size, neg_size, \
                                    title, pos_title_freq, neg_title_freq, pos_title_size, neg_title_size], 11000)

# ----------------------

    # it seems you only use token_probs from here:
    # words, token_probs, word_pos_freqs, word_neg_freqs = naive_bayes.token_probs(text,pos_freq,neg_freq,pos_size,neg_size)


    token_probs = naive_bayes.token_probs(text,pos_freq,neg_freq,pos_size,neg_size)
    title_token_probs = naive_bayes.token_probs(title,pos_title_freq,neg_title_freq,pos_title_size,neg_title_size)

    prob = naive_bayes.combined_prob(token_probs)
    title_prob = naive_bayes.combined_prob(title_token_probs)

    if article_object.mod != None: # this just changes the conclusion - it does not teach the bayes anything until later, when the article is part of a different corpus.
        prob = min(.99, prob + article_object.mod) # from the user's button click - see CorrectionHandler
        prob = max(.01, prob)
        title_prob = min(.99, title_prob + article_object.mod)
        title_prob = max(.01, title_prob)

    article_object.prob = prob
    if prob >= 0.9:
        article_object.sentiment = "positive"
    elif prob <= 0.1:
        article_object.sentiment = "negative"
    else:
        article_object.sentiment = "neutral"

    article_object.title_prob = title_prob
    if title_prob >= 0.9:
        article_object.title_sentiment = "positive"
    elif title_prob <= 0.1:
        article_object.title_sentiment = "negative"
    else:
        article_object.title_sentiment = "neutral"

    article_object.analyzed = True
    article_object.put()


def all_sentiment(): 

#fetch the clean but non-analyzed ones from db, and everything else from memcache.

    # q = Article.all()
    # q.order("datetime")

    # article_cursor = memcache.get("analyze_article_cursor")

    # if article_cursor:
    #     q.with_cursor(start_cursor = article_cursor)

    # chunk_size = 30
    # articles = q.fetch(chunk_size)

    article_ids = memcache.get("article_ids")
    if article_ids:
        for article_id in article_ids: # this must be sharded!
            article = Article.get_by_id(article_id) 

    # for article in articles: 
            if article and article.clean and article.sentiment == None: # not just article.analyzed == None, because you need to get those who 'have been analyzed', but don't have a sentiment even so.
                sentiment(article) #,articles)
                article_ids.remove(article_id)

        memcache.set("article_ids", article_ids, 11000)

    else: # if no memcache
        q = Article.all().filter("clean =", True)
        articles = q.fetch(1)
        for article in articles:
            sentiment(article)
        

    # if len(articles) < chunk_size:
    #     memcache.delete("analyze_article_cursor")

    # else:
    #     article_cursor = q.cursor()
    #     memcache.set("analyze_article_cursor", article_cursor, 11000)


